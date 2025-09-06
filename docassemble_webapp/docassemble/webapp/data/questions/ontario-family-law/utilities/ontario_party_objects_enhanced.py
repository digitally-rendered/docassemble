#!/usr/bin/env python3
"""
Ontario Party Objects Enhanced - Party information structures for family law forms
Based on analysis of 201 address fields, 112 name fields, and 108 contact fields
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field as dataclass_field

@dataclass
class PartyObjectDefinition:
    """Defines a party object structure for Docassemble"""
    object_name: str
    object_type: str  # Individual, Person, Organization
    attributes: Dict[str, Any]
    methods: List[str] = dataclass_field(default_factory=list)
    forms_used: List[str] = dataclass_field(default_factory=list)
    
    def to_docassemble_object(self) -> Dict[str, Any]:
        """Generate Docassemble object definition"""
        obj_def = {
            'object': self.object_name,
            'type': self.object_type
        }
        
        # Add attribute definitions
        for attr_name, attr_config in self.attributes.items():
            if isinstance(attr_config, dict):
                if 'type' in attr_config:
                    obj_def[f"{self.object_name}.{attr_name}"] = attr_config
        
        return obj_def

class OntarioPartyObjects:
    """Party object definitions for Ontario family law forms"""
    
    def __init__(self):
        self.party_objects = self._initialize_party_objects()
        self.lawyer_objects = self._initialize_lawyer_objects()
        self.organization_objects = self._initialize_organization_objects()
    
    def _initialize_party_objects(self) -> Dict[str, PartyObjectDefinition]:
        """Initialize party object definitions"""
        return {
            "applicant": PartyObjectDefinition(
                object_name="applicant",
                object_type="Individual",
                attributes={
                    'name.first': {'type': 'text', 'label': 'First name'},
                    'name.middle': {'type': 'text', 'label': 'Middle name(s)', 'required': False},
                    'name.last': {'type': 'text', 'label': 'Last name or surname'},
                    'name.suffix': {'type': 'text', 'label': 'Suffix (Jr., Sr., etc.)', 'required': False},
                    'birthdate': {'type': 'date', 'label': 'Date of birth'},
                    'gender': {'type': 'radio', 'choices': ['Male', 'Female', 'Other', 'Prefer not to say']},
                    'email': {'type': 'email', 'label': 'Email address'},
                    'phone_number': {'type': 'text', 'label': 'Phone number'},
                    'fax_number': {'type': 'text', 'label': 'Fax number', 'required': False},
                    'address.address': {'type': 'text', 'label': 'Street address'},
                    'address.unit': {'type': 'text', 'label': 'Unit/Apt number', 'required': False},
                    'address.city': {'type': 'text', 'label': 'City'},
                    'address.province': {'type': 'text', 'label': 'Province', 'default': 'Ontario'},
                    'address.postal_code': {'type': 'text', 'label': 'Postal code'},
                    'address.country': {'type': 'text', 'label': 'Country', 'default': 'Canada'},
                    'occupation': {'type': 'text', 'label': 'Occupation'},
                    'employer': {'type': 'text', 'label': 'Employer name', 'required': False},
                    'sin': {'type': 'text', 'label': 'Social Insurance Number', 'required': False},
                    'has_lawyer': {'type': 'yesno', 'label': 'Represented by lawyer'},
                    'lawyer': {'type': 'object', 'object_type': 'Individual', 'show_if': 'has_lawyer'},
                    'is_self_represented': {'type': 'yesno', 'label': 'Self-represented'},
                    'language_preference': {'type': 'radio', 'choices': ['English', 'French']},
                    'requires_interpreter': {'type': 'yesno', 'label': 'Requires interpreter'},
                    'interpreter_language': {'type': 'text', 'show_if': 'requires_interpreter'}
                },
                methods=['name.full()', 'age_in_years()', 'address.block()'],
                forms_used=['All forms']
            ),
            "respondent": PartyObjectDefinition(
                object_name="respondent",
                object_type="Individual",
                attributes={
                    'name.first': {'type': 'text', 'label': 'First name'},
                    'name.middle': {'type': 'text', 'label': 'Middle name(s)', 'required': False},
                    'name.last': {'type': 'text', 'label': 'Last name or surname'},
                    'name.suffix': {'type': 'text', 'label': 'Suffix (Jr., Sr., etc.)', 'required': False},
                    'birthdate': {'type': 'date', 'label': 'Date of birth'},
                    'gender': {'type': 'radio', 'choices': ['Male', 'Female', 'Other', 'Prefer not to say']},
                    'email': {'type': 'email', 'label': 'Email address'},
                    'phone_number': {'type': 'text', 'label': 'Phone number'},
                    'fax_number': {'type': 'text', 'label': 'Fax number', 'required': False},
                    'address.address': {'type': 'text', 'label': 'Street address'},
                    'address.unit': {'type': 'text', 'label': 'Unit/Apt number', 'required': False},
                    'address.city': {'type': 'text', 'label': 'City'},
                    'address.province': {'type': 'text', 'label': 'Province', 'default': 'Ontario'},
                    'address.postal_code': {'type': 'text', 'label': 'Postal code'},
                    'address.country': {'type': 'text', 'label': 'Country', 'default': 'Canada'},
                    'occupation': {'type': 'text', 'label': 'Occupation'},
                    'employer': {'type': 'text', 'label': 'Employer name', 'required': False},
                    'sin': {'type': 'text', 'label': 'Social Insurance Number', 'required': False},
                    'has_lawyer': {'type': 'yesno', 'label': 'Represented by lawyer'},
                    'lawyer': {'type': 'object', 'object_type': 'Individual', 'show_if': 'has_lawyer'},
                    'is_self_represented': {'type': 'yesno', 'label': 'Self-represented'},
                    'served': {'type': 'yesno', 'label': 'Has been served'},
                    'service_date': {'type': 'date', 'label': 'Date of service', 'show_if': 'served'},
                    'service_method': {'type': 'text', 'label': 'Method of service', 'show_if': 'served'}
                },
                methods=['name.full()', 'age_in_years()', 'address.block()'],
                forms_used=['All forms']
            ),
            "added_party": PartyObjectDefinition(
                object_name="added_parties",
                object_type="DAList.using(object_type=Individual)",
                attributes={
                    'name.first': {'type': 'text', 'label': 'First name'},
                    'name.middle': {'type': 'text', 'label': 'Middle name(s)', 'required': False},
                    'name.last': {'type': 'text', 'label': 'Last name or surname'},
                    'party_type': {'type': 'radio', 'choices': ['Added Respondent', 'Third Party', 'Intervenor']},
                    'email': {'type': 'email', 'label': 'Email address'},
                    'phone_number': {'type': 'text', 'label': 'Phone number'},
                    'address.address': {'type': 'text', 'label': 'Street address'},
                    'address.city': {'type': 'text', 'label': 'City'},
                    'address.province': {'type': 'text', 'label': 'Province'},
                    'address.postal_code': {'type': 'text', 'label': 'Postal code'},
                    'has_lawyer': {'type': 'yesno', 'label': 'Represented by lawyer'},
                    'lawyer': {'type': 'object', 'object_type': 'Individual', 'show_if': 'has_lawyer'}
                },
                methods=['name.full()', 'address.block()'],
                forms_used=['Complex cases']
            )
        }
    
    def _initialize_lawyer_objects(self) -> Dict[str, PartyObjectDefinition]:
        """Initialize lawyer object definitions"""
        return {
            "lawyer": PartyObjectDefinition(
                object_name="lawyer",
                object_type="Individual",
                attributes={
                    'name.first': {'type': 'text', 'label': 'First name'},
                    'name.last': {'type': 'text', 'label': 'Last name'},
                    'firm_name': {'type': 'text', 'label': 'Law firm name'},
                    'lsuc_number': {'type': 'text', 'label': 'LSO number', 'required': False},
                    'email': {'type': 'email', 'label': 'Email address'},
                    'phone_number': {'type': 'text', 'label': 'Phone number'},
                    'fax_number': {'type': 'text', 'label': 'Fax number'},
                    'address.address': {'type': 'text', 'label': 'Office address'},
                    'address.suite': {'type': 'text', 'label': 'Suite number', 'required': False},
                    'address.city': {'type': 'text', 'label': 'City'},
                    'address.province': {'type': 'text', 'label': 'Province', 'default': 'Ontario'},
                    'address.postal_code': {'type': 'text', 'label': 'Postal code'},
                    'preferred_contact': {'type': 'radio', 'choices': ['Email', 'Phone', 'Fax', 'Mail']},
                    'accepts_service': {'type': 'yesno', 'label': 'Accepts service on behalf of client'}
                },
                methods=['name.full()', 'address.block()', 'contact_info()'],
                forms_used=['Most forms']
            )
        }
    
    def _initialize_organization_objects(self) -> Dict[str, PartyObjectDefinition]:
        """Initialize organization object definitions"""
        return {
            "court_office": PartyObjectDefinition(
                object_name="court",
                object_type="Organization",
                attributes={
                    'name': {'type': 'text', 'label': 'Court name'},
                    'court_type': {
                        'type': 'radio',
                        'label': 'Type of court',
                        'choices': [
                            'Superior Court of Justice',
                            'Superior Court of Justice Family Branch',
                            'Ontario Court of Justice'
                        ]
                    },
                    'file_number': {'type': 'text', 'label': 'Court file number'},
                    'address.address': {'type': 'text', 'label': 'Court address'},
                    'address.city': {'type': 'text', 'label': 'City'},
                    'address.province': {'type': 'text', 'label': 'Province', 'default': 'Ontario'},
                    'address.postal_code': {'type': 'text', 'label': 'Postal code'},
                    'phone_number': {'type': 'text', 'label': 'Court phone number'},
                    'fax_number': {'type': 'text', 'label': 'Court fax number'},
                    'email': {'type': 'email', 'label': 'Court email', 'required': False},
                    'municipality': {'type': 'text', 'label': 'Municipality'},
                    'judge_name': {'type': 'text', 'label': 'Name of Judge', 'required': False},
                    'registrar_name': {'type': 'text', 'label': 'Name of Registrar', 'required': False},
                    'courtroom': {'type': 'text', 'label': 'Courtroom number', 'required': False}
                },
                methods=['address.block()', 'contact_info()'],
                forms_used=['All forms']
            ),
            "government_agency": PartyObjectDefinition(
                object_name="agency",
                object_type="Organization",
                attributes={
                    'name': {'type': 'text', 'label': 'Agency name'},
                    'agency_type': {
                        'type': 'radio',
                        'choices': [
                            'Family Responsibility Office (FRO)',
                            'Office of the Children\'s Lawyer (OCL)',
                            'Children\'s Aid Society (CAS)',
                            'Other government agency'
                        ]
                    },
                    'contact_person': {'type': 'text', 'label': 'Contact person name', 'required': False},
                    'reference_number': {'type': 'text', 'label': 'Reference/Case number', 'required': False},
                    'phone_number': {'type': 'text', 'label': 'Phone number'},
                    'fax_number': {'type': 'text', 'label': 'Fax number', 'required': False},
                    'email': {'type': 'email', 'label': 'Email address', 'required': False},
                    'address.address': {'type': 'text', 'label': 'Address'},
                    'address.city': {'type': 'text', 'label': 'City'},
                    'address.province': {'type': 'text', 'label': 'Province'},
                    'address.postal_code': {'type': 'text', 'label': 'Postal code'}
                },
                methods=['address.block()', 'contact_info()'],
                forms_used=['Support and custody forms']
            )
        }
    
    def generate_objects_yaml(self) -> str:
        """Generate YAML objects section for all party objects"""
        yaml_lines = [
            "---",
            "# Ontario Family Law Party Objects",
            "# Auto-generated from party object definitions",
            "---",
            "objects:",
            "  - applicant: Individual",
            "  - respondent: Individual",
            "  - added_parties: DAList.using(object_type=Individual, there_are_any=False)",
            "  - court: Organization",
            "  - agency: Organization",
            "---",
            "# Lawyer objects conditional on representation",
            "objects from code:",
            "  - applicant.lawyer: Individual if applicant.has_lawyer else None",
            "  - respondent.lawyer: Individual if respondent.has_lawyer else None",
            "---"
        ]
        
        return "\n".join(yaml_lines)
    
    def generate_party_questions(self, party_type: str = "applicant") -> List[Dict[str, Any]]:
        """Generate question blocks for party information"""
        questions = []
        
        # Name question
        questions.append({
            'id': f'{party_type}_name',
            'question': f"What is the {party_type}'s name?",
            'fields': [
                {f"First name": f"{party_type}.name.first"},
                {f"Middle name(s)": f"{party_type}.name.middle", "required": False},
                {f"Last name or surname": f"{party_type}.name.last"}
            ]
        })
        
        # Contact information
        questions.append({
            'id': f'{party_type}_contact',
            'question': f"What is the {party_type}'s contact information?",
            'fields': [
                {f"Email address": f"{party_type}.email", "datatype": "email", "required": False},
                {f"Phone number": f"{party_type}.phone_number", "required": False},
                {f"Fax number": f"{party_type}.fax_number", "required": False}
            ]
        })
        
        # Address question
        questions.append({
            'id': f'{party_type}_address',
            'question': f"What is the {party_type}'s address?",
            'fields': [
                {f"Street address": f"{party_type}.address.address"},
                {f"Unit/Apt number": f"{party_type}.address.unit", "required": False},
                {f"City": f"{party_type}.address.city"},
                {f"Province": f"{party_type}.address.province", "default": "Ontario"},
                {f"Postal code": f"{party_type}.address.postal_code"},
                {f"Country": f"{party_type}.address.country", "default": "Canada", "required": False}
            ]
        })
        
        # Legal representation
        questions.append({
            'id': f'{party_type}_lawyer',
            'question': f"Is the {party_type} represented by a lawyer?",
            'fields': [
                {f"Represented by lawyer": f"{party_type}.has_lawyer", "datatype": "yesnoradio"}
            ]
        })
        
        # Lawyer details (conditional)
        questions.append({
            'id': f'{party_type}_lawyer_details',
            'question': f"Lawyer information for {party_type}",
            'show if': f"{party_type}.has_lawyer",
            'fields': [
                {f"Lawyer's name": f"{party_type}.lawyer.name.full()"},
                {f"Law firm": f"{party_type}.lawyer.firm_name"},
                {f"Phone": f"{party_type}.lawyer.phone_number"},
                {f"Email": f"{party_type}.lawyer.email", "datatype": "email"}
            ]
        })
        
        return questions

# Global instance
ontario_parties = OntarioPartyObjects()