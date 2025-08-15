#!/usr/bin/env python3
"""
Docassemble Utility: Extract and categorize form fields from Word documents
Specifically designed for Ontario Family Court forms but can be adapted for other forms.
This utility addresses the non-functional form field extraction in docassemble Admin.
"""
from docx import Document
import re

def extract_form_fields(file_path):
    """Extract form fields from the Ontario Family Court Form 8"""
    doc = Document(file_path)
    
    # Define patterns for form fields
    field_patterns = {
        'court_info': ['name of court', 'court office address'],
        'party_info': ['full legal name', 'address', 'phone & fax', 'email'],
        'dates': ['birthdate', 'date', 'since'],
        'marriage_info': ['first name on the day before the marriage', 'married on', 'separated on'],
        'children': ['child', 'birthdate'],
        'claims': ['claim', 'support', 'custody', 'access', 'property'],
        'other': ['reason', 'details', 'facts']
    }
    
    # Extract unique form fields
    form_fields = {category: set() for category in field_patterns}
    
    # Process all tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                text = cell.text.strip().lower()
                if text and len(text) < 200:  # Skip very long text
                    # Check if this looks like a form field
                    if any(indicator in text for indicator in [':', '(', 'name', 'date', 'address', 'phone', 'email']):
                        # Categorize the field
                        categorized = False
                        for category, patterns in field_patterns.items():
                            if any(pattern in text for pattern in patterns):
                                form_fields[category].add(text)
                                categorized = True
                                break
                        
                        if not categorized and len(text) < 100:
                            form_fields['other'].add(text)
    
    return form_fields

def main():
    import sys
    
    # Allow file path as command line argument
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "/Users/draw/Downloads/flr-8-jun25-en.docx"
    
    print(f"Processing: {file_path}")
    fields = extract_form_fields(file_path)
    
    print("ONTARIO FAMILY COURT FORM 8 - IDENTIFIED FORM FIELDS")
    print("=" * 60)
    
    for category, field_set in fields.items():
        if field_set:
            print(f"\n{category.upper().replace('_', ' ')}:")
            print("-" * 30)
            for field in sorted(field_set):
                if len(field) < 100:  # Only show reasonable length fields
                    print(f"  • {field}")
    
    # Count total fields
    total_fields = sum(len(field_set) for field_set in fields.values())
    print(f"\nTOTAL UNIQUE FORM FIELDS IDENTIFIED: {total_fields}")

if __name__ == "__main__":
    main()