#!/usr/bin/env python3
"""
Simplified Unified Map-Based Generator
Generates interviews using consistent form keys, domain mapping, and map-to-YAML encoding
Uses only standard library modules
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class SimplifiedUnifiedGenerator:
    """Simplified generator using map-based approach with consistent keys"""
    
    def __init__(self):
        self.parsed_forms_dir = Path('parsed_forms')
        self.output_dir = Path('generated_interviews_unified')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load form key registry if available
        self.form_key_registry = self._load_form_key_registry()
        
    def _load_form_key_registry(self) -> Dict:
        """Load form key registry if available"""
        registry_path = Path('form_key_registry.json')
        if registry_path.exists():
            with open(registry_path, 'r') as f:
                return json.load(f)
        return {}
    
    def generate_interview_map_for_form(self, form_number: str) -> Dict[str, Any]:
        """Generate interview map for a specific form"""
        
        # Load parsed form data
        parsed_data = self._load_parsed_form_data(form_number)
        if not parsed_data:
            raise ValueError(f"No parsed data found for form {form_number}")
        
        # Apply consistent key mapping
        consistent_fields = self._apply_consistent_keys(parsed_data['fields'])
        
        # Apply domain mapping
        domain_mapped_fields = self._apply_domain_mapping(consistent_fields)
        
        # Generate interview map structure
        interview_map = self._generate_interview_map(form_number, domain_mapped_fields)
        
        return interview_map
    
    def _load_parsed_form_data(self, form_number: str) -> Optional[Dict]:
        """Load parsed form data, prioritizing enhanced labels"""
        possible_files = [
            f'form_{form_number}_fields_enhanced_labels.json',  # Priority: enhanced labels
            f'form_{form_number}_improved.json',
            f'form_{form_number}_fields_enhanced.json',
            f'form_{form_number}_fields_complete.json'
        ]
        
        for filename in possible_files:
            filepath = self.parsed_forms_dir / filename
            if filepath.exists():
                with open(filepath, 'r') as f:
                    return json.load(f)
        
        return None
    
    def _apply_consistent_keys(self, fields: List[Dict]) -> List[Dict]:
        """Apply consistent key mapping to fields"""
        consistent_fields = []
        
        for field in fields:
            original_name = field.get('field_name', '')
            consistent_key = self._get_consistent_key(original_name)
            
            # Create enhanced field with consistent key
            enhanced_field = field.copy()
            enhanced_field['consistent_key'] = consistent_key
            enhanced_field['normalized_key'] = self._to_snake_case(consistent_key)
            enhanced_field['human_readable'] = consistent_key.replace('_', ' ').title()
            
            consistent_fields.append(enhanced_field)
        
        return consistent_fields
    
    def _get_consistent_key(self, original_name: str) -> str:
        """Get consistent key for field name"""
        
        # Check form key registry first
        if self.form_key_registry and 'field_keys' in self.form_key_registry:
            for key, field_data in self.form_key_registry['field_keys'].items():
                if field_data.get('original_field_name') == original_name:
                    return key
        
        # Fallback to generating consistent key
        return self._generate_consistent_key(original_name)
    
    def _generate_consistent_key(self, field_name: str) -> str:
        """Generate consistent key from field name"""
        
        # Standard mappings for common patterns
        standard_mappings = {
            # Party patterns
            r'applicant.*name': 'applicant_full_legal_name',
            r'applicant.*first': 'applicant_first_name',
            r'applicant.*last': 'applicant_last_name',
            r'respondent.*name': 'respondent_full_legal_name',
            r'respondent.*first': 'respondent_first_name',
            r'respondent.*last': 'respondent_last_name',
            
            # Address patterns
            r'applicant.*address': 'applicant_street_address',
            r'applicant.*city': 'applicant_city',
            r'applicant.*postal': 'applicant_postal_code',
            r'respondent.*address': 'respondent_street_address',
            r'respondent.*city': 'respondent_city',
            r'respondent.*postal': 'respondent_postal_code',
            
            # Contact patterns
            r'applicant.*phone': 'applicant_phone_number',
            r'applicant.*email': 'applicant_email_address',
            r'respondent.*phone': 'respondent_phone_number',
            r'respondent.*email': 'respondent_email_address',
            
            # Court patterns
            r'court.*file': 'court_file_number',
            r'court.*name': 'court_name',
            
            # Children patterns
            r'child.*name': 'child_full_legal_name',
            r'child.*birth': 'child_birth_date',
            r'child.*age': 'child_current_age',
        }
        
        field_lower = field_name.lower()
        
        # Try standard mappings
        for pattern, consistent_name in standard_mappings.items():
            if re.search(pattern, field_lower):
                return consistent_name
        
        # Generate from field name
        clean_name = re.sub(r'[^\w\s]', ' ', field_name)
        clean_name = re.sub(r'\s+', '_', clean_name)
        clean_name = clean_name.lower().strip('_')
        
        return clean_name
    
    def _apply_domain_mapping(self, consistent_fields: List[Dict]) -> List[Dict]:
        """Apply domain mapping to consistent fields"""
        
        domain_mappings = {
            # Party domain
            'applicant_full_legal_name': 'party.applicant.name',
            'applicant_first_name': 'party.applicant.name.first',
            'applicant_last_name': 'party.applicant.name.last',
            'applicant_street_address': 'party.applicant.address',
            'applicant_city': 'party.applicant.address.city',
            'applicant_postal_code': 'party.applicant.address.postal',
            'applicant_phone_number': 'party.applicant.contact.phone',
            'applicant_email_address': 'party.applicant.contact.email',
            
            'respondent_full_legal_name': 'party.respondent.name',
            'respondent_first_name': 'party.respondent.name.first',
            'respondent_last_name': 'party.respondent.name.last',
            'respondent_street_address': 'party.respondent.address',
            'respondent_city': 'party.respondent.address.city',
            'respondent_postal_code': 'party.respondent.address.postal',
            'respondent_phone_number': 'party.respondent.contact.phone',
            'respondent_email_address': 'party.respondent.contact.email',
            
            # Court domain
            'court_file_number': 'case.file_number',
            'court_name': 'case.court.name',
            
            # Children domain
            'child_full_legal_name': 'children.name',
            'child_birth_date': 'children.birthdate',
            'child_current_age': 'children.age',
        }
        
        domain_mapped = []
        for field in consistent_fields:
            consistent_key = field.get('consistent_key', '')
            domain_concept = domain_mappings.get(consistent_key, f'form_specific.{consistent_key}')
            
            enhanced_field = field.copy()
            enhanced_field['domain_concept'] = domain_concept
            enhanced_field['docassemble_variable'] = self._map_to_docassemble_variable(domain_concept)
            
            domain_mapped.append(enhanced_field)
        
        return domain_mapped
    
    def _map_to_docassemble_variable(self, domain_concept: str) -> str:
        """Map domain concept to Docassemble variable"""
        
        docassemble_mappings = {
            'party.applicant.name': 'applicant.name.full',
            'party.applicant.name.first': 'applicant.name.first',
            'party.applicant.name.last': 'applicant.name.last',
            'party.applicant.address': 'applicant.address.address',
            'party.applicant.address.city': 'applicant.address.city',
            'party.applicant.address.postal': 'applicant.address.postal_code',
            'party.applicant.contact.phone': 'applicant.phone_number',
            'party.applicant.contact.email': 'applicant.email',
            
            'party.respondent.name': 'respondent.name.full',
            'party.respondent.name.first': 'respondent.name.first',
            'party.respondent.name.last': 'respondent.name.last',
            'party.respondent.address': 'respondent.address.address',
            'party.respondent.address.city': 'respondent.address.city',
            'party.respondent.address.postal': 'respondent.address.postal_code',
            'party.respondent.contact.phone': 'respondent.phone_number',
            'party.respondent.contact.email': 'respondent.email',
            
            'case.file_number': 'case.court_file_number',
            'case.court.name': 'case.court_name',
            
            'children.name': 'children[i].name.full',
            'children.birthdate': 'children[i].birthdate',
            'children.age': 'children[i].age',
        }
        
        return docassemble_mappings.get(domain_concept, domain_concept.replace('.', '_'))
    
    def _generate_interview_map(self, form_number: str, mapped_fields: List[Dict]) -> Dict[str, Any]:
        """Generate complete interview map"""
        
        interview_map = {
            'metadata': {
                'title': f'Ontario Family Law Form {form_number}',
                'short_title': f'Form {form_number}',
                'description': f'Complete interview for Ontario Family Law Form {form_number}',
                'form_number': form_number,
                'generated': datetime.now().isoformat(),
                'generator': 'simplified_unified_generator',
                'architecture': 'map_based_with_consistent_keys'
            },
            
            'include': [
                'docassemble.base:data/questions/basic-questions.yml'
            ],
            
            'objects': self._generate_objects_map(mapped_fields),
            
            'mandatory_code': self._generate_mandatory_code(form_number, mapped_fields),
            
            'questions': self._generate_questions_map(mapped_fields),
            
            'final_screens': self._generate_final_screens(form_number)
        }
        
        return interview_map
    
    def _generate_objects_map(self, mapped_fields: List[Dict]) -> List[Dict[str, str]]:
        """Generate objects map based on detected domain concepts"""
        
        objects = [
            {'applicant': 'Individual'},
            {'respondent': 'Individual'},
            {'case': 'DAObject'}
        ]
        
        # Detect if children are needed
        has_children = any('children' in field.get('domain_concept', '') for field in mapped_fields)
        if has_children:
            objects.append({'children': 'DAList.using(object_type=Individual)'})
        
        return objects
    
    def _generate_mandatory_code(self, form_number: str, mapped_fields: List[Dict]) -> str:
        """Generate mandatory code block"""
        
        code_lines = [
            f'# Ontario Family Law Form {form_number}',
            '# Generated using map-based architecture with consistent keys',
            '',
            '# Collect information using consistent field mappings'
        ]
        
        # Add variables for each field (limit to avoid too long)
        for field in mapped_fields[:20]:
            da_var = field.get('docassemble_variable', field.get('consistent_key', ''))
            code_lines.append(da_var)
        
        if len(mapped_fields) > 20:
            code_lines.append(f'# ... and {len(mapped_fields) - 20} more fields')
        
        code_lines.extend([
            '',
            '# Complete the interview',
            f'form_{form_number}_ready',
            'final_screen'
        ])
        
        return '\n'.join(code_lines)
    
    def _generate_questions_map(self, mapped_fields: List[Dict]) -> List[Dict[str, Any]]:
        """Generate questions map"""
        
        questions = []
        
        for field in mapped_fields:
            question_map = self._generate_question_for_field(field)
            if question_map:
                questions.append(question_map)
        
        return questions
    
    def _generate_question_for_field(self, field: Dict) -> Dict[str, Any]:
        """Generate question map for a single field"""
        
        field_type = field.get('field_type', 'text')
        da_variable = field.get('docassemble_variable', field.get('consistent_key', ''))
        # Use enhanced field_label first, then fall back to human_readable
        question_text = field.get('field_label', field.get('human_readable', field.get('consistent_key', '').replace('_', ' ').title()))
        
        if field_type == 'checkbox':
            return {
                'question': question_text,
                'yesno': da_variable
            }
        elif field_type == 'email':
            return {
                'question': question_text,
                'fields': [{
                    da_variable: {'datatype': 'email'}
                }]
            }
        elif field_type == 'date':
            return {
                'question': question_text,
                'fields': [{
                    da_variable: {'datatype': 'date'}
                }]
            }
        elif field_type == 'number':
            return {
                'question': question_text,
                'fields': [{
                    da_variable: {'datatype': 'integer'}
                }]
            }
        else:
            return {
                'question': question_text,
                'fields': [{da_variable: 'text'}]
            }
    
    def _generate_final_screens(self, form_number: str) -> List[Dict[str, Any]]:
        """Generate final screens"""
        
        return [
            {
                'event': 'final_screen',
                'question': f'Form {form_number} Complete',
                'subquestion': f'Your Ontario Family Law Form {form_number} has been prepared using consistent field mappings.',
                'buttons': [
                    {'Download PDF': f'${{{{ form_{form_number}_pdf.url_for() }}}}'},
                    {'Review Answers': 'review'},
                    {'Start Over': 'restart'}
                ]
            }
        ]
    
    def encode_to_yaml(self, interview_map: Dict[str, Any]) -> str:
        """Encode interview map to YAML format using simple string formatting"""
        
        yaml_blocks = []
        
        # Metadata block
        yaml_blocks.append("---")
        yaml_blocks.append("metadata:")
        for key, value in interview_map['metadata'].items():
            yaml_blocks.append(f"  {key}: {value}")
        
        # Include block
        yaml_blocks.append("---")
        yaml_blocks.append("include:")
        for include in interview_map['include']:
            yaml_blocks.append(f"  - {include}")
        
        # Objects block
        yaml_blocks.append("---")
        yaml_blocks.append("objects:")
        for obj in interview_map['objects']:
            for key, value in obj.items():
                yaml_blocks.append(f"  - {key}: {value}")
        
        # Mandatory block
        yaml_blocks.append("---")
        yaml_blocks.append("mandatory: True")
        yaml_blocks.append("code: |")
        for line in interview_map['mandatory_code'].split('\n'):
            yaml_blocks.append(f"  {line}")
        
        # Question blocks
        for question in interview_map['questions']:
            yaml_blocks.append("---")
            if 'yesno' in question:
                yaml_blocks.append(f"question: {question['question']}")
                yaml_blocks.append(f"yesno: {question['yesno']}")
            else:
                yaml_blocks.append(f"question: {question['question']}")
                yaml_blocks.append("fields:")
                for field in question['fields']:
                    for field_name, field_props in field.items():
                        if isinstance(field_props, dict):
                            yaml_blocks.append(f"  - {field_name}:")
                            for prop_key, prop_value in field_props.items():
                                yaml_blocks.append(f"      {prop_key}: {prop_value}")
                        else:
                            yaml_blocks.append(f"  - {field_name}: {field_props}")
        
        # Final screens
        for screen in interview_map['final_screens']:
            yaml_blocks.append("---")
            yaml_blocks.append(f"event: {screen['event']}")
            yaml_blocks.append(f"question: {screen['question']}")
            yaml_blocks.append(f"subquestion: {screen['subquestion']}")
            yaml_blocks.append("buttons:")
            for button in screen['buttons']:
                for button_text, button_action in button.items():
                    yaml_blocks.append(f"  - {button_text}: {button_action}")
        
        # Code block for form readiness
        yaml_blocks.append("---")
        yaml_blocks.append("code: |")
        yaml_blocks.append(f"  form_{interview_map['metadata']['form_number']}_ready = True")
        
        return '\n'.join(yaml_blocks)
    
    def _to_snake_case(self, text: str) -> str:
        """Convert text to snake_case"""
        return re.sub(r'[A-Z]', r'_\g<0>', text).lower().strip('_')
    
    def generate_all_interviews(self) -> Dict[str, Any]:
        """Generate interviews for all available forms"""
        
        results = {
            'successful': [],
            'failed': [],
            'total_interviews': 0,
            'consistent_keys_used': 0
        }
        
        # Get all parsed form files
        parsed_files = list(self.parsed_forms_dir.glob('form_*_improved.json'))
        
        for parsed_file in parsed_files:
            # Extract form number
            match = re.search(r'form_([^_]+)', parsed_file.stem)
            if not match:
                continue
            
            form_number = match.group(1)
            
            try:
                print(f"Generating interview for Form {form_number}...")
                
                # Generate interview map
                interview_map = self.generate_interview_map_for_form(form_number)
                
                # Encode to YAML
                yaml_content = self.encode_to_yaml(interview_map)
                
                # Save to file
                output_file = self.output_dir / f'form_{form_number}_unified.yml'
                with open(output_file, 'w') as f:
                    f.write(yaml_content)
                
                results['successful'].append({
                    'form_number': form_number,
                    'output_file': str(output_file),
                    'questions_count': len(interview_map.get('questions', [])),
                    'uses_consistent_keys': True
                })
                
                print(f"✅ Generated Form {form_number} with {len(interview_map.get('questions', []))} questions")
                
            except Exception as e:
                print(f"❌ Failed to generate Form {form_number}: {e}")
                results['failed'].append({
                    'form_number': form_number,
                    'error': str(e)
                })
        
        results['total_interviews'] = len(results['successful'])
        results['consistent_keys_used'] = len(self.form_key_registry.get('field_keys', {}))
        
        return results


def main():
    """Run the simplified unified generator"""
    
    generator = SimplifiedUnifiedGenerator()
    results = generator.generate_all_interviews()
    
    print(f"\n=== Generation Results ===")
    print(f"✅ Successful: {len(results['successful'])}")
    print(f"❌ Failed: {len(results['failed'])}")
    print(f"📝 Total interviews: {results['total_interviews']}")
    print(f"🔑 Consistent keys used: {results['consistent_keys_used']}")
    
    if results['failed']:
        print(f"\nFailed forms:")
        for failed in results['failed']:
            print(f"  - Form {failed['form_number']}: {failed['error']}")


if __name__ == "__main__":
    main()