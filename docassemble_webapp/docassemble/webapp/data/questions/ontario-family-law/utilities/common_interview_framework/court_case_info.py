"""
Court and case identification fields
Generated module for court_case_info fields.
"""
from docassemble.base.util import DADict, DAObject
from .base_objects import *
from .validation_functions import *

class CourtCaseInfoModule(DAObject):
    """
    Court and case identification fields
    
    Dependencies: None
    """
    
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        # Initialize field attributes
        self.court_file_number = ""

    def validate_all_fields(self):
        """Validate all fields in this module"""
        errors = []
        # Validate court_file_number
        if not validate_court_file_number(self.court_file_number):
            errors.append("court_file_number")
        return len(errors) == 0, errors

    def generate_yaml_questions(self, prefix=""):
        """Generate YAML question blocks for this module"""
        questions = []

        # court_file_number question
        questions.append({
            "question": "Court File Number",
            "fields": [
                {
                    "field": "{prefix}court_file_number",
                    "datatype": "text"
                    "validate": "^[A-Z]{2}-\d{2}-\d{8}$"
                }
            ]
        })

        return questions
