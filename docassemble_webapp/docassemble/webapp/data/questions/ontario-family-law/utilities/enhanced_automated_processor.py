#!/usr/bin/env python3
"""
Enhanced Automated Ontario Family Law Forms Processor
With proper docassemble object mapping and domain-driven design
"""

import os
import sys
import json
import csv
import re
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_form_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DocassembleObjectMapping:
    """Mapping configuration for docassemble objects"""
    object_type: str  # Individual, Address, DAList, etc.
    base_class: str  # The docassemble class to use
    attributes: Dict[str, Any] = field(default_factory=dict)
    methods: List[str] = field(default_factory=list)
    validation: Dict[str, str] = field(default_factory=dict)
    ontario_extensions: Dict[str, Any] = field(default_factory=dict)

class DocassembleObjectRegistry:
    """Registry of standard docassemble objects and their mappings"""
    
    STANDARD_OBJECTS = {
        # Person objects
        "party": DocassembleObjectMapping(
            object_type="Individual",
            base_class="Individual",
            attributes={
                "name": "IndividualName",
                "address": "Address",
                "phone_number": "str",
                "email": "str",
                "birthdate": "date",
                "gender": "str",
                "sin_masked": "str"  # Ontario extension
            },
            ontario_extensions={
                "lso_number": "str",  # For lawyers
                "occupation_details": "DAObject",
                "income_verification": "DAObject",
                "contact_preferences": "DAObject"
            }
        ),
        
        "child": DocassembleObjectMapping(
            object_type="Individual",
            base_class="Individual",
            attributes={
                "name": "IndividualName",
                "birthdate": "date",
                "gender": "str",
                "school": "str",
                "grade": "str"
            },
            ontario_extensions={
                "lives_with_applicant": "bool",
                "lives_with_respondent": "bool",
                "shared_custody": "bool",
                "primary_residence": "str",
                "special_needs": "bool",
                "extraordinary_expenses": "DAList"
            }
        ),
        
        # Address objects
        "address": DocassembleObjectMapping(
            object_type="Address",
            base_class="Address",
            attributes={
                "address": "str",
                "unit": "str",
                "city": "str",
                "state": "str",  # province in Canada
                "zip": "str",  # postal code
                "country": "str"
            },
            ontario_extensions={
                "ontario_postal_validation": "bool",
                "service_address_same": "bool",
                "municipality": "str"
            }
        ),
        
        # Financial objects
        "income": DocassembleObjectMapping(
            object_type="Income",
            base_class="Income",
            attributes={
                "value": "currency",
                "period": "number",
                "period_type": "str"
            },
            ontario_extensions={
                "source_type": "str",
                "employer_details": "DAObject",
                "gross_amount": "currency",
                "net_amount": "currency",
                "canada_child_benefit": "currency",
                "ontario_child_benefit": "currency"
            }
        ),
        
        "expense": DocassembleObjectMapping(
            object_type="Expense",
            base_class="Expense",
            attributes={
                "value": "currency",
                "period": "number",
                "period_type": "str"
            },
            ontario_extensions={
                "category": "str",
                "for_children": "bool",
                "special_expense": "bool"
            }
        ),
        
        "asset": DocassembleObjectMapping(
            object_type="Asset",
            base_class="Asset",
            attributes={
                "value": "currency",
                "description": "str",
                "balance": "currency"
            },
            ontario_extensions={
                "valuation_date": "date",
                "valuation_method": "str",
                "acquisition_date": "date",
                "excluded_property": "bool",
                "ownership_percentage": "number"
            }
        ),
        
        "debt": DocassembleObjectMapping(
            object_type="Debt",
            base_class="Debt",
            attributes={
                "value": "currency",
                "description": "str",
                "balance": "currency"
            },
            ontario_extensions={
                "creditor": "str",
                "monthly_payment": "currency",
                "secured": "bool",
                "joint_debt": "bool"
            }
        ),
        
        # Court-specific objects
        "court_info": DocassembleObjectMapping(
            object_type="DAObject",
            base_class="DAObject",
            attributes={
                "name": "str",
                "file_number": "str",
                "location": "str",
                "level": "str"  # superior, ontario court of justice
            },
            ontario_extensions={
                "municipality": "str",
                "judicial_region": "str",
                "courthouse_address": "Address"
            }
        ),
        
        # Lists
        "children_list": DocassembleObjectMapping(
            object_type="DAList",
            base_class="DAList.using(object_type=Individual, minimum_number=0)",
            attributes={},
            ontario_extensions={
                "child_support_table_amount": "currency",
                "special_expenses_total": "currency"
            }
        ),
        
        "assets_list": DocassembleObjectMapping(
            object_type="DAList",
            base_class="DAList.using(object_type=Asset)",
            attributes={},
            ontario_extensions={
                "total_at_separation": "currency",
                "total_at_marriage": "currency",
                "excluded_total": "currency"
            }
        )
    }
    
    @classmethod
    def get_object_mapping(cls, field_context: str) -> Optional[DocassembleObjectMapping]:
        """Get the appropriate object mapping based on field context"""
        context_lower = field_context.lower()
        
        # Check for party types
        if any(word in context_lower for word in ['applicant', 'petitioner', 'moving']):
            return cls.STANDARD_OBJECTS["party"]
        elif any(word in context_lower for word in ['respondent', 'responding']):
            return cls.STANDARD_OBJECTS["party"]
        elif 'child' in context_lower:
            return cls.STANDARD_OBJECTS["child"]
        elif 'address' in context_lower:
            return cls.STANDARD_OBJECTS["address"]
        elif 'income' in context_lower:
            return cls.STANDARD_OBJECTS["income"]
        elif 'expense' in context_lower:
            return cls.STANDARD_OBJECTS["expense"]
        elif 'asset' in context_lower or 'property' in context_lower:
            return cls.STANDARD_OBJECTS["asset"]
        elif 'debt' in context_lower or 'liability' in context_lower:
            return cls.STANDARD_OBJECTS["debt"]
        elif 'court' in context_lower:
            return cls.STANDARD_OBJECTS["court_info"]
        
        return None

class IntelligentFieldMapper:
    """Enhanced field mapping with docassemble object awareness"""
    
    def __init__(self):
        self.object_registry = DocassembleObjectRegistry()
        self.mapped_objects = {}  # Track which objects we've created
        self.field_to_object_map = {}  # Map fields to their parent objects
    
    def map_field_to_object(self, field_text: str, field_context: str = "") -> Dict[str, Any]:
        """Map a field to the appropriate docassemble object and attribute"""
        
        # Clean field text
        field_clean = re.sub(r'[^\w\s]', '', field_text).lower()
        
        # Try to identify the object this field belongs to
        object_mapping = self.object_registry.get_object_mapping(field_context or field_text)
        
        if object_mapping:
            # Determine the specific attribute within the object
            attribute = self._identify_attribute(field_clean, object_mapping)
            object_name = self._get_object_name(field_context or field_text)
            
            # Track this object
            if object_name not in self.mapped_objects:
                self.mapped_objects[object_name] = object_mapping
            
            return {
                "variable": f"{object_name}.{attribute}",
                "object_type": object_mapping.object_type,
                "base_class": object_mapping.base_class,
                "datatype": self._get_datatype_for_attribute(attribute, object_mapping),
                "object_name": object_name,
                "attribute": attribute,
                "requires_object": True
            }
        
        # Fallback to simple field mapping
        return {
            "variable": self._sanitize_variable_name(field_text),
            "datatype": self._detect_datatype(field_text),
            "requires_object": False
        }
    
    def _identify_attribute(self, field_text: str, object_mapping: DocassembleObjectMapping) -> str:
        """Identify which attribute of the object this field represents"""
        
        # Check standard attributes
        for attr in object_mapping.attributes:
            if attr in field_text:
                return attr
        
        # Check Ontario extensions
        for attr in object_mapping.ontario_extensions:
            if any(word in field_text for word in attr.split('_')):
                return attr
        
        # Common patterns
        if 'name' in field_text:
            if 'first' in field_text:
                return "name.first"
            elif 'last' in field_text:
                return "name.last"
            elif 'middle' in field_text:
                return "name.middle"
            else:
                return "name.text"
        
        if 'address' in field_text:
            if 'street' in field_text:
                return "address.address"
            elif 'city' in field_text:
                return "address.city"
            elif 'postal' in field_text or 'zip' in field_text:
                return "address.zip"
            elif 'province' in field_text or 'state' in field_text:
                return "address.state"
            else:
                return "address.address"
        
        if 'phone' in field_text:
            return "phone_number"
        
        if 'email' in field_text:
            return "email"
        
        if 'birth' in field_text or 'dob' in field_text:
            return "birthdate"
        
        # Default to creating a custom attribute
        return self._sanitize_variable_name(field_text)
    
    def _get_object_name(self, field_context: str) -> str:
        """Determine the object instance name"""
        context_lower = field_context.lower()
        
        if 'applicant' in context_lower or 'petitioner' in context_lower:
            return "applicant"
        elif 'respondent' in context_lower:
            return "respondent"
        elif 'child' in context_lower:
            # Check if it's a list or single child
            if any(word in context_lower for word in ['children', 'all', 'each']):
                return "children"
            else:
                return "child"
        elif 'lawyer' in context_lower:
            if 'applicant' in context_lower:
                return "applicant_lawyer"
            elif 'respondent' in context_lower:
                return "respondent_lawyer"
            else:
                return "lawyer"
        elif 'court' in context_lower:
            return "court_info"
        elif 'income' in context_lower:
            return "income"
        elif 'expense' in context_lower:
            return "expenses"
        elif 'asset' in context_lower:
            return "assets"
        elif 'debt' in context_lower:
            return "debts"
        
        return "info"
    
    def _get_datatype_for_attribute(self, attribute: str, object_mapping: DocassembleObjectMapping) -> str:
        """Get the appropriate datatype for an attribute"""
        
        # Check in attributes
        if attribute in object_mapping.attributes:
            attr_type = object_mapping.attributes[attribute]
            if attr_type == "str":
                return "text"
            elif attr_type == "date":
                return "date"
            elif attr_type == "currency":
                return "currency"
            elif attr_type == "bool":
                return "yesno"
            elif attr_type == "number":
                return "number"
            else:
                return "text"
        
        # Check in Ontario extensions
        if attribute in object_mapping.ontario_extensions:
            attr_type = object_mapping.ontario_extensions[attribute]
            if attr_type == "str":
                return "text"
            elif attr_type == "date":
                return "date"
            elif attr_type == "currency":
                return "currency"
            elif attr_type == "bool":
                return "yesno"
            elif attr_type == "number":
                return "number"
            else:
                return "text"
        
        # Detect from attribute name
        return self._detect_datatype(attribute)
    
    def _detect_datatype(self, text: str) -> str:
        """Detect datatype from text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['date', 'when', 'born']):
            return "date"
        elif any(word in text_lower for word in ['amount', 'value', 'income', 'expense', 'payment', 'cost', '$']):
            return "currency"
        elif any(word in text_lower for word in ['email', 'e-mail']):
            return "email"
        elif any(word in text_lower for word in ['phone', 'telephone', 'fax', 'cell']):
            return "phone"
        elif any(word in text_lower for word in ['number', 'count', 'quantity', 'age']):
            return "number"
        elif any(word in text_lower for word in ['yes', 'no', 'check', 'agree', 'consent']):
            return "yesno"
        elif any(word in text_lower for word in ['address', 'street', 'city']):
            return "address"
        
        return "text"
    
    def _sanitize_variable_name(self, text: str) -> str:
        """Create valid variable name"""
        name = re.sub(r'[^\w\s]', '', text)
        name = re.sub(r'\s+', '_', name)
        name = name.lower()[:50]
        return name if name else "field"
    
    def generate_objects_block(self) -> str:
        """Generate the objects block for the YAML file"""
        if not self.mapped_objects:
            return ""
        
        objects_yaml = "objects:\n"
        
        # Group objects by type for better organization
        individuals = []
        lists = []
        other_objects = []
        
        for obj_name, obj_mapping in self.mapped_objects.items():
            if obj_mapping.object_type == "Individual":
                individuals.append(f"  - {obj_name}: {obj_mapping.base_class}")
            elif obj_mapping.object_type == "DAList":
                lists.append(f"  - {obj_name}: {obj_mapping.base_class}")
            else:
                other_objects.append(f"  - {obj_name}: {obj_mapping.base_class}")
        
        # Add in logical order
        for obj in individuals:
            objects_yaml += obj + "\n"
        for obj in lists:
            objects_yaml += obj + "\n"
        for obj in other_objects:
            objects_yaml += obj + "\n"
        
        objects_yaml += "---\n"
        return objects_yaml
    
    def generate_initialization_code(self) -> str:
        """Generate initialization code for Ontario-specific attributes"""
        if not self.mapped_objects:
            return ""
        
        init_code = "code: |\n  # Initialize Ontario-specific attributes\n"
        
        for obj_name, obj_mapping in self.mapped_objects.items():
            if obj_mapping.ontario_extensions:
                init_code += f"  \n  # {obj_name} Ontario extensions\n"
                for attr, attr_type in obj_mapping.ontario_extensions.items():
                    if attr_type == "DAObject":
                        init_code += f"  {obj_name}.{attr} = DAObject()\n"
                    elif attr_type == "DAList":
                        init_code += f"  {obj_name}.{attr} = DAList()\n"
                    else:
                        init_code += f"  {obj_name}.{attr} = None\n"
        
        init_code += "---\n"
        return init_code

class EnhancedYAMLGenerator:
    """Generate YAML with proper object mappings"""
    
    def __init__(self, form_config, field_mapper: IntelligentFieldMapper):
        self.form_config = form_config
        self.field_mapper = field_mapper
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def generate_complete_interview(self, fields: List[Dict]) -> str:
        """Generate complete interview with proper object mappings"""
        
        # First pass: map all fields to identify objects
        mapped_fields = []
        for field in fields:
            field_mapping = self.field_mapper.map_field_to_object(
                field.get('field_label', ''),
                field.get('field_context', '')
            )
            field['mapping'] = field_mapping
            mapped_fields.append(field)
        
        # Generate YAML sections
        yaml_sections = []
        
        # Metadata
        yaml_sections.append(self._generate_metadata())
        
        # Includes
        yaml_sections.append(self._generate_includes())
        
        # Features
        yaml_sections.append(self._generate_features())
        
        # Objects block (from field mapper)
        yaml_sections.append(self.field_mapper.generate_objects_block())
        
        # Initialization code
        yaml_sections.append(self.field_mapper.generate_initialization_code())
        
        # Ontario-specific code blocks
        yaml_sections.append(self._generate_ontario_specific_code())
        
        # Question blocks
        yaml_sections.extend(self._generate_questions_with_objects(mapped_fields))
        
        # Review screen
        yaml_sections.append(self._generate_review_with_objects(mapped_fields))
        
        # Validation
        yaml_sections.append(self._generate_validation_with_objects())
        
        # Attachment
        yaml_sections.append(self._generate_attachment_with_objects(mapped_fields))
        
        return "\n".join(filter(None, yaml_sections))
    
    def _generate_metadata(self) -> str:
        """Generate metadata block"""
        return f"""---
metadata:
  title: |
    {self.form_config.form_title}
  short title: |
    Form {self.form_config.form_number}
  description: |
    Ontario Family Law Form {self.form_config.form_number}: {self.form_config.form_title}
    
    This interview uses docassemble standard objects for better data management.
    Generated: {self.timestamp}
  authors:
    - name: Ontario Family Law Forms Automation System
      organization: Enhanced Automated Processing
  revision_date: {datetime.now().strftime('%Y-%m-%d')}
  form_number: {self.form_config.form_number}
  form_category: {self.form_config.category}
  form_type: {self.form_config.form_type}
  uses_standard_objects: True
---"""
    
    def _generate_includes(self) -> str:
        """Generate includes with proper dependencies"""
        includes = [
            "docassemble.base:data/questions/basic-questions.yml",
            "ontario-family-law-common.yml"
        ]
        
        # Add based on objects used
        if 'applicant' in self.field_mapper.mapped_objects or 'respondent' in self.field_mapper.mapped_objects:
            includes.append("ontario-party-common.yml")
        
        if 'children' in self.field_mapper.mapped_objects:
            includes.append("ontario-children-common.yml")
        
        if any(obj for obj in self.field_mapper.mapped_objects if 'income' in obj or 'expense' in obj):
            includes.append("ontario-financial-common.yml")
        
        return f"""include:
{chr(10).join(f'  - {inc}' for inc in includes)}
---"""
    
    def _generate_features(self) -> str:
        """Generate features block"""
        return """features:
  navigation: True
  progress bar: True
  progress bar method: stepped
  show progress bar percentage: True
  navigation back button: True
  question back button: True
  review button: True
  hide navbar: False
  hide standard menu: False
  css:
    - ontario-forms.css
  javascript:
    - ontario-forms.js
---"""
    
    def _generate_ontario_specific_code(self) -> str:
        """Generate Ontario-specific helper functions"""
        return """code: |
  # Ontario-specific helper functions
  
  def calculate_ontario_postal_code_validation(postal_code):
    '''Validate Ontario postal code format'''
    import re
    pattern = r'^[KLMNP]\\d[A-Z]\\s?\\d[A-Z]\\d$'
    return bool(re.match(pattern, postal_code.upper()))
  
  def mask_sin(sin):
    '''Mask SIN for privacy'''
    if sin and len(sin) >= 9:
      return f"XXX-XXX-{sin[-3:]}"
    return "XXX-XXX-XXX"
  
  def ontario_court_locations():
    '''Return list of Ontario court locations'''
    return [
      "Toronto", "Ottawa", "Hamilton", "London", "Windsor",
      "Kitchener", "Barrie", "Kingston", "Thunder Bay", "Sudbury",
      "Peterborough", "St. Catharines", "Newmarket", "Brampton", 
      "Mississauga", "Oshawa", "Sault Ste. Marie", "North Bay"
    ]
  
  def calculate_net_family_property_simple(assets_total, debts_total, excluded_property=0):
    '''Simple NFP calculation'''
    return max(0, assets_total - debts_total - excluded_property)
---"""
    
    def _generate_questions_with_objects(self, mapped_fields: List[Dict]) -> List[str]:
        """Generate questions aware of object structure"""
        questions = []
        
        # Group fields by their parent object
        object_groups = {}
        standalone_fields = []
        
        for field in mapped_fields:
            if field['mapping'].get('requires_object'):
                obj_name = field['mapping']['object_name']
                if obj_name not in object_groups:
                    object_groups[obj_name] = []
                object_groups[obj_name].append(field)
            else:
                standalone_fields.append(field)
        
        # Generate questions for each object group
        for obj_name, obj_fields in object_groups.items():
            questions.append(self._generate_object_question(obj_name, obj_fields))
        
        # Generate questions for standalone fields
        if standalone_fields:
            questions.append(self._generate_standalone_questions(standalone_fields))
        
        return questions
    
    def _generate_object_question(self, obj_name: str, fields: List[Dict]) -> str:
        """Generate question for an object's fields"""
        
        # Determine appropriate title
        if obj_name == "applicant":
            title = "Applicant Information"
        elif obj_name == "respondent":
            title = "Respondent Information"
        elif obj_name == "children":
            title = "Children Information"
        elif obj_name == "court_info":
            title = "Court Information"
        else:
            title = obj_name.replace('_', ' ').title()
        
        question = f"""question: |
  {title}
subquestion: |
  Please provide the following information about the {obj_name.replace('_', ' ')}.
fields:"""
        
        # Add name fields first if it's a person
        if obj_name in ['applicant', 'respondent', 'applicant_lawyer', 'respondent_lawyer']:
            question += f"""
  - First Name: {obj_name}.name.first
    required: True
  - Middle Name: {obj_name}.name.middle
    required: False
  - Last Name: {obj_name}.name.last
    required: True"""
        
        # Add other fields
        for field in fields:
            if 'name' not in field['mapping']['attribute']:  # Skip name fields already added
                field_label = field.get('field_label', field['mapping']['attribute'])
                variable = field['mapping']['variable']
                datatype = field['mapping']['datatype']
                required = field.get('required', 'False') == 'True'
                
                question += f"\n  - {field_label}: {variable}"
                if datatype != 'text':
                    question += f"\n    datatype: {datatype}"
                if required:
                    question += "\n    required: True"
                if field.get('help_text'):
                    question += f"\n    help: |\n      {field['help_text']}"
        
        question += "\n---"
        return question
    
    def _generate_standalone_questions(self, fields: List[Dict]) -> str:
        """Generate questions for standalone fields"""
        question = """question: |
  Additional Information
fields:"""
        
        for field in fields:
            field_label = field.get('field_label', field['mapping']['variable'])
            variable = field['mapping']['variable']
            datatype = field['mapping']['datatype']
            required = field.get('required', 'False') == 'True'
            
            question += f"\n  - {field_label}: {variable}"
            if datatype != 'text':
                question += f"\n    datatype: {datatype}"
            if required:
                question += "\n    required: True"
        
        question += "\n---"
        return question
    
    def _generate_review_with_objects(self, mapped_fields: List[Dict]) -> str:
        """Generate review screen with object awareness"""
        review = """event: review_screen
question: |
  Review Your Information
subquestion: |
  Please review all information. Click any section to make changes.
review:"""
        
        # Group by objects
        object_groups = {}
        for field in mapped_fields:
            if field['mapping'].get('requires_object'):
                obj_name = field['mapping']['object_name']
                if obj_name not in object_groups:
                    object_groups[obj_name] = []
                object_groups[obj_name].append(field)
        
        # Add review sections for each object
        for obj_name, obj_fields in object_groups.items():
            review += f"\n  - note: |\n      ### {obj_name.replace('_', ' ').title()}"
            for field in obj_fields:
                review += f"\n  - {field.get('field_label', '')}: {field['mapping']['variable']}"
        
        review += "\n---"
        return review
    
    def _generate_validation_with_objects(self) -> str:
        """Generate validation aware of object structure"""
        return f"""code: |
  def validate_ontario_form():
    '''Validate form with Ontario requirements'''
    errors = []
    
    # Validate parties exist
    if not (defined('applicant.name.first') and applicant.name.first):
      errors.append("Applicant's first name is required")
    if not (defined('applicant.name.last') and applicant.name.last):
      errors.append("Applicant's last name is required")
    
    if not (defined('respondent.name.first') and respondent.name.first):
      errors.append("Respondent's first name is required")
    if not (defined('respondent.name.last') and respondent.name.last):
      errors.append("Respondent's last name is required")
    
    # Validate addresses if defined
    if defined('applicant.address.zip'):
      if not calculate_ontario_postal_code_validation(applicant.address.zip):
        errors.append("Invalid Ontario postal code for applicant")
    
    # Validate court information
    if defined('court_info.location'):
      if court_info.location not in ontario_court_locations():
        errors.append("Invalid Ontario court location")
    
    # Financial validation if applicable
    if defined('assets'):
      for asset in assets:
        if hasattr(asset, 'value') and asset.value < 0:
          errors.append(f"Asset value cannot be negative: {{asset.description}}")
    
    return errors
  
  validation_errors = validate_ontario_form()
---"""
    
    def _generate_attachment_with_objects(self, mapped_fields: List[Dict]) -> str:
        """Generate attachment with proper object field mappings"""
        return f"""mandatory: True
question: |
  Form {self.form_config.form_number} Complete
subquestion: |
  Your {self.form_config.form_title} is ready for download.
  
  % if validation_errors:
  <div class="alert alert-warning">
  <strong>Please review these items:</strong>
  <ul>
  % for error in validation_errors:
  <li>${{{{ error }}}}</li>
  % endfor
  </ul>
  </div>
  % endif
  
  **Next Steps:**
  1. Download and review your form
  2. Print and sign where required
  3. File with the appropriate court
  
attachment:
  name: Form {self.form_config.form_number}
  filename: form_{self.form_config.form_number.lower().replace('.', '_')}
  pdf template file: form_{self.form_config.form_number.lower()}.pdf
  editable: False
  fields:
    # Party information
    applicant_name: ${{{{ applicant.name.text }}}}
    applicant_address: ${{{{ applicant.address.on_one_line() }}}}
    respondent_name: ${{{{ respondent.name.text }}}}
    respondent_address: ${{{{ respondent.address.on_one_line() }}}}
    
    # Court information
    court_file_number: ${{{{ court_info.file_number if defined('court_info.file_number') else '' }}}}
    court_location: ${{{{ court_info.location if defined('court_info.location') else '' }}}}
    
    # Additional mapped fields
    % for field in {repr([f['mapping']['variable'] for f in mapped_fields if not f['mapping'].get('requires_object')])}:
    ${{{{ field }}}}: ${{{{ value(field) }}}}
    % endfor
buttons:
  - Exit: exit
  - Start Over: restart
---"""

def main():
    """Main entry point for enhanced processor"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Enhanced Ontario Family Law Forms Processor with Object Mapping"
    )
    
    parser.add_argument('--form', type=str, help='Process specific form')
    parser.add_argument('--output', type=str, default='enhanced_output', help='Output directory')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    
    args = parser.parse_args()
    
    # Example usage
    from automated_form_processor import FormRegistry, FormConfiguration
    
    if args.form:
        form_config = FormRegistry.get_form(args.form)
        if form_config:
            # Create field mapper
            field_mapper = IntelligentFieldMapper()
            
            # Create generator
            generator = EnhancedYAMLGenerator(form_config, field_mapper)
            
            # Generate sample fields for testing
            sample_fields = [
                {
                    'field_label': 'Applicant Full Legal Name',
                    'field_context': 'applicant information',
                    'required': 'True'
                },
                {
                    'field_label': 'Respondent Full Legal Name', 
                    'field_context': 'respondent information',
                    'required': 'True'
                },
                {
                    'field_label': 'Court File Number',
                    'field_context': 'court information',
                    'required': 'True'
                }
            ]
            
            # Generate YAML
            yaml_content = generator.generate_complete_interview(sample_fields)
            
            # Save to file
            output_path = Path(args.output)
            output_path.mkdir(parents=True, exist_ok=True)
            yaml_file = output_path / f"form_{form_config.form_number}_enhanced.yml"
            
            with open(yaml_file, 'w') as f:
                f.write(yaml_content)
            
            print(f"Generated enhanced YAML: {yaml_file}")
            print(f"Objects mapped: {list(field_mapper.mapped_objects.keys())}")
        else:
            print(f"Form {args.form} not found")
    else:
        print("Please specify a form number with --form")

if __name__ == "__main__":
    main()