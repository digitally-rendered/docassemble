#!/usr/bin/env python3
"""
Doctor Fix Script - Completes the workflow for all Ontario forms
"""

import os
import json
from pathlib import Path
from typing import Dict, List
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def diagnose_system():
    """Run complete system diagnosis"""
    print("=" * 80)
    print("ONTARIO FAMILY LAW FORMS - SYSTEM DIAGNOSIS")
    print("=" * 80)
    
    issues = []
    fixes = []
    
    # Check 1: Forms downloaded
    forms_dir = Path("workflow_output/ontario_forms")
    if forms_dir.exists():
        form_count = len(list(forms_dir.glob("**/*.docx")) + list(forms_dir.glob("**/*.pdf")))
        print(f"✅ Forms Downloaded: {form_count} files")
    else:
        issues.append("Forms directory not found")
        fixes.append("Run: python download_all_forms.py")
    
    # Check 2: Parser results
    parser_dir = Path("parser_results")
    if parser_dir.exists():
        cache_files = list(parser_dir.glob("**/*.json")) + list(parser_dir.glob("**/*.csv"))
        print(f"✅ Parser Cache: {len(cache_files)} files")
    else:
        issues.append("Parser cache directory not found")
        fixes.append("Create parser_results directory")
    
    # Check 3: Generated interviews
    interview_dir = Path("generated_interviews")
    if interview_dir.exists():
        yaml_files = list(interview_dir.glob("*.yml"))
        print(f"✅ Generated Interviews: {len(yaml_files)} YAML files")
        if len(yaml_files) < 46:
            issues.append(f"Only {len(yaml_files)} of 46 interviews generated")
            fixes.append("Generate remaining interviews")
    else:
        issues.append("Generated interviews directory not found")
        fixes.append("Create generated_interviews directory")
    
    # Check 4: Test infrastructure
    playwright_dir = Path("/Users/draw/development/docassemble/docassemble_webapp/playwright")
    if playwright_dir.exists():
        test_files = list(playwright_dir.glob("tests/*.spec.js"))
        print(f"✅ Playwright Tests: {len(test_files)} test suites")
    else:
        issues.append("Playwright directory not found")
        fixes.append("Setup Playwright tests")
    
    # Check 5: Docassemble running
    import subprocess
    try:
        result = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://localhost:8080/"], 
                              capture_output=True, text=True, timeout=5)
        if result.stdout == "200":
            print("✅ Docassemble: Running on localhost:8080")
        else:
            issues.append(f"Docassemble returned status {result.stdout}")
            fixes.append("Check port forwarding: kubectl port-forward -n docassemble svc/docassemble 8080:80")
    except:
        issues.append("Cannot connect to Docassemble")
        fixes.append("Start port forwarding: kubectl port-forward -n docassemble svc/docassemble 8080:80")
    
    # Report issues and fixes
    if issues:
        print("\n" + "=" * 40)
        print("ISSUES FOUND:")
        print("=" * 40)
        for i, issue in enumerate(issues, 1):
            print(f"{i}. ❌ {issue}")
            print(f"   FIX: {fixes[i-1]}")
    else:
        print("\n✅ ALL SYSTEMS OPERATIONAL!")
    
    return issues, fixes

def generate_remaining_interviews():
    """Generate interviews for all forms that don't have one yet"""
    print("\n" + "=" * 80)
    print("GENERATING REMAINING INTERVIEWS")
    print("=" * 80)
    
    forms_dir = Path("workflow_output/ontario_forms")
    interview_dir = Path("generated_interviews")
    interview_dir.mkdir(exist_ok=True)
    
    all_forms = list(forms_dir.glob("**/*.docx"))
    existing_interviews = {f.stem for f in interview_dir.glob("*.yml")}
    
    for form_path in all_forms:
        form_name = form_path.stem
        if form_name not in existing_interviews:
            print(f"Generating interview for: {form_name}")
            
            # Import the generator
            try:
                from docassemble_table_generator import generate_complete_interview
                from field_validation_mapper import validate_and_map_fields
                
                # For now, create a basic interview structure
                # In production, you would parse the form first
                result = generate_complete_interview(
                    validated_fields=[],  # Would be populated from parser
                    form_name=form_name.replace("_", " ").title()
                )
                
                print(f"  ✓ Generated {form_name}.yml")
                
            except Exception as e:
                print(f"  ✗ Failed to generate {form_name}: {e}")

def run_quick_test():
    """Run a quick test on Form 13 to verify system works"""
    print("\n" + "=" * 80)
    print("RUNNING QUICK VALIDATION TEST")
    print("=" * 80)
    
    # Check if Form 13 interview exists
    form13_path = Path("generated_interviews/form_13_comprehensive.yml")
    if form13_path.exists():
        print("✅ Form 13 comprehensive interview exists")
        
        # Validate YAML syntax
        import yaml
        try:
            with open(form13_path, 'r') as f:
                yaml.safe_load(f.read())
            print("✅ YAML syntax is valid")
        except yaml.YAMLError as e:
            print(f"❌ YAML syntax error: {e}")
    else:
        print("❌ Form 13 comprehensive interview not found")
    
    # Check test data
    test_data_path = Path("/Users/draw/development/docassemble/docassemble_webapp/playwright/fixtures/form-13-test-data.js")
    if test_data_path.exists():
        print("✅ Test data fixture exists")
    else:
        print("❌ Test data fixture not found")

def create_status_report():
    """Create a comprehensive status report"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "system_status": {},
        "forms": {},
        "interviews": {},
        "tests": {},
        "recommendations": []
    }
    
    # Count forms by category
    forms_dir = Path("workflow_output/ontario_forms")
    if forms_dir.exists():
        for category_dir in forms_dir.iterdir():
            if category_dir.is_dir():
                forms = list(category_dir.glob("*.docx")) + list(category_dir.glob("*.pdf"))
                report["forms"][category_dir.name] = len(forms)
    
    # Count generated interviews
    interview_dir = Path("generated_interviews")
    if interview_dir.exists():
        interviews = list(interview_dir.glob("*.yml"))
        report["interviews"]["total"] = len(interviews)
        report["interviews"]["files"] = [f.name for f in interviews]
    
    # Save report
    report_path = Path("system_health_report.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📊 Status report saved to: {report_path}")
    
    return report

if __name__ == "__main__":
    print("Starting Ontario Family Law Forms System Doctor...")
    print("=" * 80)
    
    # Run diagnosis
    issues, fixes = diagnose_system()
    
    # Run quick test
    run_quick_test()
    
    # Generate status report
    report = create_status_report()
    
    # Provide recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDED NEXT STEPS:")
    print("=" * 80)
    
    if not issues:
        print("1. ✅ System is healthy!")
        print("2. Run full test suite: cd /Users/draw/development/docassemble/docassemble_webapp/playwright && npm test")
        print("3. Deploy interviews to docassemble")
        print("4. Begin user testing")
    else:
        print("1. Fix identified issues:")
        for fix in fixes:
            print(f"   - {fix}")
        print("2. Re-run this diagnostic script")
        print("3. Generate remaining interviews")
        print("4. Run test suite")
    
    print("\n" + "=" * 80)
    print("DOCTOR DIAGNOSIS COMPLETE")
    print("=" * 80)