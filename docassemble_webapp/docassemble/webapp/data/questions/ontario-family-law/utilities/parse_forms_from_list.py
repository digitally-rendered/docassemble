#!/usr/bin/env python3
"""
Parse Ontario Family Law Forms from CSV list
Extracts fields from both PDF and DOCX files
"""

import csv
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Document parsing libraries
import PyPDF2
import pdfplumber
from docx import Document
import fitz  # PyMuPDF

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class FormField:
    """Represents a single form field"""
    field_id: str
    field_name: str
    field_type: str  # text, date, checkbox, radio, number, currency, etc.
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

class FormParser:
    """Base parser for form documents"""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.form_number = self.extract_form_number()
        self.fields = []
        
    def extract_form_number(self) -> str:
        """Extract form number from filename"""
        import re
        filename = self.file_path.name.lower()
        
        # Try to match form_XX pattern
        match = re.search(r'form[_\-](\d+(?:\.\d+)?[a-zA-Z]?)', filename)
        if match:
            return match.group(1).upper()
        
        # Try to match flr-XX pattern
        match = re.search(r'flr[_\-](\d+(?:\.\d+)?[a-zA-Z]?)', filename)
        if match:
            return match.group(1).upper()
        
        return ""
    
    def parse(self) -> List[FormField]:
        """Parse the form and extract fields"""
        ext = self.file_path.suffix.lower()
        
        if ext == '.pdf':
            return self.parse_pdf()
        elif ext in ['.docx', '.doc']:
            return self.parse_docx()
        else:
            logger.warning(f"Unsupported file type: {ext}")
            return []
    
    def parse_pdf(self) -> List[FormField]:
        """Parse PDF form"""
        fields = []
        
        try:
            # Method 1: PyPDF2 for form fields
            fields.extend(self._parse_pdf_pypdf2())
        except Exception as e:
            logger.debug(f"PyPDF2 parsing failed: {e}")
        
        try:
            # Method 2: pdfplumber for text extraction
            fields.extend(self._parse_pdf_pdfplumber())
        except Exception as e:
            logger.debug(f"pdfplumber parsing failed: {e}")
        
        try:
            # Method 3: PyMuPDF for better field detection
            fields.extend(self._parse_pdf_pymupdf())
        except Exception as e:
            logger.debug(f"PyMuPDF parsing failed: {e}")
        
        # Deduplicate fields
        unique_fields = self._deduplicate_fields(fields)
        
        return unique_fields
    
    def _parse_pdf_pypdf2(self) -> List[FormField]:
        """Parse PDF using PyPDF2"""
        fields = []
        
        with open(self.file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Check for form fields
            if '/AcroForm' in pdf_reader.trailer['/Root']:
                for page_num, page in enumerate(pdf_reader.pages):
                    if '/Annots' in page:
                        for annot_ref in page['/Annots']:
                            annot = annot_ref.get_object()
                            if annot.get('/FT'):  # Field Type exists
                                field = self._extract_pypdf2_field(annot, page_num + 1)
                                if field:
                                    fields.append(field)
        
        return fields
    
    def _extract_pypdf2_field(self, annot: Dict, page_num: int) -> Optional[FormField]:
        """Extract field from PyPDF2 annotation"""
        try:
            field_type_map = {
                '/Tx': 'text',
                '/Ch': 'choice',
                '/Btn': 'button',
                '/Sig': 'signature'
            }
            
            field_type = field_type_map.get(annot.get('/FT'), 'text')
            field_name = annot.get('/T', '')
            field_value = annot.get('/V', '')
            
            # Handle different field types
            if field_type == 'button':
                # Check if checkbox or radio
                if annot.get('/Ff', 0) & 0x10000:  # Radio button
                    field_type = 'radio'
                else:
                    field_type = 'checkbox'
            
            return FormField(
                field_id=f"pdf_field_{page_num}_{field_name}",
                field_name=str(field_name),
                field_type=field_type,
                field_label=str(field_name).replace('_', ' ').title(),
                required=bool(annot.get('/Ff', 0) & 0x2),  # Required flag
                page_number=page_num,
                field_context=f"Page {page_num}"
            )
        except Exception as e:
            logger.debug(f"Failed to extract PyPDF2 field: {e}")
            return None
    
    def _parse_pdf_pdfplumber(self) -> List[FormField]:
        """Parse PDF using pdfplumber"""
        fields = []
        
        with pdfplumber.open(self.file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                # Extract text
                text = page.extract_text() or ""
                
                # Look for field patterns
                fields.extend(self._extract_fields_from_text(text, page_num))
                
                # Extract tables
                tables = page.extract_tables()
                for table_idx, table in enumerate(tables):
                    fields.extend(self._extract_fields_from_table(table, page_num, table_idx))
        
        return fields
    
    def _parse_pdf_pymupdf(self) -> List[FormField]:
        """Parse PDF using PyMuPDF"""
        fields = []
        
        doc = fitz.open(self.file_path)
        
        for page_num, page in enumerate(doc, 1):
            # Get form widgets
            for widget in page.widgets():
                field = self._extract_pymupdf_field(widget, page_num)
                if field:
                    fields.append(field)
            
            # Also extract text patterns
            text = page.get_text()
            fields.extend(self._extract_fields_from_text(text, page_num))
        
        doc.close()
        
        return fields
    
    def _extract_pymupdf_field(self, widget, page_num: int) -> Optional[FormField]:
        """Extract field from PyMuPDF widget"""
        try:
            field_type_map = {
                fitz.PDF_WIDGET_TYPE_TEXT: 'text',
                fitz.PDF_WIDGET_TYPE_CHECKBOX: 'checkbox',
                fitz.PDF_WIDGET_TYPE_RADIOBUTTON: 'radio',
                fitz.PDF_WIDGET_TYPE_LISTBOX: 'select',
                fitz.PDF_WIDGET_TYPE_COMBOBOX: 'select'
            }
            
            field_type = field_type_map.get(widget.field_type, 'text')
            
            return FormField(
                field_id=f"widget_{page_num}_{widget.field_name}",
                field_name=widget.field_name or f"field_{page_num}",
                field_type=field_type,
                field_label=widget.field_label or widget.field_name or "",
                required=widget.field_flags & 2 != 0,
                page_number=page_num,
                coordinates={
                    "x0": widget.rect.x0,
                    "y0": widget.rect.y0,
                    "x1": widget.rect.x1,
                    "y1": widget.rect.y1
                },
                field_context=f"Page {page_num}"
            )
        except Exception as e:
            logger.debug(f"Failed to extract PyMuPDF field: {e}")
            return None
    
    def parse_docx(self) -> List[FormField]:
        """Parse DOCX form"""
        fields = []
        
        try:
            doc = Document(self.file_path)
            
            # Extract from paragraphs
            for para_idx, paragraph in enumerate(doc.paragraphs):
                fields.extend(self._extract_fields_from_text(paragraph.text, para_idx))
            
            # Extract from tables
            for table_idx, table in enumerate(doc.tables):
                fields.extend(self._extract_docx_table_fields(table, table_idx))
            
            # Extract from content controls (form fields)
            fields.extend(self._extract_docx_content_controls(doc))
            
        except Exception as e:
            logger.error(f"Failed to parse DOCX: {e}")
        
        # Deduplicate
        return self._deduplicate_fields(fields)
    
    def _extract_docx_table_fields(self, table, table_idx: int) -> List[FormField]:
        """Extract fields from DOCX table"""
        fields = []
        
        for row_idx, row in enumerate(table.rows):
            row_text = []
            for cell in row.cells:
                text = cell.text.strip()
                if text:
                    row_text.append(text)
            
            # Look for field patterns in row
            full_text = " ".join(row_text)
            if self._looks_like_field(full_text):
                fields.append(FormField(
                    field_id=f"table_{table_idx}_row_{row_idx}",
                    field_name=self._sanitize_field_name(full_text),
                    field_type=self._detect_field_type(full_text),
                    field_label=full_text[:100],
                    table_name=f"Table {table_idx + 1}",
                    table_row=row_idx,
                    field_context=f"Table {table_idx + 1}, Row {row_idx + 1}"
                ))
        
        return fields
    
    def _extract_docx_content_controls(self, doc) -> List[FormField]:
        """Extract content controls from DOCX"""
        fields = []
        
        # Note: python-docx doesn't directly support content controls
        # This is a placeholder for more advanced extraction
        # Would need to use lxml to parse the underlying XML
        
        return fields
    
    def _extract_fields_from_text(self, text: str, context_id: int) -> List[FormField]:
        """Extract fields from text using patterns"""
        fields = []
        
        if not text:
            return fields
        
        # Common field patterns
        patterns = [
            (r'(?:First|Last|Middle)\s+Name\s*[:_]?\s*_{3,}', 'text', 'name'),
            (r'Date\s+of\s+Birth\s*[:_]?\s*_{3,}', 'date', 'birthdate'),
            (r'Address\s*[:_]?\s*_{3,}', 'text', 'address'),
            (r'Phone\s*(?:Number)?\s*[:_]?\s*_{3,}', 'phone', 'phone'),
            (r'Email\s*(?:Address)?\s*[:_]?\s*_{3,}', 'email', 'email'),
            (r'(?:Court\s+)?File\s+(?:Number|No\.?)\s*[:_]?\s*_{3,}', 'text', 'file_number'),
            (r'□\s*(.+?)(?:\s*□|$)', 'checkbox', 'checkbox'),
            (r'○\s*(.+?)(?:\s*○|$)', 'radio', 'radio'),
            (r'\$\s*_{3,}', 'currency', 'amount'),
            (r'(\w+[\s\w]*?)\s*[:_]\s*_{3,}', 'text', 'generic'),
        ]
        
        for pattern, field_type, field_category in patterns:
            import re
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                label = match.group(1) if len(match.groups()) > 0 else match.group(0)
                label = label.strip(' :_')
                
                if label and len(label) > 2:
                    fields.append(FormField(
                        field_id=f"{field_category}_{context_id}_{len(fields)}",
                        field_name=self._sanitize_field_name(label),
                        field_type=field_type,
                        field_label=label,
                        field_context=f"Section {context_id}"
                    ))
        
        return fields
    
    def _looks_like_field(self, text: str) -> bool:
        """Check if text looks like a form field"""
        indicators = ['___', '[ ]', '( )', '□', '○', 'Name:', 'Date:', 'Address:', '$']
        text_lower = text.lower()
        return any(ind in text or ind.lower() in text_lower for ind in indicators)
    
    def _detect_field_type(self, text: str) -> str:
        """Detect field type from text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['date', 'when', 'born']):
            return 'date'
        elif any(word in text_lower for word in ['amount', 'value', 'income', '$']):
            return 'currency'
        elif any(word in text_lower for word in ['email', 'e-mail']):
            return 'email'
        elif any(word in text_lower for word in ['phone', 'telephone', 'fax']):
            return 'phone'
        elif any(word in text_lower for word in ['number', 'count', '#']):
            return 'number'
        elif '□' in text or '[ ]' in text:
            return 'checkbox'
        elif '○' in text or '( )' in text:
            return 'radio'
        
        return 'text'
    
    def _sanitize_field_name(self, text: str) -> str:
        """Create valid field name from text"""
        import re
        name = re.sub(r'[^a-zA-Z0-9_]', '_', text)
        name = re.sub(r'_+', '_', name)
        name = name.strip('_').lower()[:50]
        return name or "field"
    
    def _deduplicate_fields(self, fields: List[FormField]) -> List[FormField]:
        """Remove duplicate fields"""
        seen = set()
        unique = []
        
        for field in fields:
            key = (field.field_name, field.field_type, field.page_number or field.table_row or 0)
            if key not in seen:
                seen.add(key)
                unique.append(field)
        
        return unique

def parse_forms_from_csv(csv_file: str = "forms_list.csv", output_dir: str = "parsed_forms"):
    """Parse all forms listed in CSV file"""
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            file_path = row['full_path']
            form_number = row['form_number']
            category = row['category']
            
            logger.info(f"Parsing Form {form_number}: {row['filename']}")
            
            try:
                parser = FormParser(file_path)
                fields = parser.parse()
                
                # Save fields to CSV
                if fields:
                    csv_output = output_path / f"form_{form_number}_fields.csv"
                    save_fields_to_csv(fields, csv_output)
                    
                    # Save fields to JSON
                    json_output = output_path / f"form_{form_number}_fields.json"
                    save_fields_to_json(fields, json_output)
                    
                    logger.info(f"  ✓ Extracted {len(fields)} fields")
                    
                    results.append({
                        "form_number": form_number,
                        "filename": row['filename'],
                        "category": category,
                        "fields_count": len(fields),
                        "status": "success",
                        "csv_output": str(csv_output),
                        "json_output": str(json_output)
                    })
                else:
                    logger.warning(f"  ⚠ No fields extracted")
                    results.append({
                        "form_number": form_number,
                        "filename": row['filename'],
                        "category": category,
                        "fields_count": 0,
                        "status": "no_fields"
                    })
                    
            except Exception as e:
                logger.error(f"  ✗ Failed: {e}")
                results.append({
                    "form_number": form_number,
                    "filename": row['filename'],
                    "category": category,
                    "fields_count": 0,
                    "status": "error",
                    "error": str(e)
                })
    
    # Save summary
    summary_file = output_path / "parsing_summary.json"
    with open(summary_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_forms": len(results),
            "successful": len([r for r in results if r["status"] == "success"]),
            "no_fields": len([r for r in results if r["status"] == "no_fields"]),
            "errors": len([r for r in results if r["status"] == "error"]),
            "results": results
        }, f, indent=2)
    
    logger.info(f"\nParsing complete. Summary saved to {summary_file}")
    
    return results

def save_fields_to_csv(fields: List[FormField], output_file: Path):
    """Save fields to CSV file"""
    with open(output_file, 'w', newline='') as f:
        fieldnames = ['field_id', 'field_name', 'field_type', 'field_label', 
                     'required', 'field_context', 'page_number', 'table_name']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for field in fields:
            writer.writerow({
                'field_id': field.field_id,
                'field_name': field.field_name,
                'field_type': field.field_type,
                'field_label': field.field_label,
                'required': field.required,
                'field_context': field.field_context,
                'page_number': field.page_number,
                'table_name': field.table_name
            })

def save_fields_to_json(fields: List[FormField], output_file: Path):
    """Save fields to JSON file"""
    with open(output_file, 'w') as f:
        json.dump([asdict(field) for field in fields], f, indent=2)

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Parse Ontario Family Law Forms from CSV list"
    )
    parser.add_argument(
        "--csv",
        default="forms_list.csv",
        help="CSV file containing forms list"
    )
    parser.add_argument(
        "--output",
        default="parsed_forms",
        help="Output directory for parsed fields"
    )
    
    args = parser.parse_args()
    
    results = parse_forms_from_csv(args.csv, args.output)
    
    # Print summary
    successful = len([r for r in results if r["status"] == "success"])
    no_fields = len([r for r in results if r["status"] == "no_fields"])
    errors = len([r for r in results if r["status"] == "error"])
    
    print("\n" + "="*60)
    print("PARSING SUMMARY")
    print("="*60)
    print(f"Total forms processed: {len(results)}")
    print(f"✓ Successful: {successful}")
    print(f"⚠ No fields found: {no_fields}")
    print(f"✗ Errors: {errors}")
    
    if successful > 0:
        print(f"\nExtracted fields saved to {args.output}/")

if __name__ == "__main__":
    main()