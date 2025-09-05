#!/usr/bin/env python3
"""
Incremental Data-Driven Generator
Step by step generation showing how we use parsed data and domain mappings
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IncrementalDataDrivenGenerator:
    """Generate interviews incrementally from parsed data"""
    
    def __init__(self):
        self.output_dir = Path('data_driven_interviews')
        self.output_dir.mkdir(exist_ok=True)
        
        # Load the data
        self.parsed_fields = self._load_parsed_fields()
        self.domain_mappings = self._load_domain_mappings()
        
    def _load_parsed_fields(self) -> List[Dict]:
        """Load the parsed Form 13 fields"""
        # Try enhanced version first
        enhanced_path = Path('workflow_output/enhanced_parsed_forms/form_13_fields.json')
        regular_path = Path('parsed_forms/form_13_fields.json')
        
        if enhanced_path.exists():
            with open(enhanced_path, 'r') as f:
                fields = json.load(f)
                logger.info(f"Loaded {len(fields)} fields from enhanced parsed data")
                return fields
        elif regular_path.exists():
            with open(regular_path, 'r') as f:
                fields = json.load(f)
                logger.info(f"Loaded {len(fields)} fields from regular parsed data")
                return fields
        else:
            logger.error("No parsed field data found")
            return []
    
    def _load_domain_mappings(self) -> Dict:
        """Load domain mapping data"""
        path = Path('workflow_output/domain_mappings.json')
        if path.exists():
            with open(path, 'r') as f:
                mappings = json.load(f)
                logger.info(f"Loaded domain mappings with {len(mappings.get('entities', {}))} entities")
                return mappings
        else:
            logger.warning("No domain mappings found")
            return {}
    
    def step_1_analyze_data(self):
        """Step 1: Analyze what we have"""
        print("\n" + "="*60)
        print("STEP 1: ANALYZING DATA")
        print("="*60)
        
        # Show sample fields
        print(f"\nTotal parsed fields: {len(self.parsed_fields)}")
        print("\nFirst 5 fields:")
        for i, field in enumerate(self.parsed_fields[:5]):
            print(f"\n  Field {i+1}:")
            print(f"    ID: {field.get('field_id')}")
            print(f"    Name: {field.get('field_name')}")
            print(f"    Label: {field.get('field_label')}")
            print(f"    Type: {field.get('field_type')}")
            print(f"    Table: {field.get('table_name')}")
        
        # Show domain entities
        print("\n" + "-"*40)
        print("\nDomain Entities:")
        if self.domain_mappings and 'entities' in self.domain_mappings:
            for entity_id, entity in self.domain_mappings['entities'].items():
                print(f"\n  {entity_id}:")
                print(f"    Type: {entity['entity_type']}")
                print(f"    Docassemble: {entity['docassemble_type']}")
                print(f"    Variable: {entity['variable_name']}")
                print(f"    Cardinality: {entity['cardinality']}")
    
    def step_2_identify_key_fields(self) -> Dict[str, List[Dict]]:
        """Step 2: Identify key field types"""
        print("\n" + "="*60)
        print("STEP 2: IDENTIFYING KEY FIELDS")
        print("="*60)
        
        key_fields = {
            'court_info': [],
            'party_info': [],
            'financial_info': [],
            'other': []
        }
        
        for field in self.parsed_fields:
            field_name = field.get('field_name', '').lower()
            field_label = field.get('field_label', '').lower()
            
            # Classify the field
            if 'court' in field_name or 'court' in field_label:
                key_fields['court_info'].append(field)
            elif any(term in field_name or term in field_label 
                    for term in ['name', 'address', 'birth', 'applicant', 'respondent']):
                key_fields['party_info'].append(field)
            elif any(term in field_name or term in field_label 
                    for term in ['income', 'expense', 'amount', 'monthly', 'annual']):
                key_fields['financial_info'].append(field)
            else:
                key_fields['other'].append(field)
        
        # Show summary
        for category, fields in key_fields.items():
            print(f"\n{category}: {len(fields)} fields")
            if fields:
                print(f"  Sample: {fields[0].get('field_label', 'Unknown')}")
        
        return key_fields
    
    def step_3_map_to_domains(self, key_fields: Dict[str, List[Dict]]) -> Dict:
        """Step 3: Map fields to domain entities"""
        print("\n" + "="*60)
        print("STEP 3: MAPPING TO DOMAIN ENTITIES")
        print("="*60)
        
        field_mappings = {}
        
        # Get person entity
        person_entity = None
        for entity_id, entity in self.domain_mappings.get('entities', {}).items():
            if entity['entity_type'] == 'person':
                person_entity = entity
                break
        
        # Map party info fields to person entity
        if person_entity and key_fields.get('party_info'):
            print(f"\nMapping {len(key_fields['party_info'])} party fields to {person_entity['variable_name']}")
            for field in key_fields['party_info'][:5]:  # Just first 5 for demo
                field_mappings[field['field_id']] = {
                    'entity': person_entity['variable_name'],
                    'docassemble_type': person_entity['docassemble_type'],
                    'field': field
                }
        
        return field_mappings
    
    def step_4_generate_simple_yaml(self, key_fields: Dict[str, List[Dict]]) -> str:
        """Step 4: Generate simple YAML from key fields"""
        print("\n" + "="*60)
        print("STEP 4: GENERATING SIMPLE YAML")
        print("="*60)
        
        yaml = """---
metadata:
  title: Form 13 - Incremental Data-Driven
  short title: Form 13 Incremental
---
include:
  - docassemble.base:data/questions/basic-questions.yml
---
objects:
  - person: Individual
  - form_data: DAObject
---
mandatory: True
code: |
  intro_seen
  collect_basic_info
  show_summary
---
question: |
  Form 13 Financial Statement
subquestion: |
  Generated from parsed form data.
continue button field: intro_seen
---
question: |
  Basic Information
fields:"""
        
        # Add some real fields from parsed data
        added_fields = 0
        for field in key_fields.get('party_info', [])[:5]:  # First 5 party fields
            field_name = self._sanitize_field_name(field['field_name'])
            field_label = self._clean_label(field['field_label'])
            
            if field_name and field_label:
                yaml += f'\n  - "{field_label}": form_data.{field_name}'
                yaml += '\n    required: False'
                added_fields += 1
        
        if added_fields == 0:
            # Add default fields if no good fields found
            yaml += '\n  - "Your Name": person.name.first'
            yaml += '\n    required: False'
        
        yaml += """
continue button field: collect_basic_info
---
event: show_summary
question: |
  Summary
subquestion: |
  Data collected successfully.
buttons:
  - Exit: exit
---"""
        
        print(f"\nGenerated YAML with {added_fields} fields from parsed data")
        
        return yaml
    
    def step_5_generate_with_domains(self) -> str:
        """Step 5: Generate with full domain mapping"""
        print("\n" + "="*60)
        print("STEP 5: GENERATING WITH DOMAIN MAPPING")
        print("="*60)
        
        # This would be the full generation using all mappings
        # For now, keeping it simple for testing
        
        yaml = self._generate_full_yaml()
        
        return yaml
    
    def _sanitize_field_name(self, name: str) -> str:
        """Clean up field name for use as variable"""
        if not name:
            return ""
        # Remove repetitions and special chars
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        name = re.sub(r'_+', '_', name)
        name = name.strip('_').lower()
        # Truncate if too long
        if len(name) > 30:
            name = name[:30]
        return name
    
    def _clean_label(self, label: str) -> str:
        """Clean up field label"""
        if not label:
            return ""
        # Remove excessive repetition
        words = label.split()
        if words:
            # If same word repeated, keep only one
            unique_words = []
            prev = None
            for word in words:
                if word != prev:
                    unique_words.append(word)
                    prev = word
            label = ' '.join(unique_words)
        
        # Capitalize and truncate
        if label:
            label = label[0].upper() + label[1:]
        if len(label) > 50:
            label = label[:47] + "..."
        
        return label
    
    def _generate_full_yaml(self) -> str:
        """Generate complete YAML with all domain mappings"""
        # Start with basic structure
        yaml = """---
metadata:
  title: Form 13 - Full Data-Driven with Domains
  short title: Form 13 Complete
---
include:
  - docassemble.base:data/questions/basic-questions.yml
---
objects:"""
        
        # Add objects from domain mappings
        for entity_id, entity in self.domain_mappings.get('entities', {}).items():
            if entity['cardinality'] == 'single':
                yaml += f"\n  - {entity['variable_name']}: {entity['docassemble_type']}"
            else:
                yaml += f"\n  - {entity['variable_name']}: DAList.using(object_type={entity['docassemble_type']})"
        
        yaml += """
---
mandatory: True
code: |
  intro_seen
  final_screen
---
question: |
  Form 13 Financial Statement
subquestion: |
  Complete with domain mapping.
continue button field: intro_seen
---
event: final_screen
question: |
  Complete
subquestion: |
  Interview generated from parsed data and domain mappings.
buttons:
  - Exit: exit
---"""
        
        return yaml
    
    def run_all_steps(self):
        """Run all steps incrementally"""
        
        # Step 1: Analyze
        self.step_1_analyze_data()
        
        # Step 2: Identify key fields
        key_fields = self.step_2_identify_key_fields()
        
        # Step 3: Map to domains
        field_mappings = self.step_3_map_to_domains(key_fields)
        
        # Step 4: Generate simple YAML
        simple_yaml = self.step_4_generate_simple_yaml(key_fields)
        output_file = self.output_dir / 'form_13_step_4_simple.yml'
        with open(output_file, 'w') as f:
            f.write(simple_yaml)
        print(f"\n✅ Saved: {output_file}")
        
        # Step 5: Generate with domains
        full_yaml = self.step_5_generate_with_domains()
        output_file = self.output_dir / 'form_13_step_5_domains.yml'
        with open(output_file, 'w') as f:
            f.write(full_yaml)
        print(f"✅ Saved: {output_file}")
        
        print("\n" + "="*60)
        print("COMPLETE!")
        print("="*60)
        print("\nTest the interviews at:")
        print("  Step 4: /interview?i=docassemble.webapp:ontario-family-law/utilities/data_driven_interviews/form_13_step_4_simple.yml")
        print("  Step 5: /interview?i=docassemble.webapp:ontario-family-law/utilities/data_driven_interviews/form_13_step_5_domains.yml")


def main():
    generator = IncrementalDataDrivenGenerator()
    generator.run_all_steps()


if __name__ == "__main__":
    main()