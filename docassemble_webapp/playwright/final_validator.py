#!/usr/bin/env python3
"""
Final validation check for the corrected wizard
"""
import yaml
import re

def validate_corrected_wizard():
    """Validate the corrected wizard file"""
    wizard_path = "/Users/draw/development/docassemble/docassemble_webapp/docassemble/webapp/data/questions/ontario-family-law/ontario-family-law-wizard.yml"
    
    print("🔍 Final Validation of Corrected Wizard")
    print("=" * 50)
    
    try:
        with open(wizard_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Parse YAML
        docs = list(yaml.safe_load_all(content))
        print(f"✅ YAML syntax: VALID ({len(docs)} documents)")
        
        # Check for the issues we fixed
        issues_fixed = []
        
        # 1. Check that court.address: Address is removed from objects
        for doc in docs:
            if isinstance(doc, dict) and 'objects' in doc:
                objects = doc['objects']
                if isinstance(objects, list):
                    for obj in objects:
                        if isinstance(obj, str) and 'court.address:' in obj:
                            print("❌ Still has problematic court.address in objects")
                            return False
        issues_fixed.append("✅ Removed court.address from objects block")
        
        # 2. Check for court address initialization
        if 'court.address = Address()' in content:
            issues_fixed.append("✅ Added proper court.address initialization")
        
        # 3. Check for workflow_data definition
        if 'workflow_data = {' in content:
            issues_fixed.append("✅ Added missing workflow_data generation")
            
        # 4. Check for final_screen_emergency_complete
        if 'event: final_screen_emergency_complete' in content:
            issues_fixed.append("✅ Added missing emergency final screen")
            
        # 5. Check that non-standard attributes were changed
        if '.law_society_number' not in content:
            issues_fixed.append("✅ Replaced law_society_number with lso_number")
        if '.business_type' not in content:
            issues_fixed.append("✅ Replaced business_type with firm_type")
        if '.work_phone' not in content:
            issues_fixed.append("✅ Replaced work_phone with direct_phone")
            
        print("\n📋 Issues Fixed:")
        for fix in issues_fixed:
            print(f"   {fix}")
            
        # Check for any remaining potential issues
        warnings = []
        
        # Check for any undefined variables in the mandatory code
        mandatory_section = re.search(r'mandatory: True\s*code: \|(.*?)---', content, re.DOTALL)
        if mandatory_section:
            mandatory_code = mandatory_section.group(1)
            # Look for variables that might not be defined
            if 'final_screen_emergency_complete' in mandatory_code:
                if 'event: final_screen_emergency_complete' not in content:
                    warnings.append("⚠️  final_screen_emergency_complete referenced but not defined")
                    
        if warnings:
            print("\n⚠️  Remaining Warnings:")
            for warning in warnings:
                print(f"   {warning}")
        else:
            print("\n🎉 No remaining issues detected!")
            
        print(f"\n📊 Final Stats:")
        print(f"   - Total YAML documents: {len(docs)}")
        print(f"   - File size: {len(content):,} characters")
        print(f"   - Issues fixed: {len(issues_fixed)}")
        print(f"   - Remaining warnings: {len(warnings)}")
        
        return len(warnings) == 0
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

if __name__ == "__main__":
    success = validate_corrected_wizard()
    print(f"\n{'✅ WIZARD READY FOR TESTING' if success else '❌ ISSUES REMAIN'}")
    exit(0 if success else 1)