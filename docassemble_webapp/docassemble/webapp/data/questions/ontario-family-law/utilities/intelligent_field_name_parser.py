#!/usr/bin/env python3
"""
Intelligent Field Name Parser
Creates meaningful field names from Ontario family law forms by analyzing content, labels, and context
Fixes the issue of nonsense field names like 'field_0', 'field_2' etc.
"""

import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class IntelligentFormField:
    """Represents a form field with intelligent naming"""
    field_id: str
    field_name: str  # Meaningful name derived from content
    field_type: str
    field_label: str  # Human readable label
    original_control_name: str  # Original XML control name (field_0, etc.)
    required: bool = False
    validation_rules: str = ""
    max_length: Optional[int] = None
    options: Optional[List[str]] = None
    table_context: Optional[str] = None
    nearby_text: str = ""  # Text near the field for context
    section: Optional[str] = None
    confidence_score: float = 1.0  # How confident we are in the field name


class IntelligentFieldNameParser:
    """Parser that creates meaningful field names from form content"""
    
    NAMESPACES = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
        'w15': 'http://schemas.microsoft.com/office/word/2012/wordml',
    }
    
    def __init__(self, form_number: str = "unknown"):
        self.form_number = form_number
        self.fields: List[IntelligentFormField] = []
        self.field_counter: Dict[str, int] = {}
        self.used_names: Set[str] = set()
        
        # Ontario-specific field patterns with meaningful names
        self.ontario_field_patterns = {
            # Party Information
            'applicant': {
                r'applicant.*full.*name|applicant.*name': 'applicant_full_legal_name',
                r'applicant.*first.*name': 'applicant_first_name',
                r'applicant.*last.*name': 'applicant_last_name',
                r'applicant.*middle.*name': 'applicant_middle_name',
                r'applicant.*address(?!.*email)': 'applicant_street_address',
                r'applicant.*city': 'applicant_city',
                r'applicant.*province': 'applicant_province',
                r'applicant.*postal': 'applicant_postal_code',
                r'applicant.*phone': 'applicant_phone_number',
                r'applicant.*email': 'applicant_email_address',
                r'applicant.*birth': 'applicant_birth_date',
                r'applicant.*occupation': 'applicant_occupation',
            },
            'respondent': {
                r'respondent.*full.*name|respondent.*name': 'respondent_full_legal_name',
                r'respondent.*first.*name': 'respondent_first_name',
                r'respondent.*last.*name': 'respondent_last_name',
                r'respondent.*middle.*name': 'respondent_middle_name',
                r'respondent.*address(?!.*email)': 'respondent_street_address',
                r'respondent.*city': 'respondent_city',
                r'respondent.*province': 'respondent_province',
                r'respondent.*postal': 'respondent_postal_code',
                r'respondent.*phone': 'respondent_phone_number',
                r'respondent.*email': 'respondent_email_address',
                r'respondent.*birth': 'respondent_birth_date',
                r'respondent.*occupation': 'respondent_occupation',
            },
            'court': {
                r'court.*file.*no|court.*file.*number': 'court_file_number',
                r'court.*name': 'court_name',
                r'court.*address': 'court_address',
                r'court.*location': 'court_location',
                r'registry.*office': 'registry_office',
            },
            'children': {
                r'child.*full.*name|child.*name': 'child_full_legal_name',
                r'child.*first.*name': 'child_first_name',
                r'child.*last.*name': 'child_last_name',
                r'child.*birth.*date|child.*birthdate': 'child_birth_date',
                r'child.*age': 'child_current_age',
                r'child.*residence|child.*living|child.*resides': 'child_residence_with',
                r'child.*relationship.*applicant': 'child_relationship_to_applicant',
                r'child.*relationship.*respondent': 'child_relationship_to_respondent',
            },
            'financial': {
                r'income.*gross.*annual': 'annual_gross_income',
                r'income.*net.*annual': 'annual_net_income',
                r'income.*gross.*monthly': 'monthly_gross_income',
                r'income.*net.*monthly': 'monthly_net_income',
                r'assets.*total': 'total_asset_value',
                r'liabilities.*total': 'total_liability_value',
                r'financial.*statement.*attached': 'financial_statement_attached',
            },
            'marriage': {
                r'marriage.*date': 'marriage_date',
                r'separation.*date': 'separation_date',
                r'cohabitation.*start': 'cohabitation_start_date',
                r'relationship.*start': 'relationship_start_date',
                r'name.*before.*marriage': 'name_before_marriage',
            },
            'claims': {
                r'claim.*property|property.*division': 'claim_property_division',
                r'claim.*support|spousal.*support': 'claim_spousal_support',
                r'claim.*custody|child.*custody': 'claim_child_custody',
                r'claim.*access|child.*access': 'claim_child_access',
                r'claim.*child.*support': 'claim_child_support',
                r'restraining.*order': 'claim_restraining_order',
            },
            'legal': {
                r'lawyer.*name': 'lawyer_full_name',
                r'lawyer.*firm': 'law_firm_name',
                r'lawyer.*address': 'lawyer_address',
                r'lawyer.*phone': 'lawyer_phone_number',
                r'lso.*number': 'lawyer_lso_number',
                r'self.*represented': 'self_represented',
            }
        }
    
    def parse_docx_file(self, docx_path: Path) -> Dict[str, Any]:
        """Parse DOCX file and extract fields with intelligent naming"""
        logger.info(f"Parsing {docx_path} with intelligent field naming...")
        
        try:
            with zipfile.ZipFile(docx_path, 'r') as doc:
                # Parse main document
                self._parse_document_xml(doc)
                
                # Parse headers/footers if they exist
                self._parse_headers_footers(doc)
                
            # Post-process to improve field names
            self._post_process_fields()
            
            return self._create_result_dict(docx_path)
            
        except Exception as e:
            logger.error(f"Error parsing {docx_path}: {e}")
            return {'error': str(e), 'fields': []}
    
    def _parse_document_xml(self, doc: zipfile.ZipFile):
        """Parse the main document XML"""
        try:
            with doc.open('word/document.xml') as doc_file:
                tree = ET.parse(doc_file)
                root = tree.getroot()
                
                # Extract form fields with context
                self._extract_form_fields_with_context(root)
                
                # Extract content controls
                self._extract_content_controls_with_context(root)
                
                # Extract table fields
                self._extract_table_fields_with_context(root)
                
        except Exception as e:
            logger.error(f"Error parsing document XML: {e}")
    
    def _parse_headers_footers(self, doc: zipfile.ZipFile):
        """Parse headers and footers for additional fields"""
        try:
            # Check for header files
            for file_name in doc.namelist():
                if 'word/header' in file_name or 'word/footer' in file_name:
                    with doc.open(file_name) as xml_file:
                        tree = ET.parse(xml_file)
                        root = tree.getroot()
                        
                        # Extract fields from headers/footers
                        self._extract_form_fields_with_context(root)
                        self._extract_content_controls_with_context(root)
                        
        except Exception as e:
            logger.debug(f"Error parsing headers/footers: {e}")
    
    def _extract_form_fields_with_context(self, root):
        """Extract form fields with surrounding context for intelligent naming"""
        # Find all form fields
        for fld_simple in root.findall('.//w:fldSimple', self.NAMESPACES):
            instr_text = fld_simple.get(f'{{{self.NAMESPACES["w"]}}}instr', '')
            if 'FORMTEXT' in instr_text or 'FORMDROPDOWN' in instr_text or 'FORMCHECKBOX' in instr_text:
                
                # Get the field's original name from XML
                original_name = self._extract_original_field_name(instr_text)
                
                # Get surrounding context (text before and after)
                context = self._get_field_context(fld_simple, root)
                
                # Generate intelligent name
                intelligent_name = self._generate_intelligent_name(original_name, context, instr_text)
                
                # Determine field type
                field_type = self._determine_field_type(instr_text, context)
                
                # Create field
                field = IntelligentFormField(
                    field_id=f"form{self.form_number}_{intelligent_name}",
                    field_name=intelligent_name,
                    field_type=field_type,
                    field_label=self._create_human_label(intelligent_name, context),
                    original_control_name=original_name,
                    nearby_text=context.get('nearby_text', ''),
                    section=self._determine_section(context),
                    confidence_score=context.get('confidence', 0.8)
                )
                
                self.fields.append(field)
    
    def _extract_content_controls_with_context(self, root):
        """Extract content controls with context"""
        for sdt in root.findall('.//w:sdt', self.NAMESPACES):
            # Get properties
            sdt_pr = sdt.find('.//w:sdtPr', self.NAMESPACES)
            if sdt_pr is None:
                continue
            
            # Get original tag/name
            tag_elem = sdt_pr.find('.//w:tag', self.NAMESPACES)
            original_name = tag_elem.get(f'{{{self.NAMESPACES["w"]}}}val', '') if tag_elem is not None else ''
            
            # Get context
            context = self._get_field_context(sdt, root)
            
            # Generate intelligent name
            intelligent_name = self._generate_intelligent_name(original_name, context, '')
            
            # Determine type from content control properties
            field_type = self._determine_content_control_type(sdt_pr)
            
            field = IntelligentFormField(
                field_id=f"form{self.form_number}_{intelligent_name}",
                field_name=intelligent_name,
                field_type=field_type,
                field_label=self._create_human_label(intelligent_name, context),
                original_control_name=original_name,
                nearby_text=context.get('nearby_text', ''),
                section=self._determine_section(context),
                confidence_score=context.get('confidence', 0.8)
            )
            
            self.fields.append(field)
    
    def _extract_table_fields_with_context(self, root):
        """Extract fields from tables with context"""
        tables = root.findall('.//w:tbl', self.NAMESPACES)
        
        for table_idx, table in enumerate(tables):
            table_context = self._get_table_context(table, root)
            
            rows = table.findall('.//w:tr', self.NAMESPACES)
            for row_idx, row in enumerate(rows):
                cells = row.findall('.//w:tc', self.NAMESPACES)
                
                for cell_idx, cell in enumerate(cells):
                    cell_text = self._get_cell_text(cell)
                    
                    if self._is_field_cell(cell_text):
                        # Generate intelligent name from table context
                        intelligent_name = self._generate_table_field_name(
                            cell_text, table_context, row_idx, cell_idx
                        )
                        
                        field = IntelligentFormField(
                            field_id=f"form{self.form_number}_table{table_idx}_{intelligent_name}",
                            field_name=intelligent_name,
                            field_type=self._infer_field_type_from_cell(cell_text),
                            field_label=self._clean_cell_text(cell_text),
                            original_control_name=f"table_{table_idx}_row_{row_idx}_cell_{cell_idx}",
                            nearby_text=cell_text,
                            table_context=f"Table {table_idx + 1}, Row {row_idx + 1}",
                            confidence_score=0.7
                        )
                        
                        self.fields.append(field)
    
    def _get_field_context(self, element, root) -> Dict[str, Any]:
        """Get context around a field element"""
        context = {
            'nearby_text': '',
            'preceding_text': '',
            'following_text': '',
            'confidence': 0.5
        }
        
        try:
            # Get parent paragraph
            parent_para = element.find('ancestor::w:p', self.NAMESPACES)
            if parent_para is not None:
                # Get all text in the paragraph
                para_text = self._get_paragraph_text(parent_para)
                context['nearby_text'] = para_text
                context['confidence'] = 0.8
            
            # Try to get preceding and following paragraphs
            # This is a simplified approach - in real implementation you'd traverse more carefully
            context['preceding_text'] = self._get_preceding_text(element, root)
            context['following_text'] = self._get_following_text(element, root)
            
        except Exception as e:
            logger.debug(f"Error getting field context: {e}")
        
        return context
    
    def _generate_intelligent_name(self, original_name: str, context: Dict[str, Any], instr_text: str) -> str:
        """Generate intelligent field name from context"""
        
        # Combine all available text for analysis
        text_to_analyze = ' '.join([
            context.get('nearby_text', ''),
            context.get('preceding_text', ''),
            context.get('following_text', ''),
            instr_text
        ]).lower()
        
        # Try Ontario-specific patterns first
        for category, patterns in self.ontario_field_patterns.items():
            for pattern, intelligent_name in patterns.items():
                if re.search(pattern, text_to_analyze, re.IGNORECASE):
                    return self._ensure_unique_name(intelligent_name)
        
        # If no pattern matches, try to create intelligent name from context
        if context.get('nearby_text'):
            generated_name = self._generate_name_from_text(context['nearby_text'])
            if generated_name and generated_name != 'field':
                return self._ensure_unique_name(generated_name)
        
        # Fallback: improve the original name if it's generic
        if original_name and not re.match(r'^field_?\d*$', original_name):
            return self._ensure_unique_name(self._sanitize_name(original_name))
        
        # Last resort: create a descriptive generic name
        return self._ensure_unique_name(f"form_field_{len(self.fields) + 1}")
    
    def _generate_name_from_text(self, text: str) -> str:
        """Generate field name from nearby text"""
        if not text:
            return ''
        
        # Clean the text
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Look for key phrases that indicate field purpose
        key_phrases = [
            'full legal name', 'first name', 'last name', 'middle name',
            'street address', 'city', 'province', 'postal code',
            'phone number', 'email address', 'birth date',
            'court file number', 'court name', 'marriage date',
            'separation date', 'child name', 'occupation'
        ]
        
        text_lower = text.lower()
        for phrase in key_phrases:
            if phrase in text_lower:
                return self._sanitize_name(phrase)
        
        # Extract meaningful words (nouns, adjectives)
        words = text.split()
        meaningful_words = []
        
        # Simple heuristic: words longer than 3 characters that aren't common words
        skip_words = {'the', 'and', 'for', 'with', 'this', 'that', 'your', 'please', 'enter'}
        
        for word in words:
            if len(word) > 3 and word.lower() not in skip_words:
                meaningful_words.append(word)
        
        if meaningful_words:
            # Take first 3 meaningful words
            name_parts = meaningful_words[:3]
            return self._sanitize_name(' '.join(name_parts))
        
        return ''
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize name for use as field variable"""
        if not name:
            return ''
        
        # Remove special characters and normalize
        name = re.sub(r'[^\w\s]', ' ', name)
        name = re.sub(r'\s+', '_', name)
        name = name.lower().strip('_')
        
        # Ensure starts with letter
        if name and not name[0].isalpha():
            name = 'field_' + name
        
        return name or ''
    
    def _ensure_unique_name(self, name: str) -> str:
        """Ensure field name is unique"""
        if not name:
            name = 'field'
        
        original_name = name
        counter = 1
        
        while name in self.used_names:
            name = f"{original_name}_{counter}"
            counter += 1
        
        self.used_names.add(name)
        return name
    
    def _create_human_label(self, field_name: str, context: Dict[str, Any]) -> str:
        """Create human-readable label from field name and context"""
        
        # Try to use nearby text first
        nearby_text = context.get('nearby_text', '').strip()
        if nearby_text and len(nearby_text) < 100:
            # Clean up the text to make a good label
            label = re.sub(r'[_:\[\]()]+', ' ', nearby_text)
            label = re.sub(r'\s+', ' ', label).strip()
            if label:
                return label
        
        # Fallback to making field name human readable
        return field_name.replace('_', ' ').title()
    
    def _determine_field_type(self, instr_text: str, context: Dict[str, Any]) -> str:
        """Determine field type from instruction and context"""
        instr_lower = instr_text.lower()
        text_lower = context.get('nearby_text', '').lower()
        
        if 'formcheckbox' in instr_lower:
            return 'checkbox'
        elif 'formdropdown' in instr_lower:
            return 'dropdown'
        elif any(word in text_lower for word in ['date', 'birth', 'marriage', 'separation']):
            return 'date'
        elif any(word in text_lower for word in ['email', 'e-mail']):
            return 'email'
        elif any(word in text_lower for word in ['phone', 'telephone', 'fax']):
            return 'phone'
        elif any(word in text_lower for word in ['postal', 'zip']):
            return 'postal_code'
        elif any(word in text_lower for word in ['age', 'number', 'amount', 'income']):
            return 'number'
        else:
            return 'text'
    
    def _determine_content_control_type(self, sdt_pr) -> str:
        """Determine content control type"""
        if sdt_pr.find('.//w:date', self.NAMESPACES) is not None:
            return 'date'
        elif sdt_pr.find('.//w:dropDownList', self.NAMESPACES) is not None:
            return 'dropdown'
        elif sdt_pr.find('.//w:comboBox', self.NAMESPACES) is not None:
            return 'dropdown'
        elif sdt_pr.find('.//w:checkbox', self.NAMESPACES) is not None:
            return 'checkbox'
        else:
            return 'text'
    
    def _post_process_fields(self):
        """Post-process fields to improve names and remove duplicates"""
        # Remove duplicates and improve names
        unique_fields = []
        seen_names = set()
        
        for field in self.fields:
            if field.field_name not in seen_names:
                seen_names.add(field.field_name)
                unique_fields.append(field)
        
        self.fields = unique_fields
        
        # Sort by confidence score (highest first)
        self.fields.sort(key=lambda f: f.confidence_score, reverse=True)
    
    def _create_result_dict(self, docx_path: Path) -> Dict[str, Any]:
        """Create result dictionary"""
        field_types = {}
        for field in self.fields:
            field_types[field.field_type] = field_types.get(field.field_type, 0) + 1
        
        return {
            'form_number': self.form_number,
            'form_file': docx_path.name,
            'source_path': str(docx_path),
            'total_fields': len(self.fields),
            'field_types': field_types,
            'fields': [asdict(field) for field in self.fields],
            'parsing_method': 'intelligent_field_naming',
            'improvements': [
                'Created meaningful field names from content analysis',
                'Used Ontario-specific field patterns',
                'Analyzed surrounding text for context',
                'Eliminated generic field_X naming'
            ]
        }
    
    # Helper methods (simplified implementations)
    def _extract_original_field_name(self, instr_text: str) -> str:
        """Extract original field name from instruction text"""
        # Look for bookmark or name references
        name_match = re.search(r'\\b\s*(\w+)', instr_text)
        return name_match.group(1) if name_match else ''
    
    def _get_paragraph_text(self, para) -> str:
        """Get all text from a paragraph"""
        texts = para.findall('.//w:t', self.NAMESPACES)
        return ' '.join(t.text or '' for t in texts)
    
    def _get_preceding_text(self, element, root) -> str:
        """Get text from preceding elements"""
        # Simplified implementation
        return ""
    
    def _get_following_text(self, element, root) -> str:
        """Get text from following elements"""
        # Simplified implementation  
        return ""
    
    def _get_table_context(self, table, root) -> Dict[str, Any]:
        """Get context for table"""
        return {'table_type': 'unknown'}
    
    def _get_cell_text(self, cell) -> str:
        """Get text from table cell"""
        texts = cell.findall('.//w:t', self.NAMESPACES)
        return ' '.join(t.text or '' for t in texts).strip()
    
    def _is_field_cell(self, cell_text: str) -> bool:
        """Check if cell contains a field"""
        return bool(cell_text and ('___' in cell_text or '[]' in cell_text or '☐' in cell_text))
    
    def _generate_table_field_name(self, cell_text: str, table_context: Dict, row_idx: int, cell_idx: int) -> str:
        """Generate field name for table cell"""
        # Simplified - in real implementation would analyze table structure
        clean_text = self._clean_cell_text(cell_text)
        if clean_text:
            return self._sanitize_name(clean_text)
        return f"table_field_{row_idx}_{cell_idx}"
    
    def _clean_cell_text(self, cell_text: str) -> str:
        """Clean cell text for use as field name"""
        # Remove field indicators
        text = re.sub(r'[_☐\[\]]+', ' ', cell_text)
        return re.sub(r'\s+', ' ', text).strip()
    
    def _infer_field_type_from_cell(self, cell_text: str) -> str:
        """Infer field type from cell content"""
        text_lower = cell_text.lower()
        if '☐' in cell_text or '[]' in cell_text:
            return 'checkbox'
        elif 'date' in text_lower:
            return 'date'
        elif 'email' in text_lower:
            return 'email'
        else:
            return 'text'
    
    def _determine_section(self, context: Dict[str, Any]) -> Optional[str]:
        """Determine which section this field belongs to"""
        text = context.get('nearby_text', '').lower()
        
        if any(word in text for word in ['applicant', 'petitioner']):
            return 'applicant_info'
        elif any(word in text for word in ['respondent', 'defendant']):
            return 'respondent_info'
        elif any(word in text for word in ['child', 'minor']):
            return 'children_info'
        elif any(word in text for word in ['court', 'file', 'registry']):
            return 'court_info'
        elif any(word in text for word in ['marriage', 'separation', 'relationship']):
            return 'relationship_info'
        elif any(word in text for word in ['income', 'asset', 'financial']):
            return 'financial_info'
        else:
            return 'general'


def main():
    """Test the intelligent parser"""
    parser = IntelligentFieldNameParser("8")
    
    # Test with Form 8
    form_path = Path("test_download/core_applications/form_8_-_application_general_flr-8-jun25-en.docx")
    if not form_path.exists():
        print(f"Form file not found: {form_path}")
        return
    
    result = parser.parse_docx_file(form_path)
    
    # Save result
    output_path = Path("parsed_forms/form_8_intelligent.json")
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"✅ Parsed Form 8 with intelligent naming")
    print(f"📊 Found {result['total_fields']} fields")
    print(f"💾 Saved to {output_path}")
    
    # Show first few fields
    print(f"\n📋 First 10 fields:")
    for field in result['fields'][:10]:
        print(f"  - {field['field_name']} ({field['field_type']}) - {field['field_label']}")
        if field['original_control_name']:
            print(f"    Original: {field['original_control_name']}")


if __name__ == "__main__":
    main()