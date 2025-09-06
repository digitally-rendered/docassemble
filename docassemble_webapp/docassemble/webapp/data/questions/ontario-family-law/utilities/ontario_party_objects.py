#!/usr/bin/env python3
"""
Ontario Party Objects - Person and organization dataclasses for Ontario family law
Programmatically generates YAML objects for parties in family law proceedings
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, date
import re

@dataclass
class OntarioAddress:
    """Ontario address with validation"""
    street: str = ""
    city: str = "" 
    province: str = "Ontario"
    postal_code: str = ""
    country: str = "Canada"
    
    def block(self) -> str:
        """Format address as a block"""
        lines = []
        if self.street:
            lines.append(self.street)
        if self.city:
            city_line = self.city
            if self.province:
                city_line += f", {self.province}"
            if self.postal_code:
                city_line += f"  {self.postal_code}"
            lines.append(city_line)
        if self.country and self.country != "Canada":
            lines.append(self.country)
        return "\n".join(lines)
    
    def to_docassemble_object(self) -> Dict[str, Any]:
        """Generate Docassemble Address object definition"""
        return {
            "Address": {
                "address": self.street,
                "city": self.city,
                "state": self.province,
                "zip": self.postal_code,
                "country": self.country
            }
        }

@dataclass 
class OntarioName:
    """Ontario name with legal formatting"""
    first: str = ""
    middle: str = ""
    last: str = ""
    suffix: str = ""
    
    # Legal name variations
    maiden_name: str = ""
    former_name: str = ""
    aliases: List[str] = field(default_factory=list)
    
    def full(self, middle_initial: bool = False) -> str:
        """Generate full name"""
        parts = []
        if self.first:
            parts.append(self.first)
        if self.middle:
            if middle_initial:
                parts.append(f"{self.middle[0]}.")
            else:
                parts.append(self.middle)
        if self.last:
            parts.append(self.last)
        if self.suffix:
            parts.append(self.suffix)
        return " ".join(parts)
    
    def first_last(self) -> str:
        """First and last name only"""
        parts = []
        if self.first:
            parts.append(self.first)
        if self.last:
            parts.append(self.last)
        return " ".join(parts)
    
    def to_docassemble_object(self) -> Dict[str, Any]:
        """Generate Docassemble Name object definition"""
        return {
            "IndividualName": {
                "first": self.first,
                "middle": self.middle, 
                "last": self.last,
                "suffix": self.suffix
            }
        }

@dataclass
class OntarioLawyer:
    """Ontario lawyer information"""
    name: OntarioName = field(default_factory=OntarioName)
    firm_name: str = ""
    address: OntarioAddress = field(default_factory=OntarioAddress)
    phone_number: str = ""
    fax_number: str = ""
    email: str = ""
    lsuc_number: str = ""  # Law Society of Ontario number
    
    def to_docassemble_object(self) -> Dict[str, Any]:
        """Generate Docassemble Person object for lawyer"""
        return {
            "Individual": {
                "name.first": self.name.first,
                "name.middle": self.name.middle,
                "name.last": self.name.last,
                "firm_name": self.firm_name,
                "address": self.address.to_docassemble_object()["Address"],
                "phone_number": self.phone_number,
                "email": self.email,
                "lsuc_number": self.lsuc_number
            }
        }

@dataclass
class OntarioFinancialInfo:
    """Financial information for family law proceedings"""
    gross_annual_income: float = 0.0
    net_annual_income: float = 0.0
    employment_income: float = 0.0
    self_employment_income: float = 0.0
    investment_income: float = 0.0
    pension_income: float = 0.0
    ei_benefits: float = 0.0
    social_assistance: float = 0.0
    other_income: float = 0.0
    
    # Support information
    child_support_paid: float = 0.0
    child_support_received: float = 0.0
    spousal_support_paid: float = 0.0
    spousal_support_received: float = 0.0
    
    # Assets and debts
    total_assets: float = 0.0
    total_debts: float = 0.0
    
    def calculate_total_income(self) -> float:
        """Calculate total income from all sources"""
        return (self.employment_income + self.self_employment_income + 
                self.investment_income + self.pension_income + 
                self.ei_benefits + self.social_assistance + self.other_income)
    
    def to_docassemble_object(self) -> Dict[str, Any]:
        """Generate financial information object"""
        return {
            "gross_annual_income": self.gross_annual_income,
            "net_annual_income": self.net_annual_income,
            "employment_income": self.employment_income,
            "self_employment_income": self.self_employment_income,
            "investment_income": self.investment_income,
            "total_income": self.calculate_total_income()
        }

@dataclass
class OntarioChild:
    """Child information for family law proceedings"""
    name: OntarioName = field(default_factory=OntarioName)
    birthdate: Optional[date] = None
    age: Optional[int] = None
    lives_with: str = ""  # applicant, respondent, other
    
    # Support and custody
    child_support_amount: float = 0.0
    custody_arrangement: str = ""  # sole, joint, shared
    access_arrangement: str = ""
    
    # Special circumstances
    special_needs: bool = False
    special_needs_description: str = ""
    over_18_in_school: bool = False
    
    def calculate_age(self) -> Optional[int]:
        """Calculate age from birthdate"""
        if not self.birthdate:
            return self.age
        today = date.today()
        age = today.year - self.birthdate.year
        if today.month < self.birthdate.month or (today.month == self.birthdate.month and today.day < self.birthdate.day):
            age -= 1
        return age
    
    def is_child_of_marriage(self) -> bool:
        """Check if child qualifies as child of marriage"""
        age = self.calculate_age() or self.age
        if not age:
            return True  # Assume yes if age unknown
        return age < 18 or (age >= 18 and self.over_18_in_school)
    
    def to_docassemble_object(self) -> Dict[str, Any]:
        """Generate child object for Docassemble"""
        return {
            "Individual": {
                "name.first": self.name.first,
                "name.middle": self.name.middle,
                "name.last": self.name.last,
                "birthdate": self.birthdate.isoformat() if self.birthdate else None,
                "age": self.calculate_age() or self.age,
                "lives_with": self.lives_with,
                "is_child_of_marriage": self.is_child_of_marriage()
            }
        }

@dataclass
class OntarioParty:
    """Party (applicant, respondent) in Ontario family law proceeding"""
    name: OntarioName = field(default_factory=OntarioName)
    address: OntarioAddress = field(default_factory=OntarioAddress)
    
    # Contact information
    phone_number: str = ""
    fax_number: str = ""
    email: str = ""
    
    # Personal information
    birthdate: Optional[date] = None
    sin_number: str = ""
    
    # Legal representation
    has_lawyer: bool = False
    lawyer: Optional[OntarioLawyer] = None
    
    # Financial information
    financial_info: OntarioFinancialInfo = field(default_factory=OntarioFinancialInfo)
    
    # Marriage/relationship information
    gender_at_marriage: str = ""
    name_at_marriage: OntarioName = field(default_factory=OntarioName)
    
    def age(self) -> Optional[int]:
        """Calculate current age"""
        if not self.birthdate:
            return None
        today = date.today()
        age = today.year - self.birthdate.year
        if today.month < self.birthdate.month or (today.month == self.birthdate.month and today.day < self.birthdate.day):
            age -= 1
        return age
    
    def to_docassemble_objects(self, party_type: str = "applicant") -> Dict[str, Any]:
        """Generate Docassemble objects for this party"""
        objects = {}
        
        # Main party object
        objects[f"Individual:{party_type}"] = {
            "name.first": self.name.first,
            "name.middle": self.name.middle, 
            "name.last": self.name.last,
            "address.address": self.address.street,
            "address.city": self.address.city,
            "address.state": self.address.province,
            "address.zip": self.address.postal_code,
            "phone_number": self.phone_number,
            "email": self.email,
            "birthdate": self.birthdate.isoformat() if self.birthdate else None
        }
        
        # Lawyer object if applicable
        if self.has_lawyer and self.lawyer:
            objects[f"Individual:{party_type}_lawyer"] = self.lawyer.to_docassemble_object()["Individual"]
            
        return objects

class OntarioPartyGenerator:
    """Generates party-related YAML objects for Ontario family law forms"""
    
    def __init__(self):
        self.standard_objects = self._initialize_standard_objects()
        self.standard_questions = self._initialize_standard_questions()
    
    def _initialize_standard_objects(self) -> Dict[str, Any]:
        """Initialize standard party objects for Ontario forms"""
        return {
            "party_objects": [
                {"Individual": "applicant"},
                {"Individual": "respondent"}, 
                {"DAList": "children"},
                {"Individual": "applicant_lawyer"},
                {"Individual": "respondent_lawyer"}
            ],
            "case_objects": [
                {"Thing": "case"},
                {"Thing": "marriage"},
                {"Thing": "separation"}
            ],
            "financial_objects": [
                {"Thing": "applicant_financial"},
                {"Thing": "respondent_financial"}
            ]
        }
    
    def _initialize_standard_questions(self) -> Dict[str, Any]:
        """Initialize standard party questions"""
        return {
            "applicant_name": {
                "question": "What is your full legal name?",
                "subquestion": "Enter your name exactly as it appears on official documents",
                "fields": [
                    {"First name": "applicant.name.first"},
                    {"Middle name": "applicant.name.middle", "required": False},
                    {"Last name": "applicant.name.last"}
                ],
                "validation code": """
if not applicant.name.first or not applicant.name.last:
  validation_error("First and last names are required")
if len(applicant.name.full()) < 2:
  validation_error("Please enter a valid name")
"""
            },
            
            "respondent_name": {
                "question": "What is the respondent's full legal name?", 
                "subquestion": "Enter the respondent's name exactly as it appears on official documents",
                "fields": [
                    {"First name": "respondent.name.first"},
                    {"Middle name": "respondent.name.middle", "required": False},
                    {"Last name": "respondent.name.last"}
                ],
                "validation code": """
if not respondent.name.first or not respondent.name.last:
  validation_error("Respondent's first and last names are required")
"""
            },
            
            "applicant_address": {
                "question": "What is your address?",
                "subquestion": "Provide your current mailing address",
                "fields": [
                    {"Street address": "applicant.address.address"},
                    {"City": "applicant.address.city"},
                    {"Province": "applicant.address.state", "default": "Ontario"},
                    {"Postal code": "applicant.address.zip"}
                ],
                "validation code": """
if not applicant.address.address or not applicant.address.city:
  validation_error("Street address and city are required")
if applicant.address.zip and not validate_ontario_postal_code(applicant.address.zip):
  validation_error("Please enter a valid Ontario postal code")
"""
            },
            
            "applicant_contact": {
                "question": "What are your contact details?",
                "fields": [
                    {"Phone number": "applicant.phone_number"},
                    {"Email address": "applicant.email", "datatype": "email", "required": False}
                ],
                "validation code": """
if applicant.phone_number and not validate_canadian_phone(applicant.phone_number):
  validation_error("Please enter a valid Canadian phone number")
"""
            },
            
            "applicant_birthdate": {
                "question": "What is your date of birth?",
                "fields": [
                    {"Date of birth": "applicant.birthdate", "datatype": "date"}
                ],
                "validation code": """
if applicant.birthdate > today():
  validation_error("Birth date cannot be in the future")
if applicant.age_in_years() < 18:
  validation_error("You must be at least 18 years old to file this application")
"""
            },
            
            "applicant_lawyer": {
                "question": "Do you have a lawyer?",
                "yesno": "applicant.has_lawyer",
                "fields": [
                    {"I have a lawyer": "applicant.has_lawyer", "datatype": "yesnoradio"}
                ]
            },
            
            "applicant_lawyer_details": {
                "question": "What are your lawyer's details?",
                "subquestion": "Provide your lawyer's contact information",
                "show if": "applicant.has_lawyer",
                "fields": [
                    {"Lawyer's first name": "applicant.lawyer.name.first"},
                    {"Lawyer's last name": "applicant.lawyer.name.last"},
                    {"Law firm name": "applicant.lawyer.firm_name", "required": False},
                    {"Lawyer's phone": "applicant.lawyer.phone_number"},
                    {"Lawyer's email": "applicant.lawyer.email", "datatype": "email", "required": False}
                ]
            },
            
            "marriage_information": {
                "question": "Marriage Information",
                "subquestion": "Provide details about your marriage",
                "fields": [
                    {"Date of marriage": "marriage.marriage_date", "datatype": "date"},
                    {"Place of marriage": "marriage.place_of_marriage"}
                ],
                "validation code": """
if marriage.marriage_date > today():
  validation_error("Marriage date cannot be in the future")
"""
            },
            
            "separation_information": {
                "question": "Separation Information",
                "subquestion": "If you are separated, provide the date of separation",
                "fields": [
                    {"Date of separation": "separation.date_of_separation", "datatype": "date", "required": False}
                ],
                "validation code": """
if separation.date_of_separation:
  if separation.date_of_separation > today():
    validation_error("Separation date cannot be in the future")
  if separation.date_of_separation < marriage.marriage_date:
    validation_error("Separation date cannot be before marriage date")
"""
            }
        }
    
    def generate_party_objects(self, parties: List[str] = None) -> List[Dict[str, str]]:
        """Generate objects section for parties"""
        if parties is None:
            parties = ["applicant", "respondent"]
            
        objects = []
        for party in parties:
            objects.extend([
                {"Individual": party},
                {"Individual": f"{party}_lawyer"}
            ])
        
        # Add children objects if needed
        objects.append({"DAList": "children"})
        
        # Add case-related objects
        objects.extend([
            {"Thing": "case"},
            {"Thing": "marriage"},
            {"Thing": "separation"}
        ])
        
        return objects
    
    def generate_party_questions(self, party_type: str = "applicant") -> List[Dict[str, Any]]:
        """Generate question blocks for a party"""
        questions = []
        
        # Name questions
        name_question = self.standard_questions["applicant_name"].copy()
        if party_type == "respondent":
            name_question = self.standard_questions["respondent_name"].copy()
        questions.append(name_question)
        
        # Address question
        address_question = self.standard_questions["applicant_address"].copy()
        if party_type == "respondent":
            address_question["question"] = "What is the respondent's address?"
            address_question["subquestion"] = "Provide the respondent's current mailing address"
            # Update field variables
            for field in address_question["fields"]:
                for key, var in field.items():
                    if isinstance(var, str) and "applicant" in var:
                        field[key] = var.replace("applicant", "respondent")
        questions.append(address_question)
        
        # Contact question
        contact_question = self.standard_questions["applicant_contact"].copy()
        if party_type == "respondent":
            contact_question["question"] = "What are the respondent's contact details?"
            # Update field variables
            for field in contact_question["fields"]:
                for key, var in field.items():
                    if isinstance(var, str) and "applicant" in var:
                        field[key] = var.replace("applicant", "respondent")
        questions.append(contact_question)
        
        # Birthdate question
        birthdate_question = self.standard_questions["applicant_birthdate"].copy()
        if party_type == "respondent":
            birthdate_question["question"] = "What is the respondent's date of birth?"
            # Update field variables
            for field in birthdate_question["fields"]:
                for key, var in field.items():
                    if isinstance(var, str) and "applicant" in var:
                        field[key] = var.replace("applicant", "respondent")
        questions.append(birthdate_question)
        
        # Lawyer questions (only for applicant typically)
        if party_type == "applicant":
            questions.append(self.standard_questions["applicant_lawyer"])
            questions.append(self.standard_questions["applicant_lawyer_details"])
        
        return questions
    
    def generate_marriage_questions(self) -> List[Dict[str, Any]]:
        """Generate marriage-related questions"""
        return [
            self.standard_questions["marriage_information"],
            self.standard_questions["separation_information"]
        ]
    
    def generate_complete_party_interview(self, 
                                        form_number: str,
                                        include_respondent: bool = True,
                                        include_marriage: bool = True,
                                        include_children: bool = True) -> Dict[str, Any]:
        """Generate complete party interview structure"""
        
        interview = {
            "metadata": {
                "title": f"Ontario Form {form_number} - Party Information",
                "short title": f"Form {form_number} Parties"
            },
            "objects": self.generate_party_objects(),
            "mandatory": True,
            "code": "party_info_complete"
        }
        
        # Generate all question blocks
        questions = []
        
        # Applicant questions
        questions.extend(self.generate_party_questions("applicant"))
        
        # Respondent questions if needed
        if include_respondent:
            questions.extend(self.generate_party_questions("respondent"))
        
        # Marriage questions if needed
        if include_marriage:
            questions.extend(self.generate_marriage_questions())
        
        # Children questions if needed
        if include_children:
            questions.extend(self._generate_children_questions())
        
        # Set completion code
        questions.append({
            "code": "party_info_complete = True",
            "comment": "Mark party information as complete"
        })
        
        # Add questions to interview structure
        interview["questions"] = questions
        
        return interview
    
    def _generate_children_questions(self) -> List[Dict[str, Any]]:
        """Generate children-related questions"""
        return [
            {
                "question": "Are there any children of the relationship?",
                "subquestion": "Include all children born to or adopted by you and the other party during your relationship",
                "yesno": "children.there_are_any"
            },
            {
                "question": "How many children are there?",
                "show if": "children.there_are_any",
                "fields": [
                    {"Number of children": "children.target_number", "datatype": "integer"}
                ],
                "validation code": """
if children.target_number < 1 or children.target_number > 20:
  validation_error("Please enter a reasonable number of children (1-20)")
"""
            },
            {
                "question": "Tell me about ${ordinal(i)} child.",
                "show if": "children.there_are_any", 
                "fields": [
                    {"First name": "children[i].name.first"},
                    {"Last name": "children[i].name.last"},
                    {"Date of birth": "children[i].birthdate", "datatype": "date"},
                    {"Lives primarily with": "children[i].lives_with", "datatype": "radio",
                     "choices": [
                         {"applicant": "Me (applicant)"},
                         {"respondent": "The other party (respondent)"},
                         {"both": "Both parties equally"},
                         {"other": "Someone else"}
                     ]}
                ]
            }
        ]

# Global instance for easy import
ontario_party_generator = OntarioPartyGenerator()