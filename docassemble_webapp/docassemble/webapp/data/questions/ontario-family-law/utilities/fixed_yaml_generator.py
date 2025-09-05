#!/usr/bin/env python3
"""
Fixed YAML Generator for Docassemble
Creates valid single-document YAML files without multiple --- separators
"""

import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import re

class FixedYAMLGenerator:
    """Generate valid Docassemble YAML as a single document"""
    
    def __init__(self, form_config, field_mapper=None):
        self.form_config = form_config
        self.field_mapper = field_mapper
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.variable_counter = 0
        self.variable_map = {}
        
    def generate_complete_interview(self, fields: List[Dict]) -> str:
        """Generate complete interview as a single YAML document"""
        
        # Build complete document as list of blocks
        blocks = []
        
        # 1. Metadata block
        blocks.append({
            'metadata': {
                'title': f"{self.form_config.form_title}",
                'short title': f"Form {self.form_config.form_number}",
                'description': f"Ontario Family Law Form {self.form_config.form_number}: {self.form_config.form_title}\n\nThis interview uses docassemble standard objects for better data management.\nGenerated: {self.timestamp}",
                'authors': [
                    {
                        'name': 'Ontario Family Law Forms Automation System',
                        'organization': 'Fixed YAML Processing'
                    }
                ],
                'revision_date': datetime.now().strftime('%Y-%m-%d'),
                'form_number': str(self.form_config.form_number),
                'form_category': getattr(self.form_config, 'category', 'general'),
                'form_type': getattr(self.form_config, 'form_type', 'general'),
                'uses_standard_objects': True
            }
        })
        
        # 2. Include block
        blocks.append({
            'include': [
                'docassemble.base:data/questions/basic-questions.yml'
            ]
        })
        
        # 3. Features block
        blocks.append({
            'features': {
                'navigation': True,
                'progress bar': True,
                'progress bar method': 'stepped',
                'show progress bar percentage': True,
                'navigation back button': True,
                'question back button': True,
                'review button': True,
                'hide navbar': False,
                'hide standard menu': False
            }
        })
        
        # 4. Objects block
        blocks.append({
            'objects': [
                {'applicant': 'Individual'},
                {'respondent': 'Individual'},
                {'court_info': 'DAObject'},
                {'children': 'DAList.using(object_type=Individual)'},
                {'assets': 'DAList'},
                {'debts': 'DAList'},
                {'income_sources': 'DAList'},
                {'expenses': 'DAList'}
            ]
        })
        
        # 5. Mandatory block (controls flow)
        blocks.append({
            'mandatory': True,
            'code': 'form_intro_seen\napplicant.name.first\nrespondent.name.first\nform_complete'
        })
        
        # 6. Introduction question
        blocks.append({
            'question': f"Form {self.form_config.form_number} - {self.form_config.form_title}",
            'subquestion': "This interview will help you complete the official Ontario family law form.\n\nYou will need:\n- Personal information for all parties\n- Court case information (if applicable)\n- Financial information (if applicable)",
            'continue button field': 'form_intro_seen',
            'continue button label': 'Start Interview'
        })
        
        # 7. Generate field questions
        field_questions = self._generate_field_questions(fields)
        blocks.extend(field_questions)
        
        # 8. Review block
        review_fields = []
        for field in fields[:10]:  # Limit to first 10 fields for review
            field_label = field.get('field_label', 'Field')
            field_var = self._create_variable_name(field_label)
            review_fields.append({
                'label': field_label,
                'field': field_var
            })
        
        if review_fields:
            blocks.append({
                'review': [{'note': '### Review Your Information'}] + review_fields,
                'question': 'Review Your Answers',
                'subquestion': 'Please review your information. Click any item to edit.'
            })
        
        # 9. Completion screen
        blocks.append({
            'event': 'form_complete',
            'question': f"Form {self.form_config.form_number} Complete",
            'subquestion': "Your form is ready.\n\n**Next Steps:**\n1. Download your completed form\n2. Review all information carefully\n3. Print and sign where required\n4. File with the appropriate court",
            'buttons': [
                {'Exit': 'exit'},
                {'Start Over': 'restart'}
            ]
        })
        
        # 10. Code block for validation functions
        blocks.append({
            'code': self._generate_validation_code()
        })
        
        # Convert to YAML with proper formatting
        yaml_content = self._blocks_to_yaml(blocks)
        return yaml_content
    
    def _generate_field_questions(self, fields: List[Dict]) -> List[Dict]:
        """Generate question blocks for fields"""
        questions = []
        
        # Group related fields together
        grouped_fields = []
        current_group = []
        
        for field in fields:
            if len(current_group) < 5:  # Group up to 5 fields per screen
                current_group.append(field)
            else:
                grouped_fields.append(current_group)
                current_group = [field]
        
        if current_group:
            grouped_fields.append(current_group)
        
        # Create questions for each group
        for i, group in enumerate(grouped_fields):
            if not group:
                continue
                
            question = {
                'question': f"Information - Part {i + 1}",
                'fields': []
            }
            
            for field in group:
                field_label = field.get('field_label', 'Field')
                field_var = self._create_variable_name(field_label)
                field_type = self._determine_field_type(field_label, field.get('field_type'))
                
                field_def = {'label': field_label, 'field': field_var}
                
                # Add datatype if not text
                if field_type != 'text':
                    field_def['datatype'] = field_type
                
                # Add requirement if specified
                if field.get('required', '').lower() == 'true':
                    field_def['required'] = True
                    
                # Add validation if applicable
                if 'email' in field_label.lower():
                    field_def['datatype'] = 'email'
                elif 'phone' in field_label.lower():
                    field_def['hint'] = '(xxx) xxx-xxxx'
                elif 'postal' in field_label.lower() or 'zip' in field_label.lower():
                    field_def['hint'] = 'A1A 1A1'
                    
                question['fields'].append(field_def)
            
            questions.append(question)
        
        return questions
    
    def _create_variable_name(self, label: str) -> str:
        """Create valid Python variable name from label"""
        if not label:
            self.variable_counter += 1
            return f"field_{self.variable_counter}"
        
        # Check if we've already mapped this label
        if label in self.variable_map:
            return self.variable_map[label]
        
        # Clean the label
        text = re.sub(r'[^\w\s]', '', label.lower())
        text = re.sub(r'\s+', '_', text)
        text = re.sub(r'_+', '_', text).strip('_')
        
        # Ensure it starts with a letter
        if text and not text[0].isalpha():
            text = 'field_' + text
        
        if not text:
            self.variable_counter += 1
            text = f"field_{self.variable_counter}"
        
        # Ensure uniqueness
        if text in self.variable_map.values():
            self.variable_counter += 1
            text = f"{text}_{self.variable_counter}"
        
        self.variable_map[label] = text
        return text
    
    def _determine_field_type(self, label: str, field_type: str = None) -> str:
        """Determine appropriate Docassemble field type"""
        label_lower = label.lower()
        
        if field_type:
            type_lower = field_type.lower()
            if 'date' in type_lower:
                return 'date'
            elif 'number' in type_lower or 'amount' in type_lower:
                return 'currency' if 'amount' in type_lower or '$' in label else 'number'
            elif 'email' in type_lower:
                return 'email'
            elif 'phone' in type_lower:
                return 'text'  # Use text with hint for phone
            elif 'yes' in type_lower or 'no' in type_lower or 'bool' in type_lower:
                return 'yesno'
        
        # Check label for hints
        if 'email' in label_lower:
            return 'email'
        elif 'date' in label_lower or 'born' in label_lower:
            return 'date'
        elif 'amount' in label_lower or 'income' in label_lower or 'expense' in label_lower or '$' in label:
            return 'currency'
        elif 'number' in label_lower or 'count' in label_lower or 'age' in label_lower:
            return 'number'
        elif 'phone' in label_lower or 'fax' in label_lower:
            return 'text'  # Use text with hint
        elif any(word in label_lower for word in ['yes', 'no', 'do you', 'are you', 'is this', 'have you']):
            return 'yesno'
        
        return 'text'
    
    def _generate_validation_code(self) -> str:
        """Generate validation functions"""
        return """# Validation functions
def validate_ontario_postal_code(postal_code):
    import re
    if not postal_code:
        return True
    pattern = r'^[A-Z]\\d[A-Z]\\s?\\d[A-Z]\\d$'
    return bool(re.match(pattern, postal_code.upper()))

def validate_phone_number(phone):
    import re
    if not phone:
        return True
    pattern = r'^[\\d\\s\\(\\)\\-\\.\\+]+$'
    return bool(re.match(pattern, phone))

def format_currency(amount):
    try:
        return f"${float(amount):,.2f}"
    except:
        return "$0.00"
"""
    
    def _blocks_to_yaml(self, blocks: List[Dict]) -> str:
        """Convert blocks to properly formatted YAML as single document"""
        # Convert each block to YAML and collect
        yaml_parts = []
        
        for block in blocks:
            yaml_part = yaml.dump(
                block,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                width=1000
            ).strip()
            yaml_parts.append(yaml_part)
        
        # Join blocks with single line breaks (no document separators!)
        # Only one --- at the beginning for Docassemble
        return '---\n' + '\n'.join(yaml_parts) + '\n'

def fix_existing_yaml_files(input_dir: str, output_dir: str):
    """Fix existing YAML files in a directory"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    fixed_count = 0
    error_count = 0
    
    for yaml_file in input_path.glob("*.yml"):
        try:
            print(f"Fixing {yaml_file.name}...")
            
            # Read the file content
            with open(yaml_file, 'r') as f:
                content = f.read()
            
            # Parse all YAML documents
            documents = list(yaml.safe_load_all(content))
            
            # Merge documents into single structure
            merged_doc = {}
            for doc in documents:
                if doc:
                    merged_doc.update(doc)
            
            # Write as single document
            output_file = output_path / yaml_file.name
            with open(output_file, 'w') as f:
                yaml.dump(
                    merged_doc,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                    width=1000
                )
            
            fixed_count += 1
            print(f"  ✓ Fixed: {output_file}")
            
        except Exception as e:
            error_count += 1
            print(f"  ✗ Error fixing {yaml_file.name}: {e}")
    
    print(f"\nFixed {fixed_count} files, {error_count} errors")
    return fixed_count, error_count

if __name__ == "__main__":
    # Fix existing YAML files
    input_dir = "workflow_output/yaml_interviews"
    output_dir = "workflow_output/fixed_yaml_interviews"
    
    fix_existing_yaml_files(input_dir, output_dir)