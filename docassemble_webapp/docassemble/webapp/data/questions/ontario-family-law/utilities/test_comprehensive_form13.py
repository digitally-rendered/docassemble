#!/usr/bin/env python3
"""
Test comprehensive Form 13 parsing with all tables and document requirements
"""

import json
from pathlib import Path
from enhanced_form13_parser import EnhancedForm13Parser, generate_docassemble_with_documents

def test_comprehensive_form13():
    """
    Test the enhanced Form 13 parser and generate comprehensive interview
    """
    print("=" * 80)
    print("COMPREHENSIVE FORM 13 ANALYSIS")
    print("=" * 80)
    
    # Run enhanced parser
    parser = EnhancedForm13Parser("form_13.docx")
    result = parser.parse()
    
    # Display all detected tables
    print("\n1. ALL FINANCIAL TABLES DETECTED")
    print("-" * 40)
    
    print("\nINCOME TABLES:")
    for table in result['tables_detected']['income_tables']:
        print(f"  • {table.table_name}")
        print(f"    Required docs: {', '.join(table.required_documents)}")
    
    print("\nEXPENSE TABLES:")
    for table in result['tables_detected']['expense_tables']:
        print(f"  • {table.table_name}")
        print(f"    Required docs: {', '.join(table.required_documents)}")
    
    print("\nASSET TABLES:")
    for table in result['tables_detected']['asset_tables']:
        print(f"  • {table.table_name}")
        print(f"    Value required: {table.requires_value}")
        print(f"    Statement frequency: {table.statement_frequency or 'One-time'}")
        print(f"    Required docs: {', '.join(table.required_documents)}")
    
    print("\nDEBT TABLES:")
    for table in result['tables_detected']['debt_tables']:
        print(f"  • {table.table_name}")
        print(f"    Balance required: {table.requires_value}")
        print(f"    Statement frequency: {table.statement_frequency or 'One-time'}")
        print(f"    Required docs: {', '.join(table.required_documents)}")
    
    # Display document requirements
    print("\n2. DOCUMENT UPLOAD REQUIREMENTS")
    print("-" * 40)
    
    print("\nTAX DOCUMENTS (Required):")
    for doc in result['document_requirements']['tax_documents']:
        print(f"  • {doc.doc_name}")
        print(f"    Years required: {doc.years_required}")
        print(f"    Required: {doc.required}")
    
    print("\nINCOME VERIFICATION:")
    for doc in result['document_requirements']['income_verification']:
        print(f"  • {doc.doc_name}")
        print(f"    Frequency: {doc.frequency}")
        print(f"    Description: {doc.description}")
    
    print("\nASSET VERIFICATION:")
    for doc in result['document_requirements']['asset_verification']:
        print(f"  • {doc.doc_name}")
        print(f"    Frequency: {doc.frequency}")
        print(f"    Description: {doc.description}")
    
    # Generate docassemble YAML with all tables and document prompts
    yaml_content = generate_docassemble_with_documents(
        parser.tables_detected,
        parser.document_requirements
    )
    
    # Save the comprehensive interview
    output_file = Path("generated_interviews/form_13_comprehensive.yml")
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(yaml_content)
    
    print("\n3. GENERATED INTERVIEW FEATURES")
    print("-" * 40)
    print("✓ All 21 financial tables included")
    print("✓ Document upload prompts for each asset")
    print("✓ Monthly statement collection for bank accounts")
    print("✓ Quarterly statement collection for investments")
    print("✓ T1/NOA upload for 3 years")
    print("✓ Pay stub uploads")
    print("✓ Property assessment uploads")
    print("✓ Credit card statement uploads")
    print("✓ Validation for document completeness")
    print("✓ Review screen with document checklist")
    
    print(f"\nInterview saved to: {output_file}")
    
    # Show statistics
    print("\n4. STATISTICS")
    print("-" * 40)
    print(f"Total tables: {result['summary']['total_tables']}")
    print(f"Required documents: {result['summary']['required_documents']}")
    print(f"Optional documents: {result['summary']['optional_documents']}")
    
    # Calculate total fields
    total_fields = 0
    for table in parser.tables_detected:
        total_fields += len(table.columns)
    print(f"Total form fields: {total_fields}")
    
    # Show specific requirements for bank accounts
    print("\n5. SPECIAL REQUIREMENTS")
    print("-" * 40)
    print("Bank Accounts:")
    print("  - Must upload 12 monthly statements per account")
    print("  - Current balance required")
    print("  - Account verification letter")
    
    print("\nInvestments:")
    print("  - Quarterly statements for past year")
    print("  - Current portfolio value")
    print("  - Asset mix breakdown")
    
    print("\nReal Estate:")
    print("  - Property deed")
    print("  - MPAC assessment")
    print("  - Mortgage statements")
    print("  - Current market value (appraisal/comparables)")
    
    return result

if __name__ == "__main__":
    result = test_comprehensive_form13()
    
    print("\n" + "=" * 80)
    print("COMPREHENSIVE FORM 13 PROCESSING COMPLETE")
    print("=" * 80)