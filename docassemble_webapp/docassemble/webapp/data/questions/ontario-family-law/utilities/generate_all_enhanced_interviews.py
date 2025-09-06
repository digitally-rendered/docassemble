#!/usr/bin/env python3
"""
Generate all Ontario Family Law form interviews using the enhanced converter
Processes all forms with improved parsed data (3,702 fields total)
"""

import json
import logging
from pathlib import Path
from intelligent_form_converter_enhanced import IntelligentFormConverterEnhanced

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_all_form_numbers():
    """Get all available form numbers from parsed data"""
    parsed_dir = Path('parsed_forms')
    form_numbers = set()
    
    for file in parsed_dir.glob('form_*_improved.json'):
        # Extract form number from filename
        filename = file.stem  # e.g., 'form_8_improved'
        parts = filename.split('_')
        if len(parts) >= 2:
            form_number = parts[1]  # Get the form number part
            form_numbers.add(form_number)
    
    return sorted(form_numbers)

def main():
    """Main function to generate all interviews"""
    logger.info("Starting enhanced interview generation for all forms")
    
    # Initialize the converter
    converter = IntelligentFormConverterEnhanced(
        parsed_forms_dir='parsed_forms',
        output_dir='generated_interviews_enhanced'
    )
    
    # Get all available form numbers
    form_numbers = get_all_form_numbers()
    logger.info(f"Found {len(form_numbers)} forms to process: {', '.join(form_numbers)}")
    
    # Track results
    results = {
        'successful': [],
        'failed': [],
        'skipped': []
    }
    
    # Process each form
    for form_number in form_numbers:
        try:
            # Check if already generated
            output_file = Path('generated_interviews_enhanced') / f"form_{form_number}_interview_enhanced.yml"
            if output_file.exists():
                logger.info(f"Form {form_number}: Already exists, skipping")
                results['skipped'].append(form_number)
                continue
            
            logger.info(f"Generating interview for Form {form_number}")
            output_path = converter.generate_interview(form_number)
            logger.info(f"  ✓ Generated: {output_path}")
            results['successful'].append(form_number)
            
        except FileNotFoundError as e:
            logger.warning(f"  ✗ Form {form_number}: Parsed data not found - {e}")
            results['failed'].append((form_number, str(e)))
        except Exception as e:
            logger.error(f"  ✗ Form {form_number}: Generation failed - {e}")
            results['failed'].append((form_number, str(e)))
    
    # Generate summary report
    logger.info("\n" + "="*60)
    logger.info("GENERATION SUMMARY")
    logger.info("="*60)
    logger.info(f"Total forms: {len(form_numbers)}")
    logger.info(f"Successfully generated: {len(results['successful'])}")
    logger.info(f"Failed: {len(results['failed'])}")
    logger.info(f"Skipped (already exists): {len(results['skipped'])}")
    
    if results['successful']:
        logger.info(f"\nSuccessful: {', '.join(results['successful'])}")
    
    if results['failed']:
        logger.info("\nFailed:")
        for form_num, error in results['failed']:
            logger.info(f"  - Form {form_num}: {error}")
    
    # Save summary to file
    summary_file = Path('generated_interviews_enhanced') / 'generation_summary.json'
    with open(summary_file, 'w') as f:
        json.dump({
            'timestamp': str(Path.ctime(Path.cwd())),
            'total_forms': len(form_numbers),
            'successful': results['successful'],
            'failed': [{'form': f, 'error': e} for f, e in results['failed']],
            'skipped': results['skipped']
        }, f, indent=2)
    
    logger.info(f"\nSummary saved to: {summary_file}")
    
    # Generate index file for all interviews
    generate_index_file(form_numbers)
    
    return results

def generate_index_file(form_numbers):
    """Generate an index YAML file that lists all available interviews"""
    index_content = """---
metadata:
  title: Ontario Family Law Forms - Enhanced Collection
  short_title: Ontario Forms Index
  description: Complete collection of Ontario Family Law form interviews with enhanced field coverage
  authors:
    - Ontario Family Law System
  tags:
    - ontario
    - family law
    - forms
    - index
---
include:
  - ontario_common_fields_enhanced.py
  - ontario_party_objects_enhanced.py
  - ontario_children_objects_enhanced.py
---
mandatory: True
code: |
  selected_form
  if selected_form == 'exit':
    command('exit')
  else:
    command('restart', url=selected_form)
---
question: |
  Ontario Family Law Forms - Enhanced Collection
subquestion: |
  Select a form to complete. These forms have been generated with comprehensive field coverage
  from the improved parsing system (3,702 total fields extracted).
  
  **Core Applications:**
  - Form 8: Application (General)
  - Form 8A: Application (Divorce)
  - Form 10: Answer
  
  **Financial Statements:**
  - Form 13: Financial Statement (Support Claims)
  - Form 13.1: Financial Statement (Property and Support)
  - Form 13A: Certificate of Financial Disclosure
  
  **Motions:**
  - Form 14B: Motion Form
  - Form 15: Motion to Change
  
  **Divorce:**
  - Form 36: Affidavit for Divorce
  - Form 36A: Certificate of Divorce
  
  **And many more...**
field: selected_form
buttons:"""
    
    # Add buttons for each form
    for form_num in sorted(form_numbers):
        if form_num.replace('.', '_'):  # Handle form numbers like 13.1
            safe_num = form_num.replace('.', '_')
            index_content += f"""
  - Form {form_num}: form_{safe_num}_interview_enhanced.yml"""
    
    index_content += """
  - Exit: exit
---"""
    
    # Save index file
    index_file = Path('generated_interviews_enhanced') / '00_INDEX_ENHANCED.yml'
    with open(index_file, 'w') as f:
        f.write(index_content)
    
    logger.info(f"Index file generated: {index_file}")

if __name__ == "__main__":
    main()