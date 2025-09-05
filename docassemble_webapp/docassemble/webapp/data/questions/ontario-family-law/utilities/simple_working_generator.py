#!/usr/bin/env python3
"""
Simple Working Interview Generator
Builds Docassemble interviews incrementally from parsed data and domain mappings
Focuses on creating WORKING interviews with proper object mapping
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SimpleWorkingGenerator:
    """Generate working Docassemble interviews from parsed data and domain mappings"""
    
    def __init__(self):
        self.workflow_dir = Path('workflow_output')
        self.output_dir = Path('test_working_interviews')
        self.output_dir.mkdir(exist_ok=True)
        
        # Load domain mappings
        self.domain_mappings = self._load_domain_mappings()
        self.field_mappings = self._load_field_mappings()
        
    def _load_domain_mappings(self) -> Dict:
        """Load domain mappings from JSON file"""
        mapping_file = self.workflow_dir / 'domain_mappings.json'
        if mapping_file.exists():
            with open(mapping_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _load_field_mappings(self) -> Dict:
        """Load field mappings from JSON file"""
        mapping_file = self.workflow_dir / 'field_mappings.json'
        if mapping_file.exists():
            with open(mapping_file, 'r') as f:
                return json.load(f)
        return {}
    
    def generate_minimal_working_interview(self, form_number: str = "13") -> Path:
        """Generate a minimal working interview for testing"""
        
        logger.info(f"Generating minimal working interview for Form {form_number}")
        
        # Start with basic YAML structure
        yaml_content = []
        
        # 1. Metadata
        yaml_content.append(self._generate_metadata(form_number))
        
        # 2. Modules and includes
        yaml_content.append(self._generate_includes())
        
        # 3. Objects - Use proper Docassemble objects
        yaml_content.append(self._generate_objects())
        
        # 4. Mandatory flow
        yaml_content.append(self._generate_mandatory_flow())
        
        # 5. Introduction screen
        yaml_content.append(self._generate_intro_question(form_number))
        
        # 6. Basic person questions using Individual object
        yaml_content.append(self._generate_person_questions())
        
        # 7. Simple financial questions
        yaml_content.append(self._generate_financial_questions())
        
        # 8. Review screen
        yaml_content.append(self._generate_review())
        
        # 9. Completion screen
        yaml_content.append(self._generate_completion())
        
        # Join all sections
        full_yaml = '\n'.join(yaml_content)
        
        # Save the interview
        output_file = self.output_dir / f'form_{form_number}_minimal_working.yml'
        with open(output_file, 'w') as f:
            f.write(full_yaml)
        
        logger.info(f"Generated minimal working interview: {output_file}")
        return output_file
    
    def _generate_metadata(self, form_number: str) -> str:
        """Generate metadata section"""
        return f"""---
metadata:
  title: Form {form_number} - Minimal Working Interview
  short title: Form {form_number}
  description: Test interview to validate object mapping and flow
  authors:
    - name: Simple Working Generator
  generated: {datetime.now().isoformat()}"""
    
    def _generate_includes(self) -> str:
        """Generate includes and modules"""
        return """---
include:
  - docassemble.base:data/questions/basic-questions.yml
---
modules:
  - .debug_helpers
---
features:
  debug: True
  question help button: True
  progress bar: True"""
    
    def _generate_objects(self) -> str:
        """Generate proper Docassemble objects"""
        return """---
objects:
  - user: Individual
  - spouse: Individual
  - children: DAList.using(object_type=Individual)
  - income: DAObject
  - expenses: DAObject
  - assets: DAList.using(object_type=DAObject)
  - debts: DAList.using(object_type=DAObject)"""
    
    def _generate_mandatory_flow(self) -> str:
        """Generate mandatory flow"""
        return """---
mandatory: True
code: |
  # Simple linear flow
  intro_screen
  user.name.first
  user.birthdate
  
  # Check if married
  if is_married:
    spouse.name.first
    spouse.birthdate
  
  # Children
  if has_children:
    children.gather()
  
  # Financial info
  income.employment
  income.total_monthly
  
  expenses.housing
  expenses.total_monthly
  
  # Review
  review_screen
  
  # Done
  final_screen"""
    
    def _generate_intro_question(self, form_number: str) -> str:
        """Generate introduction question"""
        return f"""---
question: |
  Form {form_number} Interview
subquestion: |
  This is a test interview to validate Docassemble object mapping.
  
  We will collect:
  - Your personal information
  - Family information
  - Basic financial details
  
  This should take about 5 minutes.
field: intro_screen
continue button field: intro_screen"""
    
    def _generate_person_questions(self) -> str:
        """Generate person-related questions using Individual object"""
        return """---
question: |
  Your Information
fields:
  - First Name: user.name.first
    required: True
  - Last Name: user.name.last
    required: True
  - Date of Birth: user.birthdate
    datatype: date
    required: True
---
question: |
  Contact Information
fields:
  - Street Address: user.address.address
    required: True
  - City: user.address.city
    required: True
  - Province: user.address.state
    default: "ON"
  - Postal Code: user.address.postal_code
    required: True
  - Phone: user.phone_number
  - Email: user.email
    datatype: email
---
question: |
  Marital Status
fields:
  - Are you married?: is_married
    datatype: yesno
---
question: |
  Spouse Information
fields:
  - First Name: spouse.name.first
    required: True
  - Last Name: spouse.name.last
    required: True
  - Date of Birth: spouse.birthdate
    datatype: date
---
question: |
  Children
fields:
  - Do you have children?: has_children
    datatype: yesno
---
question: |
  Child Information
fields:
  - First Name: children[i].name.first
    required: True
  - Last Name: children[i].name.last
    required: True
  - Date of Birth: children[i].birthdate
    datatype: date
    required: True
---
question: |
  Any more children?
yesno: children.there_is_another"""
    
    def _generate_financial_questions(self) -> str:
        """Generate financial questions"""
        return """---
question: |
  Employment Income
fields:
  - Are you employed?: income.employment
    datatype: yesno
  - Employer Name: income.employer_name
    show if: income.employment
  - Monthly Income: income.total_monthly
    datatype: currency
    min: 0
    required: True
---
question: |
  Monthly Expenses
fields:
  - Housing (rent/mortgage): expenses.housing
    datatype: currency
    min: 0
    required: True
  - Food: expenses.food
    datatype: currency
    min: 0
  - Transportation: expenses.transportation
    datatype: currency
    min: 0
  - Other: expenses.other
    datatype: currency
    min: 0
---
code: |
  expenses.total_monthly = (
    expenses.housing + 
    expenses.food + 
    expenses.transportation + 
    expenses.other
  )"""
    
    def _generate_review(self) -> str:
        """Generate review screen"""
        return """---
event: review_screen
question: |
  Review Your Information
subquestion: |
  Please review the information you've provided:
  
  **Personal Information:**
  - Name: ${ user.name.full() }
  - Date of Birth: ${ user.birthdate }
  - Address: ${ user.address.on_one_line() }
  
  % if is_married:
  **Spouse:**
  - Name: ${ spouse.name.full() }
  - Date of Birth: ${ spouse.birthdate }
  % endif
  
  % if has_children:
  **Children:**
  % for child in children:
  - ${ child.name.full() } (DOB: ${ child.birthdate })
  % endfor
  % endif
  
  **Financial Summary:**
  - Monthly Income: ${ currency(income.total_monthly) }
  - Monthly Expenses: ${ currency(expenses.total_monthly) }
  - Net: ${ currency(income.total_monthly - expenses.total_monthly) }
buttons:
  - Continue: continue"""
    
    def _generate_completion(self) -> str:
        """Generate completion screen"""
        return """---
event: final_screen
question: |
  Interview Complete
subquestion: |
  Thank you for completing this interview.
  
  Your information has been collected successfully.
  
  This was a test interview to validate the system.
buttons:
  - Exit: exit
  - Restart: restart"""
    
    def generate_from_domain_mappings(self, form_number: str = "13") -> Path:
        """Generate interview using actual domain mappings"""
        
        logger.info(f"Generating interview from domain mappings for Form {form_number}")
        
        # Get entities for this form
        entities = self.domain_mappings.get('entities', {})
        
        # Filter to relevant entities
        relevant_entities = {}
        for entity_id, entity_data in entities.items():
            # Include person and financial entities for Form 13
            if entity_data['entity_type'] in ['person', 'financial', 'property']:
                relevant_entities[entity_id] = entity_data
        
        logger.info(f"Found {len(relevant_entities)} relevant entities")
        
        # Generate interview sections
        yaml_content = []
        
        # 1. Metadata
        yaml_content.append(self._generate_metadata_from_mappings(form_number))
        
        # 2. Includes
        yaml_content.append(self._generate_includes())
        
        # 3. Objects from domain mappings
        yaml_content.append(self._generate_objects_from_mappings(relevant_entities))
        
        # 4. Mandatory flow from entities
        yaml_content.append(self._generate_flow_from_mappings(relevant_entities))
        
        # 5. Questions for each entity
        for entity_id, entity_data in relevant_entities.items():
            question = self._generate_entity_question(entity_id, entity_data)
            if question:
                yaml_content.append(question)
        
        # 6. Completion
        yaml_content.append(self._generate_completion())
        
        # Save interview
        full_yaml = '\n'.join(yaml_content)
        output_file = self.output_dir / f'form_{form_number}_from_mappings.yml'
        
        with open(output_file, 'w') as f:
            f.write(full_yaml)
        
        logger.info(f"Generated interview from mappings: {output_file}")
        return output_file
    
    def _generate_metadata_from_mappings(self, form_number: str) -> str:
        """Generate metadata from mappings"""
        return f"""---
metadata:
  title: Form {form_number} - Generated from Domain Mappings
  short title: Form {form_number}
  description: Interview generated from domain object mappings
  generated: {datetime.now().isoformat()}"""
    
    def _generate_objects_from_mappings(self, entities: Dict) -> str:
        """Generate objects section from domain mappings"""
        object_lines = ["---", "objects:"]
        
        for entity_id, entity_data in entities.items():
            var_name = entity_data.get('variable_name', entity_id)
            da_type = entity_data.get('docassemble_type', 'DAObject')
            cardinality = entity_data.get('cardinality', 'single')
            
            if cardinality == 'multiple':
                object_lines.append(f"  - {var_name}: DAList.using(object_type={da_type})")
            else:
                object_lines.append(f"  - {var_name}: {da_type}")
        
        return '\n'.join(object_lines)
    
    def _generate_flow_from_mappings(self, entities: Dict) -> str:
        """Generate mandatory flow from entities"""
        flow_lines = ["---", "mandatory: True", "code: |"]
        flow_lines.append("  intro_seen")
        
        # Add entity collection in order
        person_entities = [e for e in entities.values() if e['entity_type'] == 'person']
        financial_entities = [e for e in entities.values() if e['entity_type'] == 'financial']
        property_entities = [e for e in entities.values() if e['entity_type'] == 'property']
        
        # Collect person info first
        for entity in person_entities:
            var_name = entity['variable_name']
            if entity['cardinality'] == 'multiple':
                flow_lines.append(f"  {var_name}.gather()")
            else:
                flow_lines.append(f"  {var_name}_collected")
        
        # Then financial
        for entity in financial_entities:
            var_name = entity['variable_name']
            flow_lines.append(f"  {var_name}_collected")
        
        # Then property
        for entity in property_entities:
            var_name = entity['variable_name']
            if entity['cardinality'] == 'multiple':
                flow_lines.append(f"  {var_name}.gather()")
            else:
                flow_lines.append(f"  {var_name}_collected")
        
        flow_lines.append("  final_screen")
        
        # Add intro question
        flow_lines.extend([
            "---",
            "question: |",
            "  Form Interview",
            "subquestion: |",
            "  This interview will collect information for the form.",
            "field: intro_seen"
        ])
        
        return '\n'.join(flow_lines)
    
    def _generate_entity_question(self, entity_id: str, entity_data: Dict) -> str:
        """Generate question for an entity"""
        var_name = entity_data['variable_name']
        entity_name = entity_data['entity_name']
        entity_type = entity_data['entity_type']
        da_type = entity_data['docassemble_type']
        
        if entity_type == 'person' and da_type == 'Individual':
            return f"""---
question: |
  {entity_name} Information
fields:
  - First Name: {var_name}.name.first
    required: True
  - Last Name: {var_name}.name.last
    required: True
  - Date of Birth: {var_name}.birthdate
    datatype: date
continue button field: {var_name}_collected"""
        
        elif entity_type == 'financial':
            return f"""---
question: |
  {entity_name}
fields:
  - Monthly Amount: {var_name}.monthly_amount
    datatype: currency
    min: 0
  - Description: {var_name}.description
    required: False
continue button field: {var_name}_collected"""
        
        elif entity_type == 'property':
            if entity_data['cardinality'] == 'multiple':
                return f"""---
question: |
  {entity_name} Item
fields:
  - Description: {var_name}[i].description
    required: True
  - Value: {var_name}[i].value
    datatype: currency
    min: 0
---
question: |
  Any more {entity_name.lower()} items?
yesno: {var_name}.there_is_another"""
            else:
                return f"""---
question: |
  {entity_name}
fields:
  - Description: {var_name}.description
  - Value: {var_name}.value
    datatype: currency
    min: 0
continue button field: {var_name}_collected"""
        
        return ""


def main():
    """Test the generator"""
    generator = SimpleWorkingGenerator()
    
    # Generate minimal working interview
    minimal_file = generator.generate_minimal_working_interview("13")
    print(f"✓ Generated minimal working interview: {minimal_file}")
    
    # Generate from domain mappings
    mapped_file = generator.generate_from_domain_mappings("13")
    print(f"✓ Generated interview from mappings: {mapped_file}")
    
    print("\nTest interviews generated in: test_working_interviews/")
    print("\nTo test, use:")
    print(f"  /interview?i=docassemble.webapp:ontario-family-law/utilities/test_working_interviews/form_13_minimal_working.yml")
    print(f"  /interview?i=docassemble.webapp:ontario-family-law/utilities/test_working_interviews/form_13_from_mappings.yml")


if __name__ == "__main__":
    main()