#!/usr/bin/env python3
"""
Enhanced Common Fields Analyzer Agent

Analyzes actual parsed form data to identify genuine common field patterns
across Ontario family law forms.

This agent:
1. Reads actual parsed form JSON files 
2. Identifies semantically similar fields across forms
3. Groups fields into logical categories
4. Creates shared field modules specification
5. Generates field mappings for interview generation

Author: Form Factory Orchestrator
Created: 2025-09-05
"""

import json
import os
import re
from collections import defaultdict, Counter
from dataclasses import dataclass
from typing import Dict, List, Set, Optional, Tuple
from difflib import SequenceMatcher

@dataclass
class CommonField:
    """Represents a field pattern found across multiple forms"""
    canonical_name: str
    semantic_category: str
    field_type: str
    docassemble_type: str
    validation_pattern: str
    forms_using: List[str]
    field_variations: List[Dict]
    usage_count: int

@dataclass
class FieldGroup:
    """Represents a logical grouping of related common fields"""
    group_name: str
    category: str
    description: str
    fields: List[CommonField]
    dependencies: List[str]
    docassemble_objects: List[str]

class EnhancedCommonFieldsAnalyzer:
    """Analyzes parsed form data to identify genuine common field patterns"""
    
    def __init__(self, parsed_forms_dir: str):
        self.parsed_forms_dir = parsed_forms_dir
        self.parsed_forms_data = {}
        self.common_fields = {}
        self.field_groups = {}
        
        # Semantic patterns to identify common field types
        self.semantic_patterns = {
            'court_file_number': [
                'court file number', 'file number', 'case number', 'court file no'
            ],
            'applicant_name': [
                'applicant', 'full legal name', 'name', 'first name', 'last name',
                'full name', 'legal name'
            ],
            'respondent_name': [
                'respondent', 'full legal name', 'name', 'first name', 'last name',
                'full name', 'legal name'
            ],
            'address': [
                'address', 'street address', 'mailing address', 'residential address',
                'home address', 'current address'
            ],
            'phone_number': [
                'phone', 'telephone', 'cell phone', 'mobile', 'phone number',
                'tel', 'contact number'
            ],
            'email': [
                'email', 'e-mail', 'email address', 'electronic mail'
            ],
            'date_of_birth': [
                'date of birth', 'birth date', 'born', 'dob', 'birthdate'
            ],
            'postal_code': [
                'postal code', 'postal', 'zip code', 'zip'
            ],
            'lawyer_name': [
                'lawyer', 'counsel', 'legal representative', 'attorney',
                'solicitor', 'barrister'
            ],
            'child_name': [
                'child', 'minor', 'children', 'child name', 'full name of child'
            ],
            'income_amount': [
                'income', 'gross income', 'annual income', 'monthly income',
                'salary', 'wages', 'earnings'
            ],
            'support_amount': [
                'support', 'child support', 'spousal support', 'support amount',
                'monthly support', 'support payment'
            ],
            'date_general': [
                'date', 'date of', 'on', 'dated', 'day', 'month', 'year'
            ]
        }
    
    def load_parsed_forms(self) -> Dict[str, List[Dict]]:
        """Load all parsed form JSON files"""
        parsed_data = {}
        
        # Get list of JSON files in parsed_forms directory
        json_files = [f for f in os.listdir(self.parsed_forms_dir) 
                     if f.endswith('_fields.json')]
        
        for json_file in json_files:
            form_name = json_file.replace('_fields.json', '')
            file_path = os.path.join(self.parsed_forms_dir, json_file)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    parsed_data[form_name] = data
                    print(f"✅ Loaded {len(data)} fields from {form_name}")
            except Exception as e:
                print(f"⚠️ Error loading {json_file}: {e}")
        
        self.parsed_forms_data = parsed_data
        return parsed_data
    
    def normalize_field_label(self, label: str) -> str:
        """Normalize field label for comparison"""
        if not label:
            return ""
        
        # Convert to lowercase, remove special characters, normalize spaces
        normalized = re.sub(r'[^\w\s]', ' ', label.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Remove common repetitive patterns
        normalized = re.sub(r'\b(\w+)(\s+\1)+\b', r'\1', normalized)
        
        return normalized
    
    def get_semantic_category(self, field_label: str, field_name: str) -> str:
        """Determine semantic category of a field"""
        combined_text = f"{field_label} {field_name}".lower()
        
        for category, patterns in self.semantic_patterns.items():
            for pattern in patterns:
                if pattern in combined_text:
                    return category
        
        return 'general'
    
    def calculate_similarity(self, label1: str, label2: str) -> float:
        """Calculate similarity between two field labels"""
        norm1 = self.normalize_field_label(label1)
        norm2 = self.normalize_field_label(label2)
        
        if not norm1 or not norm2:
            return 0.0
        
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def find_common_fields(self, similarity_threshold: float = 0.7) -> Dict[str, CommonField]:
        """Find fields that appear across multiple forms with high similarity"""
        all_fields = []
        
        # Collect all fields from all forms
        for form_name, fields in self.parsed_forms_data.items():
            for field in fields:
                all_fields.append({
                    'form': form_name,
                    'field': field,
                    'normalized_label': self.normalize_field_label(field.get('field_label', '')),
                    'semantic_category': self.get_semantic_category(
                        field.get('field_label', ''), 
                        field.get('field_name', '')
                    )
                })
        
        # Group similar fields
        field_groups = defaultdict(list)
        processed = set()
        
        for i, field1 in enumerate(all_fields):
            if i in processed:
                continue
            
            group_key = field1['normalized_label']
            if not group_key:
                continue
                
            field_groups[group_key].append(field1)
            processed.add(i)
            
            # Find similar fields
            for j, field2 in enumerate(all_fields[i+1:], i+1):
                if j in processed:
                    continue
                
                similarity = self.calculate_similarity(
                    field1['normalized_label'], 
                    field2['normalized_label']
                )
                
                if similarity >= similarity_threshold:
                    field_groups[group_key].append(field2)
                    processed.add(j)
        
        # Filter to only include fields that appear in multiple forms
        common_fields = {}
        
        for group_key, fields in field_groups.items():
            if len(fields) < 2:  # Must appear in at least 2 forms
                continue
            
            # Count unique forms
            forms_set = set(f['form'] for f in fields)
            if len(forms_set) < 2:
                continue
            
            # Create canonical name
            canonical_name = self._create_canonical_name(group_key, fields)
            
            # Determine field type and validation
            field_type = self._determine_field_type(fields)
            docassemble_type = self._get_docassemble_type(field_type, canonical_name)
            validation_pattern = self._get_validation_pattern(canonical_name, field_type)
            
            # Get semantic category from most common one
            categories = [f['semantic_category'] for f in fields]
            semantic_category = Counter(categories).most_common(1)[0][0]
            
            # Create field variations list
            variations = []
            for f in fields[:10]:  # Limit to 10 examples
                variations.append({
                    'form': f['form'],
                    'label': f['field']['field_label'],
                    'field_name': f['field']['field_name'],
                    'field_type': f['field']['field_type']
                })
            
            common_field = CommonField(
                canonical_name=canonical_name,
                semantic_category=semantic_category,
                field_type=field_type,
                docassemble_type=docassemble_type,
                validation_pattern=validation_pattern,
                forms_using=list(forms_set),
                field_variations=variations,
                usage_count=len(forms_set)
            )
            
            common_fields[canonical_name] = common_field
        
        self.common_fields = common_fields
        return common_fields
    
    def _create_canonical_name(self, group_key: str, fields: List[Dict]) -> str:
        """Create a canonical name for the field group"""
        # Use the semantic category if available
        semantic_categories = [f['semantic_category'] for f in fields]
        most_common_category = Counter(semantic_categories).most_common(1)[0][0]
        
        if most_common_category != 'general':
            return most_common_category
        
        # Otherwise, use the normalized group key
        words = group_key.split()
        if len(words) <= 3:
            return '_'.join(words)
        else:
            # Take first 3 most meaningful words
            return '_'.join(words[:3])
    
    def _determine_field_type(self, fields: List[Dict]) -> str:
        """Determine the most appropriate field type"""
        type_counts = Counter(f['field']['field_type'] for f in fields)
        return type_counts.most_common(1)[0][0]
    
    def _get_docassemble_type(self, field_type: str, canonical_name: str) -> str:
        """Get appropriate Docassemble field type"""
        name_lower = canonical_name.lower()
        
        # Specific mappings based on semantic meaning
        if 'email' in name_lower:
            return 'email'
        elif any(term in name_lower for term in ['date', 'birth']):
            return 'date'
        elif any(term in name_lower for term in ['phone', 'tel']):
            return 'text'
        elif any(term in name_lower for term in ['amount', 'income', 'support']):
            return 'currency'
        elif 'postal' in name_lower:
            return 'text'
        elif field_type == 'date':
            return 'date'
        else:
            return 'text'
    
    def _get_validation_pattern(self, canonical_name: str, field_type: str) -> str:
        """Get validation pattern for field"""
        name_lower = canonical_name.lower()
        
        if 'postal' in name_lower:
            return r'^[A-Za-z]\d[A-Za-z] \d[A-Za-z]\d$'
        elif any(term in name_lower for term in ['phone', 'tel']):
            return r'^(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})$'
        elif 'email' in name_lower:
            return r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        elif 'court_file_number' in name_lower:
            return r'^[A-Z]{2}-\d{2}-\d{8}$'
        
        return ''
    
    def create_field_groups(self) -> Dict[str, FieldGroup]:
        """Group common fields into logical modules"""
        if not self.common_fields:
            self.find_common_fields()
        
        # Group fields by semantic category
        category_groups = defaultdict(list)
        for field in self.common_fields.values():
            category_groups[field.semantic_category].append(field)
        
        field_groups = {}
        
        # Define logical groupings with descriptions
        group_definitions = {
            'court_case_info': {
                'description': 'Court and case identification fields',
                'categories': ['court_file_number'],
                'objects': ['Court']
            },
            'party_information': {
                'description': 'Applicant and respondent personal information',
                'categories': ['applicant_name', 'respondent_name', 'address', 'phone_number', 'email', 'date_of_birth', 'postal_code'],
                'objects': ['Individual', 'Address', 'Person']
            },
            'legal_representation': {
                'description': 'Lawyer and legal counsel information',
                'categories': ['lawyer_name'],
                'objects': ['Individual', 'Address']
            },
            'child_information': {
                'description': 'Information about children involved in the case',
                'categories': ['child_name'],
                'objects': ['Individual', 'DAList']
            },
            'financial_information': {
                'description': 'Income, support, and financial details',
                'categories': ['income_amount', 'support_amount'],
                'objects': ['Value', 'Currency']
            },
            'dates_and_timing': {
                'description': 'Date fields used across forms',
                'categories': ['date_general'],
                'objects': []
            },
            'general_fields': {
                'description': 'General purpose fields used across multiple forms',
                'categories': ['general'],
                'objects': []
            }
        }
        
        for group_name, group_def in group_definitions.items():
            group_fields = []
            
            for category in group_def['categories']:
                if category in category_groups:
                    group_fields.extend(category_groups[category])
            
            if group_fields:  # Only create groups that have fields
                dependencies = self._get_group_dependencies(group_name)
                
                field_group = FieldGroup(
                    group_name=group_name,
                    category=group_def['categories'][0] if group_def['categories'] else 'general',
                    description=group_def['description'],
                    fields=group_fields,
                    dependencies=dependencies,
                    docassemble_objects=group_def['objects']
                )
                
                field_groups[group_name] = field_group
        
        self.field_groups = field_groups
        return field_groups
    
    def _get_group_dependencies(self, group_name: str) -> List[str]:
        """Determine dependencies between field groups"""
        dependencies = []
        
        # Most groups depend on court_case_info
        if group_name != 'court_case_info':
            dependencies.append('court_case_info')
        
        # Child and financial info depend on party information
        if group_name in ['child_information', 'financial_information']:
            dependencies.append('party_information')
        
        # Legal representation depends on party information
        if group_name == 'legal_representation':
            dependencies.append('party_information')
        
        return dependencies
    
    def generate_analysis_report(self) -> Dict:
        """Generate comprehensive analysis report"""
        if not self.common_fields:
            self.find_common_fields()
        
        if not self.field_groups:
            self.create_field_groups()
        
        report = {
            'metadata': {
                'analysis_date': '2025-09-05',
                'total_forms_analyzed': len(self.parsed_forms_data),
                'total_fields_analyzed': sum(len(fields) for fields in self.parsed_forms_data.values()),
                'common_fields_found': len(self.common_fields),
                'field_groups_created': len(self.field_groups)
            },
            'forms_analyzed': list(self.parsed_forms_data.keys()),
            'common_fields': {},
            'field_groups': {}
        }
        
        # Add common fields to report
        for name, field in self.common_fields.items():
            report['common_fields'][name] = {
                'semantic_category': field.semantic_category,
                'field_type': field.field_type,
                'docassemble_type': field.docassemble_type,
                'validation_pattern': field.validation_pattern,
                'usage_count': field.usage_count,
                'forms_using': field.forms_using,
                'sample_variations': field.field_variations[:3]  # Just first 3 for report
            }
        
        # Add field groups to report  
        for name, group in self.field_groups.items():
            report['field_groups'][name] = {
                'description': group.description,
                'field_count': len(group.fields),
                'dependencies': group.dependencies,
                'docassemble_objects': group.docassemble_objects,
                'fields': [f.canonical_name for f in group.fields]
            }
        
        return report
    
    def save_analysis_report(self, output_file: str):
        """Save analysis report to JSON file"""
        report = self.generate_analysis_report()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Enhanced common fields analysis saved to: {output_file}")
        print(f"📊 Analysis Summary:")
        print(f"   • {report['metadata']['total_forms_analyzed']} forms analyzed")
        print(f"   • {report['metadata']['total_fields_analyzed']} total fields analyzed")
        print(f"   • {report['metadata']['common_fields_found']} common fields identified")
        print(f"   • {report['metadata']['field_groups_created']} field groups created")
    
    def run_complete_analysis(self, output_file: str = None):
        """Run complete field analysis workflow"""
        print("🔍 Enhanced Common Fields Analysis Starting...")
        
        # Step 1: Load parsed forms
        print("\n📁 Loading parsed form data...")
        self.load_parsed_forms()
        
        # Step 2: Find common fields
        print("\n🔎 Identifying common field patterns...")
        common_fields = self.find_common_fields()
        
        # Step 3: Create field groups
        print("\n📦 Creating logical field groups...")
        field_groups = self.create_field_groups()
        
        # Step 4: Save report
        if output_file:
            print("\n💾 Saving analysis report...")
            self.save_analysis_report(output_file)
        
        return {
            'common_fields': common_fields,
            'field_groups': field_groups,
            'report': self.generate_analysis_report()
        }

def main():
    """Main execution function"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    parsed_forms_dir = os.path.join(base_dir, 'parsed_forms')
    output_file = os.path.join(base_dir, 'enhanced_common_fields_analysis.json')
    
    analyzer = EnhancedCommonFieldsAnalyzer(parsed_forms_dir)
    
    try:
        results = analyzer.run_complete_analysis(output_file)
        
        print(f"\n🎯 Field Groups Summary:")
        for group_name, group in results['field_groups'].items():
            print(f"  • {group_name}: {len(group.fields)} fields - {group.description}")
        
        print(f"\n📋 Top Common Fields:")
        sorted_fields = sorted(results['common_fields'].values(), 
                             key=lambda x: x.usage_count, reverse=True)
        
        for field in sorted_fields[:10]:
            print(f"  • {field.canonical_name}: {field.usage_count} forms ({field.semantic_category})")
        
        print(f"\n🚀 Next Steps:")
        print(f"  1. Review enhanced_common_fields_analysis.json")
        print(f"  2. Generate shared interview modules")
        print(f"  3. Create code generators for interviews")
        print(f"  4. Build form conversion pipeline")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()