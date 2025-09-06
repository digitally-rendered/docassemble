#!/usr/bin/env python3
"""
Intelligent Form Converter Agent

Converts individual Ontario family law forms into Docassemble interviews
using the common interview framework and parsed form data.

This agent:
1. Loads parsed form data for a specific form
2. Maps form fields to common framework modules
3. Generates form-specific interview logic
4. Creates complete YAML interview files
5. Integrates with shared validation and objects

Author: Form Factory Orchestrator
Created: 2025-09-05
"""

import json
import os
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class FormField:
    """Represents a field from a parsed form"""
    field_id: str
    field_name: str
    field_type: str
    field_label: str
    required: bool
    validation_rules: str
    options: Optional[List]
    table_context: Optional[str]

@dataclass
class InterviewSection:
    """Represents a section of an interview"""
    section_name: str
    title: str
    fields: List[FormField]
    dependencies: List[str]
    validation_logic: str

class IntelligentFormConverter:
    """Converts parsed forms to Docassemble interviews using the common framework"""
    
    def __init__(self, parsed_forms_dir: str, framework_analysis_file: str):
        self.parsed_forms_dir = parsed_forms_dir
        self.framework_analysis_file = framework_analysis_file
        self.framework_analysis = None
        self.form_data = None
        self.form_name = ""
        
        # Load framework analysis
        with open(framework_analysis_file, 'r', encoding='utf-8') as f:
            self.framework_analysis = json.load(f)
    
    def load_form_data(self, form_name: str) -> List[FormField]:
        """Load parsed data for a specific form"""
        form_file = os.path.join(self.parsed_forms_dir, f"{form_name}_fields.json")
        
        if not os.path.exists(form_file):
            raise FileNotFoundError(f"Parsed form data not found: {form_file}")
        
        with open(form_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        # Convert to FormField objects
        form_fields = []
        for field_data in raw_data:
            form_field = FormField(
                field_id=field_data.get('field_id', ''),
                field_name=field_data.get('field_name', ''),
                field_type=field_data.get('field_type', 'text'),
                field_label=field_data.get('field_label', ''),
                required=field_data.get('required', False),
                validation_rules=field_data.get('validation_rules', ''),
                options=field_data.get('options'),
                table_context=field_data.get('table_name')
            )
            form_fields.append(form_field)
        
        self.form_data = form_fields
        self.form_name = form_name
        return form_fields
    
    def categorize_form_fields(self, form_fields: List[FormField]) -> Dict[str, List[FormField]]:
        """Categorize form fields using semantic analysis"""
        categories = {
            'court_case_info': [],
            'party_information': [],
            'child_information': [],
            'financial_information': [],
            'legal_representation': [],
            'dates_and_timing': [],
            'form_specific': []
        }
        
        for field in form_fields:
            category = self._determine_field_category(field)
            categories[category].append(field)
        
        return categories
    
    def _determine_field_category(self, field: FormField) -> str:
        """Determine which category a field belongs to"""
        label_lower = field.field_label.lower()
        name_lower = field.field_name.lower()
        combined = f"{label_lower} {name_lower}"
        
        # Court and case information
        if any(term in combined for term in ['court', 'file number', 'case number']):
            return 'court_case_info'
        
        # Party information
        if any(term in combined for term in ['applicant', 'respondent', 'name', 'address', 'phone', 'email']):
            return 'party_information'
        
        # Child information
        if any(term in combined for term in ['child', 'minor', 'custody', 'access', 'born']):
            return 'child_information'
        
        # Financial information
        if any(term in combined for term in ['income', 'expense', 'asset', 'debt', '$', 'amount', 'total']):
            return 'financial_information'
        
        # Legal representation
        if any(term in combined for term in ['lawyer', 'counsel', 'representative']):
            return 'legal_representation'
        
        # Dates
        if any(term in combined for term in ['date', 'year', 'month', 'day']) or field.field_type == 'date':
            return 'dates_and_timing'
        
        # Everything else is form-specific
        return 'form_specific'
    
    def create_interview_sections(self, categorized_fields: Dict[str, List[FormField]]) -> List[InterviewSection]:
        """Create logical interview sections from categorized fields"""
        sections = []
        
        # Define section ordering and titles
        section_config = {
            'court_case_info': {
                'title': 'Court and Case Information',
                'order': 1
            },
            'party_information': {
                'title': 'Party Information',
                'order': 2
            },
            'child_information': {
                'title': 'Children Information',
                'order': 3
            },
            'legal_representation': {
                'title': 'Legal Representation',
                'order': 4
            },
            'financial_information': {
                'title': 'Financial Information',
                'order': 5
            },
            'dates_and_timing': {
                'title': 'Important Dates',
                'order': 6
            },
            'form_specific': {
                'title': f'{self.form_name.replace("_", " ").title()} Specific Information',
                'order': 7
            }
        }
        
        for category, config in section_config.items():
            if category in categorized_fields and categorized_fields[category]:
                # Determine dependencies
                dependencies = self._get_section_dependencies(category)
                
                # Create validation logic
                validation_logic = self._create_validation_logic(categorized_fields[category])
                
                section = InterviewSection(
                    section_name=category,
                    title=config['title'],
                    fields=categorized_fields[category],
                    dependencies=dependencies,
                    validation_logic=validation_logic
                )
                sections.append((config['order'], section))
        
        # Sort by order and return sections
        sections.sort(key=lambda x: x[0])
        return [section for _, section in sections]
    
    def _get_section_dependencies(self, category: str) -> List[str]:
        """Get dependencies for a section"""
        dependencies = {
            'court_case_info': [],
            'party_information': ['court_case_info'],
            'child_information': ['party_information'],
            'legal_representation': ['party_information'],
            'financial_information': ['party_information'],
            'dates_and_timing': [],
            'form_specific': ['court_case_info', 'party_information']
        }
        return dependencies.get(category, [])
    
    def _create_validation_logic(self, fields: List[FormField]) -> str:
        """Create validation logic for a group of fields"""
        validation_rules = []
        
        for field in fields:
            field_name = self._sanitize_field_name(field.field_name)
            
            # Add validation based on field type and content
            if 'email' in field.field_label.lower():
                validation_rules.append(f"validate_email_address({field_name})")
            elif 'phone' in field.field_label.lower():
                validation_rules.append(f"validate_phone_number({field_name})")
            elif 'postal' in field.field_label.lower():
                validation_rules.append(f"validate_ontario_postal_code({field_name})")
            elif 'court file' in field.field_label.lower():
                validation_rules.append(f"validate_court_file_number({field_name})")
            elif field.field_type == 'currency':
                validation_rules.append(f"validate_currency_amount({field_name})")
        
        return "\\n".join(validation_rules) if validation_rules else ""
    
    def _sanitize_field_name(self, field_name: str) -> str:
        """Sanitize field name for use as Python/YAML variable"""
        # Remove special characters and convert to valid Python identifier
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', field_name)
        sanitized = re.sub(r'_+', '_', sanitized).strip('_')
        
        # Ensure it doesn't start with a number
        if sanitized and sanitized[0].isdigit():
            sanitized = f"field_{sanitized}"
        
        return sanitized[:50]  # Limit length
    
    def generate_yaml_interview(self, sections: List[InterviewSection]) -> Dict:
        """Generate complete YAML interview structure"""
        
        # Extract form number from form name
        form_number_match = re.search(r'form_(\d+[a-z]?)', self.form_name.lower())
        form_number = form_number_match.group(1).upper() if form_number_match else self.form_name
        
        interview = {
            'metadata': {
                'title': f'Ontario Family Law Form {form_number}',
                'short title': f'Form {form_number}',
                'generated': datetime.now().isoformat(),
                'source_form': self.form_name,
                'framework_version': '1.0.0'
            },
            'features': {
                'javascript': 'ontario-family-law.js',
                'css': 'ontario-family-law.css',
                'debug': True,
                'hide standard menu': False
            },
            'modules': {
                'docassemble.base.util': ['Individual', 'Address', 'DAList', 'Value', 'currency', 'validation_error'],
                'docassemble.ontario_family_law.objects': ['OntarioCourtCase', 'OntarioParty', 'OntarioChild', 'FinancialInformation']
            },
            'objects': [
                {'case': 'OntarioCourtCase'},
                {'applicant': 'OntarioParty'},
                {'respondent': 'OntarioParty'},
                {'children': 'DAList.using(object_type=OntarioChild)'},
                {'form_data': 'DADict'}
            ],
            'mandatory': True,
            'code': self._generate_mandatory_code_block(),
            'questions': []
        }
        
        # Generate questions for each section
        for section in sections:
            section_questions = self._generate_section_questions(section)
            interview['questions'].extend(section_questions)
        
        # Add navigation and completion questions
        interview['questions'].extend(self._generate_navigation_questions())
        
        # Add final document generation
        interview['questions'].append(self._generate_document_question(form_number))
        
        return interview
    
    def _generate_mandatory_code_block(self) -> str:
        """Generate the mandatory code block that drives the interview"""
        return f'''
# Set form information
form_data['form_name'] = '{self.form_name}'
form_data['form_title'] = interview_metadata()['title']

# Initialize progress tracking
form_data['sections_completed'] = []

# Drive the interview through logical sections
court_case_info_complete
party_information_complete  
form_specific_complete
review_and_submit
'''
    
    def _generate_section_questions(self, section: InterviewSection) -> List[Dict]:
        """Generate YAML questions for a section"""
        questions = []
        
        # Section introduction
        if len(section.fields) > 1:
            questions.append({
                'question': f'{section.title}',
                'subquestion': f'Please provide the {section.title.lower()} for this form.',
                'fields': self._convert_fields_to_yaml(section.fields),
                'validation code': section.validation_logic if section.validation_logic else None,
                'continue button field': f'{section.section_name}_complete'
            })
        else:
            # Single field questions
            for field in section.fields:
                questions.append(self._convert_single_field_to_yaml(field, section))
        
        return [q for q in questions if q]  # Filter out None values
    
    def _convert_fields_to_yaml(self, fields: List[FormField]) -> List[Dict]:
        """Convert form fields to YAML field definitions"""
        yaml_fields = []
        
        for field in fields:
            field_name = self._sanitize_field_name(field.field_name)
            
            # Skip empty or invalid fields
            if not field_name or not field.field_label:
                continue
            
            yaml_field = {
                'field': field_name,
                'datatype': self._convert_field_type(field.field_type)
            }
            
            # Clean and set label
            clean_label = self._clean_field_label(field.field_label)
            if clean_label:
                yaml_field['label'] = clean_label
            
            # Add validation if present
            if field.validation_rules:
                yaml_field['validate'] = field.validation_rules
            
            # Add options if present
            if field.options:
                yaml_field['choices'] = field.options
            
            # Mark as required if specified
            if field.required:
                yaml_field['required'] = True
            
            # Add help text for complex fields
            help_text = self._generate_help_text(field)
            if help_text:
                yaml_field['help'] = help_text
            
            yaml_fields.append(yaml_field)
        
        return yaml_fields
    
    def _convert_single_field_to_yaml(self, field: FormField, section: InterviewSection) -> Dict:
        """Convert a single field to a YAML question"""
        field_name = self._sanitize_field_name(field.field_name)
        
        if not field_name or not field.field_label:
            return None
        
        clean_label = self._clean_field_label(field.field_label)
        
        question = {
            'question': clean_label,
            'fields': [{
                'field': field_name,
                'datatype': self._convert_field_type(field.field_type)
            }]
        }
        
        # Add validation
        if field.validation_rules:
            question['validation code'] = field.validation_rules
        
        # Add help text
        help_text = self._generate_help_text(field)
        if help_text:
            question['subquestion'] = help_text
        
        return question
    
    def _clean_field_label(self, label: str) -> str:
        """Clean and format field label for display"""
        if not label:
            return ""
        
        # Remove repetitive text
        clean = re.sub(r'\b(\w+)(\s+\1)+\b', r'\1', label)
        
        # Remove excessive punctuation
        clean = re.sub(r'[:\s]+$', '', clean)
        clean = re.sub(r'^[:\s]+', '', clean)
        
        # Capitalize first letter
        clean = clean.strip()
        if clean:
            clean = clean[0].upper() + clean[1:]
        
        # Limit length
        if len(clean) > 100:
            clean = clean[:97] + "..."
        
        return clean
    
    def _convert_field_type(self, field_type: str) -> str:
        """Convert form field type to Docassemble datatype"""
        type_mapping = {
            'text': 'text',
            'date': 'date',
            'currency': 'currency',
            'number': 'number',
            'email': 'email',
            'tel': 'text',
            'checkbox': 'yesno',
            'radio': 'radio',
            'select': 'dropdown'
        }
        
        return type_mapping.get(field_type.lower(), 'text')
    
    def _generate_help_text(self, field: FormField) -> Optional[str]:
        """Generate helpful text for complex fields"""
        label_lower = field.field_label.lower()
        
        if 'court file number' in label_lower:
            return "Enter the court file number in format XX-YY-12345678"
        elif 'postal code' in label_lower:
            return "Enter Canadian postal code (format: A1A 1A1)"
        elif 'phone' in label_lower:
            return "Enter 10-digit phone number"
        elif 'email' in label_lower:
            return "Enter valid email address"
        elif field.field_type == 'currency':
            return "Enter dollar amount (do not include $ sign)"
        elif field.field_type == 'date':
            return "Enter date in MM/DD/YYYY format"
        
        return None
    
    def _generate_navigation_questions(self) -> List[Dict]:
        """Generate navigation and review questions"""
        return [
            {
                'question': 'Review Your Information',
                'subquestion': '''
                Please review the information you have entered. You can go back to make changes 
                or continue to generate your form.
                
                **Court Case Information:** ${ case.court_file_number if defined('case.court_file_number') else 'Not provided' }
                
                **Applicant:** ${ applicant.name if defined('applicant.name') else 'Not provided' }
                
                **Form Type:** ${ form_data['form_title'] }
                ''',
                'field': 'review_complete',
                'datatype': 'yesnoradio',
                'choices': [
                    ['True', 'Information is correct, generate form'],
                    ['False', 'Go back to make changes']
                ]
            }
        ]
    
    def _generate_document_question(self, form_number: str) -> Dict:
        """Generate the final document generation question"""
        return {
            'question': f'Your Form {form_number} is Ready',
            'subquestion': '''
            Your form has been generated with the information you provided.
            You can download it below or email it to yourself.
            ''',
            'field': 'form_generated',
            'datatype': 'yesnoradio',
            'choices': [
                ['download', 'Download PDF'],
                ['email', 'Email to me'],
                ['both', 'Download and Email']
            ],
            'attachment': {
                'name': f'Ontario Family Law Form {form_number}',
                'filename': f'form_{form_number.lower()}',
                'pdf template file': f'form_{form_number.lower()}_template.pdf',
                'fields': '${ form_data }'
            }
        }
    
    def save_interview_yaml(self, interview_data: Dict, output_file: str):
        """Save the generated interview as a YAML file"""
        import yaml
        
        # Custom YAML representer to handle our data structure
        def represent_none(self, data):
            return self.represent_scalar('tag:yaml.org,2002:null', '')
        
        yaml.add_representer(type(None), represent_none)
        
        # Convert to YAML string
        yaml_content = "---\n"
        
        # Add metadata
        yaml_content += "metadata:\n"
        for key, value in interview_data['metadata'].items():
            yaml_content += f"  {key}: {repr(value)}\n"
        
        yaml_content += "---\n"
        
        # Add features
        yaml_content += "features:\n"
        for key, value in interview_data['features'].items():
            yaml_content += f"  {key}: {value}\n"
        
        yaml_content += "---\n"
        
        # Add modules
        yaml_content += "modules:\n"
        for module, imports in interview_data['modules'].items():
            yaml_content += f"  {module}: {imports}\n"
        
        yaml_content += "---\n"
        
        # Add objects
        yaml_content += "objects:\n"
        for obj in interview_data['objects']:
            for name, type_def in obj.items():
                yaml_content += f"  - {name}: {type_def}\n"
        
        yaml_content += "---\n"
        
        # Add mandatory code
        yaml_content += "mandatory: True\n"
        yaml_content += "code: |\n"
        for line in interview_data['code'].strip().split('\\n'):
            yaml_content += f"  {line}\n"
        
        yaml_content += "---\n"
        
        # Add questions
        for question in interview_data['questions']:
            yaml_content += yaml.dump([question], default_flow_style=False)
            yaml_content += "---\n"
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        print(f"✅ Interview saved to: {output_file}")
    
    def convert_form_to_interview(self, form_name: str, output_file: str = None):
        """Convert a specific form to a Docassemble interview"""
        print(f"🔄 Converting {form_name} to Docassemble interview...")
        
        # Load form data
        form_fields = self.load_form_data(form_name)
        print(f"📋 Loaded {len(form_fields)} fields from {form_name}")
        
        # Categorize fields
        categorized_fields = self.categorize_form_fields(form_fields)
        print(f"📂 Categorized fields into {len([c for c in categorized_fields.values() if c])} sections")
        
        # Create interview sections
        sections = self.create_interview_sections(categorized_fields)
        print(f"📄 Created {len(sections)} interview sections")
        
        # Generate YAML interview
        interview_yaml = self.generate_yaml_interview(sections)
        
        # Save interview
        if not output_file:
            output_file = f"{form_name}_interview.yml"
        
        self.save_interview_yaml(interview_yaml, output_file)
        
        return {
            'form_name': form_name,
            'fields_count': len(form_fields),
            'sections': len(sections),
            'output_file': output_file,
            'categorized_fields': {k: len(v) for k, v in categorized_fields.items() if v}
        }

def main():
    """Main execution function"""
    import sys
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    parsed_forms_dir = os.path.join(base_dir, 'parsed_forms')
    framework_analysis_file = os.path.join(base_dir, 'enhanced_common_fields_analysis.json')
    output_dir = os.path.join(base_dir, 'generated_interviews')
    
    os.makedirs(output_dir, exist_ok=True)
    
    converter = IntelligentFormConverter(parsed_forms_dir, framework_analysis_file)
    
    # Get form name from command line or use default
    if len(sys.argv) > 1:
        form_names = sys.argv[1].split(',')
    else:
        # Convert all available forms
        form_names = [f.replace('_fields.json', '') for f in os.listdir(parsed_forms_dir) if f.endswith('_fields.json')]
    
    results = []
    for form_name in form_names:
        try:
            output_file = os.path.join(output_dir, f"{form_name}_interview.yml")
            result = converter.convert_form_to_interview(form_name, output_file)
            results.append(result)
            print(f"✅ Successfully converted {form_name}")
        except Exception as e:
            print(f"❌ Error converting {form_name}: {e}")
    
    # Print summary
    print(f"\\n📊 Conversion Summary:")
    print(f"   • Forms converted: {len(results)}")
    total_fields = sum(r['fields_count'] for r in results)
    total_sections = sum(r['sections'] for r in results)
    print(f"   • Total fields processed: {total_fields}")
    print(f"   • Total sections created: {total_sections}")
    print(f"   • Output directory: {output_dir}")

if __name__ == '__main__':
    main()