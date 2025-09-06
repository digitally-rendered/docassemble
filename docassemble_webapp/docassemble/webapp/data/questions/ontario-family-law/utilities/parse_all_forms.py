#!/usr/bin/env python3
"""
Batch parser for all Ontario Family Law Forms
Runs the improved parser on all available forms
"""

import os
import json
from pathlib import Path
from improved_form_parser import ImprovedFormParser
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def find_all_forms(directory: str) -> list:
    """Find all DOCX form files in the specified directory"""
    forms = []
    base_path = Path(directory)
    
    # Search patterns
    patterns = ['*.docx', '*.DOCX']
    
    for pattern in patterns:
        forms.extend(base_path.glob(f'**/{pattern}'))
    
    # Filter out filled forms and templates
    forms = [f for f in forms if 'filled' not in f.stem.lower() 
             and 'test' not in f.stem.lower()
             and 'template' not in f.stem.lower()]
    
    return sorted(forms)


def parse_form(form_path: Path, output_dir: Path) -> dict:
    """Parse a single form and save results"""
    logger.info(f"Parsing: {form_path.name}")
    
    try:
        parser = ImprovedFormParser(str(form_path))
        fields = parser.parse()
        
        # Generate output filename
        form_number = parser.form_number
        output_file = output_dir / f"form_{form_number}_improved.json"
        
        # Save results
        output_data = {
            'form_number': form_number,
            'form_file': str(form_path.name),
            'source_path': str(form_path),
            'total_fields': len(fields),
            'field_types': {},
            'fields': []
        }
        
        # Count field types
        for field in fields:
            field_type = field.field_type
            output_data['field_types'][field_type] = output_data['field_types'].get(field_type, 0) + 1
            
            # Convert field to dict
            field_dict = {
                'field_id': field.field_id,
                'field_name': field.field_name,
                'field_type': field.field_type,
                'field_label': field.field_label,
                'required': field.required,
                'validation_rules': field.validation_rules,
                'max_length': field.max_length,
                'options': field.options,
                'table_name': field.table_name,
                'table_row': field.table_row,
                'field_context': field.field_context,
                'page_number': field.page_number,
                'coordinates': field.coordinates,
                'help_text': field.help_text,
                'section': field.section
            }
            output_data['fields'].append(field_dict)
        
        # Save to JSON
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        logger.info(f"  -> Saved {len(fields)} fields to {output_file.name}")
        
        return {
            'form': form_number,
            'file': form_path.name,
            'fields': len(fields),
            'types': output_data['field_types'],
            'output': str(output_file)
        }
        
    except Exception as e:
        logger.error(f"  -> Error parsing {form_path.name}: {e}")
        return {
            'form': 'error',
            'file': form_path.name,
            'fields': 0,
            'error': str(e)
        }


def main():
    """Main function to parse all forms"""
    
    # Define directories
    forms_dirs = [
        'workflow_output/ontario_forms',
        'ontario_forms_test/core_applications',
        'ontario_forms_test/financial_statements',
        'ontario_forms_test/divorce_specific',
        'ontario_forms_test/motions_conferences',
        'ontario_forms_test/enforcement',
        'ontario_forms_test/child_protection_adoption',
    ]
    
    output_dir = Path('parsed_forms')
    output_dir.mkdir(exist_ok=True)
    
    # Find all forms
    all_forms = []
    for dir_path in forms_dirs:
        if Path(dir_path).exists():
            forms = find_all_forms(dir_path)
            all_forms.extend(forms)
            logger.info(f"Found {len(forms)} forms in {dir_path}")
    
    # Remove duplicates (based on filename)
    unique_forms = {}
    for form in all_forms:
        if form.name not in unique_forms:
            unique_forms[form.name] = form
    
    forms_to_parse = list(unique_forms.values())
    logger.info(f"\nTotal unique forms to parse: {len(forms_to_parse)}")
    
    # Parse each form
    results = []
    for form_path in forms_to_parse:
        result = parse_form(form_path, output_dir)
        results.append(result)
    
    # Generate summary report
    summary = {
        'total_forms': len(results),
        'successfully_parsed': sum(1 for r in results if r.get('fields', 0) > 0),
        'failed': sum(1 for r in results if 'error' in r),
        'total_fields_extracted': sum(r.get('fields', 0) for r in results),
        'forms': results
    }
    
    # Save summary
    summary_file = output_dir / 'parsing_summary_improved.json'
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("PARSING SUMMARY")
    print("="*60)
    print(f"Total forms processed: {summary['total_forms']}")
    print(f"Successfully parsed: {summary['successfully_parsed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Total fields extracted: {summary['total_fields_extracted']}")
    print(f"\nResults saved to: {output_dir}")
    print(f"Summary saved to: {summary_file}")
    
    # Print per-form summary
    print("\n" + "-"*60)
    print("PER-FORM RESULTS:")
    print("-"*60)
    
    for result in sorted(results, key=lambda x: x.get('form', '')):
        if 'error' not in result:
            print(f"Form {result['form']}: {result['fields']} fields")
            if result['types']:
                types_str = ', '.join(f"{k}:{v}" for k, v in sorted(result['types'].items()))
                print(f"  Types: {types_str}")
        else:
            print(f"Form {result['form']}: ERROR - {result.get('error', 'Unknown error')}")
    
    return summary


if __name__ == "__main__":
    main()