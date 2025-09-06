#!/usr/bin/env python3
"""
Streamlined Form Generator for Ontario Family Law
Generates ONLY form-specific fields, excluding everything in common_intake_enhanced_with_validation.yml
Uses common Ontario interview components from Python scripts
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
from dataclasses import dataclass, field as dataclass_field


@dataclass
class CommonIntakeMapping:
    """Maps common intake fields to their actual variable names"""
    
    # Based on actual common_intake_enhanced_with_validation.yml structure
    INTAKE_VARIABLES = {
        # Emergency and MIP
        'emergency_situation': 'Emergency status',
        'mip_status': 'MIP completion status',
        
        # Relationship and orders
        'relationship_status': 'Relationship with other party',
        'seeking_divorce': 'Seeking divorce order',
        'seeking_custody': 'Seeking custody/access',
        'seeking_child_support': 'Seeking child support',
        'seeking_spousal_support': 'Seeking spousal support',
        'seeking_property': 'Seeking property division',
        'seeking_exclusive_possession': 'Seeking exclusive possession',
        'seeking_restraining_order': 'Seeking restraining order',
        'seeking_paternity': 'Seeking paternity declaration',
        'seeking_enforcement': 'Seeking enforcement',
        'seeking_variation': 'Seeking variation',
        
        # User (applicant) information
        'user.name.first': 'Applicant first name',
        'user.name.middle': 'Applicant middle name',
        'user.name.last': 'Applicant last name',
        'user.birthdate': 'Applicant date of birth',
        'user.also_known_as': 'Applicant AKA',
        'user.address.address': 'Applicant street address',
        'user.address.unit': 'Applicant unit/apt',
        'user.address.city': 'Applicant city',
        'user.address.state': 'Applicant province',
        'user.address.postal_code': 'Applicant postal code',
        'user.phone_number': 'Applicant phone',
        'user.mobile_number': 'Applicant mobile',
        'user.email': 'Applicant email',
        
        # User lawyer
        'has_lawyer': 'User has lawyer',
        'user_lawyer.name.text': 'User lawyer name',
        'user_lawyer.firm_name': 'User lawyer firm',
        'user_lawyer.lsuc_number': 'User lawyer LSO number',
        'user_lawyer.address.address': 'User lawyer address',
        'user_lawyer.phone_number': 'User lawyer phone',
        'user_lawyer.email': 'User lawyer email',
        
        # Opposing party (respondent)
        'opposing_party.name.first': 'Respondent first name',
        'opposing_party.name.middle': 'Respondent middle name',
        'opposing_party.name.last': 'Respondent last name',
        'opposing_party.birthdate': 'Respondent date of birth',
        'opposing_party.also_known_as': 'Respondent AKA',
        'opposing_party.address.address': 'Respondent street address',
        'opposing_party.address.city': 'Respondent city',
        'opposing_party.address.state': 'Respondent province',
        'opposing_party.address.postal_code': 'Respondent postal code',
        'opposing_party.phone_number': 'Respondent phone',
        'opposing_party.email': 'Respondent email',
        
        # Opposing lawyer
        'opposing_has_lawyer': 'Respondent has lawyer',
        'opposing_lawyer.name.text': 'Respondent lawyer name',
        'opposing_lawyer.firm_name': 'Respondent lawyer firm',
        'opposing_lawyer.lsuc_number': 'Respondent lawyer LSO number',
        
        # Court information
        'court.file_exists': 'Existing court file',
        'court.name': 'Court name',
        'court.location': 'Court location',
        'court.file_number': 'Court file number',
        'court.date_started': 'Court date started',
        
        # Children
        'has_children': 'Has children',
        'children_data': 'Children information',
        
        # Financial basics
        'claiming_support': 'Claiming support',
        'paying_support': 'Paying support',
        'owns_real_estate': 'Owns real estate',
        'owns_business': 'Owns business',
        'has_investments': 'Has investments',
        'has_pension': 'Has pension',
        'total_assets': 'Total assets',
        'total_debts': 'Total debts'
    }
    
    # Common field patterns to exclude
    EXCLUDE_PATTERNS = [
        # Party names and basic info
        r'(applicant|petitioner|user|opposing|respondent).*(name|address|phone|email|birth)',
        r'(first|middle|last)\s*name',
        r'date.*birth',
        r'street|city|province|postal\s*code',
        r'phone|mobile|email',
        
        # Lawyer info
        r'lawyer|counsel|representative|lso\s*number|law\s*firm',
        
        # Court basics
        r'court.*(name|location|file\s*number|municipality)',
        r'file\s*number',
        
        # Children basics
        r'child.*(name|birth|living|custody)',
        r'number.*children',
        
        # Basic relationship/marriage
        r'relationship.*status',
        r'marriage.*date',
        r'separation.*date',
        r'divorce.*date',
        
        # Basic orders/claims
        r'seeking.*|claiming.*',
        r'emergency|mip',
        
        # Basic financial
        r'total.*(assets|debts)',
        r'owns.*(business|real\s*estate)',
        r'has.*(pension|investment)'
    ]
    
    @classmethod
    def is_common_intake_field(cls, field_label: str, field_name: str = "") -> bool:
        """Check if a field is already in common intake"""
        combined = f"{field_label} {field_name}".lower()
        
        # Check against known variables
        for var_name in cls.INTAKE_VARIABLES.keys():
            if var_name.lower() in combined:
                return True
        
        # Check against patterns
        for pattern in cls.EXCLUDE_PATTERNS:
            if re.search(pattern, combined, re.IGNORECASE):
                return True
        
        return False


@dataclass
class FormSpecificField:
    """Represents a form-specific field not in common intake"""
    field_id: str
    label: str
    variable: str
    field_type: str = "text"
    required: bool = False
    validation: Optional[str] = None
    help_text: Optional[str] = None
    section: str = "additional"
    

class OntarioComponentsIntegration:
    """Integrates common Ontario interview components from Python scripts"""
    
    @staticmethod
    def generate_ontario_validation() -> str:
        """Generate Ontario-specific validation functions"""
        return """---
code: |
  # Ontario-specific validation functions
  def ontario_postal_code_validation(value):
    '''Validate Ontario postal code (K, L, M, N, P prefixes)'''
    import re
    pattern = r'^[KLMNP][0-9][A-Z]\\s?[0-9][A-Z][0-9]$'
    if not re.match(pattern, str(value).upper().replace(' ', '')):
      validation_error("Please enter a valid Ontario postal code")
    return True
  
  def ontario_phone_validation(value):
    '''Validate Ontario phone numbers'''
    import re
    # Remove all non-digits
    digits = re.sub(r'\\D', '', str(value))
    # Check for 10 digits (with optional 1 prefix)
    if len(digits) == 11 and digits[0] == '1':
      digits = digits[1:]
    if len(digits) != 10:
      validation_error("Please enter a valid 10-digit phone number")
    # Check for valid Ontario area codes
    area_code = digits[:3]
    ontario_codes = ['226', '249', '289', '343', '365', '416', '437', '519', '548', 
                     '613', '647', '705', '807', '905']
    if area_code not in ontario_codes:
      validation_error(f"Area code {area_code} is not a valid Ontario area code")
    return True
  
  def sin_validation(value):
    '''Validate Canadian SIN'''
    import re
    # Remove spaces and hyphens
    sin = re.sub(r'[\\s-]', '', str(value))
    if not re.match(r'^\\d{9}$', sin):
      validation_error("SIN must be 9 digits")
    # Luhn algorithm check
    check_sum = 0
    for i in range(9):
      digit = int(sin[i])
      if i % 2 == 1:  # Every second digit
        digit = digit * 2
        if digit > 9:
          digit = digit - 9
      check_sum += digit
    if check_sum % 10 != 0:
      validation_error("Invalid SIN number")
    return True"""
    
    @staticmethod
    def generate_ontario_court_locations() -> str:
        """Generate Ontario court locations list"""
        return """---
code: |
  def ontario_court_locations():
    '''List of Ontario court locations'''
    return [
      "Toronto (47 Sheppard Avenue East)",
      "Toronto (311 Jarvis Street)", 
      "Toronto (393 University Avenue)",
      "Ottawa (161 Elgin Street)",
      "London (80 Dundas Street)",
      "Hamilton (55 Main Street West)",
      "Kitchener (85 Frederick Street)",
      "Windsor (245 Windsor Avenue)",
      "Barrie (75 Mulcaster Street)",
      "Kingston (5 Court Street)",
      "Thunder Bay (125 Brodie Street North)",
      "Sudbury (155 Elm Street)",
      "Peterborough (470 Water Street)",
      "Oshawa (150 Bond Street East)",
      "Belleville (15 Victoria Avenue)",
      "St. Catharines (59 Church Street)",
      "Brampton (7755 Hurontario Street)",
      "Mississauga (7755 Hurontario Street)",
      "North Bay (360 Plouffe Street)",
      "Timmins (220 Algonquin Boulevard East)",
      "Sault Ste. Marie (426 Queen Street East)",
      "Guelph (74 Woolwich Street)",
      "Cambridge (85 Frederick Street)",
      "Woodstock (415 Hunter Street)",
      "Stratford (1 Huron Street)",
      "Orangeville (10 Louisa Street)",
      "Milton (491 Steeles Avenue East)",
      "Newmarket (50 Eagle Street West)"
    ]"""


class StreamlinedFormGenerator:
    """Generates streamlined form-specific interviews"""
    
    def __init__(self, form_number: str, form_title: str = None):
        self.form_number = form_number
        self.form_title = form_title or f"Form {form_number}"
        self.specific_fields: List[FormSpecificField] = []
        self.sections: Dict[str, List[FormSpecificField]] = {}
        self.intake_mapping = CommonIntakeMapping()
        self.components = OntarioComponentsIntegration()
        
    def load_and_filter_fields(self) -> bool:
        """Load parsed fields and filter out ALL common intake fields"""
        parsed_path = Path(__file__).parent / 'parsed_forms' / f'form_{self.form_number}_fields.json'
        
        if not parsed_path.exists():
            print(f"Warning: No parsed data for Form {self.form_number}")
            return False
        
        with open(parsed_path, 'r') as f:
            parsed_fields = json.load(f)
        
        # Statistics
        total_fields = len(parsed_fields)
        excluded_count = 0
        
        for field_data in parsed_fields:
            field_label = field_data.get('field_label', '').strip()
            field_name = field_data.get('field_name', '').strip()
            
            # Check if it's a common intake field
            if CommonIntakeMapping.is_common_intake_field(field_label, field_name):
                excluded_count += 1
                continue
            
            # Skip empty or problematic fields
            if not field_label or len(field_label) > 100:
                excluded_count += 1
                continue
            
            # Skip obviously duplicated/malformed fields
            if field_label.count(':') > 2 or field_name.count('_') > 6:
                excluded_count += 1
                continue
            
            # Create form-specific field
            specific_field = self._create_specific_field(field_data)
            if specific_field:
                self.specific_fields.append(specific_field)
                
                # Categorize by section
                section = specific_field.section
                if section not in self.sections:
                    self.sections[section] = []
                self.sections[section].append(specific_field)
        
        print(f"Form {self.form_number}: {total_fields} total fields, {excluded_count} excluded (common intake), {len(self.specific_fields)} specific fields")
        return True
    
    def _create_specific_field(self, field_data: Dict) -> Optional[FormSpecificField]:
        """Create a form-specific field"""
        label = self._clean_label(field_data.get('field_label', ''))
        
        if not label:
            return None
        
        # Determine section based on form type
        section = self._determine_form_specific_section(label)
        
        return FormSpecificField(
            field_id=field_data.get('field_id', ''),
            label=label,
            variable=self._generate_form_variable(label),
            field_type=self._determine_field_type(field_data),
            required=field_data.get('required', False),
            help_text=field_data.get('help_text'),
            section=section
        )
    
    def _clean_label(self, label: str) -> str:
        """Clean field label"""
        # Remove multiple colons and duplicates
        if ':' in label:
            parts = label.split(':')
            # Take the first meaningful part
            for part in parts:
                cleaned = part.strip()
                if cleaned and len(cleaned) > 2:
                    label = cleaned
                    break
        
        # Remove extra whitespace
        label = re.sub(r'\s+', ' ', label)
        
        # Remove trailing punctuation
        label = re.sub(r'[:\s]+$', '', label)
        
        return label
    
    def _generate_form_variable(self, label: str) -> str:
        """Generate form-specific variable name"""
        # Clean the label
        clean = re.sub(r'[^\w\s]', '', label.lower())
        clean = re.sub(r'\s+', '_', clean)
        
        # Remove duplicate words
        parts = clean.split('_')
        unique = []
        for part in parts:
            if part and part not in unique:
                unique.append(part)
        
        # Form-specific prefix
        base = '_'.join(unique[:4])  # Limit to 4 parts
        return f"form{self.form_number}_{base}"
    
    def _determine_field_type(self, field_data: Dict) -> str:
        """Determine field type"""
        field_type = field_data.get('field_type', '').lower()
        label = field_data.get('field_label', '').lower()
        
        if 'date' in field_type or 'date' in label:
            return 'date'
        elif 'currency' in field_type or any(x in label for x in ['$', 'amount', 'income', 'expense']):
            return 'currency'
        elif 'sin' in label or 'social insurance' in label:
            return 'text'  # With SIN validation
        elif '[]' in field_data.get('field_label', '') or 'checkbox' in field_type:
            return 'yesno'
        elif 'phone' in label:
            return 'phone'
        elif 'email' in label:
            return 'email'
        else:
            return 'text'
    
    def _determine_form_specific_section(self, label: str) -> str:
        """Determine section based on form type and field content"""
        label_lower = label.lower()
        
        # Form 8/8A specific sections
        if self.form_number in ['8', '8A']:
            if any(word in label_lower for word in ['ground', 'basis', 'reason']):
                return 'grounds_for_application'
            elif any(word in label_lower for word in ['previous', 'prior', 'past']):
                return 'previous_proceedings'
            elif any(word in label_lower for word in ['reconciliation', 'counselling']):
                return 'reconciliation_efforts'
        
        # Form 10 (Answer) specific
        elif self.form_number == '10':
            if any(word in label_lower for word in ['dispute', 'disagree', 'contest']):
                return 'disputed_claims'
            elif any(word in label_lower for word in ['counter', 'cross']):
                return 'counter_claims'
        
        # Form 13/13.1 (Financial) specific
        elif self.form_number in ['13', '13.1']:
            if any(word in label_lower for word in ['employer', 'occupation', 'work']):
                return 'employment_details'
            elif any(word in label_lower for word in ['bank', 'account', 'savings']):
                return 'bank_accounts'
            elif any(word in label_lower for word in ['vehicle', 'car', 'automobile']):
                return 'vehicles'
            elif any(word in label_lower for word in ['rrsp', 'pension', 'retirement']):
                return 'retirement_assets'
            elif any(word in label_lower for word in ['stock', 'bond', 'investment']):
                return 'investments'
            elif any(word in label_lower for word in ['credit', 'loan', 'mortgage']):
                return 'debts_and_liabilities'
        
        # Form 36 (Affidavit for Divorce) specific
        elif self.form_number == '36':
            if any(word in label_lower for word in ['marriage', 'ceremony', 'married']):
                return 'marriage_details'
            elif any(word in label_lower for word in ['breakdown', 'irretrievable']):
                return 'marriage_breakdown'
            elif any(word in label_lower for word in ['barrier', 'religious']):
                return 'divorce_barriers'
        
        return 'additional_information'
    
    def generate_interview(self) -> str:
        """Generate streamlined form-specific interview"""
        
        if not self.load_and_filter_fields():
            if not self.specific_fields:
                return self._generate_minimal_interview()
        
        yaml_parts = []
        
        # Metadata
        yaml_parts.append(self._generate_metadata())
        
        # Include common intake
        yaml_parts.append(self._generate_includes())
        
        # Objects for form-specific data
        yaml_parts.append(self._generate_objects())
        
        # Ontario-specific validation functions
        yaml_parts.append(self.components.generate_ontario_validation())
        yaml_parts.append(self.components.generate_ontario_court_locations())
        
        # Mandatory code
        yaml_parts.append(self._generate_mandatory_code())
        
        # Form-specific questions by section
        for section_name, fields in self.sections.items():
            if fields:
                yaml_parts.append(self._generate_section_questions(section_name, fields))
        
        # Review screen for form-specific fields
        yaml_parts.append(self._generate_review())
        
        # Final screen
        yaml_parts.append(self._generate_final_screen())
        
        return '\n'.join(yaml_parts)
    
    def _generate_metadata(self) -> str:
        """Generate metadata"""
        return f"""---
metadata:
  title: |
    Form {self.form_number}: {self.form_title} - Specific Fields
  short title: |
    Form {self.form_number} Specific
  description: |
    Form-specific fields for Ontario Family Law Form {self.form_number}
    To be used after common intake completion
  authors:
    - name: Ontario Family Law System
  revision_date: {datetime.now().strftime('%Y-%m-%d')}
  tags:
    - family law
    - ontario
    - form {self.form_number}"""
    
    def _generate_includes(self) -> str:
        """Include common intake"""
        return """---
include:
  - docassemble.base:data/questions/basic-questions.yml
---
# NOTE: This interview assumes common_intake_enhanced_with_validation.yml
# has already been completed and data is available in the session"""
    
    def _generate_objects(self) -> str:
        """Generate objects for form-specific data"""
        return f"""---
objects:
  - form{self.form_number}: DAObject"""
    
    def _generate_mandatory_code(self) -> str:
        """Generate mandatory code"""
        code = f"""---
mandatory: True
code: |
  # Form {self.form_number} specific flow
  
  # Introduction to form-specific questions
  form{self.form_number}_intro"""
        
        # Add sections
        for section_name in self.sections.keys():
            code += f"\n  form{self.form_number}_{section_name}_complete"
        
        code += f"\n  form{self.form_number}_review"
        code += f"\n  form{self.form_number}_complete"
        
        return code
    
    def _generate_section_questions(self, section_name: str, fields: List[FormSpecificField]) -> str:
        """Generate questions for a section"""
        # Create readable section title
        section_title = section_name.replace('_', ' ').title()
        
        # Skip if no fields
        if not fields:
            return f"""---
code: |
  form{self.form_number}_{section_name}_complete = True"""
        
        # Introduction screen for form
        if section_name == list(self.sections.keys())[0]:  # First section
            intro = f"""---
question: |
  Form {self.form_number}: {self.form_title}
subquestion: |
  We've collected your basic information in the common intake.
  
  Now we need some additional information specific to Form {self.form_number}.
  
  % if len({repr(list(self.sections.keys()))}) > 1:
  We'll ask about:
  % for section in {repr(list(self.sections.keys()))}:
  - ${{ section.replace('_', ' ').title() }}
  % endfor
  % endif
continue button field: form{self.form_number}_intro
---"""
            question = intro
        else:
            question = ""
        
        # Generate the section question
        question += f"""---
question: |
  {section_title}
subquestion: |
  % if '{section_name}' == 'employment_details':
  Please provide details about employment and income sources.
  % elif '{section_name}' == 'bank_accounts':
  Please list all bank accounts and financial institutions.
  % elif '{section_name}' == 'vehicles':
  Please provide information about all vehicles owned or leased.
  % elif '{section_name}' == 'debts_and_liabilities':
  Please list all debts, loans, and financial obligations.
  % else:
  Please provide the following information for Form {self.form_number}.
  % endif
fields:"""
        
        # Add fields
        seen_labels = set()
        for field in fields:
            # Skip duplicates
            if field.label in seen_labels:
                continue
            seen_labels.add(field.label)
            
            question += f"\n  - {field.label}: {field.variable}"
            
            if field.field_type != 'text':
                question += f"\n    datatype: {field.field_type}"
            
            if field.required:
                question += "\n    required: True"
            
            # Add validation for specific field types
            if 'sin' in field.variable:
                question += "\n    validation code: |\n      sin_validation(value)"
            elif 'postal' in field.variable and 'ontario' in field.variable:
                question += "\n    validation code: |\n      ontario_postal_code_validation(value)"
            elif field.field_type == 'phone':
                question += "\n    validation code: |\n      ontario_phone_validation(value)"
            
            if field.help_text:
                question += f"\n    help: |\n      {field.help_text}"
        
        question += f"\ncontinue button field: form{self.form_number}_{section_name}_complete"
        
        return question
    
    def _generate_review(self) -> str:
        """Generate review screen for form-specific fields"""
        return f"""---
event: form{self.form_number}_review
question: |
  Review Form {self.form_number} Information
subquestion: |
  Please review the form-specific information you've provided.
  
  Click on any section to make changes.
review:
  - note: |
      ### Common Information
      *(From intake - already reviewed)*
      
      **Applicant:** ${{ user.name.full() }}
      
      **Respondent:** ${{ opposing_party.name.full() }}
      
      **Court:** ${{ court.location if court.file_exists else "No existing file" }}"""
    
    def _generate_final_screen(self) -> str:
        """Generate final screen"""
        return f"""---
event: form{self.form_number}_complete
question: |
  Form {self.form_number} Complete
subquestion: |
  You have completed all required information for Form {self.form_number} ({self.form_title}).
  
  **Information Collected:**
  - ✓ Common intake information (parties, court, children)
  - ✓ Form {self.form_number} specific fields ({len(self.specific_fields)} fields)
  
  **Next Steps:**
  1. Review all information for accuracy
  2. Generate the PDF form
  3. Print and sign where required
  4. File with the court
  
  **Filing Information:**
  % if court.file_exists:
  - Court: ${{ court.name }}
  - Location: ${{ court.location }}
  - File Number: ${{ court.file_number }}
  % else:
  - You will need to file this as a new application
  - Court location will be determined based on your municipality
  % endif
  
buttons:
  - Generate PDF: generate_pdf
  - Exit: exit
  - Restart: restart"""
    
    def _generate_minimal_interview(self) -> str:
        """Generate minimal interview when no specific fields"""
        return f"""---
metadata:
  title: Form {self.form_number}: {self.form_title}
  short title: Form {self.form_number}
---
include:
  - docassemble.base:data/questions/basic-questions.yml
---
mandatory: True
event: form{self.form_number}_complete
question: |
  Form {self.form_number} - No Additional Fields Required
subquestion: |
  All information needed for Form {self.form_number} has been collected in the common intake.
  
  **Collected Information:**
  - ✓ Party information
  - ✓ Court information
  - ✓ Children (if applicable)
  - ✓ Orders being sought
  
  You can now generate Form {self.form_number}.
buttons:
  - Generate Form: generate_pdf
  - Exit: exit"""


def generate_all_streamlined_forms():
    """Generate streamlined interviews for all forms"""
    output_dir = Path(__file__).parent / 'streamlined_interviews'
    output_dir.mkdir(exist_ok=True)
    
    # Get all parsed forms
    parsed_dir = Path(__file__).parent / 'parsed_forms'
    parsed_files = list(parsed_dir.glob('form_*_fields.json'))
    
    results = []
    
    for parsed_file in parsed_files:
        match = re.search(r'form_([^_]+)_fields', parsed_file.name)
        if not match:
            continue
        
        form_number = match.group(1)
        
        # Generate streamlined interview
        generator = StreamlinedFormGenerator(form_number)
        yaml_content = generator.generate_interview()
        
        # Save to file
        output_file = output_dir / f'form_{form_number}_streamlined.yml'
        with open(output_file, 'w') as f:
            f.write(yaml_content)
        
        results.append({
            'form_number': form_number,
            'total_specific_fields': len(generator.specific_fields),
            'sections': len(generator.sections),
            'output_file': output_file.name
        })
    
    # Save summary
    summary = {
        'generated_at': datetime.now().isoformat(),
        'total_forms': len(results),
        'forms': results,
        'note': 'These are streamlined interviews with ONLY form-specific fields'
    }
    
    with open(output_dir / 'generation_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ Generated {len(results)} streamlined interviews")
    print(f"📁 Output: {output_dir}")
    print("ℹ️  These interviews contain ONLY form-specific fields")
    print("ℹ️  Common intake fields are completely excluded")
    
    return results


if __name__ == "__main__":
    generate_all_streamlined_forms()