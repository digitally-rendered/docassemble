#!/usr/bin/env python3
"""
Test GCP-enhanced form parsing
"""

import os
import sys
from pathlib import Path

# Set GCP environment variables
os.environ['GCP_PROJECT_ID'] = 'default-456005'
os.environ['GCP_LOCATION'] = 'us'
os.environ['DOCAI_FORM_PARSER_ID'] = '688d4082bdc65cd2'
os.environ['DOCAI_OCR_PROCESSOR_ID'] = '2a844227b1c7aaea'

from unified_parser_with_gcp import UnifiedFormParser

def test_gcp_parsing(form_path: str):
    """Test parsing with GCP enabled"""
    
    print("=" * 80)
    print("TESTING GCP-ENHANCED FORM PARSING")
    print("=" * 80)
    print(f"Form: {Path(form_path).name}")
    print(f"Project: {os.environ.get('GCP_PROJECT_ID')}")
    print(f"Form Parser ID: {os.environ.get('DOCAI_FORM_PARSER_ID')}")
    print("-" * 80)
    
    # Test without GCP
    print("\n1. Parsing WITHOUT GCP:")
    parser_no_gcp = UnifiedFormParser(form_path, use_gcp=False)
    fields_no_gcp, report_no_gcp = parser_no_gcp.parse_comprehensive()
    
    print(f"   Fields extracted: {len(fields_no_gcp)}")
    print(f"   High confidence: {report_no_gcp['high_confidence']}")
    print(f"   Methods used: {len(set(f.extraction_methods[0] if f.extraction_methods else 'unknown' for f in fields_no_gcp))}")
    
    # Test with GCP
    print("\n2. Parsing WITH GCP:")
    parser_with_gcp = UnifiedFormParser(form_path, use_gcp=True)
    fields_with_gcp, report_with_gcp = parser_with_gcp.parse_comprehensive()
    
    print(f"   Fields extracted: {len(fields_with_gcp)}")
    print(f"   High confidence: {report_with_gcp['high_confidence']}")
    
    # Show extraction methods used
    methods_used = set()
    for field in fields_with_gcp:
        methods_used.update(field.extraction_methods)
    
    print(f"   Methods used: {', '.join(sorted(methods_used))}")
    
    # Compare results
    print("\n3. Comparison:")
    improvement = len(fields_with_gcp) - len(fields_no_gcp)
    print(f"   Additional fields with GCP: {improvement}")
    
    if improvement > 0:
        print("   ✅ GCP enhanced parsing found more fields!")
    elif improvement == 0:
        print("   ℹ️  Same number of fields (GCP may have improved confidence)")
    else:
        print("   ⚠️  Fewer fields with GCP (check for errors)")
    
    # Show sample of GCP-extracted fields
    gcp_methods = ['gcp_documentai', 'gcp_documentai_form', 'gcp_vision', 'gcp_vision_blocks']
    gcp_fields = [f for f in fields_with_gcp if any(m in f.extraction_methods for m in gcp_methods)]
    
    if gcp_fields:
        print(f"\n4. Sample GCP-extracted fields ({len(gcp_fields)} total):")
        for field in gcp_fields[:5]:
            print(f"   - {field.field_label[:50]} ({field.field_type})")
            print(f"     Confidence: {field.consensus_confidence:.2f}")
            print(f"     Methods: {', '.join(field.extraction_methods)}")
    
    # Save results
    import json
    results = {
        'form': str(form_path),
        'no_gcp': {
            'total_fields': len(fields_no_gcp),
            'report': report_no_gcp
        },
        'with_gcp': {
            'total_fields': len(fields_with_gcp),
            'report': report_with_gcp,
            'gcp_fields': len(gcp_fields)
        }
    }
    
    output_file = f"gcp_test_{Path(form_path).stem}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 Results saved to: {output_file}")
    
    return fields_with_gcp, report_with_gcp

if __name__ == "__main__":
    # Test on Form 8 (a complex form)
    test_form = "workflow_output/ontario_forms/applications/form_8_-_application_general_flr-8-jun25-en-fil.docx"
    
    if not os.path.exists(test_form):
        # Try Form 13 as alternative
        test_form = "workflow_output/ontario_forms/financial_statements/form_13_-_financial_statement_support_flr-13-may21-en-fil.docx"
    
    if os.path.exists(test_form):
        fields, report = test_gcp_parsing(test_form)
    else:
        print("Test form not found. Please provide a valid form path.")
        sys.exit(1)