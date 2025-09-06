#!/usr/bin/env python3
"""
Context-Enhanced Parser for Ontario Family Law Forms
Extracts fields with rich context from surrounding text to enable intelligent naming
"""

import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from docx import Document
from docx.text.paragraph import Paragraph
from docx.table import Table, _Cell
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ContextualField:
    """Form field with rich contextual information"""
    field_id: str
    field_name: str
    field_type: str
    field_label: str
    
    # Context information for intelligent naming
    surrounding_text: str = ""  # Text near the field
    preceding_text: str = ""    # Text before the field
    following_text: str = ""    # Text after the field
    paragraph_text: str = ""    # Full paragraph containing the field
    
    # Document structure context  
    table_headers: List[str] = None
    table_context: str = ""
    section_heading: str = ""
    page_context: str = ""
    
    # Field properties
    required: bool = False
    validation_rules: str = ""
    max_length: Optional[int] = None
    options: Optional[List[str]] = None
    help_text: Optional[str] = None
    
    # Location information
    table_name: Optional[str] = None
    table_row: Optional[int] = None
    section: Optional[str] = None
    original_name: str = ""  # Original nonsense name if applicable
    confidence_score: float = 0.5  # Confidence in intelligent name


class ContextEnhancedParser:
    """Parser that extracts rich context for intelligent field naming"""
    
    # Ontario-specific field patterns with context clues
    ONTARIO_PATTERNS = {
        'court_info': [
            (r'court\s+file\s+no|court\s+file\s+number|file\s+no', 'court_file_number'),
            (r'court\s+(?:office\s+)?address', 'court_address'),
            (r'municipality', 'municipality'),
            (r'province', 'province'),
            (r'superior\s+court|ontario\s+court', 'court_name'),
        ],
        'party_info': [
            (r'(?:applicant|respondent|party).*full.*legal.*name', 'full_legal_name'),
            (r'(?:applicant|respondent).*first.*name', 'first_name'),
            (r'(?:applicant|respondent).*last.*name', 'last_name'),
            (r'(?:applicant|respondent).*middle.*name', 'middle_name'),
            (r'date\s+of\s+birth|birth\s+date|birthdate', 'birth_date'),
            (r'street.*address|address.*line', 'street_address'),
            (r'city|town', 'city'),
            (r'postal.*code', 'postal_code'),
            (r'phone.*number|telephone', 'phone_number'),
            (r'email.*address|email', 'email_address'),
            (r'occupation', 'occupation'),
        ],
        'legal_rep': [
            (r'lawyer.*name', 'lawyer_name'),
            (r'law\s+firm', 'law_firm'),
            (r'lso\s+(?:number|#)|law\s+society', 'lso_number'),
        ],
        'relationship': [
            (r'date.*marriage|marriage.*date', 'marriage_date'),
            (r'place.*marriage|marriage.*place', 'marriage_place'),
            (r'date.*separation|separation.*date', 'separation_date'),
            (r'name.*before.*marriage', 'name_before_marriage'),
        ],
        'children': [
            (r'child.*full.*name|child.*name', 'child_name'),
            (r'child.*birth.*date|child.*birthdate', 'child_birthdate'),
            (r'child.*age', 'child_age'),
            (r'residing\s+with|lives\s+with', 'child_residing_with'),
            (r'relationship.*applicant', 'relationship_to_applicant'),
            (r'relationship.*respondent', 'relationship_to_respondent'),
        ],
        'claims': [
            (r'divorce', 'claim_divorce'),
            (r'custody', 'claim_custody'),
            (r'access', 'claim_access'),
            (r'child.*support', 'claim_child_support'),
            (r'spousal.*support', 'claim_spousal_support'),
            (r'property|equalization', 'claim_property'),
            (r'restraining.*order', 'claim_restraining_order'),
        ]
    }

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.form_number = self._extract_form_number()
        self.fields = []
        self.document = None
        self.all_paragraphs = []
        self.all_tables = []
        self.section_headings = []

    def _extract_form_number(self) -> str:
        """Extract form number from filename"""
        filename = self.file_path.stem.lower()
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

    def parse(self) -> List[ContextualField]:
        """Parse document with rich context extraction"""
        logger.info(f"Parsing {self.file_path.name} with context enhancement...")
        
        try:
            # Load document
            self.document = Document(self.file_path)
            
            # Extract document structure for context
            self._analyze_document_structure()
            
            # Extract fields with context
            self._extract_form_fields_with_context()
            self._extract_content_controls_with_context()
            self._extract_table_fields_with_context()
            self._extract_text_pattern_fields()
            
            # Apply intelligent naming
            self._apply_intelligent_naming()
            
            logger.info(f"Found {len(self.fields)} fields with contextual information")
            
        except Exception as e:
            logger.error(f"Error parsing document: {e}")
            
        return self.fields

    def _analyze_document_structure(self):
        """Analyze document structure to understand context"""
        self.all_paragraphs = []
        self.all_tables = []
        self.section_headings = []
        
        for paragraph in self.document.paragraphs:
            self.all_paragraphs.append(paragraph)
            
            # Identify section headings (bold, larger text, or specific patterns)
            if self._is_section_heading(paragraph):
                self.section_headings.append({
                    'text': paragraph.text.strip(),
                    'index': len(self.all_paragraphs) - 1
                })
        
        for table in self.document.tables:
            self.all_tables.append(table)

    def _is_section_heading(self, paragraph) -> bool:
        """Determine if paragraph is a section heading"""
        text = paragraph.text.strip().lower()
        
        # Check for heading styles
        if any(run.bold for run in paragraph.runs):
            return True
            
        # Check for heading patterns
        heading_patterns = [
            r'^\d+\.\s+',  # Numbered sections
            r'^[ivx]+\.\s+',  # Roman numerals
            r'^[a-z]\)\s+',  # Letter sections
            r'applicant.*information',
            r'respondent.*information',
            r'children.*information',
            r'court.*information',
            r'claims.*for.*relief',
            r'important.*facts',
        ]
        
        return any(re.match(pattern, text) for pattern in heading_patterns)

    def _extract_form_fields_with_context(self):
        """Extract legacy form fields with contextual information"""
        try:
            # Parse XML to find form fields
            with zipfile.ZipFile(self.file_path, 'r') as docx:
                if 'word/document.xml' in docx.namelist():
                    with docx.open('word/document.xml') as xml_file:
                        tree = ET.parse(xml_file)
                        root = tree.getroot()
                        
                        # Find form field elements
                        for elem in root.iter():
                            if elem.tag.endswith('ffData'):
                                self._process_form_field_with_context(elem)
                                
        except Exception as e:
            logger.debug(f"Error extracting XML form fields: {e}")

    def _process_form_field_with_context(self, ff_elem):
        """Process form field and extract surrounding context"""
        try:
            # Extract basic field information
            name = None
            for child in ff_elem:
                if child.tag.endswith('name'):
                    ns = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
                    name = child.get(f'{ns}val', '')
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
                    options = self._extract_dropdown_options(child)

            # Find the field's context in the document
            context = self._find_field_context(name, field_type)
            
            field = ContextualField(
                field_id=f"form{self.form_number}_{name}",
                field_name=name,
                field_type=field_type,
                field_label=self._humanize_name(name),
                surrounding_text=context.get('surrounding_text', ''),
                preceding_text=context.get('preceding_text', ''),
                following_text=context.get('following_text', ''),
                paragraph_text=context.get('paragraph_text', ''),
                section_heading=context.get('section_heading', ''),
                options=options,
                original_name=name,
                confidence_score=context.get('confidence', 0.5)
            )
            
            self.fields.append(field)
            
        except Exception as e:
            logger.debug(f"Error processing form field: {e}")

    def _extract_content_controls_with_context(self):
        """Extract content controls with rich context"""
        try:
            # Use XML to find content controls
            with zipfile.ZipFile(self.file_path, 'r') as docx:
                if 'word/document.xml' in docx.namelist():
                    with docx.open('word/document.xml') as xml_file:
                        content = xml_file.read().decode('utf-8')
                        
                        # Find content control patterns
                        sdt_pattern = r'<w:sdt\b[^>]*>.*?</w:sdt>'
                        controls = re.findall(sdt_pattern, content, re.DOTALL)
                        
                        for control_xml in controls:
                            self._process_content_control_with_context(control_xml)
                            
        except Exception as e:
            logger.debug(f"Error extracting content controls: {e}")

    def _process_content_control_with_context(self, control_xml: str):
        """Process content control with context analysis"""
        try:
            # Extract tag/alias
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

            # Extract placeholder
            placeholder_match = re.search(r'<w:placeholder>.*?<w:docPart[^>]*w:val="([^"]+)"', control_xml)
            placeholder = placeholder_match.group(1) if placeholder_match else ''

            # Find context in document
            context = self._find_field_context(name, field_type, placeholder)
            
            field = ContextualField(
                field_id=f"form{self.form_number}_{name}",
                field_name=name,
                field_type=field_type,
                field_label=placeholder or self._humanize_name(name),
                surrounding_text=context.get('surrounding_text', ''),
                preceding_text=context.get('preceding_text', ''),
                following_text=context.get('following_text', ''),
                paragraph_text=context.get('paragraph_text', ''),
                section_heading=context.get('section_heading', ''),
                original_name=name,
                confidence_score=context.get('confidence', 0.7)
            )
            
            self.fields.append(field)
            
        except Exception as e:
            logger.debug(f"Error processing content control: {e}")

    def _extract_table_fields_with_context(self):
        """Extract table fields with rich context from headers and surrounding text"""
        for table_idx, table in enumerate(self.all_tables):
            # Get table headers for context
            headers = self._extract_table_headers(table)
            table_context = self._get_table_context(table, table_idx)
            
            for row_idx, row in enumerate(table.rows):
                for cell_idx, cell in enumerate(row.cells):
                    if self._is_field_cell(cell.text):
                        field = self._create_table_field(
                            table_idx, row_idx, cell_idx, cell, headers, table_context
                        )
                        if field:
                            self.fields.append(field)

    def _extract_table_headers(self, table) -> List[str]:
        """Extract table headers for context"""
        headers = []
        if table.rows:
            first_row = table.rows[0]
            for cell in first_row.cells:
                headers.append(cell.text.strip())
        return headers

    def _get_table_context(self, table, table_idx: int) -> str:
        """Get context around a table"""
        # Find paragraphs before the table that might describe it
        context_parts = []
        
        # Look for preceding paragraphs that describe the table
        for paragraph in self.all_paragraphs:
            text = paragraph.text.strip().lower()
            if any(word in text for word in ['child', 'information', 'details', 'table']):
                context_parts.append(paragraph.text.strip())
        
        return ' '.join(context_parts[-3:])  # Last 3 relevant paragraphs

    def _is_field_cell(self, cell_text: str) -> bool:
        """Check if table cell contains a form field"""
        indicators = [
            r'_{3,}',  # Underscores
            r'☐|□',    # Checkboxes
            r'\[\s*\]', # Empty brackets
            r':\s*$',   # Ending with colon
        ]
        return any(re.search(indicator, cell_text) for indicator in indicators)

    def _create_table_field(self, table_idx: int, row_idx: int, cell_idx: int, 
                           cell, headers: List[str], table_context: str) -> Optional[ContextualField]:
        """Create field from table cell with rich context"""
        
        cell_text = cell.text.strip()
        if not cell_text:
            return None
            
        # Use header as context if available
        header_text = headers[cell_idx] if cell_idx < len(headers) else ''
        
        # Create context from cell, header, and table context
        surrounding_text = ' '.join([header_text, table_context, cell_text]).strip()
        
        field_name = f"table_{table_idx}_row_{row_idx}_cell_{cell_idx}"
        field_type = self._infer_field_type(cell_text, surrounding_text)
        
        return ContextualField(
            field_id=f"form{self.form_number}_{field_name}",
            field_name=field_name,
            field_type=field_type,
            field_label=header_text or cell_text,
            surrounding_text=surrounding_text,
            table_headers=headers,
            table_context=table_context,
            table_name=f"Table {table_idx + 1}",
            table_row=row_idx,
            original_name=field_name,
            confidence_score=0.6
        )

    def _extract_text_pattern_fields(self):
        """Extract fields based on text patterns in paragraphs"""
        for para_idx, paragraph in enumerate(self.all_paragraphs):
            text = paragraph.text.strip()
            if not text:
                continue
                
            # Look for field patterns
            for category, patterns in self.ONTARIO_PATTERNS.items():
                for pattern, field_name in patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        # Create field with paragraph context
                        context = self._get_paragraph_context(para_idx, text)
                        
                        field = ContextualField(
                            field_id=f"form{self.form_number}_{field_name}",
                            field_name=field_name,
                            field_type=self._infer_field_type(text, context.get('surrounding_text', '')),
                            field_label=self._humanize_name(field_name),
                            surrounding_text=context.get('surrounding_text', ''),
                            preceding_text=context.get('preceding_text', ''),
                            following_text=context.get('following_text', ''),
                            paragraph_text=text,
                            section_heading=context.get('section_heading', ''),
                            section=category,
                            confidence_score=0.8
                        )
                        
                        self.fields.append(field)

    def _get_paragraph_context(self, para_idx: int, paragraph_text: str) -> Dict[str, str]:
        """Get context around a paragraph"""
        context = {
            'surrounding_text': paragraph_text,
            'preceding_text': '',
            'following_text': '',
            'section_heading': ''
        }
        
        # Get preceding paragraph
        if para_idx > 0:
            context['preceding_text'] = self.all_paragraphs[para_idx - 1].text.strip()
            
        # Get following paragraph
        if para_idx < len(self.all_paragraphs) - 1:
            context['following_text'] = self.all_paragraphs[para_idx + 1].text.strip()
            
        # Find relevant section heading
        for heading in reversed(self.section_headings):
            if heading['index'] < para_idx:
                context['section_heading'] = heading['text']
                break
                
        return context

    def _find_field_context(self, field_name: str, field_type: str, placeholder: str = '') -> Dict[str, Any]:
        """Find context for a field in the document"""
        context = {
            'surrounding_text': placeholder,
            'preceding_text': '',
            'following_text': '',
            'paragraph_text': '',
            'section_heading': '',
            'confidence': 0.5
        }
        
        # Search through paragraphs for field references
        search_terms = [field_name, placeholder]
        if field_type == 'checkbox':
            search_terms.extend(['☐', '□', 'check', 'box'])
        
        for para_idx, paragraph in enumerate(self.all_paragraphs):
            text = paragraph.text
            
            # Check if this paragraph contains field references
            if any(term and term.lower() in text.lower() for term in search_terms if term):
                context.update(self._get_paragraph_context(para_idx, text))
                context['confidence'] = 0.8
                break
                
        return context

    def _apply_intelligent_naming(self):
        """Apply intelligent naming to fields with poor names"""
        for field in self.fields:
            if self._needs_intelligent_naming(field.field_name):
                new_name = self._generate_intelligent_name(field)
                if new_name and new_name != field.field_name:
                    field.field_name = new_name
                    field.field_id = field.field_id.replace(field.original_name, new_name)
                    field.field_label = self._humanize_name(new_name)

    def _needs_intelligent_naming(self, name: str) -> bool:
        """Check if field name needs intelligent improvement"""
        patterns = [
            r'^field_?\d*$',
            r'^table_\d+_row_\d+_cell_\d+$',
            r'^text_field_?\d*$',
            r'^checkbox_?\d*$',
        ]
        return any(re.match(pattern, name.lower()) for pattern in patterns)

    def _generate_intelligent_name(self, field: ContextualField) -> str:
        """Generate intelligent name from rich context"""
        
        # Collect all context for analysis
        all_context = ' '.join([
            field.surrounding_text or '',
            field.preceding_text or '',
            field.following_text or '',
            field.paragraph_text or '',
            field.section_heading or '',
            ' '.join(field.table_headers or []),
            field.table_context or ''
        ]).lower()
        
        # Try Ontario-specific patterns
        for category, patterns in self.ONTARIO_PATTERNS.items():
            for pattern, intelligent_name in patterns:
                if re.search(pattern, all_context, re.IGNORECASE):
                    return intelligent_name
        
        # Extract meaningful keywords
        keywords = self._extract_keywords(all_context)
        if keywords:
            return '_'.join(keywords[:3])  # Use top 3 keywords
        
        # Fallback based on field type and position
        if field.table_name:
            return f"{field.field_type}_field_{field.table_row}"
        else:
            return f"{field.field_type}_field"

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text"""
        if not text:
            return []
        
        # Clean text
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        
        # Important keywords for forms
        important_words = [
            'name', 'address', 'phone', 'email', 'date', 'birth', 'marriage',
            'separation', 'court', 'file', 'number', 'applicant', 'respondent',
            'child', 'custody', 'support', 'property', 'divorce', 'legal',
            'lawyer', 'occupation', 'income', 'asset', 'debt'
        ]
        
        # Skip common words
        skip_words = {
            'the', 'and', 'for', 'with', 'this', 'that', 'your', 'please',
            'enter', 'provide', 'field', 'form', 'table', 'text', 'information'
        }
        
        keywords = []
        for word in words:
            word_lower = word.lower()
            if (len(word) > 3 and 
                word_lower not in skip_words and
                (word_lower in important_words or 
                 any(important in word_lower for important in important_words))):
                keywords.append(word_lower)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        return unique_keywords

    def _humanize_name(self, name: str) -> str:
        """Convert field name to human-readable label"""
        return name.replace('_', ' ').title()

    def _infer_field_type(self, text: str, context: str = '') -> str:
        """Infer field type from text and context"""
        combined = (text + ' ' + context).lower()
        
        if '☐' in text or '□' in text or 'checkbox' in combined:
            return 'checkbox'
        elif 'date' in combined or 'birth' in combined:
            return 'date'
        elif 'email' in combined:
            return 'email'
        elif 'phone' in combined or 'telephone' in combined:
            return 'text'
        elif any(word in combined for word in ['explain', 'describe', 'details', 'facts']):
            return 'area'
        else:
            return 'text'

    def _extract_dropdown_options(self, dd_elem) -> List[str]:
        """Extract dropdown options from XML element"""
        options = []
        ns = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
        for entry in dd_elem:
            if entry.tag.endswith('listEntry'):
                val = entry.get(f'{ns}val')
                if val:
                    options.append(val)
        return options

    def save_to_json(self, output_path: str = None) -> str:
        """Save parsed fields with context to JSON"""
        if not output_path:
            output_path = f"parsed_forms/form_{self.form_number}_context_enhanced.json"
        
        output_data = {
            'form_number': self.form_number,
            'form_file': str(self.file_path),
            'total_fields': len(self.fields),
            'parsing_method': 'context_enhanced',
            'fields': [asdict(field) for field in self.fields]
        }
        
        output_path = Path(output_path)
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        logger.info(f"Saved {len(self.fields)} fields with context to {output_path}")
        return str(output_path)


def main():
    """Test the context-enhanced parser"""
    parser = ContextEnhancedParser("test_download/core_applications/form_8_-_application_general_flr-8-jun25-en.docx")
    fields = parser.parse()
    
    print(f"✅ Parsed Form 8 with context enhancement")
    print(f"📊 Found {len(fields)} fields")
    
    # Show fields with meaningful names
    meaningful_count = 0
    print(f"\n📋 Sample fields with intelligent names:")
    for field in fields[:15]:
        if not re.match(r'^(field_?\d*|table_\d+_row_\d+)$', field.field_name):
            meaningful_count += 1
            print(f"  ✨ {field.field_name} ({field.field_type}) - {field.field_label}")
            if field.surrounding_text:
                print(f"      Context: {field.surrounding_text[:60]}...")
        else:
            print(f"  ⚠️ {field.field_name} ({field.field_type}) - needs more context")
    
    print(f"\n🎯 {meaningful_count}/{len(fields)} fields have meaningful names")
    
    # Save results
    output_path = parser.save_to_json()
    print(f"💾 Saved to {output_path}")


if __name__ == "__main__":
    main()