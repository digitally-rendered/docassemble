#!/usr/bin/env python3
"""
Test the field validation, deduplication, and docassemble mapping system
"""

import os
import json
from pathlib import Path
from typing import Dict, List

# Import our parsers
from advanced_docx_parser import AdvancedDocxParser
from intelligent_form_parser import IntelligentFormParser
from hybrid_form_parser import HybridFormParser

# Import validation system
from field_validation_mapper import (
    validate_and_map_fields,
    FieldValidator,
    FieldDeduplicator,
    DocassembleMapper
)

def load_parser_results(form_path: str) -> Dict[str, List[Dict]]:
    """
    Load results from multiple parsers for a single form
    """
    print(f"Loading parser results for: {Path(form_path).name}")
    parser_results = {}
    
    # Check for cached results first
    cache_dir = Path("parser_results")
    form_stem = Path(form_path).stem
    
    # Look for cached CSV/JSON files
    for parser_name in ['simple', 'intelligent', 'unified', 'advanced', 'hybrid']:
        # Check JSON cache
        json_pattern = cache_dir / parser_name / f"{form_stem}*.json"
        json_files = list(cache_dir.glob(str(json_pattern).replace(str(cache_dir), "").lstrip("/")))
        
        if json_files:
            with open(json_files[0], 'r') as f:
                data = json.load(f)
                if isinstance(data, dict) and 'fields' in data:
                    parser_results[parser_name] = data['fields']
                elif isinstance(data, list):
                    parser_results[parser_name] = data
                print(f"  Loaded {len(parser_results[parser_name])} fields from {parser_name} cache")
    
    # If no cached results, run parsers
    if not parser_results:
        print("  No cached results found. Running parsers...")
        
        # Run advanced DOCX parser
        try:
            if form_path.endswith('.docx'):
                adv_parser = AdvancedDocxParser(form_path)
                adv_fields = adv_parser.parse()
                parser_results['advanced_docx'] = [
                    {
                        'field_name': f.field_name,
                        'field_type': f.field_type,
                        'field_label': f.field_label,
                        'confidence': f.confidence,
                        'page_number': f.page_number,
                        'extraction_method': f.extraction_method
                    }
                    for f in adv_fields
                ]
                print(f"  Advanced DOCX: {len(parser_results['advanced_docx'])} fields")
        except Exception as e:
            print(f"  Advanced DOCX parser error: {e}")
        
        # Run intelligent parser
        try:
            intel_parser = IntelligentFormParser(form_path, use_ocr=False)
            intel_fields = intel_parser.parse()
            parser_results['intelligent'] = [
                {
                    'field_name': f.field_name,
                    'field_type': f.field_type,
                    'field_label': f.field_label,
                    'confidence': f.confidence,
                    'page_number': f.page_number,
                    'extraction_method': f.extraction_method
                }
                for f in intel_fields
            ]
            print(f"  Intelligent: {len(parser_results['intelligent'])} fields")
        except Exception as e:
            print(f"  Intelligent parser error: {e}")
    
    return parser_results

def demonstrate_validation_process(form_path: str):
    """
    Demonstrate the complete validation process
    """
    print("=" * 80)
    print("FIELD VALIDATION DEMONSTRATION")
    print("=" * 80)
    
    # Step 1: Load parser results
    print("\n1. LOADING PARSER RESULTS")
    print("-" * 40)
    parser_results = load_parser_results(form_path)
    
    if not parser_results:
        print("No parser results available. Please run parsers first.")
        return
    
    # Show input statistics
    print(f"\nInput statistics:")
    total_fields = 0
    for parser_name, fields in parser_results.items():
        count = len(fields)
        total_fields += count
        print(f"  {parser_name}: {count} fields")
    print(f"  Total: {total_fields} fields across {len(parser_results)} parsers")
    
    # Step 2: Validation
    print("\n2. FIELD VALIDATION")
    print("-" * 40)
    
    validator = FieldValidator()
    validated_fields, validation_report = validator.validate_fields(parser_results)
    
    print(f"Validation results:")
    print(f"  Validated fields: {len(validated_fields)}")
    print(f"  Multi-parser agreement: {validation_report['multi_parser_fields']}")
    print(f"  Single-parser only: {validation_report['single_parser_fields']}")
    print(f"  Ontario-specific: {validation_report.get('ontario_specific_fields', 0)}")
    
    # Show consensus distribution
    print(f"\nConsensus distribution:")
    for level, count in validation_report['consensus_distribution'].items():
        print(f"  {level}: {count} fields")
    
    # Step 3: Deduplication
    print("\n3. FIELD DEDUPLICATION")
    print("-" * 40)
    
    deduplicator = FieldDeduplicator()
    unique_fields = deduplicator.deduplicate(validated_fields)
    
    duplicates_removed = len(validated_fields) - len(unique_fields)
    print(f"Deduplication results:")
    print(f"  Input fields: {len(validated_fields)}")
    print(f"  Unique fields: {len(unique_fields)}")
    print(f"  Duplicates removed: {duplicates_removed}")
    print(f"  Deduplication rate: {(duplicates_removed/max(1, len(validated_fields))*100):.1f}%")
    
    # Step 4: Docassemble mapping
    print("\n4. DOCASSEMBLE OBJECT MAPPING")
    print("-" * 40)
    
    mapper = DocassembleMapper()
    yaml_structure = mapper.generate_yaml_structure(unique_fields)
    
    print(f"Docassemble structure generated:")
    print(f"  Objects: {len(yaml_structure['objects'])}")
    for obj_type, definition in yaml_structure['objects'].items():
        print(f"    - {obj_type}: {len(definition['fields'])} fields")
    
    print(f"  Questions: {len(yaml_structure['questions'])}")
    print(f"  Field definitions: {len(yaml_structure['fields'])}")
    
    # Step 5: Show sample mappings
    print("\n5. SAMPLE FIELD MAPPINGS")
    print("-" * 40)
    
    # Show first 10 unique fields with their mappings
    print("Sample validated and mapped fields:")
    for i, field in enumerate(unique_fields[:10], 1):
        print(f"\n  {i}. {field.canonical_name}")
        print(f"     Label: {field.field_label[:50]}")
        print(f"     Type: {field.field_type}")
        print(f"     DA Object: {field.docassemble_object}")
        print(f"     DA Path: {field.docassemble_path}")
        print(f"     Consensus: {field.consensus_score:.2f}")
        print(f"     Sources: {', '.join(field.parser_sources)}")
        
        if field.ontario_specific:
            print(f"     ⚖️ Ontario-specific field")
        
        if field.validation_rules:
            print(f"     Validation: {field.validation_rules[0][:30]}...")
    
    # Step 6: Show validation issues
    if validation_report.get('validation_issues'):
        print("\n6. VALIDATION ISSUES")
        print("-" * 40)
        print(f"Found {len(validation_report['validation_issues'])} issues:")
        for issue in validation_report['validation_issues'][:5]:
            print(f"  ⚠️ {issue}")
    
    # Save comprehensive results
    output_dir = Path("validation_demo_output")
    output_dir.mkdir(exist_ok=True)
    
    # Save all results
    with open(output_dir / "parser_results.json", 'w') as f:
        json.dump(parser_results, f, indent=2)
    
    with open(output_dir / "validated_fields.json", 'w') as f:
        json.dump([
            {
                'canonical_name': field.canonical_name,
                'field_type': field.field_type,
                'field_label': field.field_label,
                'docassemble_object': field.docassemble_object,
                'docassemble_path': field.docassemble_path,
                'consensus_score': field.consensus_score,
                'parser_sources': field.parser_sources,
                'ontario_specific': field.ontario_specific
            }
            for field in unique_fields
        ], f, indent=2)
    
    with open(output_dir / "docassemble_structure.json", 'w') as f:
        json.dump(yaml_structure, f, indent=2)
    
    print(f"\n" + "=" * 80)
    print("RESULTS SAVED")
    print("=" * 80)
    print(f"Output directory: {output_dir}")
    print("  - parser_results.json (raw input)")
    print("  - validated_fields.json (validated & deduplicated)")
    print("  - docassemble_structure.json (mapped structure)")
    
    return {
        'parser_results': parser_results,
        'validated_fields': unique_fields,
        'yaml_structure': yaml_structure,
        'validation_report': validation_report
    }

def compare_parser_consistency(form_path: str):
    """
    Compare consistency between different parsers
    """
    print("\n" + "=" * 80)
    print("PARSER CONSISTENCY ANALYSIS")
    print("=" * 80)
    
    parser_results = load_parser_results(form_path)
    
    if len(parser_results) < 2:
        print("Need at least 2 parsers for comparison")
        return
    
    # Create field signature sets for each parser
    parser_signatures = {}
    for parser_name, fields in parser_results.items():
        signatures = set()
        for field in fields:
            # Create normalized signature
            sig = f"{field.get('field_type', 'text')}_{field.get('field_label', '')[:20].lower()}"
            signatures.add(sig)
        parser_signatures[parser_name] = signatures
    
    # Calculate pairwise overlap
    print("\nPairwise field overlap:")
    parser_names = list(parser_signatures.keys())
    
    for i, parser1 in enumerate(parser_names):
        for parser2 in parser_names[i+1:]:
            set1 = parser_signatures[parser1]
            set2 = parser_signatures[parser2]
            
            intersection = len(set1 & set2)
            union = len(set1 | set2)
            jaccard = intersection / max(1, union)
            
            print(f"  {parser1} vs {parser2}:")
            print(f"    Common fields: {intersection}")
            print(f"    Total unique: {union}")
            print(f"    Jaccard similarity: {jaccard:.2%}")
    
    # Find fields unique to each parser
    print("\nUnique fields by parser:")
    for parser_name, signatures in parser_signatures.items():
        # Find signatures unique to this parser
        unique = signatures.copy()
        for other_parser, other_sigs in parser_signatures.items():
            if other_parser != parser_name:
                unique -= other_sigs
        
        if unique:
            print(f"  {parser_name} unique fields: {len(unique)}")
            # Show sample
            for sig in list(unique)[:3]:
                print(f"    - {sig}")

if __name__ == "__main__":
    import sys
    
    # Use provided form or default
    if len(sys.argv) > 1:
        form_path = sys.argv[1]
    else:
        form_path = "workflow_output/ontario_forms/financial_statements/form_13_-_financial_statement_support_flr-13-may21-en-fil.docx"
        
        if not os.path.exists(form_path):
            form_path = "workflow_output/ontario_forms/applications/form_8_-_application_general_flr-8-jun25-en-fil.docx"
    
    if os.path.exists(form_path):
        # Run validation demonstration
        results = demonstrate_validation_process(form_path)
        
        # Run consistency analysis
        compare_parser_consistency(form_path)
    else:
        print(f"Form not found: {form_path}")
        print("Please provide a valid form path")