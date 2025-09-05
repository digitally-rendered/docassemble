#!/usr/bin/env python3
"""
True Data-Driven Interview Generator
Actually generates interviews from parsed form field data
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TrueDataDrivenGenerator:
    """Generate interviews directly from parsed form data"""
    
    def __init__(self):
        self.output_dir = Path('data_driven_interviews')
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_from_parsed_data(self, form_number: str = "13"):
        """Generate interview from actual parsed form data"""
        
        # Try multiple locations for parsed data
        parsed_files = [
            f'validation_results/form_{form_number}_-_financial_statement_support_flr-13-may21-en-fil_unified_results.json',
            f'parsed_forms/form_{form_number}_fields.json',
            f'workflow_output/enhanced_parsed_forms/form_{form_number}_fields.json',
            f'parser_results/parser_results/unified/form_{form_number}_-_financial_statement_support_flr-13-may21-en-fil_9cf6c647.json'
        ]
        
        parsed_data = None
        for filepath in parsed_files:
            if Path(filepath).exists():
                with open(filepath, 'r') as f:
                    parsed_data = json.load(f)
                    logger.info(f"Loaded parsed data from: {filepath}")
                    break
        
        if not parsed_data:
            logger.error(f"No parsed data found for Form {form_number}")
            return False
        
        # Extract fields
        if isinstance(parsed_data, dict) and 'fields' in parsed_data:
            fields = parsed_data['fields']
        elif isinstance(parsed_data, list):
            fields = parsed_data
        else:
            logger.error(f"Unexpected data structure in parsed file")
            return False
        
        logger.info(f"Found {len(fields)} fields in parsed data")
        
        # Generate the interview YAML
        yaml_content = self._generate_yaml_from_fields(fields, form_number)
        
        # Save the generated interview
        output_file = self.output_dir / f'form_{form_number}_true_data_driven.yml'
        with open(output_file, 'w') as f:
            f.write(yaml_content)
        
        logger.info(f"Generated: {output_file}")
        return True
    
    def _sanitize_field_name(self, field_name: str) -> str:
        """Convert field name to valid Docassemble variable name"""
        # Remove special characters and convert to snake_case
        name = re.sub(r'[^a-zA-Z0-9_]', '_', field_name)
        name = re.sub(r'_+', '_', name)  # Remove multiple underscores
        name = name.strip('_').lower()
        
        # Ensure it doesn't start with a number
        if name and name[0].isdigit():
            name = 'field_' + name
        
        # Truncate if too long
        if len(name) > 50:
            name = name[:50]
        
        return name if name else 'field_unknown'
    
    def _determine_field_type(self, field: Dict) -> str:
        """Determine Docassemble datatype from parsed field info"""
        field_type = field.get('field_type', '').lower()
        field_label = field.get('field_label', '').lower()
        field_name = field.get('field_name', '').lower()
        
        # Check for specific field types
        if 'date' in field_type or 'date' in field_label or 'birth' in field_name:
            return 'date'
        elif 'email' in field_type or 'email' in field_label:
            return 'email'
        elif 'phone' in field_type or 'phone' in field_label:
            return 'phone'
        elif 'currency' in field_type or 'amount' in field_label or 'income' in field_label or 'expense' in field_label:
            return 'currency'
        elif 'checkbox' in field_type:
            return 'yesno'
        elif 'radio' in field_type or field.get('options'):
            return 'radio'
        elif 'number' in field_type:
            return 'number'
        else:
            return 'text'
    
    def _group_fields_into_screens(self, fields: List[Dict]) -> List[Dict]:
        """Group related fields into logical screens"""
        screens = []
        
        # Group by context/table/section
        current_screen = {
            'title': 'Form Information',
            'fields': []
        }
        
        for field in fields:
            # Skip fields with overly complex names
            field_name = field.get('field_name', '')
            if len(field_name) > 100 or field_name.count('_') > 10:
                continue
            
            # Get context clues
            context = field.get('field_context', '')
            table_name = field.get('table_name', '')
            field_label = field.get('field_label', '')
            
            # Create clean field representation
            clean_field = {
                'original': field,
                'var_name': self._sanitize_field_name(field_name),
                'label': self._clean_label(field_label),
                'datatype': self._determine_field_type(field),
                'required': field.get('required', False),
                'options': field.get('options', None)
            }
            
            # Skip if label is too repetitive or unclear
            if clean_field['label'].count(clean_field['label'].split()[0] if clean_field['label'] else '') > 3:
                continue
            
            # Group by table or create new screen every 10 fields
            if table_name and table_name != current_screen.get('table'):
                # Save current screen if it has fields
                if current_screen['fields']:
                    screens.append(current_screen)
                # Start new screen for new table
                current_screen = {
                    'title': self._clean_label(table_name),
                    'table': table_name,
                    'fields': [clean_field]
                }
            elif len(current_screen['fields']) >= 10:
                # Save current screen
                screens.append(current_screen)
                # Start new screen
                current_screen = {
                    'title': f'Form Information (continued)',
                    'fields': [clean_field]
                }
            else:
                current_screen['fields'].append(clean_field)
        
        # Add last screen if it has fields
        if current_screen['fields']:
            screens.append(current_screen)
        
        return screens
    
    def _clean_label(self, label: str) -> str:
        """Clean up field labels"""
        if not label:
            return "Field"
        
        # Remove excessive repetition
        words = label.split()
        cleaned = []
        prev_word = None
        for word in words:
            if word != prev_word:
                cleaned.append(word)
                prev_word = word
        
        result = ' '.join(cleaned)
        
        # Capitalize first letter
        if result:
            result = result[0].upper() + result[1:]
        
        # Truncate if too long
        if len(result) > 100:
            result = result[:97] + "..."
        
        return result or "Field"
    
    def _generate_yaml_from_fields(self, fields: List[Dict], form_number: str) -> str:
        """Generate complete YAML from parsed fields"""
        
        # Group fields into screens
        screens = self._group_fields_into_screens(fields)
        
        logger.info(f"Grouped {len(fields)} fields into {len(screens)} screens")
        
        # Start building YAML
        yaml = f"""---
metadata:
  title: Form {form_number} - Auto-Generated from Parsed Data
  short title: Form {form_number}
  description: |
    This interview was automatically generated from parsed form fields.
    Total fields: {len(fields)}
    Total screens: {len(screens)}
---
include:
  - docassemble.base:data/questions/basic-questions.yml
---
features:
  progress bar: True
  question back button: True
  debug: True
---
# Objects for form data
objects:
  - form_data: DAObject
---
# Initialize form data
initial: True
code: |
  form_data = DAObject()
---
mandatory: True
code: |
  intro_screen
"""
        
        # Add screens to mandatory flow
        for i, screen in enumerate(screens):
            yaml += f"\n  screen_{i}_complete"
        
        yaml += "\n  final_screen\n---\n"
        
        # Add intro screen
        yaml += """question: |
  Form """ + form_number + """ - Introduction
subquestion: |
  This interview will collect information for Form """ + form_number + """.
  
  The form has been automatically parsed and contains """ + str(len(screens)) + """ sections.
  
  Click Continue to begin.
continue button field: intro_screen
---
"""
        
        # Generate each screen
        for i, screen in enumerate(screens):
            yaml += self._generate_screen_yaml(screen, i)
        
        # Add final screen
        yaml += self._generate_summary_yaml(screens)
        
        return yaml
    
    def _generate_screen_yaml(self, screen: Dict, screen_num: int) -> str:
        """Generate YAML for a single screen"""
        
        yaml = f"""question: |
  {screen['title']}
"""
        
        if screen.get('table'):
            yaml += f"subquestion: |\n  Information from {screen['table']}\n"
        
        yaml += "fields:\n"
        
        for field in screen['fields']:
            var_name = f"form_data.{field['var_name']}"
            label = field['label']
            datatype = field['datatype']
            
            # Basic field definition
            yaml += f'  - "{label}": {var_name}\n'
            
            # Add datatype if not text
            if datatype != 'text':
                if datatype == 'radio' and field.get('options'):
                    yaml += f"    datatype: radio\n"
                    yaml += f"    choices:\n"
                    for option in field['options'][:10]:  # Limit to 10 options
                        yaml += f"      - {option}\n"
                else:
                    yaml += f"    datatype: {datatype}\n"
            
            # Add required flag
            if field['required']:
                yaml += "    required: True\n"
            else:
                yaml += "    required: False\n"
            
            # Add min value for currency
            if datatype == 'currency':
                yaml += "    min: 0\n"
        
        yaml += f"continue button field: screen_{screen_num}_complete\n---\n"
        
        return yaml
    
    def _generate_summary_yaml(self, screens: List[Dict]) -> str:
        """Generate summary screen showing all collected data"""
        
        yaml = """event: final_screen
question: |
  Form Summary
subquestion: |
  Here is the information you provided:
  
"""
        
        for screen in screens:
            if not screen['fields']:
                continue
                
            yaml += f"  **{screen['title']}:**\n  \n"
            
            for field in screen['fields'][:20]:  # Limit display to prevent huge summary
                var_name = f"form_data.{field['var_name']}"
                label = field['label']
                
                yaml += f"  % if defined('{var_name}'):\n"
                
                if field['datatype'] == 'currency':
                    yaml += f"  - {label}: ${{{{ currency({var_name}) }}}}\n"
                else:
                    yaml += f"  - {label}: ${{{{ {var_name} }}}}\n"
                    
                yaml += "  % endif\n"
            
            yaml += "  \n"
        
        yaml += """buttons:
  - Exit: exit
  - Restart: restart
---"""
        
        return yaml


def main():
    """Run the true data-driven generator"""
    generator = TrueDataDrivenGenerator()
    
    print("=" * 60)
    print("TRUE DATA-DRIVEN INTERVIEW GENERATION")
    print("=" * 60)
    print("Generating from actual parsed form data...")
    
    if generator.generate_from_parsed_data("13"):
        print("\n✅ Successfully generated Form 13 from parsed data")
        print("\nAccess the interview at:")
        print("  /interview?i=docassemble.webapp:ontario-family-law/utilities/data_driven_interviews/form_13_true_data_driven.yml")
    else:
        print("\n❌ Failed to generate interview")


if __name__ == "__main__":
    main()