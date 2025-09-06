"""
Income, support, and financial details
Generated module for financial_information fields.
"""
from docassemble.base.util import DADict, DAObject
from .base_objects import *
from .validation_functions import *

class FinancialInformationModule(DAObject):
    """
    Income, support, and financial details
    
    Dependencies: court_case_info, party_information
    """
    
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        # Initialize field attributes
        self.income_amount = Value()
        self.support_amount = Value()

    def validate_all_fields(self):
        """Validate all fields in this module"""
        errors = []
        return len(errors) == 0, errors

    def generate_yaml_questions(self, prefix=""):
        """Generate YAML question blocks for this module"""
        questions = []

        # income_amount question
        questions.append({
            "question": "7. 7. 7. 7. 7. Any other income (specify source) A...",
            "fields": [
                {
                    "field": "{prefix}income_amount",
                    "datatype": "currency"
                }
            ]
        })

        # support_amount question
        questions.append({
            "question": "9. 9. Spousal support received from a former spous...",
            "fields": [
                {
                    "field": "{prefix}support_amount",
                    "datatype": "currency"
                }
            ]
        })

        return questions
