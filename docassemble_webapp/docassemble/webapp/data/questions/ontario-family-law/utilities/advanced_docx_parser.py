#!/usr/bin/env python3
"""
Advanced DOCX Parser for Ontario Family Law Forms
Uses multiple libraries to extract form fields from complex DOCX documents
"""

import os
import re
import json
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import logging

# Multiple DOCX parsing libraries
from docx import Document
import docx2txt
from docx2python import docx2python
import mammoth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DocxField:
    """Represents a field extracted from DOCX"""
    field_name: str
    field_type: str
    field_label: str
    value: Optional[str] = None
    required: bool = False
    page_number: int = 0
    context: str = ""
    extraction_method: str = ""
    confidence: float = 0.0
    metadata: Dict = None

class AdvancedDocxParser:
    """
    Advanced DOCX parser that combines multiple strategies:
    1. XML parsing for form controls
    2. Content control extraction
    3. Table analysis
    4. Pattern matching
    5. Structured text analysis
    """
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.fields = []
        
        # Ontario form patterns
        self.patterns = {
            'blank_line': r'_{3,}',
            'dots': r'\.{3,}',
            'brackets': r'\[[\s_\.]*\]',
            'checkbox': r'[☐□■☑]\s*([^☐□■☑\n]+)',
            'radio': r'[○●◯◉]\s*([^○●◯◉\n]+)',
            'currency': r'\$[\s_]*[\d,]*\.?\d*',
            'date': r'\d{1,2}/\d{1,2}/\d{4}|_{2}/_{2}/_{4}',
            'name_field': r'(?:First|Last|Middle|Full)\s+(?:Legal\s+)?Name\s*:?\s*_{3,}',
            'address_field': r'(?:Street\s+)?Address\s*:?\s*_{3,}',
            'court_file': r'Court\s+File\s+(?:Number|No\.?)\s*:?\s*_{3,}',
        }
    
    def parse(self) -> List[DocxField]:
        """Parse DOCX using all available strategies"""
        
        logger.info(f"Parsing DOCX: {self.file_path.name}")
        
        # Strategy 1: Extract XML form controls
        self._extract_xml_controls()
        
        # Strategy 2: Use python-docx for structured content
        self._extract_with_python_docx()
        
        # Strategy 3: Use docx2python for nested structure
        self._extract_with_docx2python()
        
        # Strategy 4: Use mammoth for clean HTML conversion
        self._extract_with_mammoth()
        
        # Strategy 5: Direct XML parsing for content controls
        self._extract_content_controls()
        
        # Deduplicate and merge fields
        self.fields = self._merge_fields(self.fields)
        
        return self.fields
    
    def _extract_xml_controls(self):
        """Extract form controls from DOCX XML"""
        try:
            with zipfile.ZipFile(self.file_path, 'r') as docx:
                # Parse document.xml
                if 'word/document.xml' in docx.namelist():
                    xml_content = docx.read('word/document.xml')
                    root = ET.fromstring(xml_content)
                    
                    # Define namespaces
                    namespaces = {
                        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
                        'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
                        'w15': 'http://schemas.microsoft.com/office/word/2012/wordml'
                    }
                    
                    # Find all structured document tags (content controls)
                    for sdt in root.findall('.//w:sdt', namespaces):
                        self._process_sdt(sdt, namespaces)
                    
                    # Find form fields (legacy)
                    for fldSimple in root.findall('.//w:fldSimple', namespaces):
                        self._process_form_field(fldSimple, namespaces)
                    
                    # Find checkboxes
                    for checkbox in root.findall('.//w14:checkbox', namespaces):
                        self._process_checkbox(checkbox, namespaces)
        
        except Exception as e:
            logger.debug(f"XML control extraction error: {e}")
    
    def _extract_with_python_docx(self):
        """Extract fields using python-docx"""
        try:
            doc = Document(self.file_path)
            
            # Extract from paragraphs
            for para_idx, para in enumerate(doc.paragraphs):
                text = para.text.strip()
                if text:
                    # Check for form patterns
                    for pattern_name, pattern in self.patterns.items():
                        if re.search(pattern, text):
                            field = DocxField(
                                field_name=f"field_{para_idx}",
                                field_type=self._get_field_type(pattern_name),
                                field_label=text[:100],
                                context=f"Paragraph {para_idx}",
                                extraction_method="python-docx-paragraph",
                                confidence=0.7
                            )
                            self.fields.append(field)
                            break
            
            # Extract from tables
            for table_idx, table in enumerate(doc.tables):
                self._extract_table_fields(table, table_idx)
            
            # Extract from runs (for inline fields)
            for para in doc.paragraphs:
                runs_text = ""
                for run in para.runs:
                    runs_text += run.text
                    
                    # Check for underlined blanks (often form fields)
                    if run.underline:
                        field = DocxField(
                            field_name=f"underlined_{len(self.fields)}",
                            field_type="text",
                            field_label=run.text or "Underlined field",
                            extraction_method="python-docx-underline",
                            confidence=0.6
                        )
                        self.fields.append(field)
        
        except Exception as e:
            logger.debug(f"python-docx extraction error: {e}")
    
    def _extract_with_docx2python(self):
        """Extract using docx2python for better structure preservation"""
        try:
            # Extract with structure
            result = docx2python(str(self.file_path))
            
            # Process body content
            for section_idx, section in enumerate(result.body):
                for table_idx, table in enumerate(section):
                    for row_idx, row in enumerate(table):
                        for cell_idx, cell in enumerate(row):
                            if isinstance(cell, list):
                                cell_text = " ".join(str(item) for item in cell)
                            else:
                                cell_text = str(cell)
                            
                            if self._looks_like_field(cell_text):
                                field = DocxField(
                                    field_name=f"docx2py_{section_idx}_{table_idx}_{row_idx}_{cell_idx}",
                                    field_type=self._detect_field_type(cell_text),
                                    field_label=cell_text[:100],
                                    context=f"Section {section_idx}, Table {table_idx}, Row {row_idx}",
                                    extraction_method="docx2python",
                                    confidence=0.75
                                )
                                self.fields.append(field)
            
            # Process headers and footers
            for header in result.header:
                self._process_text_for_fields(str(header), "header", "docx2python-header")
            
            for footer in result.footer:
                self._process_text_for_fields(str(footer), "footer", "docx2python-footer")
        
        except Exception as e:
            logger.debug(f"docx2python extraction error: {e}")
    
    def _extract_with_mammoth(self):
        """Extract using mammoth for clean conversion"""
        try:
            with open(self.file_path, "rb") as docx_file:
                result = mammoth.extract_raw_text(docx_file)
                text = result.value
                
                # Process lines for fields
                lines = text.split('\n')
                for line_idx, line in enumerate(lines):
                    if self._looks_like_field(line):
                        field = DocxField(
                            field_name=f"mammoth_line_{line_idx}",
                            field_type=self._detect_field_type(line),
                            field_label=line[:100],
                            context=f"Line {line_idx}",
                            extraction_method="mammoth",
                            confidence=0.65
                        )
                        self.fields.append(field)
        
        except Exception as e:
            logger.debug(f"Mammoth extraction error: {e}")
    
    def _extract_content_controls(self):
        """Extract content controls (form fields) from DOCX"""
        try:
            with zipfile.ZipFile(self.file_path, 'r') as docx:
                # Check for custom XML parts (often used for forms)
                for item in docx.namelist():
                    if 'customXml' in item and item.endswith('.xml'):
                        xml_content = docx.read(item)
                        self._process_custom_xml(xml_content)
                
                # Check document properties for form fields
                if 'docProps/custom.xml' in docx.namelist():
                    props_xml = docx.read('docProps/custom.xml')
                    self._process_custom_properties(props_xml)
        
        except Exception as e:
            logger.debug(f"Content control extraction error: {e}")
    
    def _extract_table_fields(self, table, table_idx: int):
        """Extract fields from a table"""
        for row_idx, row in enumerate(table.rows):
            row_text = ""
            cells_data = []
            
            for cell_idx, cell in enumerate(row.cells):
                cell_text = cell.text.strip()
                cells_data.append(cell_text)
                row_text += " " + cell_text
            
            # Check if row contains form fields
            if self._looks_like_field(row_text):
                # Try to identify label and field
                for i, cell_text in enumerate(cells_data):
                    if self._is_field_label(cell_text) and i + 1 < len(cells_data):
                        # Next cell might be the field
                        field_cell = cells_data[i + 1]
                        if self._is_blank_field(field_cell) or not field_cell:
                            field = DocxField(
                                field_name=self._sanitize_name(cell_text),
                                field_type=self._detect_field_type(cell_text),
                                field_label=cell_text,
                                context=f"Table {table_idx}, Row {row_idx}",
                                extraction_method="table-structure",
                                confidence=0.8
                            )
                            self.fields.append(field)
    
    def _process_sdt(self, sdt, namespaces):
        """Process structured document tag (content control)"""
        try:
            # Get properties
            props = sdt.find('.//w:sdtPr', namespaces)
            if props is not None:
                # Get alias/tag
                alias = props.find('.//w:alias', namespaces)
                tag = props.find('.//w:tag', namespaces)
                
                field_name = ""
                if alias is not None:
                    field_name = alias.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '')
                elif tag is not None:
                    field_name = tag.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '')
                
                # Get content
                content = sdt.find('.//w:sdtContent', namespaces)
                field_text = self._get_text_from_element(content, namespaces)
                
                if field_name or field_text:
                    field = DocxField(
                        field_name=field_name or f"sdt_{len(self.fields)}",
                        field_type=self._detect_control_type(props, namespaces),
                        field_label=field_text[:100],
                        extraction_method="xml-sdt",
                        confidence=0.9
                    )
                    self.fields.append(field)
        
        except Exception as e:
            logger.debug(f"SDT processing error: {e}")
    
    def _process_form_field(self, field_elem, namespaces):
        """Process legacy form field"""
        try:
            instr = field_elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}instr', '')
            
            # Parse instruction
            if 'FORMTEXT' in instr or 'FORMCHECKBOX' in instr or 'FORMDROPDOWN' in instr:
                field_type = 'text'
                if 'CHECKBOX' in instr:
                    field_type = 'checkbox'
                elif 'DROPDOWN' in instr:
                    field_type = 'select'
                
                field = DocxField(
                    field_name=f"formfield_{len(self.fields)}",
                    field_type=field_type,
                    field_label=instr,
                    extraction_method="xml-formfield",
                    confidence=0.85
                )
                self.fields.append(field)
        
        except Exception as e:
            logger.debug(f"Form field processing error: {e}")
    
    def _process_checkbox(self, checkbox_elem, namespaces):
        """Process checkbox element"""
        try:
            # Get checked state
            checked = checkbox_elem.find('.//w14:checked', namespaces)
            is_checked = checked is not None and checked.get('{http://schemas.microsoft.com/office/word/2010/wordml}val') == '1'
            
            field = DocxField(
                field_name=f"checkbox_{len(self.fields)}",
                field_type="checkbox",
                field_label="Checkbox",
                value="checked" if is_checked else "unchecked",
                extraction_method="xml-checkbox",
                confidence=0.9
            )
            self.fields.append(field)
        
        except Exception as e:
            logger.debug(f"Checkbox processing error: {e}")
    
    def _process_text_for_fields(self, text: str, context: str, method: str):
        """Process text to find fields"""
        if not text:
            return
        
        # Check each pattern
        for pattern_name, pattern in self.patterns.items():
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                field = DocxField(
                    field_name=f"{pattern_name}_{len(self.fields)}",
                    field_type=self._get_field_type(pattern_name),
                    field_label=match.group(0)[:100],
                    context=context,
                    extraction_method=method,
                    confidence=0.7
                )
                self.fields.append(field)
    
    def _process_custom_xml(self, xml_content: bytes):
        """Process custom XML for form data"""
        try:
            root = ET.fromstring(xml_content)
            # Look for form-like elements
            for elem in root.iter():
                if elem.text and self._looks_like_field_name(elem.tag):
                    field = DocxField(
                        field_name=elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag,
                        field_type="text",
                        field_label=elem.tag,
                        value=elem.text,
                        extraction_method="custom-xml",
                        confidence=0.8
                    )
                    self.fields.append(field)
        
        except Exception as e:
            logger.debug(f"Custom XML processing error: {e}")
    
    def _process_custom_properties(self, props_xml: bytes):
        """Process custom document properties"""
        try:
            root = ET.fromstring(props_xml)
            namespaces = {
                'cp': 'http://schemas.openxmlformats.org/officeDocument/2006/custom-properties',
                'vt': 'http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes'
            }
            
            for prop in root.findall('.//cp:property', namespaces):
                name = prop.get('name', '')
                value_elem = prop.find('.//vt:lpwstr', namespaces)
                
                if value_elem is not None:
                    field = DocxField(
                        field_name=name,
                        field_type="text",
                        field_label=name,
                        value=value_elem.text,
                        extraction_method="custom-properties",
                        confidence=0.75
                    )
                    self.fields.append(field)
        
        except Exception as e:
            logger.debug(f"Custom properties processing error: {e}")
    
    def _get_text_from_element(self, elem, namespaces) -> str:
        """Extract text from XML element"""
        if elem is None:
            return ""
        
        text = ""
        for t in elem.findall('.//w:t', namespaces):
            if t.text:
                text += t.text
        
        return text.strip()
    
    def _detect_control_type(self, props, namespaces) -> str:
        """Detect type of content control"""
        # Check for specific control types
        if props.find('.//w:date', namespaces) is not None:
            return 'date'
        elif props.find('.//w:dropDownList', namespaces) is not None:
            return 'select'
        elif props.find('.//w:comboBox', namespaces) is not None:
            return 'select'
        elif props.find('.//w:picture', namespaces) is not None:
            return 'image'
        else:
            return 'text'
    
    def _looks_like_field(self, text: str) -> bool:
        """Check if text looks like a form field"""
        if not text or len(text) < 2:
            return False
        
        # Check for common field indicators
        indicators = [
            '___', '...', '[ ]', '[X]', '( )', '(X)',
            '☐', '☑', '□', '■', '○', '●'
        ]
        
        for indicator in indicators:
            if indicator in text:
                return True
        
        # Check for patterns
        for pattern in self.patterns.values():
            if re.search(pattern, text):
                return True
        
        # Check for field-like labels
        field_keywords = [
            'name', 'date', 'address', 'phone', 'email',
            'number', 'amount', 'signature', 'initial'
        ]
        
        text_lower = text.lower()
        for keyword in field_keywords:
            if keyword in text_lower and (':' in text or '___' in text):
                return True
        
        return False
    
    def _looks_like_field_name(self, name: str) -> bool:
        """Check if XML tag name looks like a field"""
        if not name:
            return False
        
        # Remove namespace
        name = name.split('}')[-1] if '}' in name else name
        
        # Common form field patterns in XML
        patterns = [
            'field', 'input', 'text', 'value', 'answer',
            'name', 'date', 'address', 'phone', 'email'
        ]
        
        name_lower = name.lower()
        return any(p in name_lower for p in patterns)
    
    def _is_field_label(self, text: str) -> bool:
        """Check if text is a field label"""
        if not text or len(text) < 2:
            return False
        
        # Common label patterns
        return bool(re.search(r'.*:\s*$|^.*\?$', text)) or \
               any(kw in text.lower() for kw in ['name', 'date', 'address', 'phone', 'email'])
    
    def _is_blank_field(self, text: str) -> bool:
        """Check if text represents a blank field"""
        if not text:
            return True
        
        # Check for blank field indicators
        return bool(re.search(r'^[_\.\s]+$|^\[[\s_]*\]$', text))
    
    def _detect_field_type(self, text: str) -> str:
        """Detect field type from text"""
        text_lower = text.lower()
        
        if any(kw in text_lower for kw in ['date', 'when', 'birth', 'dob']):
            return 'date'
        elif any(kw in text_lower for kw in ['email', 'e-mail']):
            return 'email'
        elif any(kw in text_lower for kw in ['phone', 'tel', 'fax', 'cell']):
            return 'phone'
        elif any(kw in text_lower for kw in ['amount', '$', 'payment', 'income']):
            return 'currency'
        elif '☐' in text or '□' in text or '[ ]' in text:
            return 'checkbox'
        elif '○' in text or '( )' in text:
            return 'radio'
        elif any(kw in text_lower for kw in ['signature', 'sign', 'initial']):
            return 'signature'
        elif any(kw in text_lower for kw in ['select', 'choose', 'pick']):
            return 'select'
        else:
            return 'text'
    
    def _get_field_type(self, pattern_name: str) -> str:
        """Get field type from pattern name"""
        type_map = {
            'checkbox': 'checkbox',
            'radio': 'radio',
            'currency': 'currency',
            'date': 'date',
            'name_field': 'text',
            'address_field': 'text',
            'court_file': 'text'
        }
        return type_map.get(pattern_name, 'text')
    
    def _sanitize_name(self, text: str) -> str:
        """Create valid field name from text"""
        # Remove special characters
        name = re.sub(r'[^\w\s]', '', text)
        # Replace spaces with underscores
        name = re.sub(r'\s+', '_', name)
        # Limit length
        return name[:50].lower()
    
    def _merge_fields(self, fields: List[DocxField]) -> List[DocxField]:
        """Merge and deduplicate fields"""
        merged = {}
        
        for field in fields:
            # Create key for deduplication
            key = (field.field_type, field.field_label[:30])
            
            if key not in merged:
                merged[key] = field
            else:
                # Keep the one with higher confidence
                if field.confidence > merged[key].confidence:
                    merged[key] = field
        
        return list(merged.values())

def test_advanced_parser(file_path: str):
    """Test the advanced DOCX parser"""
    parser = AdvancedDocxParser(file_path)
    fields = parser.parse()
    
    print(f"\nAdvanced DOCX Parser Results: {Path(file_path).name}")
    print("=" * 60)
    print(f"Total fields extracted: {len(fields)}")
    
    # Group by extraction method
    methods = {}
    for field in fields:
        method = field.extraction_method
        if method not in methods:
            methods[method] = 0
        methods[method] += 1
    
    print("\nExtraction methods:")
    for method, count in sorted(methods.items(), key=lambda x: x[1], reverse=True):
        print(f"  {method}: {count} fields")
    
    # Group by field type
    types = {}
    for field in fields:
        ftype = field.field_type
        if ftype not in types:
            types[ftype] = 0
        types[ftype] += 1
    
    print("\nField types:")
    for ftype, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {ftype}: {count} fields")
    
    # Show high-confidence fields
    print("\nSample high-confidence fields:")
    high_conf = sorted(fields, key=lambda x: x.confidence, reverse=True)[:10]
    for field in high_conf:
        print(f"  [{field.confidence:.2f}] {field.field_label[:50]} ({field.field_type})")
    
    # Save results
    output_file = f"advanced_{Path(file_path).stem}.json"
    with open(output_file, 'w') as f:
        json.dump([asdict(field) for field in fields], f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    
    return fields

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        # Test on Form 13
        test_file = "workflow_output/ontario_forms/financial_statements/form_13_-_financial_statement_support_flr-13-may21-en-fil.docx"
        if os.path.exists(test_file):
            fields = test_advanced_parser(test_file)
        else:
            print("Please provide a DOCX file path")
    else:
        fields = test_advanced_parser(sys.argv[1])