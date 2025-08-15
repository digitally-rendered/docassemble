#!/usr/bin/env python3
"""
Comprehensive Form Field Analyzer for Ontario Family Law Forms
Extracts all fields from Word documents and generates structured data for docassemble YAML interview generation
"""

import os
import json
import re
from pathlib import Path
from docx import Document
from typing import Dict, List, Any, Optional
from datetime import datetime

class FormFieldAnalyzer:
    """Analyze Word forms to extract fields for docassemble interview generation"""
    
    def __init__(self):
        self.field_patterns = {
            # Personal Information
            'name_fields': [
                r'full legal name',
                r'first name',
                r'last name',
                r'middle name',
                r'surname',
                r'given name',
                r'applicant(?:\'s)? name',
                r'respondent(?:\'s)? name',
                r'lawyer(?:\'s)? name',
                r'child(?:\'s|ren\'s)? name'
            ],
            
            # Contact Information
            'contact_fields': [
                r'address',
                r'street',
                r'city',
                r'province',
                r'postal code',
                r'phone',
                r'fax',
                r'email',
                r'telephone'
            ],
            
            # Date Fields
            'date_fields': [
                r'date of birth',
                r'birthdate',
                r'marriage date',
                r'separation date',
                r'divorce date',
                r'filing date',
                r'court date',
                r'since \(date\)',
                r'on \(date\)',
                r'date'
            ],
            
            # Financial Fields
            'financial_fields': [
                r'income',
                r'expense',
                r'asset',
                r'debt',
                r'property',
                r'support',
                r'child support',
                r'spousal support',
                r'table amount',
                r'special expense'
            ],
            
            # Legal/Court Fields
            'court_fields': [
                r'court file number',
                r'court office',
                r'court name',
                r'judge',
                r'court location',
                r'municipality'
            ],
            
            # Checkboxes/Options
            'checkbox_fields': [
                r'☐',
                r'\[\s*\]',
                r'\(\s*\)',
                r'yes\s*☐\s*no\s*☐',
                r'check one',
                r'check all that apply',
                r'select'
            ],
            
            # Text Areas
            'text_areas': [
                r'describe',
                r'explain',
                r'provide details',
                r'reasons',
                r'facts',
                r'circumstances',
                r'additional information'
            ]
        }
        
        self.form_metadata = {}
        self.extracted_fields = []
        
    def extract_form_structure(self, doc_path: str) -> Dict[str, Any]:
        """Extract complete form structure from a Word document"""
        try:
            doc = Document(doc_path)
            form_name = Path(doc_path).stem
            
            structure = {
                'form_name': form_name,
                'file_path': doc_path,
                'extraction_date': datetime.now().isoformat(),
                'sections': [],
                'fields': [],
                'tables': [],
                'checkboxes': [],
                'text_blocks': [],
                'statistics': {
                    'total_paragraphs': len(doc.paragraphs),
                    'total_tables': len(doc.tables),
                    'total_fields': 0
                }
            }
            
            # Extract paragraphs
            current_section = None
            for para_idx, para in enumerate(doc.paragraphs):
                text = para.text.strip()
                if not text:
                    continue
                    
                # Detect section headers (usually bold or uppercase)
                if text.isupper() or (para.runs and para.runs[0].bold):
                    current_section = {
                        'title': text,
                        'fields': [],
                        'position': para_idx
                    }
                    structure['sections'].append(current_section)
                
                # Extract fields from paragraph
                fields = self._extract_fields_from_text(text, para_idx, 'paragraph')
                if fields:
                    structure['fields'].extend(fields)
                    if current_section:
                        current_section['fields'].extend(fields)
            
            # Extract tables
            for table_idx, table in enumerate(doc.tables):
                table_data = {
                    'table_index': table_idx,
                    'rows': len(table.rows),
                    'columns': len(table.columns) if table.rows else 0,
                    'fields': []
                }
                
                for row_idx, row in enumerate(table.rows):
                    for cell_idx, cell in enumerate(row.cells):
                        cell_text = cell.text.strip()
                        if cell_text:
                            fields = self._extract_fields_from_text(
                                cell_text, 
                                f"table_{table_idx}_row_{row_idx}_cell_{cell_idx}",
                                'table_cell'
                            )
                            if fields:
                                table_data['fields'].extend(fields)
                                structure['fields'].extend(fields)
                
                if table_data['fields']:
                    structure['tables'].append(table_data)
            
            # Update statistics
            structure['statistics']['total_fields'] = len(structure['fields'])
            structure['statistics']['unique_fields'] = len(set(f['field_name'] for f in structure['fields']))
            
            return structure
            
        except Exception as e:
            return {
                'error': str(e),
                'form_name': Path(doc_path).stem,
                'file_path': doc_path
            }
    
    def _extract_fields_from_text(self, text: str, location: Any, context_type: str) -> List[Dict]:
        """Extract individual fields from text"""
        fields = []
        text_lower = text.lower()
        
        # Check for fillable indicators
        has_fillable = any(indicator in text for indicator in ['___', '______', '(', ':', '☐', '[ ]'])
        
        if not has_fillable and len(text) > 200:  # Skip long text blocks without fields
            return fields
        
        # Identify field type
        field_type = self._identify_field_type(text_lower)
        
        # Extract field name and properties
        if has_fillable or field_type:
            field = {
                'field_name': self._generate_field_name(text),
                'original_text': text[:200] if len(text) > 200 else text,
                'field_type': field_type or 'text',
                'location': location,
                'context_type': context_type,
                'required': 'must' in text_lower or 'required' in text_lower,
                'has_checkbox': '☐' in text or '[ ]' in text or '( )' in text,
                'has_underline': '___' in text,
                'is_conditional': 'if' in text_lower or 'when' in text_lower
            }
            
            # Extract validation rules
            field['validation'] = self._extract_validation_rules(text)
            
            # Extract options for choice fields
            if field['has_checkbox']:
                field['options'] = self._extract_options(text)
            
            fields.append(field)
        
        return fields
    
    def _identify_field_type(self, text: str) -> Optional[str]:
        """Identify the type of field based on patterns"""
        for field_type, patterns in self.field_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    # Map to docassemble field types
                    if 'date' in field_type:
                        return 'date'
                    elif 'financial' in field_type:
                        return 'currency'
                    elif 'checkbox' in field_type:
                        return 'yesno'
                    elif 'text_area' in field_type:
                        return 'area'
                    elif 'name' in field_type:
                        return 'text'
                    elif 'contact' in field_type:
                        if 'email' in text:
                            return 'email'
                        elif 'phone' in text:
                            return 'text'  # Could add phone validation
                        else:
                            return 'text'
                    else:
                        return 'text'
        return None
    
    def _generate_field_name(self, text: str) -> str:
        """Generate a valid docassemble variable name from text"""
        # Extract meaningful part before colon or parenthesis
        text = text.split(':')[0].split('(')[0]
        
        # Remove special characters and normalize
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        text = text.strip().lower()
        
        # Convert to snake_case
        field_name = '_'.join(text.split())
        
        # Ensure valid Python variable name
        if field_name and not field_name[0].isalpha():
            field_name = 'field_' + field_name
        
        return field_name or 'unnamed_field'
    
    def _extract_validation_rules(self, text: str) -> Dict:
        """Extract validation rules from field text"""
        rules = {}
        text_lower = text.lower()
        
        # Check for required fields
        if 'must' in text_lower or 'required' in text_lower:
            rules['required'] = True
        
        # Check for date formats
        if re.search(r'\(d[,/]?\s*m[,/]?\s*y\)', text_lower):
            rules['format'] = 'DD/MM/YYYY'
        
        # Check for length constraints
        length_match = re.search(r'maximum (\d+) characters', text_lower)
        if length_match:
            rules['maxlength'] = int(length_match.group(1))
        
        return rules
    
    def _extract_options(self, text: str) -> List[str]:
        """Extract checkbox/radio options from text"""
        options = []
        
        # Pattern for checkbox options
        checkbox_pattern = r'☐\s*([^☐\n]+)'
        matches = re.findall(checkbox_pattern, text)
        if matches:
            options = [m.strip() for m in matches]
        
        # Pattern for yes/no options
        if re.search(r'yes\s*☐\s*no\s*☐', text, re.IGNORECASE):
            options = ['Yes', 'No']
        
        return options
    
    def analyze_all_forms(self, forms_dir: str) -> Dict[str, Any]:
        """Analyze all forms in a directory"""
        results = {
            'analysis_date': datetime.now().isoformat(),
            'forms_directory': forms_dir,
            'forms_analyzed': [],
            'total_fields': 0,
            'field_summary': {}
        }
        
        forms_path = Path(forms_dir)
        
        # Find all Word documents
        doc_files = []
        for ext in ['*.docx', '*.doc']:
            doc_files.extend(forms_path.rglob(ext))
        
        print(f"Found {len(doc_files)} Word documents to analyze")
        
        for doc_file in doc_files:
            print(f"Analyzing: {doc_file.name}")
            form_structure = self.extract_form_structure(str(doc_file))
            
            if 'error' not in form_structure:
                results['forms_analyzed'].append(form_structure)
                results['total_fields'] += form_structure['statistics']['total_fields']
                
                # Summarize field types
                for field in form_structure['fields']:
                    field_type = field['field_type']
                    if field_type not in results['field_summary']:
                        results['field_summary'][field_type] = 0
                    results['field_summary'][field_type] += 1
            else:
                print(f"  Error: {form_structure['error']}")
        
        return results

def generate_docassemble_yaml_template(form_structure: Dict) -> str:
    """Generate a docassemble YAML interview template from form structure"""
    yaml_content = f"""---
# Ontario Family Law Form: {form_structure['form_name']}
# Auto-generated template - requires review and customization
metadata:
  title: |
    {form_structure['form_name'].replace('_', ' ').title()}
  short title: |
    {form_structure['form_name'].split('_')[0].upper()}
  description: |
    Ontario family law form interview
  authors:
    - name: Auto-generated
  revision_date: {datetime.now().strftime('%Y-%m-%d')}
---
mandatory: True
code: |
  # Interview order
  intro_screen
"""
    
    # Group fields by section
    sections = {}
    for field in form_structure.get('fields', []):
        section = field.get('context_type', 'general')
        if section not in sections:
            sections[section] = []
        sections[section].append(field)
    
    # Generate questions for each field
    for section, fields in sections.items():
        yaml_content += f"\n  # {section.replace('_', ' ').title()} Section\n"
        for field in fields[:10]:  # Limit to first 10 fields per section for template
            yaml_content += f"  {field['field_name']}\n"
    
    yaml_content += """  
  final_screen
---
question: |
  Welcome to the {form_structure['form_name'].replace('_', ' ').title()} Interview
subquestion: |
  This interview will help you complete the Ontario family law form.
  
  Please have the following information ready:
  * Personal identification
  * Contact information
  * Relevant dates
  * Financial information (if applicable)
continue button field: intro_screen
---
"""
    
    # Generate sample questions for first few fields
    for field in form_structure.get('fields', [])[:5]:
        yaml_content += f"""question: |
  {field['original_text'][:100] if len(field['original_text']) > 100 else field['original_text']}
fields:
  - "{field['field_name'].replace('_', ' ').title()}": {field['field_name']}
"""
        
        if field['field_type'] == 'date':
            yaml_content += f"    datatype: date\n"
        elif field['field_type'] == 'currency':
            yaml_content += f"    datatype: currency\n"
        elif field['field_type'] == 'email':
            yaml_content += f"    datatype: email\n"
        elif field['field_type'] == 'yesno':
            yaml_content += f"    datatype: yesnoradio\n"
        elif field['field_type'] == 'area':
            yaml_content += f"    input type: area\n"
        
        if field.get('required'):
            yaml_content += f"    required: True\n"
        
        if field.get('validation', {}).get('maxlength'):
            yaml_content += f"    maxlength: {field['validation']['maxlength']}\n"
        
        yaml_content += "---\n"
    
    yaml_content += """event: final_screen
question: |
  Form Complete
subquestion: |
  Your form has been completed. You can now download or print it.
buttons:
  - Exit: exit
  - Restart: restart
---
"""
    
    return yaml_content

def main():
    """Main function to analyze forms and generate outputs"""
    import sys
    
    # Get forms directory
    if len(sys.argv) > 1:
        forms_dir = sys.argv[1]
    else:
        forms_dir = "/Users/draw/development/docassemble/docassemble_webapp/docassemble/webapp/data/questions/ontario-family-law/utilities/test_download"
    
    print("=" * 60)
    print("COMPREHENSIVE ONTARIO FAMILY LAW FORMS ANALYZER")
    print("=" * 60)
    
    analyzer = FormFieldAnalyzer()
    
    # Analyze all forms
    results = analyzer.analyze_all_forms(forms_dir)
    
    # Save analysis results
    output_dir = Path("./form_analysis_output")
    output_dir.mkdir(exist_ok=True)
    
    # Save complete analysis
    with open(output_dir / "complete_analysis.json", 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n✓ Complete analysis saved to: {output_dir / 'complete_analysis.json'}")
    
    # Generate YAML templates for each form
    yaml_dir = output_dir / "yaml_templates"
    yaml_dir.mkdir(exist_ok=True)
    
    for form in results['forms_analyzed']:
        yaml_content = generate_docassemble_yaml_template(form)
        yaml_file = yaml_dir / f"{form['form_name']}.yml"
        with open(yaml_file, 'w') as f:
            f.write(yaml_content)
        print(f"✓ YAML template generated: {yaml_file.name}")
    
    # Generate summary report
    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Forms analyzed: {len(results['forms_analyzed'])}")
    print(f"Total fields extracted: {results['total_fields']}")
    print(f"\nField types distribution:")
    for field_type, count in results['field_summary'].items():
        print(f"  - {field_type}: {count}")
    
    print(f"\n✓ All outputs saved to: {output_dir.absolute()}")

if __name__ == "__main__":
    main()