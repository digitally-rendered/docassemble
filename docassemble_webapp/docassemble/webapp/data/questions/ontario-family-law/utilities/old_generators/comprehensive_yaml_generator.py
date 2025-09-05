#!/usr/bin/env python3
"""
Comprehensive YAML Generator for Docassemble
Includes both fields and explanatory text properly classified
"""

import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass

@dataclass
class FormConfiguration:
    """Form configuration"""
    form_number: str
    form_title: str
    form_type: str
    category: str
    url: str
    filename: str
    requires_financial: bool = False
    has_children_section: bool = False
    has_property_section: bool = False

class ComprehensiveYAMLGenerator:
    """Generate comprehensive docassemble YAML with fields and instructions"""
    
    def __init__(self, form_config: FormConfiguration):
        self.config = form_config
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
    def sanitize_variable_name(self, text: str) -> str:
        """Create a valid Python variable name"""
        text = re.sub(r'[^\w]', '_', str(text))
        text = re.sub(r'_+', '_', text)
        text = text.lower().strip('_')
        if text and not text[0].isalpha():
            text = 'field_' + text
        if len(text) > 30:
            text = text[:30]
        return text or 'field'
    
    def sanitize_text(self, text: str, max_length: int = 1000) -> str:
        """Clean text for YAML display"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', str(text)).strip()
        # Escape special characters
        text = text.replace('"', '\\"').replace("'", "\\'")
        # Truncate if needed
        if len(text) > max_length:
            text = text[:max_length-3] + '...'
        return text
    
    def generate_comprehensive_interview(self, parsed_content: Dict) -> str:
        """Generate comprehensive docassemble YAML from classified content"""
        
        sections = []
        
        # 1. Metadata
        metadata = f"""metadata:
  title: Form {self.config.form_number} - {self.config.form_title[:50]}
  short title: Form {self.config.form_number}
  description: Ontario Family Law Form {self.config.form_number}
  authors:
    - name: Ontario Family Law Forms System
  revision_date: {datetime.now().strftime('%Y-%m-%d')}"""
        sections.append(metadata)
        
        # 2. Includes
        includes = """include:
  - docassemble.base:data/questions/basic-questions.yml"""
        sections.append(includes)
        
        # 3. Objects
        objects = """objects:
  - applicant: Individual
  - respondent: Individual  
  - court: DAObject"""
        
        if self.config.requires_financial:
            objects += "\n  - financial: DAObject"
            
        sections.append(objects)
        
        # 4. Introduction with instructions
        intro_instructions = self._extract_intro_instructions(parsed_content)
        intro = f"""mandatory: True
question: |
  Form {self.config.form_number}: {self.config.form_title[:60]}
subquestion: |
  This interview will help you complete Form {self.config.form_number}.
  
{intro_instructions}
continue button field: intro_shown"""
        sections.append(intro)
        
        # 5. Generate sections based on classified content
        sections_content = self._organize_content_by_sections(parsed_content)
        
        for section_name, section_data in sections_content.items():
            section_yaml = self._generate_section(section_name, section_data)
            if section_yaml:
                sections.append(section_yaml)
        
        # 6. Review screen
        review = f"""mandatory: True
question: |
  Review Your Information
review:
  - Edit: applicant.name.first
    button: |
      **Applicant:** ${{applicant.name.first}} ${{applicant.name.last}}
  - Edit: court.file_number
    button: |
      **Court File:** ${{court.file_number}}
continue button field: review_complete"""
        sections.append(review)
        
        # 7. Final screen
        final = f"""mandatory: True
question: |
  Form {self.config.form_number} Complete
subquestion: |
  Your form has been completed. You can now download or print your form.
buttons:
  - Exit: exit
  - Restart: restart
attachment:
  name: Form {self.config.form_number}
  filename: form_{self.config.form_number.lower()}
  description: |
    Ontario Family Law Form {self.config.form_number}
  content: |
    [Form content will be generated here]"""
        sections.append(final)
        
        return '\n---\n'.join(sections)
    
    def _extract_intro_instructions(self, parsed_content: Dict) -> str:
        """Extract introduction instructions from legal texts and instructions"""
        intro_text = []
        
        # Get first few instructions and legal texts
        if 'instructions' in parsed_content:
            for instruction in parsed_content['instructions'][:3]:
                text = self.sanitize_text(instruction.get('cleaned_text', ''), 200)
                if text and len(text) > 20:
                    intro_text.append(f"  **Note:** {text}")
        
        if 'legal_texts' in parsed_content:
            for legal in parsed_content['legal_texts'][:2]:
                if 'NOTE:' in legal.get('text', '') or 'IMPORTANT:' in legal.get('text', ''):
                    text = self.sanitize_text(legal.get('cleaned_text', ''), 200)
                    intro_text.append(f"  \n  **{text}**")
        
        # If no instructions found but we have fields, add basic intro
        if not intro_text and 'fields' in parsed_content and parsed_content.get('total_fields', 0) > 0:
            intro_text.append("  Please complete all required fields in this form.")
            intro_text.append("  Fields marked with * are mandatory.")
        
        return '\n'.join(intro_text) if intro_text else "  Please have your information ready."
    
    def _organize_content_by_sections(self, parsed_content: Dict) -> Dict:
        """Organize content into logical form sections"""
        
        sections = {
            'Court Information': {
                'fields': [],
                'instructions': [],
                'help_texts': []
            },
            'Your Information': {
                'fields': [],
                'instructions': [],
                'help_texts': []
            },
            'Other Party Information': {
                'fields': [],
                'instructions': [],
                'help_texts': []
            }
        }
        
        # Add financial section if needed
        if self.config.requires_financial:
            sections['Financial Information'] = {
                'fields': [],
                'instructions': [],
                'help_texts': []
            }
        
        # Distribute fields into sections based on labels
        if 'fields' in parsed_content:
            for field in parsed_content['fields']:
                # Handle both old and new format
                label = field.get('label', '') or field.get('metadata', {}).get('label', '')
                label_lower = label.lower()
                
                if any(word in label_lower for word in ['court', 'file', 'case']):
                    sections['Court Information']['fields'].append(field)
                elif any(word in label_lower for word in ['applicant', 'your', 'my']):
                    sections['Your Information']['fields'].append(field)
                elif any(word in label_lower for word in ['respondent', 'other party', 'spouse']):
                    sections['Other Party Information']['fields'].append(field)
                elif any(word in label_lower for word in ['income', 'expense', 'asset', 'debt', 'financial', 'money']):
                    if 'Financial Information' in sections:
                        sections['Financial Information']['fields'].append(field)
                else:
                    # Default to Your Information
                    sections['Your Information']['fields'].append(field)
        
        # If no fields found, add standard fields
        if not sections['Court Information']['fields']:
            sections['Court Information']['fields'] = self._get_standard_fields('court')
        if not sections['Your Information']['fields']:
            sections['Your Information']['fields'] = self._get_standard_fields('applicant')
        
        return sections
    
    def _get_standard_fields(self, section_type: str) -> List[Dict]:
        """Get standard fields for a section"""
        standard_fields = {
            'court': [
                {'metadata': {'label': 'Court File Number', 'field_type': 'text', 'required': True}},
                {'metadata': {'label': 'Court Name', 'field_type': 'text', 'required': True}},
                {'metadata': {'label': 'Court Office Address', 'field_type': 'text', 'required': False}},
            ],
            'applicant': [
                {'metadata': {'label': 'First Name', 'field_type': 'text', 'required': True}},
                {'metadata': {'label': 'Last Name', 'field_type': 'text', 'required': True}},
                {'metadata': {'label': 'Date of Birth', 'field_type': 'date', 'required': False}},
                {'metadata': {'label': 'Address', 'field_type': 'text', 'required': False}},
                {'metadata': {'label': 'City', 'field_type': 'text', 'required': False}},
                {'metadata': {'label': 'Province', 'field_type': 'text', 'required': False}},
            ]
        }
        return standard_fields.get(section_type, [])
    
    def _generate_section(self, section_name: str, section_data: Dict) -> Optional[str]:
        """Generate a YAML section from classified content"""
        
        fields = section_data.get('fields', [])
        instructions = section_data.get('instructions', [])
        
        if not fields and section_name not in ['Court Information', 'Your Information']:
            return None
        
        section = f"""mandatory: True
question: |
  {section_name}"""
        
        # Add instructions as subquestion if available
        if instructions:
            instruction_text = self.sanitize_text(instructions[0].get('cleaned_text', ''), 200)
            section += f"""
subquestion: |
  {instruction_text}"""
        
        section += "\nfields:"
        
        # Add fields or standard fields
        if fields:
            # Remove duplicates based on label
            seen_labels = set()
            unique_fields = []
            for field in fields:
                # Handle both old and new format
                label = field.get('label', '') or field.get('metadata', {}).get('label', 'Field')
                if label not in seen_labels:
                    seen_labels.add(label)
                    unique_fields.append(field)
            
            for field in unique_fields[:8]:  # Limit to 8 fields per section
                # Handle both old and new format
                if 'label' in field:
                    # New format from table_aware_parser
                    label = field.get('label', 'Field')
                    field_type = field.get('field_type', 'text')
                    required = field.get('required', False)
                else:
                    # Old format
                    metadata = field.get('metadata', {})
                    label = metadata.get('label', 'Field')
                    field_type = metadata.get('field_type', 'text')
                    required = metadata.get('required', False)
                
                # Clean label
                label = self.sanitize_text(label, 60)
                var_name = self.sanitize_variable_name(label)
                
                # Determine object prefix
                if 'court' in section_name.lower():
                    var_path = f"court.{var_name}"
                elif 'other party' in section_name.lower() or 'respondent' in section_name.lower():
                    var_path = f"respondent.{var_name}"
                elif 'financial' in section_name.lower():
                    var_path = f"financial.{var_name}"
                else:
                    var_path = f"applicant.{var_name}"
                
                section += f"\n  - {label}: {var_path}"
                
                if field_type != 'text':
                    section += f"\n    datatype: {field_type}"
                if required:
                    section += "\n    required: True"
                if field_type == 'currency':
                    section += "\n    min: 0"
        else:
            # Add standard fields based on section
            if 'court' in section_name.lower():
                section += """
  - Court File Number: court.file_number
    required: True
  - Court Name: court.name
    required: True
  - Court Office Address: court.address"""
            elif 'your' in section_name.lower() or 'applicant' in section_name.lower():
                section += """
  - First Name: applicant.name.first
    required: True
  - Last Name: applicant.name.last
    required: True
  - Address: applicant.address.address
  - City: applicant.address.city
  - Province: applicant.address.state
    default: ON"""
        
        return section

def generate_comprehensive_yaml(form_config: FormConfiguration, parsed_content: Dict) -> str:
    """Generate comprehensive docassemble YAML"""
    generator = ComprehensiveYAMLGenerator(form_config)
    return generator.generate_comprehensive_interview(parsed_content)

if __name__ == "__main__":
    # Test with sample parsed content
    test_config = FormConfiguration(
        form_number="13",
        form_title="Financial Statement",
        form_type="financial",
        category="support",
        url="",
        filename="form_13.docx",
        requires_financial=True
    )
    
    # Sample parsed content
    test_content = {
        'fields': [
            {
                'metadata': {
                    'label': 'Court File Number',
                    'field_type': 'text',
                    'required': True
                },
                'cleaned_text': 'Court File Number'
            }
        ],
        'instructions': [
            {
                'cleaned_text': 'You must complete this form if you are making or responding to a claim for support.'
            }
        ],
        'legal_texts': [
            {
                'text': 'NOTE: Financial disclosure is required by law.',
                'cleaned_text': 'Financial disclosure is required by law.'
            }
        ]
    }
    
    yaml_content = generate_comprehensive_yaml(test_config, test_content)
    
    with open('test_comprehensive_form_13.yml', 'w') as f:
        f.write(yaml_content)
    
    print("Generated comprehensive YAML")
    print("\nFirst 500 chars:")
    print(yaml_content[:500])