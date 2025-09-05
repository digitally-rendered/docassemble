#!/usr/bin/env python3
"""
Data-Driven Interview Generator
Generates Docassemble interviews from parsed form data and domain mappings
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataDrivenGenerator:
    """Generate interviews from parsed data and domain mappings"""
    
    def __init__(self):
        self.output_dir = Path('data_driven_interviews')
        self.output_dir.mkdir(exist_ok=True)
        
        # Load domain mappings
        self.domain_mappings = self._load_json('workflow_output/domain_mappings.json')
        
        # Load field mappings
        self.field_mappings = self._load_json('workflow_output/field_mappings.json')
        
    def _load_json(self, filepath: str) -> Dict:
        """Load JSON data from file"""
        path = Path(filepath)
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        logger.warning(f"File not found: {filepath}")
        return {}
    
    def generate_form_13_from_data(self):
        """Generate Form 13 using parsed data and domain mappings"""
        
        # Load the parsed Form 13 data
        parsed_data = self._load_json(
            'validation_results/form_13_-_financial_statement_support_flr-13-may21-en-fil_unified_results.json'
        )
        
        if not parsed_data:
            logger.error("No parsed data found for Form 13")
            return False
        
        # Extract fields from parsed data
        fields = parsed_data.get('fields', [])
        
        # Group fields by type/context
        field_groups = self._group_fields_by_context(fields)
        
        # Generate the interview
        yaml_content = self._generate_interview_yaml(field_groups)
        
        # Save the interview
        output_file = self.output_dir / 'form_13_data_driven.yml'
        with open(output_file, 'w') as f:
            f.write(yaml_content)
        
        logger.info(f"Generated: {output_file}")
        return True
    
    def _group_fields_by_context(self, fields: List[Dict]) -> Dict[str, List[Dict]]:
        """Group fields by their context/section"""
        groups = {
            'court_info': [],
            'party_info': [],
            'income': [],
            'expenses': [],
            'assets': [],
            'debts': [],
            'other': []
        }
        
        for field in fields:
            field_name = field.get('field_name', '').lower()
            field_label = field.get('field_label', '').lower()
            context = field.get('context', '').lower()
            
            # Classify field into appropriate group
            if any(term in field_name or term in field_label for term in ['court', 'file_number', 'judge']):
                groups['court_info'].append(field)
            elif any(term in field_name or term in field_label for term in ['applicant', 'respondent', 'lawyer', 'name', 'address', 'birth']):
                groups['party_info'].append(field)
            elif any(term in field_name or term in field_label for term in ['income', 'employment', 'salary', 'wages', 'earning']):
                groups['income'].append(field)
            elif any(term in field_name or term in field_label for term in ['expense', 'housing', 'food', 'transport', 'childcare']):
                groups['expenses'].append(field)
            elif any(term in field_name or term in field_label for term in ['asset', 'property', 'investment', 'bank', 'vehicle']):
                groups['assets'].append(field)
            elif any(term in field_name or term in field_label for term in ['debt', 'loan', 'mortgage', 'credit']):
                groups['debts'].append(field)
            else:
                groups['other'].append(field)
        
        return groups
    
    def _generate_interview_yaml(self, field_groups: Dict[str, List[Dict]]) -> str:
        """Generate YAML content from grouped fields"""
        
        # Start with metadata
        yaml_content = """---
metadata:
  title: Form 13 - Financial Statement (Data-Driven)
  short title: Form 13
  description: Generated from parsed form data
  form_number: 13
---
include:
  - docassemble.base:data/questions/basic-questions.yml
---
features:
  progress bar: True
  question back button: True
  debug: True
---"""
        
        # Add objects based on domain mappings
        yaml_content += self._generate_objects_section()
        
        # Add initialization
        yaml_content += """
---
initial: True
code: |
  # Initialize collections
  income_sources = DAList()
  income_sources.auto_gather = False
  
  # Initialize expense tracking
  monthly_expenses = DAObject()
  expense_categories = [
    'housing', 'food', 'clothing', 'transportation',
    'childcare', 'health', 'insurance', 'other'
  ]
  for category in expense_categories:
    setattr(monthly_expenses, category, 0)
---"""
        
        # Add mandatory flow
        yaml_content += """
mandatory: True
code: |
  intro_screen
  
  # Collect party information
  if needs_party_info:
    collect_party_info
  
  # Collect financial information
  collect_income
  collect_expenses
  
  # Calculate totals
  calculate_totals
  
  # Show summary
  show_summary
---"""
        
        # Add intro screen
        yaml_content += """
question: |
  Form 13 - Financial Statement
subquestion: |
  This interview will help you complete Form 13: Financial Statement (Support Claims).
  
  You will need to provide:
  - Personal information
  - Income sources
  - Monthly expenses
  - Assets and debts (if applicable)
continue button field: intro_screen
---"""
        
        # Add party info collection if we have party fields
        if field_groups.get('party_info'):
            yaml_content += self._generate_party_info_screen(field_groups['party_info'])
        
        # Add income collection
        yaml_content += self._generate_income_screen()
        
        # Add expense collection
        yaml_content += self._generate_expense_screen()
        
        # Add calculations
        yaml_content += """
code: |
  # Calculate totals
  if len(income_sources) > 0:
    total_income = sum(item.amount for item in income_sources)
  else:
    total_income = 0
  
  # Sum all expense categories
  expense_fields = ['housing', 'food', 'clothing', 'transportation',
                    'childcare', 'health', 'insurance', 'other']
  total_expenses = sum(getattr(monthly_expenses, field, 0) for field in expense_fields)
  
  net_income = total_income - total_expenses
  calculate_totals = True
---"""
        
        # Add summary screen
        yaml_content += self._generate_summary_screen()
        
        return yaml_content
    
    def _generate_objects_section(self) -> str:
        """Generate objects section based on domain mappings"""
        objects = """
# Domain-mapped objects
objects:"""
        
        # Add objects from domain mappings
        if self.domain_mappings and 'entities' in self.domain_mappings:
            entities = self.domain_mappings['entities']
            
            # Find person entities
            for entity_key, entity_info in entities.items():
                if entity_info.get('entity_type') == 'person':
                    objects += f"\n  - {entity_info['variable_name']}: Individual"
            
            # Add financial tracking objects
            objects += "\n  - income_sources: DAList.using(object_type=DAObject)"
            objects += "\n  - monthly_expenses: DAObject"
            objects += "\n  - assets: DAList.using(object_type=DAObject)"
            objects += "\n  - debts: DAList.using(object_type=DAObject)"
        else:
            # Default objects if no mappings
            objects += """
  - applicant: Individual
  - respondent: Individual
  - income_sources: DAList.using(object_type=DAObject)
  - monthly_expenses: DAObject
  - assets: DAList.using(object_type=DAObject)
  - debts: DAList.using(object_type=DAObject)"""
        
        objects += "\n---"
        return objects
    
    def _generate_party_info_screen(self, party_fields: List[Dict]) -> str:
        """Generate party information collection screen"""
        screen = """
code: |
  needs_party_info = True
---
question: |
  Party Information
fields:"""
        
        # Add fields for applicant
        screen += """
  - "Are you the Applicant or Respondent?": party_type
    datatype: radio
    choices:
      - Applicant
      - Respondent
  - First Name: person.name.first
    required: True
  - Last Name: person.name.last
    required: True
  - Date of Birth: person.birthdate
    datatype: date
    required: False
  - Address: person.address.address
    required: False
  - City: person.address.city
    required: False
  - Province: person.address.state
    default: "ON"
    required: False
  - Postal Code: person.address.zip
    required: False
continue button field: collect_party_info
---"""
        return screen
    
    def _generate_income_screen(self) -> str:
        """Generate income collection screen with table"""
        return """
question: |
  Income Sources
subquestion: |
  List all sources of monthly income.
fields:
  - "Income Sources": income_sources.table
    required: False
    rows:
      - Source: |
          row_item.source if defined('row_item.source') else ""
      - Amount: |
          currency(row_item.amount) if defined('row_item.amount') else ""
    columns:
      - Source: |
          row_item.source
        choices:
          - Employment
          - Self-Employment
          - Government Benefits
          - Support Payments
          - Investment Income
          - Pension
          - Other
      - Monthly Amount: |
          row_item.amount
        datatype: currency
        min: 0
    minimum_number: 0
continue button field: collect_income
---"""
    
    def _generate_expense_screen(self) -> str:
        """Generate expense collection screen"""
        return """
question: |
  Monthly Expenses
subquestion: |
  Enter your monthly expenses. Leave blank for categories that don't apply.
fields:
  - "Housing (rent/mortgage)": monthly_expenses.housing
    datatype: currency
    min: 0
    default: 0
    required: False
  - "Food and groceries": monthly_expenses.food
    datatype: currency
    min: 0
    default: 0
    required: False
  - "Clothing": monthly_expenses.clothing
    datatype: currency
    min: 0
    default: 0
    required: False
  - "Transportation": monthly_expenses.transportation
    datatype: currency
    min: 0
    default: 0
    required: False
  - "Childcare": monthly_expenses.childcare
    datatype: currency
    min: 0
    default: 0
    required: False
  - "Health and medical": monthly_expenses.health
    datatype: currency
    min: 0
    default: 0
    required: False
  - "Insurance": monthly_expenses.insurance
    datatype: currency
    min: 0
    default: 0
    required: False
  - "Other expenses": monthly_expenses.other
    datatype: currency
    min: 0
    default: 0
    required: False
continue button field: collect_expenses
---"""
    
    def _generate_summary_screen(self) -> str:
        """Generate summary screen"""
        return """
event: show_summary
question: |
  Form 13 - Financial Statement Summary
subquestion: |
  % if defined('person'):
  **Party Information:**
  - Name: ${ person.name.full() }
  - Type: ${ party_type }
  % if defined('person.birthdate'):
  - Date of Birth: ${ person.birthdate }
  % endif
  % if defined('person.address.address'):
  - Address: ${ person.address.on_one_line() }
  % endif
  % endif
  
  ---
  
  **Income Summary:**
  % if len(income_sources) > 0:
  | Source | Monthly Amount |
  |--------|---------------|
  % for item in income_sources:
  | ${ item.source } | ${ currency(item.amount) } |
  % endfor
  | **TOTAL** | **${ currency(total_income) }** |
  % else:
  No income sources listed.
  % endif
  
  ---
  
  **Expense Summary:**
  | Category | Amount |
  |----------|--------|
  % if monthly_expenses.housing > 0:
  | Housing | ${ currency(monthly_expenses.housing) } |
  % endif
  % if monthly_expenses.food > 0:
  | Food | ${ currency(monthly_expenses.food) } |
  % endif
  % if monthly_expenses.clothing > 0:
  | Clothing | ${ currency(monthly_expenses.clothing) } |
  % endif
  % if monthly_expenses.transportation > 0:
  | Transportation | ${ currency(monthly_expenses.transportation) } |
  % endif
  % if monthly_expenses.childcare > 0:
  | Childcare | ${ currency(monthly_expenses.childcare) } |
  % endif
  % if monthly_expenses.health > 0:
  | Health | ${ currency(monthly_expenses.health) } |
  % endif
  % if monthly_expenses.insurance > 0:
  | Insurance | ${ currency(monthly_expenses.insurance) } |
  % endif
  % if monthly_expenses.other > 0:
  | Other | ${ currency(monthly_expenses.other) } |
  % endif
  | **TOTAL** | **${ currency(total_expenses) }** |
  
  ---
  
  **Net Income:** ${ currency(net_income) }
  
  % if net_income < 0:
  ⚠️ Your expenses exceed income by ${ currency(abs(net_income)) }
  % endif
buttons:
  - Exit: exit
  - Restart: restart
---"""


def main():
    """Run the data-driven generator"""
    generator = DataDrivenGenerator()
    
    print("=" * 60)
    print("DATA-DRIVEN INTERVIEW GENERATION")
    print("=" * 60)
    
    if generator.generate_form_13_from_data():
        print("\n✅ Successfully generated Form 13 from parsed data")
        print("\nAccess the interview at:")
        print("  /interview?i=docassemble.webapp:ontario-family-law/utilities/data_driven_interviews/form_13_data_driven.yml")
    else:
        print("\n❌ Failed to generate interview")


if __name__ == "__main__":
    main()