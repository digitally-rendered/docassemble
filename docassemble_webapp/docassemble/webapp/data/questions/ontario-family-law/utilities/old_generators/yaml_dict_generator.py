#!/usr/bin/env python3
"""
Proper YAML Generator using PyYAML library
Builds Python dictionaries and serializes them to valid YAML
"""

import yaml
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict

# Custom YAML representer for multiline strings
def literal_presenter(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, literal_presenter)

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

class ProperYAMLGenerator:
    """Generate valid docassemble YAML using proper YAML serialization"""
    
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
        if len(text) > 50:
            text = text[:50]
            
        # Make unique if needed
        if text in self.variable_map:
            self.field_counter += 1
            text = f"{text}_{self.field_counter}"
            
        self.variable_map[text] = True
            
        return text or f"field_{self.field_counter}"
    
    def generate_complete_interview(self, fields: List[Dict]) -> str:
        """Generate complete interview as proper YAML"""
        documents = []
        
        # 1. Metadata document
        documents.append(self._create_metadata())
        
        # 2. Configuration document
        documents.append(self._create_configuration())
        
        # 3. Objects document
        documents.append(self._create_objects())
        
        # 4. Introduction screen
        documents.append(self._create_intro_screen())
        
        # 5. Field questions
        field_questions = self._create_field_questions(fields)
        documents.extend(field_questions)
        
        # 6. Summary screen
        documents.append(self._create_summary_screen(fields))
        
        # Convert to YAML with proper formatting
        yaml_content = ""
        for doc in documents:
            if yaml_content:
                yaml_content += "\n---\n"
            yaml_content += yaml.dump(doc, 
                                     default_flow_style=False, 
                                     allow_unicode=True,
                                     sort_keys=False,
                                     width=120)
        
        return yaml_content
    
    def _create_metadata(self) -> Dict[str, Any]:
        """Create metadata as dictionary"""
        return {
            'metadata': {
                'title': f"Form {self.config.form_number} - {self.config.form_title}",
                'short title': f"Form {self.config.form_number}",
                'description': f"Ontario Family Law Form {self.config.form_number}\n"
                              f"This interview helps you complete the official Ontario court form.\n"
                              f"Generated on {self.timestamp}",
                'authors': [
                    {
                        'name': 'Ontario Family Law Forms System',
                        'organization': 'Automated Form Processing'
                    }
                ],
                'revision_date': datetime.now().strftime('%Y-%m-%d')
            }
        }
    
    def _create_configuration(self) -> Dict[str, Any]:
        """Create configuration settings"""
        return {
            'include': [
                'docassemble.base:data/questions/basic-questions.yml'
            ],
            'features': {
                'navigation': True,
                'progress bar': True,
                'progress bar method': 'stepped',
                'show progress bar percentage': True,
                'navigation back button': True,
                'question back button': True
            },
            'mandatory': True,
            'code': 'multi_user = True\nallow_cron = True'
        }
    
    def _create_objects(self) -> Dict[str, Any]:
        """Create objects definition"""
        objects = [
            'user: Individual',
            'opposing_party: Individual',
            'court: DAObject'
        ]
        
        if self.config.has_children_section:
            objects.append('children: DAList.using(object_type=Individual)')
            
        if self.config.requires_financial:
            objects.extend([
                'income: DAObject',
                'expenses: DAObject',
                'assets: DAObject',
                'debts: DAObject'
            ])
        
        return {
            'objects': objects
        }
    
    def _create_intro_screen(self) -> Dict[str, Any]:
        """Create introduction screen"""
        sections = ["Court information", "Personal information"]
        if self.config.requires_financial:
            sections.append("Financial information")
        if self.config.has_children_section:
            sections.append("Information about children")
            
        subquestion = f"""This interview will help you complete Form {self.config.form_number}.

You will need to provide:

{chr(10).join(f'* {section}' for section in sections)}

The interview will save your progress automatically."""
        
        return {
            'mandatory': True,
            'question': f"Form {self.config.form_number}: {self.config.form_title}",
            'subquestion': subquestion,
            'field': 'intro_shown',
            'continue button field': 'intro_shown'
        }
    
    def _create_field_questions(self, fields: List[Dict]) -> List[Dict[str, Any]]:
        """Create question blocks for fields"""
        questions = []
        
        # Group fields into sections
        sections = self._group_fields_by_section(fields)
        
        for section_name, section_fields in sections.items():
            if not section_fields:
                continue
            
            # Split into multiple screens if too many fields
            for i in range(0, len(section_fields), 8):
                chunk = section_fields[i:i+8]
                questions.append(self._create_section_question(section_name, chunk, i==0))
        
        return questions
    
    def _group_fields_by_section(self, fields: List[Dict]) -> Dict[str, List[Dict]]:
        """Group fields into logical sections"""
        sections = {
            "Court Information": [],
            "Your Information": [],
            "Other Party Information": [],
            "Financial Information": [],
            "Additional Information": []
        }
        
        for field in fields:
            field_label = str(field.get('field_label', '')).lower()
            
            if 'court' in field_label or 'file' in field_label:
                sections["Court Information"].append(field)
            elif any(word in field_label for word in ['your', 'applicant']):
                sections["Your Information"].append(field)
            elif any(word in field_label for word in ['respondent', 'other party', 'spouse']):
                sections["Other Party Information"].append(field)
            elif any(word in field_label for word in ['income', 'expense', 'asset', 'debt', 'financial', 'money']):
                sections["Financial Information"].append(field)
            else:
                sections["Additional Information"].append(field)
        
        # Remove empty sections
        return {k: v for k, v in sections.items() if v}
    
    def _create_section_question(self, section_name: str, fields: List[Dict], is_first: bool = True) -> Dict[str, Any]:
        """Create a question block for a section"""
        question_fields = []
        
        for field in fields:
            field_label = str(field.get('field_label', 'Field'))
            field_type = field.get('field_type', 'text')
            
            # Clean and truncate label
            field_label = field_label[:100].strip()
            
            # Generate unique variable name
            var_name = self.sanitize_variable_name(field_label)
            
            # Build field definition
            field_def = {
                'label': field_label,
                'field': var_name
            }
            
            # Add field attributes based on type
            if field_type == 'date':
                field_def['datatype'] = 'date'
            elif field_type == 'currency':
                field_def['datatype'] = 'currency'
                field_def['min'] = 0
            elif field_type == 'email':
                field_def['datatype'] = 'email'
            elif field_type == 'phone':
                field_def['datatype'] = 'text'
                field_def['hint'] = '(416) 555-1234'
            elif field_type == 'number':
                field_def['datatype'] = 'number'
            elif field_type == 'checkbox':
                field_def['datatype'] = 'yesno'
            elif field_type == 'postal_code':
                field_def['datatype'] = 'text'
                field_def['hint'] = 'M5H 2N2'
                
            if field.get('required'):
                field_def['required'] = True
                
            if field.get('help_text'):
                field_def['help'] = str(field['help_text'])[:200]
            
            question_fields.append(field_def)
        
        continuation = "" if is_first else " (continued)"
        
        return {
            'question': f"{section_name}{continuation}",
            'fields': question_fields
        }
    
    def _create_summary_screen(self, fields: List[Dict]) -> Dict[str, Any]:
        """Create summary screen"""
        subquestion = f"""## Your Form Has Been Completed

**Form Number:** {self.config.form_number}  
**Form Title:** {self.config.form_title}

You have provided all required information. You can now:

* Review your answers
* Download the completed form
* Print the form for filing

Click **Download** to get your completed form."""
        
        return {
            'mandatory': True,
            'question': f"Form {self.config.form_number} Complete",
            'subquestion': subquestion,
            'buttons': [
                {'Exit': 'exit'},
                {'Restart': 'restart'}
            ],
            'attachment': {
                'name': f"Form {self.config.form_number}",
                'filename': f"form_{self.config.form_number}",
                'description': f"Form {self.config.form_number} - {self.config.form_title}",
                'content': f"[Your form content will be generated here]"
            }
        }

def generate_valid_yaml(form_config: FormConfiguration, fields: List[Dict]) -> str:
    """Generate valid YAML interview"""
    generator = ProperYAMLGenerator(form_config)
    return generator.generate_complete_interview(fields)

def save_yaml_properly(yaml_content: str, output_path: str):
    """Save YAML with proper encoding"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(yaml_content)

if __name__ == "__main__":
    # Test the generator
    test_config = FormConfiguration(
        form_number="13",
        form_title="Financial Statement (Support Claims)",
        form_type="financial",
        category="financial",
        url="",
        filename="form_13.pdf",
        requires_financial=True
    )
    
    test_fields = [
        {"field_label": "Court File Number", "field_type": "text", "required": True},
        {"field_label": "Name of Court", "field_type": "text", "required": True},
        {"field_label": "Your Full Legal Name: First", "field_type": "text", "required": True},
        {"field_label": "Date of Birth", "field_type": "date", "required": True},
        {"field_label": "Monthly Income", "field_type": "currency", "required": True},
        {"field_label": "Email Address", "field_type": "email", "required": False},
    ]
    
    yaml_content = generate_valid_yaml(test_config, test_fields)
    save_yaml_properly(yaml_content, "test_form_13_proper.yml")
    
    print("Generated YAML using proper serialization")
    
    # Validate it loads correctly
    import yaml
    try:
        with open("test_form_13_proper.yml", 'r') as f:
            docs = list(yaml.safe_load_all(f))
        print(f"✓ Valid YAML with {len(docs)} documents")
    except Exception as e:
        print(f"✗ Invalid YAML: {e}")