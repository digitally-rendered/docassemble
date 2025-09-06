"""
Applicant and respondent personal information
Generated module for party_information fields.
"""
from docassemble.base.util import DADict, DAObject
from .base_objects import *
from .validation_functions import *

class PartyInformationModule(DAObject):
    """
    Applicant and respondent personal information
    
    Dependencies: court_case_info
    """
    
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        # Initialize field attributes
        self.applicant_name = ""
        self.address = ""
        self.phone_number = ""

    def validate_all_fields(self):
        """Validate all fields in this module"""
        errors = []
        # Validate phone_number
        if not validate_phone_number(self.phone_number):
            errors.append("phone_number")
        return len(errors) == 0, errors

    def generate_yaml_questions(self, prefix=""):
        """Generate YAML question blocks for this module"""
        questions = []

        # applicant_name question
        questions.append({
            "question": "1.  My name is (full legal name)",
            "fields": [
                {
                    "field": "{prefix}applicant_name",
                    "datatype": "text"
                }
            ]
        })

        # address question
        questions.append({
            "question": "Court office address",
            "fields": [
                {
                    "field": "{prefix}address",
                    "datatype": "text"
                }
            ]
        })

        # phone_number question
        questions.append({
            "question": "Telephone Telephone Telephone Telephone Telephone ...",
            "fields": [
                {
                    "field": "{prefix}phone_number",
                    "datatype": "text"
                    "validate": "^(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})$"
                }
            ]
        })

        return questions
