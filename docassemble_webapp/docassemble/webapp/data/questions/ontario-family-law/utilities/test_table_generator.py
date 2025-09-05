#!/usr/bin/env python3
"""
Test the docassemble table generation system
"""

import os
import json
from pathlib import Path
from typing import Dict, List

from field_validation_mapper import ValidatedField
from docassemble_table_generator import generate_complete_interview

def test_table_generation():
    """
    Test table generation with Form 13 validated fields
    """
    print("=" * 80)
    print("TESTING DOCASSEMBLE TABLE GENERATION")
    print("=" * 80)
    
    # Load validated fields from the validation demo
    validation_output_dir = Path("validation_demo_output")
    
    if not validation_output_dir.exists():
        print("Please run test_validation_system.py first to generate validated fields")
        return
    
    # Load validated fields
    validated_fields_file = validation_output_dir / "validated_fields.json"
    if not validated_fields_file.exists():
        print(f"Validated fields file not found: {validated_fields_file}")
        return
    
    with open(validated_fields_file, 'r') as f:
        fields_data = json.load(f)
    
    # Convert to ValidatedField objects
    validated_fields = []
    for field_data in fields_data:
        # Create ValidatedField from dict
        validated_field = ValidatedField(
            field_id=field_data.get('field_id', ''),
            canonical_name=field_data.get('canonical_name', ''),
            field_type=field_data.get('field_type', 'text'),
            field_label=field_data.get('field_label', ''),
            docassemble_object=field_data.get('docassemble_object', 'DAObject'),
            docassemble_path=field_data.get('docassemble_path', ''),
            extraction_methods=field_data.get('extraction_methods', []),
            parser_sources=field_data.get('parser_sources', []),
            confidence_scores=field_data.get('confidence_scores', {}),
            consensus_score=field_data.get('consensus_score', 0.0),
            name_variations=field_data.get('name_variations', []),
            label_variations=field_data.get('label_variations', []),
            required=field_data.get('required', False),
            page_number=field_data.get('page_number', 0),
            validation_rules=field_data.get('validation_rules', []),
            ontario_specific=field_data.get('ontario_specific', False),
            parent_object=field_data.get('parent_object'),
            array_index=field_data.get('array_index'),
            is_nested=field_data.get('is_nested', False)
        )
        validated_fields.append(validated_field)
    
    print(f"\nLoaded {len(validated_fields)} validated fields")
    
    # Generate interview with tables
    print("\n1. GENERATING INTERVIEW STRUCTURE")
    print("-" * 40)
    
    result = generate_complete_interview(
        validated_fields=validated_fields,
        form_name="Form 13 - Financial Statement"
    )
    
    interview_yaml = result.get('interview_yaml', '')
    
    # Parse the YAML to analyze structure
    import yaml
    interview_data = yaml.safe_load(interview_yaml)
    
    print(f"Interview structure generated:")
    print(f"  Total blocks: {len(interview_data)}")
    
    # Count different block types
    metadata_blocks = sum(1 for block in interview_data if 'metadata' in block)
    object_blocks = sum(1 for block in interview_data if 'objects' in block)
    question_blocks = sum(1 for block in interview_data if 'question' in block)
    table_blocks = sum(1 for block in interview_data if 'table' in block)
    review_blocks = sum(1 for block in interview_data if 'review' in block)
    signature_blocks = sum(1 for block in interview_data if 'signature' in block)
    
    print(f"  Metadata blocks: {metadata_blocks}")
    print(f"  Object blocks: {object_blocks}")
    print(f"  Question blocks: {question_blocks}")
    print(f"  Table blocks: {table_blocks}")
    print(f"  Review blocks: {review_blocks}")
    print(f"  Signature blocks: {signature_blocks}")
    
    # Analyze tables detected
    print("\n2. TABLE DETECTION ANALYSIS")
    print("-" * 40)
    
    # Look for table patterns in field labels
    table_indicators = ['income', 'expense', 'asset', 'debt', 'real estate', 'vehicle', 'bank', 'investment']
    potential_tables = {}
    
    for field in validated_fields:
        label_lower = field.field_label.lower()
        for indicator in table_indicators:
            if indicator in label_lower:
                if indicator not in potential_tables:
                    potential_tables[indicator] = []
                potential_tables[indicator].append(field)
    
    print(f"Potential table categories found:")
    for category, fields in potential_tables.items():
        print(f"  {category.title()}: {len(fields)} fields")
        # Show sample fields
        for field in fields[:3]:
            print(f"    - {field.field_label[:50]}")
    
    # Save generated interview
    output_dir = Path("table_generation_output")
    output_dir.mkdir(exist_ok=True)
    
    interview_file = output_dir / "form_13_interview.yml"
    with open(interview_file, 'w') as f:
        f.write(interview_yaml)
    
    print(f"\n3. OUTPUT FILES")
    print("-" * 40)
    print(f"Interview saved to: {interview_file}")
    
    # Generate sample table data structure
    print("\n4. SAMPLE TABLE STRUCTURES")
    print("-" * 40)
    
    # Show a sample table structure from the interview
    for block in interview_data:
        if 'table' in block:
            print(f"\nTable: {block.get('question', 'Unknown')}")
            if 'fields' in block:
                print(f"  Fields in table:")
                for field in block['fields'][:5]:  # Show first 5 fields
                    print(f"    - {field.get('label', field.get('field', 'Unknown'))}")
            break
    
    # Show validation summary
    print("\n5. VALIDATION SUMMARY")
    print("-" * 40)
    
    # Check for required docassemble elements
    has_metadata = any('metadata' in block for block in interview_data)
    has_objects = any('objects' in block for block in interview_data)
    has_questions = any('question' in block for block in interview_data)
    has_review = any('review' in block for block in interview_data)
    has_signature = any('signature' in block for block in interview_data)
    
    print(f"Required elements:")
    print(f"  ✓ Metadata: {has_metadata}")
    print(f"  ✓ Objects: {has_objects}")
    print(f"  ✓ Questions: {has_questions}")
    print(f"  ✓ Review: {has_review}")
    print(f"  ✓ Signature: {has_signature}")
    
    # Check for Ontario-specific elements
    ontario_fields = [f for f in validated_fields if f.ontario_specific]
    print(f"\nOntario-specific fields: {len(ontario_fields)}")
    
    # Check for financial tables
    financial_types = ['currency', 'number']
    financial_fields = [f for f in validated_fields if f.field_type in financial_types]
    print(f"Financial fields: {len(financial_fields)}")
    
    print("\n" + "=" * 80)
    print("TABLE GENERATION TEST COMPLETE")
    print("=" * 80)
    
    return interview_yaml

if __name__ == "__main__":
    test_table_generation()