#!/usr/bin/env python3
"""
Ontario Common Fields - Field definitions and validation for Ontario family law forms
Programmatically generates YAML code objects for common field patterns
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import yaml

@dataclass
class FieldValidation:
    """Validation rule for a field"""
    validation_type: str  # required, format, range, custom
    validation_code: str
    error_message: str
    help_text: Optional[str] = None

@dataclass 
class CommonField:
    """Common field definition that generates YAML objects"""
    field_name: str
    field_type: str  # text, date, currency, yesno, checkboxes, radio, email
    docassemble_variable: str
    label: str
    
    # Field properties
    required: bool = False
    help_text: Optional[str] = None
    validation_rules: List[FieldValidation] = field(default_factory=list)
    
    # Display properties  
    datatype: Optional[str] = None
    choices: Optional[List[Dict[str, str]]] = None
    default: Optional[Any] = None
    
    # Ontario-specific properties
    ontario_format: Optional[str] = None  # postal_code, court_file, etc.
    legal_context: Optional[str] = None
    
    def to_docassemble_field(self) -> Dict[str, Any]:
        """Generate Docassemble field definition as YAML object"""
        field_def = {self.label: self.docassemble_variable}
        
        if self.datatype:
            field_def["datatype"] = self.datatype
        elif self.field_type == "date":
            field_def["datatype"] = "date"
        elif self.field_type == "currency":
            field_def["datatype"] = "currency"
        elif self.field_type == "yesno":
            field_def["datatype"] = "yesnoradio"
        elif self.field_type == "email":
            field_def["datatype"] = "email"
            
        if self.choices:
            field_def["choices"] = self.choices
            if self.field_type == "checkboxes":
                field_def["datatype"] = "checkboxes"
            elif self.field_type == "radio":
                field_def["datatype"] = "radio"
                
        if self.default is not None:
            field_def["default"] = self.default
            
        if self.required:
            field_def["required"] = True
            
        if self.help_text:
            field_def["help"] = self.help_text
            
        return field_def
    
    def to_question_block(self, question_id: str = None) -> Dict[str, Any]:
        """Generate complete Docassemble question block"""
        question_id = question_id or f"question_{self.field_name}"
        
        block = {
            "question": self.label,
            "fields": [self.to_docassemble_field()]
        }
        
        # Add validation code if present
        validation_code = self.generate_validation_code()
        if validation_code:
            block["validation code"] = validation_code
            
        if self.help_text:
            block["help"] = self.help_text
            
        return block
    
    def generate_validation_code(self) -> Optional[str]:
        """Generate validation code from validation rules"""
        if not self.validation_rules:
            return None
            
        validation_lines = []
        for rule in self.validation_rules:
            validation_lines.append(rule.validation_code)
            
        return "\n".join(validation_lines) if validation_lines else None

class OntarioCommonFields:
    """Registry of common Ontario family law form fields"""
    
    def __init__(self):
        self.common_fields = self._initialize_common_fields()
        self.ontario_validations = self._initialize_ontario_validations()
    
    def _initialize_common_fields(self) -> Dict[str, CommonField]:
        """Initialize registry of common Ontario form fields"""
        fields = {}
        
        # Party name fields
        fields["applicant_full_name"] = CommonField(
            field_name="applicant_full_name",
            field_type="text",
            docassemble_variable="applicant.name.full()",
            label="Full legal name of applicant",
            required=True,
            help_text="Enter the applicant's complete legal name as it appears on official documents",
            validation_rules=[
                FieldValidation(
                    validation_type="required",
                    validation_code="if not applicant.name.full():\n  validation_error('Full legal name is required')",
                    error_message="Full legal name is required"
                ),
                FieldValidation(
                    validation_type="format",
                    validation_code="if len(applicant.name.full().strip()) < 2:\n  validation_error('Please enter a valid full name')",
                    error_message="Please enter a valid full name"
                )
            ]
        )
        
        fields["respondent_full_name"] = CommonField(
            field_name="respondent_full_name", 
            field_type="text",
            docassemble_variable="respondent.name.full()",
            label="Full legal name of respondent",
            required=True,
            help_text="Enter the respondent's complete legal name as it appears on official documents",
            validation_rules=[
                FieldValidation(
                    validation_type="required",
                    validation_code="if not respondent.name.full():\n  validation_error('Respondent full legal name is required')",
                    error_message="Respondent full legal name is required"
                )
            ]
        )
        
        # Address fields
        fields["applicant_address"] = CommonField(
            field_name="applicant_address",
            field_type="text",
            docassemble_variable="applicant.address.block()",
            label="Address of applicant",
            required=True,
            help_text="Enter the applicant's current mailing address"
        )
        
        fields["respondent_address"] = CommonField(
            field_name="respondent_address",
            field_type="text", 
            docassemble_variable="respondent.address.block()",
            label="Address of respondent",
            required=True,
            help_text="Enter the respondent's current mailing address"
        )
        
        # Contact fields
        fields["applicant_phone"] = CommonField(
            field_name="applicant_phone",
            field_type="text",
            docassemble_variable="applicant.phone_number",
            label="Phone number of applicant",
            ontario_format="phone_number",
            validation_rules=[
                FieldValidation(
                    validation_type="format",
                    validation_code="if not validate_canadian_phone(applicant.phone_number):\n  validation_error('Please enter a valid Canadian phone number')",
                    error_message="Please enter a valid Canadian phone number"
                )
            ]
        )
        
        fields["applicant_email"] = CommonField(
            field_name="applicant_email",
            field_type="email",
            docassemble_variable="applicant.email",
            label="Email address of applicant"
        )
        
        # Birth date and age
        fields["applicant_birthdate"] = CommonField(
            field_name="applicant_birthdate",
            field_type="date",
            docassemble_variable="applicant.birthdate",
            label="Date of birth of applicant",
            required=True,
            validation_rules=[
                FieldValidation(
                    validation_type="range",
                    validation_code="if applicant.birthdate > today():\n  validation_error('Birth date cannot be in the future')",
                    error_message="Birth date cannot be in the future"
                ),
                FieldValidation(
                    validation_type="range", 
                    validation_code="if (today() - applicant.birthdate).days < 18*365:\n  validation_error('Applicant must be at least 18 years old')",
                    error_message="Applicant must be at least 18 years old"
                )
            ]
        )
        
        # Court information
        fields["court_file_number"] = CommonField(
            field_name="court_file_number",
            field_type="text",
            docassemble_variable="case.court_file_number",
            label="Court file number",
            help_text="Enter the court file number if this case has already been filed",
            ontario_format="court_file",
            validation_rules=[
                FieldValidation(
                    validation_type="format",
                    validation_code="if case.court_file_number and not validate_ontario_court_file(case.court_file_number):\n  validation_error('Please enter a valid Ontario court file number')",
                    error_message="Please enter a valid Ontario court file number"
                )
            ]
        )
        
        fields["court_location"] = CommonField(
            field_name="court_location",
            field_type="radio",
            docassemble_variable="case.court_location",
            label="Court location",
            required=True,
            choices=[
                {"toronto": "Toronto (393 University Avenue)"},
                {"ottawa": "Ottawa (161 Elgin Street)"},
                {"london": "London (80 Dundas Street)"},
                {"hamilton": "Hamilton (45 Main Street East)"},
                {"windsor": "Windsor (245 Windsor Avenue)"},
                {"thunder_bay": "Thunder Bay (125 Brodie Street North)"},
                {"other": "Other Ontario location"}
            ]
        )
        
        # Marriage information
        fields["marriage_date"] = CommonField(
            field_name="marriage_date",
            field_type="date",
            docassemble_variable="marriage.marriage_date", 
            label="Date of marriage",
            validation_rules=[
                FieldValidation(
                    validation_type="range",
                    validation_code="if marriage.marriage_date > today():\n  validation_error('Marriage date cannot be in the future')",
                    error_message="Marriage date cannot be in the future"
                )
            ]
        )
        
        fields["marriage_location"] = CommonField(
            field_name="marriage_location",
            field_type="text",
            docassemble_variable="marriage.marriage_location",
            label="Place of marriage (city, province/state, country)"
        )
        
        fields["separation_date"] = CommonField(
            field_name="separation_date", 
            field_type="date",
            docassemble_variable="marriage.separation_date",
            label="Date of separation",
            validation_rules=[
                FieldValidation(
                    validation_type="range",
                    validation_code="if marriage.separation_date and marriage.separation_date > today():\n  validation_error('Separation date cannot be in the future')",
                    error_message="Separation date cannot be in the future"
                ),
                FieldValidation(
                    validation_type="logical",
                    validation_code="if marriage.separation_date and marriage.marriage_date and marriage.separation_date < marriage.marriage_date:\n  validation_error('Separation date cannot be before marriage date')",
                    error_message="Separation date cannot be before marriage date"
                )
            ]
        )
        
        # Children information
        fields["has_children"] = CommonField(
            field_name="has_children",
            field_type="yesno",
            docassemble_variable="children.there_are_any",
            label="Are there any children of the relationship?"
        )
        
        fields["children_count"] = CommonField(
            field_name="children_count",
            field_type="text",
            datatype="integer",
            docassemble_variable="children.target_number",
            label="How many children are there?",
            validation_rules=[
                FieldValidation(
                    validation_type="range",
                    validation_code="if children.target_number < 1 or children.target_number > 20:\n  validation_error('Please enter a reasonable number of children (1-20)')",
                    error_message="Please enter a reasonable number of children (1-20)"
                )
            ]
        )
        
        # Financial fields
        fields["gross_annual_income"] = CommonField(
            field_name="gross_annual_income",
            field_type="currency",
            docassemble_variable="applicant.income.gross_annual",
            label="Gross annual income (before taxes and deductions)",
            help_text="Enter your total income before taxes and deductions from all sources"
        )
        
        # Lawyer information
        fields["has_lawyer"] = CommonField(
            field_name="has_lawyer",
            field_type="yesno", 
            docassemble_variable="applicant.has_lawyer",
            label="Do you have a lawyer?"
        )
        
        fields["lawyer_name"] = CommonField(
            field_name="lawyer_name",
            field_type="text",
            docassemble_variable="applicant.lawyer.name.full()",
            label="Lawyer's full name"
        )
        
        fields["lawyer_firm"] = CommonField(
            field_name="lawyer_firm",
            field_type="text", 
            docassemble_variable="applicant.lawyer.firm_name",
            label="Law firm name"
        )
        
        return fields
    
    def _initialize_ontario_validations(self) -> Dict[str, str]:
        """Initialize Ontario-specific validation functions"""
        return {
            "postal_code": """
def validate_ontario_postal_code(postal_code):
    if not postal_code:
        return True  # Optional field
    # Remove spaces and convert to uppercase
    postal_clean = re.sub(r'\\s+', '', postal_code.upper())
    # Ontario postal codes start with K, L, M, N, P
    ontario_pattern = r'^[KLMNP][0-9][A-Z][0-9][A-Z][0-9]$'
    return bool(re.match(ontario_pattern, postal_clean))
""",
            "court_file": """
def validate_ontario_court_file(file_number):
    if not file_number:
        return True  # Optional field
    # Ontario court file format: FS-XX-XXXXX or FC-XX-XXXXX etc.
    court_file_pattern = r'^(FS|FC|FD|FM|FE)-[0-9]{2}-[0-9]{5}$'
    return bool(re.match(court_file_pattern, file_number.upper()))
""",
            "phone_number": """
def validate_canadian_phone(phone_number):
    if not phone_number:
        return True  # Optional field
    # Remove all non-digits
    digits_only = re.sub(r'\\D', '', phone_number)
    # Must be 10 digits (area code + number) or 11 digits (1 + area code + number)
    if len(digits_only) == 10:
        return True
    elif len(digits_only) == 11 and digits_only[0] == '1':
        return True
    return False
""",
            "sin_number": """
def validate_sin_number(sin):
    if not sin:
        return True  # Optional field
    # Remove spaces and hyphens
    sin_clean = re.sub(r'[\\s-]', '', sin)
    # Must be exactly 9 digits
    if not re.match(r'^[0-9]{9}$', sin_clean):
        return False
    # Luhn algorithm check for SIN
    digits = [int(d) for d in sin_clean]
    check_sum = 0
    for i, digit in enumerate(digits[:-1]):
        if i % 2 == 1:  # Even positions (0-indexed)
            doubled = digit * 2
            check_sum += doubled if doubled < 10 else (doubled - 9)
        else:
            check_sum += digit
    return (check_sum % 10) == (10 - digits[-1]) % 10
"""
        }
    
    def get_field(self, field_name: str) -> Optional[CommonField]:
        """Get a common field by name"""
        return self.common_fields.get(field_name)
    
    def get_fields_by_category(self, category: str) -> List[CommonField]:
        """Get fields by category (party, court, children, etc.)"""
        category_mapping = {
            "party": ["applicant_full_name", "respondent_full_name", 
                     "applicant_address", "respondent_address",
                     "applicant_phone", "applicant_email", "applicant_birthdate"],
            "court": ["court_file_number", "court_location"],
            "marriage": ["marriage_date", "marriage_location", "separation_date"],
            "children": ["has_children", "children_count"],
            "financial": ["gross_annual_income"],
            "lawyer": ["has_lawyer", "lawyer_name", "lawyer_firm"]
        }
        
        field_names = category_mapping.get(category, [])
        return [self.common_fields[name] for name in field_names if name in self.common_fields]
    
    def generate_validation_functions(self) -> str:
        """Generate all Ontario validation functions as Python code"""
        functions = []
        for func_name, func_code in self.ontario_validations.items():
            functions.append(func_code)
        return "\n\n".join(functions)
    
    def generate_fields_yaml_objects(self, field_names: List[str]) -> List[Dict[str, Any]]:
        """Generate YAML field objects for specified field names"""
        yaml_objects = []
        for field_name in field_names:
            if field_name in self.common_fields:
                field = self.common_fields[field_name]
                yaml_objects.append(field.to_docassemble_field())
        return yaml_objects
    
    def generate_question_blocks(self, field_names: List[str]) -> List[Dict[str, Any]]:
        """Generate complete question blocks for specified fields"""
        blocks = []
        for field_name in field_names:
            if field_name in self.common_fields:
                field = self.common_fields[field_name]
                blocks.append(field.to_question_block())
        return blocks
    
    def search_fields_by_pattern(self, pattern: str) -> List[str]:
        """Search for fields matching a pattern"""
        matching_fields = []
        pattern_lower = pattern.lower()
        
        for field_name, field in self.common_fields.items():
            if (pattern_lower in field_name.lower() or 
                pattern_lower in field.label.lower() or
                pattern_lower in field.docassemble_variable.lower()):
                matching_fields.append(field_name)
                
        return matching_fields

# Global instance for easy import
ontario_common_fields = OntarioCommonFields()