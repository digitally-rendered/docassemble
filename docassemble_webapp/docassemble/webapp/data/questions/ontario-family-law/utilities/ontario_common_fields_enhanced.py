#!/usr/bin/env python3
"""
Ontario Common Fields Enhanced - Based on analysis of 3,373 fields across 45 forms
Provides comprehensive shared field definitions for Ontario family law forms.
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field as dataclass_field
from datetime import datetime

@dataclass
class FieldValidation:
    """Validation rule for a field"""
    validation_type: str  # required, format, range, custom
    validation_code: str
    error_message: str
    help_text: Optional[str] = None

@dataclass 
class CommonField:
    """Enhanced common field definition"""
    field_name: str
    field_type: str  # text, date, currency, yesno, checkboxes, radio, email, phone, area
    docassemble_variable: str
    label: str
    
    # Field properties
    required: bool = False
    help_text: Optional[str] = None
    validation_rules: List[FieldValidation] = dataclass_field(default_factory=list)
    
    # Display properties  
    datatype: Optional[str] = None
    choices: Optional[List[Any]] = None
    default: Optional[Any] = None
    show_if: Optional[str] = None
    
    # Ontario-specific properties
    ontario_format: Optional[str] = None
    legal_context: Optional[str] = None
    forms_used: List[str] = dataclass_field(default_factory=list)
    
    def to_docassemble_field(self) -> Dict[str, Any]:
        """Generate Docassemble field definition"""
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
        elif self.field_type == "phone":
            field_def["datatype"] = "text"
        elif self.field_type == "area":
            field_def["datatype"] = "area"
            
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
            
        if self.show_if:
            field_def["show if"] = self.show_if
            
        return field_def

class OntarioCommonFieldsEnhanced:
    """Enhanced registry of common Ontario family law form fields"""
    
    def __init__(self):
        self.court_fields = self._initialize_court_fields()
        self.party_fields = self._initialize_party_fields()
        self.address_fields = self._initialize_address_fields()
        self.lawyer_fields = self._initialize_lawyer_fields()
        self.children_fields = self._initialize_children_fields()
        self.financial_fields = self._initialize_financial_fields()
        self.claim_fields = self._initialize_claim_fields()
        self.service_fields = self._initialize_service_fields()
        self.signature_fields = self._initialize_signature_fields()
        self.ontario_validations = self._initialize_ontario_validations()
    
    def _initialize_court_fields(self) -> Dict[str, CommonField]:
        """Court information fields - used in 37+ forms"""
        return {
            "court_name": CommonField(
                field_name="court_name",
                field_type="radio",
                docassemble_variable="court.court_type",
                label="Name of court",
                required=True,
                choices=[
                    "Superior Court of Justice",
                    "Superior Court of Justice Family Branch",
                    "Ontario Court of Justice"
                ],
                forms_used=['8', '8A', '10', '13', '13A', '15', '17A', '25', '26', '28', '29', '36']
            ),
            "court_file_number": CommonField(
                field_name="court_file_number",
                field_type="text",
                docassemble_variable="court.file_number",
                label="Court File Number",
                required=False,
                help_text="If your case has already been filed",
                ontario_format="court_file",
                forms_used=['All forms']
            ),
            "court_address": CommonField(
                field_name="court_address",
                field_type="text",
                docassemble_variable="court.address.address",
                label="Court office address",
                required=True,
                forms_used=['All forms']
            ),
            "court_municipality": CommonField(
                field_name="court_municipality",
                field_type="text",
                docassemble_variable="court.municipality",
                label="Municipality",
                required=True,
                forms_used=['All forms']
            ),
            "judge_name": CommonField(
                field_name="judge_name",
                field_type="text",
                docassemble_variable="court.judge_name",
                label="Name of Judge",
                required=False,
                forms_used=['15', '17A', '17C', '25']
            )
        }
    
    def _initialize_party_fields(self) -> Dict[str, CommonField]:
        """Party information fields - used in all forms"""
        return {
            "applicant_last_name": CommonField(
                field_name="applicant_last_name",
                field_type="text",
                docassemble_variable="applicant.name.last",
                label="Applicant's last name or surname",
                required=True,
                forms_used=['All forms']
            ),
            "applicant_first_name": CommonField(
                field_name="applicant_first_name",
                field_type="text",
                docassemble_variable="applicant.name.first",
                label="Applicant's first name",
                required=True,
                forms_used=['All forms']
            ),
            "applicant_middle_name": CommonField(
                field_name="applicant_middle_name",
                field_type="text",
                docassemble_variable="applicant.name.middle",
                label="Applicant's middle name(s)",
                required=False,
                forms_used=['All forms']
            ),
            "respondent_last_name": CommonField(
                field_name="respondent_last_name",
                field_type="text",
                docassemble_variable="respondent.name.last",
                label="Respondent's last name or surname",
                required=True,
                forms_used=['All forms']
            ),
            "respondent_first_name": CommonField(
                field_name="respondent_first_name",
                field_type="text",
                docassemble_variable="respondent.name.first",
                label="Respondent's first name",
                required=True,
                forms_used=['All forms']
            ),
            "respondent_middle_name": CommonField(
                field_name="respondent_middle_name",
                field_type="text",
                docassemble_variable="respondent.name.middle",
                label="Respondent's middle name(s)",
                required=False,
                forms_used=['All forms']
            ),
            "applicant_birthdate": CommonField(
                field_name="applicant_birthdate",
                field_type="date",
                docassemble_variable="applicant.birthdate",
                label="Applicant's date of birth",
                required=False,
                forms_used=['8', '10', '13', '13A', '15', '17A', '36']
            ),
            "respondent_birthdate": CommonField(
                field_name="respondent_birthdate",
                field_type="date",
                docassemble_variable="respondent.birthdate",
                label="Respondent's date of birth",
                required=False,
                forms_used=['8', '10', '13', '13A', '15', '17A', '36']
            ),
            "applicant_email": CommonField(
                field_name="applicant_email",
                field_type="email",
                docassemble_variable="applicant.email",
                label="Applicant's email address",
                required=False,
                forms_used=['Most forms']
            ),
            "applicant_phone": CommonField(
                field_name="applicant_phone",
                field_type="phone",
                docassemble_variable="applicant.phone_number",
                label="Applicant's phone number",
                required=False,
                help_text="Format: (416) 555-1234",
                ontario_format="phone_number",
                forms_used=['Most forms']
            ),
            "applicant_fax": CommonField(
                field_name="applicant_fax",
                field_type="phone",
                docassemble_variable="applicant.fax_number",
                label="Applicant's fax number",
                required=False,
                ontario_format="phone_number",
                forms_used=['Some forms']
            ),
            "respondent_email": CommonField(
                field_name="respondent_email",
                field_type="email",
                docassemble_variable="respondent.email",
                label="Respondent's email address",
                required=False,
                forms_used=['Most forms']
            ),
            "respondent_phone": CommonField(
                field_name="respondent_phone",
                field_type="phone",
                docassemble_variable="respondent.phone_number",
                label="Respondent's phone number",
                required=False,
                help_text="Format: (416) 555-1234",
                ontario_format="phone_number",
                forms_used=['Most forms']
            )
        }
    
    def _initialize_address_fields(self) -> Dict[str, CommonField]:
        """Address fields - used in all forms with party info"""
        return {
            "applicant_street": CommonField(
                field_name="applicant_street",
                field_type="text",
                docassemble_variable="applicant.address.address",
                label="Applicant's street and number",
                required=True,
                help_text="Include unit/apartment number if applicable",
                forms_used=['All forms']
            ),
            "applicant_city": CommonField(
                field_name="applicant_city",
                field_type="text",
                docassemble_variable="applicant.address.city",
                label="Applicant's city",
                required=True,
                forms_used=['All forms']
            ),
            "applicant_province": CommonField(
                field_name="applicant_province",
                field_type="radio",
                docassemble_variable="applicant.address.province",
                label="Applicant's province",
                required=True,
                default="Ontario",
                choices=[
                    "Ontario",
                    "Alberta",
                    "British Columbia",
                    "Manitoba",
                    "New Brunswick",
                    "Newfoundland and Labrador",
                    "Northwest Territories",
                    "Nova Scotia",
                    "Nunavut",
                    "Prince Edward Island",
                    "Quebec",
                    "Saskatchewan",
                    "Yukon"
                ],
                forms_used=['All forms']
            ),
            "applicant_postal_code": CommonField(
                field_name="applicant_postal_code",
                field_type="text",
                docassemble_variable="applicant.address.postal_code",
                label="Applicant's postal code",
                required=True,
                help_text="Format: A1A 1A1",
                ontario_format="postal_code",
                forms_used=['All forms']
            ),
            "respondent_street": CommonField(
                field_name="respondent_street",
                field_type="text",
                docassemble_variable="respondent.address.address",
                label="Respondent's street and number",
                required=True,
                help_text="Include unit/apartment number if applicable",
                forms_used=['All forms']
            ),
            "respondent_city": CommonField(
                field_name="respondent_city",
                field_type="text",
                docassemble_variable="respondent.address.city",
                label="Respondent's city",
                required=True,
                forms_used=['All forms']
            ),
            "respondent_province": CommonField(
                field_name="respondent_province",
                field_type="radio",
                docassemble_variable="respondent.address.province",
                label="Respondent's province",
                required=True,
                default="Ontario",
                choices=[
                    "Ontario",
                    "Alberta",
                    "British Columbia",
                    "Manitoba",
                    "New Brunswick",
                    "Newfoundland and Labrador",
                    "Northwest Territories",
                    "Nova Scotia",
                    "Nunavut",
                    "Prince Edward Island",
                    "Quebec",
                    "Saskatchewan",
                    "Yukon"
                ],
                forms_used=['All forms']
            ),
            "respondent_postal_code": CommonField(
                field_name="respondent_postal_code",
                field_type="text",
                docassemble_variable="respondent.address.postal_code",
                label="Respondent's postal code",
                required=True,
                help_text="Format: A1A 1A1",
                ontario_format="postal_code",
                forms_used=['All forms']
            )
        }
    
    def _initialize_lawyer_fields(self) -> Dict[str, CommonField]:
        """Lawyer/representative fields - used in most procedural forms"""
        return {
            "applicant_has_lawyer": CommonField(
                field_name="applicant_has_lawyer",
                field_type="yesno",
                docassemble_variable="applicant.has_lawyer",
                label="Is the applicant represented by a lawyer?",
                required=True,
                forms_used=['Most forms']
            ),
            "applicant_lawyer_name": CommonField(
                field_name="applicant_lawyer_name",
                field_type="text",
                docassemble_variable="applicant.lawyer.name.full()",
                label="Applicant's lawyer's name",
                required=False,
                show_if="applicant.has_lawyer",
                forms_used=['Most forms']
            ),
            "applicant_lawyer_firm": CommonField(
                field_name="applicant_lawyer_firm",
                field_type="text",
                docassemble_variable="applicant.lawyer.firm_name",
                label="Applicant's lawyer's firm",
                required=False,
                show_if="applicant.has_lawyer",
                forms_used=['Most forms']
            ),
            "applicant_lawyer_address": CommonField(
                field_name="applicant_lawyer_address",
                field_type="text",
                docassemble_variable="applicant.lawyer.address.address",
                label="Applicant's lawyer's address",
                required=False,
                show_if="applicant.has_lawyer",
                forms_used=['Most forms']
            ),
            "applicant_lawyer_phone": CommonField(
                field_name="applicant_lawyer_phone",
                field_type="phone",
                docassemble_variable="applicant.lawyer.phone_number",
                label="Applicant's lawyer's phone",
                required=False,
                show_if="applicant.has_lawyer",
                ontario_format="phone_number",
                forms_used=['Most forms']
            ),
            "applicant_lawyer_email": CommonField(
                field_name="applicant_lawyer_email",
                field_type="email",
                docassemble_variable="applicant.lawyer.email",
                label="Applicant's lawyer's email",
                required=False,
                show_if="applicant.has_lawyer",
                forms_used=['Most forms']
            ),
            "respondent_has_lawyer": CommonField(
                field_name="respondent_has_lawyer",
                field_type="yesno",
                docassemble_variable="respondent.has_lawyer",
                label="Is the respondent represented by a lawyer?",
                required=False,
                forms_used=['Most forms']
            ),
            "respondent_lawyer_name": CommonField(
                field_name="respondent_lawyer_name",
                field_type="text",
                docassemble_variable="respondent.lawyer.name.full()",
                label="Respondent's lawyer's name",
                required=False,
                show_if="respondent.has_lawyer",
                forms_used=['Most forms']
            )
        }
    
    def _initialize_children_fields(self) -> Dict[str, CommonField]:
        """Children information fields - used in custody/support forms"""
        return {
            "has_children": CommonField(
                field_name="has_children",
                field_type="yesno",
                docassemble_variable="children.there_are_any",
                label="Are there any children of the relationship?",
                required=True,
                forms_used=['8', '10', '13', '13A', '15', '17A', '25', '26', '28', '36']
            ),
            "children_count": CommonField(
                field_name="children_count",
                field_type="text",
                datatype="integer",
                docassemble_variable="children.target_number",
                label="How many children?",
                required=False,
                show_if="children.there_are_any",
                forms_used=['8', '10', '13', '13A', '15', '17A', '25', '26', '28', '36']
            ),
            "child_name": CommonField(
                field_name="child_name",
                field_type="text",
                docassemble_variable="children[i].name.full()",
                label="Full name of child",
                required=True,
                forms_used=['Child-related forms']
            ),
            "child_birthdate": CommonField(
                field_name="child_birthdate",
                field_type="date",
                docassemble_variable="children[i].birthdate",
                label="Date of birth",
                required=True,
                forms_used=['Child-related forms']
            ),
            "child_residence": CommonField(
                field_name="child_residence",
                field_type="radio",
                docassemble_variable="children[i].residence",
                label="Child resides with",
                choices=[
                    "Applicant",
                    "Respondent",
                    "Shared (both parties)",
                    "Other"
                ],
                required=True,
                forms_used=['Child-related forms']
            ),
            "child_school": CommonField(
                field_name="child_school",
                field_type="text",
                docassemble_variable="children[i].school",
                label="Name of school",
                required=False,
                forms_used=['Some child-related forms']
            )
        }
    
    def _initialize_financial_fields(self) -> Dict[str, CommonField]:
        """Financial information fields - used in support/property forms"""
        return {
            "gross_annual_income": CommonField(
                field_name="gross_annual_income",
                field_type="currency",
                docassemble_variable="financial.gross_annual_income",
                label="Gross annual income",
                required=False,
                help_text="Income before taxes and deductions",
                forms_used=['13', '13A', '15', '26']
            ),
            "net_monthly_income": CommonField(
                field_name="net_monthly_income",
                field_type="currency",
                docassemble_variable="financial.net_monthly_income",
                label="Net monthly income",
                required=False,
                help_text="Income after taxes and deductions",
                forms_used=['13', '13A', '15']
            ),
            "child_support_amount": CommonField(
                field_name="child_support_amount",
                field_type="currency",
                docassemble_variable="financial.child_support_amount",
                label="Child support amount",
                required=False,
                forms_used=['13', '15', '26']
            ),
            "spousal_support_amount": CommonField(
                field_name="spousal_support_amount",
                field_type="currency",
                docassemble_variable="financial.spousal_support_amount",
                label="Spousal support amount",
                required=False,
                forms_used=['13', '15', '26']
            ),
            "property_value": CommonField(
                field_name="property_value",
                field_type="currency",
                docassemble_variable="financial.property_value",
                label="Value of property",
                required=False,
                forms_used=['13', '13A']
            )
        }
    
    def _initialize_claim_fields(self) -> Dict[str, CommonField]:
        """Claim/relief sought fields - used in Forms 8, 10, 36"""
        return {
            "claims_divorce": CommonField(
                field_name="claims_divorce",
                field_type="yesno",
                docassemble_variable="claims.divorce",
                label="Divorce",
                required=False,
                forms_used=['8', '36']
            ),
            "claims_custody": CommonField(
                field_name="claims_custody",
                field_type="yesno",
                docassemble_variable="claims.custody",
                label="Custody of children",
                required=False,
                forms_used=['8', '10', '36']
            ),
            "claims_access": CommonField(
                field_name="claims_access",
                field_type="yesno",
                docassemble_variable="claims.access",
                label="Access to children",
                required=False,
                forms_used=['8', '10', '36']
            ),
            "claims_child_support": CommonField(
                field_name="claims_child_support",
                field_type="yesno",
                docassemble_variable="claims.child_support",
                label="Child support",
                required=False,
                forms_used=['8', '10', '36']
            ),
            "claims_spousal_support": CommonField(
                field_name="claims_spousal_support",
                field_type="yesno",
                docassemble_variable="claims.spousal_support",
                label="Spousal support",
                required=False,
                forms_used=['8', '10', '36']
            ),
            "claims_property_division": CommonField(
                field_name="claims_property_division",
                field_type="yesno",
                docassemble_variable="claims.property_division",
                label="Division of property",
                required=False,
                forms_used=['8', '10', '36']
            ),
            "claims_equalization": CommonField(
                field_name="claims_equalization",
                field_type="yesno",
                docassemble_variable="claims.equalization",
                label="Equalization of net family property",
                required=False,
                forms_used=['8', '10', '13B']
            ),
            "claims_possession_home": CommonField(
                field_name="claims_possession_home",
                field_type="yesno",
                docassemble_variable="claims.possession_home",
                label="Possession of matrimonial home",
                required=False,
                forms_used=['8', '10']
            ),
            "claims_restraining_order": CommonField(
                field_name="claims_restraining_order",
                field_type="yesno",
                docassemble_variable="claims.restraining_order",
                label="Restraining order",
                required=False,
                forms_used=['8', '10']
            ),
            "claims_costs": CommonField(
                field_name="claims_costs",
                field_type="yesno",
                docassemble_variable="claims.costs",
                label="Costs",
                required=False,
                forms_used=['8', '10', '36']
            ),
            "claims_other": CommonField(
                field_name="claims_other",
                field_type="yesno",
                docassemble_variable="claims.other",
                label="Other claims",
                required=False,
                forms_used=['8', '10', '36']
            ),
            "claims_other_details": CommonField(
                field_name="claims_other_details",
                field_type="area",
                docassemble_variable="claims.other_details",
                label="Specify other claims",
                required=False,
                show_if="claims.other",
                forms_used=['8', '10', '36']
            )
        }
    
    def _initialize_service_fields(self) -> Dict[str, CommonField]:
        """Service and notice fields - used in procedural forms"""
        return {
            "service_method": CommonField(
                field_name="service_method",
                field_type="radio",
                docassemble_variable="service.method",
                label="Method of service",
                required=True,
                choices=[
                    "Regular mail",
                    "Special service",
                    "Courier",
                    "Email",
                    "Fax",
                    "Personal service"
                ],
                forms_used=['Procedural forms']
            ),
            "service_date": CommonField(
                field_name="service_date",
                field_type="date",
                docassemble_variable="service.date",
                label="Date of service",
                required=True,
                forms_used=['Procedural forms']
            ),
            "service_address": CommonField(
                field_name="service_address",
                field_type="text",
                docassemble_variable="service.address.address",
                label="Address for service",
                required=True,
                forms_used=['Procedural forms']
            ),
            "service_email": CommonField(
                field_name="service_email",
                field_type="email",
                docassemble_variable="service.email",
                label="Email address for service",
                required=False,
                show_if="service.method == 'Email'",
                forms_used=['Procedural forms']
            )
        }
    
    def _initialize_signature_fields(self) -> Dict[str, CommonField]:
        """Signature and affidavit fields - used in all forms"""
        return {
            "signature_date": CommonField(
                field_name="signature_date",
                field_type="date",
                docassemble_variable="signature_date",
                label="Date",
                required=True,
                default="today()",
                forms_used=['All forms']
            ),
            "signature_location": CommonField(
                field_name="signature_location",
                field_type="text",
                docassemble_variable="signature_location",
                label="At (municipality)",
                required=True,
                forms_used=['All forms']
            ),
            "commissioner_name": CommonField(
                field_name="commissioner_name",
                field_type="text",
                docassemble_variable="commissioner.name.full()",
                label="Commissioner for taking affidavits",
                required=False,
                forms_used=['Forms requiring affidavit']
            ),
            "sworn_affirmed": CommonField(
                field_name="sworn_affirmed",
                field_type="radio",
                docassemble_variable="oath_type",
                label="Sworn/Affirmed",
                choices=["Sworn", "Affirmed"],
                required=False,
                forms_used=['Forms requiring affidavit']
            )
        }
    
    def _initialize_ontario_validations(self) -> Dict[str, str]:
        """Ontario-specific validation functions"""
        return {
            "postal_code": """
def validate_ontario_postal_code(postal_code):
    '''Validate Canadian postal code with Ontario focus'''
    if not postal_code:
        return True
    postal_clean = re.sub(r'\\s+', '', postal_code.upper())
    # Canadian postal code format
    pattern = r'^[A-Z][0-9][A-Z][0-9][A-Z][0-9]$'
    if not re.match(pattern, postal_clean):
        return False
    # Ontario postal codes start with K, L, M, N, P
    ontario_first_letters = 'KLMNP'
    return postal_clean[0] in ontario_first_letters
""",
            "court_file": """
def validate_ontario_court_file(file_number):
    '''Validate Ontario court file number format'''
    if not file_number:
        return True
    # Ontario court file formats
    patterns = [
        r'^(FS|FC|FD|FM|FE)-[0-9]{2}-[0-9]{5,6}$',  # Family court
        r'^[0-9]{2}-[0-9]{5,6}$',  # Simplified format
        r'^[A-Z]{2}-[0-9]{2}-[0-9]{5,6}$'  # General format
    ]
    file_upper = file_number.upper().strip()
    return any(re.match(pattern, file_upper) for pattern in patterns)
""",
            "phone_number": """
def validate_canadian_phone(phone_number):
    '''Validate Canadian phone number'''
    if not phone_number:
        return True
    digits_only = re.sub(r'\\D', '', phone_number)
    # 10 digits or 11 with country code
    if len(digits_only) == 10:
        return True
    elif len(digits_only) == 11 and digits_only[0] == '1':
        return True
    return False
""",
            "sin_number": """
def validate_sin_number(sin):
    '''Validate Canadian Social Insurance Number'''
    if not sin:
        return True
    sin_clean = re.sub(r'[\\s-]', '', sin)
    if not re.match(r'^[0-9]{9}$', sin_clean):
        return False
    # Luhn algorithm for SIN validation
    digits = [int(d) for d in sin_clean]
    check_sum = 0
    for i, digit in enumerate(digits[:-1]):
        if i % 2 == 1:
            doubled = digit * 2
            check_sum += doubled if doubled < 10 else (doubled - 9)
        else:
            check_sum += digit
    return (check_sum % 10) == (10 - digits[-1]) % 10
""",
            "date_in_past": """
def validate_date_in_past(date_value):
    '''Ensure date is not in the future'''
    if not date_value:
        return True
    return date_value <= today()
""",
            "date_logical": """
def validate_date_logical(date1, date2, comparison='after'):
    '''Validate logical relationship between two dates'''
    if not date1 or not date2:
        return True
    if comparison == 'after':
        return date1 > date2
    elif comparison == 'before':
        return date1 < date2
    elif comparison == 'same_or_after':
        return date1 >= date2
    return True
"""
        }
    
    def get_all_fields(self) -> Dict[str, Dict[str, CommonField]]:
        """Get all field categories"""
        return {
            'court': self.court_fields,
            'party': self.party_fields,
            'address': self.address_fields,
            'lawyer': self.lawyer_fields,
            'children': self.children_fields,
            'financial': self.financial_fields,
            'claims': self.claim_fields,
            'service': self.service_fields,
            'signature': self.signature_fields
        }
    
    def get_fields_for_form(self, form_number: str) -> List[CommonField]:
        """Get all fields used in a specific form"""
        fields = []
        for category in self.get_all_fields().values():
            for field in category.values():
                if form_number in field.forms_used or 'All forms' in field.forms_used:
                    fields.append(field)
        return fields
    
    def generate_validation_module(self) -> str:
        """Generate Python module with all validation functions"""
        module_lines = [
            "# Ontario Family Law Validation Functions",
            "# Auto-generated from common field definitions",
            "",
            "import re",
            "from docassemble.base.util import today",
            ""
        ]
        
        for func_code in self.ontario_validations.values():
            module_lines.append(func_code)
            module_lines.append("")
        
        return "\n".join(module_lines)

# Global instance
ontario_fields_enhanced = OntarioCommonFieldsEnhanced()