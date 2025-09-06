#!/usr/bin/env python3
"""
Common Interview Framework Generator Agent

Generates shared Docassemble interview modules based on common field analysis.
Creates reusable Python code that generates YAML interview components.

This agent:
1. Reads enhanced common fields analysis
2. Creates shared field modules as Python classes
3. Generates reusable interview components
4. Creates validation and helper functions
5. Builds a modular interview framework

Author: Form Factory Orchestrator  
Created: 2025-09-05
"""

import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class InterviewModule:
    """Represents a reusable interview module"""
    name: str
    description: str
    fields: List[Dict]
    dependencies: List[str]
    objects: List[str]
    validation_rules: Dict[str, str]

class CommonInterviewFrameworkGenerator:
    """Generates shared interview framework for Ontario family law forms"""
    
    def __init__(self, analysis_file: str):
        self.analysis_file = analysis_file
        self.analysis_data = None
        self.modules = {}
        self.framework_code = {}
        
    def load_analysis(self):
        """Load the enhanced common fields analysis"""
        with open(self.analysis_file, 'r', encoding='utf-8') as f:
            self.analysis_data = json.load(f)
        
        print(f"✅ Loaded analysis of {self.analysis_data['metadata']['total_forms_analyzed']} forms")
        return self.analysis_data
    
    def generate_base_objects(self) -> str:
        """Generate base Docassemble objects for Ontario family law"""
        code = '''"""
Base Objects for Ontario Family Law Forms
Provides common object definitions used across all forms.
"""
from docassemble.base.core import DAObject, DAList
from docassemble.base.util import Individual, Address, Person, Value
from docassemble.base.functions import currency

class OntarioCourtCase(DAObject):
    """Represents an Ontario court case"""
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.court_file_number = ""
        self.court_name = ""
        self.court_address = Address()
        self.case_type = ""
        self.filing_date = None
    
    def court_file_formatted(self):
        """Return formatted court file number"""
        if self.court_file_number:
            # Format: XX-YY-NNNNNNNN
            return self.court_file_number.upper().replace(' ', '').replace('-', '')[:2] + '-' + \\
                   self.court_file_number.upper().replace(' ', '').replace('-', '')[2:4] + '-' + \\
                   self.court_file_number.upper().replace(' ', '').replace('-', '')[4:]
        return ""

class OntarioParty(Person):
    """Represents a party (applicant/respondent) in Ontario family law case"""
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.party_type = ""  # applicant, respondent, etc.
        self.represented_by_lawyer = None
        self.lawyer = Individual()
        self.phone_number = ""
        self.email = ""
        self.date_of_birth = None
        self.occupation = ""
        self.employer = ""
    
    def age(self):
        """Calculate age from date of birth"""
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

class OntarioChild(Individual):
    """Represents a child in Ontario family law case"""
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.date_of_birth = None
        self.lives_with = ""  # applicant, respondent, other
        self.school = ""
        self.special_needs = ""
        self.custody_arrangement = ""
        self.access_arrangement = ""
    
    def age(self):
        """Calculate age from date of birth"""
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
    
    def is_minor(self):
        """Check if child is under 18"""
        age = self.age()
        return age is not None and age < 18

class OntarioChildList(DAList):
    """List of children in Ontario family law case"""
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.object_type = OntarioChild
    
    def minor_children(self):
        """Return list of children under 18"""
        return [child for child in self if child.is_minor()]
    
    def adult_children(self):
        """Return list of children 18 or older"""
        return [child for child in self if not child.is_minor()]

class FinancialInformation(DAObject):
    """Represents financial information for a party"""
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.annual_income = Value()
        self.monthly_income = Value()
        self.employment_income = Value()
        self.other_income = Value()
        self.expenses = Value()
        self.assets = Value()
        self.debts = Value()
    
    def net_worth(self):
        """Calculate net worth (assets - debts)"""
        return currency(self.assets.amount - self.debts.amount)
    
    def monthly_disposable_income(self):
        """Calculate monthly disposable income"""
        return currency(self.monthly_income.amount - self.expenses.amount)

class SupportAmount(DAObject):
    """Represents support payment information"""
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.amount = Value()
        self.frequency = ""  # monthly, weekly, etc.
        self.start_date = None
        self.end_date = None
        self.support_type = ""  # child, spousal, etc.
    
    def monthly_amount(self):
        """Convert to monthly amount regardless of frequency"""
        if self.frequency == "weekly":
            return currency(self.amount.amount * 52 / 12)
        elif self.frequency == "bi-weekly":
            return currency(self.amount.amount * 26 / 12)
        elif self.frequency == "monthly":
            return currency(self.amount.amount)
        elif self.frequency == "annual":
            return currency(self.amount.amount / 12)
        return self.amount
'''
        return code
    
    def generate_validation_functions(self) -> str:
        """Generate validation functions for common fields"""
        code = '''"""
Validation Functions for Ontario Family Law Forms
Provides validation for common field types across all forms.
"""
import re
from docassemble.base.util import validation_error

def validate_ontario_postal_code(postal_code):
    """Validate Canadian postal code format"""
    if not postal_code:
        return True  # Optional field
    
    pattern = r'^[A-Za-z]\d[A-Za-z] \d[A-Za-z]\d$'
    if not re.match(pattern, postal_code.strip()):
        validation_error("Please enter a valid Canadian postal code (format: A1A 1A1)")
    return True

def validate_phone_number(phone):
    """Validate phone number format"""
    if not phone:
        return True  # Optional field
    
    # Remove all non-digits
    digits_only = re.sub(r'[^0-9]', '', phone)
    
    if len(digits_only) == 10:
        return True
    elif len(digits_only) == 11 and digits_only[0] == '1':
        return True
    else:
        validation_error("Please enter a valid 10-digit phone number")
    return True

def validate_court_file_number(file_number):
    """Validate Ontario court file number format"""
    if not file_number:
        return True  # Optional field
    
    # Remove spaces and convert to uppercase
    clean_number = file_number.replace(' ', '').replace('-', '').upper()
    
    # Should be format: XXYY followed by 8 digits
    pattern = r'^[A-Z]{2}\d{10}$'
    if not re.match(pattern, clean_number):
        validation_error("Please enter a valid court file number (format: XX-YY-12345678)")
    return True

def validate_email_address(email):
    """Validate email address format"""
    if not email:
        return True  # Optional field
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email.strip()):
        validation_error("Please enter a valid email address")
    return True

def validate_currency_amount(amount):
    """Validate currency amount"""
    if not amount:
        return True  # Optional field
    
    try:
        float_amount = float(str(amount).replace('$', '').replace(',', ''))
        if float_amount < 0:
            validation_error("Amount cannot be negative")
        return True
    except ValueError:
        validation_error("Please enter a valid dollar amount")
    return True

def format_phone_number(phone):
    """Format phone number consistently"""
    if not phone:
        return ""
    
    digits_only = re.sub(r'[^0-9]', '', phone)
    
    if len(digits_only) == 10:
        return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
    elif len(digits_only) == 11 and digits_only[0] == '1':
        return f"1 ({digits_only[1:4]}) {digits_only[4:7]}-{digits_only[7:]}"
    
    return phone  # Return as-is if can't format

def format_postal_code(postal_code):
    """Format postal code consistently"""
    if not postal_code:
        return ""
    
    clean_code = postal_code.replace(' ', '').upper()
    if len(clean_code) == 6:
        return f"{clean_code[:3]} {clean_code[3:]}"
    
    return postal_code  # Return as-is if can't format

def format_court_file_number(file_number):
    """Format court file number consistently"""
    if not file_number:
        return ""
    
    clean_number = file_number.replace(' ', '').replace('-', '').upper()
    if len(clean_number) >= 10:
        return f"{clean_number[:2]}-{clean_number[2:4]}-{clean_number[4:]}"
    
    return file_number  # Return as-is if can't format
'''
        return code
    
    def generate_field_modules(self) -> Dict[str, str]:
        """Generate Python modules for each field group"""
        if not self.analysis_data:
            self.load_analysis()
        
        modules = {}
        
        for group_name, group_data in self.analysis_data['field_groups'].items():
            module_code = self._generate_single_module(group_name, group_data)
            modules[group_name] = module_code
        
        return modules
    
    def _generate_single_module(self, group_name: str, group_data: Dict) -> str:
        """Generate Python code for a single field group module"""
        class_name = ''.join(word.capitalize() for word in group_name.split('_')) + 'Module'
        
        code = f'''"""
{group_data['description']}
Generated module for {group_name} fields.
"""
from docassemble.base.util import DADict, DAObject
from .base_objects import *
from .validation_functions import *

class {class_name}(DAObject):
    """
    {group_data['description']}
    
    Dependencies: {', '.join(group_data['dependencies']) if group_data['dependencies'] else 'None'}
    """
    
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        # Initialize field attributes
'''
        
        # Add field attributes based on common fields in this group
        common_fields = self.analysis_data['common_fields']
        group_fields = [field_name for field_name in group_data['fields'] 
                       if field_name in common_fields]
        
        for field_name in group_fields:
            field_info = common_fields[field_name]
            field_type = field_info['docassemble_type']
            
            if field_type == 'currency':
                code += f'        self.{field_name} = Value()\n'
            elif field_type == 'date':
                code += f'        self.{field_name} = None\n'
            else:
                code += f'        self.{field_name} = ""\n'
        
        # Add validation methods
        code += '\n    def validate_all_fields(self):\n'
        code += '        """Validate all fields in this module"""\n'
        code += '        errors = []\n'
        
        for field_name in group_fields:
            field_info = common_fields[field_name]
            validation_pattern = field_info.get('validation_pattern', '')
            
            if validation_pattern:
                code += f'        # Validate {field_name}\n'
                if 'postal' in field_name.lower():
                    code += f'        if not validate_ontario_postal_code(self.{field_name}):\n'
                    code += f'            errors.append("{field_name}")\n'
                elif 'phone' in field_name.lower():
                    code += f'        if not validate_phone_number(self.{field_name}):\n'
                    code += f'            errors.append("{field_name}")\n'
                elif 'email' in field_name.lower():
                    code += f'        if not validate_email_address(self.{field_name}):\n'
                    code += f'            errors.append("{field_name}")\n'
                elif 'court_file' in field_name.lower():
                    code += f'        if not validate_court_file_number(self.{field_name}):\n'
                    code += f'            errors.append("{field_name}")\n'
        
        code += '        return len(errors) == 0, errors\n'
        
        # Add YAML generation method
        code += '\n    def generate_yaml_questions(self, prefix=""):\n'
        code += '        """Generate YAML question blocks for this module"""\n'
        code += '        questions = []\n'
        
        for field_name in group_fields:
            field_info = common_fields[field_name]
            field_type = field_info['docassemble_type']
            
            # Get a sample label from variations
            sample_label = field_name.replace('_', ' ').title()
            if field_info['sample_variations']:
                sample_label = field_info['sample_variations'][0]['label'][:50] + "..." if len(field_info['sample_variations'][0]['label']) > 50 else field_info['sample_variations'][0]['label']
                # Clean up the label
                sample_label = sample_label.replace(':', '').strip()
            
            code += f'\n        # {field_name} question\n'
            code += f'        questions.append({{\n'
            code += f'            "question": "{sample_label}",\n'
            code += f'            "fields": [\n'
            code += f'                {{\n'
            code += f'                    "field": "{{prefix}}{field_name}",\n'
            code += f'                    "datatype": "{field_type}"\n'
            
            # Add validation if present
            validation_pattern = field_info.get('validation_pattern', '')
            if validation_pattern:
                code += f'                    "validate": "{validation_pattern}"\n'
            
            code += f'                }}\n'
            code += f'            ]\n'
            code += f'        }})\n'
        
        code += '\n        return questions\n'
        
        return code
    
    def generate_master_interview_template(self) -> str:
        """Generate master interview template that uses all modules"""
        code = '''"""
Master Interview Template for Ontario Family Law Forms
Uses modular components to build complete interviews.
"""

# Import all modules
from .base_objects import *
from .validation_functions import *
'''
        
        # Import all field modules
        for group_name in self.analysis_data['field_groups'].keys():
            module_name = ''.join(word.capitalize() for word in group_name.split('_')) + 'Module'
            code += f'from .{group_name} import {module_name}\n'
        
        code += '''

class OntarioFamilyLawInterview(DAObject):
    """
    Master interview class that coordinates all modules.
    Provides a framework for building any Ontario family law form interview.
    """
    
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        
        # Initialize all modules
'''
        
        # Initialize each module
        for group_name, group_data in self.analysis_data['field_groups'].items():
            class_name = ''.join(word.capitalize() for word in group_name.split('_')) + 'Module'
            code += f'        self.{group_name} = {class_name}()\n'
        
        code += '''        
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
        
'''
        
        # Add validation for each module
        for group_name in self.analysis_data['field_groups'].keys():
            code += f'        # Validate {group_name}\n'
            code += f'        valid, errors = self.{group_name}.validate_all_fields()\n'
            code += f'        if not valid:\n'
            code += f'            all_errors["{group_name}"] = errors\n'
            code += f'            all_valid = False\n\n'
        
        code += '''        return all_valid, all_errors
    
    def generate_complete_yaml(self, form_type="general"):
        """Generate complete YAML interview for specified form type"""
        
        yaml_content = []
        
        # Metadata
        yaml_content.append({
            "metadata": {
                "title": f"Ontario Family Law - {form_type.title()}",
                "short title": f"Form {self.form_number}",
                "generated": "''' + datetime.now().isoformat() + '''",
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
'''
        
        for group_name in self.analysis_data['field_groups'].keys():
            code += f'        # Add {group_name} questions\n'
            code += f'        {group_name}_questions = self.{group_name}.generate_yaml_questions()\n'
            code += f'        yaml_content.extend({group_name}_questions)\n\n'
        
        code += '''        
        return yaml_content
    
    def get_module_dependencies(self):
        """Return dependency graph of modules"""
        dependencies = {}
'''
        
        for group_name, group_data in self.analysis_data['field_groups'].items():
            code += f'        dependencies["{group_name}"] = {group_data["dependencies"]}\n'
        
        code += '''        
        return dependencies
    
    def get_form_completion_percentage(self):
        """Calculate completion percentage across all modules"""
        total_fields = 0
        completed_fields = 0
        
'''
        
        for group_name in self.analysis_data['field_groups'].keys():
            code += f'        # Count {group_name} fields\n'
            code += f'        module_fields = len([f for f in dir(self.{group_name}) if not f.startswith("_")])\n'
            code += f'        total_fields += module_fields\n'
            code += f'        # Count completed fields (non-empty values)\n'
            code += f'        for field_name in dir(self.{group_name}):\n'
            code += f'            if not field_name.startswith("_"):\n'
            code += f'                field_value = getattr(self.{group_name}, field_name)\n'
            code += f'                if field_value and field_value != "":\n'
            code += f'                    completed_fields += 1\n\n'
        
        code += '''        
        if total_fields == 0:
            return 0
        return int((completed_fields / total_fields) * 100)
'''
        
        return code
    
    def save_framework_files(self, output_dir: str):
        """Save all framework files to output directory"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate and save base objects
        base_objects = self.generate_base_objects()
        with open(os.path.join(output_dir, 'base_objects.py'), 'w', encoding='utf-8') as f:
            f.write(base_objects)
        
        # Generate and save validation functions
        validation_functions = self.generate_validation_functions()
        with open(os.path.join(output_dir, 'validation_functions.py'), 'w', encoding='utf-8') as f:
            f.write(validation_functions)
        
        # Generate and save field modules
        field_modules = self.generate_field_modules()
        for module_name, module_code in field_modules.items():
            with open(os.path.join(output_dir, f'{module_name}.py'), 'w', encoding='utf-8') as f:
                f.write(module_code)
        
        # Generate and save master interview template
        master_template = self.generate_master_interview_template()
        with open(os.path.join(output_dir, 'master_interview.py'), 'w', encoding='utf-8') as f:
            f.write(master_template)
        
        # Create __init__.py file
        init_content = '''"""
Ontario Family Law Interview Framework

Common components for generating Docassemble interviews for Ontario family law forms.
"""

from .base_objects import *
from .validation_functions import *
from .master_interview import OntarioFamilyLawInterview

__version__ = "1.0.0"
__author__ = "Form Factory Orchestrator"
__description__ = "Shared framework for Ontario family law form interviews"
'''
        
        with open(os.path.join(output_dir, '__init__.py'), 'w', encoding='utf-8') as f:
            f.write(init_content)
        
        print(f"✅ Framework files saved to: {output_dir}")
        print(f"📂 Generated Files:")
        print(f"   • base_objects.py - Core object definitions")
        print(f"   • validation_functions.py - Field validation functions")
        print(f"   • master_interview.py - Master interview template")
        
        for module_name in field_modules.keys():
            print(f"   • {module_name}.py - {module_name.replace('_', ' ').title()} module")
    
    def run_complete_generation(self, output_dir: str):
        """Run complete framework generation"""
        print("🏗️ Generating Common Interview Framework...")
        
        # Load analysis
        print("📊 Loading field analysis...")
        self.load_analysis()
        
        # Generate all framework components
        print("⚙️ Generating framework components...")
        self.save_framework_files(output_dir)
        
        print(f"\n🎯 Framework Generation Complete!")
        print(f"📋 Summary:")
        print(f"   • {len(self.analysis_data['field_groups'])} field modules created")
        print(f"   • {self.analysis_data['metadata']['common_fields_found']} common fields incorporated")
        print(f"   • Framework supports {self.analysis_data['metadata']['total_forms_analyzed']} analyzed forms")
        
        print(f"\n🚀 Next Steps:")
        print(f"  1. Review generated framework in {output_dir}")
        print(f"  2. Create form-specific interview generators")
        print(f"  3. Build automated conversion pipeline")
        print(f"  4. Generate comprehensive test suites")

def main():
    """Main execution function"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    analysis_file = os.path.join(base_dir, 'enhanced_common_fields_analysis.json')
    output_dir = os.path.join(base_dir, 'common_interview_framework')
    
    generator = CommonInterviewFrameworkGenerator(analysis_file)
    
    try:
        generator.run_complete_generation(output_dir)
    except Exception as e:
        print(f"❌ Error during framework generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()