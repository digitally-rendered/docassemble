#!/usr/bin/env python3
"""
Relationship-Aware YAML Generator for Docassemble
Generates structured interviews using entity and relationship information
"""

import yaml
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import re
from collections import defaultdict

class RelationshipAwareYAMLGenerator:
    """Generate YAML interviews with proper entity and field relationships"""
    
    def __init__(self, form_config, relationship_data: Dict = None):
        self.form_config = form_config
        self.relationship_data = relationship_data or {}
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
    def generate_complete_interview(self, reconciled_fields: Dict, entities: List, tables: List) -> str:
        """Generate interview with proper structure based on relationships"""
        
        blocks = []
        
        # 1. Metadata with relationship info
        blocks.append(self._generate_metadata())
        
        # 2. Include dependencies based on relationships
        blocks.append(self._generate_includes())
        
        # 3. Features
        blocks.append(self._generate_features())
        
        # 4. Objects based on detected entities
        blocks.append(self._generate_objects(entities))
        
        # 5. Code blocks for tables and calculations
        if tables:
            blocks.append(self._generate_table_code(tables, reconciled_fields))
        
        # 6. Mandatory block with proper flow
        blocks.append(self._generate_mandatory_block(entities))
        
        # 7. Introduction
        blocks.append(self._generate_introduction())
        
        # 8. Entity-based question blocks
        for entity in entities:
            entity_block = self._generate_entity_questions(entity, reconciled_fields)
            if entity_block:
                blocks.append(entity_block)
        
        # 9. Table questions
        for table in tables:
            table_block = self._generate_table_questions(table, reconciled_fields)
            if table_block:
                blocks.append(table_block)
        
        # 10. Review screen
        blocks.append(self._generate_review(entities, reconciled_fields))
        
        # 11. Completion screen
        blocks.append(self._generate_completion())
        
        # 12. Validation and helper code
        blocks.append(self._generate_validation_code())
        
        # Convert to YAML
        return self._blocks_to_yaml(blocks)
    
    def _generate_metadata(self) -> Dict:
        """Generate metadata with relationship information"""
        metadata = {
            'metadata': {
                'title': f"Ontario Family Law Form {self.form_config.form_number}",
                'short title': f"Form {self.form_config.form_number}",
                'description': f"{self.form_config.form_title}\n\nThis interview uses structured entities and relationships for better data management.\n\nGenerated: {self.timestamp}",
                'authors': [
                    {
                        'name': 'Ontario Family Law Forms System',
                        'organization': 'Relationship-Aware Processing'
                    }
                ],
                'form_number': str(self.form_config.form_number),
                'form_category': getattr(self.form_config, 'category', 'general'),
                'uses_entities': True,
                'uses_tables': True
            }
        }
        
        # Add relationship information if available
        if self.relationship_data:
            related_forms = self._get_related_forms()
            if related_forms:
                metadata['metadata']['related_forms'] = related_forms
        
        return metadata
    
    def _get_related_forms(self) -> List[str]:
        """Get list of related forms from relationship data"""
        related = []
        form_num = str(self.form_config.form_number)
        
        if 'relationships' in self.relationship_data:
            for rel in self.relationship_data['relationships']:
                if rel['source_form'] == form_num:
                    related.append(f"{rel['target_form']} ({rel['relationship_type']})")
                elif rel['target_form'] == form_num:
                    related.append(f"{rel['source_form']} ({rel['relationship_type']})")
        
        return related[:5]  # Limit to 5 for metadata
    
    def _generate_includes(self) -> Dict:
        """Generate includes based on form needs"""
        includes = ['docassemble.base:data/questions/basic-questions.yml']
        
        # Add financial calculations if needed
        if any(cat in str(self.form_config.form_number) for cat in ['13', '26']):
            includes.append('docassemble.base:data/questions/financial.yml')
        
        return {'include': includes}
    
    def _generate_features(self) -> Dict:
        """Generate features configuration"""
        return {
            'features': {
                'navigation': True,
                'progress bar': True,
                'progress bar method': 'stepped',
                'show progress bar percentage': True,
                'navigation back button': True,
                'question back button': True,
                'review button': True,
                'hide navbar': False,
                'hide standard menu': False,
                'table css class': 'table table-striped'
            }
        }
    
    def _generate_objects(self, entities: List) -> Dict:
        """Generate object definitions based on detected entities"""
        objects = []
        
        # Always have basic objects
        objects.append({'court_info': 'DAObject'})
        
        # Create objects for each entity type
        entity_types = defaultdict(int)
        for entity in entities:
            entity_types[entity.entity_type] += 1
        
        # Person entities
        if entity_types.get('person'):
            # Check for specific roles
            has_applicant = any('applicant' in e.entity_name.lower() for e in entities)
            has_respondent = any('respondent' in e.entity_name.lower() for e in entities)
            
            if has_applicant:
                objects.append({'applicant': 'Individual'})
            if has_respondent:
                objects.append({'respondent': 'Individual'})
            
            # Children if mentioned
            if any('child' in e.entity_name.lower() for e in entities):
                objects.append({'children': 'DAList.using(object_type=Individual)'})
        
        # Property entities
        if entity_types.get('property'):
            objects.append({'assets': 'DAList.using(object_type=DAObject)'})
            objects.append({'real_estate': 'DAList.using(object_type=DAObject)'})
            objects.append({'vehicles': 'DAList.using(object_type=DAObject)'})
        
        # Financial entities
        if entity_types.get('financial'):
            objects.append({'income_sources': 'DAList.using(object_type=DAObject)'})
            objects.append({'expenses': 'DAList.using(object_type=DAObject)'})
            objects.append({'debts': 'DAList.using(object_type=DAObject)'})
        
        # Table row entities
        if entity_types.get('table_row'):
            objects.append({'table_items': 'DAList.using(object_type=DAObject)'})
        
        return {'objects': objects}
    
    def _generate_table_code(self, tables: List, fields: Dict) -> Dict:
        """Generate code for table handling"""
        code_lines = [
            "# Table data initialization and calculations"
        ]
        
        for table in tables:
            if table.table_type == 'list':
                code_lines.append(f"""
def init_{table.table_id}_data():
    '''Initialize {table.table_name} data'''
    if not hasattr(table_items, 'gathered'):
        table_items.clear()
        table_items.gathered = True
    return table_items
""")
            elif table.table_type == 'matrix' and 'total' in table.table_name.lower():
                # Generate calculation code for totals
                code_lines.append(f"""
def calculate_{table.table_id}_totals():
    '''Calculate totals for {table.table_name}'''
    total = 0
    for item in table_items:
        if hasattr(item, 'amount'):
            total += float(item.amount or 0)
    return total
""")
        
        return {
            'code': '\n'.join(code_lines)
        }
    
    def _generate_mandatory_block(self, entities: List) -> Dict:
        """Generate mandatory execution block"""
        steps = ['form_intro_seen']
        
        # Add entity collection steps
        for entity in entities:
            if entity.entity_type == 'person':
                if 'applicant' in entity.entity_name.lower():
                    steps.append('applicant.name.first')
                    steps.append('applicant.name.last')
                elif 'respondent' in entity.entity_name.lower():
                    steps.append('respondent.name.first')
                    steps.append('respondent.name.last')
            elif entity.cardinality == 'multiple':
                steps.append(f'{entity.entity_id}_complete')
        
        steps.append('review_answers')
        steps.append('form_complete')
        
        return {
            'mandatory': True,
            'code': '\n'.join(steps)
        }
    
    def _generate_introduction(self) -> Dict:
        """Generate introduction screen"""
        return {
            'question': f"Form {self.form_config.form_number} - {self.form_config.form_title}",
            'subquestion': f"""This interview will help you complete the official Ontario family law form.
            
Based on the form structure, you will be asked about:
- Personal information for parties involved
- Court case details
- Financial information (if applicable)
- Supporting documentation

The interview is organized by topic to make it easier to complete.""",
            'continue button field': 'form_intro_seen',
            'continue button label': 'Start Interview'
        }
    
    def _generate_entity_questions(self, entity, fields: Dict) -> Optional[Dict]:
        """Generate questions for an entity"""
        entity_fields = [fields[fid] for fid in entity.fields if fid in fields]
        
        if not entity_fields:
            return None
        
        # Group fields by type for better UX
        text_fields = [f for f in entity_fields if f.field_type == 'text']
        date_fields = [f for f in entity_fields if f.field_type == 'date']
        currency_fields = [f for f in entity_fields if f.field_type == 'currency']
        other_fields = [f for f in entity_fields if f.field_type not in ['text', 'date', 'currency']]
        
        # Create field definitions
        field_defs = []
        
        # Add fields in logical order
        for field in text_fields[:5] + date_fields[:3] + currency_fields[:5] + other_fields[:5]:
            field_def = {
                'label': self._clean_label(field.field_label),
                'field': self._get_field_variable(entity, field)
            }
            
            if field.field_type != 'text':
                field_def['datatype'] = field.field_type
            
            if field.required:
                field_def['required'] = True
            
            if field.field_type == 'dropdown' and field.sources:
                # Extract options from metadata
                for source in field.sources:
                    if source.metadata.get('options'):
                        field_def['choices'] = source.metadata['options']
                        break
            
            field_defs.append(field_def)
        
        return {
            'question': f"{entity.entity_name} Information",
            'fields': field_defs
        }
    
    def _generate_table_questions(self, table, fields: Dict) -> Optional[Dict]:
        """Generate questions for table data"""
        if table.table_type != 'list':
            return None  # Only handle list tables as repeating questions
        
        table_fields = [fields[fid] for fid in table.fields if fid in fields]
        
        if not table_fields:
            return None
        
        # Get fields from first row as template
        row_fields = [f for f in table_fields if f.table_row == 1][:5]
        
        if not row_fields:
            return None
        
        field_defs = []
        for field in row_fields:
            field_def = {
                'label': self._clean_label(field.field_label),
                'field': f"table_items[i].{self._sanitize_variable(field.field_name)}"
            }
            
            if field.field_type != 'text':
                field_def['datatype'] = field.field_type
            
            field_defs.append(field_def)
        
        return {
            'question': f"Enter {table.table_name} Item ${{i + 1}}",
            'fields': field_defs,
            'continue button label': 'Continue'
        }
    
    def _generate_review(self, entities: List, fields: Dict) -> Dict:
        """Generate review screen"""
        review_items = [{'note': '### Review Your Information'}]
        
        # Add review items for main entities
        for entity in entities[:10]:  # Limit to prevent huge review screens
            entity_fields = [fields[fid] for fid in entity.fields if fid in fields][:5]
            
            for field in entity_fields:
                review_items.append({
                    'label': self._clean_label(field.field_label),
                    'field': self._get_field_variable(entity, field),
                    'edit': True
                })
        
        return {
            'review': review_items,
            'question': 'Review Your Answers',
            'subquestion': 'Please review your information. Click any item to edit.',
            'continue button field': 'review_answers'
        }
    
    def _generate_completion(self) -> Dict:
        """Generate completion screen"""
        return {
            'event': 'form_complete',
            'question': f'Form {self.form_config.form_number} Complete',
            'subquestion': """Your form is ready.

**Next Steps:**
1. Download your completed form
2. Review all information carefully  
3. Print and sign where required
4. File with the appropriate court""",
            'buttons': [
                {'Exit': 'exit'},
                {'Start Over': 'restart'}
            ]
        }
    
    def _generate_validation_code(self) -> Dict:
        """Generate validation functions"""
        return {
            'code': '''# Validation functions
def validate_sin(sin):
    """Validate Canadian SIN"""
    import re
    if not sin:
        return True
    sin = re.sub(r'[^0-9]', '', sin)
    return len(sin) == 9

def validate_ontario_postal_code(postal_code):
    """Validate Ontario postal code"""
    import re
    if not postal_code:
        return True
    pattern = r'^[KLMNP]\\d[A-Z]\\s?\\d[A-Z]\\d$'
    return bool(re.match(pattern, postal_code.upper()))

def format_currency(amount):
    """Format currency values"""
    try:
        return f"${float(amount):,.2f}"
    except:
        return "$0.00"

def calculate_total(items, field_name='amount'):
    """Calculate total from list of items"""
    total = 0
    for item in items:
        if hasattr(item, field_name):
            total += float(getattr(item, field_name) or 0)
    return total
'''
        }
    
    def _clean_label(self, label: str) -> str:
        """Clean up field labels"""
        # Remove duplicate text
        parts = label.split()
        seen = set()
        clean_parts = []
        for part in parts:
            if part.lower() not in seen:
                clean_parts.append(part)
                seen.add(part.lower())
        
        label = ' '.join(clean_parts[:10])  # Limit length
        
        # Ensure proper capitalization
        if label and not label[0].isupper():
            label = label.capitalize()
        
        return label
    
    def _get_field_variable(self, entity, field) -> str:
        """Get the variable name for a field within an entity"""
        if entity.entity_type == 'person':
            if 'applicant' in entity.entity_name.lower():
                return f"applicant.{self._sanitize_variable(field.field_name)}"
            elif 'respondent' in entity.entity_name.lower():
                return f"respondent.{self._sanitize_variable(field.field_name)}"
            else:
                return self._sanitize_variable(field.field_name)
        elif entity.cardinality == 'multiple':
            return f"{entity.entity_id}[i].{self._sanitize_variable(field.field_name)}"
        else:
            return self._sanitize_variable(field.field_name)
    
    def _sanitize_variable(self, text: str) -> str:
        """Create valid variable name"""
        import re
        name = re.sub(r'[^a-zA-Z0-9_]', '_', text)
        name = re.sub(r'_+', '_', name)
        name = name.strip('_').lower()[:30]
        
        # Ensure it starts with a letter
        if name and not name[0].isalpha():
            name = 'field_' + name
        
        return name or "field"
    
    def _blocks_to_yaml(self, blocks: List[Dict]) -> str:
        """Convert blocks to properly formatted YAML"""
        yaml_parts = []
        
        for block in blocks:
            yaml_part = yaml.dump(
                block,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                width=1000
            ).strip()
            yaml_parts.append(yaml_part)
        
        # Join blocks with single line breaks (no document separators!)
        return '---\n' + '\n'.join(yaml_parts) + '\n'

def generate_relationship_aware_interviews():
    """Generate interviews using relationship data"""
    from pathlib import Path
    import json
    from automated_form_processor import FormRegistry
    
    # Load relationship analysis
    with open('workflow_output/form_relationship_analysis.json', 'r') as f:
        relationship_data = json.load(f)
    
    output_dir = Path('workflow_output/relationship_aware_interviews')
    output_dir.mkdir(exist_ok=True)
    
    generated = []
    
    # Generate for top forms with most entities and relationships
    priority_forms = ['13', '13.1', '26', '8', '10', '15', '36']
    
    for form_num in priority_forms:
        if form_num not in relationship_data['forms']:
            continue
        
        form_data = relationship_data['forms'][form_num]
        
        # Get form config
        form_config = FormRegistry.get_form(form_num)
        if not form_config:
            from automated_form_processor import FormConfiguration
            form_config = FormConfiguration(
                form_number=form_num,
                form_title=f"Form {form_num}",
                form_type="general",
                category="general",
                url="",
                filename=""
            )
        
        # Load parsed field data
        field_file = Path(f'workflow_output/enhanced_parsed_forms/form_{form_num}_fields.json')
        if not field_file.exists():
            continue
        
        with open(field_file, 'r') as f:
            raw_fields = json.load(f)
        
        # Create mock reconciled fields (in real implementation, use actual reconciled data)
        reconciled_fields = {}
        for i, field_data in enumerate(raw_fields[:50]):  # Limit for demo
            reconciled_fields[f"field_{i}"] = type('Field', (), field_data)()
        
        # Create mock entities
        entities = []
        for entity_data in form_data.get('entities', []):
            entity = type('Entity', (), entity_data)()
            entities.append(entity)
        
        # Create mock tables
        tables = []
        for table_data in form_data.get('tables', []):
            table = type('Table', (), table_data)()
            tables.append(table)
        
        # Generate YAML
        generator = RelationshipAwareYAMLGenerator(form_config, relationship_data)
        yaml_content = generator.generate_complete_interview(reconciled_fields, entities, tables)
        
        # Save YAML
        output_file = output_dir / f"form_{form_num}_interview.yml"
        with open(output_file, 'w') as f:
            f.write(yaml_content)
        
        generated.append(form_num)
        print(f"Generated relationship-aware interview for Form {form_num}")
    
    print(f"\nGenerated {len(generated)} relationship-aware interviews in {output_dir}")
    return generated

if __name__ == "__main__":
    generate_relationship_aware_interviews()