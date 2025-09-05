#!/usr/bin/env python3
"""
Hybrid Form Parser
Combines all parsing strategies including DOCX-to-image conversion for OCR/AI
"""

import os
import io
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import logging
import json

# Document processing
from docx import Document
from docx2python import docx2python
import mammoth
from PIL import Image
import pypdfium2 as pdfium

# OCR and AI
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

# GCP services
try:
    from google.cloud import vision
    from google.cloud import documentai
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False

# Import our custom parsers
from advanced_docx_parser import AdvancedDocxParser, DocxField
from intelligent_form_parser import IntelligentFormParser
from unified_parser_with_gcp import UnifiedFormParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class HybridField:
    """Unified field representation"""
    field_id: str
    field_name: str
    field_type: str
    field_label: str
    value: Optional[str] = None
    required: bool = False
    confidence: float = 0.0
    extraction_methods: List[str] = None
    page_number: int = 0
    coordinates: Optional[Dict] = None
    context: str = ""
    metadata: Dict = None
    
    def __post_init__(self):
        if self.extraction_methods is None:
            self.extraction_methods = []
        if self.metadata is None:
            self.metadata = {}

class HybridFormParser:
    """
    Hybrid parser that combines:
    1. Advanced DOCX parsing (XML, content controls, etc.)
    2. DOCX-to-image conversion for OCR
    3. GCP Document AI on converted images
    4. Intelligent pattern matching
    5. Consensus building across all methods
    """
    
    def __init__(self, file_path: str, use_ocr: bool = True, use_gcp: bool = False):
        self.file_path = Path(file_path)
        self.use_ocr = use_ocr and TESSERACT_AVAILABLE
        self.use_gcp = use_gcp and GCP_AVAILABLE
        self.temp_dir = None
        self.all_fields = {}
        
    def parse(self) -> Tuple[List[HybridField], Dict[str, Any]]:
        """Parse form using all available strategies"""
        
        logger.info(f"Starting hybrid parsing of {self.file_path.name}")
        
        # Create temp directory for conversions
        self.temp_dir = tempfile.mkdtemp(prefix="hybrid_parser_")
        
        try:
            results = {
                'file': str(self.file_path),
                'strategies_used': [],
                'field_counts': {},
                'consensus_report': {}
            }
            
            # Strategy 1: Advanced DOCX parsing
            docx_fields = self._parse_with_advanced_docx()
            if docx_fields:
                results['strategies_used'].append('advanced_docx')
                results['field_counts']['advanced_docx'] = len(docx_fields)
                self._add_fields(docx_fields, 'advanced_docx')
            
            # Strategy 2: Convert DOCX to images for OCR/AI
            image_paths = self._convert_to_images()
            
            if image_paths:
                # Strategy 3: OCR on images
                if self.use_ocr:
                    ocr_fields = self._parse_images_with_ocr(image_paths)
                    if ocr_fields:
                        results['strategies_used'].append('ocr')
                        results['field_counts']['ocr'] = len(ocr_fields)
                        self._add_fields(ocr_fields, 'ocr')
                
                # Strategy 4: GCP Vision/Document AI on images  
                if self.use_gcp:
                    gcp_fields = self._parse_images_with_gcp(image_paths)
                    if gcp_fields:
                        results['strategies_used'].append('gcp_ai')
                        results['field_counts']['gcp_ai'] = len(gcp_fields)
                        self._add_fields(gcp_fields, 'gcp_ai')
            
            # Strategy 5: If DOCX, also try converting to PDF for Document AI
            if self.file_path.suffix.lower() in ['.docx', '.doc']:
                pdf_path = self._convert_docx_to_pdf()
                if pdf_path and self.use_gcp:
                    pdf_gcp_fields = self._parse_pdf_with_gcp(pdf_path)
                    if pdf_gcp_fields:
                        results['strategies_used'].append('gcp_pdf')
                        results['field_counts']['gcp_pdf'] = len(pdf_gcp_fields)
                        self._add_fields(pdf_gcp_fields, 'gcp_pdf')
            
            # Strategy 6: Use existing intelligent parser
            intelligent_fields = self._parse_with_intelligent()
            if intelligent_fields:
                results['strategies_used'].append('intelligent')
                results['field_counts']['intelligent'] = len(intelligent_fields)
                self._add_fields(intelligent_fields, 'intelligent')
            
            # Build consensus
            final_fields = self._build_consensus()
            
            # Generate report
            results['consensus_report'] = self._generate_consensus_report(final_fields)
            results['total_fields'] = len(final_fields)
            
            return final_fields, results
            
        finally:
            # Clean up temp directory
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
    
    def _parse_with_advanced_docx(self) -> List[Dict]:
        """Parse using advanced DOCX parser"""
        try:
            if self.file_path.suffix.lower() not in ['.docx', '.doc']:
                return []
            
            logger.info("Parsing with advanced DOCX parser...")
            parser = AdvancedDocxParser(str(self.file_path))
            fields = parser.parse()
            
            # Convert to dict format
            return [asdict(field) for field in fields]
            
        except Exception as e:
            logger.error(f"Advanced DOCX parsing error: {e}")
            return []
    
    def _convert_to_images(self) -> List[str]:
        """Convert document to images for OCR/AI processing"""
        try:
            logger.info("Converting document to images...")
            image_paths = []
            
            if self.file_path.suffix.lower() == '.pdf':
                # Convert PDF to images
                pdf = pdfium.PdfDocument(str(self.file_path))
                for page_num, page in enumerate(pdf):
                    # Render at high resolution for better OCR
                    bitmap = page.render(scale=2.0)  # 2x resolution
                    pil_image = bitmap.to_pil()
                    
                    image_path = os.path.join(self.temp_dir, f"page_{page_num + 1}.png")
                    pil_image.save(image_path, "PNG")
                    image_paths.append(image_path)
                
            elif self.file_path.suffix.lower() in ['.docx', '.doc']:
                # Convert DOCX to images via PDF
                pdf_path = self._convert_docx_to_pdf()
                if pdf_path:
                    # Now convert PDF to images
                    pdf = pdfium.PdfDocument(pdf_path)
                    for page_num, page in enumerate(pdf):
                        bitmap = page.render(scale=2.0)
                        pil_image = bitmap.to_pil()
                        
                        image_path = os.path.join(self.temp_dir, f"page_{page_num + 1}.png")
                        pil_image.save(image_path, "PNG")
                        image_paths.append(image_path)
            
            logger.info(f"Converted to {len(image_paths)} images")
            return image_paths
            
        except Exception as e:
            logger.error(f"Image conversion error: {e}")
            return []
    
    def _convert_docx_to_pdf(self) -> Optional[str]:
        """Convert DOCX to PDF for processing"""
        try:
            # Use mammoth to convert to HTML then to PDF
            # Or use LibreOffice in headless mode if available
            
            # For now, we'll save this for GCP Document AI which can handle PDFs
            # In production, you'd use:
            # - LibreOffice: soffice --headless --convert-to pdf file.docx
            # - Or a library like docx2pdf
            
            logger.info("DOCX to PDF conversion would happen here")
            return None
            
        except Exception as e:
            logger.error(f"DOCX to PDF conversion error: {e}")
            return None
    
    def _parse_images_with_ocr(self, image_paths: List[str]) -> List[Dict]:
        """Parse images using OCR"""
        fields = []
        
        if not TESSERACT_AVAILABLE:
            return fields
        
        logger.info("Parsing images with OCR...")
        
        for page_num, image_path in enumerate(image_paths, 1):
            try:
                # Load image
                image = Image.open(image_path)
                
                # Apply OCR with different configs
                configs = [
                    '--psm 6',  # Uniform block of text
                    '--psm 11',  # Sparse text
                    '--psm 3'   # Fully automatic
                ]
                
                for config in configs:
                    text = pytesseract.image_to_string(image, config=config)
                    
                    # Extract fields from OCR text
                    ocr_fields = self._extract_fields_from_text(text, page_num, f"ocr_{config}")
                    fields.extend(ocr_fields)
                
                # Also get detailed data
                data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                detailed_fields = self._extract_fields_from_ocr_data(data, page_num)
                fields.extend(detailed_fields)
                
            except Exception as e:
                logger.debug(f"OCR error on page {page_num}: {e}")
        
        return fields
    
    def _parse_images_with_gcp(self, image_paths: List[str]) -> List[Dict]:
        """Parse images using GCP Vision API"""
        fields = []
        
        if not self.use_gcp:
            return fields
        
        logger.info("Parsing images with GCP Vision API...")
        
        try:
            client = vision.ImageAnnotatorClient()
            
            for page_num, image_path in enumerate(image_paths, 1):
                with open(image_path, 'rb') as image_file:
                    content = image_file.read()
                
                image = vision.Image(content=content)
                
                # Document text detection
                response = client.document_text_detection(image=image)
                
                if response.full_text_annotation:
                    # Extract fields from structured text
                    for page in response.full_text_annotation.pages:
                        for block in page.blocks:
                            block_text = self._get_block_text(block)
                            if self._looks_like_field(block_text):
                                field = {
                                    'field_name': f"gcp_vision_{page_num}_{len(fields)}",
                                    'field_type': self._detect_field_type(block_text),
                                    'field_label': block_text[:100],
                                    'confidence': block.confidence,
                                    'page_number': page_num,
                                    'extraction_method': 'gcp_vision',
                                    'coordinates': {
                                        'vertices': [
                                            {'x': v.x, 'y': v.y}
                                            for v in block.bounding_box.vertices
                                        ]
                                    }
                                }
                                fields.append(field)
                
                # Form detection
                response = client.text_detection(image=image)
                texts = response.text_annotations
                
                if texts:
                    full_text = texts[0].description
                    text_fields = self._extract_fields_from_text(full_text, page_num, 'gcp_text')
                    fields.extend(text_fields)
        
        except Exception as e:
            logger.error(f"GCP Vision API error: {e}")
        
        return fields
    
    def _parse_pdf_with_gcp(self, pdf_path: str) -> List[Dict]:
        """Parse PDF using GCP Document AI"""
        fields = []
        
        if not self.use_gcp:
            return fields
        
        try:
            logger.info("Parsing PDF with GCP Document AI...")
            
            # Use Document AI Form Parser
            project_id = os.environ.get('GCP_PROJECT_ID', '')
            location = os.environ.get('GCP_LOCATION', 'us')
            processor_id = os.environ.get('DOCAI_FORM_PARSER_ID', '')
            
            if not all([project_id, processor_id]):
                logger.warning("GCP Document AI not configured")
                return fields
            
            client = documentai.DocumentProcessorServiceClient()
            
            # Read PDF
            with open(pdf_path, 'rb') as f:
                content = f.read()
            
            # Configure request
            name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"
            
            request = documentai.ProcessRequest(
                name=name,
                raw_document=documentai.RawDocument(
                    content=content,
                    mime_type='application/pdf'
                )
            )
            
            # Process document
            result = client.process_document(request=request)
            
            # Extract form fields
            for page in result.document.pages:
                for form_field in page.form_fields:
                    field_name = self._get_docai_text(form_field.field_name, result.document)
                    field_value = self._get_docai_text(form_field.field_value, result.document)
                    
                    field = {
                        'field_name': field_name or f"docai_field_{len(fields)}",
                        'field_type': 'text',
                        'field_label': field_name,
                        'value': field_value,
                        'confidence': form_field.field_name.confidence if form_field.field_name else 0.5,
                        'page_number': page.page_number,
                        'extraction_method': 'gcp_documentai'
                    }
                    fields.append(field)
            
            # Extract entities
            for entity in result.document.entities:
                field = {
                    'field_name': entity.type_,
                    'field_type': self._map_entity_type(entity.type_),
                    'field_label': entity.mention_text,
                    'value': entity.normalized_value.text if entity.normalized_value else None,
                    'confidence': entity.confidence,
                    'extraction_method': 'gcp_documentai_entity'
                }
                fields.append(field)
        
        except Exception as e:
            logger.error(f"GCP Document AI error: {e}")
        
        return fields
    
    def _parse_with_intelligent(self) -> List[Dict]:
        """Parse using intelligent parser"""
        try:
            logger.info("Parsing with intelligent parser...")
            parser = IntelligentFormParser(str(self.file_path), use_ocr=False)
            fields = parser.parse()
            
            # Convert to dict format
            return [asdict(field) for field in fields]
            
        except Exception as e:
            logger.error(f"Intelligent parser error: {e}")
            return []
    
    def _add_fields(self, fields: List[Dict], source: str):
        """Add fields to collection"""
        for field in fields:
            # Create unique key
            key = self._get_field_key(field)
            
            if key not in self.all_fields:
                self.all_fields[key] = []
            
            # Add source to field
            field['source'] = source
            self.all_fields[key].append(field)
    
    def _get_field_key(self, field: Dict) -> str:
        """Generate unique key for field grouping"""
        field_type = field.get('field_type', 'text')
        field_label = field.get('field_label', '')[:30].lower()
        page = field.get('page_number', 0)
        
        # Normalize label
        import re
        field_label = re.sub(r'[^\w\s]', '', field_label)
        field_label = re.sub(r'\s+', '_', field_label)
        
        return f"{field_type}_{field_label}_{page}"
    
    def _build_consensus(self) -> List[HybridField]:
        """Build consensus from all extracted fields"""
        logger.info("Building consensus from all extraction methods...")
        
        final_fields = []
        
        for field_key, field_list in self.all_fields.items():
            if not field_list:
                continue
            
            # Create hybrid field
            hybrid_field = HybridField(
                field_id=f"hybrid_{len(final_fields)}",
                field_name=field_list[0].get('field_name', ''),
                field_type=self._consensus_field_type(field_list),
                field_label=self._consensus_field_label(field_list),
                value=self._consensus_value(field_list),
                page_number=field_list[0].get('page_number', 0)
            )
            
            # Aggregate confidence and methods
            total_confidence = 0
            for field in field_list:
                source = field.get('source', 'unknown')
                method = field.get('extraction_method', source)
                
                if method not in hybrid_field.extraction_methods:
                    hybrid_field.extraction_methods.append(method)
                
                confidence = field.get('confidence', 0.5)
                total_confidence += confidence
            
            # Calculate consensus confidence
            hybrid_field.confidence = total_confidence / len(field_list)
            
            # Boost confidence if multiple methods agree
            if len(hybrid_field.extraction_methods) > 1:
                hybrid_field.confidence = min(1.0, hybrid_field.confidence * 1.2)
            
            # Add context from most confident source
            best_field = max(field_list, key=lambda x: x.get('confidence', 0))
            hybrid_field.context = best_field.get('context', '')
            
            final_fields.append(hybrid_field)
        
        # Sort by confidence
        final_fields.sort(key=lambda x: x.confidence, reverse=True)
        
        return final_fields
    
    def _consensus_field_type(self, field_list: List[Dict]) -> str:
        """Determine consensus field type"""
        from collections import Counter
        types = [f.get('field_type', 'text') for f in field_list]
        if types:
            return Counter(types).most_common(1)[0][0]
        return 'text'
    
    def _consensus_field_label(self, field_list: List[Dict]) -> str:
        """Determine consensus field label"""
        # Use the label from the highest confidence source
        best = max(field_list, key=lambda x: x.get('confidence', 0))
        return best.get('field_label', '')
    
    def _consensus_value(self, field_list: List[Dict]) -> Optional[str]:
        """Determine consensus value if present"""
        values = [f.get('value') for f in field_list if f.get('value')]
        if values:
            from collections import Counter
            return Counter(values).most_common(1)[0][0]
        return None
    
    def _generate_consensus_report(self, fields: List[HybridField]) -> Dict:
        """Generate consensus report"""
        report = {
            'total_fields': len(fields),
            'high_confidence': sum(1 for f in fields if f.confidence >= 0.8),
            'medium_confidence': sum(1 for f in fields if 0.5 <= f.confidence < 0.8),
            'low_confidence': sum(1 for f in fields if f.confidence < 0.5),
            'multi_method': sum(1 for f in fields if len(f.extraction_methods) > 1),
            'field_types': {},
            'method_coverage': {}
        }
        
        # Count field types
        for field in fields:
            ftype = field.field_type
            if ftype not in report['field_types']:
                report['field_types'][ftype] = 0
            report['field_types'][ftype] += 1
        
        # Count method coverage
        for field in fields:
            for method in field.extraction_methods:
                if method not in report['method_coverage']:
                    report['method_coverage'][method] = 0
                report['method_coverage'][method] += 1
        
        return report
    
    def _extract_fields_from_text(self, text: str, page_num: int, method: str) -> List[Dict]:
        """Extract fields from text using patterns"""
        fields = []
        
        if not text:
            return fields
        
        # Ontario form patterns
        patterns = {
            'name': r'(?:First|Last|Middle|Full)\s+(?:Legal\s+)?Name\s*:?\s*_{3,}|\[.*?\]',
            'date': r'Date\s+of\s+\w+\s*:?\s*_{3,}|\d{1,2}/\d{1,2}/\d{4}',
            'address': r'Address\s*:?\s*_{3,}',
            'phone': r'Phone\s*:?\s*\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|_{10,}',
            'email': r'Email\s*:?\s*\S+@\S+|_{20,}',
            'currency': r'\$\s*_{5,}|\$\s*[\d,]+\.?\d*',
            'checkbox': r'[☐□]\s*([^☐□\n]+)',
            'court_file': r'Court\s+File\s+(?:Number|No\.?)\s*:?\s*_{10,}'
        }
        
        for pattern_name, pattern in patterns.items():
            import re
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                field = {
                    'field_name': f"{pattern_name}_{page_num}_{len(fields)}",
                    'field_type': self._get_pattern_type(pattern_name),
                    'field_label': match.group(0)[:100],
                    'confidence': 0.7,
                    'page_number': page_num,
                    'extraction_method': method
                }
                fields.append(field)
        
        return fields
    
    def _extract_fields_from_ocr_data(self, data: Dict, page_num: int) -> List[Dict]:
        """Extract fields from detailed OCR data"""
        fields = []
        
        for i, text in enumerate(data.get('text', [])):
            if text and self._looks_like_field(text):
                conf = float(data['conf'][i]) / 100.0 if data['conf'][i] > 0 else 0.5
                
                field = {
                    'field_name': f"ocr_detailed_{page_num}_{i}",
                    'field_type': self._detect_field_type(text),
                    'field_label': text[:100],
                    'confidence': conf,
                    'page_number': page_num,
                    'extraction_method': 'ocr_detailed',
                    'coordinates': {
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i]
                    }
                }
                fields.append(field)
        
        return fields
    
    def _get_block_text(self, block) -> str:
        """Extract text from GCP Vision block"""
        text = ""
        for paragraph in block.paragraphs:
            for word in paragraph.words:
                for symbol in word.symbols:
                    text += symbol.text
                text += " "
        return text.strip()
    
    def _get_docai_text(self, layout, document) -> str:
        """Extract text from Document AI layout"""
        if not layout or not layout.text_anchor:
            return ""
        
        text = ""
        for segment in layout.text_anchor.text_segments:
            start = segment.start_index if segment.start_index else 0
            end = segment.end_index if segment.end_index else len(document.text)
            text += document.text[start:end]
        
        return text.strip()
    
    def _looks_like_field(self, text: str) -> bool:
        """Check if text looks like a form field"""
        if not text or len(text) < 2:
            return False
        
        indicators = ['___', '...', '[ ]', '☐', '□', ':', '$']
        keywords = ['name', 'date', 'address', 'phone', 'email', 'amount']
        
        text_lower = text.lower()
        return (any(ind in text for ind in indicators) or
                any(kw in text_lower for kw in keywords))
    
    def _detect_field_type(self, text: str) -> str:
        """Detect field type from text"""
        text_lower = text.lower()
        
        if any(kw in text_lower for kw in ['date', 'when', 'birth']):
            return 'date'
        elif any(kw in text_lower for kw in ['email', 'e-mail']):
            return 'email'
        elif any(kw in text_lower for kw in ['phone', 'tel']):
            return 'phone'
        elif '$' in text or any(kw in text_lower for kw in ['amount', 'payment']):
            return 'currency'
        elif '☐' in text or '□' in text:
            return 'checkbox'
        elif any(kw in text_lower for kw in ['signature', 'sign']):
            return 'signature'
        
        return 'text'
    
    def _get_pattern_type(self, pattern_name: str) -> str:
        """Get field type from pattern name"""
        type_map = {
            'name': 'text',
            'date': 'date',
            'address': 'text',
            'phone': 'phone',
            'email': 'email',
            'currency': 'currency',
            'checkbox': 'checkbox',
            'court_file': 'text'
        }
        return type_map.get(pattern_name, 'text')
    
    def _map_entity_type(self, entity_type: str) -> str:
        """Map entity type to field type"""
        entity_map = {
            'person': 'text',
            'location': 'address',
            'date': 'date',
            'money': 'currency',
            'phone_number': 'phone',
            'email': 'email'
        }
        return entity_map.get(entity_type.lower(), 'text')

def test_hybrid_parser(file_path: str):
    """Test the hybrid parser"""
    
    print("=" * 80)
    print("HYBRID FORM PARSER TEST")
    print("=" * 80)
    print(f"File: {Path(file_path).name}")
    
    # Set GCP environment if available
    os.environ['GCP_PROJECT_ID'] = os.environ.get('GCP_PROJECT_ID', 'default-456005')
    os.environ['GCP_LOCATION'] = os.environ.get('GCP_LOCATION', 'us')
    os.environ['DOCAI_FORM_PARSER_ID'] = os.environ.get('DOCAI_FORM_PARSER_ID', '688d4082bdc65cd2')
    
    # Parse with hybrid approach
    parser = HybridFormParser(file_path, use_ocr=True, use_gcp=GCP_AVAILABLE)
    fields, report = parser.parse()
    
    print(f"\nStrategies used: {', '.join(report['strategies_used'])}")
    print(f"Total fields extracted: {len(fields)}")
    
    # Show field counts by strategy
    print("\nFields by strategy:")
    for strategy, count in report['field_counts'].items():
        print(f"  {strategy}: {count} fields")
    
    # Show consensus report
    consensus = report['consensus_report']
    print(f"\nConsensus Report:")
    print(f"  High confidence: {consensus['high_confidence']}")
    print(f"  Multi-method agreement: {consensus['multi_method']}")
    
    print(f"\nField types:")
    for ftype, count in consensus['field_types'].items():
        print(f"  {ftype}: {count}")
    
    print(f"\nMethod coverage:")
    for method, count in list(consensus['method_coverage'].items())[:5]:
        print(f"  {method}: {count} fields")
    
    # Show sample high-confidence fields
    print(f"\nSample high-confidence fields:")
    for field in fields[:5]:
        print(f"  [{field.confidence:.2f}] {field.field_label[:40]}")
        print(f"    Type: {field.field_type}, Methods: {', '.join(field.extraction_methods[:3])}")
    
    # Save results
    output_file = f"hybrid_{Path(file_path).stem}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'report': report,
            'fields': [asdict(field) for field in fields]
        }, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    
    return fields, report

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        # Test on Form 13
        test_file = "workflow_output/ontario_forms/financial_statements/form_13_-_financial_statement_support_flr-13-may21-en-fil.docx"
        if not os.path.exists(test_file):
            test_file = "workflow_output/ontario_forms/applications/form_8_-_application_general_flr-8-jun25-en-fil.docx"
    else:
        test_file = sys.argv[1]
    
    if os.path.exists(test_file):
        fields, report = test_hybrid_parser(test_file)
    else:
        print(f"File not found: {test_file}")