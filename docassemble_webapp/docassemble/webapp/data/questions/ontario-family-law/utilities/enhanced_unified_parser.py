#!/usr/bin/env python3
"""
Enhanced Unified Parser with Content Classification
Extracts and classifies all content from forms
"""

import os
import json
import csv
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

# Import parsers
import PyPDF2
import pdfplumber
from docx import Document
import fitz  # PyMuPDF

# Import content classifier
from content_classifier import ContentClassifier, ContentType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ParsedContent:
    """Represents parsed and classified content"""
    content_id: str
    content_type: str
    text: str
    cleaned_text: str
    page_number: int
    line_number: Optional[int]
    metadata: Dict
    
    def to_dict(self) -> Dict:
        return asdict(self)

class EnhancedUnifiedParser:
    """Enhanced parser that classifies all content types"""
    
    def __init__(self):
        self.classifier = ContentClassifier()
        self.content_items = []
        self.fields = []
        self.instructions = []
        self.legal_texts = []
        self.headings = []
        
    def parse_comprehensive(self, file_path: str) -> Dict:
        """Parse and classify all content from a form"""
        logger.info(f"Starting comprehensive parsing of {Path(file_path).name}")
        
        self.content_items = []
        self.fields = []
        self.instructions = []
        self.legal_texts = []
        self.headings = []
        
        # Extract text based on file type
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            text_content = self._extract_pdf_content(file_path)
        elif file_ext in ['.docx', '.doc']:
            text_content = self._extract_docx_content(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_ext}")
            return self._create_result()
        
        # Classify all content
        self._classify_content(text_content)
        
        # Create comprehensive result
        return self._create_result()
    
    def _extract_pdf_content(self, file_path: str) -> List[Tuple[str, int]]:
        """Extract text content from PDF with page numbers"""
        content = []
        
        try:
            # Try multiple methods
            
            # Method 1: PyPDF2
            try:
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page_num, page in enumerate(pdf_reader.pages, 1):
                        text = page.extract_text()
                        if text:
                            lines = text.split('\n')
                            for line in lines:
                                if line.strip():
                                    content.append((line, page_num))
            except Exception as e:
                logger.debug(f"PyPDF2 failed: {e}")
            
            # Method 2: pdfplumber (better for tables)
            if not content:
                try:
                    with pdfplumber.open(file_path) as pdf:
                        for page_num, page in enumerate(pdf.pages, 1):
                            text = page.extract_text()
                            if text:
                                lines = text.split('\n')
                                for line in lines:
                                    if line.strip():
                                        content.append((line, page_num))
                            
                            # Also extract tables
                            tables = page.extract_tables()
                            for table in tables:
                                for row in table:
                                    for cell in row:
                                        if cell and cell.strip():
                                            content.append((cell, page_num))
                except Exception as e:
                    logger.debug(f"pdfplumber failed: {e}")
            
            # Method 3: PyMuPDF
            if not content:
                try:
                    pdf_document = fitz.open(file_path)
                    for page_num, page in enumerate(pdf_document, 1):
                        text = page.get_text()
                        if text:
                            lines = text.split('\n')
                            for line in lines:
                                if line.strip():
                                    content.append((line, page_num))
                    pdf_document.close()
                except Exception as e:
                    logger.debug(f"PyMuPDF failed: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to extract PDF content: {e}")
        
        return content
    
    def _extract_docx_content(self, file_path: str) -> List[Tuple[str, int]]:
        """Extract text content from DOCX"""
        content = []
        
        try:
            doc = Document(file_path)
            page_num = 1  # DOCX doesn't have pages, use section approximation
            
            # Extract paragraphs
            for para in doc.paragraphs:
                if para.text.strip():
                    content.append((para.text, page_num))
            
            # Extract tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            content.append((cell.text, page_num))
                            
        except Exception as e:
            logger.error(f"Failed to extract DOCX content: {e}")
        
        return content
    
    def _classify_content(self, text_content: List[Tuple[str, int]]):
        """Classify all extracted content"""
        
        for idx, (text, page_num) in enumerate(text_content):
            if not text or not text.strip():
                continue
            
            # Classify the content
            classification = self.classifier.classify_content(text)
            
            if not classification:
                continue
            
            # Create parsed content item
            content_item = ParsedContent(
                content_id=f"content_{idx:04d}",
                content_type=classification['content_type'],
                text=classification['text'],
                cleaned_text=classification['cleaned_text'],
                page_number=page_num,
                line_number=idx,
                metadata=classification.get('metadata', {})
            )
            
            self.content_items.append(content_item)
            
            # Organize by type
            if classification['content_type'] == ContentType.FIELD.value:
                self.fields.append(content_item)
            elif classification['content_type'] == ContentType.INSTRUCTION.value:
                self.instructions.append(content_item)
            elif classification['content_type'] == ContentType.LEGAL_TEXT.value:
                self.legal_texts.append(content_item)
            elif classification['content_type'] == ContentType.HEADING.value:
                self.headings.append(content_item)
    
    def _create_result(self) -> Dict:
        """Create comprehensive parsing result"""
        return {
            'total_content': len(self.content_items),
            'fields_count': len(self.fields),
            'instructions_count': len(self.instructions),
            'legal_texts_count': len(self.legal_texts),
            'headings_count': len(self.headings),
            'fields': [f.to_dict() for f in self.fields],
            'instructions': [i.to_dict() for i in self.instructions],
            'legal_texts': [l.to_dict() for l in self.legal_texts],
            'headings': [h.to_dict() for h in self.headings],
            'all_content': [c.to_dict() for c in self.content_items],
            'statistics': self.classifier.get_statistics()
        }
    
    def save_to_csv(self, result: Dict, output_path: str):
        """Save classified content to CSV"""
        csv_path = Path(output_path)
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'content_id', 'content_type', 'text', 'cleaned_text',
                'page_number', 'line_number', 'field_type', 'label',
                'required', 'length'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in result['all_content']:
                row = {
                    'content_id': item['content_id'],
                    'content_type': item['content_type'],
                    'text': item['text'][:200],  # Truncate long text
                    'cleaned_text': item['cleaned_text'],
                    'page_number': item['page_number'],
                    'line_number': item.get('line_number', ''),
                    'field_type': item['metadata'].get('field_type', ''),
                    'label': item['metadata'].get('label', ''),
                    'required': item['metadata'].get('required', ''),
                    'length': item['metadata'].get('length', 0)
                }
                writer.writerow(row)
        
        logger.info(f"Saved CSV to {csv_path}")
    
    def save_to_json(self, result: Dict, output_path: str):
        """Save classified content to JSON"""
        json_path = Path(output_path)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved JSON to {json_path}")

def test_enhanced_parser():
    """Test the enhanced parser"""
    parser = EnhancedUnifiedParser()
    
    # Test with a sample form
    test_files = [
        'workflow_output/ontario_forms/form_13_-_financial_statement_support_flr-13-may21-en-fil.docx',
        'workflow_output/ontario_forms/form_8a_-_application_divorce_flr-8a-apr24-en-fil.docx',
    ]
    
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"\nParsing {Path(test_file).name}")
            print("="*60)
            
            result = parser.parse_comprehensive(test_file)
            
            print(f"Total content items: {result['total_content']}")
            print(f"Fields: {result['fields_count']}")
            print(f"Instructions: {result['instructions_count']}")
            print(f"Legal texts: {result['legal_texts_count']}")
            print(f"Headings: {result['headings_count']}")
            
            # Show sample fields
            if result['fields']:
                print("\nSample Fields:")
                for field in result['fields'][:5]:
                    print(f"  - {field['cleaned_text'][:50]}")
                    print(f"    Type: {field['metadata'].get('field_type', 'text')}")
                    print(f"    Required: {field['metadata'].get('required', False)}")
            
            # Show sample instructions
            if result['instructions']:
                print("\nSample Instructions:")
                for instruction in result['instructions'][:3]:
                    print(f"  - {instruction['cleaned_text'][:80]}...")
            
            # Save outputs
            base_name = Path(test_file).stem
            parser.save_to_csv(result, f"test_output/{base_name}_classified.csv")
            parser.save_to_json(result, f"test_output/{base_name}_classified.json")
            
            break  # Just test one file

if __name__ == "__main__":
    test_enhanced_parser()