#!/usr/bin/env python3
"""
Test incremental parser system on a subset of forms
"""

import os
from pathlib import Path
from incremental_parser_system import IncrementalParserSystem

def test_subset():
    """Test on a small subset of forms"""
    system = IncrementalParserSystem()
    
    # Test on just a few forms
    test_forms = [
        "workflow_output/ontario_forms/financial_statements/form_13_-_financial_statement_support_flr-13-may21-en-fil.docx",
        "workflow_output/ontario_forms/applications/form_8_-_application_general_flr-8-jun25-en-fil.docx"
    ]
    
    print("=" * 80)
    print("TESTING INCREMENTAL PARSER SYSTEM")
    print("=" * 80)
    
    for form_path in test_forms:
        if os.path.exists(form_path):
            print(f"\nProcessing: {Path(form_path).name}")
            print("-" * 60)
            
            validation = system.validate_and_improve(form_path)
            
            print(f"Simple parser: {validation['results'].get('simple', 0)} fields")
            print(f"Intelligent parser: {validation['results'].get('intelligent', 0)} fields")
            print(f"Unified parser: {validation['results'].get('unified', 0)} fields")
            
            if 'simple_improved' in validation['results']:
                print(f"Simple improved: {validation['results']['simple_improved']} fields")
            
            print(f"Consistency score: {validation['consistency']['consistency_score']:.2%}")
            print(f"Common fields: {validation['consistency']['common_to_all']}")
            print(f"Improvements learned: {len(validation['improvements'])}")
    
    print("\n" + "=" * 80)
    print("CSV files saved to: parser_results/")
    print("Each parser has its own subdirectory with cached results")

if __name__ == "__main__":
    test_subset()