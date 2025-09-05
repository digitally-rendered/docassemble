#!/usr/bin/env python3
"""
Test the incremental YAML files to ensure they're valid
"""

import yaml
from pathlib import Path

def test_yaml_validity():
    """Test all incremental YAML files for validity"""
    
    interviews_dir = Path('incremental_interviews')
    
    if not interviews_dir.exists():
        print("❌ incremental_interviews directory not found")
        return False
    
    yaml_files = list(interviews_dir.glob('*.yml'))
    
    if not yaml_files:
        print("❌ No YAML files found")
        return False
    
    all_valid = True
    
    for yaml_file in sorted(yaml_files):
        try:
            with open(yaml_file, 'r') as f:
                content = f.read()
                
            # Try to parse the YAML
            documents = list(yaml.safe_load_all(content))
            
            print(f"✓ {yaml_file.name} - Valid YAML ({len(documents)} documents)")
            
        except yaml.YAMLError as e:
            print(f"❌ {yaml_file.name} - Invalid YAML: {e}")
            all_valid = False
        except Exception as e:
            print(f"❌ {yaml_file.name} - Error: {e}")
            all_valid = False
    
    return all_valid


def main():
    """Run YAML validation tests"""
    print("=" * 60)
    print("TESTING INCREMENTAL YAML FILES")
    print("=" * 60)
    
    if test_yaml_validity():
        print("\n✅ All YAML files are valid!")
    else:
        print("\n❌ Some YAML files have issues")
    
    print("\nTo test in Docassemble, visit:")
    print("  /interview?i=docassemble.webapp:ontario-family-law/utilities/incremental_interviews/00_stage_index.yml")


if __name__ == "__main__":
    main()