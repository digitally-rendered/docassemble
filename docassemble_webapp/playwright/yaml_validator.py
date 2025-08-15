#!/usr/bin/env python3
"""
YAML Validator - Check for syntax errors in the wizard file
"""
import yaml
import sys
import traceback

def validate_yaml_file(filepath):
    """Validate YAML file and report any syntax errors"""
    try:
        print(f"Validating: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Try to parse the YAML
        docs = list(yaml.safe_load_all(content))
        
        print(f"✅ YAML syntax is valid")
        print(f"📄 Found {len(docs)} documents")
        
        # Check for common Docassemble issues
        issues = []
        
        for i, doc in enumerate(docs):
            if doc is None:
                continue
                
            # Check for common problems
            if isinstance(doc, dict):
                # Check for invalid keys or structures
                if 'objects' in doc:
                    objects = doc['objects']
                    if isinstance(objects, list):
                        for obj in objects:
                            if isinstance(obj, str) and ':' not in obj:
                                issues.append(f"Document {i}: Object '{obj}' missing type definition")
                
                # Check for validation code issues
                if 'fields' in doc:
                    fields = doc['fields']
                    if isinstance(fields, list):
                        for field in fields:
                            if isinstance(field, dict) and 'validation code' in field:
                                # This is where validation code syntax would be checked
                                # But we can't execute it without Docassemble context
                                pass
        
        if issues:
            print("⚠️  Potential issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ No obvious structural issues detected")
            
        return True
        
    except yaml.YAMLError as e:
        print(f"❌ YAML syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error validating file: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Test the original wizard file
    wizard_path = "/Users/draw/development/docassemble/docassemble_webapp/docassemble/webapp/data/questions/ontario-family-law/ontario-family-law-wizard.yml"
    
    print("YAML Validation Results:")
    print("=" * 50)
    
    result = validate_yaml_file(wizard_path)
    
    if not result:
        print("\n🔧 Suggestion: Check for:")
        print("  - Missing colons after field names")
        print("  - Incorrect indentation")
        print("  - Unescaped special characters")
        print("  - Missing quotes around strings with special chars")
        sys.exit(1)
    else:
        print("\n✅ YAML structure appears valid")
        print("🔍 Issue is likely Docassemble-specific (objects, validation, etc.)")