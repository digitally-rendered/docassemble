#!/usr/bin/env python3
"""
Shared Field Mapper Agent

Maps common fields across all Ontario family law forms to identify patterns
that can be extracted into reusable interview modules.

This agent analyzes parsed form data to:
1. Identify frequently used field patterns
2. Group related fields into logical modules
3. Create field mappings for code generation
4. Define validation rules and dependencies

Author: Form Factory Orchestrator
Created: 2025-09-05
"""

import json
import os
from collections import defaultdict, Counter
from dataclasses import dataclass
from typing import Dict, List, Set, Optional, Tuple
import re

@dataclass
class FieldPattern:
    """Represents a common field pattern across forms"""
    canonical_name: str
    field_type: str
    forms_count: int
    forms_list: List[str]
    validation_pattern: str
    field_variations: List[Dict]
    module_category: str
    docassemble_type: str

@dataclass
class FieldModule:
    """Represents a logical grouping of related fields"""
    module_name: str
    category: str
    fields: List[FieldPattern]
    dependencies: List[str]
    common_validation: str
    docassemble_objects: List[str]

class SharedFieldMapper:
    """Analyzes and maps common fields across Ontario family law forms"""
    
    def __init__(self, parsed_forms_dir: str, common_fields_file: str):
        self.parsed_forms_dir = parsed_forms_dir
        self.common_fields_file = common_fields_file
        self.field_patterns = {}
        self.field_modules = {}
        self.form_categories = self._get_form_categories()
        
    def _get_form_categories(self) -> Dict[str, str]:
        """Define form categories for better organization"""
        return {
            # Core Applications
            'form_8': 'core_applications',
            'form_8a': 'core_applications', 
            'form_8b': 'core_applications',
            'form_8d': 'core_applications',
            'form_10': 'core_applications',
            'form_10a': 'core_applications',
            
            # Financial Statements
            'form_13': 'financial_statements',
            'form_13.1': 'financial_statements',
            'form_13a': 'financial_statements',
            'form_13b': 'financial_statements',
            'form_13c': 'financial_statements',
            
            # Motions and Conferences
            'form_14b': 'motions_conferences',
            'form_14c': 'motions_conferences',
            'form_15': 'motions_conferences',
            'form_15b': 'motions_conferences',
            'form_15c': 'motions_conferences',
            'form_17a': 'motions_conferences',
            'form_17c': 'motions_conferences',
            'form_17f': 'motions_conferences',
            
            # Orders
            'form_25': 'orders',
            'form_25a': 'orders',
            'form_25c': 'orders',
            'form_25d': 'orders',
            'form_25f': 'orders',
            
            # Enforcement
            'form_26': 'enforcement',
            'form_27': 'enforcement',
            'form_28': 'enforcement',
            'form_29': 'enforcement',
            'form_29a': 'enforcement',
            'form_29b': 'enforcement',
            'form_30': 'enforcement',
            
            # Service and Process
            'form_4': 'service_process',
            'form_6b': 'service_process',
            'form_6c': 'service_process',
            
            # Child Protection and Adoption
            'form_33f': 'child_protection_adoption',
            'form_34': 'child_protection_adoption',
            'form_34a': 'child_protection_adoption',
            'form_34f': 'child_protection_adoption',
            'form_34g': 'child_protection_adoption',
            'form_34i': 'child_protection_adoption',
            
            # Divorce Specific
            'form_36': 'divorce_specific',
            'form_36a': 'divorce_specific',
            
            # Interjurisdictional
            'form_37': 'interjurisdictional',
            'form_37a': 'interjurisdictional',
            'form_37b': 'interjurisdictional',
            
            # Alternative Dispute Resolution
            'form_43': 'alternative_dispute',
            'form_43a': 'alternative_dispute', 
            'form_43b': 'alternative_dispute',
        }
    
    def analyze_common_fields(self) -> Dict[str, FieldPattern]:
        """Analyze common fields from existing common_fields_report.json"""
        with open(self.common_fields_file, 'r') as f:
            data = json.load(f)
        
        patterns = {}
        
        for field_name, field_data in data.get('most_common_fields', {}).items():
            # Determine module category based on field name
            module_category = self._categorize_field(field_name)
            docassemble_type = self._get_docassemble_type(field_name)
            
            pattern = FieldPattern(
                canonical_name=self._normalize_field_name(field_name),
                field_type=self._infer_field_type(field_name, field_data),
                forms_count=field_data['count'],
                forms_list=field_data['forms'],
                validation_pattern=self._get_validation_pattern(field_name),
                field_variations=field_data.get('variations', []),
                module_category=module_category,
                docassemble_type=docassemble_type
            )
            
            patterns[pattern.canonical_name] = pattern
        
        self.field_patterns = patterns
        return patterns
    
    def _categorize_field(self, field_name: str) -> str:
        """Categorize field into logical modules"""
        field_lower = field_name.lower()
        
        # Court and Case Information
        if any(term in field_lower for term in ['court', 'file number', 'case number']):
            return 'court_case_info'
        
        # Party Information (Applicant/Respondent)
        if any(term in field_lower for term in ['applicant', 'respondent', 'party', 'name', 'address']):
            return 'party_info'
        
        # Child Information
        if any(term in field_lower for term in ['child', 'minor', 'custody', 'access']):
            return 'child_info'
        
        # Financial Information
        if any(term in field_lower for term in ['income', 'expense', 'asset', 'debt', 'financial', 'support']):
            return 'financial_info'
        
        # Legal Representation
        if any(term in field_lower for term in ['lawyer', 'counsel', 'representation']):
            return 'legal_representation'
        
        # Date and Time
        if any(term in field_lower for term in ['date', 'time', 'year', 'month', 'day']):
            return 'date_time'
        
        # Service Information
        if any(term in field_lower for term in ['service', 'served', 'notice']):
            return 'service_info'
        
        return 'general'
    
    def _normalize_field_name(self, field_name: str) -> str:
        """Normalize field name for consistent usage"""
        # Convert to snake_case
        name = re.sub(r'[^\w\s-]', '', field_name.lower())
        name = re.sub(r'[-\s]+', '_', name)
        return name.strip('_')
    
    def _infer_field_type(self, field_name: str, field_data: Dict) -> str:
        """Infer field type from name and variations"""
        field_lower = field_name.lower()
        
        # Check for specific patterns
        if any(term in field_lower for term in ['date', 'birth']):
            return 'date'
        
        if any(term in field_lower for term in ['phone', 'tel', 'fax']):
            return 'tel'
        
        if any(term in field_lower for term in ['email', '@']):
            return 'email'
        
        if any(term in field_lower for term in ['postal', 'zip']):
            return 'postal_code'
        
        if any(term in field_lower for term in ['yes/no', 'checkbox', 'check']):
            return 'yesno'
        
        if any(term in field_lower for term in ['amount', 'income', '$', 'dollar']):
            return 'currency'
        
        # Default to text
        return 'text'
    
    def _get_docassemble_type(self, field_name: str) -> str:
        """Get appropriate Docassemble field type"""
        field_type = self._infer_field_type(field_name, {})
        
        mapping = {
            'date': 'date',
            'tel': 'text',
            'email': 'email', 
            'postal_code': 'text',
            'yesno': 'yesnoradio',
            'currency': 'currency',
            'text': 'text'
        }
        
        return mapping.get(field_type, 'text')
    
    def _get_validation_pattern(self, field_name: str) -> str:
        """Get validation pattern for field"""
        field_lower = field_name.lower()
        
        if 'postal' in field_lower:
            return r'^[A-Za-z]\d[A-Za-z] \d[A-Za-z]\d$'
        
        if 'phone' in field_lower or 'tel' in field_lower:
            return r'^(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})$'
        
        if 'email' in field_lower:
            return r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if 'file number' in field_lower:
            return r'^[A-Z]{2}-\d{2}-\d{8}$'
        
        return ''
    
    def create_field_modules(self) -> Dict[str, FieldModule]:
        """Group related fields into logical modules"""
        modules = {}
        
        # Group fields by category
        categorized_fields = defaultdict(list)
        for pattern in self.field_patterns.values():
            categorized_fields[pattern.module_category].append(pattern)
        
        # Create modules for each category
        for category, fields in categorized_fields.items():
            module_name = f"{category}_module"
            
            # Determine dependencies based on field relationships
            dependencies = self._get_module_dependencies(category, fields)
            
            # Get common validation rules
            common_validation = self._get_common_validation(fields)
            
            # Define Docassemble objects needed
            objects = self._get_docassemble_objects(category, fields)
            
            module = FieldModule(
                module_name=module_name,
                category=category,
                fields=fields,
                dependencies=dependencies,
                common_validation=common_validation,
                docassemble_objects=objects
            )
            
            modules[module_name] = module
        
        self.field_modules = modules
        return modules
    
    def _get_module_dependencies(self, category: str, fields: List[FieldPattern]) -> List[str]:
        """Determine module dependencies"""
        dependencies = []
        
        # Most modules depend on court_case_info
        if category != 'court_case_info':
            dependencies.append('court_case_info_module')
        
        # Financial forms depend on party info
        if category == 'financial_info':
            dependencies.extend(['party_info_module', 'child_info_module'])
        
        # Child info depends on party info
        if category == 'child_info':
            dependencies.append('party_info_module')
        
        # Service depends on party info
        if category == 'service_info':
            dependencies.append('party_info_module')
        
        return dependencies
    
    def _get_common_validation(self, fields: List[FieldPattern]) -> str:
        """Get common validation logic for module"""
        # This would contain shared validation functions
        return "# Common validation rules for this module"
    
    def _get_docassemble_objects(self, category: str, fields: List[FieldPattern]) -> List[str]:
        """Define Docassemble objects needed for this module"""
        objects = []
        
        if category == 'party_info':
            objects.extend(['Individual', 'Address'])
        
        if category == 'child_info':
            objects.extend(['Individual', 'DAList'])
        
        if category == 'financial_info':
            objects.extend(['Value', 'DAList'])
        
        if category == 'court_case_info':
            objects.extend(['Court'])
        
        if category == 'legal_representation':
            objects.extend(['Individual', 'Address'])
        
        return objects
    
    def generate_shared_modules_spec(self) -> Dict:
        """Generate specification for shared modules"""
        if not self.field_modules:
            self.create_field_modules()
        
        spec = {
            'metadata': {
                'generated': '2025-09-05',
                'total_modules': len(self.field_modules),
                'total_fields': len(self.field_patterns),
                'description': 'Shared field modules for Ontario family law forms'
            },
            'modules': {}
        }
        
        for module_name, module in self.field_modules.items():
            spec['modules'][module_name] = {
                'category': module.category,
                'dependencies': module.dependencies,
                'docassemble_objects': module.docassemble_objects,
                'fields': []
            }
            
            for field in module.fields:
                spec['modules'][module_name]['fields'].append({
                    'canonical_name': field.canonical_name,
                    'docassemble_type': field.docassemble_type,
                    'validation_pattern': field.validation_pattern,
                    'forms_count': field.forms_count,
                    'field_variations': field.field_variations[:5]  # Limit for readability
                })
        
        return spec
    
    def save_modules_spec(self, output_file: str):
        """Save the modules specification to JSON file"""
        spec = self.generate_shared_modules_spec()
        
        with open(output_file, 'w') as f:
            json.dump(spec, f, indent=2)
        
        print(f"✅ Shared modules specification saved to: {output_file}")
        print(f"📊 Generated {spec['metadata']['total_modules']} modules with {spec['metadata']['total_fields']} fields")
    
    def run_analysis(self, output_file: str = None):
        """Run complete field analysis and mapping"""
        print("🔍 Analyzing common fields across Ontario family law forms...")
        
        # Step 1: Analyze common fields
        patterns = self.analyze_common_fields()
        print(f"✅ Analyzed {len(patterns)} common field patterns")
        
        # Step 2: Create field modules
        modules = self.create_field_modules()
        print(f"✅ Created {len(modules)} field modules")
        
        # Step 3: Generate and save specification
        if output_file:
            self.save_modules_spec(output_file)
        
        return {
            'patterns': patterns,
            'modules': modules,
            'spec': self.generate_shared_modules_spec()
        }

def main():
    """Main execution for shared field mapping"""
    import sys
    
    # Get paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    common_fields_file = os.path.join(base_dir, 'common_fields_report.json')
    parsed_forms_dir = os.path.join(base_dir, 'parsed_forms')
    output_file = os.path.join(base_dir, 'shared_modules_specification.json')
    
    # Initialize mapper
    mapper = SharedFieldMapper(parsed_forms_dir, common_fields_file)
    
    # Run analysis
    try:
        results = mapper.run_analysis(output_file)
        
        print("\n📋 Module Summary:")
        for module_name, module in results['modules'].items():
            print(f"  • {module_name}: {len(module.fields)} fields ({module.category})")
        
        print(f"\n🎯 Next Steps:")
        print(f"  1. Review shared_modules_specification.json")
        print(f"  2. Generate common interview modules")
        print(f"  3. Create Python code generators")
        print(f"  4. Build form conversion pipeline")
        
    except Exception as e:
        print(f"❌ Error during field mapping: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()