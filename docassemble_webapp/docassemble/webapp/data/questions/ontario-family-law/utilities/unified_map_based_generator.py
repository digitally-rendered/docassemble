#!/usr/bin/env python3
"""
Unified Map-Based Interview Generator
Transforms parsed form data through domain mapping and Docassemble mapping
Uses Ontario objects and interview framework for maintainable, repeatable generation

Pipeline:
1. Load parsed form data
2. Apply domain mapping (form fields -> domain concepts)
3. Apply Docassemble mapping (domain concepts -> DA objects/questions)
4. Generate interview maps using Ontario framework
5. Encode maps to YAML
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from dataclasses import dataclass, asdict

# Import Ontario frameworks
from ontario_common_fields import CommonField, FieldValidation
from ontario_party_objects import OntarioAddress, OntarioName, OntarioParty
from ontario_financial_objects import IncomeSource, FinancialAsset
from ontario_court_objects import OntarioCourtCase
from ontario_children_objects import OntarioChild

# Import interview framework
from common_interview_framework.master_interview import OntarioFamilyLawInterview
from common_interview_framework.base_objects import *
from common_interview_framework.validation_functions import *

@dataclass
class DomainMapping:
    """Maps form field to domain concept"""
    form_field_name: str
    domain_concept: str
    ontario_object_path: str
    field_type: str
    validation_rules: List[str]
    required: bool = False

@dataclass
class DocassembleMapping:
    """Maps domain concept to Docassemble structure"""
    domain_concept: str
    docassemble_variable: str
    question_type: str  # question, yesno, code, review, etc.
    field_properties: Dict[str, Any]
    dependencies: List[str]

class UnifiedMapBasedGenerator:
    """Unified generator using domain and Docassemble mapping with consistent form keys"""
    
    def __init__(self):
        self.parsed_forms_dir = Path('parsed_forms')
        self.output_dir = Path('generated_interviews_unified')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load form key consistency registry
        self.form_key_manager = self._load_form_key_registry()
        
        # Load mapping configurations
        self.domain_mappings = self._load_domain_mappings()
        self.docassemble_mappings = self._load_docassemble_mappings()
        
        # Initialize Ontario framework
        self.ontario_framework = OntarioFamilyLawInterview()
        
    def _load_form_key_registry(self):
        """Load the form key consistency registry"""
        from form_key_consistency_manager import FormKeyConsistencyManager
        
        manager = FormKeyConsistencyManager()
        registry_path = Path('form_key_registry.json')
        
        if registry_path.exists():
            manager.load_registry(registry_path)
            print(f"✅ Loaded form key registry with {manager.registry.total_fields} consistent keys")
        else:
            print("⚠️  Form key registry not found, generating from parsed forms...")
            manager.process_parsed_forms(self.parsed_forms_dir)
            manager.save_registry(registry_path)
        
        return manager
    
    def _load_domain_mappings(self) -> List[DomainMapping]:
        """Load domain mapping configuration"""
        mappings = []
        
        # Standard domain mappings for Ontario family law
        standard_mappings = [
            # Party Information Domain
            DomainMapping("applicant_name", "party.applicant.name", "applicant.name.full", "text", ["required"], True),
            DomainMapping("applicant_first_name", "party.applicant.name.first", "applicant.name.first", "text", ["required"], True),
            DomainMapping("applicant_last_name", "party.applicant.name.last", "applicant.name.last", "text", ["required"], True),
            DomainMapping("applicant_address", "party.applicant.address", "applicant.address.address", "text", ["required"], True),
            DomainMapping("applicant_city", "party.applicant.address.city", "applicant.address.city", "text", ["required"], True),
            DomainMapping("applicant_postal_code", "party.applicant.address.postal", "applicant.address.postal_code", "text", ["ontario_postal_code"], True),
            DomainMapping("applicant_phone", "party.applicant.contact.phone", "applicant.phone_number", "phone", [], False),
            DomainMapping("applicant_email", "party.applicant.contact.email", "applicant.email", "email", ["email_format"], False),
            
            # Respondent Information Domain
            DomainMapping("respondent_name", "party.respondent.name", "respondent.name.full", "text", ["required"], True),
            DomainMapping("respondent_first_name", "party.respondent.name.first", "respondent.name.first", "text", ["required"], True),
            DomainMapping("respondent_last_name", "party.respondent.name.last", "respondent.name.last", "text", ["required"], True),
            DomainMapping("respondent_address", "party.respondent.address", "respondent.address.address", "text", ["required"], True),
            DomainMapping("respondent_city", "party.respondent.address.city", "respondent.address.city", "text", ["required"], True),
            DomainMapping("respondent_postal_code", "party.respondent.address.postal", "respondent.address.postal_code", "text", ["ontario_postal_code"], True),
            DomainMapping("respondent_phone", "party.respondent.contact.phone", "respondent.phone_number", "phone", [], False),
            DomainMapping("respondent_email", "party.respondent.contact.email", "respondent.email", "email", ["email_format"], False),
            
            # Court Case Domain
            DomainMapping("court_name", "case.court.name", "case.court_name", "dropdown", [], True),
            DomainMapping("court_file_number", "case.file_number", "case.court_file_number", "text", ["court_file_format"], True),
            DomainMapping("court_address", "case.court.address", "case.court_address.address", "text", [], False),
            
            # Financial Domain
            DomainMapping("income", "financial.income.gross", "applicant_income.gross_annual", "currency", ["positive_number"], False),
            DomainMapping("assets", "financial.assets.total", "applicant_assets.total_value", "currency", ["positive_number"], False),
            
            # Children Domain
            DomainMapping("child_name", "children.name", "children[i].name.full", "text", ["required"], False),
            DomainMapping("child_birthdate", "children.birthdate", "children[i].birthdate", "date", ["valid_date"], False),
            DomainMapping("child_age", "children.age", "children[i].age", "integer", ["valid_age"], False),
            
            # Marriage/Relationship Domain
            DomainMapping("marriage_date", "relationship.marriage.date", "marriage_date", "date", ["valid_date"], False),
            DomainMapping("separation_date", "relationship.separation.date", "separation_date", "date", ["valid_date", "after_marriage"], False),
            
            # Claims Domain
            DomainMapping("claim_property", "claims.property", "claims.property_division", "yesno", [], False),
            DomainMapping("claim_support", "claims.support", "claims.spousal_support", "yesno", [], False),
            DomainMapping("claim_custody", "claims.custody", "claims.child_custody", "yesno", [], False),
        ]
        
        mappings.extend(standard_mappings)
        return mappings
    
    def _load_docassemble_mappings(self) -> List[DocassembleMapping]:
        """Load Docassemble mapping configuration"""
        mappings = []
        
        # Standard Docassemble mappings
        standard_mappings = [
            # Text questions
            DocassembleMapping(
                "party.applicant.name.first", 
                "applicant.name.first",
                "question",
                {"datatype": "text", "maxlength": 50},
                []
            ),
            DocassembleMapping(
                "party.applicant.name.last", 
                "applicant.name.last",
                "question",
                {"datatype": "text", "maxlength": 50},
                ["applicant.name.first"]
            ),
            
            # Address questions
            DocassembleMapping(
                "party.applicant.address", 
                "applicant.address.address",
                "question",
                {"datatype": "text", "maxlength": 100},
                []
            ),
            DocassembleMapping(
                "party.applicant.address.city", 
                "applicant.address.city",
                "question",
                {"datatype": "text", "maxlength": 50},
                ["applicant.address.address"]
            ),
            DocassembleMapping(
                "party.applicant.address.postal", 
                "applicant.address.postal_code",
                "question",
                {"datatype": "text", "validation": "ontario_postal_code"},
                ["applicant.address.city"]
            ),
            
            # Contact questions
            DocassembleMapping(
                "party.applicant.contact.phone", 
                "applicant.phone_number",
                "question",
                {"datatype": "text", "validation": "phone_number"},
                []
            ),
            DocassembleMapping(
                "party.applicant.contact.email", 
                "applicant.email",
                "question",
                {"datatype": "email"},
                []
            ),
            
            # Yes/No questions
            DocassembleMapping(
                "claims.property", 
                "claims.property_division",
                "yesno",
                {},
                []
            ),
            DocassembleMapping(
                "claims.support", 
                "claims.spousal_support",
                "yesno",
                {},
                []
            ),
            
            # Date questions
            DocassembleMapping(
                "relationship.marriage.date", 
                "marriage_date",
                "question",
                {"datatype": "date"},
                []
            ),
            DocassembleMapping(
                "relationship.separation.date", 
                "separation_date",
                "question",
                {"datatype": "date", "validation": "after_marriage_date"},
                ["marriage_date"]
            ),
            
            # Currency questions
            DocassembleMapping(
                "financial.income.gross", 
                "applicant_income.gross_annual",
                "question",
                {"datatype": "currency", "min": 0},
                []
            ),
        ]
        
        mappings.extend(standard_mappings)
        return mappings
    
    def generate_interview_from_parsed_form(self, form_number: str) -> Dict[str, Any]:
        """Generate interview map from parsed form data"""
        
        # Step 1: Load parsed form data
        parsed_data = self._load_parsed_form_data(form_number)
        if not parsed_data:
            raise ValueError(f"No parsed data found for form {form_number}")
        
        # Step 2: Apply domain mapping
        domain_concepts = self._apply_domain_mapping(parsed_data['fields'])
        
        # Step 3: Apply Docassemble mapping
        docassemble_structure = self._apply_docassemble_mapping(domain_concepts)
        
        # Step 4: Generate interview maps using Ontario framework
        interview_map = self._generate_interview_map(form_number, docassemble_structure)
        
        return interview_map
    
    def _load_parsed_form_data(self, form_number: str) -> Optional[Dict]:
        """Load parsed form data"""
        # Try different possible filenames
        possible_files = [
            f'form_{form_number}_improved.json',
            f'form_{form_number}_fields_enhanced.json',
            f'form_{form_number}_fields_complete.json'
        ]
        
        for filename in possible_files:
            filepath = self.parsed_forms_dir / filename
            if filepath.exists():
                with open(filepath, 'r') as f:
                    return json.load(f)
        
        return None
    
    def _apply_domain_mapping(self, form_fields: List[Dict]) -> Dict[str, Any]:
        """Apply domain mapping using consistent form keys to transform to domain concepts"""
        domain_concepts = {}
        
        # Create lookup for domain mappings using consistent keys
        mapping_lookup = {m.form_field_name: m for m in self.domain_mappings}
        
        for field in form_fields:
            original_field_name = field.get('field_name', '')
            
            # Get consistent key from registry
            consistent_key = None
            for key, field_key_obj in self.form_key_manager.registry.field_keys.items():
                if field_key_obj.original_field_name == original_field_name:
                    consistent_key = key
                    break
            
            # Use consistent key or original as fallback
            field_key_to_use = consistent_key or original_field_name
            
            # Try exact match with consistent key
            if field_key_to_use in mapping_lookup:
                mapping = mapping_lookup[field_key_to_use]
                domain_concepts[mapping.domain_concept] = {
                    'field_data': field,
                    'mapping': mapping,
                    'ontario_object_path': mapping.ontario_object_path,
                    'consistent_key': field_key_to_use,
                    'original_field_name': original_field_name
                }
                continue
            
            # Try pattern matching with consistent key
            matched = False
            for pattern, mapping in mapping_lookup.items():
                if self._field_matches_pattern(field_key_to_use, pattern):
                    domain_concepts[mapping.domain_concept] = {
                        'field_data': field,
                        'mapping': mapping,
                        'ontario_object_path': mapping.ontario_object_path,
                        'consistent_key': field_key_to_use,
                        'original_field_name': original_field_name
                    }
                    matched = True
                    break
            
            if not matched:
                # Unmatched field - create generic domain concept using consistent key
                domain_concepts[f'form_specific.{field_key_to_use}'] = {
                    'field_data': field,
                    'mapping': None,
                    'ontario_object_path': f'form_data.{field_key_to_use}',
                    'consistent_key': field_key_to_use,
                    'original_field_name': original_field_name
                }
        
        return domain_concepts
    
    def _apply_docassemble_mapping(self, domain_concepts: Dict[str, Any]) -> Dict[str, Any]:
        """Apply Docassemble mapping to transform domain concepts to DA structure"""
        docassemble_structure = {
            'objects': [],
            'questions': [],
            'code_blocks': [],
            'validation_rules': [],
            'dependencies': {}
        }
        
        # Create lookup for Docassemble mappings
        da_mapping_lookup = {m.domain_concept: m for m in self.docassemble_mappings}
        
        for domain_concept, concept_data in domain_concepts.items():
            if domain_concept in da_mapping_lookup:
                da_mapping = da_mapping_lookup[domain_concept]
                
                # Generate Docassemble question structure
                question_structure = self._generate_question_structure(
                    da_mapping, concept_data['field_data']
                )
                
                docassemble_structure['questions'].append(question_structure)
                
                # Add dependencies
                if da_mapping.dependencies:
                    docassemble_structure['dependencies'][da_mapping.docassemble_variable] = da_mapping.dependencies
                
            else:
                # Generate generic question for unmapped concepts
                generic_question = self._generate_generic_question(domain_concept, concept_data)
                docassemble_structure['questions'].append(generic_question)
        
        return docassemble_structure
    
    def _generate_interview_map(self, form_number: str, docassemble_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete interview map using Ontario framework"""
        
        # Use Ontario framework to structure the interview
        interview_map = {
            # Block 1: Metadata
            'metadata': {
                'title': f'Ontario Family Law Form {form_number}',
                'short_title': f'Form {form_number}',
                'description': f'Complete interview for Ontario Family Law Form {form_number}',
                'form_number': form_number,
                'generated': datetime.now().isoformat(),
                'generator': 'unified_map_based_generator',
                'uses_framework': 'ontario_family_law_framework'
            },
            
            # Block 2: Includes
            'include': [
                'docassemble.base:data/questions/basic-questions.yml'
            ],
            
            # Block 3: Objects (using Ontario framework)
            'objects': self._generate_objects_map(docassemble_structure),
            
            # Block 4: Mandatory code block
            'mandatory': True,
            'code': self._generate_mandatory_code_map(form_number, docassemble_structure),
            
            # Block 5: Questions (from Docassemble mapping)
            'questions': docassemble_structure['questions'],
            
            # Block 6: Validation code
            'validation': self._generate_validation_map(docassemble_structure),
            
            # Block 7: Final screens
            'final_screens': self._generate_final_screens_map(form_number)
        }
        
        return interview_map
    
    def _generate_objects_map(self, docassemble_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate objects map using Ontario framework"""
        objects_map = [
            {'applicant': 'Individual'},
            {'respondent': 'Individual'},
            {'case': 'DAObject'},
            {'claims': 'DAObject'}
        ]
        
        # Add conditional objects based on detected domain concepts
        if any('children' in str(q) for q in docassemble_structure['questions']):
            objects_map.append({'children': 'DAList.using(object_type=Individual)'})
        
        if any('financial' in str(q) for q in docassemble_structure['questions']):
            objects_map.extend([
                {'applicant_income': 'DAObject'},
                {'applicant_assets': 'DAObject'}
            ])
        
        return objects_map
    
    def _generate_mandatory_code_map(self, form_number: str, docassemble_structure: Dict[str, Any]) -> str:
        """Generate mandatory code flow"""
        code_lines = [
            f'# Ontario Family Law Form {form_number}',
            '# Generated using Ontario Family Law Framework',
            '',
            '# Initialize framework',
            'ontario_framework_ready',
            '',
            '# Collect required information'
        ]
        
        # Add variables based on questions
        for question in docassemble_structure['questions']:
            if 'variable' in question:
                code_lines.append(question['variable'])
        
        code_lines.extend([
            '',
            '# Validate all inputs',
            'all_inputs_valid',
            '',
            '# Generate final document',
            f'form_{form_number}_ready',
            'final_screen'
        ])
        
        return '\n'.join(code_lines)
    
    def _generate_validation_map(self, docassemble_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Generate validation rules map"""
        validation_map = {
            'code_blocks': []
        }
        
        # Ontario postal code validation
        validation_map['code_blocks'].append({
            'code': '''
def ontario_postal_code_valid(postal_code):
    """Validate Ontario postal code format"""
    import re
    if not postal_code:
        return False
    pattern = r'^[KLMNPRSTUV]\d[A-Z]\s?\d[A-Z]\d$'
    return bool(re.match(pattern, postal_code.upper().strip()))
            '''.strip()
        })
        
        # Court file number validation
        validation_map['code_blocks'].append({
            'code': '''
def court_file_number_valid(file_number):
    """Validate Ontario court file number format"""
    import re
    if not file_number:
        return False
    # Basic format: XX-YY-NNNNNN
    pattern = r'^\d{2}-\d{2}-\d{6,8}$'
    return bool(re.match(pattern, file_number))
            '''.strip()
        })
        
        return validation_map
    
    def _generate_final_screens_map(self, form_number: str) -> List[Dict[str, Any]]:
        """Generate final screens map"""
        return [
            {
                'event': 'final_screen',
                'question': f'Form {form_number} Complete',
                'subquestion': f'Your Ontario Family Law Form {form_number} has been prepared and is ready for review.',
                'buttons': [
                    {'Download PDF': f'${{ form_{form_number}_pdf.url_for() }}'},
                    {'Review Responses': 'review'},
                    {'Start Over': 'restart'}
                ]
            }
        ]
    
    def encode_interview_to_yaml(self, interview_map: Dict[str, Any]) -> str:
        """Encode interview map to YAML format"""
        
        # Configure YAML output
        yaml.add_representer(str, self._literal_presenter)
        
        # Convert to YAML blocks
        yaml_blocks = []
        
        # Metadata block
        yaml_blocks.append(yaml.dump({'metadata': interview_map['metadata']}, default_flow_style=False))
        
        # Include block
        if interview_map.get('include'):
            yaml_blocks.append(yaml.dump({'include': interview_map['include']}, default_flow_style=False))
        
        # Objects block
        if interview_map.get('objects'):
            yaml_blocks.append(yaml.dump({'objects': interview_map['objects']}, default_flow_style=False))
        
        # Mandatory block
        if interview_map.get('mandatory') and interview_map.get('code'):
            yaml_blocks.append(yaml.dump({
                'mandatory': interview_map['mandatory'],
                'code': interview_map['code']
            }, default_flow_style=False))
        
        # Question blocks
        for question in interview_map.get('questions', []):
            yaml_blocks.append(yaml.dump(question, default_flow_style=False))
        
        # Validation blocks
        if interview_map.get('validation', {}).get('code_blocks'):
            for code_block in interview_map['validation']['code_blocks']:
                yaml_blocks.append(yaml.dump(code_block, default_flow_style=False))
        
        # Final screens
        for screen in interview_map.get('final_screens', []):
            yaml_blocks.append(yaml.dump(screen, default_flow_style=False))
        
        # Join with YAML document separators
        return '\n---\n'.join(yaml_blocks)
    
    def _literal_presenter(self, dumper, data):
        """YAML presenter for multiline strings"""
        if isinstance(data, str) and '\n' in data:
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)
    
    def _generate_question_structure(self, da_mapping: DocassembleMapping, field_data: Dict) -> Dict[str, Any]:
        """Generate question structure from DA mapping"""
        question_struct = {
            'variable': da_mapping.docassemble_variable
        }
        
        # Set question text
        question_text = field_data.get('field_label') or field_data.get('field_name', '').replace('_', ' ').title()
        
        if da_mapping.question_type == 'yesno':
            question_struct['yesno'] = da_mapping.docassemble_variable
            question_struct['question'] = question_text
        else:
            question_struct['question'] = question_text
            question_struct['fields'] = [{
                da_mapping.docassemble_variable: da_mapping.field_properties
            }]
        
        return question_struct
    
    def _generate_generic_question(self, domain_concept: str, concept_data: Dict) -> Dict[str, Any]:
        """Generate generic question for unmapped domain concept"""
        field_data = concept_data['field_data']
        variable_name = concept_data['ontario_object_path']
        
        field_type = field_data.get('field_type', 'text')
        question_text = field_data.get('field_label') or field_data.get('field_name', '').replace('_', ' ').title()
        
        if field_type == 'checkbox':
            return {
                'yesno': variable_name,
                'question': question_text
            }
        else:
            return {
                'question': question_text,
                'fields': [{variable_name: 'text'}]
            }
    
    def _field_matches_pattern(self, field_name: str, pattern: str) -> bool:
        """Check if field name matches pattern"""
        import re
        return bool(re.search(pattern.lower(), field_name.lower()))
    
    def generate_all_interviews(self) -> Dict[str, Any]:
        """Generate interviews for all available parsed forms"""
        results = {
            'successful': [],
            'failed': [],
            'total_interviews': 0
        }
        
        # Get all parsed form files
        parsed_files = list(self.parsed_forms_dir.glob('form_*_improved.json'))
        
        for parsed_file in parsed_files:
            # Extract form number
            import re
            match = re.search(r'form_([^_]+)', parsed_file.stem)
            if not match:
                continue
            
            form_number = match.group(1)
            
            try:
                print(f"Generating interview for Form {form_number}...")
                
                # Generate interview map
                interview_map = self.generate_interview_from_parsed_form(form_number)
                
                # Encode to YAML
                yaml_content = self.encode_interview_to_yaml(interview_map)
                
                # Save to file
                output_file = self.output_dir / f'form_{form_number}_interview.yml'
                with open(output_file, 'w') as f:
                    f.write(yaml_content)
                
                results['successful'].append({
                    'form_number': form_number,
                    'output_file': str(output_file),
                    'questions_count': len(interview_map.get('questions', []))
                })
                
                print(f"✅ Generated Form {form_number} with {len(interview_map.get('questions', []))} questions")
                
            except Exception as e:
                print(f"❌ Failed to generate Form {form_number}: {e}")
                results['failed'].append({
                    'form_number': form_number,
                    'error': str(e)
                })
        
        results['total_interviews'] = len(results['successful'])
        return results


def main():
    """Run the unified map-based generator"""
    generator = UnifiedMapBasedGenerator()
    results = generator.generate_all_interviews()
    
    print(f"\n=== Generation Results ===")
    print(f"✅ Successful: {len(results['successful'])}")
    print(f"❌ Failed: {len(results['failed'])}")
    print(f"📝 Total interviews: {results['total_interviews']}")
    
    if results['failed']:
        print(f"\nFailed forms:")
        for failed in results['failed']:
            print(f"  - Form {failed['form_number']}: {failed['error']}")


if __name__ == "__main__":
    main()