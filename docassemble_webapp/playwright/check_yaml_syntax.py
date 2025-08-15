#!/usr/bin/env python3
import yaml
import sys
import re

def check_yaml_syntax(filepath):
    """Check YAML syntax using Python's yaml parser"""
    print("CHECKING YAML SYNTAX WITH PYTHON")
    print("=================================\n")
    
    try:
        with open(filepath, 'r') as file:
            content = file.read()
            
        # Split by document separator
        documents = re.split(r'^---$', content, flags=re.MULTILINE)
        
        doc_count = 0
        errors = []
        
        for i, doc in enumerate(documents):
            if doc.strip():
                doc_count += 1
                try:
                    # Try to parse the YAML document
                    yaml.safe_load(doc)
                    print(f"Document {doc_count}: ✅ Valid YAML syntax")
                except yaml.YAMLError as e:
                    print(f"Document {doc_count}: ❌ Invalid YAML")
                    print(f"Error: {e}")
                    errors.append((doc_count, str(e)))
                    
                    # Try to extract more details
                    if hasattr(e, 'problem_mark'):
                        mark = e.problem_mark
                        print(f"  Line: {mark.line + 1}, Column: {mark.column + 1}")
                        
                        # Show the problematic line
                        lines = doc.split('\n')
                        if mark.line < len(lines):
                            print(f"  Problem line: {lines[mark.line]}")
                            print(f"  {' ' * mark.column}^")
        
        print(f"\nTotal documents: {doc_count}")
        
        if errors:
            print(f"\n⚠️ Found {len(errors)} error(s)")
            return False
        else:
            print("\n✅ All YAML documents are valid")
            return True
            
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_docassemble_specific(filepath):
    """Check for Docassemble-specific issues"""
    print("\nCHECKING DOCASSEMBLE-SPECIFIC SYNTAX")
    print("=====================================\n")
    
    try:
        with open(filepath, 'r') as file:
            content = file.read()
            
        issues = []
        
        # Check for common Docassemble issues
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for tabs vs spaces (Docassemble prefers spaces)
            if '\t' in line and not line.strip().startswith('#'):
                issues.append(f"Line {i}: Contains tabs (use spaces instead)")
            
            # Check for validation code indentation
            if 'validation code:' in line:
                if i < len(lines):
                    next_line = lines[i]
                    if next_line and not next_line.startswith('      '):
                        issues.append(f"Line {i+1}: Validation code must be indented properly")
            
            # Check for undefined functions
            if 'validation_error(' in line:
                # This is a Docassemble built-in, should be fine
                pass
                
            # Check for proper field syntax
            if line.strip().startswith('- "') and ':' in line:
                # This is a field definition
                if 'validation code:' in line and '|' not in lines[i] if i < len(lines) else True:
                    issues.append(f"Line {i}: Validation code needs | for multi-line")
        
        # Check for required includes
        if 'Individual' in content or 'Person' in content:
            if 'docassemble.base:data/questions/basic-questions.yml' not in content:
                print("⚠️ Using Individual/Person objects but basic-questions.yml might not be included")
        
        # Check for Address objects
        if 'Address' in content:
            if 'court.address: Address' in content:
                print("✅ Address object properly defined for court")
        
        if issues:
            print(f"Found {len(issues)} potential issue(s):")
            for issue in issues[:10]:  # Show first 10 issues
                print(f"  - {issue}")
        else:
            print("✅ No obvious Docassemble-specific issues found")
            
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ Error checking Docassemble syntax: {e}")
        return False

if __name__ == "__main__":
    filepath = "/Users/draw/development/docassemble/docassemble_webapp/docassemble/webapp/data/questions/ontario-family-law/ontario-family-law-wizard.yml"
    
    yaml_valid = check_yaml_syntax(filepath)
    da_valid = check_docassemble_specific(filepath)
    
    print("\n=================================")
    if yaml_valid and da_valid:
        print("✅ File appears to be valid")
    else:
        print("❌ File has issues that need fixing")
    
    sys.exit(0 if (yaml_valid and da_valid) else 1)