"""
Information about children involved in the case
Generated module for child_information fields.
"""
from docassemble.base.util import DADict, DAObject
from .base_objects import *
from .validation_functions import *

class ChildInformationModule(DAObject):
    """
    Information about children involved in the case
    
    Dependencies: court_case_info, party_information
    """
    
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        # Initialize field attributes
        self.child_name = ""

    def validate_all_fields(self):
        """Validate all fields in this module"""
        errors = []
        return len(errors) == 0, errors

    def generate_yaml_questions(self, prefix=""):
        """Generate YAML question blocks for this module"""
        questions = []

        # child_name question
        questions.append({
            "question": ". . . Medical insurance premiums and certain healt...",
            "fields": [
                {
                    "field": "{prefix}child_name",
                    "datatype": "text"
                }
            ]
        })

        return questions
