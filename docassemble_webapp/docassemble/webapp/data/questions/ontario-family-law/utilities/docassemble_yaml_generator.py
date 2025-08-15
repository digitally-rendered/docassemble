#!/usr/bin/env python3
"""
Advanced Docassemble YAML Generator for Ontario Family Law Forms
Generates production-ready docassemble interview files from extracted form field data
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Set
from datetime import datetime
from collections import OrderedDict

class DocassembleYAMLGenerator:
    """Generate sophisticated docassemble YAML interviews from form field analysis"""
    
    def __init__(self):
        self.form_mappings = {
            'form_8': {
                'title': 'Ontario Family Law Form 8 - Application (General)',
                'short_title': 'Form 8 - Application',
                'description': 'Complete Ontario Family Court Form 8 - Application (General) to start family court proceedings.',
                'objects': ['applicant', 'respondent', 'children', 'court_info', 'claims']
            },
            'form_10': {
                'title': 'Ontario Family Law Form 10 - Answer',
                'short_title': 'Form 10 - Answer',
                'description': 'Complete Ontario Family Court Form 10 - Answer to respond to an application.',
                'objects': ['applicant', 'respondent', 'children', 'court_info', 'response_claims']
            },
            'form_13': {
                'title': 'Ontario Family Law Form 13 - Financial Statement (Support Claims)',
                'short_title': 'Form 13 - Financial Statement',
                'description': 'Complete financial disclosure for support claims.',
                'objects': ['party', 'income', 'expenses', 'assets', 'debts']
            },
            'form_36': {
                'title': 'Ontario Family Law Form 36 - Affidavit for Divorce',
                'short_title': 'Form 36 - Divorce Affidavit',
                'description': 'Affidavit required for uncontested divorce proceedings.',
                'objects': ['applicant', 'respondent', 'marriage_info', 'separation_info', 'children']
            }
        }
        
        self.field_groups = {
            'party_info': ['name', 'birthdate', 'address', 'phone', 'email', 'lawyer'],
            'court_info': ['court_name', 'court_file_number', 'court_address', 'court_location'],
            'financial': ['income', 'expense', 'asset', 'debt', 'support', 'property'],
            'children': ['child_name', 'child_birthdate', 'custody', 'access', 'child_support'],
            'marriage': ['marriage_date', 'separation_date', 'divorce_grounds', 'reconciliation'],
            'claims': ['custody', 'access', 'support', 'property', 'divorce', 'restraining']
        }
    
    def deduplicate_fields(self, fields: List[Dict]) -> List[Dict]:
        """Remove duplicate fields keeping the most informative version"""
        seen_fields = {}
        
        for field in fields:
            key = field['field_name']
            
            # Skip unnamed or generic fields
            if key in ['unnamed_field', 'field', '']:
                continue
            
            # Keep the most complete version of each field
            if key not in seen_fields:
                seen_fields[key] = field
            else:
                # Keep the one with more information
                existing = seen_fields[key]
                if len(field.get('original_text', '')) > len(existing.get('original_text', '')):
                    seen_fields[key] = field
        
        return list(seen_fields.values())
    
    def group_fields_by_section(self, fields: List[Dict]) -> Dict[str, List[Dict]]:
        """Organize fields into logical sections"""
        sections = {
            'court_information': [],
            'applicant_information': [],
            'respondent_information': [],
            'children_information': [],
            'financial_information': [],
            'marriage_information': [],
            'claims': [],
            'other': []
        }
        
        for field in fields:
            field_name = field['field_name'].lower()
            original_text = field.get('original_text', '').lower()
            
            # Categorize based on field name and content
            if any(term in field_name or term in original_text for term in ['court', 'file_number', 'judge']):
                sections['court_information'].append(field)
            elif any(term in field_name or term in original_text for term in ['applicant', 'petitioner']):
                sections['applicant_information'].append(field)
            elif any(term in field_name or term in original_text for term in ['respondent', 'defendant']):
                sections['respondent_information'].append(field)
            elif any(term in field_name or term in original_text for term in ['child', 'custody', 'access', 'parenting']):
                sections['children_information'].append(field)
            elif any(term in field_name or term in original_text for term in ['income', 'expense', 'asset', 'debt', 'financial', 'support', 'money']):
                sections['financial_information'].append(field)
            elif any(term in field_name or term in original_text for term in ['marriage', 'married', 'separation', 'divorce']):
                sections['marriage_information'].append(field)
            elif any(term in field_name or term in original_text for term in ['claim', 'order', 'relief']):
                sections['claims'].append(field)
            else:
                sections['other'].append(field)
        
        # Remove empty sections
        return {k: v for k, v in sections.items() if v}
    
    def generate_docassemble_variable(self, field: Dict, section: str) -> str:
        """Generate proper docassemble variable name"""
        field_name = field['field_name']
        
        # Map sections to object prefixes
        prefix_map = {
            'court_information': 'court_info',
            'applicant_information': 'applicant',
            'respondent_information': 'respondent',
            'children_information': 'children',
            'financial_information': 'financial',
            'marriage_information': 'marriage',
            'claims': 'claims'
        }
        
        prefix = prefix_map.get(section, '')
        
        # Clean up field name
        if field_name and field_name != 'unnamed_field':
            clean_name = re.sub(r'[^a-z0-9_]', '_', field_name.lower())
            clean_name = re.sub(r'_+', '_', clean_name).strip('_')
            
            if prefix and not clean_name.startswith(prefix):
                return f"{prefix}.{clean_name}"
            return clean_name
        
        # Generate name from original text if field_name is generic
        original = field.get('original_text', '')
        if original:
            # Extract meaningful part
            clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', original)
            words = clean_text.lower().split()[:3]  # First 3 words
            generated_name = '_'.join(words)
            if prefix:
                return f"{prefix}.{generated_name}"
            return generated_name
        
        return f"{prefix}.field_{id(field)}"
    
    def generate_yaml_content(self, form_structure: Dict) -> str:
        """Generate complete docassemble YAML interview"""
        form_name = form_structure.get('form_name', 'unknown_form')
        fields = form_structure.get('fields', [])
        
        # Deduplicate fields
        unique_fields = self.deduplicate_fields(fields)
        
        # Group fields by section
        sections = self.group_fields_by_section(unique_fields)
        
        # Determine form type
        form_key = None
        for key in self.form_mappings:
            if key in form_name.lower():
                form_key = key
                break
        
        if not form_key:
            form_key = 'form_8'  # Default
        
        form_config = self.form_mappings[form_key]
        
        # Start building YAML content
        yaml_content = f"""---
metadata:
  title: |
    {form_config['title']}
  short title: |
    {form_config['short_title']}
  description: |
    {form_config['description']}
  authors:
    - name: Ontario Family Law Forms System
  revision_date: {datetime.now().strftime('%Y-%m-%d')}
  tags:
    - ontario
    - family-law
    - {form_name.lower().replace('_', '-')}
    - court-forms
  help_url: https://ontariocourtforms.on.ca/en/family-law-forms/
---
include:
  - ontario-family-law-common.yml
---
features:
  question help button: True
  navigation: True
  progress bar: True
  show progress bar percentage: True
  css: ontario-family-law.css
---
objects:"""
        
        # Add objects based on sections found
        if 'applicant_information' in sections:
            yaml_content += "\n  - applicant: Individual"
        if 'respondent_information' in sections:
            yaml_content += "\n  - respondent: Individual"
        if 'children_information' in sections:
            yaml_content += "\n  - children: DAList.using(object_type=Individual, minimum_number=0)"
        if 'court_information' in sections:
            yaml_content += "\n  - court_info: DAObject"
        if 'financial_information' in sections:
            yaml_content += "\n  - financial: DAObject"
        if 'marriage_information' in sections:
            yaml_content += "\n  - marriage: DAObject"
        if 'claims' in sections:
            yaml_content += "\n  - claims: DADict"
        
        yaml_content += "\n---\n"
        
        # Generate mandatory code block for interview flow
        yaml_content += """mandatory: True
code: |
  # Introduction
  introduction_screen
  legal_disclaimer_accepted
  
  # Main interview flow"""
        
        # Add interview flow based on sections
        for section_name, section_fields in sections.items():
            if section_fields:
                yaml_content += f"\n  \n  # {section_name.replace('_', ' ').title()}"
                
                # Add first few fields from each section to flow
                for field in section_fields[:3]:
                    var_name = self.generate_docassemble_variable(field, section_name)
                    yaml_content += f"\n  {var_name}"
        
        yaml_content += """
  
  # Review and submission
  review_screen
  final_screen
---
# Introduction screen
question: |
  Welcome to the Ontario Family Law Forms Assistant
subquestion: |
  This interview will help you complete your Ontario family law court form.
  
  Before you begin, please have the following information ready:
  
  * Personal identification for all parties
  * Contact information
  * Court file number (if you have one)
  * Financial information (if applicable)
  * Details about your case
  
  **Important:** This tool provides assistance in completing court forms but does not provide legal advice.
continue button field: introduction_screen
---
# Legal disclaimer
question: |
  Legal Information Disclaimer
subquestion: |
  **Please read carefully:**
  
  This tool helps you complete Ontario family law court forms. It does not provide legal advice.
  
  * The information you provide will be used to populate official court forms
  * You are responsible for the accuracy of all information
  * Consider consulting a lawyer for legal advice about your case
  * Court forms must be filed according to the Family Law Rules
  
  Do you understand and accept these terms?
field: legal_disclaimer_accepted
buttons:
  - "I understand and accept": True
  - "I do not accept": False
---"""
        
        # Generate questions for each section
        for section_name, section_fields in sections.items():
            if not section_fields:
                continue
            
            yaml_content += f"\n# {section_name.replace('_', ' ').title()} Questions\n"
            
            # Generate questions for first few fields in each section
            for field in section_fields[:5]:  # Limit to 5 per section for template
                var_name = self.generate_docassemble_variable(field, section_name)
                field_type = field.get('field_type', 'text')
                original_text = field.get('original_text', '')[:100]
                required = field.get('required', False)
                
                # Generate question text
                question_text = original_text if original_text else var_name.replace('_', ' ').title()
                
                yaml_content += f"""question: |
  {question_text}
fields:
  - "{question_text}": {var_name}"""
                
                # Add field attributes based on type
                if field_type == 'date':
                    yaml_content += "\n    datatype: date"
                elif field_type == 'currency':
                    yaml_content += "\n    datatype: currency\n    min: 0"
                elif field_type == 'email':
                    yaml_content += "\n    datatype: email"
                elif field_type == 'yesno':
                    yaml_content += "\n    datatype: yesnoradio"
                elif field_type == 'area':
                    yaml_content += "\n    input type: area\n    rows: 4"
                
                if required:
                    yaml_content += "\n    required: True"
                
                # Add validation if present
                validation = field.get('validation', {})
                if validation.get('maxlength'):
                    yaml_content += f"\n    maxlength: {validation['maxlength']}"
                
                yaml_content += "\n---\n"
        
        # Add review screen
        yaml_content += """# Review screen
question: |
  Review Your Information
subquestion: |
  Please review the information you have provided:
  
  % if 'applicant_information' in sections:
  **Applicant Information**
  
  * Name: ${applicant.name.full() if defined('applicant.name.first') else 'Not provided'}
  * Address: ${applicant.address.on_one_line() if defined('applicant.address.address') else 'Not provided'}
  % endif
  
  % if 'respondent_information' in sections:
  **Respondent Information**
  
  * Name: ${respondent.name.full() if defined('respondent.name.first') else 'Not provided'}
  * Address: ${respondent.address.on_one_line() if defined('respondent.address.address') else 'Not provided'}
  % endif
  
  % if 'court_information' in sections:
  **Court Information**
  
  * Court: ${court_info.name if defined('court_info.name') else 'Not provided'}
  * File Number: ${court_info.file_number if defined('court_info.file_number') else 'Not provided'}
  % endif
  
  Is this information correct?
continue button field: review_screen
continue button label: Yes, continue
---
# Final screen
event: final_screen
question: |
  Form Completed
subquestion: |
  Your form has been completed and is ready for download.
  
  **Next Steps:**
  
  1. Download your completed form
  2. Review the form carefully
  3. Sign the form where required
  4. File the form with the court
  5. Serve copies as required by the Family Law Rules
  
  **Important Reminders:**
  
  * Keep copies of all documents for your records
  * File your documents on time
  * Consider seeking legal advice if you have questions
  
attachment:
  - name: Completed Form
    filename: completed_form
    valid formats:
      - pdf
      - docx
    content: |
      [Your completed form will be attached here]
buttons:
  - Exit: exit
  - Start Over: restart
---
# Attachment generation (placeholder)
attachment:
  - name: ${form_name.replace('_', ' ').title()}
    filename: ${form_name}
    valid formats:
      - pdf
      - docx
    content: |
      [Form content will be generated here based on the Word template]
---"""
        
        return yaml_content
    
    def process_all_forms(self, analysis_file: str, output_dir: str):
        """Process all analyzed forms and generate docassemble YAML files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Load analysis results
        with open(analysis_file, 'r') as f:
            analysis = json.load(f)
        
        generated_files = []
        
        for form in analysis.get('forms_analyzed', []):
            form_name = form.get('form_name', 'unknown')
            
            # Skip non-Ontario family law forms
            if not any(term in form_name.lower() for term in ['form_', 'flr']):
                continue
            
            print(f"Generating docassemble YAML for: {form_name}")
            
            # Generate YAML content
            yaml_content = self.generate_yaml_content(form)
            
            # Save to file
            output_file = output_path / f"{form_name}_interview.yml"
            with open(output_file, 'w') as f:
                f.write(yaml_content)
            
            generated_files.append(output_file)
            print(f"  ✓ Generated: {output_file.name}")
        
        return generated_files

def main():
    """Main function"""
    import sys
    
    # Get paths
    if len(sys.argv) > 1:
        analysis_file = sys.argv[1]
    else:
        analysis_file = "form_analysis_output/complete_analysis.json"
    
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    else:
        output_dir = "docassemble_interviews"
    
    print("=" * 60)
    print("DOCASSEMBLE YAML GENERATOR")
    print("=" * 60)
    
    generator = DocassembleYAMLGenerator()
    
    # Generate YAML files
    generated = generator.process_all_forms(analysis_file, output_dir)
    
    print(f"\n✓ Generated {len(generated)} docassemble interview files")
    print(f"✓ Output directory: {Path(output_dir).absolute()}")

if __name__ == "__main__":
    main()