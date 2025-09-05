#!/usr/bin/env python3
"""
Docassemble-safe YAML Generator
Creates properly formatted YAML that won't crash docassemble
"""

import yaml
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
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

class DocassembleSafeYAMLGenerator:
    """Generate docassemble-safe YAML interviews"""
    
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
        """Clean and truncate label for display"""
        # Remove special characters that might break YAML
        label = str(label).replace('\n', ' ').replace('\r', ' ')
        label = re.sub(r'\s+', ' ', label).strip()
        
        # Truncate at word boundary if too long
        if len(label) > 80:
            label = label[:77] + '...'
            
        return label
    
    def determine_field_type(self, field: Dict) -> str:
        """Determine appropriate docassemble datatype"""
        field_type = field.get('field_type', 'text')
        field_label = str(field.get('field_label', '')).lower()
        
        # Map field types to docassemble datatypes
        if field_type == 'date':
            return 'date'
        elif field_type == 'email':
            return 'email'
        elif field_type == 'number':
            return 'number'
        elif field_type == 'checkbox':
            return 'yesno'
        elif field_type == 'currency' or any(word in field_label for word in ['amount', 'income', 'expense', 'money', 'cost', 'price', '$']):
            return 'currency'
        elif field_type == 'phone' or 'phone' in field_label:
            return 'text'  # Use text with hint for phone numbers
        else:
            return 'text'
    
    def generate_complete_interview(self, fields: List[Dict]) -> str:
        """Generate complete interview as a single YAML document"""
        
        # Build the complete document structure
        doc = {
            'metadata': {
                'title': f"Form {self.config.form_number} - {self.config.form_title}",
                'short title': f"Form {self.config.form_number}",
                'description': f"Ontario Family Law Form {self.config.form_number}",
                'authors': [
                    {
                        'name': 'Ontario Family Law Forms System',
                        'organization': 'Automated Form Processing'
                    }
                ],
                'revision_date': datetime.now().strftime('%Y-%m-%d')
            },
            'include': [
                'docassemble.base:data/questions/basic-questions.yml'
            ],
            'features': {
                'navigation': True,
                'progress bar': True
            },
            'mandatory': True,
            'code': 'multi_user = True',
            'objects': [
                'user: Individual',
                'court: DAObject'
            ],
            'sections': [
                {'Introduction': 'intro_section'},
                {'Court Information': 'court_section'},
                {'Your Information': 'your_section'},
                {'Review': 'review_section'}
            ],
            'question order': [
                'intro_shown',
                'court_info_gathered',
                'user_info_gathered',
                'form_complete'
            ]
        }
        
        # Add financial objects if needed
        if self.config.requires_financial:
            doc['objects'].extend([
                'income: DAObject',
                'expenses: DAObject',
                'assets: DAObject',
                'debts: DAObject'
            ])
            doc['sections'].insert(3, {'Financial Information': 'financial_section'})
            doc['question order'].insert(3, 'financial_info_gathered')
        
        # Build questions list
        questions = []
        
        # Introduction screen
        questions.append({
            'id': 'intro_shown',
            'section': 'intro_section',
            'question': f"Form {self.config.form_number} - {self.config.form_title}",
            'subquestion': f"This interview will help you complete Form {self.config.form_number}.",
            'continue button field': 'intro_shown'
        })
        
        # Court information screen
        court_fields = []
        court_field_names = ['court file number', 'court name', 'court address', 'court office']
        for field in fields[:5]:  # Take first 5 fields as court info
            field_label = self.sanitize_label(field.get('field_label', 'Field'))
            var_name = self.sanitize_variable_name(field_label)
            
            field_def = {
                'label': field_label,
                'field': f"court.{var_name}"
            }
            
            # Only add datatype if not text
            datatype = self.determine_field_type(field)
            if datatype != 'text':
                field_def['datatype'] = datatype
                
            court_fields.append(field_def)
        
        if court_fields:
            questions.append({
                'id': 'court_info_gathered',
                'section': 'court_section',
                'question': 'Court Information',
                'fields': court_fields
            })
        
        # User information screen
        user_fields = []
        for field in fields[5:10]:  # Next 5 fields as user info
            field_label = self.sanitize_label(field.get('field_label', 'Field'))
            var_name = self.sanitize_variable_name(field_label)
            
            field_def = {
                'label': field_label,
                'field': f"user.{var_name}"
            }
            
            datatype = self.determine_field_type(field)
            if datatype != 'text':
                field_def['datatype'] = datatype
                
            user_fields.append(field_def)
        
        if user_fields:
            questions.append({
                'id': 'user_info_gathered',
                'section': 'your_section',
                'question': 'Your Information',
                'fields': user_fields
            })
        
        # Financial information if applicable
        if self.config.requires_financial and len(fields) > 10:
            financial_fields = []
            for field in fields[10:15]:  # Next 5 fields as financial info
                field_label = self.sanitize_label(field.get('field_label', 'Field'))
                var_name = self.sanitize_variable_name(field_label)
                
                field_def = {
                    'label': field_label,
                    'field': f"income.{var_name}"
                }
                
                datatype = self.determine_field_type(field)
                if datatype != 'text':
                    field_def['datatype'] = datatype
                    
                financial_fields.append(field_def)
            
            if financial_fields:
                questions.append({
                    'id': 'financial_info_gathered',
                    'section': 'financial_section',
                    'question': 'Financial Information',
                    'fields': financial_fields
                })
        
        # Summary screen
        questions.append({
            'id': 'form_complete',
            'section': 'review_section',
            'question': f"Form {self.config.form_number} Complete",
            'subquestion': "You have completed all required information.",
            'buttons': [
                'Exit: exit',
                'Restart: restart'
            ],
            'attachment': {
                'name': f"Form {self.config.form_number}",
                'filename': f"form_{self.config.form_number.lower()}",
                'description': f"Form {self.config.form_number} - {self.config.form_title}",
                'content': '[Your form content will be generated here]'
            }
        })
        
        # Add questions to document
        doc['questions'] = questions
        
        # Convert to YAML with safe settings
        yaml_content = yaml.dump(doc, 
                                default_flow_style=False, 
                                allow_unicode=True,
                                sort_keys=False,
                                width=120,
                                indent=2)
        
        # Clean up any problematic formatting
        yaml_content = yaml_content.replace('|-\n', '|\n')
        yaml_content = yaml_content.replace('|2-\n', '|\n')
        
        return yaml_content

def generate_docassemble_safe_yaml(form_config: FormConfiguration, fields: List[Dict]) -> str:
    """Generate docassemble-safe YAML interview"""
    generator = DocassembleSafeYAMLGenerator(form_config)
    return generator.generate_complete_interview(fields)

def save_yaml_safely(yaml_content: str, output_path: str):
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
        {"field_label": "Court Office Address", "field_type": "text", "required": True},
        {"field_label": "Your Full Legal Name", "field_type": "text", "required": True},
        {"field_label": "Date of Birth", "field_type": "date", "required": True},
        {"field_label": "Monthly Income", "field_type": "currency", "required": True},
        {"field_label": "Email Address", "field_type": "email", "required": False},
    ]
    
    yaml_content = generate_docassemble_safe_yaml(test_config, test_fields)
    save_yaml_safely(yaml_content, "test_form_13_safe.yml")
    
    print("Generated docassemble-safe YAML")
    
    # Validate it loads correctly
    try:
        with open("test_form_13_safe.yml", 'r') as f:
            doc = yaml.safe_load(f)
        print(f"✓ Valid YAML")
        print(f"  - Has {len(doc.get('questions', []))} questions")
        print(f"  - Has {len(doc.get('objects', []))} objects")
        print(f"  - Has {len(doc.get('sections', []))} sections")
    except Exception as e:
        print(f"✗ Invalid YAML: {e}")