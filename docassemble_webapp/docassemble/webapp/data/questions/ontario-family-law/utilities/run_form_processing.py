#!/usr/bin/env python3
"""
Complete Ontario Family Law Forms Processing Pipeline
1. Download forms from Ontario Court Forms website
2. Parse forms to extract fields
3. Save fields to CSV
4. Generate docassemble YAML interviews
"""

import os
import sys
from pathlib import Path
import subprocess
import argparse

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

def download_forms():
    """Download Ontario family law forms"""
    print("\n" + "="*50)
    print("STEP 1: Downloading Ontario Family Law Forms")
    print("="*50)
    
    from download_all_forms import download_all_ontario_forms
    forms_dir = Path(__file__).parent / "ontario_forms"
    download_all_ontario_forms(str(forms_dir))
    return forms_dir

def parse_forms(forms_dir):
    """Parse forms and generate CSV/YAML files"""
    print("\n" + "="*50)
    print("STEP 2: Parsing Forms and Extracting Fields")
    print("="*50)
    
    from comprehensive_form_parser import process_all_forms
    output_dir = Path(__file__).parent / "form_analysis_output"
    process_all_forms(str(forms_dir), str(output_dir))
    return output_dir

def validate_yaml_files(yaml_dir):
    """Validate generated YAML files"""
    print("\n" + "="*50)
    print("STEP 3: Validating Generated YAML Files")
    print("="*50)
    
    from validate_interviews import validate_all_interviews
    yaml_path = yaml_dir / "yaml_files"
    validate_all_interviews(str(yaml_path))

def generate_summary_report(output_dir):
    """Generate summary report of all processed forms"""
    print("\n" + "="*50)
    print("STEP 4: Generating Summary Report")
    print("="*50)
    
    import csv
    import json
    
    csv_dir = output_dir / "csv_files"
    summary = []
    
    for csv_file in csv_dir.glob("*_fields.csv"):
        form_number = csv_file.stem.replace("_fields", "")
        
        # Count fields
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fields = list(reader)
            
            field_types = {}
            for field in fields:
                field_type = field.get('field_type', 'unknown')
                field_types[field_type] = field_types.get(field_type, 0) + 1
            
            summary.append({
                'form_number': form_number,
                'total_fields': len(fields),
                'field_types': field_types,
                'has_tables': any(f.get('table_name') for f in fields),
                'pages': max(int(f.get('page_number', 1)) for f in fields) if fields else 1
            })
    
    # Write summary report
    report_file = output_dir / "processing_summary.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    # Print summary
    print(f"\nProcessed {len(summary)} forms:")
    for form in summary:
        print(f"  - {form['form_number']}: {form['total_fields']} fields across {form['pages']} pages")
        print(f"    Field types: {form['field_types']}")
    
    print(f"\nSummary report saved to: {report_file}")

def copy_to_docassemble(yaml_dir):
    """Copy generated YAML files to docassemble questions directory"""
    print("\n" + "="*50)
    print("STEP 5: Copying YAML Files to Docassemble")
    print("="*50)
    
    import shutil
    
    yaml_source = yaml_dir / "yaml_files"
    yaml_dest = Path(__file__).parent.parent  # ontario-family-law directory
    
    copied = 0
    for yaml_file in yaml_source.glob("*.yml"):
        dest_file = yaml_dest / yaml_file.name
        shutil.copy2(yaml_file, dest_file)
        copied += 1
        print(f"  Copied: {yaml_file.name}")
    
    print(f"\nCopied {copied} YAML files to: {yaml_dest}")

def main():
    """Main processing pipeline"""
    parser = argparse.ArgumentParser(description="Process Ontario Family Law Forms")
    parser.add_argument('--skip-download', action='store_true', help='Skip downloading forms')
    parser.add_argument('--skip-install', action='store_true', help='Skip installing requirements')
    parser.add_argument('--copy-yaml', action='store_true', help='Copy YAML files to docassemble')
    parser.add_argument('--forms-dir', help='Directory containing forms (if skipping download)')
    args = parser.parse_args()
    
    print("Ontario Family Law Forms Processing Pipeline")
    print("=" * 50)
    
    # Install requirements if needed
    if not args.skip_install:
        try:
            install_requirements()
        except Exception as e:
            print(f"Warning: Could not install all requirements: {e}")
            print("Some features may not be available.")
    
    # Download or use existing forms
    if args.skip_download:
        if args.forms_dir:
            forms_dir = Path(args.forms_dir)
        else:
            forms_dir = Path(__file__).parent / "ontario_forms"
        
        if not forms_dir.exists():
            print(f"Error: Forms directory not found: {forms_dir}")
            return
    else:
        forms_dir = download_forms()
    
    # Parse forms and generate files
    output_dir = parse_forms(forms_dir)
    
    # Validate YAML files
    try:
        validate_yaml_files(output_dir)
    except Exception as e:
        print(f"Warning: YAML validation failed: {e}")
    
    # Generate summary report
    generate_summary_report(output_dir)
    
    # Copy to docassemble if requested
    if args.copy_yaml:
        copy_to_docassemble(output_dir)
    
    print("\n" + "="*50)
    print("Processing Complete!")
    print("="*50)
    print(f"Forms downloaded to: {forms_dir}")
    print(f"CSV files saved to: {output_dir}/csv_files")
    print(f"YAML files saved to: {output_dir}/yaml_files")
    print(f"Summary report: {output_dir}/processing_summary.json")

if __name__ == "__main__":
    main()