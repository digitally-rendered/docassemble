#!/usr/bin/env python3
"""
Refined Map Structure Generator
Builds proper map/list structures for Docassemble interviews
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import OrderedDict

class RefinedMapGenerator:
    """Generate interviews using refined map structures"""
    
    def __init__(self):
        self.output_dir = Path('../')  # Output to main ontario-family-law directory
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Load data
        self.parsed_fields = self._load_parsed_fields()
        self.domain_mappings = self._load_domain_mappings()
        
    def _load_parsed_fields(self) -> List[Dict]:
        """Load parsed fields"""
        path = Path('workflow_output/enhanced_parsed_forms/form_13_fields.json')
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        return []
    
    def _load_domain_mappings(self) -> Dict:
        """Load domain mappings"""
        path = Path('workflow_output/domain_mappings.json')
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        return {}
    
    def generate_refined_form_13(self):
        """Generate Form 13 with refined map structures"""
        
        # Build the interview structure as a proper map
        interview_map = OrderedDict()
        
        # 1. Build metadata map
        interview_map['metadata'] = self._build_metadata_map()
        
        # 2. Build configuration maps
        interview_map['config'] = self._build_config_maps()
        
        # 3. Build object maps
        interview_map['objects'] = self._build_object_maps()
        
        # 4. Build initialization map
        interview_map['initialization'] = self._build_initialization_map()
        
        # 5. Build question maps
        interview_map['questions'] = self._build_question_maps()
        
        # 6. Build logic maps
        interview_map['logic'] = self._build_logic_maps()
        
        # Convert to Docassemble YAML format
        yaml_content = self._convert_to_docassemble_yaml(interview_map)
        
        # Save the file
        output_file = self.output_dir / 'form_13_refined.yml'
        with open(output_file, 'w') as f:
            f.write(yaml_content)
        
        print(f"Generated: {output_file}")
        return True
    
    def _build_metadata_map(self) -> Dict:
        """Build metadata as a structured map"""
        return {
            'title': 'Form 13 - Financial Statement (Refined)',
            'short_title': 'Form 13',
            'description': 'Generated with refined map structures',
            'form_number': 13,
            'version': '1.0'
        }
    
    def _build_config_maps(self) -> Dict:
        """Build configuration maps"""
        return {
            'includes': ['docassemble.base:data/questions/basic-questions.yml'],
            'features': {
                'progress_bar': True,
                'question_back_button': True,
                'debug': False
            }
        }
    
    def _build_object_maps(self) -> Dict:
        """Build object maps from domain mappings"""
        objects = {}
        
        # Add person objects
        objects['applicant'] = {
            'type': 'Individual',
            'description': 'The person filling out the form'
        }
        
        # Add financial containers
        objects['income'] = {
            'type': 'DAObject',
            'attributes': {
                'employment': 0,
                'self_employment': 0,
                'ei_benefits': 0,
                'social_assistance': 0,
                'pension': 0,
                'investments': 0,
                'spousal_support': 0,
                'child_benefits': 0,
                'other': 0
            }
        }
        
        objects['expenses'] = {
            'type': 'DAObject',
            'attributes': {
                'housing': 0,
                'food': 0,
                'clothing': 0,
                'transportation': 0,
                'childcare': 0,
                'health': 0,
                'insurance': 0,
                'utilities': 0,
                'other': 0
            }
        }
        
        # Add lists for complex items
        objects['assets'] = {
            'type': 'DAList',
            'object_type': 'Thing',
            'description': 'List of assets'
        }
        
        objects['debts'] = {
            'type': 'DAList',
            'object_type': 'DAObject',
            'description': 'List of debts'
        }
        
        return objects
    
    def _build_initialization_map(self) -> Dict:
        """Build initialization logic"""
        return {
            'initial_code': {
                'set_defaults': [
                    'income = DAObject()',
                    'expenses = DAObject()',
                    'for attr in ["employment", "self_employment", "ei_benefits", "social_assistance", "pension", "investments", "spousal_support", "child_benefits", "other"]:',
                    '  setattr(income, attr, 0)',
                    'for attr in ["housing", "food", "clothing", "transportation", "childcare", "health", "insurance", "utilities", "other"]:',
                    '  setattr(expenses, attr, 0)'
                ]
            }
        }
    
    def _build_question_maps(self) -> List[Dict]:
        """Build question maps from parsed fields"""
        questions = []
        
        # Intro question
        questions.append({
            'id': 'intro',
            'type': 'continue',
            'question': 'Form 13 - Financial Statement',
            'subquestion': 'This form collects financial information for family law proceedings.',
            'field': 'intro_complete'
        })
        
        # Applicant info
        questions.append({
            'id': 'applicant_info',
            'type': 'fields',
            'question': 'Your Information',
            'fields': [
                {
                    'label': 'First Name',
                    'field': 'applicant.name.first',
                    'datatype': 'text',
                    'required': True
                },
                {
                    'label': 'Last Name',
                    'field': 'applicant.name.last',
                    'datatype': 'text',
                    'required': True
                },
                {
                    'label': 'Date of Birth',
                    'field': 'applicant.birthdate',
                    'datatype': 'date',
                    'required': False
                }
            ]
        })
        
        # Income fields - structured from real Form 13
        income_fields = self._extract_income_fields_map()
        questions.append({
            'id': 'income_info',
            'type': 'fields',
            'question': 'Monthly Income',
            'subquestion': 'Enter all sources of monthly income',
            'fields': income_fields
        })
        
        # Expense fields - structured map
        expense_fields = self._extract_expense_fields_map()
        questions.append({
            'id': 'expense_info',
            'type': 'fields',
            'question': 'Monthly Expenses',
            'subquestion': 'Enter your monthly expenses',
            'fields': expense_fields
        })
        
        # Summary screen
        questions.append({
            'id': 'summary',
            'type': 'event',
            'question': 'Financial Summary',
            'content': {
                'applicant_name': '${applicant.name.full()}',
                'total_income': '${currency(total_income)}',
                'total_expenses': '${currency(total_expenses)}',
                'net_income': '${currency(net_income)}'
            }
        })
        
        return questions
    
    def _extract_income_fields_map(self) -> List[Dict]:
        """Extract income fields as structured map"""
        income_types = [
            ('Employment Income', 'income.employment', 'Employment income before deductions'),
            ('Self-Employment', 'income.self_employment', 'Net self-employment income'),
            ('EI Benefits', 'income.ei_benefits', 'Employment Insurance benefits'),
            ('Social Assistance', 'income.social_assistance', 'Including ODSP payments'),
            ('Pension Income', 'income.pension', 'Including CPP and OAS'),
            ('Investment Income', 'income.investments', 'Interest and dividends'),
            ('Spousal Support', 'income.spousal_support', 'Support received'),
            ('Child Tax Benefits', 'income.child_benefits', 'CTB and GST credits'),
            ('Other Income', 'income.other', 'Any other sources')
        ]
        
        fields = []
        for label, field, help_text in income_types:
            fields.append({
                'label': label,
                'field': field,
                'datatype': 'currency',
                'min': 0,
                'default': 0,
                'required': False,
                'help': help_text
            })
        
        return fields
    
    def _extract_expense_fields_map(self) -> List[Dict]:
        """Extract expense fields as structured map"""
        expense_types = [
            ('Housing', 'expenses.housing', 'Rent or mortgage'),
            ('Food', 'expenses.food', 'Groceries and meals'),
            ('Clothing', 'expenses.clothing', 'Clothing and footwear'),
            ('Transportation', 'expenses.transportation', 'Car, transit, gas'),
            ('Childcare', 'expenses.childcare', 'Daycare, babysitting'),
            ('Health/Medical', 'expenses.health', 'Not covered by insurance'),
            ('Insurance', 'expenses.insurance', 'All insurance premiums'),
            ('Utilities', 'expenses.utilities', 'Heat, hydro, water'),
            ('Other', 'expenses.other', 'All other expenses')
        ]
        
        fields = []
        for label, field, help_text in expense_types:
            fields.append({
                'label': label,
                'field': field,
                'datatype': 'currency',
                'min': 0,
                'default': 0,
                'required': False,
                'help': help_text
            })
        
        return fields
    
    def _build_logic_maps(self) -> Dict:
        """Build logic and calculation maps"""
        return {
            'mandatory_flow': [
                'intro_complete',
                'applicant.name.first',
                'income_complete',
                'expenses_complete',
                'calculations_done',
                'show_summary'
            ],
            'calculations': {
                'total_income': 'sum([income.employment, income.self_employment, income.ei_benefits, income.social_assistance, income.pension, income.investments, income.spousal_support, income.child_benefits, income.other])',
                'total_expenses': 'sum([expenses.housing, expenses.food, expenses.clothing, expenses.transportation, expenses.childcare, expenses.health, expenses.insurance, expenses.utilities, expenses.other])',
                'net_income': 'total_income - total_expenses'
            }
        }
    
    def _convert_to_docassemble_yaml(self, interview_map: Dict) -> str:
        """Convert structured map to Docassemble YAML format"""
        yaml_blocks = []
        
        # Metadata block
        yaml_blocks.append(yaml.dump({'metadata': interview_map['metadata']}, default_flow_style=False))
        
        # Include block
        yaml_blocks.append(yaml.dump({'include': interview_map['config']['includes']}, default_flow_style=False))
        
        # Features block
        yaml_blocks.append(yaml.dump({'features': interview_map['config']['features']}, default_flow_style=False))
        
        # Objects block
        objects_list = []
        for obj_name, obj_info in interview_map['objects'].items():
            if obj_info['type'] == 'Individual':
                objects_list.append({obj_name: obj_info['type']})
            elif obj_info['type'] == 'DAList':
                objects_list.append({obj_name: f"DAList.using(object_type={obj_info['object_type']})"})
            else:
                objects_list.append({obj_name: obj_info['type']})
        yaml_blocks.append(yaml.dump({'objects': objects_list}, default_flow_style=False))
        
        # Initialization
        init_code = '\n'.join(interview_map['initialization']['initial_code']['set_defaults'])
        yaml_blocks.append(yaml.dump({'initial': True, 'code': '|\n  ' + init_code.replace('\n', '\n  ')}, default_flow_style=False))
        
        # Mandatory flow
        flow_code = '\n'.join(interview_map['logic']['mandatory_flow'])
        yaml_blocks.append(yaml.dump({'mandatory': True, 'code': '|\n  ' + flow_code}, default_flow_style=False))
        
        # Questions
        for q in interview_map['questions']:
            if q['type'] == 'continue':
                yaml_blocks.append(yaml.dump({
                    'question': q['question'],
                    'subquestion': q['subquestion'],
                    'continue button field': q['field']
                }, default_flow_style=False))
            elif q['type'] == 'fields':
                fields_list = []
                for f in q['fields']:
                    field_dict = {f['label']: f['field']}
                    if f.get('datatype'):
                        field_dict['datatype'] = f['datatype']
                    if f.get('required'):
                        field_dict['required'] = f['required']
                    if f.get('min') is not None:
                        field_dict['min'] = f['min']
                    if f.get('default') is not None:
                        field_dict['default'] = f['default']
                    fields_list.append(field_dict)
                
                question_dict = {
                    'question': q['question'],
                    'fields': fields_list
                }
                if q.get('subquestion'):
                    question_dict['subquestion'] = q['subquestion']
                if q['id'] == 'income_info':
                    question_dict['continue button field'] = 'income_complete'
                elif q['id'] == 'expense_info':
                    question_dict['continue button field'] = 'expenses_complete'
                    
                yaml_blocks.append(yaml.dump(question_dict, default_flow_style=False))
        
        # Calculations
        calc_lines = []
        for var, formula in interview_map['logic']['calculations'].items():
            calc_lines.append(f"{var} = {formula}")
        calc_lines.append("calculations_done = True")
        yaml_blocks.append(yaml.dump({'code': '|\n  ' + '\n  '.join(calc_lines)}, default_flow_style=False))
        
        # Summary screen
        yaml_blocks.append(yaml.dump({
            'event': 'show_summary',
            'question': 'Financial Summary',
            'subquestion': '|\n  **Name:** ${ applicant.name.full() }\n  \n  **Total Income:** ${ currency(total_income) }\n  **Total Expenses:** ${ currency(total_expenses) }\n  **Net Income:** ${ currency(net_income) }',
            'buttons': [{'Exit': 'exit'}]
        }, default_flow_style=False))
        
        return '---\n' + '---\n'.join(yaml_blocks)


def main():
    generator = RefinedMapGenerator()
    
    print("=" * 60)
    print("REFINED MAP STRUCTURE GENERATOR")
    print("=" * 60)
    
    if generator.generate_refined_form_13():
        print("\n✅ Generated Form 13 with refined map structures")
        print("\nTest at:")
        print("  http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/form_13_refined.yml")


if __name__ == "__main__":
    main()