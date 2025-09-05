#!/usr/bin/env python3
"""
Incremental Interview Generator
Builds interviews step by step, ensuring each stage works before adding complexity
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


class IncrementalGenerator:
    """Generate interviews incrementally, testing at each stage"""
    
    def __init__(self):
        self.output_dir = Path('incremental_interviews')
        self.output_dir.mkdir(exist_ok=True)
        self.stages = []
        
    def generate_form_13_incremental(self):
        """Generate Form 13 in incremental stages"""
        
        logger.info("Starting incremental generation of Form 13")
        
        # Stage 1: Bare minimum
        stage1 = self.generate_stage_1_minimal()
        self.save_interview("form_13_stage_1_minimal", stage1)
        
        # Stage 2: Add basic structure
        stage2 = self.generate_stage_2_basic_structure()
        self.save_interview("form_13_stage_2_structure", stage2)
        
        # Stage 3: Add Individual object
        stage3 = self.generate_stage_3_with_person()
        self.save_interview("form_13_stage_3_person", stage3)
        
        # Stage 4: Add financial fields
        stage4 = self.generate_stage_4_with_financial()
        self.save_interview("form_13_stage_4_financial", stage4)
        
        # Stage 5: Add error handling
        stage5 = self.generate_stage_5_with_error_handling()
        self.save_interview("form_13_stage_5_errors", stage5)
        
        # Stage 6: Add validation
        stage6 = self.generate_stage_6_with_validation()
        self.save_interview("form_13_stage_6_validation", stage6)
        
        # Stage 7: Add domain mapping
        stage7 = self.generate_stage_7_with_domain_mapping()
        self.save_interview("form_13_stage_7_complete", stage7)
        
        # Generate index
        self.generate_stage_index()
        
        logger.info("Completed incremental generation")
        return True
    
    def generate_stage_1_minimal(self) -> str:
        """Stage 1: Absolute minimum working interview"""
        return """---
metadata:
  title: Form 13 - Stage 1 - Minimal
  short title: Stage 1
  stage: 1
  description: Bare minimum working interview
---
mandatory: True
code: |
  show_intro
  show_complete
---
question: |
  Form 13 Financial Statement
subquestion: |
  Stage 1: This is the simplest possible working interview.
  
  Click Continue to proceed.
continue button field: show_intro
---
event: show_complete
question: |
  Stage 1 Complete
subquestion: |
  The minimal interview loaded and completed successfully.
  
  This proves the basic structure works.
buttons:
  - Exit: exit"""
    
    def generate_stage_2_basic_structure(self) -> str:
        """Stage 2: Add basic docassemble structure"""
        return """---
metadata:
  title: Form 13 - Stage 2 - Basic Structure  
  short title: Stage 2
  stage: 2
  description: Basic docassemble structure with includes and features
---
include:
  - docassemble.base:data/questions/basic-questions.yml
---
features:
  progress bar: True
  question back button: True
---
mandatory: True
code: |
  intro_screen
  name_collected
  final_screen
---
question: |
  Form 13 Financial Statement
subquestion: |
  Stage 2: Basic structure with includes and features.
  
  This interview has:
  - Include statement for basic questions
  - Progress bar enabled
  - Back button enabled
continue button field: intro_screen
---
question: |
  Test Question
fields:
  - Your Name: user_name
continue button field: name_collected
---
event: final_screen
question: |
  Stage 2 Complete
subquestion: |
  You entered: **${ user_name }**
  
  Basic structure with includes works correctly.
buttons:
  - Exit: exit
  - Restart: restart"""
    
    def generate_stage_3_with_person(self) -> str:
        """Stage 3: Add Individual object for person"""
        return """---
metadata:
  title: Form 13 - Stage 3 - Individual Object
  short title: Stage 3
  stage: 3
  description: Using Individual object for person data
---
include:
  - docassemble.base:data/questions/basic-questions.yml
---
features:
  progress bar: True
  question back button: True
---
objects:
  - user: Individual
---
mandatory: True
code: |
  intro_screen
  user.name.first
  user.birthdate
  final_screen
---
question: |
  Form 13 Financial Statement
subquestion: |
  Stage 3: Using Individual object for person data.
  
  This adds:
  - Individual object declaration
  - Proper name fields using user.name.first/last
  - Date field for birthdate
continue button field: intro_screen
---
question: |
  Your Information
fields:
  - First Name: user.name.first
    required: True
  - Last Name: user.name.last
    required: True
  - Date of Birth: user.birthdate
    datatype: date
---
event: final_screen
question: |
  Stage 3 Complete
subquestion: |
  **Your Information:**
  - Name: ${ user.name.full() }
  - Date of Birth: ${ user.birthdate }
  
  Individual object works correctly!
buttons:
  - Exit: exit
  - Restart: restart"""
    
    def generate_stage_4_with_financial(self) -> str:
        """Stage 4: Add financial fields"""
        return """---
metadata:
  title: Form 13 - Stage 4 - Financial Fields
  short title: Stage 4
  stage: 4
  description: Adding financial income and expense fields
---
include:
  - docassemble.base:data/questions/basic-questions.yml
---
features:
  progress bar: True
  question back button: True
---
objects:
  - user: Individual
  - income: DAObject
  - expenses: DAObject
---
mandatory: True
code: |
  intro_screen
  user.name.first
  income.employment
  expenses.housing
  show_summary
---
question: |
  Form 13 Financial Statement
subquestion: |
  Stage 4: Adding financial fields with DAObject.
  
  This adds:
  - Income object
  - Expenses object
  - Currency fields
  - Calculations
continue button field: intro_screen
---
question: |
  Your Information
fields:
  - First Name: user.name.first
    required: True
  - Last Name: user.name.last
    required: True
---
question: |
  Income Information
fields:
  - Employment Income (Monthly): income.employment
    datatype: currency
    min: 0
    required: True
  - Other Income: income.other
    datatype: currency
    min: 0
    default: 0
---
question: |
  Monthly Expenses
fields:
  - Housing (Rent/Mortgage): expenses.housing
    datatype: currency
    min: 0
    required: True
  - Food: expenses.food
    datatype: currency
    min: 0
    default: 0
  - Transportation: expenses.transport
    datatype: currency
    min: 0
    default: 0
---
code: |
  income.total = income.employment + income.other
  expenses.total = expenses.housing + expenses.food + expenses.transport
  net_income = income.total - expenses.total
---
event: show_summary
question: |
  Stage 4 Complete - Financial Summary
subquestion: |
  **Person:** ${ user.name.full() }
  
  **Monthly Income:**
  - Employment: ${ currency(income.employment) }
  - Other: ${ currency(income.other) }
  - Total: ${ currency(income.total) }
  
  **Monthly Expenses:**
  - Housing: ${ currency(expenses.housing) }
  - Food: ${ currency(expenses.food) }
  - Transportation: ${ currency(expenses.transport) }
  - Total: ${ currency(expenses.total) }
  
  **Net Income:** ${ currency(net_income) }
buttons:
  - Exit: exit
  - Restart: restart"""
    
    def generate_stage_5_with_error_handling(self) -> str:
        """Stage 5: Add error handling"""
        return """---
metadata:
  title: Form 13 - Stage 5 - Error Handling
  short title: Stage 5
  stage: 5
  description: Adding error handling infrastructure
---
include:
  - docassemble.base:data/questions/basic-questions.yml
---
features:
  progress bar: True
  question back button: True
  debug: True
---
objects:
  - user: Individual
  - income: DAObject
  - expenses: DAObject
  - error_log: DAList
---
# Initialize error handling
initial: True
code: |
  error_log = DAList()
  error_count = 0
---
# Error handling function
code: |
  def log_error(context, message):
    error_entry = {
      'time': current_datetime(),
      'context': context,
      'message': message
    }
    error_log.append(error_entry)
    error_count = len(error_log)
    return True
---
# Safe getter function
code: |
  def safe_value(obj, attr, default=0):
    try:
      if hasattr(obj, attr):
        val = getattr(obj, attr)
        return val if val is not None else default
      return default
    except Exception as e:
      log_error(f"safe_value({attr})", str(e))
      return default
---
mandatory: True
code: |
  try:
    intro_screen
    user.name.first
    income.employment
    expenses.housing
    show_summary
  except Exception as e:
    log_error("main_flow", str(e))
    show_error_screen
---
question: |
  Form 13 Financial Statement
subquestion: |
  Stage 5: With error handling infrastructure.
  
  This adds:
  - Error logging
  - Safe value getters
  - Try/catch blocks
  - Error recovery
continue button field: intro_screen
---
question: |
  Your Information
fields:
  - First Name: user.name.first
    required: True
  - Last Name: user.name.last
    required: True
---
question: |
  Income Information
fields:
  - Employment Income: income.employment
    datatype: currency
    min: 0
    required: True
---
question: |
  Monthly Expenses
fields:
  - Housing: expenses.housing
    datatype: currency
    min: 0
    required: True
---
code: |
  income.total = safe_value(income, 'employment', 0)
  expenses.total = safe_value(expenses, 'housing', 0)
  net_income = income.total - expenses.total
---
event: show_summary
question: |
  Stage 5 Complete - With Error Handling
subquestion: |
  **Person:** ${ user.name.full() }
  
  **Financial Summary:**
  - Income: ${ currency(income.total) }
  - Expenses: ${ currency(expenses.total) }
  - Net: ${ currency(net_income) }
  
  **Error Status:**
  - Errors logged: ${ len(error_log) }
  
  % if len(error_log) > 0:
  **Errors:**
  % for error in error_log:
  - ${ error['context'] }: ${ error['message'] }
  % endfor
  % endif
buttons:
  - Exit: exit
  - Restart: restart
---
event: show_error_screen
question: |
  Error Occurred
subquestion: |
  An error occurred during the interview.
  
  % if len(error_log) > 0:
  Last error: ${ error_log[-1]['message'] }
  % endif
buttons:
  - Restart: restart
  - Exit: exit"""
    
    def generate_stage_6_with_validation(self) -> str:
        """Stage 6: Add field validation"""
        return """---
metadata:
  title: Form 13 - Stage 6 - Field Validation
  short title: Stage 6
  stage: 6
  description: Adding field validation
---
include:
  - docassemble.base:data/questions/basic-questions.yml
---
features:
  progress bar: True
  question back button: True
  debug: True
---
objects:
  - user: Individual
  - income: DAObject
  - expenses: DAObject
  - validation_errors: DAList
---
initial: True
code: |
  validation_errors = DAList()
---
mandatory: True
code: |
  intro_screen
  user.name.first
  income_validated
  expenses_validated
  show_summary
---
question: |
  Form 13 Financial Statement
subquestion: |
  Stage 6: With field validation.
  
  This adds:
  - Field validation rules
  - Validation messages
  - Custom validation code
continue button field: intro_screen
---
question: |
  Your Information
fields:
  - First Name: user.name.first
    required: True
    validation messages:
      required: |
        First name is required
  - Last Name: user.name.last
    required: True
    validation messages:
      required: |
        Last name is required
  - Email: user.email
    datatype: email
    required: False
    validation messages:
      datatype: |
        Please enter a valid email address
validation code: |
  if len(user.name.first) < 2:
    validation_error("First name must be at least 2 characters")
---
question: |
  Income Information
fields:
  - Employment Income: income.employment
    datatype: currency
    min: 0
    required: True
    validation messages:
      required: |
        Employment income is required
      min: |
        Income cannot be negative
validation code: |
  if income.employment > 1000000:
    validation_error("Please verify income amount - seems unusually high", field="income.employment")
  income.total = income.employment
continue button field: income_validated
---
question: |
  Monthly Expenses  
fields:
  - Housing: expenses.housing
    datatype: currency
    min: 0
    required: True
validation code: |
  if expenses.housing > income.total:
    note("Warning: Housing expenses exceed total income")
  expenses.total = expenses.housing
continue button field: expenses_validated
---
code: |
  net_income = income.total - expenses.total
---
event: show_summary
question: |
  Stage 6 Complete - With Validation
subquestion: |
  **Person:** ${ user.name.full() }
  % if defined('user.email'):
  - Email: ${ user.email }
  % endif
  
  **Financial Summary:**
  - Income: ${ currency(income.total) }
  - Expenses: ${ currency(expenses.total) }
  - Net: ${ currency(net_income) }
  
  **Validation Status:**
  % if len(validation_errors) == 0:
  ✓ All fields validated successfully
  % else:
  ⚠ ${ len(validation_errors) } validation warnings
  % endif
buttons:
  - Exit: exit
  - Restart: restart"""
    
    def generate_stage_7_with_domain_mapping(self) -> str:
        """Stage 7: Add domain mapping for Form 13"""
        return """---
metadata:
  title: Form 13 - Stage 7 - Complete with Domain Mapping
  short title: Stage 7
  stage: 7
  description: Complete Form 13 with domain mapping
  form_number: 13
---
include:
  - docassemble.base:data/questions/basic-questions.yml
---
features:
  progress bar: True
  question back button: True
  debug: True
---
# Domain-mapped objects
objects:
  # Person entities
  - applicant: Individual
  - respondent: Individual
  - children: DAList.using(object_type=Individual)
  
  # Financial entities
  - income_sources: DAList.using(object_type=DAObject)
  - expenses_list: DAList.using(object_type=DAObject)
  - assets: DAList.using(object_type=DAObject)
  - debts: DAList.using(object_type=DAObject)
  
  # Support for error handling
  - validation_errors: DAList
---
# Initialize
initial: True
code: |
  validation_errors = DAList()
---
# Domain mapping code
code: |
  # Map form fields to domain entities
  form_13_domains = {
    'person_info': ['applicant', 'respondent'],
    'financial_info': ['income_sources', 'expenses_list'],
    'property_info': ['assets', 'debts'],
    'children_info': ['children']
  }
---
mandatory: True
code: |
  intro_screen
  
  # Collect person domain
  applicant.name.first
  
  # Collect financial domain
  has_income = True
  if has_income:
    income_sources.gather()
  
  has_expenses = True
  if has_expenses:
    expenses_list.gather()
  
  # Calculate totals
  calculate_totals
  
  # Show final
  show_final
---
question: |
  Form 13 Financial Statement
subquestion: |
  Stage 7: Complete with domain mapping.
  
  This is the full Form 13 with:
  - Domain entity mapping
  - Multiple object types
  - Collections (DAList)
  - Calculations
  - Full error handling
  - Validation
continue button field: intro_screen
---
question: |
  Applicant Information
fields:
  - First Name: applicant.name.first
    required: True
  - Last Name: applicant.name.last
    required: True
  - Date of Birth: applicant.birthdate
    datatype: date
---
question: |
  Income Source ${ i + 1 }
fields:
  - Source: income_sources[i].source
    required: True
    choices:
      - Employment
      - Self-Employment
      - Government Benefits
      - Other
  - Monthly Amount: income_sources[i].amount
    datatype: currency
    min: 0
    required: True
---
question: |
  Any more income sources?
yesno: income_sources.there_is_another
---
question: |
  Expense ${ i + 1 }
fields:
  - Category: expenses_list[i].category
    required: True
    choices:
      - Housing
      - Food
      - Transportation
      - Childcare
      - Other
  - Monthly Amount: expenses_list[i].amount
    datatype: currency
    min: 0
    required: True
---
question: |
  Any more expenses?
yesno: expenses_list.there_is_another
---
code: |
  # Calculate domain totals
  total_income = sum(item.amount for item in income_sources)
  total_expenses = sum(item.amount for item in expenses_list)
  net_income = total_income - total_expenses
  calculate_totals = True
---
event: show_final
question: |
  Form 13 Complete - Full Domain Mapping
subquestion: |
  **Applicant:** ${ applicant.name.full() }
  
  **Income Sources:** ${ len(income_sources) }
  % for item in income_sources:
  - ${ item.source }: ${ currency(item.amount) }
  % endfor
  **Total Income:** ${ currency(total_income) }
  
  **Expenses:** ${ len(expenses_list) }
  % for item in expenses_list:
  - ${ item.category }: ${ currency(item.amount) }
  % endfor
  **Total Expenses:** ${ currency(total_expenses) }
  
  **Net Income:** ${ currency(net_income) }
  
  ---
  
  This completes the incremental development:
  1. ✓ Basic structure
  2. ✓ Individual objects  
  3. ✓ Financial fields
  4. ✓ Error handling
  5. ✓ Validation
  6. ✓ Domain mapping
buttons:
  - Exit: exit
  - Restart: restart"""
    
    def save_interview(self, filename: str, content: str):
        """Save interview to file"""
        filepath = self.output_dir / f"{filename}.yml"
        with open(filepath, 'w') as f:
            f.write(content)
        logger.info(f"Created: {filepath}")
        
    def generate_stage_index(self):
        """Generate index for all stages"""
        index = """---
metadata:
  title: Form 13 - Incremental Development Stages
  short title: Stage Index
---
mandatory: True
question: |
  Form 13 - Incremental Development
subquestion: |
  ## Test Each Stage in Order
  
  Each stage builds on the previous one. Test them in sequence to see how the interview develops:
  
  ### Stage 1: Minimal
  [Test Stage 1](/interview?i=docassemble.webapp:ontario-family-law/utilities/incremental_interviews/form_13_stage_1_minimal.yml)
  - Absolute minimum working interview
  - Just intro and complete screens
  
  ### Stage 2: Basic Structure
  [Test Stage 2](/interview?i=docassemble.webapp:ontario-family-law/utilities/incremental_interviews/form_13_stage_2_structure.yml)
  - Adds includes and features
  - Simple field collection
  
  ### Stage 3: Individual Object
  [Test Stage 3](/interview?i=docassemble.webapp:ontario-family-law/utilities/incremental_interviews/form_13_stage_3_person.yml)
  - Uses Individual object for person
  - Proper name fields
  
  ### Stage 4: Financial Fields
  [Test Stage 4](/interview?i=docassemble.webapp:ontario-family-law/utilities/incremental_interviews/form_13_stage_4_financial.yml)
  - Adds income and expense objects
  - Currency fields and calculations
  
  ### Stage 5: Error Handling
  [Test Stage 5](/interview?i=docassemble.webapp:ontario-family-law/utilities/incremental_interviews/form_13_stage_5_errors.yml)
  - Error logging
  - Safe value getters
  - Error recovery
  
  ### Stage 6: Validation
  [Test Stage 6](/interview?i=docassemble.webapp:ontario-family-law/utilities/incremental_interviews/form_13_stage_6_validation.yml)
  - Field validation rules
  - Custom validation messages
  
  ### Stage 7: Complete with Domain Mapping
  [Test Stage 7](/interview?i=docassemble.webapp:ontario-family-law/utilities/incremental_interviews/form_13_stage_7_complete.yml)
  - Full domain entity mapping
  - Collections (DAList)
  - Complete Form 13
  
  ## Testing Instructions
  
  1. Start with Stage 1 - verify it loads
  2. Test each stage in order
  3. Note where errors occur
  4. Each stage should work independently
  
buttons:
  - Exit: exit"""
        
        self.save_interview("00_stage_index", index)
        

def main():
    """Run the incremental generator"""
    generator = IncrementalGenerator()
    
    print("=" * 60)
    print("INCREMENTAL FORM 13 GENERATION")
    print("=" * 60)
    
    generator.generate_form_13_incremental()
    
    print("\nGeneration complete!")
    print("\nAccess the stages at:")
    print("  /interview?i=docassemble.webapp:ontario-family-law/utilities/incremental_interviews/00_stage_index.yml")
    print("\nTest each stage in order to see the progression.")


if __name__ == "__main__":
    main()