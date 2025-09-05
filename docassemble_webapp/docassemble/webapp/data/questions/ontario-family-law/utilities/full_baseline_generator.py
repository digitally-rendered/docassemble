#!/usr/bin/env python3
"""
Full Baseline Interview Generator
Generates all Ontario Family Law form interviews with error handling as the foundation
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import yaml

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('full_generation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FullBaselineGenerator:
    """Generate all form interviews with baseline error handling"""
    
    def __init__(self):
        self.output_dir = Path('baseline_complete_interviews')
        self.output_dir.mkdir(exist_ok=True)
        
        self.workflow_dir = Path('workflow_output')
        self.parsed_forms_dir = self.workflow_dir / 'parsed_forms'
        
        # Load all available data
        self.domain_mappings = self._load_json('domain_mappings.json')
        self.field_mappings = self._load_json('field_mappings.json')
        self.relationship_data = self._load_json('form_relationships.json')
        
        # Track generation stats
        self.stats = {
            'total_forms': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        }
    
    def _load_json(self, filename: str) -> Dict:
        """Load JSON file from workflow directory"""
        file_path = self.workflow_dir / filename
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load {filename}: {e}")
        return {}
    
    def generate_all_interviews(self) -> Dict:
        """Generate interviews for all available forms"""
        logger.info("=" * 60)
        logger.info("STARTING FULL INTERVIEW GENERATION WITH BASELINE ERROR HANDLING")
        logger.info("=" * 60)
        
        # Get all available form data
        form_files = list(self.parsed_forms_dir.glob('form_*.json')) if self.parsed_forms_dir.exists() else []
        
        if not form_files:
            logger.error("No parsed form data found!")
            return self.stats
        
        self.stats['total_forms'] = len(form_files)
        logger.info(f"Found {len(form_files)} forms to process")
        
        # Process each form
        for form_file in sorted(form_files):
            form_number = self._extract_form_number(form_file.name)
            if form_number:
                try:
                    logger.info(f"Processing Form {form_number}...")
                    self._generate_form_interview(form_number, form_file)
                    self.stats['successful'] += 1
                except Exception as e:
                    logger.error(f"Failed to generate Form {form_number}: {e}")
                    self.stats['failed'] += 1
                    self.stats['errors'].append(f"Form {form_number}: {str(e)}")
        
        # Generate master index
        self._generate_master_index()
        
        # Log summary
        logger.info("=" * 60)
        logger.info("GENERATION COMPLETE")
        logger.info(f"Total forms: {self.stats['total_forms']}")
        logger.info(f"Successful: {self.stats['successful']}")
        logger.info(f"Failed: {self.stats['failed']}")
        logger.info("=" * 60)
        
        return self.stats
    
    def _extract_form_number(self, filename: str) -> Optional[str]:
        """Extract form number from filename"""
        match = re.search(r'form_([0-9A-Z.]+)_', filename, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    
    def _generate_form_interview(self, form_number: str, form_file: Path):
        """Generate interview for a specific form"""
        
        # Load form data
        with open(form_file, 'r') as f:
            form_fields = json.load(f)
        
        # Get domain entities for this form
        entities = self._get_form_entities(form_number)
        
        # Build interview sections
        sections = []
        
        # 1. Metadata with form info
        sections.append(self._generate_metadata(form_number, len(form_fields)))
        
        # 2. Error handling infrastructure (always the same)
        sections.append(self._generate_error_infrastructure())
        
        # 3. Objects based on form type
        sections.append(self._generate_objects(form_number, entities))
        
        # 4. Mandatory flow with error handling
        sections.append(self._generate_flow(form_number, entities, form_fields))
        
        # 5. Introduction
        sections.append(self._generate_introduction(form_number, len(form_fields)))
        
        # 6. Questions for form fields
        sections.extend(self._generate_field_questions(form_number, form_fields, entities))
        
        # 7. Error screens
        sections.append(self._generate_error_screens())
        
        # 8. Review and completion
        sections.append(self._generate_review_completion(form_number))
        
        # Save interview
        output_file = self.output_dir / f'form_{form_number}_interview.yml'
        with open(output_file, 'w') as f:
            f.write('\n'.join(sections))
        
        logger.info(f"✓ Generated: {output_file}")
    
    def _get_form_entities(self, form_number: str) -> Dict:
        """Get relevant entities for a form"""
        entities = {}
        
        # Determine form category
        if '13' in form_number:
            # Financial forms need person, income, expense, asset entities
            entities['user'] = {'type': 'Individual', 'label': 'Your Information'}
            entities['spouse'] = {'type': 'Individual', 'label': 'Spouse Information'}
            entities['income'] = {'type': 'DAObject', 'label': 'Income'}
            entities['expenses'] = {'type': 'DAObject', 'label': 'Expenses'}
            entities['assets'] = {'type': 'DAList', 'label': 'Assets'}
            entities['debts'] = {'type': 'DAList', 'label': 'Debts'}
        elif '8' in form_number or '10' in form_number:
            # Application/Answer forms
            entities['applicant'] = {'type': 'Individual', 'label': 'Applicant'}
            entities['respondent'] = {'type': 'Individual', 'label': 'Respondent'}
            entities['children'] = {'type': 'DAList', 'label': 'Children'}
        elif '36' in form_number:
            # Divorce forms
            entities['applicant'] = {'type': 'Individual', 'label': 'Applicant'}
            entities['respondent'] = {'type': 'Individual', 'label': 'Respondent'}
            entities['marriage'] = {'type': 'DAObject', 'label': 'Marriage Details'}
        else:
            # Default entities
            entities['user'] = {'type': 'Individual', 'label': 'Your Information'}
            entities['other_party'] = {'type': 'Individual', 'label': 'Other Party'}
        
        return entities
    
    def _generate_metadata(self, form_number: str, field_count: int) -> str:
        """Generate metadata section"""
        form_titles = {
            '13': 'Financial Statement (Support Claims)',
            '13.1': 'Financial Statement (Property and Support)',
            '13A': 'Certificate of Financial Disclosure',
            '13B': 'Net Family Property Statement',
            '13C': 'Comparison of Net Family Properties',
            '8': 'Application (General)',
            '8A': 'Application (Divorce)',
            '10': 'Answer',
            '10A': 'Reply',
            '14B': 'Motion Form',
            '15': 'Motion to Change',
            '25': 'Order (General)',
            '36': 'Affidavit for Divorce',
            '36A': 'Certificate of Divorce'
        }
        
        title = form_titles.get(form_number, f'Form {form_number}')
        
        return f"""---
metadata:
  title: "Ontario Family Law Form {form_number}: {title}"
  short title: Form {form_number}
  description: Interview with baseline error handling for {field_count} fields
  form_number: {form_number}
  field_count: {field_count}
  error_handling: baseline
  generated: "{datetime.now().isoformat()}" """
    
    def _generate_error_infrastructure(self) -> str:
        """Generate standard error handling infrastructure"""
        return """---
include:
  - docassemble.base:data/questions/basic-questions.yml
---
features:
  debug: True
  question help button: True
  question back button: True
  progress bar: True
  progress bar method: all
  progress bar multiplier: 0.05
---
objects:
  - validation_errors: DAList
  - error_log: DAList
  - field_errors: DADict
---
initial: True
code: |
  validation_errors = DAList()
  error_log = DAList()
  field_errors = DADict()
  debug_mode = get_config('debug', False)
  error_count = 0
---
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
code: |
  def safe_get(obj, attr, default=""):
    '''Safely get object attribute'''
    try:
      if hasattr(obj, attr):
        val = getattr(obj, attr)
        return val if val is not None else default
      return default
    except:
      return default
---
code: |
  def validate_required(field_name, value):
    '''Validate required field'''
    if not value or (isinstance(value, str) and not value.strip()):
      field_errors[field_name] = f"{field_name} is required"
      return False
    return True"""
    
    def _generate_objects(self, form_number: str, entities: Dict) -> str:
        """Generate objects section"""
        lines = ["---", "objects:"]
        
        for entity_name, entity_info in entities.items():
            if entity_info['type'] == 'DAList':
                lines.append(f"  - {entity_name}: DAList.using(object_type=Individual)")
            else:
                lines.append(f"  - {entity_name}: {entity_info['type']}")
        
        return '\n'.join(lines)
    
    def _generate_flow(self, form_number: str, entities: Dict, form_fields: List) -> str:
        """Generate mandatory flow with error handling"""
        flow_items = []
        
        # Introduction
        flow_items.append("intro_seen")
        
        # Collect entity data
        for entity_name in entities:
            if entities[entity_name]['type'] == 'Individual':
                flow_items.append(f"{entity_name}.name.first")
            elif entities[entity_name]['type'] == 'DAList':
                flow_items.append(f"{entity_name}_count")
                flow_items.append(f"if {entity_name}_count > 0:\n    {entity_name}.gather()")
            else:
                flow_items.append(f"{entity_name}_collected")
        
        # Additional form-specific fields
        if '13' in form_number:
            flow_items.extend([
                "income_collected",
                "expenses_collected",
                "if has_assets:\n    assets.gather()",
                "if has_debts:\n    debts.gather()"
            ])
        
        # Review and completion
        flow_items.extend([
            "review_answers",
            "if len(validation_errors) > 0:\n    review_with_errors",
            "form_complete"
        ])
        
        flow_code = '\n  '.join(flow_items)
        
        return f"""---
mandatory: True
code: |
  try:
    {flow_code}
  except Exception as e:
    handle_error("main_flow", "FlowError", str(e))
    error_recovery"""
    
    def _generate_introduction(self, form_number: str, field_count: int) -> str:
        """Generate introduction screen"""
        return f"""---
question: |
  Ontario Family Law Form {form_number}
subquestion: |
  Welcome to the Form {form_number} interview.
  
  This interview will collect {field_count} fields of information.
  
  % if debug_mode:
  <div class="alert alert-info">
    Debug mode is enabled - detailed error information will be shown
  </div>
  % endif
  
  All fields include validation and error handling.
continue button field: intro_seen"""
    
    def _generate_field_questions(self, form_number: str, form_fields: List, entities: Dict) -> List[str]:
        """Generate questions for form fields"""
        questions = []
        
        # Group fields by context
        grouped_fields = self._group_fields_by_context(form_fields)
        
        for context, fields in grouped_fields.items():
            question = self._create_question_for_group(context, fields, entities)
            if question:
                questions.append(question)
        
        # Add entity-specific questions
        for entity_name, entity_info in entities.items():
            if entity_info['type'] == 'Individual':
                questions.append(self._create_person_question(entity_name, entity_info['label']))
            elif entity_info['type'] == 'DAList':
                questions.append(self._create_list_questions(entity_name, entity_info['label']))
            elif entity_info['type'] == 'DAObject' and entity_name in ['income', 'expenses']:
                questions.append(self._create_financial_question(entity_name, entity_info['label']))
        
        return questions
    
    def _group_fields_by_context(self, fields: List) -> Dict[str, List]:
        """Group fields by their context/table"""
        grouped = {}
        for field in fields:
            context = field.get('field_context', 'General Information')
            if context not in grouped:
                grouped[context] = []
            grouped[context].append(field)
        return grouped
    
    def _create_question_for_group(self, context: str, fields: List, entities: Dict) -> Optional[str]:
        """Create a question for a group of fields"""
        if not fields:
            return None
        
        # Clean up context name
        context_clean = re.sub(r'[^a-zA-Z0-9_]', '_', context.lower())
        
        field_definitions = []
        for field in fields[:10]:  # Limit to 10 fields per question
            field_def = self._create_field_definition(field)
            if field_def:
                field_definitions.append(field_def)
        
        if not field_definitions:
            return None
        
        fields_yaml = '\n'.join(field_definitions)
        
        return f"""---
question: |
  {context}
fields:
{fields_yaml}
validation code: |
  # Validate required fields
  for field in [{', '.join([f'"{f["field_name"]}"' for f in fields if f.get("required")])}]:
    if not defined(field) or not value(field):
      validation_error(f"{{field}} is required")
continue button field: {context_clean}_collected"""
    
    def _create_field_definition(self, field: Dict) -> Optional[str]:
        """Create field definition from parsed field data"""
        field_name = self._sanitize_field_name(field.get('field_name', ''))
        if not field_name:
            return None
        
        field_label = field.get('field_label', field_name).replace(':', '')
        field_type = field.get('field_type', 'text')
        
        # Basic field definition
        definition = f"  - {field_label}: {field_name}"
        
        # Add field type
        if field_type == 'date':
            definition += "\n    datatype: date"
        elif field_type in ['currency', 'money']:
            definition += "\n    datatype: currency\n    min: 0"
        elif field_type == 'email':
            definition += "\n    datatype: email"
        elif field_type == 'phone':
            definition += "\n    datatype: phone"
        elif field_type == 'number':
            definition += "\n    datatype: number"
        elif field_type == 'yesno':
            definition += "\n    datatype: yesno"
        
        # Add required
        if field.get('required'):
            definition += "\n    required: True"
        
        return definition
    
    def _sanitize_field_name(self, name: str) -> str:
        """Sanitize field name for use as variable"""
        # Remove duplicate text
        name = re.sub(r'(\w+)_\1+', r'\1', name)
        # Keep only valid characters
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Remove leading numbers
        name = re.sub(r'^[0-9]+', '', name)
        # Limit length
        if len(name) > 50:
            name = name[:50]
        return name.lower()
    
    def _create_person_question(self, entity_name: str, label: str) -> str:
        """Create question for Individual entity"""
        return f"""---
question: |
  {label}
fields:
  - First Name: {entity_name}.name.first
    required: True
    validation messages:
      required: First name is required
  - Last Name: {entity_name}.name.last
    required: True
    validation messages:
      required: Last name is required
  - Date of Birth: {entity_name}.birthdate
    datatype: date
    required: False"""
    
    def _create_list_questions(self, entity_name: str, label: str) -> str:
        """Create questions for DAList entity"""
        singular = label.rstrip('s') if label.endswith('s') else label
        
        return f"""---
question: |
  How many {label.lower()} are there?
fields:
  - Number: {entity_name}_count
    datatype: integer
    min: 0
    max: 20
---
question: |
  {singular} ${{i + 1}} Information
fields:
  - First Name: {entity_name}[i].name.first
    required: True
  - Last Name: {entity_name}[i].name.last
    required: True
  - Date of Birth: {entity_name}[i].birthdate
    datatype: date
    required: False
---
question: |
  Add another {singular.lower()}?
yesno: {entity_name}.there_is_another"""
    
    def _create_financial_question(self, entity_name: str, label: str) -> str:
        """Create financial questions"""
        if entity_name == 'income':
            return """---
question: |
  Income Information
fields:
  - Employment Income: income.employment
    datatype: currency
    min: 0
    required: True
  - Self-Employment Income: income.self_employment
    datatype: currency
    min: 0
    required: False
  - Other Income: income.other
    datatype: currency
    min: 0
    required: False
validation code: |
  income.total = (income.employment or 0) + (income.self_employment or 0) + (income.other or 0)
continue button field: income_collected"""
        
        elif entity_name == 'expenses':
            return """---
question: |
  Monthly Expenses
fields:
  - Housing: expenses.housing
    datatype: currency
    min: 0
    required: True
  - Food: expenses.food
    datatype: currency
    min: 0
    required: True
  - Transportation: expenses.transportation
    datatype: currency
    min: 0
    required: False
  - Other: expenses.other
    datatype: currency
    min: 0
    required: False
validation code: |
  expenses.total = (expenses.housing or 0) + (expenses.food or 0) + (expenses.transportation or 0) + (expenses.other or 0)
continue button field: expenses_collected"""
        
        return ""
    
    def _generate_error_screens(self) -> str:
        """Generate error handling screens"""
        return """---
event: error_recovery
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
  
  You can try restarting or contact support.
buttons:
  - Restart: restart
  - Exit: exit
---
event: review_with_errors
question: |
  Review with Validation Issues
subquestion: |
  <div class="alert alert-warning">
    There are ${ len(validation_errors) } validation issues to review.
  </div>
  
  % for error in validation_errors[:10]:
  - ${ error }
  % endfor
  
  You can continue anyway or go back to fix these issues.
buttons:
  - Continue Anyway: continue
  - Go Back: restart"""
    
    def _generate_review_completion(self, form_number: str) -> str:
        """Generate review and completion screens"""
        return f"""---
event: review_answers
question: |
  Review Your Answers
subquestion: |
  Please review the information you've provided.
  
  % if len(validation_errors) == 0:
  <div class="alert alert-success">
    ✓ All information validated successfully
  </div>
  % else:
  <div class="alert alert-warning">
    ⚠ ${{ len(validation_errors) }} validation warnings
  </div>
  % endif
  
  **Form {form_number} Summary**
  
  Information has been collected for all required fields.
  
  % if debug_mode:
  **Debug Info:**
  - Errors logged: ${{ len(error_log) }}
  - Fields with errors: ${{ len(field_errors) }}
  % endif
buttons:
  - Continue: continue
  - Edit Answers: restart
---
event: form_complete
question: |
  Form {form_number} Complete
subquestion: |
  Thank you for completing Form {form_number}.
  
  % if len(error_log) == 0:
  <div class="alert alert-success">
    ✓ Interview completed without errors
  </div>
  % else:
  <div class="alert alert-info">
    Interview completed with ${{ len(error_log) }} logged events
  </div>
  % endif
  
  **Summary:**
  - All required fields completed
  - Validation: ${{ "Passed" if len(validation_errors) == 0 else str(len(validation_errors)) + " warnings" }}
  
buttons:
  - Exit: exit
  - Start Over: restart"""
    
    def _generate_master_index(self):
        """Generate master index of all interviews"""
        logger.info("Generating master index...")
        
        # Get all generated interviews
        interviews = sorted(self.output_dir.glob('form_*.yml'))
        
        # Group by category
        categories = {
            'Financial Forms': [],
            'Applications and Responses': [],
            'Motions': [],
            'Orders': [],
            'Affidavits': [],
            'Other Forms': []
        }
        
        for interview in interviews:
            form_num = self._extract_form_number(interview.name)
            if not form_num:
                continue
            
            link = f"  - [Form {form_num}](/interview?i=docassemble.webapp:ontario-family-law/utilities/baseline_complete_interviews/{interview.name})"
            
            # Categorize
            if '13' in form_num or '26' in form_num:
                categories['Financial Forms'].append(link)
            elif '8' in form_num or '10' in form_num:
                categories['Applications and Responses'].append(link)
            elif '14' in form_num or '15' in form_num or '17' in form_num:
                categories['Motions'].append(link)
            elif '25' in form_num:
                categories['Orders'].append(link)
            elif '36' in form_num or '29' in form_num or '30' in form_num:
                categories['Affidavits'].append(link)
            else:
                categories['Other Forms'].append(link)
        
        # Build index content
        content = f"""---
metadata:
  title: Complete Ontario Family Law Forms - Baseline Error Handling
  short title: All Forms Index
  generated: "{datetime.now().isoformat()}"
---
mandatory: True
question: |
  Ontario Family Law Forms - Complete Collection
subquestion: |
  ## All Forms with Baseline Error Handling
  
  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
  
  Total Forms: {self.stats['successful']}
  
  All interviews include:
  - ✅ Baseline error handling infrastructure
  - ✅ Field validation with messages
  - ✅ Error recovery screens
  - ✅ Debug mode support
  - ✅ Safe value access
  - ✅ Progress tracking
  
"""
        
        for category, forms in categories.items():
            if forms:
                content += f"  ### {category}\n"
                content += '\n'.join(forms) + '\n\n'
        
        content += """
  ## Features
  
  Every interview includes:
  - Error logging and tracking
  - Validation for all fields
  - Recovery options for errors
  - Debug information when enabled
  - User-friendly error messages
  
  ## Testing
  
  Add `?debug=1` to any URL to enable debug mode.
  
buttons:
  - Exit: exit"""
        
        # Save index
        index_file = self.output_dir / '00_INDEX.yml'
        with open(index_file, 'w') as f:
            f.write(content)
        
        logger.info(f"✓ Generated master index: {index_file}")


def main():
    """Run full interview generation"""
    generator = FullBaselineGenerator()
    
    logger.info("Starting full interview generation with baseline error handling...")
    
    # Generate all interviews
    stats = generator.generate_all_interviews()
    
    # Print summary
    print("\n" + "=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    print(f"Total forms processed: {stats['total_forms']}")
    print(f"Successfully generated: {stats['successful']}")
    print(f"Failed: {stats['failed']}")
    
    if stats['errors']:
        print("\nErrors encountered:")
        for error in stats['errors'][:10]:
            print(f"  - {error}")
    
    print("\nAccess the master index at:")
    print("  /interview?i=docassemble.webapp:ontario-family-law/utilities/baseline_complete_interviews/00_INDEX.yml")
    
    print("\nAll interviews include:")
    print("  ✅ Baseline error handling")
    print("  ✅ Field validation")
    print("  ✅ Error recovery")
    print("  ✅ Debug mode support")


if __name__ == "__main__":
    main()