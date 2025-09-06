#!/usr/bin/env python3
"""
Form Key Consistency Manager

Maintains consistent field keys across all pipeline steps:
1. Parsed form data -> Consistent form keys
2. Form keys -> Domain concepts  
3. Domain concepts -> Docassemble variables
4. Docassemble variables -> Document template fields

This ensures that document templating and field mapping is predictable and maintainable.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class FormFieldKey:
    """Represents a consistent field key with its transformations"""
    original_field_name: str
    consistent_key: str
    normalized_key: str  # snake_case version
    camel_case_key: str  # camelCase version
    human_readable: str  # Human readable version
    field_type: str
    domain_concept: Optional[str] = None
    docassemble_variable: Optional[str] = None
    template_field: Optional[str] = None
    form_numbers: List[str] = None

    def __post_init__(self):
        if self.form_numbers is None:
            self.form_numbers = []

@dataclass
class FormKeyRegistry:
    """Registry of all form keys and their mappings"""
    creation_date: str
    total_forms: int
    total_fields: int
    field_keys: Dict[str, FormFieldKey]
    form_specific_keys: Dict[str, List[str]]  # form_number -> list of keys
    cross_form_keys: List[str]  # keys that appear in multiple forms
    
class FormKeyConsistencyManager:
    """Manages consistent field keys across the entire pipeline"""
    
    def __init__(self):
        self.registry = FormKeyRegistry(
            creation_date=datetime.now().isoformat(),
            total_forms=0,
            total_fields=0,
            field_keys={},
            form_specific_keys={},
            cross_form_keys=[]
        )
        
        # Standard field patterns for consistency
        self.standard_patterns = self._load_standard_patterns()
        
    def _load_standard_patterns(self) -> Dict[str, Dict[str, str]]:
        """Load standard field patterns for consistent naming"""
        return {
            # Party Information Patterns
            'party_names': {
                'applicant_name': 'applicant_full_legal_name',
                'applicant_first_name': 'applicant_first_name', 
                'applicant_last_name': 'applicant_last_name',
                'applicant_middle_name': 'applicant_middle_name',
                'petitioner_name': 'applicant_full_legal_name',  # Legacy mapping
                'respondent_name': 'respondent_full_legal_name',
                'respondent_first_name': 'respondent_first_name',
                'respondent_last_name': 'respondent_last_name',
                'respondent_middle_name': 'respondent_middle_name'
            },
            
            # Address Patterns
            'addresses': {
                'applicant_address': 'applicant_street_address',
                'applicant_street': 'applicant_street_address',
                'applicant_city': 'applicant_city',
                'applicant_province': 'applicant_province',
                'applicant_postal_code': 'applicant_postal_code',
                'respondent_address': 'respondent_street_address',
                'respondent_street': 'respondent_street_address',
                'respondent_city': 'respondent_city',
                'respondent_province': 'respondent_province',
                'respondent_postal_code': 'respondent_postal_code'
            },
            
            # Contact Information
            'contact': {
                'applicant_phone': 'applicant_phone_number',
                'applicant_telephone': 'applicant_phone_number',
                'applicant_email': 'applicant_email_address',
                'respondent_phone': 'respondent_phone_number',
                'respondent_telephone': 'respondent_phone_number',
                'respondent_email': 'respondent_email_address'
            },
            
            # Court Information
            'court': {
                'court_file_no': 'court_file_number',
                'court_file_number': 'court_file_number',
                'court_name': 'court_name',
                'court_location': 'court_location_address'
            },
            
            # Financial Information
            'financial': {
                'income': 'annual_gross_income',
                'gross_income': 'annual_gross_income',
                'net_income': 'annual_net_income',
                'monthly_income': 'monthly_gross_income',
                'assets': 'total_asset_value',
                'liabilities': 'total_liability_value'
            },
            
            # Children Information
            'children': {
                'child_name': 'child_full_legal_name',
                'child_first_name': 'child_first_name',
                'child_last_name': 'child_last_name',
                'child_birthdate': 'child_birth_date',
                'child_age': 'child_current_age'
            },
            
            # Marriage/Relationship
            'relationship': {
                'marriage_date': 'marriage_date',
                'separation_date': 'separation_date',
                'relationship_start': 'relationship_start_date',
                'cohabitation_start': 'cohabitation_start_date'
            },
            
            # Claims and Relief
            'claims': {
                'claim_property': 'claims_property_division',
                'claim_support': 'claims_spousal_support',
                'claim_custody': 'claims_child_custody',
                'claim_access': 'claims_child_access'
            }
        }
    
    def process_parsed_forms(self, parsed_forms_dir: Path) -> 'FormKeyRegistry':
        """Process all parsed forms and create consistent key registry"""
        
        parsed_files = list(parsed_forms_dir.glob('form_*_improved.json'))
        self.registry.total_forms = len(parsed_files)
        
        all_field_occurrences = {}  # Track how many forms each field appears in
        
        for parsed_file in parsed_files:
            form_number = self._extract_form_number(parsed_file.stem)
            
            with open(parsed_file, 'r') as f:
                form_data = json.load(f)
            
            form_fields = form_data.get('fields', [])
            form_keys = []
            
            for field_data in form_fields:
                original_name = field_data.get('field_name', '')
                if not original_name:
                    continue
                
                # Generate consistent key
                consistent_key = self._generate_consistent_key(original_name)
                
                # Track field occurrence across forms
                if consistent_key not in all_field_occurrences:
                    all_field_occurrences[consistent_key] = set()
                all_field_occurrences[consistent_key].add(form_number)
                
                # Create or update field key record
                if consistent_key not in self.registry.field_keys:
                    field_key = FormFieldKey(
                        original_field_name=original_name,
                        consistent_key=consistent_key,
                        normalized_key=self._to_snake_case(consistent_key),
                        camel_case_key=self._to_camel_case(consistent_key),
                        human_readable=self._to_human_readable(consistent_key),
                        field_type=field_data.get('field_type', 'text'),
                        form_numbers=[form_number]
                    )
                    self.registry.field_keys[consistent_key] = field_key
                else:
                    # Add form number if not already present
                    if form_number not in self.registry.field_keys[consistent_key].form_numbers:
                        self.registry.field_keys[consistent_key].form_numbers.append(form_number)
                
                form_keys.append(consistent_key)
            
            self.registry.form_specific_keys[form_number] = form_keys
        
        # Identify cross-form fields
        self.registry.cross_form_keys = [
            key for key, forms in all_field_occurrences.items() 
            if len(forms) > 1
        ]
        
        self.registry.total_fields = len(self.registry.field_keys)
        
        return self.registry
    
    def _generate_consistent_key(self, original_field_name: str) -> str:
        """Generate consistent key using standard patterns"""
        
        # Normalize the field name
        normalized = original_field_name.lower().strip()
        
        # Check against standard patterns
        for category, patterns in self.standard_patterns.items():
            for pattern, consistent_key in patterns.items():
                if self._field_matches_pattern(normalized, pattern):
                    return consistent_key
        
        # If no pattern match, create consistent version
        return self._create_consistent_field_name(original_field_name)
    
    def _field_matches_pattern(self, field_name: str, pattern: str) -> bool:
        """Check if field name matches a pattern"""
        
        # Exact match
        if field_name == pattern.lower():
            return True
        
        # Fuzzy match for common variations
        field_parts = set(re.split(r'[_\s\-]', field_name.lower()))
        pattern_parts = set(re.split(r'[_\s\-]', pattern.lower()))
        
        # High overlap indicates match
        overlap = len(field_parts & pattern_parts)
        total_parts = len(field_parts | pattern_parts)
        
        if total_parts > 0 and overlap / total_parts > 0.6:
            return True
        
        return False
    
    def _create_consistent_field_name(self, field_name: str) -> str:
        """Create consistent field name from original"""
        
        # Clean and normalize
        clean_name = re.sub(r'[^\w\s]', ' ', field_name)
        clean_name = re.sub(r'\s+', '_', clean_name)
        clean_name = clean_name.lower().strip('_')
        
        # Apply consistency rules
        consistency_rules = {
            # Standardize common terms
            'addr': 'address',
            'tel': 'phone',
            'telephone': 'phone',
            'ph': 'phone',
            'dob': 'birth_date',
            'birthdate': 'birth_date',
            'email_addr': 'email_address',
            'postal': 'postal_code',
            'zip': 'postal_code',
            
            # Standardize party references
            'petitioner': 'applicant',
            'plaintiff': 'applicant',
            'defendant': 'respondent',
            
            # Standardize field types
            'checkbox': 'check',
            'textbox': 'text',
            'dropdown': 'select'
        }
        
        for old_term, new_term in consistency_rules.items():
            clean_name = re.sub(f'\\b{old_term}\\b', new_term, clean_name)
        
        return clean_name
    
    def _to_snake_case(self, text: str) -> str:
        """Convert to snake_case"""
        return re.sub(r'[A-Z]', r'_\g<0>', text).lower().strip('_')
    
    def _to_camel_case(self, text: str) -> str:
        """Convert to camelCase"""
        parts = text.split('_')
        return parts[0].lower() + ''.join(part.capitalize() for part in parts[1:])
    
    def _to_human_readable(self, text: str) -> str:
        """Convert to human readable format"""
        return text.replace('_', ' ').title()
    
    def _extract_form_number(self, filename: str) -> str:
        """Extract form number from filename"""
        match = re.search(r'form_([^_]+)', filename)
        return match.group(1) if match else 'unknown'
    
    def apply_domain_mapping(self, domain_mappings: Dict[str, str]) -> None:
        """Apply domain concept mapping to field keys"""
        for consistent_key, field_key in self.registry.field_keys.items():
            if consistent_key in domain_mappings:
                field_key.domain_concept = domain_mappings[consistent_key]
    
    def apply_docassemble_mapping(self, da_mappings: Dict[str, str]) -> None:
        """Apply Docassemble variable mapping to field keys"""
        for consistent_key, field_key in self.registry.field_keys.items():
            if field_key.domain_concept and field_key.domain_concept in da_mappings:
                field_key.docassemble_variable = da_mappings[field_key.domain_concept]
    
    def apply_template_mapping(self, template_mappings: Dict[str, str]) -> None:
        """Apply document template field mapping to field keys"""
        for consistent_key, field_key in self.registry.field_keys.items():
            if consistent_key in template_mappings:
                field_key.template_field = template_mappings[consistent_key]
    
    def get_mapping_for_form(self, form_number: str) -> Dict[str, FormFieldKey]:
        """Get field mapping for specific form"""
        form_keys = self.registry.form_specific_keys.get(form_number, [])
        return {key: self.registry.field_keys[key] for key in form_keys}
    
    def get_cross_form_mappings(self) -> Dict[str, FormFieldKey]:
        """Get mappings for fields that appear across multiple forms"""
        return {key: self.registry.field_keys[key] for key in self.registry.cross_form_keys}
    
    def save_registry(self, output_path: Path) -> None:
        """Save the registry to JSON file"""
        registry_data = {
            'metadata': {
                'creation_date': self.registry.creation_date,
                'total_forms': self.registry.total_forms,
                'total_fields': self.registry.total_fields,
                'cross_form_fields': len(self.registry.cross_form_keys)
            },
            'field_keys': {
                key: asdict(field_key) for key, field_key in self.registry.field_keys.items()
            },
            'form_specific_keys': self.registry.form_specific_keys,
            'cross_form_keys': self.registry.cross_form_keys
        }
        
        with open(output_path, 'w') as f:
            json.dump(registry_data, f, indent=2)
        
        print(f"✅ Saved form key registry to {output_path}")
        print(f"   📊 {self.registry.total_forms} forms, {self.registry.total_fields} fields")
        print(f"   🔗 {len(self.registry.cross_form_keys)} cross-form fields")
    
    def load_registry(self, registry_path: Path) -> None:
        """Load registry from JSON file"""
        with open(registry_path, 'r') as f:
            registry_data = json.load(f)
        
        # Reconstruct field keys
        field_keys = {}
        for key, field_data in registry_data['field_keys'].items():
            field_keys[key] = FormFieldKey(**field_data)
        
        self.registry = FormKeyRegistry(
            creation_date=registry_data['metadata']['creation_date'],
            total_forms=registry_data['metadata']['total_forms'],
            total_fields=registry_data['metadata']['total_fields'],
            field_keys=field_keys,
            form_specific_keys=registry_data['form_specific_keys'],
            cross_form_keys=registry_data['cross_form_keys']
        )
    
    def generate_consistency_report(self) -> str:
        """Generate a report on field consistency"""
        report_lines = [
            "# Form Key Consistency Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            f"- **Total Forms**: {self.registry.total_forms}",
            f"- **Total Fields**: {self.registry.total_fields}",
            f"- **Cross-form Fields**: {len(self.registry.cross_form_keys)}",
            "",
            "## Cross-form Fields",
            "These fields appear in multiple forms and maintain consistent keys:",
            ""
        ]
        
        for key in self.registry.cross_form_keys:
            field_key = self.registry.field_keys[key]
            forms_list = ', '.join(field_key.form_numbers)
            report_lines.append(f"- **{key}**: Forms {forms_list}")
        
        report_lines.extend([
            "",
            "## Field Key Transformations",
            "Examples of how original field names are made consistent:",
            ""
        ])
        
        # Show examples of transformations
        examples = []
        for key, field_key in list(self.registry.field_keys.items())[:10]:
            if field_key.original_field_name != key:
                examples.append(f"- `{field_key.original_field_name}` → `{key}`")
        
        report_lines.extend(examples)
        
        return '\n'.join(report_lines)


def main():
    """Run the form key consistency manager"""
    
    manager = FormKeyConsistencyManager()
    
    # Process parsed forms
    parsed_forms_dir = Path('parsed_forms')
    if not parsed_forms_dir.exists():
        print("❌ Parsed forms directory not found")
        return
    
    print("🔍 Processing parsed forms for key consistency...")
    registry = manager.process_parsed_forms(parsed_forms_dir)
    
    # Save registry
    output_path = Path('form_key_registry.json')
    manager.save_registry(output_path)
    
    # Generate and save report
    report = manager.generate_consistency_report()
    report_path = Path('form_key_consistency_report.md')
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"📝 Generated consistency report: {report_path}")


if __name__ == "__main__":
    main()