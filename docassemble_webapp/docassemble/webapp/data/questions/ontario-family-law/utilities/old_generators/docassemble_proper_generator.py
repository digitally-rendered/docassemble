#!/usr/bin/env python3
"""
Proper Docassemble YAML Generator
Creates YAML in the exact format docassemble expects
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
import re

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

class DocassembleProperGenerator:
    """Generate proper docassemble YAML interviews"""
    
    def __init__(self, form_config: FormConfiguration):
        self.config = form_config
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.field_counter = 0
        self.variable_map = {}
        
    def sanitize_variable_name(self, text: str) -> str:
        """Convert text to valid Python variable name"""
        # Remove special characters and convert to snake_case
        text = re.sub(r'[^\w\s]', '', str(text))
        text = re.sub(r'\s+', '_', text)
        text = text.lower().strip('_')
        
        # Ensure it starts with a letter
        if text and not text[0].isalpha():
            text = 'field_' + text
            
        # Truncate if too long
        if len(text) > 40:
            text = text[:40]
            
        # Make unique if needed
        if text in self.variable_map:
            self.field_counter += 1
            text = f"{text}_{self.field_counter}"
            
        self.variable_map[text] = True
            
        return text or f"field_{self.field_counter}"
    
    def sanitize_label(self, label: str) -> str:
        """Clean label for display"""
        # Remove problematic characters
        label = str(label).replace('\n', ' ').replace('\r', ' ')
        label = re.sub(r'\s+', ' ', label).strip()
        
        # Escape quotes
        label = label.replace('"', '\\"').replace("'", "\\'")
        
        # Truncate at word boundary if too long
        if len(label) > 60:
            label = label[:57] + '...'
            
        return label
    
    def generate_complete_interview(self, fields: List[Dict]) -> str:
        """Generate complete interview in docassemble format"""
        
        sections = []
        
        # 1. Metadata block
        metadata = f"""metadata:
  title: Form {self.config.form_number} - {self.config.form_title}
  short title: Form {self.config.form_number}
  description: Ontario Family Law Form {self.config.form_number}
  authors:
    - name: Ontario Family Law Forms System
  revision_date: {datetime.now().strftime('%Y-%m-%d')}"""
        sections.append(metadata)
        
        # 2. Include block
        include = """include:
  - docassemble.base:data/questions/basic-questions.yml"""
        sections.append(include)
        
        # 3. Objects block
        objects = """objects:
  - user: Individual
  - court: DAObject"""
        
        if self.config.requires_financial:
            objects += """
  - income: DAObject
  - expenses: DAObject"""
            
        sections.append(objects)
        
        # 4. Introduction question
        intro = f"""mandatory: True
question: |
  Form {self.config.form_number}: {self.config.form_title}
subquestion: |
  This interview will help you complete Form {self.config.form_number}.
  
  Please have the following information ready:
  * Court information
  * Personal information
continue button field: intro_shown"""
        sections.append(intro)
        
        # 5. Court information question
        if len(fields) > 0:
            court_q = """mandatory: True
question: |
  Court Information
fields:"""
            
            # Add up to 3 court-related fields
            court_count = 0
            for field in fields:
                field_label = str(field.get('field_label', '')).lower()
                if court_count < 3 and any(word in field_label for word in ['court', 'file', 'number', 'office']):
                    label = self.sanitize_label(field.get('field_label', 'Field'))
                    var_name = self.sanitize_variable_name(label)
                    field_type = field.get('field_type', 'text')
                    
                    court_q += f"\n  - {label}: court.{var_name}"
                    
                    if field_type == 'date':
                        court_q += "\n    datatype: date"
                    elif field_type == 'email':
                        court_q += "\n    datatype: email"
                    elif field_type == 'number':
                        court_q += "\n    datatype: number"
                    
                    court_count += 1
            
            # If no court fields found, add defaults
            if court_count == 0:
                court_q += """
  - Court File Number: court.file_number
  - Court Name: court.name
  - Court Office Address: court.address"""
            
            sections.append(court_q)
        
        # 6. User information question
        user_q = """mandatory: True
question: |
  Your Information
fields:
  - First Name: user.name.first
  - Last Name: user.name.last
  - Address: user.address.address
  - City: user.address.city
  - Province: user.address.state
    default: ON
  - Postal Code: user.address.postal_code"""
        sections.append(user_q)
        
        # 7. Financial information if needed
        if self.config.requires_financial:
            financial_q = """mandatory: True
question: |
  Financial Information
fields:
  - Monthly Income: income.monthly
    datatype: currency
    min: 0
  - Monthly Expenses: expenses.monthly
    datatype: currency
    min: 0"""
            sections.append(financial_q)
        
        # 8. Summary/complete screen
        summary = f"""mandatory: True
question: |
  Form {self.config.form_number} Complete
subquestion: |
  You have completed all required information for Form {self.config.form_number}.
  
  Click below to download your completed form.
buttons:
  - Exit: exit
  - Restart: restart
attachment:
  name: Form {self.config.form_number}
  filename: form_{self.config.form_number.lower()}
  description: |
    Form {self.config.form_number} - {self.config.form_title}
  content: |
    [Your form content will be generated here]"""
        sections.append(summary)
        
        # Join all sections with proper separators
        yaml_content = '\n---\n'.join(sections)
        
        return yaml_content

def generate_docassemble_proper_yaml(form_config: FormConfiguration, fields: List[Dict]) -> str:
    """Generate proper docassemble YAML interview"""
    generator = DocassembleProperGenerator(form_config)
    return generator.generate_complete_interview(fields)

def save_yaml_properly(yaml_content: str, output_path: str):
    """Save YAML with proper encoding"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(yaml_content)

if __name__ == "__main__":
    # Test the generator
    test_config = FormConfiguration(
        form_number="13",
        form_title="Financial Statement",
        form_type="financial",
        category="financial",
        url="",
        filename="form_13.pdf",
        requires_financial=True
    )
    
    test_fields = [
        {"field_label": "Court File Number", "field_type": "text", "required": True},
        {"field_label": "Name of Court", "field_type": "text", "required": True},
        {"field_label": "Your Full Legal Name", "field_type": "text", "required": True},
    ]
    
    yaml_content = generate_docassemble_proper_yaml(test_config, test_fields)
    save_yaml_properly(yaml_content, "test_form_13_proper.yml")
    
    print("Generated proper docassemble YAML")
    print("\nContent preview:")
    print(yaml_content[:500])