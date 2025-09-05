#!/usr/bin/env python3
"""
Intelligent Field Extractor for Ontario Family Law Forms
Understands document structure, boxes, sections, and field relationships
"""

import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict

# Try different PDF/DOCX libraries
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    from pdfplumber import PDF
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    from docx import Document
    from docx.oxml.table import CT_Tbl
    from docx.oxml.text.paragraph import CT_P
    from docx.table import Table
    from docx.text.paragraph import Paragraph
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FieldInfo:
    """Information about a form field"""
    field_id: str
    field_name: str
    field_label: str
    field_type: str  # text, checkbox, radio, date, number, etc.
    section: str
    subsection: str = ""
    box_number: str = ""
    required: bool = False
    validation: str = ""
    options: List[str] = field(default_factory=list)
    related_fields: List[str] = field(default_factory=list)
    position: Dict[str, float] = field(default_factory=dict)  # x, y, width, height
    context: str = ""
    help_text: str = ""
    default_value: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class DocumentSection:
    """Represents a section of the document"""
    section_id: str
    title: str
    box_number: str = ""
    fields: List[FieldInfo] = field(default_factory=list)
    subsections: List['DocumentSection'] = field(default_factory=list)
    instructions: str = ""
    
class IntelligentFieldExtractor:
    """Extract fields intelligently from Ontario Court Forms"""
    
    def __init__(self):
        self.field_patterns = {
            'checkbox': r'[\[\]□☐]\s*([A-Za-z\s]+)',
            'radio': r'[○◯⭕]\s*([A-Za-z\s]+)',
            'text_field': r'_{3,}|\.{3,}',
            'date_field': r'(day|month|year|date)',
            'number_field': r'\$\s*_{3,}|#\s*_{3,}',
            'box_label': r'Box\s*(\d+[A-Za-z]?):?\s*([^\\n]+)',
            'section_header': r'^(?:PART|Section|Schedule)\s*([A-Z0-9]+)[:\s]*([^\\n]+)',
        }
        
        self.section_keywords = {
            'applicant': ['applicant', 'petitioner', 'plaintiff'],
            'respondent': ['respondent', 'defendant'],
            'children': ['child', 'children', 'dependant'],
            'financial': ['income', 'expense', 'asset', 'debt', 'property', 'financial'],
            'support': ['support', 'maintenance', 'alimony'],
            'custody': ['custody', 'access', 'parenting', 'decision-making'],
            'property': ['property', 'asset', 'debt', 'equalization'],
            'court': ['court', 'file number', 'registry', 'location'],
        }
        
    def extract_from_file(self, file_path: str) -> List[FieldInfo]:
        """Extract fields from a file (PDF or DOCX)"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return []
            
        if file_path.suffix.lower() == '.pdf':
            return self.extract_from_pdf(file_path)
        elif file_path.suffix.lower() in ['.docx', '.doc']:
            return self.extract_from_docx(file_path)
        else:
            logger.error(f"Unsupported file type: {file_path.suffix}")
            return []
    
    def extract_from_pdf(self, pdf_path: Path) -> List[FieldInfo]:
        """Extract fields from PDF using multiple methods"""
        fields = []
        
        # Try PyMuPDF first (better for forms)
        if HAS_PYMUPDF:
            fields = self._extract_with_pymupdf(pdf_path)
            
        # If no fields found, try pdfplumber
        if not fields and HAS_PDFPLUMBER:
            fields = self._extract_with_pdfplumber(pdf_path)
            
        if not fields:
            logger.warning(f"No PDF library available or no fields found in {pdf_path}")
            
        return fields
    
    def _extract_with_pymupdf(self, pdf_path: Path) -> List[FieldInfo]:
        """Extract using PyMuPDF (good for form fields)"""
        fields = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num, page in enumerate(doc):
                # Extract form fields
                widgets = page.widgets()
                for widget in widgets:
                    field_info = self._parse_widget(widget, page_num)
                    if field_info:
                        fields.append(field_info)
                
                # Extract text and analyze structure
                text = page.get_text()
                page_fields = self._analyze_text_structure(text, page_num)
                fields.extend(page_fields)
                
            doc.close()
            
        except Exception as e:
            logger.error(f"Error extracting with PyMuPDF: {e}")
            
        return fields
    
    def _parse_widget(self, widget, page_num: int) -> Optional[FieldInfo]:
        """Parse a PDF form widget"""
        try:
            field_name = widget.field_name or f"field_{page_num}_{widget.rect}"
            field_label = widget.field_label or widget.field_name or ""
            field_type = self._determine_widget_type(widget)
            
            return FieldInfo(
                field_id=field_name,
                field_name=field_name,
                field_label=field_label,
                field_type=field_type,
                section=f"Page {page_num + 1}",
                position={
                    'x': widget.rect.x0,
                    'y': widget.rect.y0,
                    'width': widget.rect.width,
                    'height': widget.rect.height,
                    'page': page_num
                },
                options=widget.field_choices if hasattr(widget, 'field_choices') else [],
                default_value=widget.field_value or ""
            )
        except Exception as e:
            logger.debug(f"Error parsing widget: {e}")
            return None
    
    def _determine_widget_type(self, widget) -> str:
        """Determine the type of form widget"""
        if hasattr(widget, 'field_type'):
            ft = widget.field_type
            if ft == fitz.PDF_WIDGET_TYPE_CHECKBOX:
                return 'checkbox'
            elif ft == fitz.PDF_WIDGET_TYPE_RADIOBUTTON:
                return 'radio'
            elif ft == fitz.PDF_WIDGET_TYPE_TEXT:
                return 'text'
            elif ft == fitz.PDF_WIDGET_TYPE_COMBOBOX:
                return 'dropdown'
        return 'text'
    
    def _extract_with_pdfplumber(self, pdf_path: Path) -> List[FieldInfo]:
        """Extract using pdfplumber (good for text analysis)"""
        fields = []
        
        try:
            with PDF.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract tables
                    tables = page.extract_tables()
                    for table in tables:
                        table_fields = self._analyze_table(table, page_num)
                        fields.extend(table_fields)
                    
                    # Extract text
                    text = page.extract_text()
                    if text:
                        page_fields = self._analyze_text_structure(text, page_num)
                        fields.extend(page_fields)
                        
        except Exception as e:
            logger.error(f"Error extracting with pdfplumber: {e}")
            
        return fields
    
    def extract_from_docx(self, docx_path: Path) -> List[FieldInfo]:
        """Extract fields from DOCX files"""
        if not HAS_DOCX:
            logger.error("python-docx not installed")
            return []
            
        fields = []
        
        try:
            doc = Document(docx_path)
            
            # Extract from paragraphs
            for para_num, para in enumerate(doc.paragraphs):
                if para.text.strip():
                    para_fields = self._analyze_paragraph(para, para_num)
                    fields.extend(para_fields)
            
            # Extract from tables
            for table_num, table in enumerate(doc.tables):
                table_fields = self._analyze_docx_table(table, table_num)
                fields.extend(table_fields)
            
            # Extract from content controls (form fields)
            fields.extend(self._extract_content_controls(docx_path))
            
        except Exception as e:
            logger.error(f"Error extracting from DOCX: {e}")
            
        return fields
    
    def _analyze_paragraph(self, para, para_num: int) -> List[FieldInfo]:
        """Analyze a paragraph for fields"""
        fields = []
        text = para.text
        
        # Check for box labels
        box_match = re.search(self.field_patterns['box_label'], text)
        if box_match:
            box_num = box_match.group(1)
            box_title = box_match.group(2)
            
            # Look for fields in this box
            field_text = text[box_match.end():]
            fields.extend(self._extract_fields_from_text(
                field_text, 
                section=box_title,
                box_number=box_num
            ))
        
        # Check for section headers
        section_match = re.search(self.field_patterns['section_header'], text)
        if section_match:
            section_num = section_match.group(1)
            section_title = section_match.group(2)
            
            # Look for fields in this section
            field_text = text[section_match.end():]
            fields.extend(self._extract_fields_from_text(
                field_text,
                section=f"{section_num}: {section_title}"
            ))
        
        # Look for standalone fields
        if not box_match and not section_match:
            fields.extend(self._extract_fields_from_text(text, section=f"Paragraph {para_num}"))
        
        return fields
    
    def _analyze_docx_table(self, table, table_num: int) -> List[FieldInfo]:
        """Analyze a DOCX table for fields"""
        fields = []
        
        for row_idx, row in enumerate(table.rows):
            row_data = []
            for cell in row.cells:
                cell_text = cell.text.strip()
                row_data.append(cell_text)
                
                # Check if cell contains field indicators
                if any(pattern in cell_text for pattern in ['___', '...', '[ ]', '( )']):
                    field_info = self._create_field_from_cell(
                        cell_text,
                        section=f"Table {table_num + 1}",
                        subsection=f"Row {row_idx + 1}"
                    )
                    if field_info:
                        fields.append(field_info)
        
        return fields
    
    def _extract_content_controls(self, docx_path: Path) -> List[FieldInfo]:
        """Extract content controls (form fields) from DOCX"""
        fields = []
        
        try:
            # Open as ZIP to access XML
            with zipfile.ZipFile(docx_path, 'r') as docx_zip:
                # Read document XML
                with docx_zip.open('word/document.xml') as xml_file:
                    tree = ET.parse(xml_file)
                    root = tree.getroot()
                    
                    # Find all content controls
                    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                    controls = root.findall('.//w:sdt', ns)
                    
                    for control in controls:
                        field_info = self._parse_content_control(control, ns)
                        if field_info:
                            fields.append(field_info)
                            
        except Exception as e:
            logger.debug(f"Could not extract content controls: {e}")
            
        return fields
    
    def _parse_content_control(self, control, ns) -> Optional[FieldInfo]:
        """Parse a content control element"""
        try:
            # Get properties
            props = control.find('.//w:sdtPr', ns)
            if props is None:
                return None
                
            # Get alias/tag (field name)
            alias = props.find('.//w:alias', ns)
            field_name = alias.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if alias is not None else ""
            
            # Get placeholder text
            placeholder = props.find('.//w:placeholder/w:docPart', ns)
            field_label = placeholder.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if placeholder is not None else field_name
            
            # Determine field type
            if props.find('.//w:date', ns) is not None:
                field_type = 'date'
            elif props.find('.//w:dropDownList', ns) is not None:
                field_type = 'dropdown'
                # Get options
                options = []
                for item in props.findall('.//w:listItem', ns):
                    value = item.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}value')
                    if value:
                        options.append(value)
            elif props.find('.//w:checkbox', ns) is not None:
                field_type = 'checkbox'
            else:
                field_type = 'text'
                
            return FieldInfo(
                field_id=field_name or f"control_{id(control)}",
                field_name=field_name,
                field_label=field_label,
                field_type=field_type,
                section="Form Fields",
                options=options if field_type == 'dropdown' else []
            )
            
        except Exception as e:
            logger.debug(f"Error parsing content control: {e}")
            return None
    
    def _analyze_text_structure(self, text: str, page_num: int) -> List[FieldInfo]:
        """Analyze text structure to identify fields and sections"""
        fields = []
        lines = text.split('\n')
        
        current_section = f"Page {page_num + 1}"
        current_box = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for box labels
            box_match = re.search(self.field_patterns['box_label'], line)
            if box_match:
                current_box = box_match.group(1)
                current_section = box_match.group(2)
                continue
            
            # Check for section headers
            section_match = re.search(self.field_patterns['section_header'], line)
            if section_match:
                current_section = f"{section_match.group(1)}: {section_match.group(2)}"
                continue
            
            # Extract fields from line
            line_fields = self._extract_fields_from_text(
                line,
                section=current_section,
                box_number=current_box
            )
            fields.extend(line_fields)
        
        return fields
    
    def _extract_fields_from_text(self, text: str, section: str = "", box_number: str = "") -> List[FieldInfo]:
        """Extract fields from a text string"""
        fields = []
        
        # Check for checkboxes
        checkbox_matches = re.finditer(self.field_patterns['checkbox'], text)
        for match in checkbox_matches:
            label = match.group(1).strip()
            fields.append(FieldInfo(
                field_id=f"checkbox_{label.lower().replace(' ', '_')}",
                field_name=label.lower().replace(' ', '_'),
                field_label=label,
                field_type='checkbox',
                section=section,
                box_number=box_number,
                context=text[:100]
            ))
        
        # Check for radio buttons
        radio_matches = re.finditer(self.field_patterns['radio'], text)
        for match in radio_matches:
            label = match.group(1).strip()
            fields.append(FieldInfo(
                field_id=f"radio_{label.lower().replace(' ', '_')}",
                field_name=label.lower().replace(' ', '_'),
                field_label=label,
                field_type='radio',
                section=section,
                box_number=box_number,
                context=text[:100]
            ))
        
        # Check for text fields (underscores or dots)
        if re.search(self.field_patterns['text_field'], text):
            # Try to extract label from text before the field
            label_match = re.search(r'([A-Za-z\s]+)(?:_{3,}|\.{3,})', text)
            if label_match:
                label = label_match.group(1).strip()
                field_type = 'date' if any(d in label.lower() for d in ['date', 'day', 'month', 'year']) else 'text'
                field_type = 'number' if '$' in text or '#' in text else field_type
                
                fields.append(FieldInfo(
                    field_id=f"{field_type}_{label.lower().replace(' ', '_')}",
                    field_name=label.lower().replace(' ', '_'),
                    field_label=label,
                    field_type=field_type,
                    section=section,
                    box_number=box_number,
                    context=text[:100]
                ))
        
        return fields
    
    def _create_field_from_cell(self, cell_text: str, section: str, subsection: str) -> Optional[FieldInfo]:
        """Create field info from table cell"""
        if not cell_text or len(cell_text) < 3:
            return None
            
        # Determine field type
        field_type = 'text'
        if '[ ]' in cell_text or '[x]' in cell_text or '☐' in cell_text:
            field_type = 'checkbox'
        elif '( )' in cell_text or '(x)' in cell_text or '○' in cell_text:
            field_type = 'radio'
        elif any(d in cell_text.lower() for d in ['date', 'day', 'month', 'year']):
            field_type = 'date'
        elif '$' in cell_text:
            field_type = 'currency'
        elif '#' in cell_text or 'number' in cell_text.lower():
            field_type = 'number'
        
        # Extract label
        label = re.sub(r'[\[\]()_.$#\s]+', ' ', cell_text).strip()
        
        if not label:
            return None
            
        return FieldInfo(
            field_id=f"{field_type}_{label.lower().replace(' ', '_')}",
            field_name=label.lower().replace(' ', '_'),
            field_label=label,
            field_type=field_type,
            section=section,
            subsection=subsection,
            context=cell_text
        )
    
    def _analyze_table(self, table: List[List[str]], page_num: int) -> List[FieldInfo]:
        """Analyze a table structure for fields"""
        fields = []
        
        if not table:
            return fields
            
        # Assume first row might be headers
        headers = table[0] if table else []
        
        for row_idx, row in enumerate(table):
            for col_idx, cell in enumerate(row):
                if not cell or not cell.strip():
                    continue
                    
                # Get header if available
                header = headers[col_idx] if col_idx < len(headers) and row_idx > 0 else ""
                
                # Check if cell looks like a field
                if any(indicator in cell for indicator in ['___', '...', '[ ]', '( )', '$_', '#_']):
                    field_info = self._create_field_from_cell(
                        cell,
                        section=f"Table on Page {page_num + 1}",
                        subsection=header or f"Row {row_idx + 1}, Column {col_idx + 1}"
                    )
                    if field_info:
                        fields.append(field_info)
        
        return fields
    
    def identify_relationships(self, fields: List[FieldInfo]) -> List[FieldInfo]:
        """Identify relationships between fields"""
        # Group fields by section
        sections = defaultdict(list)
        for field in fields:
            sections[field.section].append(field)
        
        # Identify related fields within sections
        for section_fields in sections.values():
            for i, field1 in enumerate(section_fields):
                for field2 in section_fields[i+1:]:
                    # Check if fields are related
                    if self._are_fields_related(field1, field2):
                        field1.related_fields.append(field2.field_id)
                        field2.related_fields.append(field1.field_id)
        
        return fields
    
    def _are_fields_related(self, field1: FieldInfo, field2: FieldInfo) -> bool:
        """Determine if two fields are related"""
        # Same box number
        if field1.box_number and field1.box_number == field2.box_number:
            return True
            
        # Similar names
        name1_parts = set(field1.field_name.split('_'))
        name2_parts = set(field2.field_name.split('_'))
        if len(name1_parts & name2_parts) > 1:
            return True
            
        # Radio buttons with similar labels
        if field1.field_type == 'radio' and field2.field_type == 'radio':
            if field1.section == field2.section:
                return True
                
        return False
    
    def save_extraction_results(self, fields: List[FieldInfo], output_file: str):
        """Save extraction results to JSON"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'extraction_date': datetime.now().isoformat(),
            'total_fields': len(fields),
            'fields_by_type': self._count_by_type(fields),
            'fields_by_section': self._count_by_section(fields),
            'fields': [f.to_dict() for f in fields]
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
            
        logger.info(f"Saved {len(fields)} fields to {output_path}")
    
    def _count_by_type(self, fields: List[FieldInfo]) -> Dict[str, int]:
        """Count fields by type"""
        counts = defaultdict(int)
        for field in fields:
            counts[field.field_type] += 1
        return dict(counts)
    
    def _count_by_section(self, fields: List[FieldInfo]) -> Dict[str, int]:
        """Count fields by section"""
        counts = defaultdict(int)
        for field in fields:
            counts[field.section] += 1
        return dict(counts)

def main():
    """Test the extractor"""
    extractor = IntelligentFieldExtractor()
    
    # Test with a sample form
    test_file = "workflow_output/ontario_forms/form_8_-_application_general_flr-8-jun25-en.docx"
    
    if Path(test_file).exists():
        logger.info(f"Extracting fields from {test_file}")
        fields = extractor.extract_from_file(test_file)
        fields = extractor.identify_relationships(fields)
        
        logger.info(f"Extracted {len(fields)} fields")
        
        # Save results
        output_file = "test_extraction_results.json"
        extractor.save_extraction_results(fields, output_file)
        
        # Print summary
        for field in fields[:10]:  # Show first 10 fields
            print(f"Field: {field.field_label} ({field.field_type}) in {field.section}")
    else:
        logger.error(f"Test file not found: {test_file}")

if __name__ == "__main__":
    main()