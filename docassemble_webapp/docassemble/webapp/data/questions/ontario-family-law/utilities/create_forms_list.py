#!/usr/bin/env python3
"""
Create a list of all downloaded Ontario family law forms (PDF and DOCX)
"""

import os
import json
from pathlib import Path
from typing import List, Dict

def find_all_forms(base_dir: str = "workflow_output/ontario_forms") -> List[Dict[str, str]]:
    """
    Find all PDF and DOCX files in the ontario_forms directory
    
    Returns:
        List of dictionaries containing form information
    """
    forms = []
    base_path = Path(base_dir)
    
    if not base_path.exists():
        print(f"Directory {base_path} does not exist")
        return forms
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.lower().endswith(('.pdf', '.docx', '.doc')):
                file_path = Path(root) / file
                relative_path = file_path.relative_to(base_path)
                category = relative_path.parts[0] if len(relative_path.parts) > 1 else "uncategorized"
                
                # Extract form number from filename
                form_number = extract_form_number(file)
                
                forms.append({
                    "filename": file,
                    "full_path": str(file_path),
                    "relative_path": str(relative_path),
                    "category": category,
                    "form_number": form_number,
                    "extension": file_path.suffix.lower()
                })
    
    # Sort by form number
    forms.sort(key=lambda x: x.get("form_number", ""))
    
    return forms

def extract_form_number(filename: str) -> str:
    """
    Extract form number from filename
    
    Examples:
        form_8_-_application_general_flr-8-jun25-en.docx -> 8
        form_13.1_-_financial_statement_property_flr-13-1-may21-en-fil.docx -> 13.1
    """
    import re
    
    # Try to match form_XX pattern
    match = re.search(r'form[_\-](\d+(?:\.\d+)?[a-zA-Z]?)', filename.lower())
    if match:
        return match.group(1).upper()
    
    # Try to match flr-XX pattern
    match = re.search(r'flr[_\-](\d+(?:\.\d+)?[a-zA-Z]?)', filename.lower())
    if match:
        return match.group(1).upper()
    
    return ""

def save_forms_list(forms: List[Dict[str, str]], output_file: str = "forms_list.json"):
    """
    Save the forms list to a JSON file
    """
    output_path = Path(output_file)
    
    with open(output_path, 'w') as f:
        json.dump({
            "total_forms": len(forms),
            "forms": forms,
            "categories": list(set(f["category"] for f in forms)),
            "file_types": {
                "pdf": len([f for f in forms if f["extension"] == ".pdf"]),
                "docx": len([f for f in forms if f["extension"] == ".docx"]),
                "doc": len([f for f in forms if f["extension"] == ".doc"])
            }
        }, f, indent=2)
    
    print(f"Forms list saved to {output_path}")
    return output_path

def save_forms_csv(forms: List[Dict[str, str]], output_file: str = "forms_list.csv"):
    """
    Save the forms list to a CSV file
    """
    import csv
    
    output_path = Path(output_file)
    
    with open(output_path, 'w', newline='') as f:
        if forms:
            writer = csv.DictWriter(f, fieldnames=forms[0].keys())
            writer.writeheader()
            writer.writerows(forms)
    
    print(f"Forms CSV saved to {output_path}")
    return output_path

def print_forms_summary(forms: List[Dict[str, str]]):
    """
    Print a summary of found forms
    """
    print("\n" + "="*60)
    print("ONTARIO FAMILY LAW FORMS - DOWNLOADED FILES")
    print("="*60)
    
    # Group by category
    categories = {}
    for form in forms:
        category = form["category"]
        if category not in categories:
            categories[category] = []
        categories[category].append(form)
    
    # Print by category
    for category, category_forms in sorted(categories.items()):
        print(f"\n📁 {category.replace('_', ' ').title()}")
        print("-" * 40)
        for form in category_forms:
            form_num = form["form_number"] or "N/A"
            ext = form["extension"].upper()[1:]
            print(f"  Form {form_num:6s} - {form['filename'][:50]:50s} [{ext}]")
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("-" * 40)
    print(f"Total forms found: {len(forms)}")
    print(f"Categories: {len(categories)}")
    print(f"PDF files: {len([f for f in forms if f['extension'] == '.pdf'])}")
    print(f"DOCX files: {len([f for f in forms if f['extension'] == '.docx'])}")
    print("="*60)

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Create a list of all downloaded Ontario family law forms"
    )
    parser.add_argument(
        "--input-dir",
        default="workflow_output/ontario_forms",
        help="Directory containing downloaded forms"
    )
    parser.add_argument(
        "--output-json",
        default="forms_list.json",
        help="Output JSON file"
    )
    parser.add_argument(
        "--output-csv",
        default="forms_list.csv",
        help="Output CSV file"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed information"
    )
    
    args = parser.parse_args()
    
    # Find all forms
    forms = find_all_forms(args.input_dir)
    
    if not forms:
        print(f"No forms found in {args.input_dir}")
        return
    
    # Save to JSON
    save_forms_list(forms, args.output_json)
    
    # Save to CSV
    save_forms_csv(forms, args.output_csv)
    
    # Print summary
    if args.verbose:
        print_forms_summary(forms)
    else:
        print(f"\nFound {len(forms)} forms in {args.input_dir}")
        print(f"Lists saved to {args.output_json} and {args.output_csv}")

if __name__ == "__main__":
    main()