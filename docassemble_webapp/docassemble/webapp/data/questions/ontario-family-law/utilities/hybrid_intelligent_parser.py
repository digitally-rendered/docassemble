#!/usr/bin/env python3
"""
Hybrid Intelligent Parser
Combines the improved parser's field detection with intelligent naming
Fixes the nonsense field names like 'field_0', 'field_2' etc.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from improved_form_parser import ImprovedFormParser, FormField
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HybridIntelligentParser(ImprovedFormParser):
    """Parser that uses improved detection with intelligent naming"""
    
    def __init__(self, file_path: str):
        super().__init__(file_path)
        
        # Ontario-specific intelligent naming patterns
        self.intelligent_patterns = {
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
                r'divorce': 'claim_divorce',
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
        
        # Common field patterns that help with generic identification
        self.common_patterns = {
            r'full.*legal.*name|legal.*name': 'full_legal_name',
            r'first.*name': 'first_name',
            r'last.*name|surname': 'last_name',
            r'middle.*name': 'middle_name',
            r'date.*of.*birth|birth.*date|birthdate': 'birth_date',
            r'street.*address|address.*line': 'street_address',
            r'city(?:\s|$)': 'city',
            r'province(?:\s|$)': 'province',
            r'postal.*code|zip.*code': 'postal_code',
            r'phone.*number|telephone': 'phone_number',
            r'email.*address|email': 'email_address',
            r'court.*file.*number|file.*number': 'court_file_number',
            r'occupation(?:\s|$)': 'occupation',
            r'marriage.*date': 'marriage_date',
            r'separation.*date': 'separation_date',
            r'age(?:\s|$)': 'age',
            r'(?:yes|no).*checkbox|checkbox': 'checkbox_field',
        }

    def parse(self) -> List[FormField]:
        """Parse with improved detection and intelligent naming"""
        logger.info(f"Parsing {self.file_path.name} with hybrid intelligent approach...")
        
        # Use parent class to detect all fields
        fields = super().parse()
        
        # Apply intelligent naming to improve field names
        improved_fields = []
        name_counter = {}
        
        for field in fields:
            original_name = field.field_name
            
            # Only improve nonsense names like field_0, field_1, etc.
            if self._is_nonsense_name(original_name):
                # Try to create intelligent name from context
                intelligent_name = self._create_intelligent_name(field)
                
                # Ensure uniqueness
                intelligent_name = self._ensure_unique_name(intelligent_name, name_counter)
                
                # Update field with new name
                field.field_name = intelligent_name
                field.field_id = field.field_id.replace(original_name, intelligent_name)
                field.field_label = self._create_human_label(intelligent_name, field)
                
                logger.debug(f"Improved: {original_name} -> {intelligent_name}")
            
            improved_fields.append(field)
        
        logger.info(f"Improved {len([f for f in fields if self._is_nonsense_name(f.field_name)])} field names")
        return improved_fields
    
    def _is_nonsense_name(self, name: str) -> bool:
        """Check if field name is nonsense like field_0, field_1, etc."""
        return bool(re.match(r'^field_?\d*$', name.lower()))
    
    def _create_intelligent_name(self, field: FormField) -> str:
        """Create intelligent name from field context"""
        
        # Collect all available text for analysis
        context_text = ' '.join([
            field.field_context or '',
            field.field_label or '',
            field.help_text or '',
            field.table_name or '',
        ]).lower()
        
        # Try Ontario-specific patterns first
        for category, patterns in self.intelligent_patterns.items():
            for pattern, intelligent_name in patterns.items():
                if re.search(pattern, context_text, re.IGNORECASE):
                    return intelligent_name
        
        # Try common patterns
        for pattern, intelligent_name in self.common_patterns.items():
            if re.search(pattern, context_text, re.IGNORECASE):
                return intelligent_name
        
        # Try to extract meaningful words from context
        generated_name = self._generate_name_from_context(context_text)
        if generated_name and generated_name != 'field':
            return generated_name
        
        # Last resort: use field type and position
        if field.table_name:
            return f"table_{field.table_row}_{field.field_type}_field"
        else:
            return f"{field.field_type}_field"
    
    def _generate_name_from_context(self, context: str) -> str:
        """Generate field name from context text"""
        if not context:
            return ''
        
        # Clean the text
        context = re.sub(r'[^\w\s]', ' ', context)
        context = re.sub(r'\s+', ' ', context).strip()
        
        # Look for key phrases
        key_phrases = [
            'full legal name', 'first name', 'last name', 'middle name',
            'street address', 'city', 'province', 'postal code',
            'phone number', 'email address', 'birth date', 'age',
            'court file number', 'court name', 'marriage date',
            'separation date', 'child name', 'occupation'
        ]
        
        for phrase in key_phrases:
            if phrase in context:
                return self._sanitize_field_name(phrase)
        
        # Extract meaningful words (skip common words)
        words = context.split()
        meaningful_words = []
        skip_words = {'the', 'and', 'for', 'with', 'this', 'that', 'your', 
                     'please', 'enter', 'provide', 'field', 'form', 'table'}
        
        for word in words:
            if len(word) > 3 and word.lower() not in skip_words:
                meaningful_words.append(word)
        
        if meaningful_words:
            # Take first 2-3 meaningful words
            name_parts = meaningful_words[:3]
            return self._sanitize_field_name(' '.join(name_parts))
        
        return ''
    
    def _ensure_unique_name(self, name: str, name_counter: Dict[str, int]) -> str:
        """Ensure field name is unique"""
        if not name:
            name = 'form_field'
        
        original_name = name
        if name in name_counter:
            name_counter[name] += 1
            name = f"{original_name}_{name_counter[name]}"
        else:
            name_counter[name] = 1
        
        return name
    
    def _create_human_label(self, field_name: str, field: FormField) -> str:
        """Create human-readable label from field name"""
        
        # If field has help text or existing context, prefer that
        if field.help_text and len(field.help_text) < 100:
            return field.help_text
        
        # Convert field name to human readable
        label = field_name.replace('_', ' ').title()
        
        # Handle specific cases
        label = re.sub(r'\bLso\b', 'LSO', label)
        label = re.sub(r'\bEmail\b', 'Email Address', label) 
        label = re.sub(r'\bPhone\b', 'Phone Number', label)
        label = re.sub(r'\bDate\b', 'Date', label)
        
        return label


def main():
    """Test the hybrid intelligent parser"""
    parser = HybridIntelligentParser("test_download/core_applications/form_8_-_application_general_flr-8-jun25-en.docx")
    fields = parser.parse()
    
    print(f"✅ Parsed Form 8 with hybrid intelligent approach")
    print(f"📊 Found {len(fields)} fields")
    
    # Count improvements
    original_parser = ImprovedFormParser("test_download/core_applications/form_8_-_application_general_flr-8-jun25-en.docx")
    original_fields = original_parser.parse()
    
    nonsense_count = len([f for f in original_fields if re.match(r'^field_?\d*$', f.field_name.lower())])
    print(f"🔧 Improved {nonsense_count} nonsense field names")
    
    # Show comparison
    print("\n📋 Field Name Improvements (first 10):")
    for i, (orig, improved) in enumerate(zip(original_fields[:10], fields[:10])):
        if orig.field_name != improved.field_name:
            print(f"  ✨ {orig.field_name} → {improved.field_name}")
        else:
            print(f"  ✓ {orig.field_name} (already good)")
    
    # Save results
    output_data = {
        'form_number': parser.form_number,
        'form_file': str(parser.file_path),
        'total_fields': len(fields),
        'improvements': nonsense_count,
        'parsing_method': 'hybrid_intelligent',
        'fields': [
            {
                'field_id': field.field_id,
                'field_name': field.field_name,
                'field_type': field.field_type,
                'field_label': field.field_label,
                'field_context': field.field_context,
                'help_text': field.help_text,
                'options': field.options,
                'required': field.required,
                'table_name': field.table_name,
                'table_row': field.table_row,
                'section': field.section
            }
            for field in fields
        ]
    }
    
    output_path = Path("parsed_forms/form_8_hybrid_intelligent.json")
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"💾 Saved to {output_path}")


if __name__ == "__main__":
    main()