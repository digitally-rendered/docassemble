#!/usr/bin/env python3
"""
Intelligent Form Parser with Multi-Strategy Approach
Combines raw parsing, OCR, and AI-based recognition
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import re

# Basic parsing
import PyPDF2
import pdfplumber
from docx import Document
import fitz  # PyMuPDF

# Image processing
from PIL import Image
import numpy as np

# OCR
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

# Cloud services (optional)
try:
    from google.cloud import vision
    from google.cloud import documentai
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ExtractedField:
    """Enhanced field with confidence and extraction method"""
    field_name: str
    field_type: str
    field_label: str
    value: Optional[str] = None
    required: bool = False
    confidence: float = 0.0
    extraction_method: str = ""
    page_number: int = 0
    coordinates: Optional[Dict] = None
    context: str = ""
    table_info: Optional[Dict] = None
    validation_rules: Optional[List[str]] = None

class IntelligentFormParser:
    """
    Multi-strategy form parser that combines:
    1. Native PDF/DOCX parsing
    2. OCR for scanned documents
    3. AI-based field detection
    4. Table extraction
    5. Pattern recognition
    """
    
    def __init__(self, file_path: str, use_ocr: bool = True, use_ai: bool = False):
        self.file_path = Path(file_path)
        self.use_ocr = use_ocr and TESSERACT_AVAILABLE
        self.use_ai = use_ai
        self.fields = []
        self.confidence_threshold = 0.5
        
    def parse(self) -> List[ExtractedField]:
        """
        Parse form using multiple strategies and combine results
        """
        all_fields = []
        
        # Strategy 1: Native parsing
        logger.info("Strategy 1: Native document parsing...")
        native_fields = self._parse_native()
        all_fields.extend(native_fields)
        
        # Strategy 2: Pattern-based extraction
        logger.info("Strategy 2: Pattern-based extraction...")
        pattern_fields = self._parse_patterns()
        all_fields.extend(pattern_fields)
        
        # Strategy 3: Table extraction
        logger.info("Strategy 3: Table extraction...")
        table_fields = self._parse_tables()
        all_fields.extend(table_fields)
        
        # Strategy 4: OCR (if needed and available)
        if self.use_ocr and self._needs_ocr():
            logger.info("Strategy 4: OCR extraction...")
            ocr_fields = self._parse_with_ocr()
            all_fields.extend(ocr_fields)
        
        # Strategy 5: AI-based extraction (if enabled)
        if self.use_ai:
            logger.info("Strategy 5: AI-based extraction...")
            ai_fields = self._parse_with_ai()
            all_fields.extend(ai_fields)
        
        # Merge and deduplicate fields
        merged_fields = self._merge_fields(all_fields)
        
        # Post-processing
        final_fields = self._post_process(merged_fields)
        
        return final_fields
    
    def _parse_native(self) -> List[ExtractedField]:
        """Native PDF/DOCX parsing"""
        ext = self.file_path.suffix.lower()
        
        if ext == '.pdf':
            return self._parse_pdf_native()
        elif ext in ['.docx', '.doc']:
            return self._parse_docx_native()
        
        return []
    
    def _parse_pdf_native(self) -> List[ExtractedField]:
        """Parse PDF using native libraries"""
        fields = []
        
        # Try PyMuPDF first (best for forms)
        try:
            doc = fitz.open(self.file_path)
            
            for page_num, page in enumerate(doc, 1):
                # Extract form widgets
                for widget in page.widgets():
                    field = ExtractedField(
                        field_name=widget.field_name or f"field_{page_num}_{len(fields)}",
                        field_type=self._get_widget_type(widget),
                        field_label=widget.field_label or widget.field_name or "",
                        value=widget.field_value,
                        required=widget.field_flags & 2 != 0,
                        confidence=0.9,
                        extraction_method="pymupdf_widget",
                        page_number=page_num,
                        coordinates={
                            "x0": widget.rect.x0,
                            "y0": widget.rect.y0,
                            "x1": widget.rect.x1,
                            "y1": widget.rect.y1
                        }
                    )
                    fields.append(field)
            
            doc.close()
        except Exception as e:
            logger.debug(f"PyMuPDF parsing error: {e}")
        
        # Fallback to PyPDF2
        if not fields:
            try:
                with open(self.file_path, 'rb') as file:
                    pdf = PyPDF2.PdfReader(file)
                    
                    if '/AcroForm' in pdf.trailer['/Root']:
                        for page_num, page in enumerate(pdf.pages, 1):
                            if '/Annots' in page:
                                for annot_ref in page['/Annots']:
                                    annot = annot_ref.get_object()
                                    if annot.get('/FT'):
                                        field = self._extract_pypdf2_field(annot, page_num)
                                        if field:
                                            fields.append(field)
            except Exception as e:
                logger.debug(f"PyPDF2 parsing error: {e}")
        
        return fields
    
    def _parse_docx_native(self) -> List[ExtractedField]:
        """Parse DOCX using python-docx"""
        fields = []
        
        try:
            doc = Document(self.file_path)
            
            # Parse paragraphs for field patterns
            for para_idx, para in enumerate(doc.paragraphs):
                if self._looks_like_field(para.text):
                    fields.extend(self._extract_fields_from_text(
                        para.text, 
                        context=f"Paragraph {para_idx}",
                        method="docx_paragraph"
                    ))
            
            # Parse tables
            for table_idx, table in enumerate(doc.tables):
                for row_idx, row in enumerate(table.rows):
                    row_text = " ".join(cell.text for cell in row.cells)
                    if self._looks_like_field(row_text):
                        field = ExtractedField(
                            field_name=self._sanitize_name(row_text),
                            field_type=self._detect_field_type(row_text),
                            field_label=row_text[:100],
                            confidence=0.7,
                            extraction_method="docx_table",
                            table_info={
                                "table_index": table_idx,
                                "row_index": row_idx
                            },
                            context=f"Table {table_idx + 1}, Row {row_idx + 1}"
                        )
                        fields.append(field)
        
        except Exception as e:
            logger.error(f"DOCX parsing error: {e}")
        
        return fields
    
    def _parse_patterns(self) -> List[ExtractedField]:
        """Extract fields using regex patterns"""
        fields = []
        text = self._get_document_text()
        
        # Ontario-specific patterns
        patterns = [
            # Names
            (r'(?:First|Last|Middle)\s+Name\s*[:_]?\s*_{3,}|\[.*?\]', 'text', 'name', 0.8),
            (r'Full\s+Legal\s+Name\s*[:_]?\s*_{3,}|\[.*?\]', 'text', 'full_name', 0.9),
            
            # Dates
            (r'Date\s+of\s+Birth\s*[:_]?\s*_{3,}|\[DD/MM/YYYY\]', 'date', 'birthdate', 0.9),
            (r'(?:Date|When)\s+\w+\s*[:_]?\s*_{3,}', 'date', 'date', 0.7),
            
            # Addresses
            (r'(?:Street\s+)?Address\s*[:_]?\s*_{3,}', 'text', 'address', 0.8),
            (r'City\s*[:_]?\s*_{3,}', 'text', 'city', 0.8),
            (r'Postal\s+Code\s*[:_]?\s*[A-Z]\d[A-Z]\s*\d[A-Z]\d|_{6}', 'text', 'postal_code', 0.9),
            
            # Contact
            (r'Phone\s*(?:Number)?\s*[:_]?\s*\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|_{10,}', 'phone', 'phone', 0.8),
            (r'Email\s*(?:Address)?\s*[:_]?\s*\S+@\S+|_{20,}', 'email', 'email', 0.8),
            
            # Legal
            (r'Court\s+File\s+(?:Number|No\.?)\s*[:_]?\s*_{10,}', 'text', 'court_file_number', 0.9),
            (r'LSO\s+(?:Number|#)\s*[:_]?\s*\d{5}[A-Z]?|_{6}', 'text', 'lso_number', 0.9),
            
            # Financial
            (r'\$\s*_{5,}|\$\s*\d+(?:,\d{3})*(?:\.\d{2})?', 'currency', 'amount', 0.8),
            (r'Income\s*[:_]?\s*\$?\s*_{5,}', 'currency', 'income', 0.8),
            
            # Checkboxes
            (r'□\s*(.+?)(?:\s*□|$)', 'checkbox', 'checkbox', 0.7),
            (r'\[\s*\]\s*(.+?)(?:\s*\[|$)', 'checkbox', 'checkbox', 0.7),
            
            # Radio buttons
            (r'○\s*(.+?)(?:\s*○|$)', 'radio', 'radio', 0.7),
            (r'\(\s*\)\s*(.+?)(?:\s*\(|$)', 'radio', 'radio', 0.7),
        ]
        
        for pattern, field_type, field_category, confidence in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match_idx, match in enumerate(matches):
                label = match.group(1) if len(match.groups()) > 0 else match.group(0)
                
                field = ExtractedField(
                    field_name=f"{field_category}_{match_idx}",
                    field_type=field_type,
                    field_label=label.strip(' :_[]()'),
                    confidence=confidence,
                    extraction_method="pattern_matching",
                    context=text[max(0, match.start()-50):min(len(text), match.end()+50)]
                )
                fields.append(field)
        
        return fields
    
    def _parse_tables(self) -> List[ExtractedField]:
        """Extract structured data from tables"""
        fields = []
        
        if self.file_path.suffix.lower() == '.pdf':
            fields.extend(self._parse_pdf_tables())
        elif self.file_path.suffix.lower() in ['.docx', '.doc']:
            fields.extend(self._parse_docx_tables())
        
        return fields
    
    def _parse_pdf_tables(self) -> List[ExtractedField]:
        """Extract tables from PDF"""
        fields = []
        
        try:
            with pdfplumber.open(self.file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    tables = page.extract_tables()
                    
                    for table_idx, table in enumerate(tables):
                        if not table:
                            continue
                        
                        # Analyze table structure
                        headers = table[0] if table else []
                        
                        for row_idx, row in enumerate(table[1:], 1):
                            for col_idx, cell in enumerate(row):
                                if cell and self._looks_like_field(cell):
                                    header = headers[col_idx] if col_idx < len(headers) else ""
                                    
                                    field = ExtractedField(
                                        field_name=f"table_{table_idx}_r{row_idx}_c{col_idx}",
                                        field_type=self._detect_field_type(cell),
                                        field_label=f"{header}: {cell}" if header else cell,
                                        confidence=0.75,
                                        extraction_method="pdf_table",
                                        page_number=page_num,
                                        table_info={
                                            "table_index": table_idx,
                                            "row": row_idx,
                                            "column": col_idx,
                                            "header": header
                                        },
                                        context=f"Page {page_num}, Table {table_idx + 1}"
                                    )
                                    fields.append(field)
        
        except Exception as e:
            logger.debug(f"PDF table extraction error: {e}")
        
        return fields
    
    def _parse_docx_tables(self) -> List[ExtractedField]:
        """Extract tables from DOCX"""
        # Already handled in _parse_docx_native
        return []
    
    def _parse_with_ocr(self) -> List[ExtractedField]:
        """Use OCR for scanned documents"""
        fields = []
        
        if not TESSERACT_AVAILABLE:
            return fields
        
        try:
            # Convert PDF pages to images
            if self.file_path.suffix.lower() == '.pdf':
                doc = fitz.open(self.file_path)
                
                for page_num, page in enumerate(doc, 1):
                    # Convert page to image
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x scaling for better OCR
                    img_data = pix.pil_tobytes(format="PNG")
                    img = Image.open(io.BytesIO(img_data))
                    
                    # Apply OCR
                    text = pytesseract.image_to_string(img)
                    
                    # Extract fields from OCR text
                    ocr_fields = self._extract_fields_from_text(
                        text,
                        context=f"OCR Page {page_num}",
                        method="tesseract_ocr"
                    )
                    
                    # Adjust confidence for OCR
                    for field in ocr_fields:
                        field.confidence *= 0.7  # OCR is less reliable
                        field.page_number = page_num
                    
                    fields.extend(ocr_fields)
                
                doc.close()
        
        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
        
        return fields
    
    def _parse_with_ai(self) -> List[ExtractedField]:
        """Use AI/ML models for complex field detection"""
        fields = []
        
        # This would integrate with:
        # 1. Google Document AI
        # 2. Azure Form Recognizer
        # 3. AWS Textract
        # 4. Custom trained models
        
        # Placeholder for AI integration
        logger.info("AI-based extraction not yet implemented")
        
        return fields
    
    def _merge_fields(self, all_fields: List[ExtractedField]) -> List[ExtractedField]:
        """Merge and deduplicate fields from different strategies"""
        merged = {}
        
        for field in all_fields:
            # Create a key for deduplication
            key = (
                field.field_name.lower(),
                field.field_type,
                field.page_number or 0,
                field.table_info.get("table_index", -1) if field.table_info else -1
            )
            
            if key not in merged:
                merged[key] = field
            else:
                # Keep the one with higher confidence
                if field.confidence > merged[key].confidence:
                    merged[key] = field
        
        return list(merged.values())
    
    def _post_process(self, fields: List[ExtractedField]) -> List[ExtractedField]:
        """Post-process fields for Ontario-specific requirements"""
        processed = []
        
        for field in fields:
            # Filter by confidence
            if field.confidence < self.confidence_threshold:
                continue
            
            # Add Ontario-specific validation rules
            if field.field_type == "postal_code":
                field.validation_rules = ["^[KLMNP]\\d[A-Z]\\s?\\d[A-Z]\\d$"]
            elif field.field_type == "phone":
                field.validation_rules = ["^\\(?\\d{3}\\)?[-\\s]?\\d{3}[-\\s]?\\d{4}$"]
            elif field.field_type == "lso_number":
                field.validation_rules = ["^\\d{5}[A-Z]?$"]
            
            # Enhance field context
            if "applicant" in field.context.lower():
                field.context = "Applicant Information"
            elif "respondent" in field.context.lower():
                field.context = "Respondent Information"
            elif "child" in field.context.lower():
                field.context = "Children Information"
            elif "financial" in field.context.lower() or "income" in field.context.lower():
                field.context = "Financial Information"
            
            processed.append(field)
        
        return processed
    
    def _needs_ocr(self) -> bool:
        """Check if document needs OCR"""
        # Simple heuristic: if native parsing found few fields, try OCR
        native_field_count = len([f for f in self.fields if f.extraction_method != "ocr"])
        return native_field_count < 5
    
    def _get_document_text(self) -> str:
        """Extract all text from document"""
        text = ""
        
        if self.file_path.suffix.lower() == '.pdf':
            try:
                with pdfplumber.open(self.file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except:
                pass
        
        elif self.file_path.suffix.lower() in ['.docx', '.doc']:
            try:
                doc = Document(self.file_path)
                for para in doc.paragraphs:
                    text += para.text + "\n"
            except:
                pass
        
        return text
    
    def _looks_like_field(self, text: str) -> bool:
        """Check if text looks like a form field"""
        if not text or len(text) < 3:
            return False
        
        indicators = [
            '___', '[ ]', '( )', '□', '○',
            'Name:', 'Date:', 'Address:', 'Phone:',
            'Email:', '$', 'Amount:', 'Number:'
        ]
        
        text_lower = text.lower()
        return any(ind in text or ind.lower() in text_lower for ind in indicators)
    
    def _detect_field_type(self, text: str) -> str:
        """Detect field type from text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['date', 'when', 'dob', 'birth']):
            return 'date'
        elif any(word in text_lower for word in ['amount', 'value', 'income', '$', 'payment']):
            return 'currency'
        elif any(word in text_lower for word in ['email', 'e-mail']):
            return 'email'
        elif any(word in text_lower for word in ['phone', 'telephone', 'tel', 'fax', 'cell']):
            return 'phone'
        elif any(word in text_lower for word in ['number', 'count', '#', 'qty']):
            return 'number'
        elif '□' in text or '[ ]' in text:
            return 'checkbox'
        elif '○' in text or '( )' in text:
            return 'radio'
        elif any(word in text_lower for word in ['select', 'choose', 'pick']):
            return 'select'
        elif any(word in text_lower for word in ['signature', 'sign']):
            return 'signature'
        
        return 'text'
    
    def _sanitize_name(self, text: str) -> str:
        """Create valid field name"""
        import re
        name = re.sub(r'[^a-zA-Z0-9_]', '_', text)
        name = re.sub(r'_+', '_', name)
        name = name.strip('_').lower()[:50]
        return name or "field"
    
    def _get_widget_type(self, widget) -> str:
        """Get field type from PyMuPDF widget"""
        type_map = {
            fitz.PDF_WIDGET_TYPE_TEXT: 'text',
            fitz.PDF_WIDGET_TYPE_CHECKBOX: 'checkbox',
            fitz.PDF_WIDGET_TYPE_RADIOBUTTON: 'radio',
            fitz.PDF_WIDGET_TYPE_LISTBOX: 'select',
            fitz.PDF_WIDGET_TYPE_COMBOBOX: 'select',
            fitz.PDF_WIDGET_TYPE_SIGNATURE: 'signature'
        }
        return type_map.get(widget.field_type, 'text')
    
    def _extract_pypdf2_field(self, annot: Dict, page_num: int) -> Optional[ExtractedField]:
        """Extract field from PyPDF2 annotation"""
        try:
            field_type_map = {
                '/Tx': 'text',
                '/Ch': 'select',
                '/Btn': 'button',
                '/Sig': 'signature'
            }
            
            field_type = field_type_map.get(annot.get('/FT'), 'text')
            
            # Check if checkbox or radio
            if field_type == 'button':
                if annot.get('/Ff', 0) & 0x10000:
                    field_type = 'radio'
                else:
                    field_type = 'checkbox'
            
            return ExtractedField(
                field_name=str(annot.get('/T', f'field_{page_num}')),
                field_type=field_type,
                field_label=str(annot.get('/TU', annot.get('/T', ''))),
                value=str(annot.get('/V', '')),
                required=bool(annot.get('/Ff', 0) & 0x2),
                confidence=0.85,
                extraction_method="pypdf2",
                page_number=page_num
            )
        except Exception as e:
            logger.debug(f"PyPDF2 field extraction error: {e}")
            return None
    
    def _extract_fields_from_text(self, text: str, context: str = "", method: str = "text") -> List[ExtractedField]:
        """Extract fields from text using patterns"""
        fields = []
        
        # Split text into lines for better processing
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines):
            if self._looks_like_field(line):
                field = ExtractedField(
                    field_name=self._sanitize_name(line),
                    field_type=self._detect_field_type(line),
                    field_label=line.strip()[:100],
                    confidence=0.6,
                    extraction_method=method,
                    context=context or f"Line {line_num + 1}"
                )
                fields.append(field)
        
        return fields

def analyze_form(file_path: str, output_file: str = None):
    """Analyze a form and save results"""
    parser = IntelligentFormParser(file_path, use_ocr=True, use_ai=False)
    fields = parser.parse()
    
    # Sort by confidence
    fields.sort(key=lambda x: x.confidence, reverse=True)
    
    # Save results
    if output_file:
        with open(output_file, 'w') as f:
            json.dump([asdict(field) for field in fields], f, indent=2)
    
    # Print summary
    print(f"\nForm Analysis: {Path(file_path).name}")
    print("="*60)
    print(f"Total fields found: {len(fields)}")
    
    # Group by extraction method
    methods = {}
    for field in fields:
        method = field.extraction_method
        if method not in methods:
            methods[method] = 0
        methods[method] += 1
    
    print("\nExtraction methods:")
    for method, count in methods.items():
        print(f"  {method}: {count} fields")
    
    # Group by field type
    types = {}
    for field in fields:
        ftype = field.field_type
        if ftype not in types:
            types[ftype] = 0
        types[ftype] += 1
    
    print("\nField types:")
    for ftype, count in types.items():
        print(f"  {ftype}: {count} fields")
    
    # Show high-confidence fields
    print("\nHigh-confidence fields (>0.8):")
    for field in fields[:10]:
        if field.confidence > 0.8:
            print(f"  [{field.confidence:.2f}] {field.field_label[:50]} ({field.field_type})")
    
    return fields

if __name__ == "__main__":
    import sys
    import io
    
    if len(sys.argv) < 2:
        print("Usage: python intelligent_form_parser.py <form_file> [output_json]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    fields = analyze_form(file_path, output_file)
    
    print(f"\nExtracted {len(fields)} fields successfully")