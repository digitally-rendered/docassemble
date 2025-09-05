#!/usr/bin/env python3
import yaml
import sys

def check_yaml_file(filename):
    """Check YAML file for syntax errors and extract code blocks."""
    
    with open(filename, 'r') as f:
        content = f.read()
    
    # Parse YAML documents
    try:
        documents = list(yaml.safe_load_all(content))
        print(f"✓ YAML syntax is valid - {len(documents)} blocks found")
    except yaml.YAMLError as e:
        print(f"✗ YAML syntax error: {e}")
        return False
    
    # Look for validation code blocks
    validation_blocks = []
    code_blocks = []
    
    for i, doc in enumerate(documents):
        if doc and isinstance(doc, dict):
            if 'validation code' in doc:
                validation_blocks.append((i, doc['validation code']))
            if 'code' in doc:
                code_blocks.append((i, doc['code']))
    
    print(f"\nFound {len(code_blocks)} code blocks")
    print(f"Found {len(validation_blocks)} validation code blocks")
    
    # Check for common issues
    print("\nChecking for common issues:")
    
    # Check for duplicate imports in validation blocks
    for i, code in validation_blocks:
        lines = code.strip().split('\n')
        imports = [line for line in lines if line.strip().startswith('import ')]
        if len(imports) > 1:
            print(f"  Block {i}: Multiple import statements found - {imports}")
    
    # Check for undefined function calls
    all_code = '\n'.join([code for _, code in code_blocks])
    if 'validate_postal_code_field(' in content:
        if 'def validate_postal_code_field' not in all_code:
            print("  ✗ Function validate_postal_code_field is called but not defined in code blocks")
        else:
            print("  ✓ Function validate_postal_code_field is defined")
    
    # Check for syntax in validation blocks
    print("\nChecking Python syntax in validation blocks:")
    for i, code in validation_blocks:
        try:
            compile(code, f'<validation_block_{i}>', 'exec')
            print(f"  Block {i}: ✓ Valid Python syntax")
        except SyntaxError as e:
            print(f"  Block {i}: ✗ Syntax error: {e}")
            print(f"    Line {e.lineno}: {e.text}")
    
    return True

if __name__ == '__main__':
    filename = '/Users/draw/development/docassemble/docassemble_webapp/docassemble/webapp/data/questions/ontario-family-law/common_intake_final.yml'
    check_yaml_file(filename)