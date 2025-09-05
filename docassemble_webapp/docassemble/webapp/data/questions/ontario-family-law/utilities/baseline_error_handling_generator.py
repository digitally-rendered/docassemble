#!/usr/bin/env python3
"""
Baseline Error Handling Generator
Every interview MUST have error handling as the foundation
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import yaml

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BaselineErrorHandlingGenerator:
    """Generator that makes error handling the baseline of every interview"""
    
    def __init__(self):
        self.output_dir = Path('baseline_interviews')
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_baseline_interview(self, form_number: str = "13") -> Path:
        """Generate interview with error handling as the foundation"""
        
        logger.info(f"Generating baseline interview with error handling for Form {form_number}")
        
        # Build interview with error handling at every level
        sections = []
        
        # 1. Metadata with error context
        sections.append(self._generate_metadata_with_error_context(form_number))
        
        # 2. Core error handling infrastructure
        sections.append(self._generate_error_handling_infrastructure())
        
        # 3. Objects with error tracking
        sections.append(self._generate_objects_with_error_tracking())
        
        # 4. Mandatory flow with error recovery
        sections.append(self._generate_error_aware_flow())
        
        # 5. Questions with validation and error handling
        sections.append(self._generate_questions_with_validation())
        
        # 6. Error display and recovery screens
        sections.append(self._generate_error_screens())
        
        # 7. Completion with error summary
        sections.append(self._generate_completion_with_errors())
        
        # Join all sections
        full_yaml = '\n'.join(sections)
        
        # Save interview
        output_file = self.output_dir / f'form_{form_number}_baseline.yml'
        with open(output_file, 'w') as f:
            f.write(full_yaml)
        
        logger.info(f"Generated baseline interview with error handling: {output_file}")
        return output_file
    
    def _generate_metadata_with_error_context(self, form_number: str) -> str:
        """Generate metadata with error tracking info"""
        return f"""---
metadata:
  title: Form {form_number} - With Baseline Error Handling
  short title: Form {form_number}
  description: Interview with comprehensive error handling built-in
  error_handling: enabled
  debug_mode: available
  generated: {datetime.now().isoformat()}"""
    
    def _generate_error_handling_infrastructure(self) -> str:
        """Generate core error handling infrastructure"""
        return """---
include:
  - docassemble.base:data/questions/basic-questions.yml
---
features:
  debug: True
  question help button: True
  question back button: True
  progress bar: True
---
# Error Handling Infrastructure
---
objects:
  - user: Individual
  - validation_errors: DAList
  - error_log: DAList
  - field_errors: DADict
---
# Initialize error handling
initial: True
code: |
  validation_errors = DAList()
  error_log = DAList()
  field_errors = DADict()
  debug_mode = user_info().interview_metadata.get("debug", False)
  error_count = 0
---
# Global error handler
code: |
  def handle_error(context, error_type, details):
    '''Global error handler'''
    error_entry = {
      'timestamp': current_datetime(),
      'context': context,
      'type': error_type,
      'details': details
    }
    error_log.append(error_entry)
    
    if debug_mode:
      log(f"ERROR in {context}: {error_type} - {details}", 'error')
    
    return error_entry
---
# Field validation wrapper
code: |
  def validate_field(field_name, value, rules):
    '''Validate a field and track errors'''
    errors = []
    
    # Required check
    if rules.get('required') and not value:
      errors.append(f"{field_name} is required")
    
    # Type checks
    field_type = rules.get('type')
    if value and field_type:
      if field_type == 'email':
        import re
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', str(value)):
          errors.append(f"{field_name} must be a valid email")
      
      elif field_type == 'phone':
        import re
        phone = re.sub(r'[^0-9]', '', str(value))
        if len(phone) not in [10, 11]:
          errors.append(f"{field_name} must be a valid phone number")
      
      elif field_type == 'postal_code':
        import re
        if not re.match(r'^[A-Z]\d[A-Z]\s?\d[A-Z]\d$', str(value).upper()):
          errors.append(f"{field_name} must be a valid postal code")
    
    # Track errors
    if errors:
      field_errors[field_name] = errors
      for error in errors:
        validation_errors.append({'field': field_name, 'error': error})
    
    return len(errors) == 0
---
# Safe value getter with error handling
code: |
  def safe_get(obj, attr, default=""):
    '''Safely get object attribute with error handling'''
    try:
      if hasattr(obj, attr):
        val = getattr(obj, attr)
        return val if val is not None else default
      return default
    except Exception as e:
      handle_error(f"safe_get({attr})", "AttributeError", str(e))
      return default"""
    
    def _generate_objects_with_error_tracking(self) -> str:
        """Generate objects that track their own errors"""
        return """---
# Domain objects with error tracking
objects:
  - spouse: Individual
  - income_info: DAObject
  - expense_info: DAObject
---
# Initialize objects with error tracking
code: |
  income_info.errors = []
  expense_info.errors = []"""
    
    def _generate_error_aware_flow(self) -> str:
        """Generate flow that handles errors gracefully"""
        return """---
mandatory: True
code: |
  try:
    # Introduction with error status
    intro_with_status
    
    # Collect user info with validation
    user_info_valid = False
    while not user_info_valid:
      user.name.first
      if validate_field("First Name", user.name.first, {'required': True}):
        user_info_valid = True
      else:
        show_validation_error
    
    user.birthdate
    
    # Marital status
    is_married
    
    # Spouse info if married
    if is_married:
      spouse.name.first
    
    # Financial info with validation
    income_validated
    expenses_validated
    
    # Review with error summary
    if len(validation_errors) > 0:
      review_with_errors
    else:
      review_screen
    
    # Complete
    final_screen
    
  except Exception as e:
    handle_error("mandatory_flow", "FlowError", str(e))
    error_recovery_screen"""
    
    def _generate_questions_with_validation(self) -> str:
        """Generate questions that include validation"""
        return """---
question: |
  Welcome to Form 13
subquestion: |
  This interview includes comprehensive error handling.
  
  % if len(error_log) > 0:
  <div class="alert alert-warning">
    Previous errors detected: ${ len(error_log) }
  </div>
  % endif
  
  % if debug_mode:
  <div class="alert alert-info">
    Debug mode is enabled
  </div>
  % endif
field: intro_with_status
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
  - Date of Birth: user.birthdate
    datatype: date
    required: True
    validation messages:
      required: |
        Date of birth is required
  - Email: user.email
    datatype: email
    required: False
    validation messages:
      datatype: |
        Please enter a valid email address
validation code: |
  # Custom validation
  if user.name.first and len(user.name.first) < 2:
    validation_error("First name must be at least 2 characters")
  
  if defined('user.birthdate'):
    age = date_difference(starting=user.birthdate, ending=today()).years
    if age < 18:
      validation_error("You must be 18 or older")
    elif age > 120:
      validation_error("Please enter a valid birth date")
---
question: |
  Marital Status
yesno: is_married
---
question: |
  Spouse Information
fields:
  - First Name: spouse.name.first
    required: True
  - Last Name: spouse.name.last
    required: True
---
question: |
  Income Information
fields:
  - Monthly Employment Income: income_info.employment
    datatype: currency
    min: 0
    required: True
  - Other Income: income_info.other
    datatype: currency
    min: 0
    required: False
validation code: |
  total = income_info.employment + (income_info.other if defined('income_info.other') else 0)
  if total < 0:
    validation_error("Total income cannot be negative")
  income_info.total = total
continue button field: income_validated
---
question: |
  Monthly Expenses
fields:
  - Housing: expense_info.housing
    datatype: currency
    min: 0
    required: True
  - Food: expense_info.food
    datatype: currency
    min: 0
    required: True
  - Transportation: expense_info.transport
    datatype: currency
    min: 0
    required: False
validation code: |
  expense_info.total = (
    expense_info.housing + 
    expense_info.food + 
    (expense_info.transport if defined('expense_info.transport') else 0)
  )
  if expense_info.total > income_info.total * 2:
    warning("Expenses exceed twice your income - please verify")
continue button field: expenses_validated"""
    
    def _generate_error_screens(self) -> str:
        """Generate error display and recovery screens"""
        return """---
event: show_validation_error
question: |
  Validation Error
subquestion: |
  Please correct the following errors:
  
  % for field, errors in field_errors.items():
  **${ field }:**
  % for error in errors:
  - ${ error }
  % endfor
  % endfor
buttons:
  - Try Again: restart
---
event: error_recovery_screen
question: |
  Error Recovery
subquestion: |
  An error occurred during the interview.
  
  % if len(error_log) > 0:
  **Recent Errors:**
  % for error in error_log[-5:]:
  - ${ error['context'] }: ${ error['type'] }
  % endfor
  % endif
  
  **Options:**
  - Try restarting the interview
  - Contact support if the problem persists
  
  % if debug_mode:
  **Debug Information:**
  Session: ${ user_info().session }
  % endif
buttons:
  - Restart: restart
  - Exit: exit
---
event: review_with_errors
question: |
  Review with Warnings
subquestion: |
  <div class="alert alert-warning">
    There are ${ len(validation_errors) } validation warnings.
    You can proceed, but please review:
  </div>
  
  % for error in validation_errors[:10]:
  - ${ error['field'] }: ${ error['error'] }
  % endfor
  
  **Information Collected:**
  - Name: ${ safe_get(user, 'name.full()', 'Not provided') }
  - Birth Date: ${ safe_get(user, 'birthdate', 'Not provided') }
  % if is_married:
  - Spouse: ${ safe_get(spouse, 'name.full()', 'Not provided') }
  % endif
  - Monthly Income: ${ currency(safe_get(income_info, 'total', 0)) }
  - Monthly Expenses: ${ currency(safe_get(expense_info, 'total', 0)) }
buttons:
  - Continue Anyway: continue
  - Go Back: restart"""
    
    def _generate_completion_with_errors(self) -> str:
        """Generate completion screen with error summary"""
        return """---
event: review_screen
question: |
  Review Your Information
subquestion: |
  % if len(validation_errors) == 0:
  <div class="alert alert-success">
    ✓ All information validated successfully
  </div>
  % endif
  
  **Personal Information:**
  - Name: ${ user.name.full() }
  - Birth Date: ${ user.birthdate }
  - Email: ${ safe_get(user, 'email', 'Not provided') }
  
  % if is_married:
  **Spouse:**
  - Name: ${ spouse.name.full() }
  % endif
  
  **Financial Summary:**
  - Monthly Income: ${ currency(income_info.total) }
  - Monthly Expenses: ${ currency(expense_info.total) }
  - Net: ${ currency(income_info.total - expense_info.total) }
buttons:
  - Continue: continue
---
event: final_screen
question: |
  Interview Complete
subquestion: |
  % if len(error_log) == 0:
  <div class="alert alert-success">
    ✓ Interview completed without errors
  </div>
  % else:
  <div class="alert alert-info">
    Interview completed with ${ len(error_log) } logged events
  </div>
  % endif
  
  Thank you for completing Form 13.
  
  **Summary:**
  - Fields Completed: ✓
  - Validation Passed: ${ "✓" if len(validation_errors) == 0 else str(len(validation_errors)) + " warnings" }
  - Errors Logged: ${ len(error_log) }
  
  % if debug_mode:
  **Debug Summary:**
  - Session: ${ user_info().session }
  - Duration: Started at intro
  % endif
buttons:
  - Exit: exit
  - Restart: restart"""


def main():
    """Generate baseline interview with error handling"""
    generator = BaselineErrorHandlingGenerator()
    
    # Generate Form 13 with baseline error handling
    output = generator.generate_baseline_interview("13")
    print(f"✅ Generated baseline interview with error handling: {output}")
    
    # Generate a test index
    index_content = f"""---
metadata:
  title: Baseline Error Handling Interviews
  short title: Baseline Tests
---
mandatory: True
question: |
  Baseline Error Handling Interviews
subquestion: |
  ## Interviews with Error Handling as Foundation
  
  ### Form 13 with Baseline Error Handling
  **[Form 13 Baseline](/interview?i=docassemble.webapp:ontario-family-law/utilities/baseline_interviews/form_13_baseline.yml)**
  
  This interview includes:
  - ✅ Error handling infrastructure
  - ✅ Field validation with messages
  - ✅ Error recovery screens
  - ✅ Safe value access
  - ✅ Debug mode support
  - ✅ Error logging and tracking
  - ✅ Validation warnings
  - ✅ Error summary in completion
  
  Test with `?debug=1` to see debug information.
buttons:
  - Exit: exit"""
    
    index_path = Path('baseline_interviews') / 'index.yml'
    with open(index_path, 'w') as f:
        f.write(index_content)
    
    print(f"✅ Generated index: {index_path}")
    print("\nAccess at: /interview?i=docassemble.webapp:ontario-family-law/utilities/baseline_interviews/index.yml")


if __name__ == "__main__":
    main()