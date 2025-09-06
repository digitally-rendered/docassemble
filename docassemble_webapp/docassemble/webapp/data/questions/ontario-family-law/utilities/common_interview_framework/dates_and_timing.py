"""
Date fields used across forms
Generated module for dates_and_timing fields.
"""
from docassemble.base.util import DADict, DAObject
from .base_objects import *
from .validation_functions import *

class DatesAndTimingModule(DAObject):
    """
    Date fields used across forms
    
    Dependencies: court_case_info
    """
    
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        # Initialize field attributes
        self.date_general = None

    def validate_all_fields(self):
        """Validate all fields in this module"""
        errors = []
        return len(errors) == 0, errors

    def generate_yaml_questions(self, prefix=""):
        """Generate YAML question blocks for this module"""
        questions = []

        # date_general question
        questions.append({
            "question": "I earn $ I earn $ per year which should be used to...",
            "fields": [
                {
                    "field": "{prefix}date_general",
                    "datatype": "date"
                }
            ]
        })

        return questions
