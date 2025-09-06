#!/usr/bin/env python3
"""
Improved Form Parser for Ontario Family Law Forms
Extracts all fields including text fields, checkboxes, tables, and long-form areas
Works without external dependencies beyond standard library
"""

import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class FormField:
    """Represents a single form field"""
    field_id: str
    field_name: str
    field_type: str  # text, date, checkbox, radio, dropdown, area, table
    field_label: str
    required: bool = False
    validation_rules: str = ""
    max_length: Optional[int] = None
    options: Optional[List[str]] = None
    table_name: Optional[str] = None
    table_row: Optional[int] = None
    field_context: str = ""
    page_number: int = 0
    coordinates: Optional[Dict] = None
    help_text: Optional[str] = None
    section: Optional[str] = None


class ImprovedFormParser:
    """Enhanced parser that extracts all form fields from DOCX files"""
    
    # Namespaces for Word XML
    NAMESPACES = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
        'w15': 'http://schemas.microsoft.com/office/word/2012/wordml',
        'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
        'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    }
    
    # Field patterns to identify in text
    FIELD_PATTERNS = {
        'court_info': [
            (r'Court File Number', 'court_file_number', 'text'),
            (r'Court (?:Office )?Address', 'court_address', 'text'),
            (r'Municipality', 'municipality', 'text'),
            (r'Province', 'province', 'dropdown'),
        ],
        'party_info': [
            (r"(?:Applicant|Respondent|Party)'?s? Full Legal Name", 'full_legal_name', 'text'),
            (r'Date of Birth', 'date_of_birth', 'date'),
            (r'Address.*Street', 'street_address', 'text'),
            (r'City/Town', 'city', 'text'),
            (r'Postal Code', 'postal_code', 'text'),
            (r'Phone|Telephone', 'phone', 'text'),
            (r'Email', 'email', 'email'),
            (r'Fax', 'fax', 'text'),
        ],
        'lawyer_info': [
            (r"Lawyer'?s? Name", 'lawyer_name', 'text'),
            (r'Law Firm', 'law_firm', 'text'),
            (r'LSO #|Law Society', 'lso_number', 'text'),
        ],
        'marriage_info': [
            (r'Date of Marriage', 'marriage_date', 'date'),
            (r'Place of Marriage', 'marriage_place', 'text'),
            (r'Date of Separation', 'separation_date', 'date'),
            (r'Name.*before.*marriage', 'name_before_marriage', 'text'),
        ],
        'claims': [
            (r'□\s*Divorce', 'claim_divorce', 'checkbox'),
            (r'□\s*Custody', 'claim_custody', 'checkbox'),
            (r'□\s*Access', 'claim_access', 'checkbox'),
            (r'□\s*Support.*applicant', 'claim_support_applicant', 'checkbox'),
            (r'□\s*Support.*child', 'claim_support_children', 'checkbox'),
            (r'□\s*Property|Equalization', 'claim_property', 'checkbox'),
            (r'□\s*Possession.*home', 'claim_possession_home', 'checkbox'),
            (r'□\s*Restraining [Oo]rder', 'claim_restraining_order', 'checkbox'),
        ],
        'children': [
            (r'Child.*Full.*Name', 'child_name', 'text'),
            (r'Child.*Birth.*Date', 'child_birthdate', 'date'),
            (r'Child.*Age', 'child_age', 'number'),
            (r'Residing with', 'child_residing_with', 'dropdown'),
        ],
        'financial': [
            (r'Form 13(?:\.1)?.*attached', 'financial_statement_attached', 'checkbox'),
        ],
        'long_form': [
            (r'Important facts', 'important_facts', 'area'),
            (r'Explain|Describe|Provide details', 'details', 'area'),
            (r'Other.*specify', 'other_specify', 'area'),
        ]
    }
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.form_number = self._extract_form_number()
        self.fields = []
        self.field_counter = {}
        self.current_section = ""
        
    def _extract_form_number(self) -> str:
        """Extract form number from filename"""
        filename = self.file_path.stem.lower()
        
        # Try various patterns
        patterns = [
            r'form[_\s-]?(\d+[a-z]?)',
            r'flr[_\s-]?(\d+[a-z]?)',
            r'^(\d+[a-z]?)[_\s-]'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                return match.group(1).upper()
        
        return "unknown"
    
    def parse(self) -> List[FormField]:
        """Main parsing method"""
        logger.info(f"Parsing form: {self.file_path.name}")
        
        if self.file_path.suffix.lower() != '.docx':
            logger.warning(f"File is not a DOCX: {self.file_path}")
            return []
        
        try:
            # Extract all possible fields
            self._extract_form_fields_from_xml()
            self._extract_content_controls()
            self._extract_text_patterns()
            self._extract_tables()
            
            # Deduplicate and clean
            self._deduplicate_fields()
            
            logger.info(f"Extracted {len(self.fields)} fields from {self.form_number}")
            
        except Exception as e:
            logger.error(f"Error parsing form: {e}")
        
        return self.fields
    
    def _extract_form_fields_from_xml(self):
        """Extract legacy form fields from document.xml"""
        try:
            with zipfile.ZipFile(self.file_path, 'r') as docx:
                if 'word/document.xml' in docx.namelist():
                    with docx.open('word/document.xml') as xml_file:
                        tree = ET.parse(xml_file)
                        root = tree.getroot()
                        
                        # Find all form field data elements
                        for elem in root.iter():
                            if elem.tag.endswith('ffData'):
                                self._process_form_field_data(elem)
                                
        except Exception as e:
            logger.debug(f"Error extracting XML form fields: {e}")
    
    def _process_form_field_data(self, ff_elem):
        """Process a form field data element"""
        try:
            # Extract field name
            name = None
            for child in ff_elem:
                if child.tag.endswith('name'):
                    name = child.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '')
                    break
            
            if not name:
                name = f'field_{len(self.fields)}'
            
            # Determine field type
            field_type = 'text'
            options = None
            
            for child in ff_elem:
                if child.tag.endswith('checkBox'):
                    field_type = 'checkbox'
                elif child.tag.endswith('ddList'):
                    field_type = 'dropdown'
                    # Extract dropdown options
                    options = []
                    for entry in child:
                        if entry.tag.endswith('listEntry'):
                            val = entry.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
                            if val:
                                options.append(val)
            
            # Extract help text
            help_text = None
            for child in ff_elem:
                if child.tag.endswith('helpText'):
                    help_text = child.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '')
                    break
            
            # Create field
            field = FormField(
                field_id=self._generate_field_id(name),
                field_name=self._sanitize_field_name(name),
                field_type=field_type,
                field_label=self._humanize_field_name(name),
                options=options,
                help_text=help_text,
                field_context="Form Field",
                section=self.current_section
            )
            
            self.fields.append(field)
            
        except Exception as e:
            logger.debug(f"Error processing form field: {e}")
    
    def _extract_content_controls(self):
        """Extract content control fields (modern form fields)"""
        try:
            with zipfile.ZipFile(self.file_path, 'r') as docx:
                if 'word/document.xml' in docx.namelist():
                    with docx.open('word/document.xml') as xml_file:
                        content = xml_file.read().decode('utf-8')
                        
                        # Look for content controls
                        sdt_pattern = r'<w:sdt\b[^>]*>.*?</w:sdt>'
                        controls = re.findall(sdt_pattern, content, re.DOTALL)
                        
                        for control in controls:
                            self._process_content_control(control)
                            
        except Exception as e:
            logger.debug(f"Error extracting content controls: {e}")
    
    def _process_content_control(self, control_xml):
        """Process a content control element"""
        try:
            # Extract alias/tag
            alias_match = re.search(r'<w:alias[^>]*w:val="([^"]+)"', control_xml)
            tag_match = re.search(r'<w:tag[^>]*w:val="([^"]+)"', control_xml)
            
            name = None
            if alias_match:
                name = alias_match.group(1)
            elif tag_match:
                name = tag_match.group(1)
            
            if not name:
                return
            
            # Determine type
            field_type = 'text'
            if '<w:date' in control_xml:
                field_type = 'date'
            elif '<w:dropDownList' in control_xml:
                field_type = 'dropdown'
            elif '<w:checkbox' in control_xml or '<w14:checkbox' in control_xml:
                field_type = 'checkbox'
            
            # Extract placeholder text
            placeholder_match = re.search(r'<w:placeholder>.*?<w:docPart[^>]*w:val="([^"]+)"', control_xml)
            label = placeholder_match.group(1) if placeholder_match else self._humanize_field_name(name)
            
            field = FormField(
                field_id=self._generate_field_id(name),
                field_name=self._sanitize_field_name(name),
                field_type=field_type,
                field_label=label,
                field_context="Content Control",
                section=self.current_section
            )
            
            self.fields.append(field)
            
        except Exception as e:
            logger.debug(f"Error processing content control: {e}")
    
    def _extract_text_patterns(self):
        """Extract fields based on text patterns in the document"""
        try:
            with zipfile.ZipFile(self.file_path, 'r') as docx:
                if 'word/document.xml' in docx.namelist():
                    with docx.open('word/document.xml') as xml_file:
                        tree = ET.parse(xml_file)
                        root = tree.getroot()
                        
                        # Extract all text
                        text_content = self._extract_all_text(root)
                        
                        # Apply patterns
                        for section, patterns in self.FIELD_PATTERNS.items():
                            for pattern, field_name, field_type in patterns:
                                if re.search(pattern, text_content, re.IGNORECASE):
                                    self._add_pattern_field(pattern, field_name, field_type, section)
                                    
        except Exception as e:
            logger.debug(f"Error extracting text patterns: {e}")
    
    def _extract_all_text(self, root) -> str:
        """Extract all text from XML root"""
        text_parts = []
        for elem in root.iter():
            if elem.tag.endswith('t'):
                if elem.text:
                    text_parts.append(elem.text)
        return ' '.join(text_parts)
    
    def _extract_tables(self):
        """Extract table-based fields"""
        try:
            with zipfile.ZipFile(self.file_path, 'r') as docx:
                if 'word/document.xml' in docx.namelist():
                    with docx.open('word/document.xml') as xml_file:
                        tree = ET.parse(xml_file)
                        root = tree.getroot()
                        
                        # Find all tables
                        tables = root.findall('.//w:tbl', self.NAMESPACES)
                        
                        for table_idx, table in enumerate(tables):
                            self._process_table(table, table_idx)
                            
        except Exception as e:
            logger.debug(f"Error extracting tables: {e}")
    
    def _process_table(self, table_elem, table_idx):
        """Process a table element to extract fields"""
        try:
            rows = table_elem.findall('.//w:tr', self.NAMESPACES)
            
            # Check if it's a children table
            header_text = self._get_table_header_text(table_elem)
            if 'child' in header_text.lower():
                self._add_children_table_fields(table_idx)
            
            # Look for label-value pairs in table cells
            for row_idx, row in enumerate(rows):
                cells = row.findall('.//w:tc', self.NAMESPACES)
                
                for cell_idx, cell in enumerate(cells):
                    cell_text = self._get_cell_text(cell)
                    
                    # Check if cell contains a field indicator
                    if self._is_field_indicator(cell_text):
                        field_name = self._extract_field_name_from_text(cell_text)
                        field = FormField(
                            field_id=self._generate_field_id(f"table_{table_idx}_row_{row_idx}_cell_{cell_idx}"),
                            field_name=field_name,
                            field_type=self._infer_field_type(cell_text),
                            field_label=cell_text,
                            table_name=f"Table {table_idx + 1}",
                            table_row=row_idx,
                            field_context=f"Table {table_idx + 1}, Row {row_idx + 1}"
                        )
                        self.fields.append(field)
                        
        except Exception as e:
            logger.debug(f"Error processing table: {e}")
    
    def _get_table_header_text(self, table_elem) -> str:
        """Get text from table header"""
        try:
            first_row = table_elem.find('.//w:tr', self.NAMESPACES)
            if first_row:
                return self._get_cell_text(first_row)
        except:
            pass
        return ""
    
    def _get_cell_text(self, cell_elem) -> str:
        """Extract text from a table cell"""
        text_parts = []
        for t_elem in cell_elem.findall('.//w:t', self.NAMESPACES):
            if t_elem.text:
                text_parts.append(t_elem.text)
        return ' '.join(text_parts)
    
    def _is_field_indicator(self, text: str) -> bool:
        """Check if text indicates a form field"""
        indicators = [
            r':\s*$',  # Ends with colon
            r'^\s*□',  # Starts with checkbox
            r'__+',    # Contains underscores (fill-in line)
            r'Date:',
            r'Name:',
            r'Address:',
            r'Phone:',
            r'Email:',
        ]
        
        for indicator in indicators:
            if re.search(indicator, text):
                return True
        
        return False
    
    def _extract_field_name_from_text(self, text: str) -> str:
        """Extract a field name from label text"""
        # Remove special characters and clean up
        name = re.sub(r'[:\□__]', '', text)
        name = re.sub(r'\s+', '_', name.strip())
        return self._sanitize_field_name(name.lower())
    
    def _infer_field_type(self, text: str) -> str:
        """Infer field type from text"""
        text_lower = text.lower()
        
        if '□' in text or 'checkbox' in text_lower:
            return 'checkbox'
        elif 'date' in text_lower:
            return 'date'
        elif 'email' in text_lower:
            return 'email'
        elif 'phone' in text_lower or 'tel' in text_lower:
            return 'text'
        elif 'postal' in text_lower or 'zip' in text_lower:
            return 'text'
        elif any(word in text_lower for word in ['explain', 'describe', 'details', 'facts']):
            return 'area'
        else:
            return 'text'
    
    def _add_pattern_field(self, pattern: str, field_name: str, field_type: str, section: str):
        """Add a field based on pattern match"""
        field_id = self._generate_field_id(field_name)
        
        # Don't add if already exists
        if any(f.field_name == field_name for f in self.fields):
            return
        
        field = FormField(
            field_id=field_id,
            field_name=field_name,
            field_type=field_type,
            field_label=self._humanize_field_name(field_name),
            field_context="Pattern Match",
            section=section
        )
        
        self.fields.append(field)
    
    def _add_children_table_fields(self, table_idx: int):
        """Add standard children table fields"""
        children_fields = [
            ('child_name', 'Child Full Legal Name', 'text'),
            ('child_birthdate', 'Date of Birth', 'date'),
            ('child_age', 'Age', 'number'),
            ('child_grade', 'Grade/Year', 'text'),
            ('child_residing_with', 'Residing With', 'dropdown'),
            ('child_relationship_applicant', 'Relationship to Applicant', 'text'),
            ('child_relationship_respondent', 'Relationship to Respondent', 'text'),
        ]
        
        for field_name, label, field_type in children_fields:
            field = FormField(
                field_id=self._generate_field_id(f"table_{table_idx}_{field_name}"),
                field_name=field_name,
                field_type=field_type,
                field_label=label,
                table_name=f"Children Table",
                field_context="Children Information",
                section="children"
            )
            self.fields.append(field)
    
    def _generate_field_id(self, base_name: str) -> str:
        """Generate unique field ID"""
        if base_name in self.field_counter:
            self.field_counter[base_name] += 1
            return f"form{self.form_number}_{base_name}_{self.field_counter[base_name]}"
        else:
            self.field_counter[base_name] = 1
            return f"form{self.form_number}_{base_name}"
    
    def _sanitize_field_name(self, name: str) -> str:
        """Sanitize field name for use as variable"""
        # Remove special characters
        name = re.sub(r'[^\w\s]', '', name)
        # Replace spaces with underscores
        name = re.sub(r'\s+', '_', name)
        # Remove leading/trailing underscores
        name = name.strip('_')
        # Convert to lowercase
        name = name.lower()
        # Ensure it starts with a letter
        if name and not name[0].isalpha():
            name = 'field_' + name
        
        return name or 'field'
    
    def _humanize_field_name(self, name: str) -> str:
        """Convert field name to human-readable label"""
        # Handle special cases
        special_cases = {
            'court_file_number': 'Court File Number',
            'lso_number': 'LSO Number',
            'email': 'Email Address',
            'phone': 'Phone Number',
            'postal_code': 'Postal Code',
        }
        
        if name.lower() in special_cases:
            return special_cases[name.lower()]
        
        # General conversion
        label = re.sub(r'_', ' ', name)
        label = re.sub(r'([a-z])([A-Z])', r'\1 \2', label)
        label = label.strip().title()
        
        return label
    
    def _deduplicate_fields(self):
        """Remove duplicate fields"""
        seen = set()
        unique_fields = []
        
        for field in self.fields:
            key = (field.field_name, field.field_type)
            if key not in seen:
                seen.add(key)
                unique_fields.append(field)
        
        self.fields = unique_fields
    
    def save_to_json(self, output_path: Optional[str] = None) -> str:
        """Save parsed fields to JSON file"""
        if not output_path:
            output_path = self.file_path.with_suffix('.json')
        
        output_data = {
            'form_number': self.form_number,
            'form_file': str(self.file_path),
            'total_fields': len(self.fields),
            'fields': [asdict(field) for field in self.fields]
        }
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        logger.info(f"Saved {len(self.fields)} fields to {output_path}")
        
        return str(output_path)


def main():
    """Main function for testing"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python improved_form_parser.py <form.docx>")
        sys.exit(1)
    
    parser = ImprovedFormParser(sys.argv[1])
    fields = parser.parse()
    
    print(f"Extracted {len(fields)} fields from {parser.form_number}")
    
    # Print summary by type
    by_type = {}
    for field in fields:
        by_type[field.field_type] = by_type.get(field.field_type, 0) + 1
    
    print("\nFields by type:")
    for field_type, count in sorted(by_type.items()):
        print(f"  {field_type}: {count}")
    
    # Save to JSON
    output_file = parser.save_to_json()
    print(f"\nSaved to: {output_file}")


if __name__ == "__main__":
    main()