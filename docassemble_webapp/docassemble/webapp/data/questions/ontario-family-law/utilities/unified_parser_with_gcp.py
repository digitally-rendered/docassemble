#!/usr/bin/env python3
"""
Unified Form Parser with OSS and GCP Integration
Validates consistency across multiple parsing strategies
"""

import os
import json
import logging
import re
import io
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
import hashlib
from collections import defaultdict, Counter
from datetime import datetime

# Import smart field extractor
from smart_field_extractor import SmartFieldExtractor

# OSS Libraries
import PyPDF2
import pdfplumber
from docx import Document
import fitz  # PyMuPDF
from PIL import Image
import pandas as pd

# OCR Libraries
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

# Google Cloud Services
try:
    from google.cloud import vision
    from google.cloud import documentai
    from google.cloud import language_v1
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False
    print("GCP libraries not available. Install with: pip install google-cloud-vision google-cloud-documentai google-cloud-language")

# Other OSS tools
try:
    import camelot  # For advanced table extraction
    CAMELOT_AVAILABLE = True
except ImportError:
    CAMELOT_AVAILABLE = False

try:
    import tabula  # Another table extraction tool
    TABULA_AVAILABLE = True
except ImportError:
    TABULA_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UnifiedField:
    """Unified field representation across all parsers"""
    field_id: str
    field_name: str
    field_type: str
    field_label: str
    value: Optional[str] = None
    required: bool = False
    confidence_scores: Dict[str, float] = None
    extraction_methods: List[str] = None
    page_number: int = 0
    coordinates: Optional[Dict] = None
    context: str = ""
    validators: List[str] = None
    
    def __post_init__(self):
        if self.confidence_scores is None:
            self.confidence_scores = {}
        if self.extraction_methods is None:
            self.extraction_methods = []
        if self.validators is None:
            self.validators = []
    
    @property
    def average_confidence(self) -> float:
        """Calculate average confidence across all methods"""
        if not self.confidence_scores:
            return 0.0
        return sum(self.confidence_scores.values()) / len(self.confidence_scores)
    
    @property
    def consensus_confidence(self) -> float:
        """Higher confidence if multiple methods agree"""
        base_confidence = self.average_confidence
        method_bonus = min(0.2, len(self.extraction_methods) * 0.05)
        return min(1.0, base_confidence + method_bonus)

class UnifiedFormParser:
    """
    Unified parser that combines:
    1. Multiple OSS libraries
    2. GCP Document AI
    3. Validation and consensus building
    """
    
    def __init__(self, file_path: str, use_gcp: bool = False):
        self.file_path = Path(file_path)
        self.use_gcp = use_gcp and GCP_AVAILABLE
        self.all_fields = defaultdict(list)  # Group fields by normalized key
        self.unified_fields = []
        
        # GCP clients (if available)
        if self.use_gcp:
            try:
                self.vision_client = vision.ImageAnnotatorClient()
                self.docai_client = documentai.DocumentProcessorServiceClient()
                self.language_client = language_v1.LanguageServiceClient()
            except Exception as e:
                logger.warning(f"Failed to initialize GCP clients: {e}")
                self.use_gcp = False
    
    def parse_comprehensive(self) -> List[UnifiedField]:
        """
        Parse using all available methods and build consensus
        """
        logger.info(f"Starting comprehensive parsing of {self.file_path.name}")
        
        # 1. OSS Native Parsing
        self._parse_with_oss_native()
        
        # 2. OSS Table Extraction
        self._parse_with_oss_tables()
        
        # 3. OSS OCR
        if TESSERACT_AVAILABLE:
            self._parse_with_tesseract()
        
        # 4. GCP Document AI
        if self.use_gcp:
            self._parse_with_gcp_documentai()
            self._parse_with_gcp_vision()
        
        # 5. Build consensus
        self.unified_fields = self._build_consensus()
        
        # 6. Validate consistency
        validation_report = self._validate_consistency()
        
        # 7. Apply Ontario-specific rules
        self._apply_ontario_rules()
        
        return self.unified_fields, validation_report
    
    def _parse_with_oss_native(self):
        """Parse using native OSS libraries"""
        logger.info("Parsing with OSS native libraries...")
        
        ext = self.file_path.suffix.lower()
        
        if ext == '.pdf':
            # PyMuPDF
            try:
                doc = fitz.open(self.file_path)
                for page_num, page in enumerate(doc, 1):
                    for widget in page.widgets():
                        self._add_field(
                            field_name=widget.field_name or f"field_{page_num}",
                            field_type=self._get_widget_type(widget),
                            field_label=widget.field_label or widget.field_name or "",
                            method="pymupdf",
                            confidence=0.9,
                            page_number=page_num
                        )
                doc.close()
            except Exception as e:
                logger.debug(f"PyMuPDF error: {e}")
            
            # pdfplumber
            try:
                with pdfplumber.open(self.file_path) as pdf:
                    for page_num, page in enumerate(pdf.pages, 1):
                        text = page.extract_text() or ""
                        self._extract_fields_from_text(text, "pdfplumber", page_num)
            except Exception as e:
                logger.debug(f"pdfplumber error: {e}")
        
        elif ext in ['.docx', '.doc']:
            # python-docx
            try:
                doc = Document(self.file_path)
                
                # Parse paragraphs
                for para_idx, para in enumerate(doc.paragraphs):
                    if para.text.strip():
                        self._extract_fields_from_text(para.text, "python-docx", para_idx)
                
                # Parse tables - important for forms
                for table_idx, table in enumerate(doc.tables):
                    for row_idx, row in enumerate(table.rows):
                        for cell_idx, cell in enumerate(row.cells):
                            cell_text = cell.text.strip()
                            if cell_text and self._looks_like_field(cell_text):
                                self._add_field(
                                    field_name=self._sanitize_name(cell_text),
                                    field_type=self._detect_field_type(cell_text),
                                    field_label=cell_text[:100],
                                    method="python-docx-table",
                                    confidence=0.75,
                                    page_number=0,
                                    context=f"Table {table_idx+1}, Row {row_idx+1}, Cell {cell_idx+1}"
                                )
            except Exception as e:
                logger.debug(f"python-docx error: {e}")
    
    def _parse_with_oss_tables(self):
        """Parse tables using OSS libraries"""
        logger.info("Parsing tables with OSS libraries...")
        
        if self.file_path.suffix.lower() != '.pdf':
            return
        
        # Camelot (lattice and stream methods)
        if CAMELOT_AVAILABLE:
            try:
                # Try lattice method (for bordered tables)
                tables = camelot.read_pdf(str(self.file_path), pages='all', flavor='lattice')
                for table in tables:
                    self._process_table(table.df, "camelot_lattice", table.page)
                
                # Try stream method (for borderless tables)
                tables = camelot.read_pdf(str(self.file_path), pages='all', flavor='stream')
                for table in tables:
                    self._process_table(table.df, "camelot_stream", table.page)
            except Exception as e:
                logger.debug(f"Camelot error: {e}")
        
        # Tabula
        if TABULA_AVAILABLE:
            try:
                tables = tabula.read_pdf(str(self.file_path), pages='all', multiple_tables=True)
                for idx, table in enumerate(tables):
                    self._process_table(table, "tabula", idx + 1)
            except Exception as e:
                logger.debug(f"Tabula error: {e}")
    
    def _parse_with_tesseract(self):
        """Parse using Tesseract OCR"""
        logger.info("Parsing with Tesseract OCR...")
        
        try:
            if self.file_path.suffix.lower() == '.pdf':
                doc = fitz.open(self.file_path)
                
                for page_num, page in enumerate(doc, 1):
                    # Convert to image
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    
                    # OCR with different modes
                    # Mode 1: Standard
                    text = pytesseract.image_to_string(img)
                    self._extract_fields_from_text(text, "tesseract_standard", page_num)
                    
                    # Mode 2: With layout preservation
                    text_layout = pytesseract.image_to_string(img, config='--psm 6')
                    self._extract_fields_from_text(text_layout, "tesseract_layout", page_num)
                    
                    # Mode 3: Get detailed data
                    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
                    self._process_tesseract_data(data, page_num)
                
                doc.close()
        except Exception as e:
            logger.debug(f"Tesseract error: {e}")
    
    def _parse_with_gcp_documentai(self):
        """Parse using Google Cloud Document AI"""
        if not self.use_gcp:
            return
        
        logger.info("Parsing with GCP Document AI...")
        
        try:
            # Read file content
            with open(self.file_path, 'rb') as f:
                content = f.read()
            
            # Configure the request
            project_id = os.environ.get('GCP_PROJECT_ID', '')
            location = os.environ.get('GCP_LOCATION', 'us')
            processor_id = os.environ.get('DOCAI_FORM_PARSER_ID', '')
            
            if not project_id or not processor_id:
                logger.warning("GCP Document AI requires PROJECT_ID and PROCESSOR_ID")
                return
            
            name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"
            
            # Create document
            document = documentai.Document(
                content=content,
                mime_type='application/pdf' if self.file_path.suffix == '.pdf' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            
            # Process request
            request = documentai.ProcessRequest(
                name=name,
                raw_document=documentai.RawDocument(
                    content=content,
                    mime_type=document.mime_type
                )
            )
            
            result = self.docai_client.process_document(request=request)
            
            # Extract entities
            for entity in result.document.entities:
                self._add_field(
                    field_name=entity.type_,
                    field_type=self._map_entity_type(entity.type_),
                    field_label=entity.mention_text,
                    value=entity.normalized_value.text if entity.normalized_value else None,
                    method="gcp_documentai",
                    confidence=entity.confidence,
                    page_number=entity.page_anchor.page_refs[0].page if entity.page_anchor.page_refs else 0
                )
            
            # Extract form fields
            for page in result.document.pages:
                for field in page.form_fields:
                    field_name = self._get_text(field.field_name, result.document)
                    field_value = self._get_text(field.field_value, result.document)
                    
                    self._add_field(
                        field_name=field_name,
                        field_type="text",
                        field_label=field_name,
                        value=field_value,
                        method="gcp_documentai_form",
                        confidence=field.field_name.confidence if field.field_name else 0.5,
                        page_number=page.page_number
                    )
        
        except Exception as e:
            logger.error(f"GCP Document AI error: {e}")
    
    def _parse_with_gcp_vision(self):
        """Parse using Google Cloud Vision API"""
        if not self.use_gcp:
            return
        
        logger.info("Parsing with GCP Vision API...")
        
        try:
            # Read file content
            with open(self.file_path, 'rb') as f:
                content = f.read()
            
            image = vision.Image(content=content)
            
            # Text detection
            response = self.vision_client.text_detection(image=image)
            texts = response.text_annotations
            
            if texts:
                full_text = texts[0].description
                self._extract_fields_from_text(full_text, "gcp_vision", 0)
            
            # Document text detection (better for forms)
            response = self.vision_client.document_text_detection(image=image)
            
            for page in response.full_text_annotation.pages:
                for block in page.blocks:
                    block_text = ""
                    for paragraph in block.paragraphs:
                        for word in paragraph.words:
                            word_text = ''.join([symbol.text for symbol in word.symbols])
                            block_text += word_text + " "
                    
                    if self._looks_like_field(block_text):
                        self._add_field(
                            field_name=self._sanitize_name(block_text),
                            field_type=self._detect_field_type(block_text),
                            field_label=block_text.strip(),
                            method="gcp_vision_blocks",
                            confidence=block.confidence,
                            page_number=1
                        )
        
        except Exception as e:
            logger.error(f"GCP Vision error: {e}")
    
    def _build_consensus(self) -> List[UnifiedField]:
        """Build consensus from all extracted fields"""
        logger.info("Building consensus from all extraction methods...")
        
        unified = []
        
        for field_key, field_list in self.all_fields.items():
            if not field_list:
                continue
            
            # Create unified field
            unified_field = UnifiedField(
                field_id=f"unified_{len(unified)}",
                field_name=field_list[0]['field_name'],
                field_type=self._consensus_field_type(field_list),
                field_label=self._consensus_field_label(field_list),
                value=self._consensus_value(field_list),
                required=any(f.get('required', False) for f in field_list),
                page_number=field_list[0].get('page_number', 0)
            )
            
            # Aggregate confidence scores and methods
            for field in field_list:
                method = field.get('method', 'unknown')
                confidence = field.get('confidence', 0.5)
                
                unified_field.confidence_scores[method] = confidence
                if method not in unified_field.extraction_methods:
                    unified_field.extraction_methods.append(method)
            
            # Only include fields with reasonable confidence
            if unified_field.consensus_confidence >= 0.4:
                unified.append(unified_field)
        
        # Sort by confidence
        unified.sort(key=lambda x: x.consensus_confidence, reverse=True)
        
        return unified
    
    def _validate_consistency(self) -> Dict[str, Any]:
        """Validate consistency across extraction methods"""
        logger.info("Validating consistency...")
        
        report = {
            "total_fields": len(self.unified_fields),
            "high_confidence": 0,
            "medium_confidence": 0,
            "low_confidence": 0,
            "single_method": 0,
            "multi_method": 0,
            "method_agreement": {},
            "field_types": {},
            "warnings": []
        }
        
        for field in self.unified_fields:
            # Confidence levels
            if field.consensus_confidence >= 0.8:
                report["high_confidence"] += 1
            elif field.consensus_confidence >= 0.6:
                report["medium_confidence"] += 1
            else:
                report["low_confidence"] += 1
            
            # Method coverage
            if len(field.extraction_methods) == 1:
                report["single_method"] += 1
            else:
                report["multi_method"] += 1
            
            # Field types
            ftype = field.field_type
            if ftype not in report["field_types"]:
                report["field_types"][ftype] = 0
            report["field_types"][ftype] += 1
            
            # Check for inconsistencies
            if len(field.extraction_methods) > 1:
                confidence_variance = max(field.confidence_scores.values()) - min(field.confidence_scores.values())
                if confidence_variance > 0.3:
                    report["warnings"].append(
                        f"High confidence variance for '{field.field_label[:30]}': {confidence_variance:.2f}"
                    )
        
        # Method agreement analysis
        for field in self.unified_fields:
            if len(field.extraction_methods) > 1:
                key = tuple(sorted(field.extraction_methods))
                if key not in report["method_agreement"]:
                    report["method_agreement"][key] = 0
                report["method_agreement"][key] += 1
        
        return report
    
    def _apply_ontario_rules(self):
        """Apply Ontario-specific validation and enhancement"""
        logger.info("Applying Ontario-specific rules...")
        
        for field in self.unified_fields:
            # Postal code validation
            if 'postal' in field.field_label.lower():
                field.field_type = 'postal_code'
                field.validators.append(r'^[KLMNP]\d[A-Z]\s?\d[A-Z]\d$')
            
            # SIN handling
            elif 'social insurance' in field.field_label.lower() or 'sin' in field.field_label.lower():
                field.field_type = 'sin'
                field.validators.append(r'^\d{3}-\d{3}-\d{3}$')
                field.context = "PRIVACY: Mask SIN in output"
            
            # LSO number
            elif 'lso' in field.field_label.lower():
                field.field_type = 'lso_number'
                field.validators.append(r'^\d{5}[A-Z]?$')
            
            # Court file number
            elif 'court file' in field.field_label.lower():
                field.field_type = 'court_file_number'
                field.context = "Ontario Court"
            
            # Financial amounts
            elif field.field_type == 'currency':
                field.validators.append(r'^\$?\d{1,3}(,\d{3})*(\.\d{2})?$')
    
    # Helper methods
    def _add_field(self, field_name: str, field_type: str, field_label: str, 
                   method: str, confidence: float, **kwargs):
        """Add a field to the collection"""
        key = self._normalize_field_key(field_name, field_type, kwargs.get('page_number', 0))
        
        field_data = {
            'field_name': field_name,
            'field_type': field_type,
            'field_label': field_label,
            'method': method,
            'confidence': confidence,
            **kwargs
        }
        
        self.all_fields[key].append(field_data)
    
    def _normalize_field_key(self, name: str, ftype: str, page: int) -> str:
        """Create normalized key for field grouping"""
        # Normalize name
        name_normalized = re.sub(r'[^a-z0-9]', '', name.lower())
        
        # Create hash for very long names
        if len(name_normalized) > 20:
            name_normalized = hashlib.md5(name_normalized.encode()).hexdigest()[:10]
        
        return f"{name_normalized}_{ftype}_{page}"
    
    def _extract_fields_from_text(self, text: str, method: str, page_num: int):
        """Extract fields from text using smart field extractor"""
        if not text:
            return
        
        # Use smart field extractor to distinguish fields from explanatory text
        extractor = SmartFieldExtractor()
        
        # Split text into lines for analysis
        lines = text.split('\n')
        
        # Extract fields using smart logic
        fields = extractor.extract_fields_from_lines(lines)
        
        # Add extracted fields
        for field in fields:
            self._add_field(
                field_name=field['field_id'],
                field_type=field['field_type'],
                field_label=field['field_label'],
                method=method,
                confidence=0.8,  # High confidence from smart extractor
                page_number=page_num
            )
    
    def _process_table(self, df: pd.DataFrame, method: str, page_num: int):
        """Process extracted table using smart field extractor"""
        extractor = SmartFieldExtractor()
        
        for row_idx, row in df.iterrows():
            for col_idx, cell in row.items():
                if pd.notna(cell):
                    # Use smart extractor to check if this is a field
                    field_info = extractor.extract_field_info(str(cell))
                    if field_info:
                        self._add_field(
                            field_name=field_info['field_id'],
                            field_type=field_info['field_type'],
                            field_label=field_info['field_label'],
                            method=method,
                            confidence=0.7,
                            page_number=page_num
                        )
    
    def _process_tesseract_data(self, data: Dict, page_num: int):
        """Process detailed Tesseract data"""
        for i, text in enumerate(data['text']):
            if text and self._looks_like_field(text):
                conf = float(data['conf'][i]) / 100.0 if data['conf'][i] > 0 else 0.5
                self._add_field(
                    field_name=f"ocr_{page_num}_{i}",
                    field_type=self._detect_field_type(text),
                    field_label=text,
                    method="tesseract_detailed",
                    confidence=conf,
                    page_number=page_num,
                    coordinates={
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i]
                    }
                )
    
    def _consensus_field_type(self, field_list: List[Dict]) -> str:
        """Determine consensus field type"""
        type_counts = defaultdict(int)
        for field in field_list:
            type_counts[field['field_type']] += field.get('confidence', 0.5)
        
        if type_counts:
            return max(type_counts, key=type_counts.get)
        return 'text'
    
    def _consensus_field_label(self, field_list: List[Dict]) -> str:
        """Determine consensus field label"""
        # Use the label from the highest confidence extraction
        best_field = max(field_list, key=lambda x: x.get('confidence', 0))
        return best_field.get('field_label', '')
    
    def _consensus_value(self, field_list: List[Dict]) -> Optional[str]:
        """Determine consensus value if present"""
        values = [f.get('value') for f in field_list if f.get('value')]
        if values:
            # Return most common value
            from collections import Counter
            counter = Counter(values)
            return counter.most_common(1)[0][0]
        return None
    
    def _looks_like_field(self, text: str) -> bool:
        """Check if text looks like a form field"""
        if not text or len(text) < 3:
            return False
        
        # More comprehensive indicators
        indicators = [
            '___', '[ ]', '( )', '□', '○', ':', '$',
            '\u2002',  # Unicode spaces often used in forms
            'Name:', 'Date:', 'Address:', 'Phone:',
            'Email:', 'Amount:', 'Number:'
        ]
        
        # More comprehensive keywords
        keywords = [
            'name', 'date', 'address', 'phone', 'email', 'number', 'amount',
            'full legal', 'applicant', 'respondent', 'income', 'value',
            'court', 'file', 'lso', 'postal', 'city', 'province',
            'first', 'last', 'middle', 'birth', 'age', 'gender'
        ]
        
        text_lower = text.lower()
        
        # Check for indicators
        for ind in indicators:
            if ind in text or ind.lower() in text_lower:
                return True
        
        # Check for keywords
        for kw in keywords:
            if kw in text_lower:
                return True
        
        # Check for patterns that suggest fields
        if len(text) > 20 and text.count(' ') > 2:  # Multi-word phrases
            return True
            
        return False
    
    def _detect_field_type(self, text: str) -> str:
        """Detect field type from text"""
        text_lower = text.lower()
        
        type_patterns = [
            (['date', 'when', 'dob', 'birth'], 'date'),
            (['amount', 'value', 'income', '$', 'payment', 'cost'], 'currency'),
            (['email', 'e-mail'], 'email'),
            (['phone', 'tel', 'fax', 'cell'], 'phone'),
            (['number', 'count', '#', 'qty'], 'number'),
            (['signature', 'sign'], 'signature'),
            (['select', 'choose', 'pick'], 'select')
        ]
        
        for keywords, field_type in type_patterns:
            if any(kw in text_lower for kw in keywords):
                return field_type
        
        if '□' in text or '[ ]' in text:
            return 'checkbox'
        elif '○' in text or '( )' in text:
            return 'radio'
        
        return 'text'
    
    def _sanitize_name(self, text: str) -> str:
        """Create valid field name"""
        name = re.sub(r'[^a-zA-Z0-9_]', '_', text)
        name = re.sub(r'_+', '_', name)
        return name.strip('_').lower()[:50] or "field"
    
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
    
    def _map_entity_type(self, entity_type: str) -> str:
        """Map GCP entity type to field type"""
        entity_map = {
            'person': 'text',
            'location': 'address',
            'date': 'date',
            'money': 'currency',
            'phone_number': 'phone',
            'email': 'email',
            'number': 'number'
        }
        return entity_map.get(entity_type.lower(), 'text')
    
    def _get_text(self, layout, document) -> str:
        """Extract text from Document AI layout"""
        if not layout or not layout.text_anchor:
            return ""
        
        text = ""
        for segment in layout.text_anchor.text_segments:
            start = segment.start_index if segment.start_index else 0
            end = segment.end_index if segment.end_index else len(document.text)
            text += document.text[start:end]
        
        return text.strip()

def compare_parsers(file_path: str, output_dir: str = "validation_results"):
    """Compare results from different parsing strategies"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Run unified parser
    parser = UnifiedFormParser(file_path, use_gcp=False)  # Set to True if GCP is configured
    unified_fields, validation_report = parser.parse_comprehensive()
    
    # Save results
    results_file = output_path / f"{Path(file_path).stem}_unified_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            'file': str(file_path),
            'timestamp': datetime.now().isoformat(),
            'fields': [asdict(field) for field in unified_fields],
            'validation_report': validation_report
        }, f, indent=2)
    
    # Print report
    print(f"\nUnified Parser Results: {Path(file_path).name}")
    print("="*60)
    print(f"Total fields extracted: {len(unified_fields)}")
    print(f"High confidence fields: {validation_report['high_confidence']}")
    print(f"Multi-method consensus: {validation_report['multi_method']}")
    
    print("\nExtraction method coverage:")
    method_counts = defaultdict(int)
    for field in unified_fields:
        for method in field.extraction_methods:
            method_counts[method] += 1
    
    for method, count in sorted(method_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {method}: {count} fields")
    
    print("\nField type distribution:")
    for ftype, count in validation_report['field_types'].items():
        print(f"  {ftype}: {count}")
    
    if validation_report['warnings']:
        print(f"\nWarnings ({len(validation_report['warnings'])}):")
        for warning in validation_report['warnings'][:5]:
            print(f"  - {warning}")
    
    print(f"\nResults saved to: {results_file}")
    
    return unified_fields, validation_report

if __name__ == "__main__":
    import sys
    import io
    
    if len(sys.argv) < 2:
        print("Usage: python unified_parser_with_gcp.py <form_file> [output_dir]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "validation_results"
    
    fields, report = compare_parsers(file_path, output_dir)