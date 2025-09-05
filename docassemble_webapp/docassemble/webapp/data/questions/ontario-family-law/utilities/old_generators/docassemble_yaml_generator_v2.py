#!/usr/bin/env python3
"""
Improved Docassemble YAML Generator for Ontario Family Law Forms
Properly handles special characters, long text, and YAML formatting
"""

import json
import re
import yaml
from pathlib import Path
from typing import Dict, List, Any, Set
from datetime import datetime
from collections import OrderedDict

class ImprovedDocassembleYAMLGenerator:
    """Generate robust docassemble YAML interviews from form field analysis"""
    
    def __init__(self):
        self.form_mappings = {
            'form_8': {
                'title': 'Ontario Family Law Form 8 - Application (General)',
                'short_title': 'Form 8 - Application',
                'description': 'Complete Ontario Family Court Form 8 - Application (General) to start family court proceedings.',
                'objects': ['applicant', 'respondent', 'children', 'court_info', 'claims']
            },
            'form_10': {
                'title': 'Ontario Family Law Form 10 - Answer',
                'short_title': 'Form 10 - Answer',
                'description': 'Complete Ontario Family Court Form 10 - Answer to respond to an application.',
                'objects': ['applicant', 'respondent', 'children', 'court_info', 'response_claims']
            },
            'form_13': {
                'title': 'Ontario Family Law Form 13 - Financial Statement (Support Claims)',
                'short_title': 'Form 13 - Financial Statement',
                'description': 'Complete financial disclosure for support claims.',
                'objects': ['party', 'income', 'expenses', 'assets', 'debts']
            },
            'form_36': {
                'title': 'Ontario Family Law Form 36 - Affidavit for Divorce',
                'short_title': 'Form 36 - Divorce Affidavit',
                'description': 'Affidavit required for uncontested divorce proceedings.',
                'objects': ['applicant', 'respondent', 'marriage_info', 'separation_info', 'children']
            }
        }
    
    def safe_yaml_string(self, text: str, max_length: int = 80) -> str:
        """Create a YAML-safe string with proper escaping"""
        if not text:
            return ""
        
        # Remove any null bytes or control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        
        # Replace line breaks with spaces
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        # Remove multiple spaces
        text = ' '.join(text.split())
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length-3] + "..."
        
        # Escape special YAML characters
        # If string contains quotes, colons, or other special chars, we need to quote it
        needs_quotes = any(char in text for char in [':', '"', "'", '|', '>', '-', '*', '&', '!', '%', '@', '`'])
        
        if needs_quotes:
            # Escape any double quotes in the string
            text = text.replace('"', '\\"')
            return f'"{text}"'
        
        return text
    
    def safe_variable_name(self, text: str, max_length: int = 50) -> str:
        """Create a valid docassemble variable name"""
        if not text:
            return "unnamed_field"
        
        # Convert to lowercase and replace non-alphanumeric with underscore
        text = re.sub(r'[^a-z0-9]+', '_', text.lower())
        
        # Remove leading/trailing underscores
        text = text.strip('_')
        
        # Ensure it starts with a letter
        if text and not text[0].isalpha():
            text = 'field_' + text
        
        # Truncate if too long
        if len(text) > max_length:
            # Keep meaningful parts
            parts = text.split('_')
            if len(parts) > 1:
                text = '_'.join(parts[:5])[:max_length]
            else:
                text = text[:max_length]
        
        return text or "unnamed_field"
    
    def deduplicate_fields(self, fields: List[Dict]) -> List[Dict]:
        """Remove duplicate fields keeping the most informative version"""
        seen_fields = {}
        
        for field in fields:
            # Generate a clean key for deduplication
            key = self.safe_variable_name(field.get('field_name', ''))
            
            # Skip generic fields
            if key in ['unnamed_field', 'field', '']:
                continue
            
            # Keep the most complete version of each field
            if key not in seen_fields:
                seen_fields[key] = field
            else:
                # Keep the one with more information
                existing = seen_fields[key]
                existing_text = existing.get('original_text', '')
                new_text = field.get('original_text', '')
                
                # Prefer the one with more descriptive text
                if len(new_text) > len(existing_text) and len(new_text) < 200:
                    seen_fields[key] = field
        
        return list(seen_fields.values())
    
    def group_fields_by_section(self, fields: List[Dict]) -> Dict[str, List[Dict]]:
        """Organize fields into logical sections"""
        sections = {
            'court_information': [],
            'applicant_information': [],
            'respondent_information': [],
            'children_information': [],
            'financial_information': [],
            'marriage_information': [],
            'claims': [],
            'other': []
        }
        
        for field in fields:
            field_name = (field.get('field_name', '') or '').lower()
            original_text = (field.get('original_text', '') or '').lower()
            
            # Categorize based on field name and content
            categorized = False
            
            # Court information
            if any(term in field_name or term in original_text for term in 
                   ['court', 'file number', 'judge', 'registry']):
                sections['court_information'].append(field)
                categorized = True
            
            # Applicant information
            elif any(term in field_name or term in original_text for term in 
                     ['applicant', 'petitioner', 'plaintiff']):
                sections['applicant_information'].append(field)
                categorized = True
            
            # Respondent information
            elif any(term in field_name or term in original_text for term in 
                     ['respondent', 'defendant']):
                sections['respondent_information'].append(field)
                categorized = True
            
            # Children information
            elif any(term in field_name or term in original_text for term in 
                     ['child', 'custody', 'access', 'parenting']):
                sections['children_information'].append(field)
                categorized = True
            
            # Financial information
            elif any(term in field_name or term in original_text for term in 
                     ['income', 'expense', 'asset', 'debt', 'financial', 'support', 'money', 'property']):
                sections['financial_information'].append(field)
                categorized = True
            
            # Marriage information
            elif any(term in field_name or term in original_text for term in 
                     ['marriage', 'married', 'separation', 'divorce', 'relationship']):
                sections['marriage_information'].append(field)
                categorized = True
            
            # Claims
            elif any(term in field_name or term in original_text for term in 
                     ['claim', 'order', 'relief', 'ask']):
                sections['claims'].append(field)
                categorized = True
            
            # Other
            if not categorized:
                sections['other'].append(field)
        
        # Remove empty sections
        return {k: v for k, v in sections.items() if v}
    
    def generate_docassemble_variable(self, field: Dict, section: str) -> str:
        """Generate proper docassemble variable name"""
        
        # Map sections to object prefixes
        prefix_map = {
            'court_information': 'court_info',
            'applicant_information': 'applicant',
            'respondent_information': 'respondent',
            'children_information': 'children',
            'financial_information': 'financial',
            'marriage_information': 'marriage',
            'claims': 'claims'
        }
        
        prefix = prefix_map.get(section, '')
        
        # Get field name
        field_name = field.get('field_name', '')
        if not field_name or field_name == 'unnamed_field':
            # Try to generate from original text
            original = field.get('original_text', '')
            if original:
                field_name = self.safe_variable_name(original)
            else:
                field_name = f"field_{id(field) % 10000}"
        else:
            field_name = self.safe_variable_name(field_name)
        
        # Combine with prefix if needed
        if prefix and not field_name.startswith(prefix):
            return f"{prefix}.{field_name}"
        
        return field_name
    
    def generate_question_block(self, field: Dict, var_name: str) -> str:
        """Generate a properly formatted question block"""
        field_type = field.get('field_type', 'text')
        original_text = field.get('original_text', var_name.replace('_', ' ').title())
        required = field.get('required', False)
        
        # Create safe question text
        question_text = self.safe_yaml_string(original_text, 100)
        
        # Create safe field label
        field_label = self.safe_yaml_string(original_text[:60] if len(original_text) > 60 else original_text, 60)
        
        # Build the question block
        block = "question: |\n"
        block += f"  {question_text}\n"
        block += "fields:\n"
        block += f"  - {field_label}: {var_name}\n"
        
        # Add field attributes based on type
        if field_type == 'date':
            block += "    datatype: date\n"
        elif field_type == 'currency':
            block += "    datatype: currency\n"
            block += "    min: 0\n"
        elif field_type == 'email':
            block += "    datatype: email\n"
        elif field_type == 'yesno':
            block += "    datatype: yesnoradio\n"
        elif field_type == 'area':
            block += "    input type: area\n"
            block += "    rows: 4\n"
        
        if required:
            block += "    required: True\n"
        
        # Add validation if present
        validation = field.get('validation', {})
        if validation.get('maxlength'):
            block += f"    maxlength: {validation['maxlength']}\n"
        
        block += "---\n"
        
        return block
    
    def generate_yaml_content(self, form_structure: Dict) -> str:
        """Generate complete docassemble YAML interview with proper formatting"""
        form_name = form_structure.get('form_name', 'unknown_form')
        fields = form_structure.get('fields', [])
        
        # Deduplicate fields
        unique_fields = self.deduplicate_fields(fields)
        
        # Group fields by section
        sections = self.group_fields_by_section(unique_fields)
        
        # Determine form type
        form_key = None
        for key in self.form_mappings:
            if key in form_name.lower():
                form_key = key
                break
        
        if not form_key:
            form_key = 'form_8'  # Default
        
        form_config = self.form_mappings[form_key]
        
        # Build YAML content using proper structure
        yaml_parts = []
        
        # Metadata section
        metadata = {
            'metadata': {
                'title': form_config['title'],
                'short title': form_config['short_title'],
                'description': form_config['description'],
                'authors': [{'name': 'Ontario Family Law Forms System'}],
                'revision_date': datetime.now().strftime('%Y-%m-%d'),
                'tags': ['ontario', 'family-law', form_name.lower().replace('_', '-'), 'court-forms'],
                'help_url': 'https://ontariocourtforms.on.ca/en/family-law-forms/'
            }
        }
        yaml_parts.append(yaml.dump(metadata, default_flow_style=False, allow_unicode=True))
        
        # Include section
        yaml_parts.append("include:\n  - ontario-family-law-common.yml\n")
        
        # Features section
        features = {
            'features': {
                'question help button': True,
                'navigation': True,
                'progress bar': True,
                'show progress bar percentage': True,
                'css': 'ontario-family-law.css'
            }
        }
        yaml_parts.append(yaml.dump(features, default_flow_style=False))
        
        # Objects section
        objects_list = []
        if 'applicant_information' in sections:
            objects_list.append("  - applicant: Individual")
        if 'respondent_information' in sections:
            objects_list.append("  - respondent: Individual")
        if 'children_information' in sections:
            objects_list.append("  - children: DAList.using(object_type=Individual, minimum_number=0)")
        if 'court_information' in sections:
            objects_list.append("  - court_info: DAObject")
        if 'financial_information' in sections:
            objects_list.append("  - financial: DAObject")
        if 'marriage_information' in sections:
            objects_list.append("  - marriage: DAObject")
        if 'claims' in sections:
            objects_list.append("  - claims: DADict")
        
        if objects_list:
            yaml_parts.append("objects:\n" + "\n".join(objects_list) + "\n")
        
        # Mandatory code block
        yaml_parts.append("---\nmandatory: True\ncode: |\n")
        yaml_parts.append("  # Introduction\n")
        yaml_parts.append("  introduction_screen\n")
        yaml_parts.append("  legal_disclaimer_accepted\n")
        yaml_parts.append("  \n  # Main interview flow\n")
        
        # Track variables to avoid duplicates
        used_vars = set()
        
        # Add interview flow based on sections
        for section_name, section_fields in sections.items():
            if section_fields:
                yaml_parts.append(f"  \n  # {section_name.replace('_', ' ').title()}\n")
                
                # Add first few unique fields from each section to flow
                count = 0
                for field in section_fields:
                    if count >= 3:  # Limit fields per section in mandatory block
                        break
                    var_name = self.generate_docassemble_variable(field, section_name)
                    if var_name not in used_vars:
                        yaml_parts.append(f"  {var_name}\n")
                        used_vars.add(var_name)
                        count += 1
        
        yaml_parts.append("  \n  # Review and submission\n")
        yaml_parts.append("  review_screen\n")
        yaml_parts.append("  final_screen\n")
        yaml_parts.append("---\n")
        
        # Introduction screen
        yaml_parts.append("""# Introduction screen
question: |
  Welcome to the Ontario Family Law Forms Assistant
subquestion: |
  This interview will help you complete your Ontario family law court form.
  
  Before you begin, please have the following information ready:
  
  * Personal identification for all parties
  * Contact information
  * Court file number (if you have one)
  * Financial information (if applicable)
  * Details about your case
  
  **Important:** This tool provides assistance in completing court forms but does not provide legal advice.
continue button field: introduction_screen
---
""")
        
        # Legal disclaimer
        yaml_parts.append("""# Legal disclaimer
question: |
  Legal Information Disclaimer
subquestion: |
  **Please read carefully:**
  
  This tool helps you complete Ontario family law court forms. It does not provide legal advice.
  
  * The information you provide will be used to populate official court forms
  * You are responsible for the accuracy of all information
  * Consider consulting a lawyer for legal advice about your case
  * Court forms must be filed according to the Family Law Rules
  
  Do you understand and accept these terms?
field: legal_disclaimer_accepted
buttons:
  - "I understand and accept": True
  - "I do not accept": False
---
""")
        
        # Generate questions for each section
        used_vars = set()  # Reset for questions
        
        for section_name, section_fields in sections.items():
            if not section_fields:
                continue
            
            yaml_parts.append(f"# {section_name.replace('_', ' ').title()} Questions\n")
            
            # Generate questions for first few fields in each section
            count = 0
            for field in section_fields:
                if count >= 5:  # Limit questions per section
                    break
                
                var_name = self.generate_docassemble_variable(field, section_name)
                
                # Skip if we already created a question for this variable
                if var_name in used_vars:
                    continue
                
                used_vars.add(var_name)
                question_block = self.generate_question_block(field, var_name)
                yaml_parts.append(question_block)
                count += 1
        
        # Review screen
        yaml_parts.append("""# Review screen
question: |
  Review Your Information
subquestion: |
  Please review the information you have provided.
  
  % if defined('applicant.name.first'):
  **Applicant:** ${ applicant.name }
  % endif
  
  % if defined('respondent.name.first'):
  **Respondent:** ${ respondent.name }
  % endif
  
  % if defined('court_info.file_number'):
  **Court File Number:** ${ court_info.file_number }
  % endif
  
  Is this information correct?
continue button field: review_screen
continue button label: Yes, continue
---
""")
        
        # Final screen
        yaml_parts.append("""# Final screen
event: final_screen
question: |
  Form Completed
subquestion: |
  Your form has been completed and is ready for download.
  
  **Next Steps:**
  
  1. Download your completed form
  2. Review the form carefully
  3. Sign the form where required
  4. File the form with the court
  5. Serve copies as required by the Family Law Rules
buttons:
  - Exit: exit
  - Start Over: restart
---
""")
        
        # Join all parts
        return ''.join(yaml_parts)
    
    def process_all_forms(self, analysis_file: str, output_dir: str):
        """Process all analyzed forms and generate docassemble YAML files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Load analysis results
        with open(analysis_file, 'r') as f:
            analysis = json.load(f)
        
        generated_files = []
        
        for form in analysis.get('forms_analyzed', []):
            form_name = form.get('form_name', 'unknown')
            
            # Skip non-Ontario family law forms
            if not any(term in form_name.lower() for term in ['form_', 'flr']):
                continue
            
            print(f"Generating docassemble YAML for: {form_name}")
            
            try:
                # Generate YAML content
                yaml_content = self.generate_yaml_content(form)
                
                # Save to file
                output_file = output_path / f"{form_name}_interview.yml"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(yaml_content)
                
                generated_files.append(output_file)
                print(f"  ✓ Generated: {output_file.name}")
                
            except Exception as e:
                print(f"  ✗ Error generating {form_name}: {e}")
        
        return generated_files

def main():
    """Main function"""
    import sys
    
    # Get paths
    if len(sys.argv) > 1:
        analysis_file = sys.argv[1]
    else:
        analysis_file = "form_analysis_output/complete_analysis.json"
    
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    else:
        output_dir = "docassemble_interviews_v2"
    
    print("=" * 60)
    print("IMPROVED DOCASSEMBLE YAML GENERATOR V2")
    print("=" * 60)
    
    generator = ImprovedDocassembleYAMLGenerator()
    
    # Generate YAML files
    generated = generator.process_all_forms(analysis_file, output_dir)
    
    print(f"\n✓ Generated {len(generated)} docassemble interview files")
    print(f"✓ Output directory: {Path(output_dir).absolute()}")

if __name__ == "__main__":
    main()