#!/usr/bin/env python3
"""
Validate that all parsing methods are cohesively finding the same fields
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import pandas as pd

def load_parser_results(form_path: str) -> Dict[str, List]:
    """Load results from all three parsers for a given form"""
    results = {}
    form_name = Path(form_path).stem
    
    # Check for intelligent parser results
    intelligent_json = f"{form_name}_intelligent.json"
    if os.path.exists(intelligent_json):
        with open(intelligent_json, 'r') as f:
            results['intelligent'] = json.load(f)
    
    # Check for unified parser results
    unified_json = f"validation_results/{form_name}_unified_results.json"
    if os.path.exists(unified_json):
        with open(unified_json, 'r') as f:
            data = json.load(f)
            results['unified'] = data.get('fields', [])
    
    # Check for simple parser results (from parse_forms_from_list.py)
    simple_csv = "ontario_forms_parsed.csv"
    if os.path.exists(simple_csv):
        df = pd.read_csv(simple_csv)
        form_rows = df[df['form_path'].str.contains(form_name, na=False)]
        if not form_rows.empty:
            # Reconstruct field data from CSV
            fields = []
            for _, row in form_rows.iterrows():
                if pd.notna(row['field_name']):
                    fields.append({
                        'field_name': row['field_name'],
                        'field_type': row['field_type'],
                        'field_label': row.get('field_label', ''),
                        'confidence': 0.5  # Default confidence
                    })
            results['simple'] = fields
    
    return results

def normalize_field(field: Dict) -> Tuple[str, str]:
    """Normalize a field for comparison"""
    # Get core field properties
    field_type = field.get('field_type', 'text').lower()
    field_label = field.get('field_label', '').lower()
    
    # Clean up label
    field_label = field_label.replace('\u2002', ' ')  # Unicode space
    field_label = ' '.join(field_label.split())  # Normalize whitespace
    field_label = field_label[:50]  # Truncate for comparison
    
    return (field_type, field_label)

def compare_parsers(form_path: str) -> Dict:
    """Compare results from different parsers"""
    results = load_parser_results(form_path)
    
    if not results:
        return {'error': 'No parser results found'}
    
    comparison = {
        'form': form_path,
        'parser_counts': {},
        'common_fields': [],
        'unique_fields': defaultdict(list),
        'field_type_agreement': {},
        'consistency_score': 0.0
    }
    
    # Get field sets from each parser
    field_sets = {}
    for parser_name, fields in results.items():
        comparison['parser_counts'][parser_name] = len(fields)
        field_sets[parser_name] = set()
        
        for field in fields:
            normalized = normalize_field(field)
            field_sets[parser_name].add(normalized)
    
    # Find common fields across all parsers
    if len(field_sets) > 1:
        common = set.intersection(*field_sets.values())
        comparison['common_fields'] = list(common)
        
        # Find unique fields per parser
        for parser_name, fields in field_sets.items():
            unique = fields - common
            comparison['unique_fields'][parser_name] = list(unique)[:10]  # Limit to 10 for readability
        
        # Calculate consistency score
        total_unique = sum(len(s) for s in field_sets.values())
        if total_unique > 0:
            comparison['consistency_score'] = len(common) * len(field_sets) / total_unique
    
    # Check field type agreement for common fields
    if comparison['common_fields']:
        for parser_name, fields in results.items():
            type_counts = defaultdict(int)
            for field in fields:
                field_type = field.get('field_type', 'text')
                type_counts[field_type] += 1
            comparison['field_type_agreement'][parser_name] = dict(type_counts)
    
    return comparison

def validate_all_forms(forms_dir: str = "workflow_output/ontario_forms") -> List[Dict]:
    """Validate all forms in the directory"""
    validations = []
    
    # Find all forms
    for root, dirs, files in os.walk(forms_dir):
        for file in files:
            if file.lower().endswith(('.docx', '.pdf')):
                form_path = os.path.join(root, file)
                print(f"Validating: {file}")
                validation = compare_parsers(form_path)
                validations.append(validation)
    
    return validations

def generate_report(validations: List[Dict]) -> str:
    """Generate a validation report"""
    report = []
    report.append("=" * 80)
    report.append("PARSER CONSISTENCY VALIDATION REPORT")
    report.append("=" * 80)
    report.append("")
    
    # Summary statistics
    total_forms = len(validations)
    forms_with_results = sum(1 for v in validations if 'error' not in v)
    avg_consistency = sum(v.get('consistency_score', 0) for v in validations) / max(1, forms_with_results)
    
    report.append(f"Total forms analyzed: {total_forms}")
    report.append(f"Forms with parser results: {forms_with_results}")
    report.append(f"Average consistency score: {avg_consistency:.2%}")
    report.append("")
    
    # Parser coverage
    parser_coverage = defaultdict(int)
    for v in validations:
        for parser in v.get('parser_counts', {}).keys():
            parser_coverage[parser] += 1
    
    report.append("Parser Coverage:")
    for parser, count in parser_coverage.items():
        report.append(f"  {parser}: {count} forms")
    report.append("")
    
    # Detailed results for each form
    report.append("-" * 80)
    report.append("DETAILED RESULTS BY FORM")
    report.append("-" * 80)
    
    for validation in validations:
        if 'error' in validation:
            continue
            
        form_name = Path(validation['form']).name
        report.append(f"\n{form_name}")
        report.append("=" * len(form_name))
        
        # Field counts
        report.append("Field counts by parser:")
        for parser, count in validation['parser_counts'].items():
            report.append(f"  {parser}: {count} fields")
        
        # Common fields
        common_count = len(validation['common_fields'])
        report.append(f"Common fields across parsers: {common_count}")
        
        # Consistency score
        report.append(f"Consistency score: {validation['consistency_score']:.2%}")
        
        # Field type distribution
        if validation['field_type_agreement']:
            report.append("Field type distribution:")
            for parser, types in validation['field_type_agreement'].items():
                type_str = ", ".join(f"{t}:{c}" for t, c in types.items())
                report.append(f"  {parser}: {type_str}")
        
        # Unique fields sample
        for parser, unique in validation['unique_fields'].items():
            if unique:
                report.append(f"Unique to {parser} (sample): {len(unique)} fields")
                for field in unique[:3]:  # Show first 3
                    report.append(f"    - {field}")
    
    # Recommendations
    report.append("")
    report.append("-" * 80)
    report.append("RECOMMENDATIONS")
    report.append("-" * 80)
    
    if avg_consistency < 0.5:
        report.append("⚠️  Low consistency detected. Consider:")
        report.append("  - Review field detection patterns")
        report.append("  - Adjust confidence thresholds")
        report.append("  - Implement field normalization")
    elif avg_consistency < 0.8:
        report.append("ℹ️  Moderate consistency. Consider:")
        report.append("  - Fine-tune field extraction patterns")
        report.append("  - Add more parsing strategies")
    else:
        report.append("✅ Good consistency across parsers!")
    
    return "\n".join(report)

def main():
    """Main validation function"""
    print("Starting parser consistency validation...")
    
    # Run validation on all forms
    validations = validate_all_forms()
    
    # Generate report
    report = generate_report(validations)
    
    # Save report
    with open("parser_consistency_report.txt", "w") as f:
        f.write(report)
    
    # Print report
    print(report)
    
    # Save detailed JSON results
    with open("parser_consistency_data.json", "w") as f:
        json.dump(validations, f, indent=2)
    
    print("\n" + "=" * 80)
    print("Validation complete!")
    print("Report saved to: parser_consistency_report.txt")
    print("Detailed data saved to: parser_consistency_data.json")

if __name__ == "__main__":
    main()