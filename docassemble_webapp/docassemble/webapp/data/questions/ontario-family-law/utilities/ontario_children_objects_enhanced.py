#!/usr/bin/env python3
"""
Ontario Children Objects Enhanced - Children information structures for family law forms
Based on analysis of 104 child info fields, 25 name fields, and 17 birth fields
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field as dataclass_field

@dataclass
class ChildObjectDefinition:
    """Defines a child object structure for Docassemble"""
    object_name: str
    object_type: str
    attributes: Dict[str, Any]
    methods: List[str] = dataclass_field(default_factory=list)
    forms_used: List[str] = dataclass_field(default_factory=list)

class OntarioChildrenObjects:
    """Children object definitions for Ontario family law forms"""
    
    def __init__(self):
        self.child_objects = self._initialize_child_objects()
        self.custody_objects = self._initialize_custody_objects()
        self.support_objects = self._initialize_support_objects()
    
    def _initialize_child_objects(self) -> Dict[str, ChildObjectDefinition]:
        """Initialize child object definitions"""
        return {
            "children": ChildObjectDefinition(
                object_name="children",
                object_type="DAList.using(object_type=Individual, there_are_any=False)",
                attributes={
                    'name.first': {'type': 'text', 'label': 'First name'},
                    'name.middle': {'type': 'text', 'label': 'Middle name(s)', 'required': False},
                    'name.last': {'type': 'text', 'label': 'Last name'},
                    'birthdate': {'type': 'date', 'label': 'Date of birth'},
                    'age': {'type': 'computed', 'formula': 'age_in_years()'},
                    'gender': {'type': 'radio', 'choices': ['Male', 'Female', 'Other']},
                    'relationship_to_applicant': {
                        'type': 'radio',
                        'label': 'Relationship to applicant',
                        'choices': [
                            'Biological child',
                            'Adopted child',
                            'Step-child',
                            'Child treated as own',
                            'Other'
                        ]
                    },
                    'relationship_to_respondent': {
                        'type': 'radio',
                        'label': 'Relationship to respondent',
                        'choices': [
                            'Biological child',
                            'Adopted child',
                            'Step-child',
                            'Child treated as own',
                            'Other'
                        ]
                    },
                    'residence': {
                        'type': 'radio',
                        'label': 'Child resides with',
                        'choices': [
                            'Applicant',
                            'Respondent',
                            'Shared (both parties)',
                            'Other person'
                        ]
                    },
                    'residence_address': {
                        'type': 'object',
                        'label': 'Address where child lives',
                        'show_if': "residence == 'Other person'"
                    },
                    'school': {'type': 'text', 'label': 'Name of school', 'required': False},
                    'grade': {'type': 'text', 'label': 'Grade/Year', 'required': False},
                    'special_needs': {'type': 'yesno', 'label': 'Has special needs'},
                    'special_needs_details': {
                        'type': 'area',
                        'label': 'Describe special needs',
                        'show_if': 'special_needs'
                    },
                    'health_card_number': {'type': 'text', 'label': 'Health card number', 'required': False},
                    'sin': {'type': 'text', 'label': 'Social Insurance Number', 'required': False},
                    'indigenous_status': {
                        'type': 'radio',
                        'label': 'Indigenous status',
                        'choices': ['First Nations', 'Métis', 'Inuit', 'Not Indigenous', 'Unknown'],
                        'required': False
                    },
                    'band_name': {
                        'type': 'text',
                        'label': 'Band/First Nation name',
                        'show_if': "indigenous_status in ['First Nations', 'Métis', 'Inuit']"
                    }
                },
                methods=['name.full()', 'age_in_years()', 'is_minor()'],
                forms_used=['8', '10', '13', '13A', '15', '17A', '25', '26', '28', '36']
            ),
            "child_of_marriage": ChildObjectDefinition(
                object_name="children_of_marriage",
                object_type="DAList.using(object_type=Individual)",
                attributes={
                    'name.full()': {'type': 'text', 'label': 'Full name'},
                    'birthdate': {'type': 'date', 'label': 'Date of birth'},
                    'is_child_of_marriage': {
                        'type': 'yesno',
                        'label': 'Is child of the marriage',
                        'help': 'Under 18 or unable to withdraw from parental charge'
                    },
                    'reason_dependent': {
                        'type': 'radio',
                        'label': 'Reason for dependency',
                        'choices': [
                            'Under age of majority',
                            'Enrolled in full-time education',
                            'Illness or disability',
                            'Other reason'
                        ],
                        'show_if': 'is_child_of_marriage and age_in_years() >= 18'
                    },
                    'education_details': {
                        'type': 'area',
                        'label': 'Education program details',
                        'show_if': "reason_dependent == 'Enrolled in full-time education'"
                    },
                    'disability_details': {
                        'type': 'area',
                        'label': 'Disability/illness details',
                        'show_if': "reason_dependent == 'Illness or disability'"
                    }
                },
                methods=['name.full()', 'age_in_years()', 'is_adult()'],
                forms_used=['Divorce and support forms']
            )
        }
    
    def _initialize_custody_objects(self) -> Dict[str, Any]:
        """Initialize custody and parenting arrangement objects"""
        return {
            "custody_arrangement": {
                'custody_type': {
                    'type': 'radio',
                    'label': 'Type of custody arrangement',
                    'choices': [
                        'Sole custody to applicant',
                        'Sole custody to respondent',
                        'Joint custody',
                        'Shared custody',
                        'Split custody',
                        'Other arrangement'
                    ]
                },
                'decision_making': {
                    'type': 'checkboxes',
                    'label': 'Decision-making responsibility',
                    'choices': [
                        'Education',
                        'Health care',
                        'Religion',
                        'Extracurricular activities',
                        'Other major decisions'
                    ]
                },
                'primary_residence': {
                    'type': 'radio',
                    'label': 'Primary residence',
                    'choices': ['Applicant', 'Respondent', 'Shared equally', 'Other']
                },
                'parenting_schedule': {
                    'type': 'area',
                    'label': 'Describe the parenting schedule',
                    'rows': 4
                },
                'holiday_schedule': {
                    'type': 'area',
                    'label': 'Holiday and special occasion schedule',
                    'rows': 3
                },
                'exchanges_location': {
                    'type': 'text',
                    'label': 'Location for exchanges'
                },
                'exchanges_time': {
                    'type': 'text',
                    'label': 'Time for exchanges'
                },
                'supervised_access': {
                    'type': 'yesno',
                    'label': 'Is supervised access required?'
                },
                'supervision_details': {
                    'type': 'area',
                    'label': 'Supervision arrangements',
                    'show_if': 'supervised_access'
                }
            }
        }
    
    def _initialize_support_objects(self) -> Dict[str, Any]:
        """Initialize child support calculation objects"""
        return {
            "child_support": {
                'payor': {
                    'type': 'radio',
                    'label': 'Who will pay child support?',
                    'choices': ['Applicant', 'Respondent', 'Both (set-off)']
                },
                'guideline_amount': {
                    'type': 'currency',
                    'label': 'Child Support Guidelines table amount'
                },
                'special_expenses': {
                    'type': 'yesno',
                    'label': 'Are there special or extraordinary expenses?'
                },
                'expense_categories': {
                    'type': 'checkboxes',
                    'label': 'Types of special expenses',
                    'choices': [
                        'Child care',
                        'Medical/dental insurance premiums',
                        'Health-related expenses',
                        'Primary/secondary school expenses',
                        'Post-secondary education',
                        'Extracurricular activities'
                    ],
                    'show_if': 'special_expenses'
                },
                'expense_amounts': {
                    'child_care': {'type': 'currency', 'label': 'Child care costs'},
                    'medical_insurance': {'type': 'currency', 'label': 'Medical/dental premiums'},
                    'health_expenses': {'type': 'currency', 'label': 'Uninsured health expenses'},
                    'education': {'type': 'currency', 'label': 'Education expenses'},
                    'activities': {'type': 'currency', 'label': 'Extracurricular activities'}
                },
                'start_date': {
                    'type': 'date',
                    'label': 'Child support start date'
                },
                'payment_frequency': {
                    'type': 'radio',
                    'label': 'Payment frequency',
                    'choices': ['Monthly', 'Bi-weekly', 'Weekly', 'Other']
                },
                'payment_method': {
                    'type': 'radio',
                    'label': 'Payment method',
                    'choices': [
                        'Family Responsibility Office (FRO)',
                        'Direct payment',
                        'Post-dated cheques',
                        'Electronic transfer'
                    ]
                }
            }
        }
    
    def generate_children_yaml(self) -> str:
        """Generate YAML for children objects"""
        yaml_lines = [
            "---",
            "# Ontario Family Law Children Objects",
            "# Auto-generated from children object definitions",
            "---",
            "objects:",
            "  - children: DAList.using(object_type=Individual, there_are_any=False)",
            "  - children_of_marriage: DAList.using(object_type=Individual, there_are_any=False)",
            "---",
            "# Children collection management",
            "code: |",
            "  children.there_are_any = has_children",
            "  if children.there_are_any:",
            "    children.target_number = children_count",
            "---",
            "# Child of marriage determination",
            "code: |",
            "  for child in children:",
            "    if child.age_in_years() < 18:",
            "      child.is_child_of_marriage = True",
            "    elif child.age_in_years() < 25 and child.in_school:",
            "      child.is_child_of_marriage = True",
            "    elif child.has_disability:",
            "      child.is_child_of_marriage = True",
            "    else:",
            "      child.is_child_of_marriage = False",
            "---"
        ]
        
        return "\n".join(yaml_lines)
    
    def generate_children_questions(self) -> List[Dict[str, Any]]:
        """Generate question blocks for children information"""
        questions = []
        
        # Initial children question
        questions.append({
            'id': 'has_children',
            'question': "Are there any children of the relationship?",
            'subquestion': "Include all biological, adopted, and step-children",
            'fields': [
                {"Children of the relationship": "children.there_are_any", "datatype": "yesnoradio"}
            ]
        })
        
        # Number of children
        questions.append({
            'id': 'children_count',
            'question': "How many children are there?",
            'show if': "children.there_are_any",
            'fields': [
                {"Number of children": "children.target_number", "datatype": "integer", "min": 1, "max": 20}
            ]
        })
        
        # Child details (table format)
        questions.append({
            'id': 'children_details',
            'question': "Information about the children",
            'show if': "children.there_are_any",
            'fields': [
                {
                    'label': "Child ${i+1}",
                    'field': "children[i].name.first",
                    'datatype': "text"
                },
                {
                    'label': "Last name",
                    'field': "children[i].name.last",
                    'datatype': "text"
                },
                {
                    'label': "Date of birth",
                    'field': "children[i].birthdate",
                    'datatype': "date"
                },
                {
                    'label': "Resides with",
                    'field': "children[i].residence",
                    'datatype': "radio",
                    'choices': ["Applicant", "Respondent", "Shared", "Other"]
                }
            ],
            'list collect': True
        })
        
        # Special needs
        questions.append({
            'id': 'children_special_needs',
            'question': "Do any children have special needs?",
            'show if': "children.there_are_any",
            'fields': [
                {
                    'label': f"Does {child.name.first} have special needs?",
                    'field': "children[i].special_needs",
                    'datatype': "yesno"
                } for child in "children"
            ]
        })
        
        # Custody arrangements
        questions.append({
            'id': 'custody_arrangement',
            'question': "What custody arrangement are you seeking?",
            'show if': "children.there_are_any",
            'fields': [
                {
                    'label': "Custody type",
                    'field': "custody.custody_type",
                    'datatype': "radio",
                    'choices': [
                        "Sole custody to applicant",
                        "Sole custody to respondent",
                        "Joint custody",
                        "Shared custody",
                        "Other"
                    ]
                }
            ]
        })
        
        # Child support
        questions.append({
            'id': 'child_support_needed',
            'question': "Is child support being requested?",
            'show if': "children.there_are_any",
            'fields': [
                {"Child support requested": "child_support.requested", "datatype": "yesnoradio"}
            ]
        })
        
        return questions
    
    def generate_child_table_yaml(self) -> str:
        """Generate YAML for child information table"""
        return """---
# Children information table
table: children.table
rows: children
columns:
  - Name: |
      row_item.name.full()
  - Date of Birth: |
      row_item.birthdate.format()
  - Age: |
      row_item.age_in_years()
  - Resides With: |
      row_item.residence
  - School: |
      row_item.school if hasattr(row_item, 'school') else ''
edit:
  - name.first
  - name.last
  - birthdate
  - residence
  - school
---
# Review screen for children
review:
  - label: Children Information
    button: |
      **Children of the Relationship**
      
      % if children.there_are_any:
      ${ children.table }
      
      ${ children.add_action() }
      % else:
      No children of the relationship.
      % endif
    fields:
      - children.revisit
---"""

# Global instance
ontario_children = OntarioChildrenObjects()