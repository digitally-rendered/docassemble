#!/usr/bin/env python3
"""
Ontario Family Law Common Interview Framework
Creates a shared foundation for all Ontario family law forms
Generates valid Docassemble YAML with proper question structures
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field as dataclass_field
from datetime import datetime


@dataclass
class OntarioField:
    """Represents a field in an Ontario form with proper mapping"""
    field_id: str
    label: str
    variable_name: str
    field_type: str = "text"
    required: bool = False
    validation: Optional[str] = None
    help_text: Optional[str] = None
    choices: Optional[List[str]] = None
    section: Optional[str] = None
    
    @classmethod
    def from_parsed(cls, parsed_field: Dict) -> 'OntarioField':
        """Create from parsed field data"""
        # Clean up the label
        label = parsed_field.get('field_label', '').strip()
        label = re.sub(r':\s*$', '', label)  # Remove trailing colons
        label = re.sub(r'\s+', ' ', label)  # Normalize whitespace
        
        # Generate clean variable name
        var_name = cls._generate_variable_name(label, parsed_field.get('field_name', ''))
        
        # Determine field type
        field_type = cls._determine_field_type(parsed_field)
        
        return cls(
            field_id=parsed_field.get('field_id', ''),
            label=label,
            variable_name=var_name,
            field_type=field_type,
            required=parsed_field.get('required', False),
            validation=parsed_field.get('validation_rules'),
            help_text=parsed_field.get('help_text'),
            section=cls._determine_section(label)
        )
    
    @staticmethod
    def _generate_variable_name(label: str, field_name: str) -> str:
        """Generate a clean variable name"""
        # Use field_name if it's already clean
        if field_name and not field_name.count('_') > 5:
            base = field_name
        else:
            base = label
        
        # Clean up the base
        base = re.sub(r'[^\w\s]', '', base.lower())
        base = re.sub(r'\s+', '_', base)
        
        # Remove duplicate words
        parts = base.split('_')
        seen = set()
        unique_parts = []
        for part in parts:
            if part not in seen and part:
                seen.add(part)
                unique_parts.append(part)
        
        result = '_'.join(unique_parts[:5])  # Limit to 5 parts
        return result if result else 'field'
    
    @staticmethod
    def _determine_field_type(parsed_field: Dict) -> str:
        """Determine the Docassemble field type"""
        field_type = parsed_field.get('field_type', 'text').lower()
        label_lower = parsed_field.get('field_label', '').lower()
        
        if field_type == 'date' or 'date' in label_lower:
            return 'date'
        elif field_type == 'currency' or any(word in label_lower for word in ['$', 'amount', 'income', 'expense']):
            return 'currency'
        elif field_type == 'phone' or 'phone' in label_lower:
            return 'phone'
        elif field_type == 'email' or 'email' in label_lower:
            return 'email'
        elif field_type == 'checkbox' or '[]' in parsed_field.get('field_label', ''):
            return 'yesno'
        elif 'address' in label_lower:
            return 'address'
        else:
            return 'text'
    
    @staticmethod
    def _determine_section(label: str) -> str:
        """Determine which section this field belongs to"""
        label_lower = label.lower()
        
        if any(word in label_lower for word in ['court', 'file', 'municipality']):
            return 'court_information'
        elif any(word in label_lower for word in ['applicant', 'petitioner']):
            return 'applicant_information'
        elif any(word in label_lower for word in ['respondent', 'responding']):
            return 'respondent_information'
        elif 'child' in label_lower:
            return 'children_information'
        elif any(word in label_lower for word in ['income', 'expense', 'asset', 'debt', 'financial']):
            return 'financial_information'
        elif any(word in label_lower for word in ['marriage', 'divorce', 'separation']):
            return 'marriage_information'
        else:
            return 'additional_information'


class CommonInterviewFramework:
    """Generates the common interview framework for Ontario forms"""
    
    # Common field patterns shared across forms
    COMMON_PATTERNS = {
        'applicant_name': {
            'label': 'Full legal name of applicant',
            'variable': 'applicant.name.text',
            'type': 'text',
            'required': True
        },
        'applicant_address': {
            'label': 'Address of applicant',
            'variable': 'applicant.address.address',
            'type': 'text',
            'required': True
        },
        'respondent_name': {
            'label': 'Full legal name of respondent',
            'variable': 'respondent.name.text',
            'type': 'text',
            'required': True
        },
        'respondent_address': {
            'label': 'Address of respondent',
            'variable': 'respondent.address.address',
            'type': 'text',
            'required': True
        },
        'court_file_number': {
            'label': 'Court file number',
            'variable': 'court.file_number',
            'type': 'text',
            'required': True
        },
        'court_location': {
            'label': 'Court location',
            'variable': 'court.location',
            'type': 'text',
            'required': True
        }
    }
    
    @classmethod
    def generate_base_yaml(cls) -> str:
        """Generate the base YAML structure common to all forms"""
        return """---
metadata:
  title: |
    Ontario Family Law Forms
  short title: |
    Ontario Forms
  description: |
    Common framework for Ontario family law forms
  authors:
    - name: Ontario Family Law System
  revision_date: {date}
---
include:
  - docassemble.base:data/questions/basic-questions.yml
---
features:
  navigation: True
  progress bar: True
  progress bar method: stepped
  question back button: True
  navigation back button: True
---
objects:
  - applicant: Individual
  - respondent: Individual  
  - court: DAObject
  - children: DAList.using(object_type=Individual, there_are_any=False)
---""".format(date=datetime.now().strftime('%Y-%m-%d'))
    
    @classmethod
    def generate_common_questions(cls) -> str:
        """Generate common question blocks used across forms"""
        return """
---
question: |
  Court Information
fields:
  - Court file number: court.file_number
    required: True
  - Court location: court.location
    required: True
    code: |
      ontario_court_locations()
---
question: |
  Applicant Information
fields:
  - Full legal name: applicant.name.text
    required: True
  - Address: applicant.address.address
    required: True
  - City: applicant.address.city
    required: True
  - Province: applicant.address.province
    default: "Ontario"
  - Postal Code: applicant.address.postal_code
    required: True
    validation code: |
      ontario_postal_code_validation(applicant.address.postal_code)
  - Phone number: applicant.phone_number
    required: False
    datatype: phone
  - Email: applicant.email
    required: False
    datatype: email
---
question: |
  Respondent Information
fields:
  - Full legal name: respondent.name.text
    required: True
  - Address: respondent.address.address
    required: True
  - City: respondent.address.city
    required: True
  - Province: respondent.address.province
    default: "Ontario"
  - Postal Code: respondent.address.postal_code
    required: True
    validation code: |
      ontario_postal_code_validation(respondent.address.postal_code)
  - Phone number: respondent.phone_number
    required: False
    datatype: phone
  - Email: respondent.email
    required: False
    datatype: email
---
question: |
  Are there any children?
yesno: children.there_are_any
---
question: |
  How many children are there?
fields:
  - Number of children: children.target_number
    datatype: integer
    min: 1
---
question: |
  Information about ${ ordinal(i) } child
fields:
  - Full name: children[i].name.text
    required: True
  - Date of birth: children[i].birthdate
    datatype: date
    required: True
  - Currently living with: children[i].living_with
    choices:
      - Applicant
      - Respondent  
      - Both (shared)
      - Other
---"""
    
    @classmethod
    def generate_validation_code(cls) -> str:
        """Generate validation functions"""
        return """
---
code: |
  def ontario_postal_code_validation(postal_code):
    '''Validate Ontario postal code format'''
    import re
    pattern = r'^[KLMNP]\\d[A-Z]\\s?\\d[A-Z]\\d$'
    if not re.match(pattern, postal_code.upper().replace(' ', '')):
      validation_error("Please enter a valid Ontario postal code (e.g., K1A 0B1)")
    return True
---
code: |
  def ontario_court_locations():
    '''Return list of Ontario court locations'''
    return [
      "Toronto",
      "Ottawa", 
      "London",
      "Hamilton",
      "Kitchener",
      "Windsor",
      "Barrie",
      "Kingston",
      "Thunder Bay",
      "Sudbury",
      "Peterborough",
      "Oshawa",
      "Belleville",
      "St. Catharines",
      "Brampton",
      "Mississauga",
      "North Bay",
      "Timmins",
      "Sault Ste. Marie",
      "Other"
    ]
---"""


class OntarioFormGenerator:
    """Generates complete, valid Docassemble interviews for Ontario forms"""
    
    def __init__(self, form_number: str, form_title: str = None):
        self.form_number = form_number
        self.form_title = form_title or f"Form {form_number}"
        self.fields: List[OntarioField] = []
        self.sections: Dict[str, List[OntarioField]] = {}
        
    def load_parsed_fields(self, parsed_fields_path: Path = None):
        """Load and process parsed fields"""
        if not parsed_fields_path:
            # Default path
            base_path = Path(__file__).parent
            parsed_fields_path = base_path / 'parsed_forms' / f'form_{self.form_number}_fields.json'
        
        if parsed_fields_path.exists():
            with open(parsed_fields_path, 'r') as f:
                parsed_data = json.load(f)
                
            # Convert to OntarioField objects
            for field_data in parsed_data:
                field = OntarioField.from_parsed(field_data)
                self.fields.append(field)
                
                # Group by section
                if field.section not in self.sections:
                    self.sections[field.section] = []
                self.sections[field.section].append(field)
    
    def generate_interview(self) -> str:
        """Generate complete interview YAML"""
        yaml_parts = []
        
        # Metadata
        yaml_parts.append(self._generate_metadata())
        
        # Include common framework
        yaml_parts.append(self._generate_includes())
        
        # Features
        yaml_parts.append(self._generate_features())
        
        # Objects
        yaml_parts.append(self._generate_objects())
        
        # Mandatory code block
        yaml_parts.append(self._generate_mandatory_code())
        
        # Generate questions for each section
        for section_name, section_fields in self.sections.items():
            if section_fields:  # Only if section has fields
                yaml_parts.append(self._generate_section_questions(section_name, section_fields))
        
        # Review screen
        yaml_parts.append(self._generate_review_screen())
        
        # Final screen
        yaml_parts.append(self._generate_final_screen())
        
        return '\n'.join(yaml_parts)
    
    def _generate_metadata(self) -> str:
        """Generate metadata block"""
        return f"""---
metadata:
  title: |
    Form {self.form_number}: {self.form_title}
  short title: |
    Form {self.form_number}
  description: |
    Ontario Family Law Form {self.form_number}
  authors:
    - name: Ontario Family Law System
  revision_date: {datetime.now().strftime('%Y-%m-%d')}
  form_number: "{self.form_number}"
  form_title: "{self.form_title}"
"""
    
    def _generate_includes(self) -> str:
        """Generate includes block"""
        return """---
include:
  - docassemble.base:data/questions/basic-questions.yml"""
    
    def _generate_features(self) -> str:
        """Generate features block"""
        return """---
features:
  navigation: True
  progress bar: True
  progress bar method: stepped
  question back button: True
  navigation back button: True"""
    
    def _generate_objects(self) -> str:
        """Generate objects block"""
        return """---
objects:
  - applicant: Individual
  - respondent: Individual
  - court: DAObject
  - children: DAList.using(object_type=Individual, there_are_any=False)"""
    
    def _generate_mandatory_code(self) -> str:
        """Generate mandatory code block"""
        sections_list = list(self.sections.keys())
        
        code = """---
mandatory: True
code: |
  # Interview flow control
  multi_user = True
  
  # Gather information in logical order"""
        
        # Add each section
        for section in sections_list:
            if section and self.sections.get(section):
                code += f"\n  {section}_complete"
        
        code += "\n  review_answers"
        code += "\n  form_complete"
        
        return code
    
    def _generate_section_questions(self, section_name: str, fields: List[OntarioField]) -> str:
        """Generate question block for a section"""
        # Create human-readable section title
        section_title = section_name.replace('_', ' ').title()
        
        # Skip if this is a common section (handled by framework)
        if section_name in ['court_information', 'applicant_information', 'respondent_information']:
            # Just create the completion variable
            return f"""---
code: |
  {section_name}_complete = True"""
        
        question = f"""---
question: |
  {section_title}
subquestion: |
  Please provide the following information.
fields:"""
        
        for field in fields:
            # Skip duplicate or malformed fields
            if field.variable_name.count('_') > 5 or len(field.variable_name) > 50:
                continue
                
            # Build field definition
            field_def = f"\n  - {field.label}: {field.variable_name}"
            
            if field.field_type != 'text':
                field_def += f"\n    datatype: {field.field_type}"
            
            if field.required:
                field_def += "\n    required: True"
            
            if field.help_text:
                field_def += f"\n    help: |\n      {field.help_text}"
            
            question += field_def
        
        question += f"\ncontinue button field: {section_name}_complete"
        
        return question
    
    def _generate_review_screen(self) -> str:
        """Generate review screen"""
        return """---
event: review_answers
question: |
  Review Your Answers
subquestion: |
  Please review your answers below. Click on any item to make changes.
review:
  - Edit court information: court.file_number
    button: |
      **Court File Number:** ${ court.file_number }
      
      **Court Location:** ${ court.location }
  - Edit applicant information: applicant.name.text
    button: |
      **Applicant:** ${ applicant.name.text }
      
      **Address:** ${ applicant.address.address }, ${ applicant.address.city }, ${ applicant.address.province } ${ applicant.address.postal_code }
  - Edit respondent information: respondent.name.text
    button: |
      **Respondent:** ${ respondent.name.text }
      
      **Address:** ${ respondent.address.address }, ${ respondent.address.city }, ${ respondent.address.province } ${ respondent.address.postal_code }
continue button field: review_complete"""
    
    def _generate_final_screen(self) -> str:
        """Generate final screen"""
        return f"""---
event: form_complete
question: |
  Form {self.form_number} Complete
subquestion: |
  Your Form {self.form_number} ({self.form_title}) has been completed.
  
  **Next Steps:**
  
  1. Download your completed form
  2. Print and sign where required
  3. File with the court
  
  You can download your form using the button below.
buttons:
  - Exit: exit
  - Restart: restart"""


def generate_form_interview(form_number: str, form_title: str = None, 
                           parsed_fields_path: Path = None) -> str:
    """Main function to generate a complete interview"""
    generator = OntarioFormGenerator(form_number, form_title)
    
    if parsed_fields_path or Path(f'parsed_forms/form_{form_number}_fields.json').exists():
        generator.load_parsed_fields(parsed_fields_path)
    
    return generator.generate_interview()


if __name__ == "__main__":
    # Example: Generate Form 8 interview
    form_8_yaml = generate_form_interview("8", "Application (General)")
    
    output_path = Path("generated_interviews/form_8_valid.yml")
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(form_8_yaml)
    
    print(f"Generated valid interview: {output_path}")