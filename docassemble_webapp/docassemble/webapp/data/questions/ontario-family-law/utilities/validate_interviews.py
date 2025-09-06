#!/usr/bin/env python3
"""
Validate all generated Docassemble interviews for YAML syntax
"""

import yaml
import json
from pathlib import Path
import sys

def validate_yaml_file(file_path):
    """Validate a single YAML file"""
    try:
        with open(file_path, 'r') as f:
            # Try to load all documents in the file
            docs = list(yaml.safe_load_all(f))
        return True, f"Valid - {len(docs)} documents"
    except yaml.YAMLError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    """Validate all interview files"""
    base_dir = Path(__file__).parent
    interview_dir = base_dir / "generated_interviews_enhanced"
    
    print("Validating enhanced Docassemble interviews...")
    print("=" * 60)
    
    # Get all YAML files
    yaml_files = sorted(interview_dir.glob("*.yml"))
    
    results = {}
    valid_count = 0
    invalid_count = 0
    
    for yaml_file in yaml_files:
        form_name = yaml_file.stem.replace('_interview_enhanced', '')
        is_valid, message = validate_yaml_file(yaml_file)
        
        if is_valid:
            valid_count += 1
            print(f"✓ {form_name:10} - {message}")
        else:
            invalid_count += 1
            print(f"✗ {form_name:10} - ERROR: {message}")
        
        results[form_name] = {
            'valid': is_valid,
            'message': message,
            'file': str(yaml_file.name)
        }
    
    print("=" * 60)
    print(f"\nValidation Summary:")
    print(f"  Total Files: {len(yaml_files)}")
    print(f"  Valid:       {valid_count}")
    print(f"  Invalid:     {invalid_count}")
    
    if invalid_count > 0:
        print(f"\n⚠️  {invalid_count} files have validation errors")
        print("\nInvalid files:")
        for form_name, result in results.items():
            if not result['valid']:
                print(f"  - {form_name}: {result['message'][:50]}...")
    else:
        print("\n✅ All interviews have valid YAML syntax!")
    
    # Save validation results
    results_file = interview_dir / "validation_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            'total': len(yaml_files),
            'valid': valid_count,
            'invalid': invalid_count,
            'results': results
        }, f, indent=2)
    
    print(f"\nResults saved to: {results_file}")
    
    return 0 if invalid_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
