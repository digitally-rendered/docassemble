#!/usr/bin/env python3
"""
Ontario Children Objects - Children and family structure for Ontario family law
Programmatically generates YAML objects for children-related information
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
import calendar

@dataclass
class OntarioChildSupport:
    """Child support calculation information"""
    payor_income: float = 0.0
    recipient_income: float = 0.0
    
    # Support amounts
    table_amount: float = 0.0  # Basic table amount
    special_expenses: float = 0.0  # Section 7 expenses
    total_support: float = 0.0
    
    # Support details
    payment_frequency: str = "monthly"  # monthly, weekly, etc.
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    # Special circumstances
    shared_custody: bool = False
    split_custody: bool = False
    undue_hardship: bool = False
    
    def calculate_annual_support(self) -> float:
        """Calculate annual support amount"""
        if self.payment_frequency == "monthly":
            return self.total_support * 12
        elif self.payment_frequency == "weekly":
            return self.total_support * 52
        elif self.payment_frequency == "bi-weekly":
            return self.total_support * 26
        else:
            return self.total_support

@dataclass
class OntarioCustodyArrangement:
    """Custody and access arrangement"""
    decision_making: str = ""  # sole_applicant, sole_respondent, joint
    primary_residence: str = ""  # applicant, respondent, shared
    
    # Parenting time schedule
    regular_schedule: str = ""
    holiday_schedule: str = ""
    summer_schedule: str = ""
    
    # Communication and transportation
    communication_method: str = ""  # phone, video, in_person
    transportation_responsibility: str = ""  # applicant, respondent, shared
    
    # Special considerations
    supervised_access: bool = False
    no_contact: bool = False
    restraining_order: bool = False

@dataclass
class OntarioChild:
    """Child in Ontario family law proceeding"""
    # Basic information
    first_name: str = ""
    middle_name: str = ""
    last_name: str = ""
    birthdate: Optional[date] = None
    
    # Legal status
    is_child_of_marriage: bool = True
    adopted: bool = False
    stepchild: bool = False
    
    # Current living situation
    lives_with: str = ""  # applicant, respondent, other
    school_name: str = ""
    school_address: str = ""
    
    # Support information
    support_info: OntarioChildSupport = field(default_factory=OntarioChildSupport)
    
    # Custody information  
    custody_arrangement: OntarioCustodyArrangement = field(default_factory=OntarioCustodyArrangement)
    
    # Special needs and circumstances
    has_special_needs: bool = False
    special_needs_description: str = ""
    medical_conditions: List[str] = field(default_factory=list)
    
    # Education and support after 18
    in_full_time_education: bool = False
    education_details: str = ""
    over_18_needs_support: bool = False
    
    def age(self) -> Optional[int]:
        """Calculate current age"""
        if not self.birthdate:
            return None
        today = date.today()
        age = today.year - self.birthdate.year
        if today.month < self.birthdate.month or (today.month == self.birthdate.month and today.day < self.birthdate.day):
            age -= 1
        return age
    
    def full_name(self) -> str:
        """Generate full name"""
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return " ".join(parts)
    
    def is_minor(self) -> bool:
        """Check if child is under 18"""
        child_age = self.age()
        return child_age is not None and child_age < 18
    
    def eligible_for_support(self) -> bool:
        """Check if child is eligible for support"""
        child_age = self.age()
        if child_age is None:
            return True  # Assume eligible if age unknown
        
        if child_age < 18:
            return True
        
        # Over 18 - check if in school or has special needs
        if child_age >= 18 and (self.in_full_time_education or self.over_18_needs_support or self.has_special_needs):
            return True
            
        return False
    
    def to_docassemble_object(self) -> Dict[str, Any]:
        """Generate Docassemble object for child"""
        return {
            "Individual": {
                "name.first": self.first_name,
                "name.middle": self.middle_name,
                "name.last": self.last_name,
                "birthdate": self.birthdate.isoformat() if self.birthdate else None,
                "age": self.age(),
                "lives_with": self.lives_with,
                "is_child_of_marriage": self.is_child_of_marriage,
                "eligible_for_support": self.eligible_for_support(),
                "has_special_needs": self.has_special_needs
            }
        }

class OntarioChildrenGenerator:
    """Generates children-related YAML objects for Ontario family law forms"""
    
    def __init__(self):
        self.children_questions = self._initialize_children_questions()
        self.custody_questions = self._initialize_custody_questions()
        self.support_questions = self._initialize_support_questions()
    
    def _initialize_children_questions(self) -> Dict[str, Any]:
        """Initialize children-related questions"""
        return {
            "has_children": {
                "question": "Are there any children of the relationship?",
                "subquestion": """
Include any children who are:
- Born to you and the other party during your relationship
- Adopted by both of you during your relationship  
- Children you have both acted as parents to during your relationship
""",
                "yesno": "children.there_are_any"
            },
            
            "children_count": {
                "question": "How many children are there?",
                "show if": "children.there_are_any",
                "fields": [
                    {"Number of children": "children.target_number", "datatype": "integer"}
                ],
                "validation code": """
if children.target_number < 1:
  validation_error("Please enter at least 1 child")
if children.target_number > 20:
  validation_error("Please enter a reasonable number of children (maximum 20)")
"""
            },
            
            "child_details": {
                "question": "Tell me about ${ordinal(i)} child.",
                "show if": "children.there_are_any",
                "fields": [
                    {"First name": "children[i].name.first"},
                    {"Middle name (if any)": "children[i].name.middle", "required": False},
                    {"Last name": "children[i].name.last"},
                    {"Date of birth": "children[i].birthdate", "datatype": "date"}
                ],
                "validation code": """
if not children[i].name.first or not children[i].name.last:
  validation_error("First and last name are required for each child")
if children[i].birthdate > today():
  validation_error("Birth date cannot be in the future")
"""
            },
            
            "child_living_arrangements": {
                "question": "Where does ${children[i].name.first} live?",
                "show if": "children.there_are_any",
                "fields": [
                    {"${children[i].name.first} lives primarily with": "children[i].lives_with", 
                     "datatype": "radio",
                     "choices": [
                         {"applicant": "Me (the applicant)"},
                         {"respondent": "The other party (the respondent)"},
                         {"shared": "Both parties (shared residence)"},
                         {"other": "Someone else (please specify below)"}
                     ]},
                    {"If someone else, who?": "children[i].other_guardian", "required": False,
                     "show if": "children[i].lives_with == 'other'"}
                ]
            },
            
            "child_relationship_status": {
                "question": "What is ${children[i].name.first}'s relationship to you and the other party?",
                "show if": "children.there_are_any",
                "fields": [
                    {"Relationship": "children[i].relationship_type",
                     "datatype": "radio", 
                     "choices": [
                         {"biological": "Biological child of both parties"},
                         {"adopted_both": "Adopted by both parties"},
                         {"adopted_applicant": "Adopted by me only"},
                         {"adopted_respondent": "Adopted by the other party only"},
                         {"stepchild_applicant": "My biological/adopted child, stepchild to other party"},
                         {"stepchild_respondent": "Other party's biological/adopted child, my stepchild"},
                         {"other": "Other relationship (please specify)"}
                     ]},
                    {"Please specify": "children[i].relationship_details", "required": False,
                     "show if": "children[i].relationship_type == 'other'"}
                ]
            },
            
            "child_special_circumstances": {
                "question": "Does ${children[i].name.first} have any special circumstances?",
                "show if": "children.there_are_any",
                "fields": [
                    {"Special needs or disabilities": "children[i].has_special_needs", "datatype": "yesnoradio"},
                    {"Description of special needs": "children[i].special_needs_description", 
                     "required": False, "show if": "children[i].has_special_needs"},
                    {"Currently in full-time education (if over 18)": "children[i].in_education", 
                     "datatype": "yesnoradio", "required": False},
                    {"School/program details": "children[i].education_details",
                     "required": False, "show if": "children[i].in_education"}
                ]
            }
        }
    
    def _initialize_custody_questions(self) -> Dict[str, Any]:
        """Initialize custody and access questions"""
        return {
            "seeking_custody": {
                "question": "Are you asking for orders about decision-making responsibility and parenting time?",
                "subquestion": """
Decision-making responsibility means making important decisions about the children's:
- Healthcare
- Education  
- Religious upbringing
- Extracurricular activities

Parenting time means the time each parent spends with the children.
""",
                "yesno": "seeking_custody_orders"
            },
            
            "decision_making": {
                "question": "What decision-making responsibility are you asking for?",
                "show if": "seeking_custody_orders",
                "fields": [
                    {"Decision-making responsibility": "custody.decision_making",
                     "datatype": "radio",
                     "choices": [
                         {"sole_applicant": "Sole decision-making responsibility to me"},
                         {"sole_respondent": "Sole decision-making responsibility to the other party"},  
                         {"joint": "Joint decision-making responsibility (both parties decide together)"},
                         {"divided": "Divided decision-making (different areas to different parties)"}
                     ]}
                ],
                "help": """
**Sole:** One parent makes all major decisions
**Joint:** Both parents must agree on major decisions  
**Divided:** Each parent makes decisions about specific areas (e.g., one decides education, other decides healthcare)
"""
            },
            
            "primary_residence": {
                "question": "Where should the children primarily live?",
                "show if": "seeking_custody_orders", 
                "fields": [
                    {"Primary residence": "custody.primary_residence",
                     "datatype": "radio",
                     "choices": [
                         {"applicant": "With me (the applicant)"},
                         {"respondent": "With the other party (the respondent)"},
                         {"shared": "Shared residence (children spend equal or nearly equal time with both)"}
                     ]}
                ]
            },
            
            "parenting_schedule": {
                "question": "What parenting time schedule are you proposing?",
                "show if": "seeking_custody_orders",
                "fields": [
                    {"Regular weekly schedule": "custody.weekly_schedule", "input type": "area"},
                    {"Holiday and special occasion schedule": "custody.holiday_schedule", 
                     "input type": "area", "required": False},
                    {"Summer vacation schedule": "custody.summer_schedule",
                     "input type": "area", "required": False}
                ],
                "help": """
Describe the schedule in detail. For example:
- "Children with applicant every Wednesday after school until Thursday morning, and alternate weekends from Friday 6pm to Sunday 6pm"
- "Christmas alternates each year, Easter with applicant in odd years, Thanksgiving with respondent"
"""
            },
            
            "special_conditions": {
                "question": "Are there any special conditions needed for the children's safety and wellbeing?",
                "show if": "seeking_custody_orders",
                "fields": [
                    {"Supervised access required": "custody.supervised_access", "datatype": "yesnoradio"},
                    {"No contact with other party": "custody.no_contact", "datatype": "yesnoradio"},
                    {"Restraining order needed": "custody.restraining_order", "datatype": "yesnoradio"},
                    {"Other special conditions": "custody.other_conditions", 
                     "input type": "area", "required": False}
                ]
            }
        }
    
    def _initialize_support_questions(self) -> Dict[str, Any]:
        """Initialize child support questions"""
        return {
            "seeking_child_support": {
                "question": "Are you asking for child support?",
                "subquestion": """
Child support is money paid by one parent to the other to help cover the costs of raising the children.

The amount is usually based on:
- The paying parent's income
- The number of children  
- Which province/territory the paying parent lives in
- Special expenses (like daycare, medical costs, activities)
""",
                "yesno": "seeking_child_support"
            },
            
            "support_payor": {
                "question": "Who should pay child support?",
                "show if": "seeking_child_support",
                "fields": [
                    {"Child support should be paid by": "child_support.payor",
                     "datatype": "radio", 
                     "choices": [
                         {"respondent": "The other party (respondent) should pay me"},
                         {"applicant": "I should pay the other party"},
                         {"both": "We should both pay (if children live with different parents)"}
                     ]}
                ]
            },
            
            "payor_income": {
                "question": "What is the income of the person who will pay support?",
                "show if": "seeking_child_support",
                "fields": [
                    {"Annual gross income": "child_support.payor_annual_income", "datatype": "currency"},
                    {"Source of income information": "child_support.income_source",
                     "datatype": "radio",
                     "choices": [
                         {"tax_return": "Most recent tax return/Notice of Assessment"},
                         {"pay_stubs": "Recent pay stubs"},
                         {"employment_letter": "Letter from employer"},
                         {"estimated": "Estimated (no documents available)"},
                         {"other": "Other source"}
                     ]}
                ],
                "validation code": """
if child_support.payor_annual_income <= 0:
  validation_error("Please enter a valid income amount")
if child_support.payor_annual_income > 1000000:
  validation_error("Please verify this income amount is correct")
"""
            },
            
            "special_expenses": {
                "question": "Are there any special or extraordinary expenses for the children?",
                "show if": "seeking_child_support",
                "subquestion": """
Special expenses (also called "Section 7 expenses") can include:
- Childcare costs
- Medical/dental expenses not covered by insurance
- Education costs (private school, tutoring, etc.)
- Extracurricular activities  
- Post-secondary education costs
""",
                "yesno": "child_support.has_special_expenses"
            },
            
            "special_expenses_details": {
                "question": "What are the special expenses?",
                "show if": "child_support.has_special_expenses", 
                "fields": [
                    {"Childcare costs": "child_support.childcare_costs", 
                     "datatype": "currency", "required": False},
                    {"Medical/dental costs": "child_support.medical_costs",
                     "datatype": "currency", "required": False},
                    {"Education costs": "child_support.education_costs",
                     "datatype": "currency", "required": False},
                    {"Extracurricular activities": "child_support.activity_costs", 
                     "datatype": "currency", "required": False},
                    {"Other expenses": "child_support.other_expenses",
                     "datatype": "currency", "required": False},
                    {"Description of expenses": "child_support.expense_description",
                     "input type": "area", "required": False}
                ]
            },
            
            "support_start_date": {
                "question": "When should child support start?", 
                "show if": "seeking_child_support",
                "fields": [
                    {"Support should start on": "child_support.start_date", "datatype": "date"}
                ],
                "validation code": """
if child_support.start_date > today() + timedelta(days=365):
  validation_error("Support start date seems too far in the future")
"""
            }
        }
    
    def generate_children_objects(self) -> List[Dict[str, str]]:
        """Generate children-related objects"""
        return [
            {"DAList": "children"},
            {"Thing": "custody"},
            {"Thing": "child_support"},
            {"DAList": "special_expenses"}
        ]
    
    def generate_children_questions(self,
                                  include_custody: bool = True,
                                  include_support: bool = True) -> List[Dict[str, Any]]:
        """Generate children-related questions"""
        questions = []
        
        # Basic children information
        questions.append(self.children_questions["has_children"])
        questions.append(self.children_questions["children_count"])
        questions.append(self.children_questions["child_details"])
        questions.append(self.children_questions["child_living_arrangements"])
        questions.append(self.children_questions["child_relationship_status"])
        questions.append(self.children_questions["child_special_circumstances"])
        
        # Custody questions if requested
        if include_custody:
            questions.extend([
                self.custody_questions["seeking_custody"],
                self.custody_questions["decision_making"],
                self.custody_questions["primary_residence"],
                self.custody_questions["parenting_schedule"],
                self.custody_questions["special_conditions"]
            ])
        
        # Support questions if requested  
        if include_support:
            questions.extend([
                self.support_questions["seeking_child_support"],
                self.support_questions["support_payor"],
                self.support_questions["payor_income"],
                self.support_questions["special_expenses"],
                self.support_questions["special_expenses_details"],
                self.support_questions["support_start_date"]
            ])
        
        return questions
    
    def generate_children_summary_block(self) -> Dict[str, Any]:
        """Generate children information summary"""
        return {
            "question": "Children Summary",
            "subquestion": """
% if children.there_are_any:
**Number of children:** ${children.target_number}

% for child in children:
**Child ${loop.index}:** ${child.name.full()}, born ${child.birthdate.format()}, age ${child.age_in_years()}
- Lives with: ${child.lives_with}
% if child.has_special_needs:
- Special needs: ${child.special_needs_description}
% endif
% if child.in_education and child.age_in_years() >= 18:
- In education: ${child.education_details}
% endif

% endfor

% if seeking_custody_orders:
**Custody Arrangement Requested:**
- Decision-making: ${custody.decision_making}
- Primary residence: ${custody.primary_residence}
% endif

% if seeking_child_support:
**Child Support Requested:**
- Payor: ${child_support.payor}
- Annual income: ${currency(child_support.payor_annual_income)}
- Start date: ${child_support.start_date.format()}
% if child_support.has_special_expenses:
- Special expenses: Yes
% endif
% endif

% else:
**No children of the relationship**
% endif
""",
            "continue button field": "children_summary_reviewed"
        }
    
    def generate_children_validation_code(self) -> str:
        """Generate children-related validation functions"""
        return """
def calculate_child_support_table_amount(annual_income, num_children, province="ON"):
    '''
    Estimate child support based on Federal Child Support Guidelines
    This is a simplified calculation - actual amounts should be verified
    '''
    # Ontario table amounts for 2024 (approximate)
    if province.upper() == "ON":
        table_data = {
            1: {20000: 167, 30000: 286, 40000: 365, 50000: 444, 60000: 523, 70000: 602, 80000: 681, 90000: 760, 100000: 839},
            2: {20000: 274, 30000: 469, 40000: 599, 50000: 728, 60000: 858, 70000: 987, 80000: 1116, 90000: 1246, 100000: 1375},
            3: {20000: 343, 30000: 587, 40000: 750, 50000: 912, 60000: 1074, 70000: 1237, 80000: 1399, 90000: 1561, 100000: 1723}
        }
        
        if num_children > 3:
            # Add approximately $400 per additional child
            base = table_data.get(3, {}).get(annual_income, 0)
            return base + ((num_children - 3) * 400)
        
        child_table = table_data.get(num_children, {})
        
        # Find closest income bracket
        income_brackets = sorted(child_table.keys())
        for bracket in income_brackets:
            if annual_income <= bracket:
                return child_table[bracket]
        
        # If income is higher than table, extrapolate
        if annual_income > 100000:
            base_amount = child_table.get(100000, 0)
            excess_income = annual_income - 100000
            # Rough estimate: add percentage of excess
            additional = excess_income * 0.008 * num_children  # Approximately 0.8% per child
            return int(base_amount + additional)
    
    return 0

def validate_child_birthdate(birthdate):
    '''Validate child birthdate'''
    if not birthdate:
        return False
    
    today = date.today()
    
    # Cannot be in future
    if birthdate > today:
        return False
    
    # Cannot be more than 30 years ago (reasonable limit)
    if birthdate < today - timedelta(days=30*365):
        return False
    
    return True

def child_eligible_for_support(child):
    '''Check if child is eligible for support'''
    if not child.birthdate:
        return True  # Assume eligible if no birthdate
    
    age = child.age_in_years()
    
    # Under 18 - always eligible
    if age < 18:
        return True
    
    # 18 or over - eligible if in school or special needs
    if age >= 18:
        return child.in_education or child.has_special_needs or child.over_18_needs_support
    
    return False
"""
    
    def generate_complete_children_interview(self,
                                           form_number: str,
                                           include_custody: bool = True,
                                           include_support: bool = True) -> Dict[str, Any]:
        """Generate complete children interview structure"""
        
        interview = {
            "metadata": {
                "title": f"Ontario Form {form_number} - Children Information", 
                "short title": f"Form {form_number} Children"
            },
            "objects": self.generate_children_objects(),
            "mandatory": True,
            "code": "children_info_complete"
        }
        
        # Generate questions
        questions = self.generate_children_questions(
            include_custody=include_custody,
            include_support=include_support
        )
        
        # Add summary
        questions.append(self.generate_children_summary_block())
        
        # Set completion code
        questions.append({
            "code": "children_info_complete = True",
            "comment": "Mark children information as complete"
        })
        
        interview["questions"] = questions
        
        return interview
    
    def estimate_child_support(self, 
                             payor_income: float,
                             children_count: int,
                             special_expenses: float = 0.0) -> Dict[str, float]:
        """Estimate child support amounts"""
        # This is a simplified calculation
        # Real implementation should use official tables
        
        # Basic table amount (rough estimates for Ontario)
        if children_count == 1:
            if payor_income <= 30000:
                table_amount = payor_income * 0.17
            elif payor_income <= 50000:
                table_amount = payor_income * 0.20
            else:
                table_amount = payor_income * 0.22
        elif children_count == 2:
            table_amount = payor_income * 0.32
        else:
            table_amount = payor_income * 0.40
        
        # Monthly amount
        monthly_table = table_amount / 12
        monthly_special = special_expenses / 12
        monthly_total = monthly_table + monthly_special
        
        return {
            "annual_table": table_amount,
            "annual_special": special_expenses, 
            "annual_total": table_amount + special_expenses,
            "monthly_table": monthly_table,
            "monthly_special": monthly_special,
            "monthly_total": monthly_total
        }

# Global instance for easy import
ontario_children_generator = OntarioChildrenGenerator()