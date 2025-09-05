#!/usr/bin/env python3
"""
Real Data Generator - Uses actual parsed Form 13 fields
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RealDataGenerator:
    """Generate Form 13 from real parsed data"""
    
    def __init__(self):
        self.output_dir = Path('data_driven_interviews')
        self.output_dir.mkdir(exist_ok=True)
        
        # Load enhanced parsed fields
        self.fields = self._load_fields()
        self.domain_mappings = self._load_domain_mappings()
        
    def _load_fields(self) -> List[Dict]:
        """Load the enhanced parsed fields"""
        path = Path('workflow_output/enhanced_parsed_forms/form_13_fields.json')
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        return []
    
    def _load_domain_mappings(self) -> Dict:
        """Load domain mappings"""
        path = Path('workflow_output/domain_mappings.json')
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        return {}
    
    def generate_real_form_13(self):
        """Generate Form 13 using actual parsed fields"""
        
        # Find the income fields (indices 341-354 from our search)
        income_fields = []
        expense_fields = []
        court_fields = []
        party_fields = []
        
        for i, field in enumerate(self.fields):
            label = field.get('field_label', '').lower()
            name = field.get('field_name', '').lower()
            
            # Income fields (based on our search results)
            if i >= 341 and i <= 354:
                income_fields.append(field)
            # Look for expense fields  
            elif 'expense' in label or 'housing' in label or 'food' in label:
                expense_fields.append(field)
            # Court info
            elif 'court' in label or 'court' in name:
                court_fields.append(field)
            # Party info
            elif i < 50 and ('name' in label or 'address' in label):
                party_fields.append(field)
        
        logger.info(f"Found: {len(income_fields)} income, {len(expense_fields)} expense, "
                   f"{len(court_fields)} court, {len(party_fields)} party fields")
        
        # Generate YAML
        yaml = self._generate_yaml_from_real_fields(
            income_fields, expense_fields, court_fields, party_fields
        )
        
        # Save the file
        output_file = self.output_dir / 'form_13_real_data.yml'
        with open(output_file, 'w') as f:
            f.write(yaml)
        
        logger.info(f"Generated: {output_file}")
        return True
    
    def _generate_yaml_from_real_fields(self, income_fields, expense_fields, 
                                        court_fields, party_fields) -> str:
        """Generate YAML using the actual parsed fields"""
        
        yaml = """---
metadata:
  title: Form 13 - Financial Statement (Real Data)
  short title: Form 13 Real
  description: Generated from actual parsed Form 13 fields
---
include:
  - docassemble.base:data/questions/basic-questions.yml
---
features:
  progress bar: True
  question back button: True
---
objects:
  - applicant: Individual
  - financial_data: DAObject
---
mandatory: True
code: |
  intro_screen
  court_info_collected
  applicant.name.first
  income_collected
  show_summary
---
question: |
  Form 13 - Financial Statement
subquestion: |
  This interview uses real fields parsed from Form 13.
continue button field: intro_screen
---
question: |
  Court Information
fields:"""
        
        # Add court fields
        if court_fields:
            for field in court_fields[:3]:  # First 3 court fields
                var_name = self._clean_var_name(field['field_name'])
                label = self._clean_label(field['field_label'])
                if label and var_name:
                    yaml += f'\n  - "{label}": financial_data.{var_name}'
                    yaml += '\n    required: False'
        else:
            yaml += '\n  - "Court File Number": financial_data.court_file_number'
            yaml += '\n    required: False'
        
        yaml += """
continue button field: court_info_collected
---
question: |
  Your Information
fields:
  - First Name: applicant.name.first
    required: True
  - Last Name: applicant.name.last
    required: True
  - Address: applicant.address.address
    required: False
  - City: applicant.address.city
    required: False
  - Province: applicant.address.state
    default: ON
  - Postal Code: applicant.address.zip
    required: False
---
question: |
  Monthly Income
subquestion: |
  Enter your monthly income from each source. Leave blank if not applicable.
fields:"""
        
        # Add real income fields
        for field in income_fields:
            var_name = self._clean_var_name(field['field_name'])
            label = self._extract_income_label(field['field_label'])
            
            if label and var_name:
                yaml += f'\n  - "{label}": financial_data.{var_name}'
                yaml += '\n    datatype: currency'
                yaml += '\n    min: 0'
                yaml += '\n    required: False'
                yaml += '\n    default: 0'
        
        yaml += """
continue button field: income_collected
---
code: |
  # Calculate total income
  income_fields = ["""
        
        # List the income field names for calculation
        income_var_names = []
        for field in income_fields:
            var_name = self._clean_var_name(field['field_name'])
            if var_name:
                income_var_names.append(f"'financial_data.{var_name}'")
        
        if income_var_names:
            yaml += ',\n    '.join(income_var_names[:10])  # Limit to 10 for simplicity
        
        yaml += """
  ]
  
  total_income = 0
  for field_name in income_fields:
    if defined(field_name):
      value = eval(field_name)
      if value:
        total_income += value
---
event: show_summary
question: |
  Financial Statement Summary
subquestion: |
  **Your Information:**
  - Name: ${ applicant.name.full() }
  % if defined('applicant.address.address'):
  - Address: ${ applicant.address.on_one_line() }
  % endif
  
  **Monthly Income:**"""
        
        # Show income fields in summary
        for field in income_fields[:10]:  # First 10 income fields
            var_name = self._clean_var_name(field['field_name'])
            label = self._extract_income_label(field['field_label'])
            
            if label and var_name:
                yaml += f"""
  % if defined('financial_data.{var_name}') and financial_data.{var_name} > 0:
  - {label}: ${{{{ currency(financial_data.{var_name}) }}}}
  % endif"""
        
        yaml += """
  
  **Total Monthly Income:** ${ currency(total_income) if defined('total_income') else '$0' }
  
buttons:
  - Exit: exit
  - Restart: restart
---"""
        
        return yaml
    
    def _clean_var_name(self, name: str) -> str:
        """Clean variable name"""
        if not name:
            return ""
        # Remove special chars
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        name = re.sub(r'_+', '_', name)
        name = name.strip('_').lower()
        # Limit length
        if len(name) > 40:
            name = name[:40]
        return name
    
    def _clean_label(self, label: str) -> str:
        """Clean label text"""
        if not label:
            return ""
        # Remove repetitions
        words = label.split()
        clean_words = []
        prev = None
        for word in words:
            if word != prev:
                clean_words.append(word)
                prev = word
        
        label = ' '.join(clean_words[:10])  # Limit words
        return label.strip()
    
    def _extract_income_label(self, label: str) -> str:
        """Extract clean income field label"""
        if not label:
            return ""
        
        # Common patterns in Form 13 income fields
        patterns = [
            r'(\d+\.\s+)?(.+?)(?:\s+\1)',  # Remove duplicates
            r'^\d+\.\s*\d*\.\s*(.+)',  # Extract after numbering
            r'^(.+?)(?:\s+.+){2,}$',  # Get first occurrence
        ]
        
        for pattern in patterns:
            match = re.search(pattern, label)
            if match:
                label = match.group(1) if match.lastindex else match.group(0)
                break
        
        # Clean up
        label = re.sub(r'\s+', ' ', label)
        label = label.strip()
        
        # Common replacements for Form 13
        replacements = {
            'Employment income (before deductions)': 'Employment Income',
            'Self-employment income': 'Self-Employment Income',
            'Employment Insurance benefits': 'EI Benefits',
            'Social assistance income': 'Social Assistance',
            'Interest and investment income': 'Investment Income',
            'Pension income': 'Pension Income',
            'Total monthly income': 'Total Monthly Income',
        }
        
        for old, new in replacements.items():
            if old.lower() in label.lower():
                return new
        
        # Truncate if still too long
        if len(label) > 50:
            label = label[:47] + "..."
        
        return label


def main():
    generator = RealDataGenerator()
    
    print("=" * 60)
    print("GENERATING FORM 13 FROM REAL PARSED DATA")
    print("=" * 60)
    
    if generator.generate_real_form_13():
        print("\n✅ Success! Generated Form 13 with real parsed fields")
        print("\nTest it at:")
        print("  /interview?i=docassemble.webapp:ontario-family-law/utilities/data_driven_interviews/form_13_real_data.yml")
    else:
        print("\n❌ Failed to generate")


if __name__ == "__main__":
    main()