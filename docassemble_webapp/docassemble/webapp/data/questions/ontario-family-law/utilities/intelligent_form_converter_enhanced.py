#!/usr/bin/env python3
"""
Intelligent Form Converter Enhanced - Generates Docassemble interviews from improved parsed forms
Uses enhanced field analysis (3,373 fields) and shared module architecture
"""

import json
import os
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

class IntelligentFormConverterEnhanced:
    def __init__(self, parsed_forms_dir: str, output_dir: str):
        self.parsed_forms_dir = Path(parsed_forms_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load shared modules specification
        spec_path = Path(__file__).parent / 'shared_modules_specification.json'
        with open(spec_path, 'r') as f:
            self.shared_spec = json.load(f)
        
        # Load enhanced common fields
        self.common_fields = self._load_common_fields()
        
    def _load_common_fields(self) -> Dict[str, Any]:
        """Load the enhanced common fields mapping"""
        return self.shared_spec.get('common_fields_mapping', {})
    
    def generate_interview(self, form_number: str) -> str:
        """Generate a complete Docassemble interview for a form"""
        # Load the improved parsed form data
        parsed_file = self.parsed_forms_dir / f"form_{form_number}_improved.json"
        if not parsed_file.exists():
            raise FileNotFoundError(f"Parsed form data not found: {parsed_file}")
        
        with open(parsed_file, 'r') as f:
            form_data = json.load(f)
        
        # Build the interview structure
        interview = []
        
        # Add metadata block
        interview.append(self._generate_metadata(form_number, form_data))
        
        # Add imports for shared modules
        interview.append(self._generate_imports(form_number))
        
        # Add objects initialization
        interview.append(self._generate_objects(form_number))
        
        # Add validation functions
        interview.append(self._generate_validation_code())
        
        # Add mandatory block
        interview.append(self._generate_mandatory_block(form_number))
        
        # Add question blocks
        questions = self._generate_questions(form_number, form_data)
        interview.extend(questions)
        
        # Add review screen
        interview.append(self._generate_review_screen(form_number))
        
        # Add document generation
        interview.append(self._generate_document_block(form_number))
        
        # Convert to YAML
        yaml_content = self._convert_to_yaml(interview)
        
        # Save the interview
        output_file = self.output_dir / f"form_{form_number}_interview_enhanced.yml"
        with open(output_file, 'w') as f:
            f.write(yaml_content)
        
        return str(output_file)
    
    def _generate_metadata(self, form_number: str, form_data: Dict) -> Dict:
        """Generate metadata block"""
        form_title = form_data.get('form_title', f'Form {form_number}')
        return {
            'metadata': {
                'title': f"Ontario Family Law {form_title}",
                'short_title': f"Form {form_number}",
                'description': f"Docassemble interview for Ontario Family Law Form {form_number}",
                'authors': ['Ontario Family Law System'],
                'revision_date': datetime.now().strftime('%Y-%m-%d'),
                'form_number': form_number,
                'field_count': form_data.get('total_fields', 0),
                'generated_from': 'improved_parsed_data',
                'tags': ['ontario', 'family law', f'form {form_number}']
            }
        }
    
    def _generate_imports(self, form_number: str) -> Dict:
        """Generate imports for shared modules"""
        # Get the modules needed for this form
        form_spec = self.shared_spec.get('form_specific_fields', {}).get(f'form_{form_number}', {})
        modules = form_spec.get('shared_modules_used', [
            'ontario_common_fields',
            'ontario_party_objects'
        ])
        
        imports = {
            'include': [
                'docassemble.base:data/questions/basic-questions.yml'
            ],
            'modules': []
        }
        
        # Add shared module imports
        for module in modules:
            imports['modules'].append(f'.{module}')
        
        # Add validation module
        imports['modules'].append('.ontario_validation_functions')
        
        return imports
    
    def _generate_objects(self, form_number: str) -> Dict:
        """Generate objects initialization"""
        objects = {
            'objects': [
                'applicant: Individual',
                'respondent: Individual',
                'court: Organization'
            ]
        }
        
        # Add children objects if needed
        if form_number in ['8', '10', '13', '13A', '15', '17A', '25', '26', '28', '36']:
            objects['objects'].append('children: DAList.using(object_type=Individual, there_are_any=False)')
        
        # Add lawyer objects conditionally
        objects['objects from code'] = [
            'applicant.lawyer: Individual if applicant.has_lawyer else None',
            'respondent.lawyer: Individual if respondent.has_lawyer else None'
        ]
        
        return objects
    
    def _generate_validation_code(self) -> Dict:
        """Generate validation code block"""
        return {
            'code': """
# Ontario-specific validation functions
def validate_ontario_postal_code(postal_code):
    if not postal_code:
        return True
    postal_clean = re.sub(r'\\s+', '', postal_code.upper())
    pattern = r'^[A-Z][0-9][A-Z][0-9][A-Z][0-9]$'
    if not re.match(pattern, postal_clean):
        return False
    ontario_first_letters = 'KLMNP'
    return postal_clean[0] in ontario_first_letters

def validate_ontario_court_file(file_number):
    if not file_number:
        return True
    patterns = [
        r'^(FS|FC|FD|FM|FE)-[0-9]{2}-[0-9]{5,6}$',
        r'^[0-9]{2}-[0-9]{5,6}$',
        r'^[A-Z]{2}-[0-9]{2}-[0-9]{5,6}$'
    ]
    file_upper = file_number.upper().strip()
    return any(re.match(pattern, file_upper) for pattern in patterns)

def validate_canadian_phone(phone_number):
    if not phone_number:
        return True
    digits_only = re.sub(r'\\D', '', phone_number)
    if len(digits_only) == 10:
        return True
    elif len(digits_only) == 11 and digits_only[0] == '1':
        return True
    return False
"""
        }
    
    def _generate_mandatory_block(self, form_number: str) -> Dict:
        """Generate mandatory question flow"""
        return {
            'mandatory': True,
            'question': f"Form {form_number} Interview Complete",
            'subquestion': """
Your form has been completed and is ready for download.

**Next Steps:**
1. Review your information below
2. Download the completed form
3. Print and sign the form
4. File with the court

${ form_download }
""",
            'buttons': [
                {'Exit': 'exit'},
                {'Restart': 'restart'}
            ]
        }
    
    def _generate_questions(self, form_number: str, form_data: Dict) -> List[Dict]:
        """Generate question blocks from parsed fields"""
        questions = []
        fields = form_data.get('fields', [])
        
        # Group fields by section/page
        field_groups = self._group_fields(fields)
        
        for group_name, group_fields in field_groups.items():
            question = self._create_question_block(group_name, group_fields, form_number)
            if question:
                questions.append(question)
        
        return questions
    
    def _group_fields(self, fields: List[Dict]) -> Dict[str, List[Dict]]:
        """Group fields by logical sections"""
        groups = {
            'court_info': [],
            'party_info': [],
            'children_info': [],
            'claims': [],
            'financial': [],
            'other': []
        }
        
        for field in fields:
            field_name = field.get('field_name', '').lower()
            field_label = field.get('field_label', '').lower()
            
            if 'court' in field_name or 'court' in field_label:
                groups['court_info'].append(field)
            elif any(term in field_name or term in field_label for term in ['applicant', 'respondent', 'party', 'name', 'address']):
                groups['party_info'].append(field)
            elif any(term in field_name or term in field_label for term in ['child', 'children', 'custody']):
                groups['children_info'].append(field)
            elif any(term in field_name or term in field_label for term in ['claim', 'relief', 'order']):
                groups['claims'].append(field)
            elif any(term in field_name or term in field_label for term in ['income', 'expense', 'asset', 'debt', 'support']):
                groups['financial'].append(field)
            else:
                groups['other'].append(field)
        
        # Remove empty groups
        return {k: v for k, v in groups.items() if v}
    
    def _create_question_block(self, group_name: str, fields: List[Dict], form_number: str) -> Optional[Dict]:
        """Create a question block for a group of fields"""
        if not fields:
            return None
        
        # Check if these fields are already in common modules
        docassemble_fields = []
        for field in fields:
            if not self._is_common_field(field):
                da_field = self._convert_field_to_docassemble(field, form_number)
                if da_field:
                    docassemble_fields.append(da_field)
        
        if not docassemble_fields:
            return None
        
        question_titles = {
            'court_info': 'Court Information',
            'party_info': 'Party Information',
            'children_info': 'Children Information',
            'claims': 'Claims and Relief Sought',
            'financial': 'Financial Information',
            'other': 'Additional Information'
        }
        
        return {
            'question': question_titles.get(group_name, 'Information'),
            'fields': docassemble_fields
        }
    
    def _is_common_field(self, field: Dict) -> bool:
        """Check if field is already defined in common modules"""
        field_name = field.get('field_name', '').lower()
        field_label = field.get('field_label', '').lower()
        
        # Check against common field patterns
        common_patterns = [
            'court_file_number', 'court_name', 'municipality',
            'applicant_name', 'respondent_name',
            'applicant_address', 'respondent_address',
            'signature_date', 'commissioner'
        ]
        
        return any(pattern in field_name or pattern in field_label for pattern in common_patterns)
    
    def _convert_field_to_docassemble(self, field: Dict, form_number: str) -> Optional[Dict]:
        """Convert a parsed field to Docassemble format"""
        field_type = field.get('field_type', 'text')
        field_label = field.get('field_label', field.get('field_name', 'Field'))
        field_name = self._generate_variable_name(field, form_number)
        
        da_field = {field_label: field_name}
        
        # Set datatype based on field type
        if field_type == 'date':
            da_field['datatype'] = 'date'
        elif field_type == 'email':
            da_field['datatype'] = 'email'
        elif field_type == 'number':
            da_field['datatype'] = 'number'
        elif field_type == 'currency':
            da_field['datatype'] = 'currency'
        elif field_type == 'checkbox':
            da_field['datatype'] = 'yesno'
        elif field_type == 'dropdown':
            da_field['datatype'] = 'radio'
            if field.get('options'):
                da_field['choices'] = field['options']
        elif field_type == 'area':
            da_field['datatype'] = 'area'
            da_field['rows'] = 4
        
        # Add required flag
        if field.get('required'):
            da_field['required'] = True
        
        # Add help text
        if field.get('help_text'):
            da_field['help'] = field['help_text']
        
        return da_field
    
    def _generate_variable_name(self, field: Dict, form_number: str) -> str:
        """Generate a proper variable name for a field"""
        field_name = field.get('field_name', '')
        field_label = field.get('field_label', '')
        
        # Clean and convert to snake_case
        if field_name and not field_name.startswith('field_'):
            base_name = field_name
        else:
            base_name = field_label
        
        # Convert to snake_case
        base_name = re.sub(r'[^a-zA-Z0-9]+', '_', base_name.lower())
        base_name = re.sub(r'^_+|_+$', '', base_name)
        
        # Add form prefix if not a common field
        if not base_name.startswith(('applicant', 'respondent', 'court', 'child')):
            base_name = f"form{form_number}_{base_name}"
        
        return base_name
    
    def _generate_review_screen(self, form_number: str) -> Dict:
        """Generate review screen"""
        return {
            'review': {
                'question': f"Review Form {form_number}",
                'subquestion': "Please review your information before submitting.",
                'review': [
                    {'label': 'Court Information', 'fields': ['court.court_type', 'court.file_number']},
                    {'label': 'Applicant', 'fields': ['applicant.name.full()', 'applicant.address.block()']},
                    {'label': 'Respondent', 'fields': ['respondent.name.full()', 'respondent.address.block()']}
                ]
            }
        }
    
    def _generate_document_block(self, form_number: str) -> Dict:
        """Generate document assembly block"""
        return {
            'attachment': {
                'name': f"Form {form_number}",
                'filename': f"form_{form_number}_completed",
                'variable_name': 'form_download',
                'content': f"[Your completed Form {form_number} content will be generated here]"
            }
        }
    
    def _convert_to_yaml(self, interview: List[Dict]) -> str:
        """Convert interview structure to YAML format"""
        yaml_parts = []
        
        for block in interview:
            # Convert each block to YAML
            yaml_text = yaml.dump(block, default_flow_style=False, sort_keys=False)
            yaml_parts.append(yaml_text)
        
        # Join with separator
        return '---\n'.join(yaml_parts)
    
    def generate_all_forms(self) -> Dict[str, str]:
        """Generate interviews for all available forms"""
        results = {}
        
        # Get all improved parsed files
        for parsed_file in self.parsed_forms_dir.glob('form_*_improved.json'):
            # Extract form number
            match = re.search(r'form_([^_]+)_improved\.json', parsed_file.name)
            if match:
                form_number = match.group(1)
                try:
                    output_file = self.generate_interview(form_number)
                    results[form_number] = output_file
                    print(f"Generated interview for Form {form_number}: {output_file}")
                except Exception as e:
                    print(f"Error generating Form {form_number}: {e}")
                    results[form_number] = f"Error: {e}"
        
        return results

def main():
    converter = IntelligentFormConverterEnhanced(
        parsed_forms_dir='/Users/draw/development/docassemble/docassemble_webapp/docassemble/webapp/data/questions/ontario-family-law/utilities/parsed_forms',
        output_dir='/Users/draw/development/docassemble/docassemble_webapp/docassemble/webapp/data/questions/ontario-family-law/utilities/generated_interviews_enhanced'
    )
    
    # Generate specific forms first
    priority_forms = ['8', '10', '13', '13A', '15', '36']
    
    for form_number in priority_forms:
        try:
            output = converter.generate_interview(form_number)
            print(f"Successfully generated Form {form_number}: {output}")
        except Exception as e:
            print(f"Failed to generate Form {form_number}: {e}")
    
    print("\nGeneration complete!")

if __name__ == '__main__':
    main()