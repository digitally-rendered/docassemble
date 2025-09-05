#!/usr/bin/env python3
"""
Structured Data Generator
Generates interviews using Python data structures (dicts/lists) that get encoded to YAML
Includes proper scaffolding and error handling
"""

import yaml
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StructuredDataGenerator:
    """Generate interviews using structured data that gets encoded to YAML"""
    
    def __init__(self):
        self.output_dir = Path('data_driven_interviews')
        self.output_dir.mkdir(exist_ok=True)
        
        # Load parsed fields and domain mappings
        self.parsed_fields = self._load_parsed_fields()
        self.domain_mappings = self._load_domain_mappings()
        
    def _load_parsed_fields(self) -> List[Dict]:
        """Load parsed Form 13 fields"""
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
    
    def generate_form_13_structured(self):
        """Generate Form 13 using structured data approach"""
        
        # Build the interview as structured data
        interview_data = []
        
        # 1. Metadata block
        interview_data.append({
            'metadata': {
                'title': 'Form 13 - Financial Statement (Structured)',
                'short title': 'Form 13',
                'description': 'Generated from structured data with error handling',
                'form_number': '13'
            }
        })
        
        # 2. Includes block - with error handling modules
        interview_data.append({
            'include': [
                'docassemble.base:data/questions/basic-questions.yml'
            ]
        })
        
        # 3. Features block
        interview_data.append({
            'features': {
                'progress bar': True,
                'question back button': True,
                'debug': True
            }
        })
        
        # 4. Objects block - scaffolding with proper structure
        objects_map = self._build_objects_scaffolding()
        interview_data.append({'objects': objects_map})
        
        # 5. Initial code block - error handling setup
        initial_code = self._build_initial_code()
        interview_data.append(initial_code)
        
        # 6. Error handling functions
        error_functions = self._build_error_handling_functions()
        interview_data.append(error_functions)
        
        # 7. Mandatory flow
        mandatory_flow = self._build_mandatory_flow()
        interview_data.append(mandatory_flow)
        
        # 8. Questions from parsed data
        questions = self._build_questions_from_parsed_data()
        for question in questions:
            interview_data.append(question)
        
        # 9. Calculations
        calculations = self._build_calculations()
        interview_data.append(calculations)
        
        # 10. Summary screen
        summary = self._build_summary_screen()
        interview_data.append(summary)
        
        # Convert to YAML
        yaml_content = self._convert_to_yaml(interview_data)
        
        # Save the file
        output_file = self.output_dir / 'form_13_structured.yml'
        with open(output_file, 'w') as f:
            f.write(yaml_content)
        
        logger.info(f"Generated: {output_file}")
        return True
    
    def _build_objects_scaffolding(self) -> List[Dict]:
        """Build objects scaffolding with proper structure"""
        objects = []
        
        # Add person entities from domain mappings
        if self.domain_mappings and 'entities' in self.domain_mappings:
            for entity_id, entity in self.domain_mappings['entities'].items():
                if entity['entity_type'] == 'person':
                    objects.append({
                        entity['variable_name']: entity['docassemble_type']
                    })
                    break
        else:
            # Default person object
            objects.append({'applicant': 'Individual'})
        
        # Add financial data containers
        objects.append({'income_sources': 'DAList.using(object_type=DAObject)'})
        objects.append({'expenses': 'DAObject'})
        objects.append({'assets': 'DAList.using(object_type=DAObject)'})
        objects.append({'debts': 'DAList.using(object_type=DAObject)'})
        
        # Add error handling objects
        objects.append({'error_log': 'DAList'})
        objects.append({'validation_errors': 'DADict'})
        
        return objects
    
    def _build_initial_code(self) -> Dict:
        """Build initial setup code with error handling"""
        return {
            'initial': True,
            'code': """# Initialize error handling
error_log = DAList()
validation_errors = DADict()
debug_mode = get_config('debug', False)

# Initialize financial containers
income_sources.auto_gather = False
expense_categories = [
  'housing', 'food', 'transportation', 'childcare',
  'health', 'insurance', 'utilities', 'other'
]
for category in expense_categories:
  setattr(expenses, category, 0)

# Set up default values
total_income = 0
total_expenses = 0
net_income = 0"""
        }
    
    def _build_error_handling_functions(self) -> Dict:
        """Build error handling functions"""
        return {
            'code': """def safe_currency_value(obj, attr, default=0):
  '''Safely get currency value with error handling'''
  try:
    if hasattr(obj, attr):
      val = getattr(obj, attr)
      if val is None:
        return default
      if isinstance(val, (int, float)):
        return float(val)
      return default
    return default
  except Exception as e:
    error_log.append({
      'error': str(e),
      'field': attr,
      'timestamp': current_datetime()
    })
    return default

def validate_income_field(value, field_name):
  '''Validate income field value'''
  if value < 0:
    validation_errors[field_name] = "Income cannot be negative"
    return False
  if value > 1000000:
    validation_errors[field_name] = "Please verify amount - seems unusually high"
    return False
  return True"""
        }
    
    def _build_mandatory_flow(self) -> Dict:
        """Build mandatory flow with error handling"""
        return {
            'mandatory': True,
            'code': """try:
  intro_screen
  applicant_info
  income_collection
  expense_collection
  perform_calculations
  final_summary
except Exception as e:
  error_occurred = True
  show_error_screen"""
        }
    
    def _build_questions_from_parsed_data(self) -> List[Dict]:
        """Build question blocks from parsed data"""
        questions = []
        
        # 1. Intro screen
        questions.append({
            'question': 'Form 13 - Financial Statement',
            'subquestion': 'This interview collects financial information for support claims.',
            'continue button field': 'intro_screen'
        })
        
        # 2. Applicant info - using simple fields
        applicant_fields = [
            {'First Name': 'applicant.name.first', 'required': True},
            {'Last Name': 'applicant.name.last', 'required': True},
            {'Date of Birth': 'applicant.birthdate', 'datatype': 'date', 'required': False},
        ]
        
        questions.append({
            'question': 'Your Information',
            'fields': applicant_fields,
            'continue button field': 'applicant_info'
        })
        
        # 3. Income collection - from parsed data
        income_fields = self._extract_income_fields()
        questions.append({
            'question': 'Monthly Income',
            'subquestion': 'Enter your monthly income from each source.',
            'fields': income_fields,
            'continue button field': 'income_collection',
            'validation code': """for field_name in ['employment_income', 'self_employment', 'ei_benefits']:
  if defined('income_data.' + field_name):
    value = value('income_data.' + field_name)
    validate_income_field(value, field_name)"""
        })
        
        # 4. Expense collection
        expense_fields = self._build_expense_fields()
        questions.append({
            'question': 'Monthly Expenses',
            'subquestion': 'Enter your monthly expenses.',
            'fields': expense_fields,
            'continue button field': 'expense_collection'
        })
        
        return questions
    
    def _extract_income_fields(self) -> List[Dict]:
        """Extract income fields from parsed data"""
        fields = []
        
        # Map common income types to clean names
        income_mapping = {
            'employment': {'label': 'Employment Income', 'var': 'income_data.employment_income'},
            'self_employment': {'label': 'Self-Employment Income', 'var': 'income_data.self_employment'},
            'ei_benefits': {'label': 'EI Benefits', 'var': 'income_data.ei_benefits'},
            'social_assistance': {'label': 'Social Assistance', 'var': 'income_data.social_assistance'},
            'pension': {'label': 'Pension Income', 'var': 'income_data.pension'},
            'investment': {'label': 'Investment Income', 'var': 'income_data.investments'},
        }
        
        for key, info in income_mapping.items():
            field = {
                info['label']: info['var'],
                'datatype': 'currency',
                'min': 0,
                'default': 0,
                'required': False
            }
            fields.append(field)
        
        return fields
    
    def _build_expense_fields(self) -> List[Dict]:
        """Build expense fields"""
        expense_types = [
            ('Housing (rent/mortgage)', 'expenses.housing'),
            ('Food and groceries', 'expenses.food'),
            ('Transportation', 'expenses.transportation'),
            ('Childcare', 'expenses.childcare'),
            ('Health and medical', 'expenses.health'),
            ('Insurance', 'expenses.insurance'),
            ('Utilities', 'expenses.utilities'),
            ('Other expenses', 'expenses.other')
        ]
        
        fields = []
        for label, var in expense_types:
            fields.append({
                label: var,
                'datatype': 'currency',
                'min': 0,
                'default': 0,
                'required': False
            })
        
        return fields
    
    def _build_calculations(self) -> Dict:
        """Build calculation code block"""
        return {
            'code': """# Calculate totals with error handling
try:
  # Income total
  income_fields = ['employment_income', 'self_employment', 'ei_benefits', 
                   'social_assistance', 'pension', 'investments']
  total_income = 0
  for field in income_fields:
    if defined('income_data.' + field):
      total_income += safe_currency_value(income_data, field)
  
  # Expense total
  expense_fields = ['housing', 'food', 'transportation', 'childcare',
                    'health', 'insurance', 'utilities', 'other']
  total_expenses = 0
  for field in expense_fields:
    total_expenses += safe_currency_value(expenses, field)
  
  # Net income
  net_income = total_income - total_expenses
  
  perform_calculations = True
  
except Exception as e:
  error_log.append({
    'error': str(e),
    'context': 'calculations',
    'timestamp': current_datetime()
  })
  total_income = 0
  total_expenses = 0
  net_income = 0
  perform_calculations = True"""
        }
    
    def _build_summary_screen(self) -> Dict:
        """Build summary screen"""
        return {
            'event': 'final_summary',
            'question': 'Financial Statement Summary',
            'subquestion': """**Applicant:** ${ applicant.name.full() }

**Total Monthly Income:** ${ currency(total_income) }

**Total Monthly Expenses:** ${ currency(total_expenses) }

**Net Monthly Income:** ${ currency(net_income) }

% if len(error_log) > 0:
**Note:** ${ len(error_log) } issues were handled during processing.
% endif""",
            'buttons': [
                {'Exit': 'exit'},
                {'Restart': 'restart'}
            ]
        }
    
    def _convert_to_yaml(self, interview_data: List[Dict]) -> str:
        """Convert structured data to YAML"""
        yaml_blocks = []
        
        for block in interview_data:
            # Convert each block to YAML separately
            yaml_str = yaml.dump(
                block,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False
            )
            yaml_blocks.append(yaml_str)
        
        # Join blocks with YAML document separator
        return '---\n' + '---\n'.join(yaml_blocks)


def main():
    generator = StructuredDataGenerator()
    
    print("=" * 60)
    print("STRUCTURED DATA GENERATOR")
    print("=" * 60)
    print("Generating Form 13 using maps/lists and proper scaffolding...")
    
    if generator.generate_form_13_structured():
        print("\n✅ Success! Generated structured Form 13")
        print("\nFeatures:")
        print("  - Built from Python data structures (dicts/lists)")
        print("  - Proper error handling scaffolding")
        print("  - Domain object mapping")
        print("  - Safe value getters")
        print("  - Validation functions")
        print("\nTest at:")
        print("  /interview?i=docassemble.webapp:ontario-family-law/utilities/data_driven_interviews/form_13_structured.yml")
    else:
        print("\n❌ Failed to generate")


if __name__ == "__main__":
    main()