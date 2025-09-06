#!/usr/bin/env python3
"""
Comprehensive Field Analyzer for Ontario Family Law Forms
Analyzes improved parsed form data to identify common fields and patterns
"""

import json
import os
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple, Any
import re

class ComprehensiveFieldAnalyzer:
    def __init__(self, parsed_forms_dir: str):
        self.parsed_forms_dir = parsed_forms_dir
        self.forms_data = {}
        self.all_fields = []
        self.field_patterns = defaultdict(list)
        self.common_fields = defaultdict(set)
        self.field_type_mapping = defaultdict(Counter)
        
    def load_improved_forms(self):
        """Load all improved parsed form JSON files"""
        for filename in os.listdir(self.parsed_forms_dir):
            if filename.endswith('_improved.json'):
                filepath = os.path.join(self.parsed_forms_dir, filename)
                with open(filepath, 'r') as f:
                    form_data = json.load(f)
                    form_number = form_data.get('form_number', filename.replace('form_', '').replace('_improved.json', ''))
                    self.forms_data[form_number] = form_data
                    if 'fields' in form_data:
                        for field in form_data['fields']:
                            self.all_fields.append({
                                'form': form_number,
                                **field
                            })
    
    def identify_field_patterns(self):
        """Identify common field patterns across forms"""
        patterns = {
            # Party information patterns
            'party_name': r'(applicant|respondent|party|name|surname|given)',
            'party_address': r'(address|street|city|province|postal|municipality)',
            'party_contact': r'(phone|telephone|fax|email)',
            'party_birth': r'(birth|born|birthdate|date.*birth)',
            'party_lawyer': r'(lawyer|representative|counsel|solicitor)',
            
            # Court information patterns
            'court_info': r'(court|judge|justice|file.*no|docket)',
            'court_location': r'(court.*address|court.*office|municipality.*court)',
            
            # Children patterns
            'child_info': r'(child|children|dependant)',
            'child_name': r'(child.*name|children.*name)',
            'child_birth': r'(child.*birth|children.*birth)',
            'child_residence': r'(child.*resid|children.*resid|custody)',
            
            # Financial patterns
            'financial_amount': r'(amount|income|expense|payment|support|property.*value)',
            'financial_date': r'(date.*payment|payment.*date|effective.*date)',
            
            # Legal claim patterns
            'claims': r'(claim|order|relief|asking|request)',
            'divorce': r'(divorce|separation|marriage)',
            'custody': r'(custody|access|parenting|decision)',
            'support': r'(support|maintenance|spousal|child.*support)',
            'property': r'(property|equalization|possession|matrimonial)',
            
            # Document patterns
            'date_field': r'(date|dated|effective|commence)',
            'signature': r'(signature|sign|sworn|affirm)',
            'checkbox': r'(check|select|mark|choose)',
            
            # Service patterns
            'service': r'(serve|service|deliver|notice)',
        }
        
        for field in self.all_fields:
            field_name = field.get('field_name', '').lower()
            field_label = field.get('field_label', '').lower()
            
            for pattern_name, pattern_regex in patterns.items():
                if re.search(pattern_regex, field_name) or re.search(pattern_regex, field_label):
                    self.field_patterns[pattern_name].append({
                        'form': field['form'],
                        'field_id': field.get('field_id'),
                        'field_name': field.get('field_name'),
                        'field_type': field.get('field_type'),
                        'field_label': field.get('field_label')
                    })
    
    def identify_common_fields(self):
        """Identify fields that appear in multiple forms"""
        field_occurrences = defaultdict(set)
        
        for field in self.all_fields:
            # Create normalized field key
            field_name = field.get('field_name', '').lower()
            field_label = field.get('field_label', '').lower()
            
            # Track by both name and label patterns
            if field_name and field_name != 'field_':
                field_occurrences[field_name].add(field['form'])
            if field_label and field_label != 'field ':
                field_occurrences[field_label].add(field['form'])
        
        # Find fields in multiple forms
        for field_key, forms in field_occurrences.items():
            if len(forms) > 1:
                self.common_fields[field_key] = forms
    
    def analyze_field_types(self):
        """Analyze field types and their usage patterns"""
        for field in self.all_fields:
            field_type = field.get('field_type', 'unknown')
            field_name = field.get('field_name', '').lower()
            field_label = field.get('field_label', '').lower()
            
            # Map field types to Docassemble equivalents
            if field_type == 'text':
                # Further categorize text fields
                if re.search(r'email', field_name) or re.search(r'email', field_label):
                    self.field_type_mapping['email'][field['form']] += 1
                elif re.search(r'phone|tel', field_name) or re.search(r'phone|tel', field_label):
                    self.field_type_mapping['phone'][field['form']] += 1
                elif re.search(r'postal|zip', field_name) or re.search(r'postal|zip', field_label):
                    self.field_type_mapping['postal_code'][field['form']] += 1
                else:
                    self.field_type_mapping['text'][field['form']] += 1
            elif field_type == 'date':
                self.field_type_mapping['date'][field['form']] += 1
            elif field_type == 'checkbox':
                self.field_type_mapping['yesno'][field['form']] += 1
            elif field_type == 'dropdown':
                self.field_type_mapping['choices'][field['form']] += 1
            elif field_type == 'number':
                if re.search(r'amount|income|expense|payment|value|\$', field_name) or \
                   re.search(r'amount|income|expense|payment|value|\$', field_label):
                    self.field_type_mapping['currency'][field['form']] += 1
                else:
                    self.field_type_mapping['number'][field['form']] += 1
            elif field_type == 'area':
                self.field_type_mapping['area'][field['form']] += 1
    
    def generate_common_fields_spec(self) -> Dict:
        """Generate specification for common fields across forms"""
        spec = {
            'party_fields': [],
            'court_fields': [],
            'children_fields': [],
            'financial_fields': [],
            'claim_fields': [],
            'service_fields': [],
            'document_fields': []
        }
        
        # Categorize common fields
        for pattern_name, fields in self.field_patterns.items():
            if 'party' in pattern_name or pattern_name in ['party_name', 'party_address', 'party_contact', 'party_birth', 'party_lawyer']:
                category = 'party_fields'
            elif 'court' in pattern_name:
                category = 'court_fields'
            elif 'child' in pattern_name:
                category = 'children_fields'
            elif 'financial' in pattern_name or pattern_name in ['support', 'property']:
                category = 'financial_fields'
            elif pattern_name in ['claims', 'divorce', 'custody']:
                category = 'claim_fields'
            elif pattern_name == 'service':
                category = 'service_fields'
            else:
                category = 'document_fields'
            
            # Add unique fields to category
            seen = set()
            for field in fields:
                field_key = f"{field['field_name']}_{field['field_type']}"
                if field_key not in seen:
                    spec[category].append({
                        'field_name': field['field_name'],
                        'field_type': field['field_type'],
                        'field_label': field['field_label'],
                        'forms_used': [f['form'] for f in fields if f['field_name'] == field['field_name']]
                    })
                    seen.add(field_key)
        
        return spec
    
    def generate_report(self) -> Dict:
        """Generate comprehensive analysis report"""
        self.load_improved_forms()
        self.identify_field_patterns()
        self.identify_common_fields()
        self.analyze_field_types()
        
        report = {
            'summary': {
                'total_forms': len(self.forms_data),
                'total_fields': len(self.all_fields),
                'forms_analyzed': list(self.forms_data.keys())
            },
            'field_statistics': {
                'fields_per_form': {
                    form: data.get('total_fields', 0) 
                    for form, data in self.forms_data.items()
                },
                'field_types_distribution': dict(self.field_type_mapping),
                'common_fields_count': len(self.common_fields)
            },
            'common_fields': {
                field: list(forms) 
                for field, forms in self.common_fields.items()
                if len(forms) > 2  # Fields in 3+ forms
            },
            'field_patterns': {
                pattern: len(fields) 
                for pattern, fields in self.field_patterns.items()
            },
            'common_fields_specification': self.generate_common_fields_spec(),
            'recommendations': self.generate_recommendations()
        }
        
        return report
    
    def generate_recommendations(self) -> Dict:
        """Generate recommendations for module organization"""
        return {
            'shared_modules': {
                'ontario_party_objects': 'Handle all party information (applicant, respondent, lawyers)',
                'ontario_court_objects': 'Court information, case details, filing info',
                'ontario_children_objects': 'Children information, custody, parenting',
                'ontario_financial_objects': 'Financial information, support calculations',
                'ontario_common_fields': 'Cross-cutting fields used everywhere'
            },
            'field_standardization': {
                'dates': 'Use DADate for all date fields',
                'currency': 'Use DANumber with currency validation',
                'addresses': 'Use DAAddress with Canadian postal code validation',
                'emails': 'Use email validation pattern',
                'phones': 'Use phone number validation pattern'
            },
            'object_patterns': {
                'parties': 'Use Individual objects with proper attributes',
                'children': 'Use DAList of Individual objects',
                'claims': 'Use DADict for claim selections',
                'documents': 'Use attachment blocks for document generation'
            }
        }

def main():
    analyzer = ComprehensiveFieldAnalyzer(
        '/Users/draw/development/docassemble/docassemble_webapp/docassemble/webapp/data/questions/ontario-family-law/utilities/parsed_forms'
    )
    
    report = analyzer.generate_report()
    
    # Save report
    with open('improved_field_analysis_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Analysis complete!")
    print(f"Total forms analyzed: {report['summary']['total_forms']}")
    print(f"Total fields found: {report['summary']['total_fields']}")
    print(f"Common fields identified: {report['field_statistics']['common_fields_count']}")
    
    print("\nField Pattern Distribution:")
    for pattern, count in report['field_patterns'].items():
        print(f"  {pattern}: {count} fields")
    
    print("\nTop Common Fields (in 3+ forms):")
    for field, forms in list(report['common_fields'].items())[:10]:
        print(f"  {field}: {len(forms)} forms")

if __name__ == '__main__':
    main()