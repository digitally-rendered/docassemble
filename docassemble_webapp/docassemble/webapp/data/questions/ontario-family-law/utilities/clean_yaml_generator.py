#!/usr/bin/env python3
"""
Clean YAML Generator
Generates properly formatted YAML interviews without errors
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

class CleanYAMLGenerator:
    """Generate clean, working YAML interviews"""
    
    def __init__(self):
        self.output_dir = Path('data_driven_interviews')
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_clean_form_13(self):
        """Generate a clean, working Form 13"""
        
        # Build as a list of YAML documents (each will be separated by ---)
        documents = []
        
        # Document 1: Metadata
        documents.append({
            'metadata': {
                'title': 'Form 13 - Financial Statement (Clean)',
                'short title': 'Form 13 Clean'
            }
        })
        
        # Document 2: Includes
        documents.append({
            'include': ['docassemble.base:data/questions/basic-questions.yml']
        })
        
        # Document 3: Features
        documents.append({
            'features': {
                'progress bar': True,
                'question back button': True
            }
        })
        
        # Document 4: Objects - FIXED FORMAT
        documents.append({
            'objects': [
                {'applicant': 'Individual'},
                {'income_data': 'DAObject'},
                {'expenses': 'DAObject'}
            ]
        })
        
        # Document 5: Mandatory flow
        documents.append({
            'mandatory': True,
            'code': '|\n  intro_screen\n  applicant.name.first\n  collect_income\n  collect_expenses\n  show_summary'
        })
        
        # Document 6: Intro screen
        documents.append({
            'question': 'Form 13 Financial Statement',
            'subquestion': 'This form collects financial information.',
            'continue button field': 'intro_screen'
        })
        
        # Document 7: Applicant info
        documents.append({
            'question': 'Your Information',
            'fields': [
                {'First Name': 'applicant.name.first', 'required': True},
                {'Last Name': 'applicant.name.last', 'required': True}
            ]
        })
        
        # Document 8: Income collection
        documents.append({
            'question': 'Monthly Income',
            'fields': [
                {
                    'Employment Income': 'income_data.employment',
                    'datatype': 'currency',
                    'min': 0,
                    'default': 0,
                    'required': False
                },
                {
                    'Self-Employment': 'income_data.self_employment',
                    'datatype': 'currency',
                    'min': 0,
                    'default': 0,
                    'required': False
                },
                {
                    'Other Income': 'income_data.other',
                    'datatype': 'currency',
                    'min': 0,
                    'default': 0,
                    'required': False
                }
            ],
            'continue button field': 'collect_income'
        })
        
        # Document 9: Expense collection
        documents.append({
            'question': 'Monthly Expenses',
            'fields': [
                {
                    'Housing': 'expenses.housing',
                    'datatype': 'currency',
                    'min': 0,
                    'default': 0,
                    'required': False
                },
                {
                    'Food': 'expenses.food',
                    'datatype': 'currency',
                    'min': 0,
                    'default': 0,
                    'required': False
                },
                {
                    'Transportation': 'expenses.transportation',
                    'datatype': 'currency',
                    'min': 0,
                    'default': 0,
                    'required': False
                }
            ],
            'continue button field': 'collect_expenses'
        })
        
        # Document 10: Calculations
        documents.append({
            'code': '|\n  total_income = income_data.employment + income_data.self_employment + income_data.other\n  total_expenses = expenses.housing + expenses.food + expenses.transportation\n  net_income = total_income - total_expenses'
        })
        
        # Document 11: Summary
        documents.append({
            'event': 'show_summary',
            'question': 'Financial Summary',
            'subquestion': '|\n  **Name:** ${ applicant.name.full() }\n  \n  **Total Income:** ${ currency(total_income) }\n  \n  **Total Expenses:** ${ currency(total_expenses) }\n  \n  **Net Income:** ${ currency(net_income) }',
            'buttons': [
                {'Exit': 'exit'}
            ]
        })
        
        # Convert to YAML with proper formatting
        yaml_content = self._format_yaml_documents(documents)
        
        # Save the file
        output_file = self.output_dir / 'form_13_clean.yml'
        with open(output_file, 'w') as f:
            f.write(yaml_content)
        
        print(f"Generated: {output_file}")
        return True
    
    def _format_yaml_documents(self, documents: List[Dict]) -> str:
        """Format documents as proper YAML with --- separators"""
        yaml_parts = []
        
        for doc in documents:
            # Special handling for code blocks to preserve formatting
            if 'code' in doc and isinstance(doc['code'], str) and doc['code'].startswith('|'):
                # Handle multi-line code blocks
                yaml_str = yaml.dump(doc, default_flow_style=False, allow_unicode=True)
            else:
                yaml_str = yaml.dump(doc, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            yaml_parts.append(yaml_str.rstrip())
        
        # Join with document separators
        return '---\n' + '\n---\n'.join(yaml_parts)


def main():
    generator = CleanYAMLGenerator()
    
    print("=" * 60)
    print("CLEAN YAML GENERATOR")
    print("=" * 60)
    
    if generator.generate_clean_form_13():
        print("\n✅ Generated clean Form 13")
        print("\nTest at:")
        print("  /interview?i=docassemble.webapp:ontario-family-law/utilities/data_driven_interviews/form_13_clean.yml")


if __name__ == "__main__":
    main()