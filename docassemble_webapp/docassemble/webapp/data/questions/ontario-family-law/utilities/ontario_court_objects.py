#!/usr/bin/env python3
"""
Ontario Court Objects - Court and case information for Ontario family law proceedings
Programmatically generates YAML objects for court-related information
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, date
import re

@dataclass
class OntarioCourt:
    """Ontario court information"""
    court_name: str = ""
    court_address: str = ""
    court_city: str = ""
    court_postal_code: str = ""
    court_phone: str = ""
    
    # Court identifiers
    court_code: str = ""  # e.g., "SC" for Superior Court
    jurisdiction: str = "Ontario"
    
    def full_court_name(self) -> str:
        """Generate full court name"""
        if self.court_name:
            return self.court_name
        elif self.court_city:
            return f"Superior Court of Justice - {self.court_city}"
        else:
            return "Superior Court of Justice"
    
    def to_docassemble_object(self) -> Dict[str, Any]:
        """Generate court object"""
        return {
            "court_name": self.full_court_name(),
            "court_address": self.court_address,
            "court_city": self.court_city,
            "court_postal_code": self.court_postal_code,
            "court_phone": self.court_phone,
            "jurisdiction": self.jurisdiction
        }

@dataclass
class OntarioCase:
    """Ontario family law case information"""
    court_file_number: str = ""
    case_type: str = ""  # divorce, separation, custody, support, etc.
    
    # Case status
    filing_date: Optional[date] = None
    status: str = "not_filed"  # not_filed, filed, served, responded, etc.
    
    # Court information
    court: OntarioCourt = field(default_factory=OntarioCourt)
    
    # Case participants
    applicant_count: int = 1
    respondent_count: int = 1
    children_count: int = 0
    
    # Related cases
    related_cases: List[str] = field(default_factory=list)
    consolidated_with: str = ""
    
    def generate_case_number(self) -> str:
        """Generate temporary case number for unfiled cases"""
        if self.court_file_number:
            return self.court_file_number
        
        # Generate temporary number based on case type and date
        today = date.today()
        case_prefix = {
            "divorce": "FS",
            "separation": "FS", 
            "custody": "FC",
            "support": "FC",
            "property": "FC",
            "adoption": "FA",
            "enforcement": "FE"
        }.get(self.case_type, "FS")
        
        return f"{case_prefix}-{today.year % 100:02d}-XXXXX (to be assigned)"
    
    def to_docassemble_object(self) -> Dict[str, Any]:
        """Generate case object"""
        return {
            "court_file_number": self.court_file_number or self.generate_case_number(),
            "case_type": self.case_type,
            "filing_date": self.filing_date.isoformat() if self.filing_date else None,
            "status": self.status,
            "court": self.court.to_docassemble_object(),
            "applicant_count": self.applicant_count,
            "respondent_count": self.respondent_count,
            "children_count": self.children_count
        }

@dataclass
class OntarioOrder:
    """Court order information"""
    order_type: str = ""  # interim, final, consent, etc.
    order_date: Optional[date] = None
    order_number: str = ""
    
    # Order details
    support_amount: float = 0.0
    support_frequency: str = "monthly"  # monthly, weekly, etc.
    custody_arrangement: str = ""
    access_arrangement: str = ""
    
    # Order terms
    effective_date: Optional[date] = None
    review_date: Optional[date] = None
    
    def is_active(self) -> bool:
        """Check if order is currently active"""
        if not self.effective_date:
            return False
        today = date.today()
        if self.effective_date > today:
            return False
        if self.review_date and self.review_date < today:
            return False  # May be expired, needs review
        return True
    
    def to_docassemble_object(self) -> Dict[str, Any]:
        """Generate order object"""
        return {
            "order_type": self.order_type,
            "order_date": self.order_date.isoformat() if self.order_date else None,
            "order_number": self.order_number,
            "support_amount": self.support_amount,
            "support_frequency": self.support_frequency,
            "is_active": self.is_active()
        }

class OntarioCourtGenerator:
    """Generates court-related YAML objects for Ontario family law forms"""
    
    def __init__(self):
        self.ontario_courts = self._initialize_ontario_courts()
        self.court_questions = self._initialize_court_questions()
        self.case_types = self._initialize_case_types()
    
    def _initialize_ontario_courts(self) -> Dict[str, OntarioCourt]:
        """Initialize Ontario Superior Court locations"""
        courts = {}
        
        court_data = [
            {
                "key": "toronto",
                "name": "Superior Court of Justice - Toronto",
                "address": "393 University Avenue, 10th Floor",
                "city": "Toronto",
                "postal_code": "M5G 1E6",
                "phone": "(416) 327-5020"
            },
            {
                "key": "ottawa", 
                "name": "Superior Court of Justice - Ottawa",
                "address": "161 Elgin Street, 2nd Floor",
                "city": "Ottawa",
                "postal_code": "K2P 2K1", 
                "phone": "(613) 239-1506"
            },
            {
                "key": "london",
                "name": "Superior Court of Justice - London",
                "address": "80 Dundas Street, 3rd Floor",
                "city": "London",
                "postal_code": "N6A 6A3",
                "phone": "(519) 660-3090"
            },
            {
                "key": "hamilton",
                "name": "Superior Court of Justice - Hamilton", 
                "address": "45 Main Street East, 3rd Floor",
                "city": "Hamilton",
                "postal_code": "L8N 2B7",
                "phone": "(905) 645-5252"
            },
            {
                "key": "windsor",
                "name": "Superior Court of Justice - Windsor",
                "address": "245 Windsor Avenue, 2nd Floor",
                "city": "Windsor", 
                "postal_code": "N9A 1J2",
                "phone": "(519) 973-6500"
            },
            {
                "key": "thunder_bay",
                "name": "Superior Court of Justice - Thunder Bay",
                "address": "125 Brodie Street North",
                "city": "Thunder Bay",
                "postal_code": "P7C 0A3",
                "phone": "(807) 343-2710"
            },
            {
                "key": "kingston",
                "name": "Superior Court of Justice - Kingston", 
                "address": "26 Antares Drive",
                "city": "Kingston",
                "postal_code": "K7P 1R7",
                "phone": "(613) 548-6811"
            },
            {
                "key": "kitchener",
                "name": "Superior Court of Justice - Kitchener",
                "address": "85 Frederick Street, 2nd Floor",
                "city": "Kitchener",
                "postal_code": "N2H 0A7", 
                "phone": "(519) 741-3270"
            },
            {
                "key": "sudbury",
                "name": "Superior Court of Justice - Sudbury",
                "address": "155 Elm Street, 2nd Floor",
                "city": "Sudbury",
                "postal_code": "P3C 1T9",
                "phone": "(705) 564-7600"
            },
            {
                "key": "barrie",
                "name": "Superior Court of Justice - Barrie",
                "address": "75 Mulcaster Street, 2nd Floor", 
                "city": "Barrie",
                "postal_code": "L4M 6P2",
                "phone": "(705) 739-6151"
            }
        ]
        
        for court_info in court_data:
            courts[court_info["key"]] = OntarioCourt(
                court_name=court_info["name"],
                court_address=court_info["address"],
                court_city=court_info["city"],
                court_postal_code=court_info["postal_code"],
                court_phone=court_info["phone"]
            )
        
        return courts
    
    def _initialize_case_types(self) -> Dict[str, Dict[str, Any]]:
        """Initialize case type configurations"""
        return {
            "divorce": {
                "title": "Divorce Application",
                "description": "Application for divorce and related orders",
                "forms": ["8", "8A", "36"],
                "requires_financial": True,
                "has_children_section": True,
                "typical_orders": ["divorce", "custody", "support", "property"]
            },
            "separation": {
                "title": "Separation Application",
                "description": "Application for orders related to separation",
                "forms": ["8"],
                "requires_financial": True, 
                "has_children_section": True,
                "typical_orders": ["custody", "support", "property"]
            },
            "custody": {
                "title": "Custody Application",
                "description": "Application for decision-making responsibility and parenting time",
                "forms": ["8"],
                "requires_financial": False,
                "has_children_section": True,
                "typical_orders": ["custody", "access"]
            },
            "support": {
                "title": "Support Application",
                "description": "Application for child or spousal support",
                "forms": ["8"],
                "requires_financial": True,
                "has_children_section": True,
                "typical_orders": ["child_support", "spousal_support"]
            },
            "motion_to_change": {
                "title": "Motion to Change", 
                "description": "Motion to change an existing order",
                "forms": ["15"],
                "requires_financial": True,
                "has_children_section": True,
                "typical_orders": ["change_support", "change_custody"]
            },
            "enforcement": {
                "title": "Enforcement Application",
                "description": "Application to enforce an existing order",
                "forms": ["26", "27", "28", "29"],
                "requires_financial": False,
                "has_children_section": False,
                "typical_orders": ["garnishment", "seizure", "contempt"]
            }
        }
    
    def _initialize_court_questions(self) -> Dict[str, Any]:
        """Initialize court-related questions"""
        return {
            "court_location": {
                "question": "Where do you want to file this application?",
                "subquestion": """
Select the Ontario Superior Court location where you want to file your case. 
You should generally choose the court in the area where:
- You or the other party lives, or
- The events giving rise to the case happened, or  
- An existing case is already filed
""",
                "field": "case.court_location",
                "datatype": "radio",
                "choices": [
                    {"toronto": "Toronto - 393 University Avenue"},
                    {"ottawa": "Ottawa - 161 Elgin Street"}, 
                    {"london": "London - 80 Dundas Street"},
                    {"hamilton": "Hamilton - 45 Main Street East"},
                    {"windsor": "Windsor - 245 Windsor Avenue"},
                    {"thunder_bay": "Thunder Bay - 125 Brodie Street North"},
                    {"kingston": "Kingston - 26 Antares Drive"},
                    {"kitchener": "Kitchener - 85 Frederick Street"},
                    {"sudbury": "Sudbury - 155 Elm Street"},
                    {"barrie": "Barrie - 75 Mulcaster Street"},
                    {"other": "Other Ontario location"}
                ]
            },
            
            "court_file_number": {
                "question": "Do you have a court file number?",
                "subquestion": """
If this case has already been filed with the court, enter the court file number.
If you are filing a new case, leave this blank - a number will be assigned when you file.
                
Ontario court file numbers look like: FS-24-12345 or FC-24-67890
""",
                "fields": [
                    {"Court file number": "case.court_file_number", "required": False}
                ],
                "validation code": """
if case.court_file_number and not validate_ontario_court_file(case.court_file_number):
  validation_error("Please enter a valid Ontario court file number (e.g., FS-24-12345)")
"""
            },
            
            "case_type": {
                "question": "What type of case are you filing?",
                "subquestion": "Select the main type of order you are asking the court to make",
                "field": "case.case_type", 
                "datatype": "radio",
                "choices": [
                    {"divorce": "Divorce"},
                    {"separation": "Separation (without divorce)"},
                    {"custody": "Decision-making responsibility and parenting time"},
                    {"support": "Child or spousal support"},
                    {"property": "Property division"},
                    {"motion_to_change": "Change an existing order"},
                    {"enforcement": "Enforce an existing order"},
                    {"other": "Other"}
                ]
            },
            
            "related_cases": {
                "question": "Are there any related court cases?",
                "subquestion": """
List any other court cases involving you and the same parties, including:
- Previous applications in this court
- Cases in other Ontario courts  
- Cases in other provinces or countries
""",
                "yesno": "case.has_related_cases"
            },
            
            "related_case_details": {
                "question": "What are the details of the related cases?",
                "show if": "case.has_related_cases",
                "fields": [
                    {"Court file number of related case": "case.related_case_number"},
                    {"Court where related case was filed": "case.related_case_court"},
                    {"Status of related case": "case.related_case_status"}
                ]
            },
            
            "existing_orders": {
                "question": "Are there any existing court orders?",
                "subquestion": """
Tell us about any existing court orders between you and the other party, including:
- Support orders
- Custody/access orders  
- Property orders
- Restraining orders
""",
                "yesno": "case.has_existing_orders"
            }
        }
    
    def generate_court_objects(self) -> List[Dict[str, str]]:
        """Generate court-related objects"""
        return [
            {"Thing": "case"},
            {"Thing": "court"},
            {"DAList": "existing_orders"},
            {"DAList": "related_cases"}
        ]
    
    def generate_court_questions(self, 
                               include_file_number: bool = True,
                               include_related_cases: bool = True,
                               include_existing_orders: bool = True) -> List[Dict[str, Any]]:
        """Generate court-related questions"""
        questions = []
        
        # Always include court location and case type
        questions.append(self.court_questions["court_location"])
        questions.append(self.court_questions["case_type"])
        
        # Optionally include other questions
        if include_file_number:
            questions.append(self.court_questions["court_file_number"])
        
        if include_related_cases:
            questions.append(self.court_questions["related_cases"])
            questions.append(self.court_questions["related_case_details"])
            
        if include_existing_orders:
            questions.append(self.court_questions["existing_orders"])
        
        return questions
    
    def generate_court_validation_code(self) -> str:
        """Generate court validation functions"""
        return """
def validate_ontario_court_file(file_number):
    '''Validate Ontario court file number format'''
    if not file_number:
        return True  # Optional field
    
    # Remove spaces and convert to uppercase
    file_clean = re.sub(r'\\s+', '', file_number.upper())
    
    # Ontario court file patterns:
    # FS-YY-NNNNN (Family - Support/Divorce)
    # FC-YY-NNNNN (Family - Custody/Other)
    # FE-YY-NNNNN (Family - Enforcement)
    # FA-YY-NNNNN (Family - Adoption)
    patterns = [
        r'^(FS|FC|FE|FA)-[0-9]{2}-[0-9]{5}$',
        r'^[0-9]{2}-[0-9]{6}$'  # Older format
    ]
    
    for pattern in patterns:
        if re.match(pattern, file_clean):
            return True
    
    return False

def get_court_info(court_location):
    '''Get court information by location key'''
    court_data = {
        "toronto": {
            "name": "Superior Court of Justice - Toronto",
            "address": "393 University Avenue, 10th Floor\\nToronto, Ontario M5G 1E6",
            "phone": "(416) 327-5020"
        },
        "ottawa": {
            "name": "Superior Court of Justice - Ottawa", 
            "address": "161 Elgin Street, 2nd Floor\\nOttawa, Ontario K2P 2K1",
            "phone": "(613) 239-1506"
        },
        "london": {
            "name": "Superior Court of Justice - London",
            "address": "80 Dundas Street, 3rd Floor\\nLondon, Ontario N6A 6A3", 
            "phone": "(519) 660-3090"
        },
        "hamilton": {
            "name": "Superior Court of Justice - Hamilton",
            "address": "45 Main Street East, 3rd Floor\\nHamilton, Ontario L8N 2B7",
            "phone": "(905) 645-5252"
        },
        "windsor": {
            "name": "Superior Court of Justice - Windsor",
            "address": "245 Windsor Avenue, 2nd Floor\\nWindsor, Ontario N9A 1J2",
            "phone": "(519) 973-6500"
        },
        "thunder_bay": {
            "name": "Superior Court of Justice - Thunder Bay", 
            "address": "125 Brodie Street North\\nThunder Bay, Ontario P7C 0A3",
            "phone": "(807) 343-2710"
        }
    }
    
    return court_data.get(court_location, {
        "name": "Superior Court of Justice",
        "address": "Please contact the court for address information",
        "phone": "Please contact the court for phone information"
    })
"""
    
    def generate_case_summary_block(self) -> Dict[str, Any]:
        """Generate case summary review block"""
        return {
            "question": "Case Summary",
            "subquestion": """
Please review the case information:

**Court:** ${get_court_info(case.court_location)["name"]}

**Case Type:** ${case.case_type.title()}

% if case.court_file_number:
**Court File Number:** ${case.court_file_number}
% endif

% if case.has_related_cases:
**Related Cases:** Yes - ${case.related_case_number} in ${case.related_case_court}
% endif

% if case.has_existing_orders:
**Existing Orders:** Yes
% endif
""",
            "continue button field": "case_summary_reviewed"
        }
    
    def get_court_by_location(self, location: str) -> Optional[OntarioCourt]:
        """Get court object by location key"""
        return self.ontario_courts.get(location)
    
    def get_case_type_info(self, case_type: str) -> Optional[Dict[str, Any]]:
        """Get case type configuration"""
        return self.case_types.get(case_type)
    
    def generate_complete_court_interview(self, 
                                        form_number: str,
                                        include_all_options: bool = True) -> Dict[str, Any]:
        """Generate complete court information interview"""
        
        interview = {
            "metadata": {
                "title": f"Ontario Form {form_number} - Court Information",
                "short title": f"Form {form_number} Court Info"
            },
            "objects": self.generate_court_objects(),
            "mandatory": True,
            "code": "court_info_complete"
        }
        
        # Generate questions
        questions = self.generate_court_questions(
            include_file_number=include_all_options,
            include_related_cases=include_all_options,
            include_existing_orders=include_all_options
        )
        
        # Add case summary
        questions.append(self.generate_case_summary_block())
        
        # Set completion code
        questions.append({
            "code": "court_info_complete = True",
            "comment": "Mark court information as complete"
        })
        
        interview["questions"] = questions
        
        return interview

# Global instance for easy import
ontario_court_generator = OntarioCourtGenerator()