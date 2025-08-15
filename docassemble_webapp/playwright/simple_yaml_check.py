#!/usr/bin/env python3
import json

def check_basic_yaml(filepath):
    """Basic check of YAML structure without yaml module"""
    print("BASIC YAML STRUCTURE CHECK")
    print("==========================\n")
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Basic checks
        issues = []
        
        # Check for tab characters (YAML prefers spaces)
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if '\t' in line:
                issues.append(f"Line {i}: Contains tab character (use spaces)")
        
        # Check for unmatched quotes
        for i, line in enumerate(lines, 1):
            # Count quotes that aren't escaped
            single_quotes = line.count("'") - line.count("\\'")
            double_quotes = line.count('"') - line.count('\\"')
            
            if single_quotes % 2 != 0:
                issues.append(f"Line {i}: Odd number of single quotes")
            if double_quotes % 2 != 0:
                issues.append(f"Line {i}: Odd number of double quotes")
        
        # Check for common YAML issues
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for colons without space after
            if ':' in line and not line.endswith(':'):
                after_colon = line.split(':', 1)[1] if ':' in line else ''
                if after_colon and not after_colon.startswith(' ') and not after_colon.startswith('\n'):
                    if '://' not in line:  # Skip URLs
                        issues.append(f"Line {i}: Missing space after colon")
            
            # Check for lists without space after dash
            if stripped.startswith('-') and len(stripped) > 1:
                if stripped[1] not in ' \t':
                    issues.append(f"Line {i}: Missing space after dash in list")
        
        # Check for consistent indentation
        indent_sizes = set()
        for i, line in enumerate(lines, 1):
            if line and not line.strip().startswith('#'):
                leading_spaces = len(line) - len(line.lstrip())
                if leading_spaces > 0:
                    indent_sizes.add(leading_spaces)
        
        # Check document separators
        doc_count = content.count('\n---\n') + content.count('\n---') 
        print(f"Document blocks found: {doc_count + 1}")
        
        # Check for required sections
        has_metadata = 'metadata:' in content
        has_objects = 'objects:' in content
        has_mandatory = 'mandatory:' in content or 'mandatory: True' in content
        
        print(f"Has metadata: {'✅' if has_metadata else '❌'}")
        print(f"Has objects: {'✅' if has_objects else '❌'}")
        print(f"Has mandatory code: {'✅' if has_mandatory else '❌'}")
        
        if issues:
            print(f"\n⚠️ Found {len(issues)} potential issue(s):")
            for issue in issues[:10]:
                print(f"  - {issue}")
        else:
            print("\n✅ No obvious syntax issues found")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

if __name__ == "__main__":
    filepath = "/Users/draw/development/docassemble/docassemble_webapp/docassemble/webapp/data/questions/ontario-family-law/ontario-family-law-wizard.yml"
    check_basic_yaml(filepath)