#!/usr/bin/env python3
"""
System Validator Agent
Validates the complete generated system for quality and correctness.
"""

import os
import json
from datetime import datetime

def validate_framework():
    """Validate common framework was generated"""
    framework_dir = 'common_interview_framework'
    required_files = [
        'base_objects.py',
        'validation_functions.py', 
        'master_interview.py'
    ]
    
    issues = []
    for file in required_files:
        if not os.path.exists(os.path.join(framework_dir, file)):
            issues.append(f"Missing framework file: {file}")
    
    return issues

def validate_interviews():
    """Validate generated interviews"""
    interviews_dir = 'generated_interviews'
    if not os.path.exists(interviews_dir):
        return ["Generated interviews directory not found"]
    
    interview_files = [f for f in os.listdir(interviews_dir) if f.endswith('.yml')]
    issues = []
    
    if len(interview_files) == 0:
        issues.append("No interview files generated")
    
    return issues

def main():
    """Run complete system validation"""
    print("🔍 Running system validation...")
    
    all_issues = []
    
    # Validate framework
    framework_issues = validate_framework()
    all_issues.extend(framework_issues)
    
    # Validate interviews  
    interview_issues = validate_interviews()
    all_issues.extend(interview_issues)
    
    # Generate validation report
    report = {
        'validation_date': datetime.now().isoformat(),
        'total_issues': len(all_issues),
        'issues': all_issues,
        'status': 'PASS' if len(all_issues) == 0 else 'FAIL'
    }
    
    with open('validation_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    if len(all_issues) == 0:
        print("✅ System validation passed")
    else:
        print(f"❌ System validation failed with {len(all_issues)} issues")
        for issue in all_issues:
            print(f"  • {issue}")

if __name__ == '__main__':
    main()
