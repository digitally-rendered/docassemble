#!/usr/bin/env python3
"""
Parser Comparison Analysis
Compares results from different parsing approaches
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from collections import Counter
import re

def analyze_field_quality(field: Dict) -> Dict[str, Any]:
    """Analyze quality of a single field"""
    
    field_name = field.get('field_name', '')
    field_label = field.get('field_label', '')
    
    quality = {
        'has_meaningful_name': not re.match(r'^(field_|text_field_|dropdown_field)', field_name),
        'has_descriptive_label': len(field_label) > 5 and not re.match(r'^Field \d+$', field_label),
        'has_duplicate_label': field_label.count(':') > 2 or 'Name: Name:' in field_label,
        'has_confidence_score': 'confidence' in field,
        'confidence_value': field.get('confidence', 0),
        'has_validation': field.get('validation_status') == 'valid',
        'has_field_type': field.get('field_type') and field.get('field_type') != 'text'
    }
    
    # Calculate overall quality score
    quality['score'] = sum([
        quality['has_meaningful_name'] * 3,
        quality['has_descriptive_label'] * 3,
        not quality['has_duplicate_label'] * 2,
        quality['has_confidence_score'] * 1,
        quality['confidence_value'] * 2,
        quality['has_validation'] * 1,
        quality['has_field_type'] * 1
    ]) / 13  # Normalize to 0-1
    
    return quality

def compare_parsers():
    """Compare different parser outputs"""
    
    results = {}
    
    # Load original basic parser results
    basic_file = Path('parsed_forms/form_8_fields.json')
    if basic_file.exists():
        with open(basic_file, 'r') as f:
            data = json.load(f)
            results['basic'] = {
                'fields': data if isinstance(data, list) else data.get('fields', []),
                'source': 'Original basic parser'
            }
    
    # Load improved parser results
    improved_file = Path('parsed_forms/form_8_improved.json')
    if improved_file.exists():
        with open(improved_file, 'r') as f:
            data = json.load(f)
            results['improved'] = {
                'fields': data.get('fields', []),
                'source': 'Improved parser'
            }
    
    # Load enhanced parser results
    enhanced_file = Path('parsed_forms/form_8_fields_enhanced.json')
    if enhanced_file.exists():
        with open(enhanced_file, 'r') as f:
            data = json.load(f)
            results['enhanced'] = {
                'fields': data.get('fields', []),
                'source': 'Enhanced parser with label improvements'
            }
    
    # Load unified parser results
    unified_file = Path('parsed_forms/form_8_unified_test.json')
    if unified_file.exists():
        with open(unified_file, 'r') as f:
            data = json.load(f)
            results['unified'] = {
                'fields': data.get('fields', []),
                'source': 'Unified orchestrator (multiple parsers)'
            }
    
    # Analyze each parser's results
    analysis = {}
    
    for parser_name, parser_data in results.items():
        fields = parser_data['fields']
        
        if not fields:
            analysis[parser_name] = {
                'total_fields': 0,
                'source': parser_data['source'],
                'quality_metrics': {}
            }
            continue
            
        # Analyze field quality
        quality_scores = [analyze_field_quality(f) for f in fields]
        
        analysis[parser_name] = {
            'total_fields': len(fields),
            'source': parser_data['source'],
            'quality_metrics': {
                'meaningful_names': sum(1 for q in quality_scores if q['has_meaningful_name']),
                'descriptive_labels': sum(1 for q in quality_scores if q['has_descriptive_label']),
                'duplicate_labels': sum(1 for q in quality_scores if q['has_duplicate_label']),
                'with_confidence': sum(1 for q in quality_scores if q['has_confidence_score']),
                'avg_confidence': sum(q['confidence_value'] for q in quality_scores) / len(quality_scores) if quality_scores else 0,
                'validated_fields': sum(1 for q in quality_scores if q['has_validation']),
                'typed_fields': sum(1 for q in quality_scores if q['has_field_type']),
                'avg_quality_score': sum(q['score'] for q in quality_scores) / len(quality_scores) if quality_scores else 0
            },
            'sample_fields': []
        }
        
        # Add sample fields
        for field in fields[:5]:
            analysis[parser_name]['sample_fields'].append({
                'name': field.get('field_name', ''),
                'label': field.get('field_label', ''),
                'type': field.get('field_type', 'unknown')
            })
    
    return analysis

def generate_comparison_report():
    """Generate a detailed comparison report"""
    
    analysis = compare_parsers()
    
    # Create markdown report
    report = []
    report.append("# Ontario Form Parser Comparison Report\n")
    report.append("## Executive Summary\n")
    
    # Find best performer
    if analysis:
        best_parser = max(analysis.items(), 
                         key=lambda x: x[1]['quality_metrics'].get('avg_quality_score', 0) if x[1]['total_fields'] > 0 else 0)
        report.append(f"**Best Overall Parser:** {best_parser[0]} (Quality Score: {best_parser[1]['quality_metrics'].get('avg_quality_score', 0):.2%})\n")
    
    report.append("\n## Detailed Parser Comparison\n")
    
    # Create comparison table
    report.append("| Parser | Fields | Meaningful Names | Good Labels | No Duplicates | Avg Confidence | Quality Score |")
    report.append("|--------|--------|-----------------|-------------|---------------|----------------|---------------|")
    
    for parser_name, data in analysis.items():
        metrics = data['quality_metrics']
        total = data['total_fields']
        
        if total > 0:
            meaningful_pct = metrics.get('meaningful_names', 0) / total * 100
            good_labels_pct = metrics.get('descriptive_labels', 0) / total * 100
            no_dup_pct = (total - metrics.get('duplicate_labels', 0)) / total * 100
            avg_conf = metrics.get('avg_confidence', 0) * 100
            quality = metrics.get('avg_quality_score', 0) * 100
            
            report.append(f"| {parser_name} | {total} | {meaningful_pct:.0f}% | {good_labels_pct:.0f}% | {no_dup_pct:.0f}% | {avg_conf:.0f}% | {quality:.0f}% |")
        else:
            report.append(f"| {parser_name} | 0 | N/A | N/A | N/A | N/A | N/A |")
    
    report.append("\n## Parser Details\n")
    
    for parser_name, data in analysis.items():
        report.append(f"\n### {parser_name.title()} Parser")
        report.append(f"**Source:** {data['source']}")
        report.append(f"**Total Fields:** {data['total_fields']}")
        
        if data['total_fields'] > 0:
            report.append("\n**Quality Metrics:**")
            metrics = data['quality_metrics']
            report.append(f"- Fields with meaningful names: {metrics.get('meaningful_names', 0)}/{data['total_fields']}")
            report.append(f"- Fields with descriptive labels: {metrics.get('descriptive_labels', 0)}/{data['total_fields']}")
            report.append(f"- Fields with duplicate labels: {metrics.get('duplicate_labels', 0)}/{data['total_fields']}")
            report.append(f"- Fields with confidence scores: {metrics.get('with_confidence', 0)}/{data['total_fields']}")
            report.append(f"- Average confidence: {metrics.get('avg_confidence', 0):.2%}")
            report.append(f"- Overall quality score: {metrics.get('avg_quality_score', 0):.2%}")
            
            if data['sample_fields']:
                report.append("\n**Sample Fields:**")
                for i, field in enumerate(data['sample_fields'], 1):
                    report.append(f"{i}. `{field['name']}`: \"{field['label']}\" (type: {field['type']})")
    
    report.append("\n## Key Improvements\n")
    
    # Compare enhanced vs basic
    if 'basic' in analysis and 'enhanced' in analysis:
        basic_quality = analysis['basic']['quality_metrics'].get('avg_quality_score', 0)
        enhanced_quality = analysis['enhanced']['quality_metrics'].get('avg_quality_score', 0)
        improvement = (enhanced_quality - basic_quality) / basic_quality * 100 if basic_quality > 0 else 0
        
        report.append(f"- **Enhanced vs Basic:** {improvement:.0f}% quality improvement")
        
    if 'basic' in analysis and 'unified' in analysis:
        basic_quality = analysis['basic']['quality_metrics'].get('avg_quality_score', 0)
        unified_quality = analysis['unified']['quality_metrics'].get('avg_quality_score', 0)
        improvement = (unified_quality - basic_quality) / basic_quality * 100 if basic_quality > 0 else 0
        
        report.append(f"- **Unified vs Basic:** {improvement:.0f}% quality improvement")
    
    report.append("\n## Recommendations\n")
    report.append("1. **Use the Unified Parser Orchestrator** for best results when multiple parsers are available")
    report.append("2. **Install additional dependencies** (pdfplumber, PyMuPDF, etc.) for better extraction")
    report.append("3. **Apply field validation** to ensure data quality")
    report.append("4. **Use confidence scoring** to identify fields that need manual review")
    report.append("5. **Implement template-based extraction** for known form types")
    
    # Save report
    report_text = '\n'.join(report)
    
    report_path = Path('PARSER_COMPARISON_REPORT.md')
    with open(report_path, 'w') as f:
        f.write(report_text)
    
    # Also save as JSON for programmatic access
    json_path = Path('parsed_forms/parser_comparison.json')
    with open(json_path, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    return report_text

if __name__ == "__main__":
    report = generate_comparison_report()
    print(report)
    print(f"\n✅ Report saved to PARSER_COMPARISON_REPORT.md")
    print(f"📊 JSON data saved to parsed_forms/parser_comparison.json")