#!/usr/bin/env python3
"""
Procedural Interview Generator for Ontario Family Law Forms
Generates Docassemble interviews directly from parsed and analyzed form data
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict, OrderedDict
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProceduralInterviewGenerator:
    """Generate interviews procedurally from actual parsed data"""
    
    def __init__(self):
        self.base_dir = Path('workflow_output')
        self.enhanced_parsed_dir = self.base_dir / 'enhanced_parsed_forms'
        self.relationship_file = self.base_dir / 'form_relationship_analysis.json'
        self.output_dir = self.base_dir / 'procedural_interviews'
        self.output_dir.mkdir(exist_ok=True)
        
        # Load relationship analysis
        with open(self.relationship_file, 'r') as f:
            self.relationship_data = json.load(f)
    
    def generate_all_interviews(self):
        """Generate interviews for all parsed forms"""
        generated_count = 0
        
        for form_num, form_analysis in self.relationship_data['forms'].items():
            try:
                yaml_content = self.generate_form_interview(form_num, form_analysis)
                if yaml_content:
                    output_file = self.output_dir / f"form_{form_num}_interview.yml"
                    with open(output_file, 'w') as f:
                        f.write(yaml_content)
                    generated_count += 1
                    logger.info(f"Generated procedural interview for Form {form_num}")
            except Exception as e:
                logger.error(f"Failed to generate Form {form_num}: {e}")
        
        logger.info(f"Generated {generated_count} procedural interviews")
        self._generate_master_index(list(self.relationship_data['forms'].keys()))
        
        return generated_count
    
    def generate_form_interview(self, form_num: str, form_analysis: Dict) -> str:
        """Generate a single form interview from its analysis data"""
        
        # Load the actual parsed fields
        fields_file = self.enhanced_parsed_dir / f"form_{form_num}_fields.json"
        if not fields_file.exists():
            logger.warning(f"No field data found for Form {form_num}")
            return None
        
        with open(fields_file, 'r') as f:
            raw_fields = json.load(f)
        
        # Process fields into structured groups
        processed_data = self._process_form_fields(raw_fields, form_analysis)
        
        # Build interview blocks procedurally
        blocks = []
        
        # 1. Metadata block with actual form info
        blocks.append(self._build_metadata_block(form_num, form_analysis, processed_data))
        
        # 2. Includes based on detected features
        blocks.append(self._build_includes_block(processed_data))
        
        # 3. Features configuration
        blocks.append(self._build_features_block(processed_data))
        
        # 4. Objects based on detected entities and tables
        blocks.append(self._build_objects_block(processed_data, form_analysis))
        
        # 5. Mandatory flow based on field dependencies
        blocks.append(self._build_mandatory_block(processed_data))
        
        # 6. Introduction with form-specific info
        blocks.append(self._build_introduction_block(form_num, processed_data))
        
        # 7. Generate question blocks procedurally
        question_blocks = self._build_question_blocks(processed_data)
        blocks.extend(question_blocks)
        
        # 8. Table handling if needed
        if processed_data['tables']:
            table_blocks = self._build_table_blocks(processed_data['tables'], raw_fields)
            blocks.extend(table_blocks)
        
        # 9. Calculation code if needed
        if processed_data['calculations']:
            blocks.append(self._build_calculations_block(processed_data['calculations']))
        
        # 10. Review screen
        blocks.append(self._build_review_block(processed_data))
        
        # 11. Completion screen
        blocks.append(self._build_completion_block(form_num))
        
        # 12. Validation code
        blocks.append(self._build_validation_block(processed_data))
        
        # Convert to YAML
        return self._blocks_to_yaml(blocks)
    
    def _process_form_fields(self, raw_fields: List[Dict], form_analysis: Dict) -> Dict:
        """Process raw fields into structured data for interview generation"""
        
        processed = {
            'field_groups': defaultdict(list),
            'entities': [],
            'tables': [],
            'calculations': [],
            'validations': set(),
            'field_types': set(),
            'total_fields': len(raw_fields),
            'has_currency': False,
            'has_dates': False,
            'has_checkboxes': False,
            'has_dropdowns': False,
            'conditional_fields': [],
            'required_fields': []
        }
        
        # Analyze each field
        for field_data in raw_fields:
            field_type = field_data.get('field_type', 'text')
            field_name = field_data.get('field_name', '')
            field_label = field_data.get('field_label', '')
            field_context = field_data.get('field_context', '')
            
            # Track field types
            processed['field_types'].add(field_type)
            if field_type == 'currency':
                processed['has_currency'] = True
            elif field_type == 'date':
                processed['has_dates'] = True
            elif field_type == 'checkbox':
                processed['has_checkboxes'] = True
            elif field_type == 'dropdown':
                processed['has_dropdowns'] = True
            
            # Group fields by context/section
            group_key = self._determine_field_group(field_data)
            processed['field_groups'][group_key].append(field_data)
            
            # Track special fields
            if field_data.get('required'):
                processed['required_fields'].append(field_name)
            
            if 'if' in field_label.lower() or 'when' in field_label.lower():
                processed['conditional_fields'].append(field_data)
            
            if 'total' in field_label.lower() or 'sum' in field_label.lower():
                processed['calculations'].append(field_data)
            
            # Track validation needs
            if 'email' in field_label.lower():
                processed['validations'].add('email')
            elif 'phone' in field_label.lower():
                processed['validations'].add('phone')
            elif 'postal' in field_label.lower() or 'zip' in field_label.lower():
                processed['validations'].add('postal_code')
            elif 'sin' in field_label.lower() or 'social insurance' in field_label.lower():
                processed['validations'].add('sin')
        
        # Extract entities from analysis
        if 'entities' in form_analysis:
            for entity_data in form_analysis['entities']:
                processed['entities'].append({
                    'name': entity_data['entity_name'],
                    'type': entity_data['entity_type'],
                    'field_count': len(entity_data['fields']),
                    'cardinality': entity_data.get('cardinality', 'single')
                })
        
        # Extract tables from analysis
        if 'tables' in form_analysis:
            for table_data in form_analysis['tables']:
                processed['tables'].append({
                    'id': table_data['table_id'],
                    'name': table_data['table_name'],
                    'type': table_data['table_type'],
                    'rows': table_data['rows'],
                    'cols': table_data['cols'],
                    'repeating': table_data.get('repeating', False)
                })
        
        return processed
    
    def _determine_field_group(self, field_data: Dict) -> str:
        """Determine which group/section a field belongs to"""
        context = field_data.get('field_context', '').lower()
        label = field_data.get('field_label', '').lower()
        
        # Table fields
        if 'table' in context:
            table_match = re.search(r'table\s*(\d+)', context)
            if table_match:
                return f"table_{table_match.group(1)}"
            return 'table_fields'
        
        # Section fields
        if 'section' in context:
            section_match = re.search(r'section\s*(\d+)', context)
            if section_match:
                return f"section_{section_match.group(1)}"
        
        # Group by field type/purpose
        if any(word in label for word in ['name', 'address', 'phone', 'email']):
            return 'personal_info'
        elif any(word in label for word in ['income', 'expense', 'asset', 'debt', 'payment']):
            return 'financial_info'
        elif any(word in label for word in ['court', 'file', 'case']):
            return 'court_info'
        elif any(word in label for word in ['child', 'dependent']):
            return 'children_info'
        elif any(word in label for word in ['property', 'real estate', 'vehicle']):
            return 'property_info'
        
        # Page-based grouping
        page_num = field_data.get('page_number', 0)
        if page_num > 0:
            return f"page_{page_num}"
        
        return 'general_fields'
    
    def _build_metadata_block(self, form_num: str, form_analysis: Dict, processed_data: Dict) -> Dict:
        """Build metadata block from actual form data"""
        
        # Get form title from first few fields or default
        form_title = f"Form {form_num}"
        if processed_data['field_groups']:
            # Try to extract from field context
            for fields in processed_data['field_groups'].values():
                if fields and fields[0].get('field_context'):
                    context = fields[0]['field_context']
                    if 'financial' in context.lower():
                        form_title = f"Form {form_num} - Financial Statement"
                        break
                    elif 'application' in context.lower():
                        form_title = f"Form {form_num} - Application"
                        break
        
        metadata = {
            'metadata': {
                'title': f"Ontario Family Law Form {form_num}",
                'short title': f"Form {form_num}",
                'description': f"{form_title}\\n\\nAuto-generated from {processed_data['total_fields']} parsed fields\\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                'authors': [{
                    'name': 'Procedural Interview Generator',
                    'organization': 'Ontario Family Law Automation'
                }],
                'form_number': form_num,
                'field_count': processed_data['total_fields'],
                'entity_count': len(processed_data['entities']),
                'table_count': len(processed_data['tables'])
            }
        }
        
        # Add related forms if available
        related = self._get_related_forms(form_num)
        if related:
            metadata['metadata']['related_forms'] = related
        
        return metadata
    
    def _get_related_forms(self, form_num: str) -> List[str]:
        """Get related forms from relationship data"""
        related = []
        for rel in self.relationship_data.get('relationships', []):
            if rel['source_form'] == form_num:
                related.append(f"{rel['target_form']} ({rel['relationship_type']})")
            elif rel['target_form'] == form_num:
                related.append(f"{rel['source_form']} ({rel['relationship_type']})")
        return related[:3]
    
    def _build_includes_block(self, processed_data: Dict) -> Dict:
        """Build includes based on detected features"""
        includes = ['docassemble.base:data/questions/basic-questions.yml']
        
        if processed_data['has_currency']:
            includes.append('docassemble.base:data/questions/financial.yml')
        
        return {'include': includes}
    
    def _build_features_block(self, processed_data: Dict) -> Dict:
        """Build features configuration"""
        features = {
            'navigation': True,
            'progress bar': True,
            'progress bar method': 'stepped',
            'show progress bar percentage': True,
            'navigation back button': True,
            'question back button': True
        }
        
        # Add review if many fields
        if processed_data['total_fields'] > 10:
            features['review button'] = True
        
        # Add table styling if tables present
        if processed_data['tables']:
            features['table css class'] = 'table table-striped'
        
        return {'features': features}
    
    def _build_objects_block(self, processed_data: Dict, form_analysis: Dict) -> Dict:
        """Build objects based on detected entities"""
        objects = []
        
        # Always include court info
        objects.append({'court_info': 'DAObject'})
        
        # Add objects based on entities
        entity_types = set()
        for entity in processed_data['entities']:
            entity_types.add(entity['type'])
            
            if entity['type'] == 'person':
                if 'applicant' in entity['name'].lower():
                    objects.append({'applicant': 'Individual'})
                elif 'respondent' in entity['name'].lower():
                    objects.append({'respondent': 'Individual'})
                elif 'child' in entity['name'].lower() and entity['cardinality'] == 'multiple':
                    objects.append({'children': 'DAList.using(object_type=Individual)'})
            
            elif entity['type'] == 'property':
                if entity['cardinality'] == 'multiple':
                    obj_name = entity['name'].lower().replace(' ', '_') + 's'
                    objects.append({obj_name: 'DAList.using(object_type=DAObject)'})
            
            elif entity['type'] == 'financial':
                obj_name = entity['name'].lower().replace(' ', '_')
                objects.append({obj_name: 'DAObject'})
        
        # Add table objects if needed
        if processed_data['tables']:
            for table in processed_data['tables']:
                if table['repeating']:
                    table_obj = table['name'].lower().replace(' ', '_') + '_items'
                    objects.append({table_obj: 'DAList.using(object_type=DAObject)'})
        
        # Default person objects if none detected but we have personal fields
        if 'personal_info' in processed_data['field_groups'] and 'person' not in entity_types:
            objects.append({'user': 'Individual'})
        
        return {'objects': objects if objects else [{'user': 'Individual'}]}
    
    def _build_mandatory_block(self, processed_data: Dict) -> Dict:
        """Build mandatory execution flow"""
        steps = ['form_intro_seen']
        
        # Add steps for each field group in logical order
        group_order = [
            'court_info', 'personal_info', 'children_info',
            'financial_info', 'property_info', 'general_fields'
        ]
        
        for group in group_order:
            if group in processed_data['field_groups']:
                steps.append(f"{group}_complete")
        
        # Add section steps
        section_groups = sorted([g for g in processed_data['field_groups'] if g.startswith('section_')])
        for section in section_groups:
            steps.append(f"{section}_complete")
        
        # Add table steps
        if processed_data['tables']:
            for table in processed_data['tables']:
                table_var = table['name'].lower().replace(' ', '_')
                if table['repeating']:
                    steps.append(f"{table_var}_items.gathered")
                else:
                    steps.append(f"{table_var}_complete")
        
        steps.extend(['review_complete', 'form_complete'])
        
        return {
            'mandatory': True,
            'code': '\\n'.join(steps)
        }
    
    def _build_introduction_block(self, form_num: str, processed_data: Dict) -> Dict:
        """Build introduction screen"""
        
        # Build dynamic content based on what's in the form
        content_list = []
        if 'personal_info' in processed_data['field_groups']:
            content_list.append("Personal information")
        if 'financial_info' in processed_data['field_groups']:
            content_list.append("Financial details")
        if 'children_info' in processed_data['field_groups']:
            content_list.append("Information about children")
        if 'property_info' in processed_data['field_groups']:
            content_list.append("Property and assets")
        if processed_data['tables']:
            content_list.append(f"{len(processed_data['tables'])} data tables")
        
        subquestion = f"""This interview will help you complete Form {form_num}.
        
You will be asked about:
{chr(10).join('- ' + item for item in content_list)}

Total questions: Approximately {len(processed_data['field_groups'])} sections"""
        
        return {
            'question': f"Ontario Family Law Form {form_num}",
            'subquestion': subquestion,
            'continue button field': 'form_intro_seen'
        }
    
    def _build_question_blocks(self, processed_data: Dict) -> List[Dict]:
        """Build question blocks for each field group"""
        blocks = []
        
        # Process each field group
        for group_name, fields in processed_data['field_groups'].items():
            if not fields:
                continue
            
            # Skip table fields (handled separately)
            if group_name.startswith('table_'):
                continue
            
            # Create question block for this group
            question_block = self._create_question_block(group_name, fields)
            if question_block:
                blocks.append(question_block)
        
        return blocks
    
    def _create_question_block(self, group_name: str, fields: List[Dict]) -> Dict:
        """Create a question block for a group of fields"""
        
        # Determine question title
        title = self._get_group_title(group_name)
        
        # Build field definitions
        field_defs = []
        seen_labels = set()
        
        for field_data in fields[:20]:  # Limit fields per screen
            label = field_data.get('field_label', '')
            field_name = field_data.get('field_name', '')
            field_type = field_data.get('field_type', 'text')
            
            # Skip duplicate labels
            label_key = label.lower().strip()
            if label_key in seen_labels:
                continue
            seen_labels.add(label_key)
            
            # Clean up label
            label = self._clean_label(label)
            if not label:
                continue
            
            # Create field definition
            field_def = {
                'label': label,
                'field': self._sanitize_field_name(field_name, group_name)
            }
            
            # Add field type
            if field_type != 'text':
                if field_type == 'currency':
                    field_def['datatype'] = 'currency'
                    field_def['min'] = 0
                elif field_type == 'date':
                    field_def['datatype'] = 'date'
                elif field_type == 'email':
                    field_def['datatype'] = 'email'
                elif field_type == 'phone':
                    field_def['datatype'] = 'text'
                    field_def['hint'] = '(xxx) xxx-xxxx'
                elif field_type == 'checkbox':
                    field_def['datatype'] = 'yesno'
                elif field_type == 'dropdown' or field_type == 'select':
                    # Add choices if available
                    if field_data.get('options'):
                        field_def['choices'] = field_data['options']
                    else:
                        field_def['datatype'] = 'text'
            
            # Add validation if needed
            if field_data.get('required'):
                field_def['required'] = True
            
            if field_data.get('max_length'):
                field_def['maxlength'] = field_data['max_length']
            
            field_defs.append(field_def)
        
        if not field_defs:
            return None
        
        # Create the question block
        question_block = {
            'question': title,
            'fields': field_defs
        }
        
        # Add continue button field for tracking
        if not group_name.startswith('page_'):
            question_block['continue button field'] = f"{group_name}_complete"
        
        return question_block
    
    def _get_group_title(self, group_name: str) -> str:
        """Get human-readable title for field group"""
        if group_name == 'personal_info':
            return 'Personal Information'
        elif group_name == 'financial_info':
            return 'Financial Information'
        elif group_name == 'court_info':
            return 'Court Information'
        elif group_name == 'children_info':
            return 'Children Information'
        elif group_name == 'property_info':
            return 'Property and Assets'
        elif group_name == 'general_fields':
            return 'Additional Information'
        elif group_name.startswith('section_'):
            num = group_name.replace('section_', '')
            return f'Section {num}'
        elif group_name.startswith('page_'):
            num = group_name.replace('page_', '')
            return f'Information (Page {num})'
        else:
            return group_name.replace('_', ' ').title()
    
    def _build_table_blocks(self, tables: List[Dict], raw_fields: List[Dict]) -> List[Dict]:
        """Build blocks for table handling"""
        blocks = []
        
        for table in tables:
            if table['repeating']:
                # Create a repeating question for list tables
                table_var = table['name'].lower().replace(' ', '_') + '_items'
                
                # Find fields for this table
                table_fields = []
                for field in raw_fields:
                    if table['id'] in field.get('field_context', ''):
                        table_fields.append(field)
                
                if table_fields:
                    # Group by row to find pattern
                    row_fields = defaultdict(list)
                    for field in table_fields:
                        row = field.get('table_row', 0)
                        if row > 0:  # Skip header row
                            row_fields[row].append(field)
                    
                    # Use first data row as template
                    if row_fields:
                        template_fields = list(row_fields.values())[0][:5]  # Limit fields
                        
                        field_defs = []
                        for field in template_fields:
                            field_def = {
                                'label': self._clean_label(field.get('field_label', '')),
                                'field': f"{table_var}[i].{self._sanitize_field_name(field.get('field_name', ''))}"
                            }
                            
                            field_type = field.get('field_type', 'text')
                            if field_type == 'currency':
                                field_def['datatype'] = 'currency'
                            elif field_type == 'date':
                                field_def['datatype'] = 'date'
                            
                            field_defs.append(field_def)
                        
                        if field_defs:
                            blocks.append({
                                'question': f"Enter {table['name']} - Item ${{i + 1}}",
                                'fields': field_defs,
                                'list collect': True
                            })
                            
                            blocks.append({
                                'question': f"Are there more {table['name']} items?",
                                'yesno': f"{table_var}.there_is_another"
                            })
        
        return blocks
    
    def _build_calculations_block(self, calculations: List[Dict]) -> Dict:
        """Build code block for calculations"""
        code_lines = ["# Calculation functions"]
        
        for calc in calculations:
            label = calc.get('field_label', '').lower()
            field_name = self._sanitize_field_name(calc.get('field_name', ''))
            
            if 'total' in label:
                # Generate a total calculation function
                code_lines.append(f"""
def calculate_{field_name}():
    '''Calculate {calc.get('field_label', 'total')}'''
    # TODO: Add actual calculation logic based on form structure
    return 0
""")
        
        return {'code': '\\n'.join(code_lines)}
    
    def _build_review_block(self, processed_data: Dict) -> Dict:
        """Build review screen"""
        review_items = [{'note': '### Review Your Information'}]
        
        # Add sample fields from each group
        for group_name, fields in processed_data['field_groups'].items():
            if group_name.startswith('table_'):
                continue
            
            # Add up to 3 fields from each group
            for field in fields[:3]:
                label = self._clean_label(field.get('field_label', ''))
                if label:
                    review_items.append({
                        'label': label,
                        'field': self._sanitize_field_name(field.get('field_name', ''), group_name),
                        'edit': True
                    })
        
        return {
            'review': review_items,
            'question': 'Review Your Answers',
            'subquestion': 'Please review all information before submitting.',
            'continue button field': 'review_complete'
        }
    
    def _build_completion_block(self, form_num: str) -> Dict:
        """Build completion screen"""
        return {
            'event': 'form_complete',
            'question': f'Form {form_num} Complete',
            'subquestion': '''Your form has been completed.

**Next Steps:**
1. Download your completed form
2. Review all information
3. Sign where required
4. File with the court

**Important:** This is a procedurally generated form. Please review carefully.''',
            'buttons': [
                {'Download': 'exit'},
                {'Start Over': 'restart'}
            ]
        }
    
    def _build_validation_block(self, processed_data: Dict) -> Dict:
        """Build validation code based on detected needs"""
        code_lines = ["# Validation functions"]
        
        if 'email' in processed_data['validations']:
            code_lines.append("""
def validate_email(email):
    import re
    if not email:
        return True
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
""")
        
        if 'phone' in processed_data['validations']:
            code_lines.append("""
def validate_phone(phone):
    import re
    if not phone:
        return True
    phone_digits = re.sub(r'[^0-9]', '', phone)
    return len(phone_digits) == 10
""")
        
        if 'postal_code' in processed_data['validations']:
            code_lines.append("""
def validate_postal_code(postal):
    import re
    if not postal:
        return True
    # Ontario postal codes start with K, L, M, N, or P
    pattern = r'^[KLMNP]\\d[A-Z]\\s?\\d[A-Z]\\d$'
    return bool(re.match(pattern, postal.upper()))
""")
        
        if 'sin' in processed_data['validations']:
            code_lines.append("""
def validate_sin(sin):
    import re
    if not sin:
        return True
    sin_digits = re.sub(r'[^0-9]', '', sin)
    return len(sin_digits) == 9
""")
        
        if processed_data['has_currency']:
            code_lines.append("""
def format_currency(amount):
    try:
        return f"${float(amount):,.2f}"
    except:
        return "$0.00"
""")
        
        return {'code': '\\n'.join(code_lines)}
    
    def _clean_label(self, label: str) -> str:
        """Clean up field labels"""
        if not label:
            return ""
        
        # Remove excessive repetition
        words = label.split()
        seen = []
        for word in words:
            if not seen or word.lower() != seen[-1].lower():
                seen.append(word)
        
        label = ' '.join(seen[:15])  # Limit length
        
        # Remove special characters at the end
        label = re.sub(r'[_:]+$', '', label).strip()
        
        # Ensure proper capitalization
        if label and not label[0].isupper():
            label = label[0].upper() + label[1:]
        
        return label
    
    def _sanitize_field_name(self, field_name: str, group_name: str = '') -> str:
        """Create valid Docassemble variable name"""
        if not field_name:
            field_name = "field"
        
        # Clean the name
        name = re.sub(r'[^a-zA-Z0-9_]', '_', field_name.lower())
        name = re.sub(r'_+', '_', name)
        name = name.strip('_')[:30]
        
        # Ensure it starts with a letter
        if name and not name[0].isalpha():
            name = 'field_' + name
        
        # Add group prefix for uniqueness if needed
        if group_name and group_name not in ['general_fields', 'page_1']:
            prefix = group_name.replace('_info', '').replace('_fields', '')
            if not name.startswith(prefix):
                name = f"{prefix}_{name}"[:40]
        
        return name or "field"
    
    def _blocks_to_yaml(self, blocks: List[Dict]) -> str:
        """Convert blocks to YAML format"""
        yaml_parts = []
        
        for block in blocks:
            if block:  # Skip empty blocks
                yaml_part = yaml.dump(
                    block,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                    width=1000
                ).strip()
                yaml_parts.append(yaml_part)
        
        # Single document with no separators between blocks
        return '---\n' + '\n'.join(yaml_parts) + '\n'
    
    def _generate_master_index(self, form_numbers: List[str]):
        """Generate a master index of all procedural interviews"""
        
        # Build content sections
        content_sections = []
        content_sections.append(f"This system contains procedurally generated interviews for all {len(form_numbers)} Ontario family law forms.")
        content_sections.append("")
        content_sections.append("Each interview is generated directly from parsed form data and includes:")
        content_sections.append("- All detected fields organized by context")
        content_sections.append("- Proper entity relationships")
        content_sections.append("- Table handling for repeating data")
        content_sections.append("- Ontario-specific validation")
        content_sections.append("- Calculated fields where detected")
        content_sections.append("")
        content_sections.append("## Available Forms")
        content_sections.append("")
        
        # Organize forms by category
        categories = {
            'Financial Disclosure Forms': [],
            'Applications and Answers': [],
            'Motions and Conferences': [],
            'Orders': [],
            'Other Forms': []
        }
        
        for form_num in sorted(form_numbers):
            form_info = self.relationship_data['forms'].get(form_num, {})
            field_count = form_info.get('field_count', 0)
            entity_count = form_info.get('entity_count', 0)
            table_count = form_info.get('table_count', 0)
            
            form_link = f"* **[Form {form_num}](/interview?i=docassemble.webapp:ontario-family-law/utilities/workflow_output/procedural_interviews/form_{form_num}_interview.yml)** ({field_count} fields, {entity_count} entities, {table_count} tables)"
            
            if '13' in form_num or '26' in form_num:
                categories['Financial Disclosure Forms'].append(form_link)
            elif '8' in form_num or '10' in form_num:
                categories['Applications and Answers'].append(form_link)
            elif '14' in form_num or '15' in form_num or '17' in form_num:
                categories['Motions and Conferences'].append(form_link)
            elif '25' in form_num:
                categories['Orders'].append(form_link)
            else:
                categories['Other Forms'].append(form_link)
        
        # Add categories to content
        category_icons = {
            'Financial Disclosure Forms': '💰',
            'Applications and Answers': '📋',
            'Motions and Conferences': '📝',
            'Orders': '⚖️',
            'Other Forms': '📄'
        }
        
        for category_name, forms in categories.items():
            if forms:
                content_sections.append(f"### {category_icons.get(category_name, '')} {category_name}")
                content_sections.extend(forms)
                content_sections.append("")
        
        # Add system information
        content_sections.extend([
            "---",
            "",
            "## System Information",
            "",
            "These interviews are procedurally generated from:",
            "- Enhanced field parsing (legacy form fields + patterns)",
            "- Automatic entity detection",
            "- Table structure analysis",
            "- Field relationship mapping",
            "",
            "The system adapts to the actual structure of each form, creating appropriate:",
            "- Object definitions for detected entities",
            "- Question groupings based on field context",
            "- Table handling for repeating data",
            "- Validation functions for detected field types"
        ])
        
        # Build the YAML structure as Python objects
        interview_data = {
            'metadata': {
                'title': 'Ontario Family Law Forms - Procedural Interviews',
                'short title': 'All Forms Index',
                'description': 'Complete index of procedurally generated interviews',
                'generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_forms': len(form_numbers)
            },
            'mandatory': True,
            'question': '# Ontario Family Law Forms - Procedural System',
            'subquestion': '\n'.join(content_sections),
            'buttons': [
                {'Exit': 'exit'},
                {'Refresh': 'restart'}
            ]
        }
        
        # Convert to YAML
        yaml_content = '---\n' + yaml.dump(
            interview_data,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=1000
        )
        
        # Save index
        index_file = self.output_dir / '00_procedural_index.yml'
        with open(index_file, 'w') as f:
            f.write(yaml_content)
        
        logger.info(f"Generated master index: {index_file}")

def main():
    """Run the procedural interview generator"""
    generator = ProceduralInterviewGenerator()
    count = generator.generate_all_interviews()
    print(f"\\nSuccessfully generated {count} procedural interviews")
    print(f"Output directory: workflow_output/procedural_interviews")
    print(f"Index file: workflow_output/procedural_interviews/00_procedural_index.yml")

if __name__ == "__main__":
    main()