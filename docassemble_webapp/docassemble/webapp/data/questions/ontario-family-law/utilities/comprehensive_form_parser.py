#!/usr/bin/env python3
"""
Comprehensive Ontario Family Law Forms Parser
Extracts fields from PDFs and Word documents, saves to CSV, then generates docassemble YAML files
"""

import os
import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Document parsing libraries
import PyPDF2
import pdfplumber
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
import fitz  # PyMuPDF for better PDF handling

# OCR and Vision
try:
    from google.cloud import vision
    from google.cloud import documentai_v1 as documentai
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    print("Google Cloud libraries not available. Using local parsing only.")

# Image processing for PDF OCR fallback
from PIL import Image
try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    print("Warning: pytesseract not available. OCR functionality will be disabled.")
import numpy as np

@dataclass
class FormField:
    """Represents a single form field"""
    field_id: str
    field_name: str
    field_type: str  # text, date, checkbox, radio, number, currency, etc.
    field_label: str
    required: bool
    validation_rules: str
    max_length: Optional[int]
    options: Optional[List[str]]  # For select/radio fields
    table_name: Optional[str]  # If part of a table
    table_row: Optional[int]
    table_col: Optional[int]
    page_number: int
    x_position: Optional[float]
    y_position: Optional[float]
    width: Optional[float]
    height: Optional[float]
    default_value: Optional[str]
    help_text: Optional[str]
    depends_on: Optional[str]  # Field dependencies
    
    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}

class FormParser:
    """Base class for form parsing"""
    
    # Common Ontario form field patterns
    FIELD_PATTERNS = {
        'date': r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|_+/\s*_+/\s*_+)\b',
        'sin': r'\b(\d{3}[-\s]?\d{3}[-\s]?\d{3}|___[-\s]?___[-\s]?___)\b',
        'postal_code': r'\b([A-Z]\d[A-Z]\s?\d[A-Z]\d|___ ___)\b',
        'phone': r'\b(\(\d{3}\)\s?\d{3}-\d{4}|\d{3}-\d{3}-\d{4}|\(___\)\s?___-____)\b',
        'currency': r'\$[\s_]*[\d,]+\.?\d*|\$[\s_]*[_]+',
        'checkbox': r'[\[\]☐☑□■]\s*([^\[\]☐☑□■\n]+)',
        'blank_field': r'_{3,}|\.{3,}',
        'court_file': r'Court File Number:?\s*([^\n]+)',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b|_{3,}@_{3,}'
    }
    
    # Common field labels in Ontario forms
    COMMON_LABELS = {
        'applicant': ['Applicant', 'Petitioner', 'Moving Party', 'Claimant'],
        'respondent': ['Respondent', 'Responding Party', 'Defendant'],
        'name': ['Full Legal Name', 'Name', 'First Name', 'Last Name', 'Middle Name'],
        'address': ['Address', 'Street', 'City', 'Province', 'Postal Code'],
        'date_of_birth': ['Date of Birth', 'Birth Date', 'DOB', 'Born'],
        'marriage_date': ['Date of Marriage', 'Married on', 'Marriage Date'],
        'separation_date': ['Date of Separation', 'Separated on', 'Separation Date'],
        'children': ['Children', 'Child', 'Dependants', 'Minor Children']
    }
    
    def __init__(self, form_path: str, form_number: str):
        self.form_path = Path(form_path)
        self.form_number = form_number
        self.fields: List[FormField] = []
        self.tables: Dict[str, List[List[str]]] = {}
        
    def extract_fields(self) -> List[FormField]:
        """Extract all fields from the form"""
        raise NotImplementedError("Subclasses must implement extract_fields")
    
    def identify_field_type(self, text: str, context: str = "") -> str:
        """Identify the field type based on patterns and context"""
        text_lower = text.lower()
        context_lower = context.lower()
        
        # Check for specific patterns
        if re.search(self.FIELD_PATTERNS['date'], text):
            return 'date'
        elif re.search(self.FIELD_PATTERNS['sin'], text):
            return 'sin'
        elif re.search(self.FIELD_PATTERNS['postal_code'], text, re.IGNORECASE):
            return 'postal_code'
        elif re.search(self.FIELD_PATTERNS['phone'], text):
            return 'phone'
        elif re.search(self.FIELD_PATTERNS['currency'], text):
            return 'currency'
        elif re.search(self.FIELD_PATTERNS['checkbox'], text):
            return 'checkbox'
        elif re.search(self.FIELD_PATTERNS['email'], text):
            return 'email'
        
        # Check context for field type hints
        if any(word in context_lower for word in ['date', 'when', 'on', 'day']):
            return 'date'
        elif any(word in context_lower for word in ['amount', 'payment', '$', 'dollar', 'income', 'expense']):
            return 'currency'
        elif any(word in context_lower for word in ['email', 'e-mail']):
            return 'email'
        elif any(word in context_lower for word in ['phone', 'telephone', 'fax', 'cell']):
            return 'phone'
        elif any(word in context_lower for word in ['number of', 'how many', 'quantity']):
            return 'number'
        elif any(word in context_lower for word in ['check all', 'select all', 'tick']):
            return 'checkbox_group'
        elif any(word in context_lower for word in ['choose one', 'select one']):
            return 'radio'
        
        # Default to text field
        return 'text'
    
    def is_required_field(self, label: str, context: str = "") -> bool:
        """Determine if a field is required"""
        required_indicators = ['required', 'must', 'shall', '*', 'mandatory']
        optional_indicators = ['optional', 'if applicable', 'if any', 'may']
        
        label_lower = label.lower()
        context_lower = context.lower()
        
        # Check for explicit indicators
        for indicator in required_indicators:
            if indicator in label_lower or indicator in context_lower:
                return True
        
        for indicator in optional_indicators:
            if indicator in label_lower or indicator in context_lower:
                return False
        
        # Common required fields in Ontario forms
        required_fields = ['name', 'address', 'court file number', 'date of birth']
        for field in required_fields:
            if field in label_lower:
                return True
        
        return False
    
    def extract_validation_rules(self, field_type: str, label: str) -> str:
        """Extract validation rules based on field type and label"""
        rules = []
        
        if field_type == 'date':
            rules.append('format:DD/MM/YYYY')
            if 'birth' in label.lower():
                rules.append('max:today')
                rules.append('min:1900-01-01')
            elif 'future' in label.lower():
                rules.append('min:today')
        
        elif field_type == 'sin':
            rules.append('format:XXX-XXX-XXX')
            rules.append('luhn_check')
        
        elif field_type == 'postal_code':
            rules.append('format:A1A 1A1')
            rules.append('canadian_postal')
        
        elif field_type == 'phone':
            rules.append('format:(XXX) XXX-XXXX')
            rules.append('digits:10')
        
        elif field_type == 'currency':
            rules.append('min:0')
            rules.append('decimal:2')
        
        elif field_type == 'email':
            rules.append('email')
        
        elif field_type == 'number':
            if 'age' in label.lower():
                rules.append('min:0')
                rules.append('max:120')
            elif 'children' in label.lower():
                rules.append('min:0')
                rules.append('max:20')
        
        return '|'.join(rules) if rules else ''

class PDFFormParser(FormParser):
    """Parser for PDF forms"""
    
    def extract_fields(self) -> List[FormField]:
        """Extract fields from PDF using multiple methods"""
        fields = []
        
        # Try different extraction methods
        fields.extend(self._extract_with_pdfplumber())
        fields.extend(self._extract_with_pymupdf())
        
        if GOOGLE_CLOUD_AVAILABLE:
            fields.extend(self._extract_with_google_ocr())
        
        # Deduplicate fields
        seen = set()
        unique_fields = []
        for field in fields:
            field_key = (field.field_name, field.page_number, field.field_type)
            if field_key not in seen:
                seen.add(field_key)
                unique_fields.append(field)
        
        return unique_fields
    
    def _extract_with_pdfplumber(self) -> List[FormField]:
        """Extract fields using pdfplumber"""
        fields = []
        
        with pdfplumber.open(self.form_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                # Extract text
                text = page.extract_text() or ""
                
                # Extract tables
                tables = page.extract_tables()
                for table_idx, table in enumerate(tables):
                    table_name = f"table_{page_num}_{table_idx}"
                    self.tables[table_name] = table
                    
                    # Process table cells as fields
                    for row_idx, row in enumerate(table):
                        for col_idx, cell in enumerate(row):
                            if cell and re.search(self.FIELD_PATTERNS['blank_field'], cell):
                                field = FormField(
                                    field_id=f"{self.form_number}_p{page_num}_t{table_idx}_r{row_idx}_c{col_idx}",
                                    field_name=f"table_field_{table_idx}_{row_idx}_{col_idx}",
                                    field_type=self.identify_field_type(cell),
                                    field_label=cell.replace('_', '').strip(),
                                    required=False,
                                    validation_rules="",
                                    max_length=None,
                                    options=None,
                                    table_name=table_name,
                                    table_row=row_idx,
                                    table_col=col_idx,
                                    page_number=page_num,
                                    x_position=None,
                                    y_position=None,
                                    width=None,
                                    height=None,
                                    default_value=None,
                                    help_text=None,
                                    depends_on=None
                                )
                                fields.append(field)
                
                # Extract form fields
                if hasattr(page, 'annots'):
                    for annot in page.annots or []:
                        if annot and annot.get('data'):
                            field_name = annot.get('data', {}).get('T', '')
                            field_type = annot.get('data', {}).get('FT', '')
                            
                            field = FormField(
                                field_id=f"{self.form_number}_p{page_num}_{field_name}",
                                field_name=field_name,
                                field_type=self._map_pdf_field_type(field_type),
                                field_label=field_name,
                                required=False,
                                validation_rules="",
                                max_length=None,
                                options=None,
                                table_name=None,
                                table_row=None,
                                table_col=None,
                                page_number=page_num,
                                x_position=annot.get('x0'),
                                y_position=annot.get('y0'),
                                width=annot.get('width'),
                                height=annot.get('height'),
                                default_value=None,
                                help_text=None,
                                depends_on=None
                            )
                            fields.append(field)
        
        return fields
    
    def _extract_with_pymupdf(self) -> List[FormField]:
        """Extract fields using PyMuPDF"""
        fields = []
        
        pdf = fitz.open(self.form_path)
        for page_num, page in enumerate(pdf, 1):
            # Get widgets (form fields)
            for widget in page.widgets():
                field = FormField(
                    field_id=f"{self.form_number}_p{page_num}_{widget.field_name}",
                    field_name=widget.field_name or f"field_{page_num}_{widget.rect}",
                    field_type=self._map_widget_type(widget.field_type),
                    field_label=widget.field_display or widget.field_name or "",
                    required=bool(widget.field_flags & 2),  # Required flag
                    validation_rules="",
                    max_length=widget.text_maxlen if hasattr(widget, 'text_maxlen') else None,
                    options=widget.choice_values if hasattr(widget, 'choice_values') else None,
                    table_name=None,
                    table_row=None,
                    table_col=None,
                    page_number=page_num,
                    x_position=widget.rect.x0,
                    y_position=widget.rect.y0,
                    width=widget.rect.width,
                    height=widget.rect.height,
                    default_value=widget.field_value,
                    help_text=None,
                    depends_on=None
                )
                fields.append(field)
        
        pdf.close()
        return fields
    
    def _extract_with_google_ocr(self) -> List[FormField]:
        """Extract fields using Google Cloud Vision/Document AI"""
        fields = []
        
        # This would require Google Cloud credentials setup
        # Placeholder for Google Cloud OCR implementation
        
        return fields
    
    def _map_pdf_field_type(self, pdf_type: str) -> str:
        """Map PDF field types to our field types"""
        mapping = {
            'Tx': 'text',
            'Ch': 'select',
            'Btn': 'checkbox',
            'Sig': 'signature'
        }
        return mapping.get(pdf_type, 'text')
    
    def _map_widget_type(self, widget_type: int) -> str:
        """Map PyMuPDF widget types to our field types"""
        mapping = {
            1: 'button',
            2: 'checkbox',
            3: 'radio',
            4: 'text',
            5: 'select',
            6: 'combo',
            7: 'signature'
        }
        return mapping.get(widget_type, 'text')

class WordFormParser(FormParser):
    """Parser for Word documents"""
    
    def extract_fields(self) -> List[FormField]:
        """Extract fields from Word document"""
        fields = []
        doc = Document(self.form_path)
        
        # Process paragraphs
        for para_idx, para in enumerate(doc.paragraphs):
            fields.extend(self._extract_fields_from_text(para.text, para_idx, 1))
        
        # Process tables
        for table_idx, table in enumerate(doc.tables):
            table_name = f"table_{table_idx}"
            table_data = []
            
            for row_idx, row in enumerate(table.rows):
                row_data = []
                for col_idx, cell in enumerate(row.cells):
                    cell_text = cell.text.strip()
                    row_data.append(cell_text)
                    
                    # Check if cell contains a field
                    if re.search(self.FIELD_PATTERNS['blank_field'], cell_text):
                        field = FormField(
                            field_id=f"{self.form_number}_t{table_idx}_r{row_idx}_c{col_idx}",
                            field_name=f"table_field_{table_idx}_{row_idx}_{col_idx}",
                            field_type=self.identify_field_type(cell_text),
                            field_label=self._get_cell_label(table, row_idx, col_idx),
                            required=self.is_required_field(cell_text),
                            validation_rules=self.extract_validation_rules(
                                self.identify_field_type(cell_text), 
                                cell_text
                            ),
                            max_length=None,
                            options=None,
                            table_name=table_name,
                            table_row=row_idx,
                            table_col=col_idx,
                            page_number=1,  # Word doesn't have page numbers readily
                            x_position=None,
                            y_position=None,
                            width=None,
                            height=None,
                            default_value=None,
                            help_text=None,
                            depends_on=None
                        )
                        fields.append(field)
                
                table_data.append(row_data)
            
            self.tables[table_name] = table_data
        
        # Process form fields (content controls)
        if hasattr(doc, 'element'):
            fields.extend(self._extract_content_controls(doc))
        
        return fields
    
    def _extract_fields_from_text(self, text: str, para_idx: int, page_num: int) -> List[FormField]:
        """Extract fields from paragraph text"""
        fields = []
        
        # Look for blank fields
        blank_fields = re.finditer(self.FIELD_PATTERNS['blank_field'], text)
        for match in blank_fields:
            # Try to find the label (text before the blank)
            label = text[:match.start()].strip().split('\n')[-1].strip()
            if not label:
                label = f"field_{para_idx}_{match.start()}"
            
            field = FormField(
                field_id=f"{self.form_number}_p{para_idx}_{match.start()}",
                field_name=self._sanitize_field_name(label),
                field_type=self.identify_field_type(text[match.start():], label),
                field_label=label,
                required=self.is_required_field(label, text),
                validation_rules=self.extract_validation_rules(
                    self.identify_field_type(text[match.start():], label),
                    label
                ),
                max_length=len(match.group()),
                options=None,
                table_name=None,
                table_row=None,
                table_col=None,
                page_number=page_num,
                x_position=None,
                y_position=None,
                width=None,
                height=None,
                default_value=None,
                help_text=None,
                depends_on=None
            )
            fields.append(field)
        
        # Look for checkboxes
        checkboxes = re.finditer(self.FIELD_PATTERNS['checkbox'], text)
        for match in checkboxes:
            label = match.group(1).strip()
            field = FormField(
                field_id=f"{self.form_number}_cb_{para_idx}_{match.start()}",
                field_name=self._sanitize_field_name(label),
                field_type='checkbox',
                field_label=label,
                required=False,
                validation_rules="",
                max_length=None,
                options=['checked', 'unchecked'],
                table_name=None,
                table_row=None,
                table_col=None,
                page_number=page_num,
                x_position=None,
                y_position=None,
                width=None,
                height=None,
                default_value='unchecked',
                help_text=None,
                depends_on=None
            )
            fields.append(field)
        
        return fields
    
    def _extract_content_controls(self, doc) -> List[FormField]:
        """Extract content control fields from Word document"""
        fields = []
        
        # This requires python-docx2txt or similar library for content controls
        # Placeholder for now
        
        return fields
    
    def _get_cell_label(self, table, row_idx: int, col_idx: int) -> str:
        """Get label for a table cell (usually from header row or first column)"""
        label_parts = []
        
        # Try to get column header
        if row_idx > 0 and len(table.rows) > 0:
            header_cell = table.rows[0].cells[col_idx].text.strip()
            if header_cell:
                label_parts.append(header_cell)
        
        # Try to get row label
        if col_idx > 0:
            row_label = table.rows[row_idx].cells[0].text.strip()
            if row_label:
                label_parts.append(row_label)
        
        return " - ".join(label_parts) if label_parts else f"cell_{row_idx}_{col_idx}"
    
    def _sanitize_field_name(self, text: str) -> str:
        """Sanitize text to create valid field name"""
        # Remove special characters and spaces
        name = re.sub(r'[^\w\s]', '', text)
        # Replace spaces with underscores
        name = re.sub(r'\s+', '_', name)
        # Convert to lowercase
        name = name.lower()
        # Limit length
        name = name[:50]
        return name if name else "unnamed_field"

class FormCSVWriter:
    """Write form fields to CSV files"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def write_form_fields(self, form_number: str, fields: List[FormField], tables: Dict[str, List[List[str]]]):
        """Write form fields to CSV"""
        # Write main fields CSV
        fields_file = self.output_dir / f"{form_number}_fields.csv"
        with open(fields_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'field_id', 'field_name', 'field_type', 'field_label', 'required',
                'validation_rules', 'max_length', 'options', 'table_name',
                'table_row', 'table_col', 'page_number', 'x_position', 'y_position',
                'width', 'height', 'default_value', 'help_text', 'depends_on'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for field in fields:
                row = field.to_dict()
                # Convert lists to JSON strings for CSV
                if row.get('options'):
                    row['options'] = json.dumps(row['options'])
                writer.writerow(row)
        
        # Write tables CSV
        if tables:
            tables_file = self.output_dir / f"{form_number}_tables.csv"
            with open(tables_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['table_name', 'row_index', 'col_index', 'cell_value'])
                
                for table_name, table_data in tables.items():
                    for row_idx, row in enumerate(table_data):
                        for col_idx, cell in enumerate(row):
                            writer.writerow([table_name, row_idx, col_idx, cell])
        
        print(f"Wrote {len(fields)} fields to {fields_file}")
        if tables:
            print(f"Wrote {len(tables)} tables to {tables_file}")
        
        return fields_file

class YAMLGenerator:
    """Generate docassemble YAML from CSV fields"""
    
    def __init__(self, csv_file: str, output_dir: str):
        self.csv_file = Path(csv_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_yaml(self, form_number: str, form_title: str) -> str:
        """Generate docassemble YAML from CSV fields"""
        fields = self._read_csv_fields()
        
        yaml_content = self._generate_yaml_header(form_number, form_title)
        yaml_content += self._generate_objects_block(fields)
        yaml_content += self._generate_questions(fields)
        yaml_content += self._generate_review_screen(fields)
        yaml_content += self._generate_attachment(form_number, fields)
        
        output_file = self.output_dir / f"{form_number}_interview.yml"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        print(f"Generated YAML interview: {output_file}")
        return str(output_file)
    
    def _read_csv_fields(self) -> List[Dict]:
        """Read fields from CSV file"""
        fields = []
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse JSON fields
                if row.get('options'):
                    try:
                        row['options'] = json.loads(row['options'])
                    except:
                        row['options'] = []
                fields.append(row)
        return fields
    
    def _generate_yaml_header(self, form_number: str, form_title: str) -> str:
        """Generate YAML header"""
        return f"""---
metadata:
  title: |
    {form_title}
  short title: |
    {form_number}
  description: |
    Ontario family law form {form_number} interview
  authors:
    - name: Ontario Family Law Forms System
  revision_date: {datetime.now().strftime('%Y-%m-%d')}
---
include:
  - ontario-family-law-common.yml
---
features:
  navigation: True
  progress bar: True
  question back button: True
  navigation back button: True
---
"""
    
    def _generate_objects_block(self, fields: List[Dict]) -> str:
        """Generate objects block"""
        objects = """objects:
  - applicant: Individual
  - respondent: Individual
  - children: DAList.using(object_type=Individual)
  - court_info: DAObject
  - financial_info: DAObject
---
"""
        return objects
    
    def _generate_questions(self, fields: List[Dict]) -> str:
        """Generate question blocks for fields"""
        questions = ""
        
        # Group fields by page/table
        grouped_fields = {}
        for field in fields:
            key = field.get('table_name') or f"page_{field.get('page_number', 1)}"
            if key not in grouped_fields:
                grouped_fields[key] = []
            grouped_fields[key].append(field)
        
        # Generate question for each group
        for group_key, group_fields in grouped_fields.items():
            questions += self._generate_question_block(group_key, group_fields)
        
        return questions
    
    def _generate_question_block(self, group_name: str, fields: List[Dict]) -> str:
        """Generate a single question block"""
        question = f"""question: |
  {group_name.replace('_', ' ').title()}
fields:
"""
        
        for field in fields:
            field_yaml = self._generate_field_yaml(field)
            question += field_yaml
        
        question += "---\n"
        return question
    
    def _generate_field_yaml(self, field: Dict) -> str:
        """Generate YAML for a single field"""
        field_name = field['field_name']
        field_type = field['field_type']
        field_label = field['field_label']
        required = field['required'] == 'True'
        
        yaml = f"  - {field_label}: {field_name}\n"
        
        # Add field attributes based on type
        if field_type == 'date':
            yaml += "    datatype: date\n"
        elif field_type == 'currency':
            yaml += "    datatype: currency\n"
            yaml += "    min: 0\n"
        elif field_type == 'number':
            yaml += "    datatype: number\n"
        elif field_type == 'email':
            yaml += "    datatype: email\n"
        elif field_type == 'checkbox':
            yaml += "    datatype: yesno\n"
        elif field_type == 'radio' and field.get('options'):
            yaml += "    datatype: radio\n"
            yaml += "    choices:\n"
            for option in field['options']:
                yaml += f"      - {option}\n"
        elif field_type == 'select' and field.get('options'):
            yaml += "    datatype: dropdown\n"
            yaml += "    choices:\n"
            for option in field['options']:
                yaml += f"      - {option}\n"
        
        if required:
            yaml += "    required: True\n"
        
        if field.get('validation_rules'):
            yaml += f"    validation: {field['validation_rules']}\n"
        
        if field.get('help_text'):
            yaml += f"    help: |\n      {field['help_text']}\n"
        
        return yaml
    
    def _generate_review_screen(self, fields: List[Dict]) -> str:
        """Generate review screen"""
        review = """question: |
  Review your answers
review:
"""
        for field in fields:
            if field['field_name'] and field['field_label']:
                review += f"  - {field['field_label']}: {field['field_name']}\n"
        
        review += "---\n"
        return review
    
    def _generate_attachment(self, form_number: str, fields: List[Dict]) -> str:
        """Generate attachment block"""
        attachment = f"""mandatory: True
question: |
  Your form is ready
subquestion: |
  Your {form_number} has been prepared. You can download it below.
attachment:
  name: {form_number}
  filename: {form_number}
  pdf template file: {form_number.lower()}.pdf
  fields:
"""
        
        for field in fields:
            if field['field_name']:
                attachment += f"    {field['field_name']}: ${{{{ {field['field_name']} }}}}\n"
        
        attachment += "---\n"
        return attachment

def process_all_forms(input_dir: str, output_dir: str):
    """Process all forms in the input directory"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    csv_dir = output_path / "csv_files"
    yaml_dir = output_path / "yaml_files"
    csv_dir.mkdir(exist_ok=True)
    yaml_dir.mkdir(exist_ok=True)
    
    # Process each form
    for form_file in input_path.glob("*"):
        if form_file.suffix.lower() in ['.pdf', '.docx', '.doc']:
            print(f"\nProcessing: {form_file.name}")
            
            # Extract form number from filename
            form_number_match = re.search(r'form[_\s]+(\d+[a-zA-Z]?(?:\.\d+)?)', form_file.name, re.IGNORECASE)
            if form_number_match:
                form_number = f"form_{form_number_match.group(1).replace('.', '_')}"
            else:
                form_number = form_file.stem
            
            try:
                # Parse the form
                if form_file.suffix.lower() == '.pdf':
                    parser = PDFFormParser(str(form_file), form_number)
                else:
                    parser = WordFormParser(str(form_file), form_number)
                
                fields = parser.extract_fields()
                
                # Write to CSV
                csv_writer = FormCSVWriter(str(csv_dir))
                csv_file = csv_writer.write_form_fields(form_number, fields, parser.tables)
                
                # Generate YAML
                yaml_generator = YAMLGenerator(csv_file, str(yaml_dir))
                form_title = form_file.stem.replace('_', ' ').title()
                yaml_generator.generate_yaml(form_number, form_title)
                
                print(f"✓ Successfully processed {form_file.name}")
                print(f"  - Found {len(fields)} fields")
                print(f"  - Found {len(parser.tables)} tables")
                
            except Exception as e:
                print(f"✗ Error processing {form_file.name}: {str(e)}")
                import traceback
                traceback.print_exc()

def main():
    """Main function"""
    # Set up directories
    base_dir = Path(__file__).parent
    forms_dir = base_dir / "ontario_forms"  # Directory with downloaded forms
    output_dir = base_dir / "form_analysis_output"
    
    print("Ontario Family Law Forms Parser")
    print("=" * 50)
    print(f"Input directory: {forms_dir}")
    print(f"Output directory: {output_dir}")
    
    if not forms_dir.exists():
        print(f"Error: Forms directory not found: {forms_dir}")
        print("Please run the download script first to get the forms.")
        return
    
    # Process all forms
    process_all_forms(str(forms_dir), str(output_dir))
    
    print("\n" + "=" * 50)
    print("Processing complete!")
    print(f"CSV files saved to: {output_dir}/csv_files")
    print(f"YAML files saved to: {output_dir}/yaml_files")

if __name__ == "__main__":
    main()