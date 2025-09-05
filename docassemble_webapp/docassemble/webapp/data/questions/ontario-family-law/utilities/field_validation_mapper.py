#!/usr/bin/env python3
"""
Field Validation, Deduplication, and Docassemble Mapping System
Ensures consistency across parsers and maps to docassemble objects
"""

import os
import json
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, asdict, field
from collections import defaultdict, Counter
import difflib
import logging
from fuzzywuzzy import fuzz, process
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ValidatedField:
    """Represents a validated and deduplicated field"""
    field_id: str
    canonical_name: str  # Standard name across all parsers
    field_type: str
    field_label: str
    docassemble_object: str  # DAObject type to map to
    docassemble_path: str  # Full path in docassemble (e.g., users[0].name.first)
    
    # Validation metadata
    extraction_methods: List[str] = field(default_factory=list)
    parser_sources: List[str] = field(default_factory=list)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    consensus_score: float = 0.0
    
    # Original variations
    name_variations: List[str] = field(default_factory=list)
    label_variations: List[str] = field(default_factory=list)
    
    # Field properties
    required: bool = False
    page_number: int = 0
    validation_rules: List[str] = field(default_factory=list)
    ontario_specific: bool = False
    
    # Mapping metadata
    parent_object: Optional[str] = None
    array_index: Optional[int] = None
    is_nested: bool = False

class FieldValidator:
    """
    Validates fields across multiple parsers to ensure consistency
    """
    
    def __init__(self):
        # Field similarity thresholds
        self.name_similarity_threshold = 85  # Fuzzy match threshold
        self.label_similarity_threshold = 80
        self.position_tolerance = 5  # Page number tolerance
        
        # Canonical field mappings for Ontario forms
        self.canonical_mappings = self._load_canonical_mappings()
        
        # Docassemble object mappings
        self.da_object_mappings = self._load_da_mappings()
    
    def validate_fields(self, 
                       parser_results: Dict[str, List[Dict]]) -> Tuple[List[ValidatedField], Dict]:
        """
        Validate fields from multiple parsers
        
        Args:
            parser_results: Dict with parser name as key and list of fields as value
        
        Returns:
            Tuple of (validated_fields, validation_report)
        """
        
        logger.info("Starting field validation across parsers...")
        
        # Group similar fields
        field_groups = self._group_similar_fields(parser_results)
        
        # Validate each group
        validated_fields = []
        for group_id, field_group in field_groups.items():
            validated_field = self._validate_field_group(field_group)
            if validated_field:
                validated_fields.append(validated_field)
        
        # Generate validation report
        report = self._generate_validation_report(validated_fields, parser_results)
        
        return validated_fields, report
    
    def _group_similar_fields(self, parser_results: Dict[str, List[Dict]]) -> Dict[str, List[Tuple[str, Dict]]]:
        """
        Group similar fields from different parsers
        """
        field_groups = defaultdict(list)
        processed_fields = set()
        
        # Flatten all fields with parser source
        all_fields = []
        for parser_name, fields in parser_results.items():
            for field in fields:
                all_fields.append((parser_name, field))
        
        # Group by similarity
        for i, (parser1, field1) in enumerate(all_fields):
            if i in processed_fields:
                continue
            
            # Create field signature
            field_key = self._get_field_signature(field1)
            field_groups[field_key].append((parser1, field1))
            processed_fields.add(i)
            
            # Find similar fields
            for j, (parser2, field2) in enumerate(all_fields[i+1:], start=i+1):
                if j in processed_fields:
                    continue
                
                if self._are_fields_similar(field1, field2):
                    field_groups[field_key].append((parser2, field2))
                    processed_fields.add(j)
        
        return field_groups
    
    def _are_fields_similar(self, field1: Dict, field2: Dict) -> bool:
        """
        Check if two fields are similar enough to be the same
        """
        # Check field type
        if field1.get('field_type') != field2.get('field_type'):
            return False
        
        # Check page proximity
        page1 = field1.get('page_number', 0)
        page2 = field2.get('page_number', 0)
        if abs(page1 - page2) > self.position_tolerance:
            return False
        
        # Check name similarity
        name1 = field1.get('field_name', '')
        name2 = field2.get('field_name', '')
        name_similarity = fuzz.ratio(name1, name2)
        
        # Check label similarity
        label1 = field1.get('field_label', '')[:50]
        label2 = field2.get('field_label', '')[:50]
        label_similarity = fuzz.partial_ratio(label1, label2)
        
        # Combined similarity check
        return (name_similarity >= self.name_similarity_threshold or
                label_similarity >= self.label_similarity_threshold)
    
    def _get_field_signature(self, field: Dict) -> str:
        """
        Generate a signature for field grouping
        """
        field_type = field.get('field_type', 'text')
        field_label = re.sub(r'[^\w\s]', '', field.get('field_label', '')[:30]).lower()
        page = field.get('page_number', 0)
        
        # Create hash for consistent grouping
        sig = f"{field_type}_{field_label}_{page}"
        return hashlib.md5(sig.encode()).hexdigest()[:16]
    
    def _validate_field_group(self, field_group: List[Tuple[str, Dict]]) -> Optional[ValidatedField]:
        """
        Validate a group of similar fields
        """
        if not field_group:
            return None
        
        # Extract canonical information
        canonical_name = self._get_canonical_name(field_group)
        canonical_type = self._get_canonical_type(field_group)
        canonical_label = self._get_canonical_label(field_group)
        
        # Map to docassemble object
        da_object, da_path = self._map_to_docassemble(canonical_name, canonical_type, canonical_label)
        
        # Create validated field
        validated = ValidatedField(
            field_id=hashlib.md5(f"{canonical_name}_{canonical_type}".encode()).hexdigest()[:8],
            canonical_name=canonical_name,
            field_type=canonical_type,
            field_label=canonical_label,
            docassemble_object=da_object,
            docassemble_path=da_path
        )
        
        # Aggregate metadata
        for parser_name, field in field_group:
            validated.parser_sources.append(parser_name)
            
            # Extraction methods
            method = field.get('extraction_method', parser_name)
            if method not in validated.extraction_methods:
                validated.extraction_methods.append(method)
            
            # Confidence scores
            confidence = field.get('confidence', 0.5)
            validated.confidence_scores[parser_name] = confidence
            
            # Name variations
            name = field.get('field_name', '')
            if name and name not in validated.name_variations:
                validated.name_variations.append(name)
            
            # Label variations
            label = field.get('field_label', '')
            if label and label not in validated.label_variations:
                validated.label_variations.append(label)
            
            # Page number (use most common)
            validated.page_number = field.get('page_number', validated.page_number)
            
            # Required flag
            validated.required = validated.required or field.get('required', False)
        
        # Calculate consensus score
        validated.consensus_score = self._calculate_consensus_score(validated)
        
        # Check if Ontario-specific
        validated.ontario_specific = self._is_ontario_specific(canonical_label)
        
        # Add validation rules
        validated.validation_rules = self._get_validation_rules(canonical_type, canonical_label)
        
        return validated
    
    def _get_canonical_name(self, field_group: List[Tuple[str, Dict]]) -> str:
        """
        Determine the canonical field name
        """
        # Check if it matches a known canonical field
        all_labels = [f[1].get('field_label', '') for f in field_group]
        
        for label in all_labels:
            canonical = self._lookup_canonical_name(label)
            if canonical:
                return canonical
        
        # Use most common or highest confidence name
        name_counts = Counter()
        for _, field in field_group:
            name = field.get('field_name', '')
            confidence = field.get('confidence', 0.5)
            name_counts[name] += confidence
        
        if name_counts:
            return name_counts.most_common(1)[0][0]
        
        return f"field_{len(field_group)}"
    
    def _get_canonical_type(self, field_group: List[Tuple[str, Dict]]) -> str:
        """
        Determine the canonical field type
        """
        type_counts = Counter()
        for _, field in field_group:
            field_type = field.get('field_type', 'text')
            confidence = field.get('confidence', 0.5)
            type_counts[field_type] += confidence
        
        if type_counts:
            return type_counts.most_common(1)[0][0]
        return 'text'
    
    def _get_canonical_label(self, field_group: List[Tuple[str, Dict]]) -> str:
        """
        Determine the canonical field label
        """
        # Use the longest, most descriptive label
        labels = []
        for _, field in field_group:
            label = field.get('field_label', '')
            confidence = field.get('confidence', 0.5)
            labels.append((label, confidence))
        
        if labels:
            # Sort by confidence and length
            labels.sort(key=lambda x: (x[1], len(x[0])), reverse=True)
            return labels[0][0]
        
        return ""
    
    def _calculate_consensus_score(self, validated: ValidatedField) -> float:
        """
        Calculate consensus score based on parser agreement
        """
        if not validated.confidence_scores:
            return 0.0
        
        # Base score is average confidence
        avg_confidence = sum(validated.confidence_scores.values()) / len(validated.confidence_scores)
        
        # Bonus for multi-parser agreement
        parser_bonus = min(0.2, len(validated.parser_sources) * 0.05)
        
        # Bonus for multi-method extraction
        method_bonus = min(0.1, len(validated.extraction_methods) * 0.02)
        
        return min(1.0, avg_confidence + parser_bonus + method_bonus)
    
    def _is_ontario_specific(self, label: str) -> bool:
        """
        Check if field is Ontario-specific
        """
        ontario_indicators = [
            'ontario', 'lso', 'court file', 'ocj', 'scj',
            'family court', 'superior court'
        ]
        
        label_lower = label.lower()
        return any(indicator in label_lower for indicator in ontario_indicators)
    
    def _get_validation_rules(self, field_type: str, label: str) -> List[str]:
        """
        Get validation rules for field
        """
        rules = []
        label_lower = label.lower()
        
        # Type-based rules
        if field_type == 'email':
            rules.append(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        elif field_type == 'phone':
            rules.append(r'^\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$')
        elif field_type == 'date':
            rules.append(r'^\d{4}-\d{2}-\d{2}$|^\d{2}/\d{2}/\d{4}$')
        elif field_type == 'currency':
            rules.append(r'^\$?[0-9]{1,3}(,[0-9]{3})*(\.[0-9]{2})?$')
        
        # Ontario-specific rules
        if 'postal' in label_lower:
            rules.append(r'^[KLMNP]\d[A-Z]\s?\d[A-Z]\d$')
        elif 'sin' in label_lower or 'social insurance' in label_lower:
            rules.append(r'^\d{3}-\d{3}-\d{3}$')
        elif 'lso' in label_lower:
            rules.append(r'^\d{5}[A-Z]?$')
        elif 'court file' in label_lower:
            rules.append(r'^[A-Z]{2}-\d{2}-\d{6}$')
        
        return rules
    
    def _lookup_canonical_name(self, label: str) -> Optional[str]:
        """
        Look up canonical name from known mappings
        """
        label_lower = label.lower()
        
        for pattern, canonical in self.canonical_mappings.items():
            if pattern in label_lower:
                return canonical
        
        return None
    
    def _load_canonical_mappings(self) -> Dict[str, str]:
        """
        Load canonical field mappings for Ontario forms
        """
        return {
            'full legal name': 'full_legal_name',
            'first name': 'first_name',
            'last name': 'last_name',
            'middle name': 'middle_name',
            'date of birth': 'date_of_birth',
            'address': 'address',
            'street': 'street_address',
            'city': 'city',
            'province': 'province',
            'postal code': 'postal_code',
            'phone': 'phone_number',
            'email': 'email_address',
            'court file': 'court_file_number',
            'applicant': 'applicant',
            'respondent': 'respondent',
            'lawyer': 'lawyer',
            'lso': 'lso_number',
            'marriage date': 'marriage_date',
            'separation date': 'separation_date',
            'divorce date': 'divorce_date',
            'income': 'income',
            'expense': 'expense',
            'asset': 'asset',
            'debt': 'debt',
            'child': 'child',
            'signature': 'signature',
            'date signed': 'signature_date'
        }
    
    def _load_da_mappings(self) -> Dict[str, Tuple[str, str]]:
        """
        Load docassemble object mappings
        Returns: Dict[field_pattern, (DAObject, path_template)]
        """
        return {
            # Person fields
            'applicant': ('Individual', 'users[0]'),
            'respondent': ('Individual', 'users[1]'),
            'child': ('Individual', 'children[i]'),
            'lawyer': ('Individual', 'lawyers[i]'),
            
            # Name components
            'first_name': ('Individual', '{parent}.name.first'),
            'last_name': ('Individual', '{parent}.name.last'),
            'middle_name': ('Individual', '{parent}.name.middle'),
            'full_legal_name': ('Individual', '{parent}.name.text'),
            
            # Address components
            'address': ('Address', '{parent}.address'),
            'street_address': ('Address', '{parent}.address.address'),
            'city': ('Address', '{parent}.address.city'),
            'province': ('Address', '{parent}.address.state'),
            'postal_code': ('Address', '{parent}.address.postal_code'),
            
            # Contact
            'phone_number': ('Individual', '{parent}.phone_number'),
            'email_address': ('Individual', '{parent}.email'),
            
            # Dates
            'date_of_birth': ('Individual', '{parent}.birthdate'),
            'marriage_date': ('DAObject', 'marriage.date'),
            'separation_date': ('DAObject', 'separation.date'),
            'divorce_date': ('DAObject', 'divorce.date'),
            
            # Financial
            'income': ('Value', '{parent}.income'),
            'expense': ('Value', '{parent}.expense'),
            'asset': ('Value', 'assets[i]'),
            'debt': ('Value', 'debts[i]'),
            
            # Legal
            'court_file_number': ('DAObject', 'court.file_number'),
            'lso_number': ('Individual', '{parent}.lso_number'),
            
            # Other
            'signature': ('Individual', '{parent}.signature'),
            'signature_date': ('Individual', '{parent}.signature_date')
        }
    
    def _map_to_docassemble(self, canonical_name: str, field_type: str, label: str) -> Tuple[str, str]:
        """
        Map field to docassemble object and path
        """
        # Check direct mapping
        if canonical_name in self.da_object_mappings:
            da_object, path_template = self.da_object_mappings[canonical_name]
            
            # Determine parent object from context
            parent = self._determine_parent_object(label)
            
            # Format path
            if '{parent}' in path_template:
                path = path_template.format(parent=parent)
            else:
                path = path_template
            
            return da_object, path
        
        # Default mappings by type
        type_mappings = {
            'email': ('Individual', 'users[i].email'),
            'phone': ('Individual', 'users[i].phone_number'),
            'date': ('DAObject', 'dates[i]'),
            'currency': ('Value', 'amounts[i]'),
            'checkbox': ('DAObject', 'selections[i]'),
            'radio': ('DAObject', 'choices[i]'),
            'signature': ('Individual', 'users[i].signature'),
            'text': ('DAObject', 'fields[i]')
        }
        
        if field_type in type_mappings:
            return type_mappings[field_type]
        
        return ('DAObject', f'fields.{canonical_name}')
    
    def _determine_parent_object(self, label: str) -> str:
        """
        Determine parent object from field label/context
        """
        label_lower = label.lower()
        
        if 'applicant' in label_lower:
            return 'users[0]'
        elif 'respondent' in label_lower:
            return 'users[1]'
        elif 'child' in label_lower:
            return 'children[i]'
        elif 'lawyer' in label_lower:
            return 'lawyers[i]'
        else:
            return 'users[i]'
    
    def _generate_validation_report(self, 
                                   validated_fields: List[ValidatedField],
                                   parser_results: Dict[str, List[Dict]]) -> Dict:
        """
        Generate comprehensive validation report
        """
        report = {
            'total_validated_fields': len(validated_fields),
            'parser_coverage': {},
            'consensus_distribution': {
                'high': 0,  # > 0.8
                'medium': 0,  # 0.5 - 0.8
                'low': 0  # < 0.5
            },
            'multi_parser_fields': 0,
            'single_parser_fields': 0,
            'ontario_specific_fields': 0,
            'docassemble_mappings': {},
            'field_type_distribution': {},
            'validation_issues': []
        }
        
        # Analyze validated fields
        for field in validated_fields:
            # Consensus distribution
            if field.consensus_score > 0.8:
                report['consensus_distribution']['high'] += 1
            elif field.consensus_score >= 0.5:
                report['consensus_distribution']['medium'] += 1
            else:
                report['consensus_distribution']['low'] += 1
            
            # Parser agreement
            if len(field.parser_sources) > 1:
                report['multi_parser_fields'] += 1
            else:
                report['single_parser_fields'] += 1
            
            # Ontario-specific
            if field.ontario_specific:
                report['ontario_specific_fields'] += 1
            
            # Docassemble mappings
            da_obj = field.docassemble_object
            if da_obj not in report['docassemble_mappings']:
                report['docassemble_mappings'][da_obj] = 0
            report['docassemble_mappings'][da_obj] += 1
            
            # Field types
            ftype = field.field_type
            if ftype not in report['field_type_distribution']:
                report['field_type_distribution'][ftype] = 0
            report['field_type_distribution'][ftype] += 1
            
            # Check for issues
            if field.consensus_score < 0.5:
                report['validation_issues'].append(
                    f"Low consensus for '{field.canonical_name}': {field.consensus_score:.2f}"
                )
            
            if len(field.parser_sources) == 1:
                report['validation_issues'].append(
                    f"Single parser extraction for '{field.canonical_name}': {field.parser_sources[0]}"
                )
        
        # Parser coverage
        for parser_name, fields in parser_results.items():
            report['parser_coverage'][parser_name] = {
                'total_fields': len(fields),
                'validated_fields': sum(1 for vf in validated_fields if parser_name in vf.parser_sources)
            }
        
        return report

class FieldDeduplicator:
    """
    Deduplicates fields using advanced similarity matching
    """
    
    def __init__(self):
        self.similarity_threshold = 90
        self.position_weight = 0.2
        self.type_weight = 0.3
        self.label_weight = 0.5
    
    def deduplicate(self, fields: List[ValidatedField]) -> List[ValidatedField]:
        """
        Deduplicate validated fields
        """
        if not fields:
            return []
        
        logger.info(f"Deduplicating {len(fields)} fields...")
        
        # Sort by consensus score
        fields.sort(key=lambda x: x.consensus_score, reverse=True)
        
        deduplicated = []
        seen_signatures = set()
        
        for field in fields:
            signature = self._get_field_signature(field)
            
            # Check if similar field already exists
            is_duplicate = False
            for seen_sig in seen_signatures:
                if self._calculate_similarity(signature, seen_sig) >= self.similarity_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                deduplicated.append(field)
                seen_signatures.add(signature)
        
        logger.info(f"Deduplicated to {len(deduplicated)} unique fields")
        
        return deduplicated
    
    def _get_field_signature(self, field: ValidatedField) -> str:
        """
        Generate signature for deduplication
        """
        # Combine key attributes
        sig_parts = [
            field.field_type,
            field.canonical_name.lower(),
            str(field.page_number),
            field.docassemble_object
        ]
        
        return '|'.join(sig_parts)
    
    def _calculate_similarity(self, sig1: str, sig2: str) -> float:
        """
        Calculate similarity between two signatures
        """
        parts1 = sig1.split('|')
        parts2 = sig2.split('|')
        
        if len(parts1) != len(parts2):
            return 0.0
        
        # Type match
        type_score = 100 if parts1[0] == parts2[0] else 0
        
        # Name similarity
        name_score = fuzz.ratio(parts1[1], parts2[1])
        
        # Position proximity
        try:
            page1 = int(parts1[2])
            page2 = int(parts2[2])
            position_score = 100 - min(100, abs(page1 - page2) * 20)
        except:
            position_score = 50
        
        # Weighted average
        total_score = (
            type_score * self.type_weight +
            name_score * self.label_weight +
            position_score * self.position_weight
        )
        
        return total_score

class DocassembleMapper:
    """
    Maps validated fields to docassemble YAML structure
    """
    
    def __init__(self):
        self.object_registry = {}
        self.field_registry = {}
    
    def generate_yaml_structure(self, validated_fields: List[ValidatedField]) -> Dict:
        """
        Generate docassemble YAML structure from validated fields
        """
        logger.info("Generating docassemble YAML structure...")
        
        # Initialize structure
        yaml_structure = {
            'metadata': {
                'title': 'Ontario Family Law Form',
                'short_title': 'Form',
                'auto_generated': True
            },
            'objects': {},
            'questions': [],
            'fields': []
        }
        
        # Group fields by docassemble object
        object_fields = defaultdict(list)
        for field in validated_fields:
            object_fields[field.docassemble_object].append(field)
        
        # Generate objects section
        for da_object, fields in object_fields.items():
            yaml_structure['objects'][da_object] = self._generate_object_definition(da_object, fields)
        
        # Generate questions
        yaml_structure['questions'] = self._generate_questions(validated_fields)
        
        # Generate field definitions
        yaml_structure['fields'] = self._generate_field_definitions(validated_fields)
        
        return yaml_structure
    
    def _generate_object_definition(self, da_object: str, fields: List[ValidatedField]) -> Dict:
        """
        Generate docassemble object definition
        """
        definition = {
            'type': da_object,
            'fields': []
        }
        
        # Add field mappings
        for field in fields:
            field_def = {
                'name': field.canonical_name,
                'type': field.field_type,
                'label': field.field_label,
                'required': field.required
            }
            
            if field.validation_rules:
                field_def['validation'] = field.validation_rules
            
            definition['fields'].append(field_def)
        
        return definition
    
    def _generate_questions(self, fields: List[ValidatedField]) -> List[Dict]:
        """
        Generate docassemble questions
        """
        questions = []
        
        # Group by page for logical flow
        page_fields = defaultdict(list)
        for field in fields:
            page_fields[field.page_number].append(field)
        
        # Generate question for each page
        for page_num in sorted(page_fields.keys()):
            question = {
                'id': f'page_{page_num}',
                'question': f'Information - Page {page_num}',
                'fields': []
            }
            
            for field in page_fields[page_num]:
                field_config = {
                    'label': field.field_label,
                    'field': field.docassemble_path,
                    'datatype': self._map_field_type(field.field_type),
                    'required': field.required
                }
                
                if field.validation_rules:
                    field_config['validation'] = field.validation_rules[0] if field.validation_rules else None
                
                question['fields'].append(field_config)
            
            questions.append(question)
        
        return questions
    
    def _generate_field_definitions(self, fields: List[ValidatedField]) -> List[Dict]:
        """
        Generate field definitions
        """
        definitions = []
        
        for field in fields:
            definition = {
                'variable': field.docassemble_path,
                'datatype': self._map_field_type(field.field_type),
                'label': field.field_label,
                'canonical_name': field.canonical_name
            }
            
            if field.ontario_specific:
                definition['ontario_specific'] = True
            
            definitions.append(definition)
        
        return definitions
    
    def _map_field_type(self, field_type: str) -> str:
        """
        Map field type to docassemble datatype
        """
        type_mapping = {
            'text': 'text',
            'email': 'email',
            'phone': 'phone',
            'date': 'date',
            'currency': 'currency',
            'checkbox': 'yesno',
            'radio': 'radio',
            'select': 'dropdown',
            'signature': 'signature',
            'number': 'number'
        }
        
        return type_mapping.get(field_type, 'text')

def validate_and_map_fields(parser_results: Dict[str, List[Dict]], 
                           output_dir: str = "validation_output") -> Dict:
    """
    Complete validation, deduplication, and mapping pipeline
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    print("=" * 80)
    print("FIELD VALIDATION AND MAPPING PIPELINE")
    print("=" * 80)
    
    # Step 1: Validate fields
    validator = FieldValidator()
    validated_fields, validation_report = validator.validate_fields(parser_results)
    
    print(f"\nValidation complete:")
    print(f"  Total validated fields: {len(validated_fields)}")
    print(f"  Multi-parser agreement: {validation_report['multi_parser_fields']}")
    print(f"  Single-parser only: {validation_report['single_parser_fields']}")
    
    # Step 2: Deduplicate
    deduplicator = FieldDeduplicator()
    unique_fields = deduplicator.deduplicate(validated_fields)
    
    print(f"\nDeduplication complete:")
    print(f"  Unique fields: {len(unique_fields)}")
    print(f"  Duplicates removed: {len(validated_fields) - len(unique_fields)}")
    
    # Step 3: Map to docassemble
    mapper = DocassembleMapper()
    yaml_structure = mapper.generate_yaml_structure(unique_fields)
    
    print(f"\nDocassemble mapping complete:")
    print(f"  Objects created: {len(yaml_structure['objects'])}")
    print(f"  Questions generated: {len(yaml_structure['questions'])}")
    
    # Save results
    # Save validated fields
    validated_file = output_path / "validated_fields.json"
    with open(validated_file, 'w') as f:
        json.dump([asdict(field) for field in unique_fields], f, indent=2)
    
    # Save validation report
    report_file = output_path / "validation_report.json"
    with open(report_file, 'w') as f:
        json.dump(validation_report, f, indent=2)
    
    # Save YAML structure
    yaml_file = output_path / "docassemble_structure.json"
    with open(yaml_file, 'w') as f:
        json.dump(yaml_structure, f, indent=2)
    
    # Generate summary report
    summary = {
        'timestamp': pd.Timestamp.now().isoformat(),
        'input_parsers': list(parser_results.keys()),
        'total_input_fields': sum(len(fields) for fields in parser_results.values()),
        'validated_fields': len(validated_fields),
        'unique_fields': len(unique_fields),
        'validation_report': validation_report,
        'docassemble_objects': list(yaml_structure['objects'].keys()),
        'files_generated': [
            str(validated_file),
            str(report_file),
            str(yaml_file)
        ]
    }
    
    summary_file = output_path / "pipeline_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nFiles saved to: {output_path}")
    print(f"  - validated_fields.json")
    print(f"  - validation_report.json")
    print(f"  - docassemble_structure.json")
    print(f"  - pipeline_summary.json")
    
    return summary

if __name__ == "__main__":
    # Test with sample data
    sample_parser_results = {
        'parser1': [
            {
                'field_name': 'applicant_name',
                'field_type': 'text',
                'field_label': 'Full Legal Name of Applicant',
                'confidence': 0.9,
                'page_number': 1
            },
            {
                'field_name': 'applicant_email',
                'field_type': 'email',
                'field_label': 'Email Address',
                'confidence': 0.8,
                'page_number': 1
            }
        ],
        'parser2': [
            {
                'field_name': 'full_legal_name_applicant',
                'field_type': 'text',
                'field_label': 'Applicant Full Legal Name',
                'confidence': 0.85,
                'page_number': 1
            },
            {
                'field_name': 'email',
                'field_type': 'email',
                'field_label': 'Email:',
                'confidence': 0.7,
                'page_number': 1
            }
        ]
    }
    
    # Run validation pipeline
    summary = validate_and_map_fields(sample_parser_results)