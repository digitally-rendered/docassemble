"""
Master Interview Template for Ontario Family Law Forms
Uses modular components to build complete interviews.
"""

# Import all modules
from .base_objects import *
from .validation_functions import *
from .court_case_info import CourtCaseInfoModule
from .party_information import PartyInformationModule
from .child_information import ChildInformationModule
from .financial_information import FinancialInformationModule
from .dates_and_timing import DatesAndTimingModule
from .general_fields import GeneralFieldsModule


class OntarioFamilyLawInterview(DAObject):
    """
    Master interview class that coordinates all modules.
    Provides a framework for building any Ontario family law form interview.
    """
    
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        
        # Initialize all modules
        self.court_case_info = CourtCaseInfoModule()
        self.party_information = PartyInformationModule()
        self.child_information = ChildInformationModule()
        self.financial_information = FinancialInformationModule()
        self.dates_and_timing = DatesAndTimingModule()
        self.general_fields = GeneralFieldsModule()
        
        # Core objects
        self.case = OntarioCourtCase()
        self.applicant = OntarioParty()
        self.respondent = OntarioParty()
        self.children = OntarioChildList()
        
        # Form-specific data
        self.form_data = DADict()
        self.form_type = ""
        self.form_number = ""
    
    def validate_all_modules(self):
        """Validate all modules and return consolidated errors"""
        all_errors = {}
        all_valid = True
        
        # Validate court_case_info
        valid, errors = self.court_case_info.validate_all_fields()
        if not valid:
            all_errors["court_case_info"] = errors
            all_valid = False

        # Validate party_information
        valid, errors = self.party_information.validate_all_fields()
        if not valid:
            all_errors["party_information"] = errors
            all_valid = False

        # Validate child_information
        valid, errors = self.child_information.validate_all_fields()
        if not valid:
            all_errors["child_information"] = errors
            all_valid = False

        # Validate financial_information
        valid, errors = self.financial_information.validate_all_fields()
        if not valid:
            all_errors["financial_information"] = errors
            all_valid = False

        # Validate dates_and_timing
        valid, errors = self.dates_and_timing.validate_all_fields()
        if not valid:
            all_errors["dates_and_timing"] = errors
            all_valid = False

        # Validate general_fields
        valid, errors = self.general_fields.validate_all_fields()
        if not valid:
            all_errors["general_fields"] = errors
            all_valid = False

        return all_valid, all_errors
    
    def generate_complete_yaml(self, form_type="general"):
        """Generate complete YAML interview for specified form type"""
        
        yaml_content = []
        
        # Metadata
        yaml_content.append({
            "metadata": {
                "title": f"Ontario Family Law - {form_type.title()}",
                "short title": f"Form {self.form_number}",
                "generated": "2025-09-05T12:53:46.531625",
                "framework": "Common Interview Framework"
            }
        })
        
        # Include statements
        yaml_content.append({
            "include": [
                "ontario-family-law-base.yml",
                "ontario-validation.yml"
            ]
        })
        
        # Objects
        objects = []
        objects.append({"case": "OntarioCourtCase"})
        objects.append({"applicant": "OntarioParty"})
        objects.append({"respondent": "OntarioParty"})
        objects.append({"children": "OntarioChildList"})
        
        yaml_content.append({"objects": objects})
        
        # Generate questions from all relevant modules
        # Add court_case_info questions
        court_case_info_questions = self.court_case_info.generate_yaml_questions()
        yaml_content.extend(court_case_info_questions)

        # Add party_information questions
        party_information_questions = self.party_information.generate_yaml_questions()
        yaml_content.extend(party_information_questions)

        # Add child_information questions
        child_information_questions = self.child_information.generate_yaml_questions()
        yaml_content.extend(child_information_questions)

        # Add financial_information questions
        financial_information_questions = self.financial_information.generate_yaml_questions()
        yaml_content.extend(financial_information_questions)

        # Add dates_and_timing questions
        dates_and_timing_questions = self.dates_and_timing.generate_yaml_questions()
        yaml_content.extend(dates_and_timing_questions)

        # Add general_fields questions
        general_fields_questions = self.general_fields.generate_yaml_questions()
        yaml_content.extend(general_fields_questions)

        
        return yaml_content
    
    def get_module_dependencies(self):
        """Return dependency graph of modules"""
        dependencies = {}
        dependencies["court_case_info"] = []
        dependencies["party_information"] = ['court_case_info']
        dependencies["child_information"] = ['court_case_info', 'party_information']
        dependencies["financial_information"] = ['court_case_info', 'party_information']
        dependencies["dates_and_timing"] = ['court_case_info']
        dependencies["general_fields"] = ['court_case_info']
        
        return dependencies
    
    def get_form_completion_percentage(self):
        """Calculate completion percentage across all modules"""
        total_fields = 0
        completed_fields = 0
        
        # Count court_case_info fields
        module_fields = len([f for f in dir(self.court_case_info) if not f.startswith("_")])
        total_fields += module_fields
        # Count completed fields (non-empty values)
        for field_name in dir(self.court_case_info):
            if not field_name.startswith("_"):
                field_value = getattr(self.court_case_info, field_name)
                if field_value and field_value != "":
                    completed_fields += 1

        # Count party_information fields
        module_fields = len([f for f in dir(self.party_information) if not f.startswith("_")])
        total_fields += module_fields
        # Count completed fields (non-empty values)
        for field_name in dir(self.party_information):
            if not field_name.startswith("_"):
                field_value = getattr(self.party_information, field_name)
                if field_value and field_value != "":
                    completed_fields += 1

        # Count child_information fields
        module_fields = len([f for f in dir(self.child_information) if not f.startswith("_")])
        total_fields += module_fields
        # Count completed fields (non-empty values)
        for field_name in dir(self.child_information):
            if not field_name.startswith("_"):
                field_value = getattr(self.child_information, field_name)
                if field_value and field_value != "":
                    completed_fields += 1

        # Count financial_information fields
        module_fields = len([f for f in dir(self.financial_information) if not f.startswith("_")])
        total_fields += module_fields
        # Count completed fields (non-empty values)
        for field_name in dir(self.financial_information):
            if not field_name.startswith("_"):
                field_value = getattr(self.financial_information, field_name)
                if field_value and field_value != "":
                    completed_fields += 1

        # Count dates_and_timing fields
        module_fields = len([f for f in dir(self.dates_and_timing) if not f.startswith("_")])
        total_fields += module_fields
        # Count completed fields (non-empty values)
        for field_name in dir(self.dates_and_timing):
            if not field_name.startswith("_"):
                field_value = getattr(self.dates_and_timing, field_name)
                if field_value and field_value != "":
                    completed_fields += 1

        # Count general_fields fields
        module_fields = len([f for f in dir(self.general_fields) if not f.startswith("_")])
        total_fields += module_fields
        # Count completed fields (non-empty values)
        for field_name in dir(self.general_fields):
            if not field_name.startswith("_"):
                field_value = getattr(self.general_fields, field_name)
                if field_value and field_value != "":
                    completed_fields += 1

        
        if total_fields == 0:
            return 0
        return int((completed_fields / total_fields) * 100)
