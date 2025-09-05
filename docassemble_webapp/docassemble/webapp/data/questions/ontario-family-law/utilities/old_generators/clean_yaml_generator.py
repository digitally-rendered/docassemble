#!/usr/bin/env python3
"""
Clean YAML Generator for Docassemble
Generates crash-free YAML with only actual fillable fields
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

class CleanYAMLGenerator:
    """Generate clean, crash-free docassemble YAML"""
    
    # Standard Ontario family law form fields
    STANDARD_FIELDS = {
        'court': [
            ('Court File Number', 'file_number', 'text', True),
            ('Court Name', 'name', 'text', True),
            ('Court Office Address', 'address', 'text', False),
        ],
        'applicant': [
            ('First Name', 'name.first', 'text', True),
            ('Last Name', 'name.last', 'text', True),
            ('Date of Birth', 'birthdate', 'date', False),
            ('Address', 'address.address', 'text', False),
            ('City', 'address.city', 'text', False),
            ('Province', 'address.state', 'text', False),
            ('Postal Code', 'address.postal_code', 'text', False),
            ('Phone Number', 'phone_number', 'text', False),
            ('Email', 'email', 'email', False),
        ],
        'respondent': [
            ('First Name', 'name.first', 'text', True),
            ('Last Name', 'name.last', 'text', True),
            ('Address', 'address.address', 'text', False),
        ],
        'marriage': [
            ('Date of Marriage', 'date', 'date', False),
            ('Place of Marriage', 'place', 'text', False),
            ('Date of Separation', 'separation_date', 'date', False),
        ],
        'children': [
            ('Number of Children', 'number', 'integer', False),
            ('Child Name', 'name', 'text', False),
            ('Child Date of Birth', 'birthdate', 'date', False),
        ],
        'financial': [
            ('Monthly Income', 'monthly_income', 'currency', False),
            ('Monthly Expenses', 'monthly_expenses', 'currency', False),
            ('Total Assets', 'total_assets', 'currency', False),
            ('Total Debts', 'total_debts', 'currency', False),
        ],
    }
    
    def __init__(self, form_config: FormConfiguration):
        self.config = form_config
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
    def sanitize_variable_name(self, text: str) -> str:
        """Create a valid Python variable name"""
        # Remove all non-alphanumeric characters
        text = re.sub(r'[^\w]', '_', str(text))
        # Remove multiple underscores
        text = re.sub(r'_+', '_', text)
        # Convert to lowercase
        text = text.lower().strip('_')
        # Ensure it starts with a letter
        if text and not text[0].isalpha():
            text = 'field_' + text
        # Truncate if too long
        if len(text) > 30:
            text = text[:30]
        return text or 'field'
    
    def generate_clean_interview(self, extracted_fields: List[Dict] = None) -> str:
        """Generate clean docassemble YAML"""
        
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
        
        if self.config.has_children_section:
            objects += "\n  - children: DAList.using(object_type=Individual)"
        
        if self.config.requires_financial:
            objects += "\n  - financial: DAObject"
            
        if 'marriage' in self.config.category or 'divorce' in self.config.form_type:
            objects += "\n  - marriage: DAObject"
            
        sections.append(objects)
        
        # 4. Introduction
        intro = f"""mandatory: True
question: |
  Form {self.config.form_number}: {self.config.form_title[:60]}
subquestion: |
  This interview will help you complete Form {self.config.form_number}.
  
  Please have your information ready.
continue button field: intro_shown"""
        sections.append(intro)
        
        # 5. Court Information
        court_fields = self._get_fields_for_section('court')
        court_section = """mandatory: True
question: |
  Court Information
fields:"""
        for label, var, dtype, required in court_fields:
            court_section += f"\n  - {label}: court.{var}"
            if dtype != 'text':
                court_section += f"\n    datatype: {dtype}"
            if required:
                court_section += "\n    required: True"
        sections.append(court_section)
        
        # 6. Applicant Information
        applicant_fields = self._get_fields_for_section('applicant')
        applicant_section = """mandatory: True
question: |
  Applicant Information
fields:"""
        for label, var, dtype, required in applicant_fields[:6]:  # Limit fields
            applicant_section += f"\n  - {label}: applicant.{var}"
            if dtype != 'text':
                applicant_section += f"\n    datatype: {dtype}"
            if required:
                applicant_section += "\n    required: True"
            if 'province' in var.lower():
                applicant_section += "\n    default: ON"
        sections.append(applicant_section)
        
        # 7. Respondent Information
        respondent_section = """mandatory: True
question: |
  Respondent Information
fields:"""
        respondent_fields = self._get_fields_for_section('respondent')
        for label, var, dtype, required in respondent_fields[:4]:  # Limit fields
            respondent_section += f"\n  - {label}: respondent.{var}"
            if dtype != 'text':
                respondent_section += f"\n    datatype: {dtype}"
            if required:
                respondent_section += "\n    required: True"
        sections.append(respondent_section)
        
        # 8. Additional sections based on form type
        if 'divorce' in self.config.form_type or 'marriage' in self.config.category:
            marriage_section = """mandatory: True
question: |
  Marriage Information
fields:
  - Date of Marriage: marriage.date
    datatype: date
  - Place of Marriage: marriage.place
  - Date of Separation: marriage.separation_date
    datatype: date"""
            sections.append(marriage_section)
        
        if self.config.requires_financial:
            financial_section = """mandatory: True
question: |
  Financial Information
fields:
  - Monthly Income: financial.monthly_income
    datatype: currency
    min: 0
  - Monthly Expenses: financial.monthly_expenses
    datatype: currency
    min: 0"""
            sections.append(financial_section)
        
        # 9. Review screen
        review = f"""mandatory: True
question: |
  Review Your Information
review:
  - Edit: applicant.name.first
    button: |
      **Applicant:** ${{applicant.name.first}} ${{applicant.name.last}}
  - Edit: respondent.name.first
    button: |
      **Respondent:** ${{respondent.name.first}} ${{respondent.name.last}}
  - Edit: court.file_number
    button: |
      **Court File:** ${{court.file_number}}
continue button field: review_complete"""
        sections.append(review)
        
        # 10. Final screen
        final = f"""mandatory: True
question: |
  Form {self.config.form_number} Complete
subquestion: |
  Your form has been completed.
  
  You can now download or print your form.
buttons:
  - Exit: exit
  - Restart: restart
attachment:
  name: Form {self.config.form_number}
  filename: form_{self.config.form_number.lower()}
  description: |
    Ontario Family Law Form {self.config.form_number}
  content: |
    % if defined('applicant.name.first'):
    **Applicant:** ${{applicant.name.first}} ${{applicant.name.last}}
    % endif
    % if defined('respondent.name.first'):
    **Respondent:** ${{respondent.name.first}} ${{respondent.name.last}}
    % endif
    % if defined('court.file_number'):
    **Court File Number:** ${{court.file_number}}
    % endif"""
        sections.append(final)
        
        # Join sections with proper separators
        return '\n---\n'.join(sections)
    
    def _get_fields_for_section(self, section: str) -> List[tuple]:
        """Get standard fields for a section"""
        return self.STANDARD_FIELDS.get(section, [])

def generate_clean_yaml(form_config: FormConfiguration, extracted_fields: List[Dict] = None) -> str:
    """Generate clean docassemble YAML"""
    generator = CleanYAMLGenerator(form_config)
    return generator.generate_clean_interview(extracted_fields)

if __name__ == "__main__":
    # Test with different form types
    test_configs = [
        FormConfiguration(
            form_number="8A",
            form_title="Application for Divorce",
            form_type="application",
            category="divorce",
            url="",
            filename="form_8a.docx",
            requires_financial=False
        ),
        FormConfiguration(
            form_number="13",
            form_title="Financial Statement",
            form_type="financial",
            category="support",
            url="",
            filename="form_13.docx",
            requires_financial=True
        ),
    ]
    
    for config in test_configs:
        yaml_content = generate_clean_yaml(config)
        filename = f"test_clean_form_{config.form_number}.yml"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        print(f"Generated {filename}")
        print(f"  - Form: {config.form_number}")
        print(f"  - Title: {config.form_title}")
        print(f"  - Has financial: {config.requires_financial}")
        print()