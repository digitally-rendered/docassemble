#!/usr/bin/env python3
"""
Advanced Document Parser for Ontario Family Law Forms
Implements multi-tool extraction, preprocessing, and intelligent field detection
"""

import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
import hashlib
from datetime import datetime
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import tempfile
import shutil

# Document processing libraries
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    
try:
    from PIL import Image, ImageEnhance, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    from docx import Document
    PYTHON_DOCX_AVAILABLE = True
except ImportError:
    PYTHON_DOCX_AVAILABLE = False

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    from fuzzywuzzy import fuzz, process
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ExtractionMethod(Enum):
    """Available extraction methods"""
    GOOGLE_DOC_AI = "google_doc_ai"
    AZURE_FORM_RECOGNIZER = "azure_form_recognizer"
    AWS_TEXTRACT = "aws_textract"
    TESSERACT_OCR = "tesseract_ocr"
    PYMUPDF = "pymupdf"
    PDFPLUMBER = "pdfplumber"
    PYTHON_DOCX = "python_docx"
    TEMPLATE_BASED = "template_based"


class FieldType(Enum):
    """Field types in legal forms"""
    TEXT = "text"
    DROPDOWN = "dropdown"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    DATE = "date"
    SIGNATURE = "signature"
    TABLE = "table"
    LONGTEXT = "longtext"


@dataclass
class ExtractedField:
    """Represents an extracted form field with confidence scoring"""
    field_id: str
    field_name: str
    field_type: FieldType
    field_label: str
    value: Optional[Any] = None
    confidence: float = 0.0
    extraction_method: Optional[ExtractionMethod] = None
    position: Optional[Dict[str, float]] = None  # {x, y, width, height}
    page_number: Optional[int] = None
    validation_status: str = "unvalidated"
    validation_errors: List[str] = field(default_factory=list)
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentMetadata:
    """Document metadata and processing info"""
    document_id: str
    file_path: str
    form_type: Optional[str] = None
    form_number: Optional[str] = None
    total_pages: int = 0
    document_quality: float = 0.0
    processing_time: float = 0.0
    extraction_methods_used: List[ExtractionMethod] = field(default_factory=list)
    preprocessing_applied: List[str] = field(default_factory=list)
    overall_confidence: float = 0.0


class DocumentPreprocessor:
    """Handles document preprocessing and enhancement"""
    
    @staticmethod
    def enhance_image_quality(image_path: Path, output_path: Optional[Path] = None) -> Path:
        """Enhance image quality for better OCR"""
        if not PIL_AVAILABLE:
            logger.warning("PIL not available, skipping image enhancement")
            return image_path
            
        try:
            img = Image.open(image_path)
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.0)
            
            # Apply denoising
            img = img.filter(ImageFilter.MedianFilter(size=3))
            
            # Save enhanced image
            if output_path is None:
                output_path = image_path.parent / f"{image_path.stem}_enhanced{image_path.suffix}"
            
            img.save(output_path, dpi=(300, 300))
            logger.info(f"Enhanced image saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Image enhancement failed: {e}")
            return image_path
    
    @staticmethod
    def deskew_image(image_path: Path) -> Path:
        """Deskew scanned documents"""
        if not OPENCV_AVAILABLE:
            logger.warning("OpenCV not available, skipping deskew")
            return image_path
            
        try:
            img = cv2.imread(str(image_path))
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Find edges
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # Detect lines using Hough transform
            lines = cv2.HoughLines(edges, 1, np.pi/180, 200)
            
            if lines is not None:
                # Calculate average angle
                angles = []
                for rho, theta in lines[:, 0]:
                    angle = (theta * 180 / np.pi) - 90
                    if -45 <= angle <= 45:
                        angles.append(angle)
                
                if angles:
                    median_angle = np.median(angles)
                    
                    # Rotate image
                    (h, w) = img.shape[:2]
                    center = (w // 2, h // 2)
                    M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                    rotated = cv2.warpAffine(img, M, (w, h), 
                                           flags=cv2.INTER_CUBIC,
                                           borderMode=cv2.BORDER_REPLICATE)
                    
                    output_path = image_path.parent / f"{image_path.stem}_deskewed{image_path.suffix}"
                    cv2.imwrite(str(output_path), rotated)
                    logger.info(f"Deskewed image saved to {output_path}")
                    return output_path
                    
        except Exception as e:
            logger.error(f"Deskewing failed: {e}")
            
        return image_path
    
    @staticmethod
    def convert_pdf_to_images(pdf_path: Path, output_dir: Optional[Path] = None) -> List[Path]:
        """Convert PDF pages to high-quality images"""
        if not PYMUPDF_AVAILABLE:
            logger.warning("PyMuPDF not available, cannot convert PDF to images")
            return []
            
        try:
            if output_dir is None:
                output_dir = pdf_path.parent / f"{pdf_path.stem}_images"
            output_dir.mkdir(exist_ok=True)
            
            doc = fitz.open(pdf_path)
            image_paths = []
            
            for page_num, page in enumerate(doc):
                # Render at high resolution (300 DPI)
                mat = fitz.Matrix(300/72, 300/72)
                pix = page.get_pixmap(matrix=mat)
                
                image_path = output_dir / f"page_{page_num + 1}.png"
                pix.save(str(image_path))
                image_paths.append(image_path)
                
            doc.close()
            logger.info(f"Converted {len(image_paths)} pages to images")
            return image_paths
            
        except Exception as e:
            logger.error(f"PDF to image conversion failed: {e}")
            return []


class LayoutAnalyzer:
    """Analyzes document layout and structure"""
    
    @staticmethod
    def detect_tables(document_path: Path) -> List[Dict[str, Any]]:
        """Detect tables in document"""
        tables = []
        
        if PDFPLUMBER_AVAILABLE and document_path.suffix.lower() == '.pdf':
            try:
                with pdfplumber.open(document_path) as pdf:
                    for page_num, page in enumerate(pdf.pages):
                        page_tables = page.find_tables()
                        for table_num, table in enumerate(page_tables):
                            tables.append({
                                'page': page_num + 1,
                                'table_num': table_num + 1,
                                'bbox': table.bbox,
                                'data': table.extract(),
                                'rows': len(table.extract()),
                                'cols': len(table.extract()[0]) if table.extract() else 0
                            })
                logger.info(f"Detected {len(tables)} tables in document")
            except Exception as e:
                logger.error(f"Table detection failed: {e}")
                
        return tables
    
    @staticmethod
    def identify_form_sections(document_path: Path) -> List[Dict[str, Any]]:
        """Identify logical sections in a form"""
        sections = []
        
        # Common section patterns in Ontario legal forms
        section_patterns = [
            r'PART\s+\d+[:\s]+(.+)',
            r'SECTION\s+([A-Z])[\s:]+(.+)',
            r'^\d+\.\s+(.+)',
            r'^[A-Z]\.\s+(.+)',
            r'(APPLICANT|RESPONDENT|CHILDREN|PROPERTY|SUPPORT|CLAIMS)',
        ]
        
        if PYMUPDF_AVAILABLE and document_path.suffix.lower() == '.pdf':
            try:
                doc = fitz.open(document_path)
                for page_num, page in enumerate(doc):
                    text = page.get_text()
                    lines = text.split('\n')
                    
                    for line_num, line in enumerate(lines):
                        for pattern in section_patterns:
                            match = re.match(pattern, line, re.IGNORECASE)
                            if match:
                                sections.append({
                                    'page': page_num + 1,
                                    'line': line_num + 1,
                                    'title': line.strip(),
                                    'pattern_matched': pattern,
                                    'content_start': line_num + 1
                                })
                doc.close()
            except Exception as e:
                logger.error(f"Section identification failed: {e}")
                
        return sections


class MultiToolExtractor:
    """Orchestrates multiple extraction tools"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.available_methods = self._detect_available_methods()
        logger.info(f"Available extraction methods: {self.available_methods}")
        
    def _detect_available_methods(self) -> List[ExtractionMethod]:
        """Detect which extraction methods are available"""
        methods = []
        
        if TESSERACT_AVAILABLE:
            methods.append(ExtractionMethod.TESSERACT_OCR)
        if PYMUPDF_AVAILABLE:
            methods.append(ExtractionMethod.PYMUPDF)
        if PDFPLUMBER_AVAILABLE:
            methods.append(ExtractionMethod.PDFPLUMBER)
        if PYTHON_DOCX_AVAILABLE:
            methods.append(ExtractionMethod.PYTHON_DOCX)
            
        # Check for cloud API configurations
        if self.config.get('google_doc_ai_enabled'):
            methods.append(ExtractionMethod.GOOGLE_DOC_AI)
        if self.config.get('azure_form_recognizer_enabled'):
            methods.append(ExtractionMethod.AZURE_FORM_RECOGNIZER)
        if self.config.get('aws_textract_enabled'):
            methods.append(ExtractionMethod.AWS_TEXTRACT)
            
        return methods
    
    def extract_with_tesseract(self, image_path: Path) -> List[ExtractedField]:
        """Extract text using Tesseract OCR"""
        fields = []
        
        if not TESSERACT_AVAILABLE:
            return fields
            
        try:
            # Configure Tesseract
            custom_config = r'--oem 3 --psm 6'
            
            # Extract text
            text = pytesseract.image_to_string(image_path, config=custom_config)
            
            # Extract data with bounding boxes
            data = pytesseract.image_to_data(image_path, output_type=pytesseract.Output.DICT)
            
            # Process extracted data
            n_boxes = len(data['text'])
            for i in range(n_boxes):
                if int(data['conf'][i]) > 60:  # Confidence threshold
                    text = data['text'][i].strip()
                    if text:
                        field_obj = ExtractedField(
                            field_id=f"tesseract_{i}",
                            field_name=f"field_{i}",
                            field_type=FieldType.TEXT,
                            field_label=text,
                            value=text,
                            confidence=float(data['conf'][i]) / 100,
                            extraction_method=ExtractionMethod.TESSERACT_OCR,
                            position={
                                'x': data['left'][i],
                                'y': data['top'][i],
                                'width': data['width'][i],
                                'height': data['height'][i]
                            }
                        )
                        fields.append(field_obj)
                        
        except Exception as e:
            logger.error(f"Tesseract extraction failed: {e}")
            
        return fields
    
    def extract_with_pdfplumber(self, pdf_path: Path) -> List[ExtractedField]:
        """Extract form fields using pdfplumber"""
        fields = []
        
        if not PDFPLUMBER_AVAILABLE:
            return fields
            
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract text with positions
                    words = page.extract_words()
                    
                    for word_idx, word in enumerate(words):
                        field_obj = ExtractedField(
                            field_id=f"pdfplumber_p{page_num}_w{word_idx}",
                            field_name=f"field_p{page_num}_{word_idx}",
                            field_type=FieldType.TEXT,
                            field_label=word['text'],
                            value=word['text'],
                            confidence=0.8,  # pdfplumber doesn't provide confidence
                            extraction_method=ExtractionMethod.PDFPLUMBER,
                            position={
                                'x': word['x0'],
                                'y': word['top'],
                                'width': word['x1'] - word['x0'],
                                'height': word['bottom'] - word['top']
                            },
                            page_number=page_num + 1
                        )
                        fields.append(field_obj)
                        
        except Exception as e:
            logger.error(f"PDFPlumber extraction failed: {e}")
            
        return fields
    
    def extract_with_pymupdf(self, pdf_path: Path) -> List[ExtractedField]:
        """Extract form fields using PyMuPDF"""
        fields = []
        
        if not PYMUPDF_AVAILABLE:
            return fields
            
        try:
            doc = fitz.open(pdf_path)
            
            for page_num, page in enumerate(doc):
                # Extract form fields
                for widget in page.widgets():
                    field_obj = ExtractedField(
                        field_id=f"pymupdf_{widget.field_name}",
                        field_name=widget.field_name or f"field_{page_num}_{widget.field_type}",
                        field_type=self._map_widget_type(widget.field_type),
                        field_label=widget.field_label or "",
                        value=widget.field_value,
                        confidence=0.9,  # High confidence for actual form fields
                        extraction_method=ExtractionMethod.PYMUPDF,
                        position={
                            'x': widget.rect.x0,
                            'y': widget.rect.y0,
                            'width': widget.rect.width,
                            'height': widget.rect.height
                        },
                        page_number=page_num + 1,
                        metadata={
                            'field_flags': widget.field_flags,
                            'field_type_string': widget.field_type_string
                        }
                    )
                    fields.append(field_obj)
                    
            doc.close()
            
        except Exception as e:
            logger.error(f"PyMuPDF extraction failed: {e}")
            
        return fields
    
    def _map_widget_type(self, widget_type: int) -> FieldType:
        """Map PyMuPDF widget type to our FieldType"""
        mapping = {
            1: FieldType.CHECKBOX,
            2: FieldType.RADIO,
            3: FieldType.TEXT,
            4: FieldType.DROPDOWN,
            5: FieldType.SIGNATURE,
        }
        return mapping.get(widget_type, FieldType.TEXT)
    
    def extract_with_docx(self, docx_path: Path) -> List[ExtractedField]:
        """Extract form fields from DOCX files"""
        fields = []
        
        if not PYTHON_DOCX_AVAILABLE:
            return fields
            
        try:
            doc = Document(docx_path)
            field_counter = 0
            
            # Extract from paragraphs
            for para_idx, paragraph in enumerate(doc.paragraphs):
                if paragraph.text.strip():
                    # Look for form field patterns
                    if '____' in paragraph.text or '[  ]' in paragraph.text:
                        field_obj = ExtractedField(
                            field_id=f"docx_para_{para_idx}",
                            field_name=f"field_para_{para_idx}",
                            field_type=FieldType.TEXT,
                            field_label=paragraph.text.replace('____', '').replace('[  ]', '').strip(),
                            confidence=0.7,
                            extraction_method=ExtractionMethod.PYTHON_DOCX,
                            metadata={'paragraph_index': para_idx}
                        )
                        fields.append(field_obj)
            
            # Extract from tables
            for table_idx, table in enumerate(doc.tables):
                for row_idx, row in enumerate(table.rows):
                    for cell_idx, cell in enumerate(row.cells):
                        if '____' in cell.text or '[  ]' in cell.text:
                            field_obj = ExtractedField(
                                field_id=f"docx_t{table_idx}_r{row_idx}_c{cell_idx}",
                                field_name=f"field_t{table_idx}_r{row_idx}_c{cell_idx}",
                                field_type=FieldType.TEXT,
                                field_label=cell.text.replace('____', '').replace('[  ]', '').strip(),
                                confidence=0.7,
                                extraction_method=ExtractionMethod.PYTHON_DOCX,
                                metadata={
                                    'table_index': table_idx,
                                    'row_index': row_idx,
                                    'cell_index': cell_idx
                                }
                            )
                            fields.append(field_obj)
                            
        except Exception as e:
            logger.error(f"DOCX extraction failed: {e}")
            
        return fields


class FieldValidator:
    """Validates and corrects extracted fields"""
    
    def __init__(self):
        self.ontario_patterns = self._load_ontario_patterns()
        
    def _load_ontario_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load Ontario-specific validation patterns"""
        return {
            'postal_code': {
                'pattern': r'^[A-Z]\d[A-Z]\s?\d[A-Z]\d$',
                'example': 'M5H 2N2',
                'type': 'regex'
            },
            'phone_number': {
                'pattern': r'^(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$',
                'example': '(416) 555-1234',
                'type': 'regex'
            },
            'court_file_number': {
                'pattern': r'^\d{2}-?\d{4,6}(?:-\d{2,4})?$',
                'example': '23-12345',
                'type': 'regex'
            },
            'lso_number': {
                'pattern': r'^[A-Z]?\d{5}[A-Z]?$',
                'example': '12345P',
                'type': 'regex'
            },
            'date': {
                'pattern': r'^(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})$',
                'example': '2024-01-15',
                'type': 'regex'
            }
        }
    
    def validate_field(self, field: ExtractedField) -> ExtractedField:
        """Validate a single field"""
        
        # Check if field matches known patterns
        for pattern_name, pattern_info in self.ontario_patterns.items():
            if pattern_name.lower() in field.field_name.lower():
                if pattern_info['type'] == 'regex':
                    pattern = re.compile(pattern_info['pattern'], re.IGNORECASE)
                    if field.value and not pattern.match(str(field.value)):
                        field.validation_errors.append(
                            f"Value doesn't match expected {pattern_name} format. "
                            f"Expected format like: {pattern_info['example']}"
                        )
                        field.validation_status = 'invalid'
                    else:
                        field.validation_status = 'valid'
                        
        return field
    
    def correct_field_value(self, field: ExtractedField) -> ExtractedField:
        """Attempt to correct common OCR errors"""
        
        if not field.value:
            return field
            
        value = str(field.value)
        
        # Common OCR corrections
        corrections = {
            # Letter/number confusion
            'O': '0', 'o': '0',  # in numbers
            '0': 'O',  # in text
            'l': '1', 'I': '1',  # in numbers
            '1': 'I',  # in text
            'S': '5', 's': '5',  # in numbers
            'Z': '2', 'z': '2',  # in numbers
        }
        
        # Apply corrections based on field type
        if 'number' in field.field_name.lower() or 'phone' in field.field_name.lower():
            # Correct to numbers
            for old, new in corrections.items():
                if old.isalpha() and new.isdigit():
                    value = value.replace(old, new)
                    
        field.value = value
        return field


class FieldMerger:
    """Merges results from multiple extraction methods"""
    
    @staticmethod
    def merge_fields(field_sets: List[List[ExtractedField]]) -> List[ExtractedField]:
        """Merge fields from multiple extraction methods using voting"""
        
        if not field_sets:
            return []
            
        # Group fields by position/content similarity
        merged_fields = []
        field_groups = {}
        
        for fields in field_sets:
            for field in fields:
                # Create a key based on position or content
                key = FieldMerger._create_field_key(field)
                if key not in field_groups:
                    field_groups[key] = []
                field_groups[key].append(field)
        
        # Merge each group
        for key, group in field_groups.items():
            merged_field = FieldMerger._merge_field_group(group)
            merged_fields.append(merged_field)
            
        return merged_fields
    
    @staticmethod
    def _create_field_key(field: ExtractedField) -> str:
        """Create a unique key for field grouping"""
        if field.position:
            # Use position if available
            return f"{field.page_number}_{int(field.position['x'])}_{int(field.position['y'])}"
        else:
            # Use content hash
            return hashlib.md5(str(field.field_label).encode()).hexdigest()[:8]
    
    @staticmethod
    def _merge_field_group(group: List[ExtractedField]) -> ExtractedField:
        """Merge a group of similar fields"""
        
        if len(group) == 1:
            return group[0]
            
        # Use the field with highest confidence as base
        base_field = max(group, key=lambda f: f.confidence)
        
        # Aggregate confidence scores
        avg_confidence = sum(f.confidence for f in group) / len(group)
        base_field.confidence = avg_confidence
        
        # Store alternatives
        base_field.alternatives = [
            {
                'value': f.value,
                'confidence': f.confidence,
                'method': f.extraction_method.value if f.extraction_method else 'unknown'
            }
            for f in group if f != base_field
        ]
        
        # Update extraction methods used
        methods_used = list(set(f.extraction_method for f in group if f.extraction_method))
        base_field.metadata['extraction_methods'] = [m.value for m in methods_used]
        
        return base_field


class TemplateBasedExtractor:
    """Template-based extraction for known form types"""
    
    def __init__(self):
        self.templates = self._load_form_templates()
        
    def _load_form_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load predefined templates for Ontario forms"""
        return {
            'form_8': {
                'name': 'Application (General)',
                'fields': [
                    {'name': 'court_name', 'type': 'dropdown', 'page': 1, 'region': {'x': 100, 'y': 150, 'w': 400, 'h': 30}},
                    {'name': 'court_file_number', 'type': 'text', 'page': 1, 'region': {'x': 450, 'y': 150, 'w': 200, 'h': 30}},
                    {'name': 'applicant_name', 'type': 'text', 'page': 1, 'region': {'x': 100, 'y': 250, 'w': 400, 'h': 30}},
                    {'name': 'applicant_address', 'type': 'text', 'page': 1, 'region': {'x': 100, 'y': 290, 'w': 400, 'h': 60}},
                    {'name': 'respondent_name', 'type': 'text', 'page': 1, 'region': {'x': 100, 'y': 400, 'w': 400, 'h': 30}},
                    {'name': 'respondent_address', 'type': 'text', 'page': 1, 'region': {'x': 100, 'y': 440, 'w': 400, 'h': 60}},
                ]
            },
            'form_13': {
                'name': 'Financial Statement',
                'fields': [
                    {'name': 'gross_annual_income', 'type': 'text', 'page': 2, 'region': {'x': 350, 'y': 200, 'w': 150, 'h': 30}},
                    {'name': 'net_annual_income', 'type': 'text', 'page': 2, 'region': {'x': 350, 'y': 240, 'w': 150, 'h': 30}},
                ]
            }
        }
    
    def extract_using_template(self, document_path: Path, form_type: str) -> List[ExtractedField]:
        """Extract fields using predefined template"""
        
        if form_type not in self.templates:
            logger.warning(f"No template found for form type: {form_type}")
            return []
            
        template = self.templates[form_type]
        fields = []
        
        # This would use OCR or other methods to extract from specific regions
        # For now, return template structure
        for field_def in template['fields']:
            field = ExtractedField(
                field_id=f"template_{form_type}_{field_def['name']}",
                field_name=field_def['name'],
                field_type=FieldType[field_def['type'].upper()],
                field_label=field_def['name'].replace('_', ' ').title(),
                confidence=0.0,  # Would be set based on actual extraction
                extraction_method=ExtractionMethod.TEMPLATE_BASED,
                page_number=field_def['page'],
                position=field_def['region']
            )
            fields.append(field)
            
        return fields


class AdvancedDocumentParser:
    """Main orchestrator for advanced document parsing"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.preprocessor = DocumentPreprocessor()
        self.layout_analyzer = LayoutAnalyzer()
        self.extractor = MultiToolExtractor(config)
        self.validator = FieldValidator()
        self.merger = FieldMerger()
        self.template_extractor = TemplateBasedExtractor()
        
    def parse_document(self, document_path: Path, 
                       form_type: Optional[str] = None,
                       use_preprocessing: bool = True,
                       extraction_methods: Optional[List[ExtractionMethod]] = None) -> Dict[str, Any]:
        """
        Main entry point for document parsing
        
        Args:
            document_path: Path to document
            form_type: Type of form (e.g., 'form_8')
            use_preprocessing: Whether to apply preprocessing
            extraction_methods: Specific methods to use (None = use all available)
            
        Returns:
            Dictionary containing extracted fields and metadata
        """
        
        start_time = datetime.now()
        
        # Initialize metadata
        metadata = DocumentMetadata(
            document_id=hashlib.md5(str(document_path).encode()).hexdigest(),
            file_path=str(document_path),
            form_type=form_type
        )
        
        # Preprocessing
        processed_path = document_path
        if use_preprocessing:
            metadata.preprocessing_applied = self._apply_preprocessing(document_path)
            
        # Layout analysis
        tables = self.layout_analyzer.detect_tables(processed_path)
        sections = self.layout_analyzer.identify_form_sections(processed_path)
        
        # Multi-method extraction
        all_extracted_fields = []
        
        # Template-based extraction if form type is known
        if form_type:
            template_fields = self.template_extractor.extract_using_template(processed_path, form_type)
            if template_fields:
                all_extracted_fields.append(template_fields)
                metadata.extraction_methods_used.append(ExtractionMethod.TEMPLATE_BASED)
        
        # Apply selected extraction methods
        if not extraction_methods:
            extraction_methods = self.extractor.available_methods
            
        for method in extraction_methods:
            fields = self._extract_with_method(processed_path, method)
            if fields:
                all_extracted_fields.append(fields)
                metadata.extraction_methods_used.append(method)
        
        # Merge results from multiple methods
        merged_fields = self.merger.merge_fields(all_extracted_fields)
        
        # Validate and correct fields
        validated_fields = []
        for field in merged_fields:
            field = self.validator.validate_field(field)
            field = self.validator.correct_field_value(field)
            validated_fields.append(field)
        
        # Calculate overall confidence
        if validated_fields:
            metadata.overall_confidence = sum(f.confidence for f in validated_fields) / len(validated_fields)
        
        # Set processing time
        metadata.processing_time = (datetime.now() - start_time).total_seconds()
        
        # Prepare result
        result = {
            'metadata': asdict(metadata),
            'fields': [asdict(f) for f in validated_fields],
            'tables': tables,
            'sections': sections,
            'extraction_summary': {
                'total_fields': len(validated_fields),
                'valid_fields': sum(1 for f in validated_fields if f.validation_status == 'valid'),
                'invalid_fields': sum(1 for f in validated_fields if f.validation_status == 'invalid'),
                'average_confidence': metadata.overall_confidence,
                'methods_used': [m.value for m in metadata.extraction_methods_used]
            }
        }
        
        return result
    
    def _apply_preprocessing(self, document_path: Path) -> List[str]:
        """Apply preprocessing steps"""
        applied = []
        
        if document_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.tiff']:
            # Enhance image quality
            enhanced = self.preprocessor.enhance_image_quality(document_path)
            if enhanced != document_path:
                applied.append('image_enhancement')
                
            # Deskew
            deskewed = self.preprocessor.deskew_image(enhanced)
            if deskewed != enhanced:
                applied.append('deskew')
                
        elif document_path.suffix.lower() == '.pdf':
            # Convert to images for better OCR
            images = self.preprocessor.convert_pdf_to_images(document_path)
            if images:
                applied.append('pdf_to_images')
                
        return applied
    
    def _extract_with_method(self, document_path: Path, method: ExtractionMethod) -> List[ExtractedField]:
        """Extract fields using a specific method"""
        
        if method == ExtractionMethod.TESSERACT_OCR:
            if document_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.tiff']:
                return self.extractor.extract_with_tesseract(document_path)
                
        elif method == ExtractionMethod.PDFPLUMBER:
            if document_path.suffix.lower() == '.pdf':
                return self.extractor.extract_with_pdfplumber(document_path)
                
        elif method == ExtractionMethod.PYMUPDF:
            if document_path.suffix.lower() == '.pdf':
                return self.extractor.extract_with_pymupdf(document_path)
                
        elif method == ExtractionMethod.PYTHON_DOCX:
            if document_path.suffix.lower() in ['.docx', '.doc']:
                return self.extractor.extract_with_docx(document_path)
                
        return []
    
    def batch_process(self, document_paths: List[Path], 
                     max_workers: int = 4) -> List[Dict[str, Any]]:
        """Process multiple documents in parallel"""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_path = {
                executor.submit(self.parse_document, path): path 
                for path in document_paths
            }
            
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(f"Successfully processed {path}")
                except Exception as e:
                    logger.error(f"Failed to process {path}: {e}")
                    
        return results


def main():
    """Example usage"""
    
    # Configure parser
    config = {
        'google_doc_ai_enabled': False,  # Set to True if you have API access
        'azure_form_recognizer_enabled': False,
        'aws_textract_enabled': False
    }
    
    # Initialize parser
    parser = AdvancedDocumentParser(config)
    
    # Parse a document
    document_path = Path("test_download/core_applications/form_8_-_application_general_flr-8-jun25-en.docx")
    
    if document_path.exists():
        result = parser.parse_document(
            document_path,
            form_type='form_8',
            use_preprocessing=True
        )
        
        # Save results
        output_path = Path("parsed_forms/form_8_advanced_extraction.json")
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)
            
        print(f"Extraction complete. Results saved to {output_path}")
        print(f"Total fields extracted: {result['extraction_summary']['total_fields']}")
        print(f"Average confidence: {result['extraction_summary']['average_confidence']:.2%}")
        print(f"Methods used: {', '.join(result['extraction_summary']['methods_used'])}")
    else:
        print(f"Document not found: {document_path}")


if __name__ == "__main__":
    main()