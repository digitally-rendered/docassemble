#!/usr/bin/env python3
"""
Find Common Fields Across All Ontario Family Law Forms
Analyzes parsed JSON and CSV files to identify common fields like:
- Court information
- Applicant/Respondent details
- Lawyer information
- Common administrative fields
"""

import json
import csv
import re
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CommonFieldAnalyzer:
    """Analyze parsed forms to find common fields"""
    
    def __init__(self):
        self.parsed_forms_dir = Path('parsed_forms')
        self.enhanced_forms_dir = Path('workflow_output/enhanced_parsed_forms')
        self.parser_results_dir = Path('parser_results')
        
        # Track fields across forms
        self.all_fields = defaultdict(list)  # field_name -> [(form, label, type)]
        self.field_labels = defaultdict(list)  # normalized_label -> [(form, original_label, field_name)]
        self.form_fields = defaultdict(set)  # form -> set of field_names
        
        # Common field patterns
        self.common_patterns = {
            'court': [
                r'court.*(?:name|location|address|file.*number|office)',
                r'(?:name|location|address).*court',
                r'court.*(?:file|case).*(?:number|no\.?)',
                r'judicial.*(?:region|district)',
            ],
            'applicant': [
                r'applicant.*(?:name|first|last|middle|surname|given)',
                r'(?:your|my).*name',
                r'party.*a.*name',
                r'petitioner',
                r'plaintiff',
                r'moving.*party',
            ],
            'respondent': [
                r'respondent.*(?:name|first|last|middle|surname|given)',
                r'(?:other|opposing).*party',
                r'party.*b.*name',
                r'defendant',
                r'responding.*party',
            ],
            'lawyer': [
                r'lawyer.*(?:name|firm|address|phone|email|lsuc)',
                r'(?:legal|law).*representative',
                r'counsel.*(?:name|for)',
                r'attorney',
                r'lsuc.*number',
                r'law.*society.*number',
            ],
            'children': [
                r'child.*(?:name|birth|age|dob)',
                r'(?:name|birth).*child',
                r'dependent.*(?:name|age)',
            ],
            'address': [
                r'(?:street|mailing|residential|home).*address',
                r'address.*(?:line|street|city|province|postal)',
                r'municipality',
                r'postal.*code',
                r'city.*province',
            ],
            'contact': [
                r'(?:phone|telephone|tel).*(?:number|home|work|cell|mobile)',
                r'email.*address',
                r'fax.*number',
                r'contact.*(?:information|details)',
            ],
            'date': [
                r'date.*(?:separation|marriage|birth|filing|service|hearing)',
                r'(?:separation|marriage|birth|filing|service|hearing).*date',
                r'valuation.*date',
            ],
            'signature': [
                r'signature',
                r'sworn.*(?:at|before)',
                r'commissioner.*oaths',
                r'affidavit',
                r'declaration',
            ],
            'financial': [
                r'income.*(?:monthly|annual|gross|net)',
                r'(?:asset|debt|expense|property).*value',
                r'support.*(?:amount|payment)',
                r'(?:monthly|annual).*(?:income|expense)',
            ]
        }
        
    def load_all_forms(self):
        """Load all parsed form data from various sources"""
        
        # Load from parsed_forms JSON files
        json_files = list(self.parsed_forms_dir.glob('*_fields.json'))
        logger.info(f"Found {len(json_files)} JSON files in parsed_forms")
        
        for json_file in json_files:
            self._load_json_file(json_file)
        
        # Load from enhanced parsed forms
        if self.enhanced_forms_dir.exists():
            enhanced_files = list(self.enhanced_forms_dir.glob('*.json'))
            logger.info(f"Found {len(enhanced_files)} enhanced JSON files")
            for json_file in enhanced_files:
                self._load_json_file(json_file)
        
        # Load from CSV files
        csv_files = list(self.parsed_forms_dir.glob('*_fields.csv'))
        logger.info(f"Found {len(csv_files)} CSV files in parsed_forms")
        
        for csv_file in csv_files:
            self._load_csv_file(csv_file)
        
        # Load from parser results
        if self.parser_results_dir.exists():
            for subdir in ['intelligent', 'simple', 'unified']:
                subpath = self.parser_results_dir / 'parser_results' / subdir
                if subpath.exists():
                    json_files = list(subpath.glob('*.json'))
                    logger.info(f"Found {len(json_files)} files in {subdir} parser results")
                    for json_file in json_files:
                        self._load_json_file(json_file)
    
    def _load_json_file(self, filepath: Path):
        """Load fields from a JSON file"""
        try:
            form_name = self._extract_form_name(filepath.stem)
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                # Handle list of field objects
                for field in data:
                    if isinstance(field, dict):
                        self._process_field(form_name, field)
            elif isinstance(data, dict):
                # Handle different JSON structures
                if 'fields' in data:
                    for field in data['fields']:
                        self._process_field(form_name, field)
                elif 'form_fields' in data:
                    for field in data['form_fields']:
                        self._process_field(form_name, field)
                else:
                    # Might be a single field or nested structure
                    for key, value in data.items():
                        if isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict):
                                    self._process_field(form_name, item)
                        elif isinstance(value, dict):
                            self._process_field(form_name, value)
        except Exception as e:
            logger.warning(f"Error loading {filepath}: {e}")
    
    def _load_csv_file(self, filepath: Path):
        """Load fields from a CSV file"""
        try:
            form_name = self._extract_form_name(filepath.stem)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self._process_field(form_name, row)
        except Exception as e:
            logger.warning(f"Error loading CSV {filepath}: {e}")
    
    def _process_field(self, form_name: str, field_data: dict):
        """Process a single field entry"""
        # Extract field information
        field_name = (
            field_data.get('field_name') or 
            field_data.get('name') or 
            field_data.get('variable') or
            field_data.get('field_id') or
            ''
        )
        
        field_label = (
            field_data.get('field_label') or 
            field_data.get('label') or 
            field_data.get('text') or
            field_data.get('question') or
            field_name
        )
        
        field_type = (
            field_data.get('field_type') or 
            field_data.get('type') or 
            field_data.get('datatype') or
            'text'
        )
        
        if field_name:
            self.all_fields[field_name].append((form_name, field_label, field_type))
            self.form_fields[form_name].add(field_name)
            
            # Normalize label for comparison
            normalized = self._normalize_label(field_label)
            if normalized:
                self.field_labels[normalized].append((form_name, field_label, field_name))
    
    def _extract_form_name(self, filename: str) -> str:
        """Extract form number from filename"""
        # Look for patterns like form_13, form_8A, etc.
        match = re.search(r'form[_\s]*(\d+[A-Z]?\.?\d*)', filename, re.IGNORECASE)
        if match:
            return f"Form {match.group(1)}"
        return filename
    
    def _normalize_label(self, label: str) -> str:
        """Normalize field label for comparison"""
        if not label:
            return ""
        
        # Convert to lowercase and remove special characters
        normalized = re.sub(r'[^\w\s]', ' ', label.lower())
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        # Remove common words
        stop_words = {'the', 'a', 'an', 'of', 'for', 'and', 'or', 'if', 'any', 'please', 'enter', 'provide'}
        words = [w for w in normalized.split() if w not in stop_words]
        
        return ' '.join(words)
    
    def find_common_fields(self, min_forms: int = 3) -> Dict[str, List]:
        """Find fields that appear in at least min_forms forms"""
        common_fields = {}
        
        # Check by normalized label
        for normalized_label, occurrences in self.field_labels.items():
            unique_forms = set(occ[0] for occ in occurrences)
            
            if len(unique_forms) >= min_forms:
                common_fields[normalized_label] = {
                    'count': len(unique_forms),
                    'forms': sorted(unique_forms),
                    'variations': [
                        {
                            'form': occ[0],
                            'label': occ[1],
                            'field_name': occ[2]
                        }
                        for occ in occurrences[:10]  # Limit to first 10 examples
                    ]
                }
        
        return common_fields
    
    def categorize_common_fields(self) -> Dict[str, Dict]:
        """Categorize fields by type (court, applicant, etc.)"""
        categorized = defaultdict(lambda: defaultdict(list))
        
        for normalized_label, occurrences in self.field_labels.items():
            for category, patterns in self.common_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, normalized_label, re.IGNORECASE):
                        unique_forms = set(occ[0] for occ in occurrences)
                        
                        categorized[category][normalized_label] = {
                            'count': len(unique_forms),
                            'forms': sorted(unique_forms),
                            'examples': [
                                {
                                    'form': occ[0],
                                    'label': occ[1],
                                    'field_name': occ[2]
                                }
                                for occ in occurrences[:5]
                            ]
                        }
                        break
        
        return dict(categorized)
    
    def find_field_groups(self) -> Dict[str, Set[str]]:
        """Find groups of fields that commonly appear together"""
        field_groups = defaultdict(set)
        
        # Find fields that appear in the same forms
        for form, fields in self.form_fields.items():
            # Look for common prefixes in field names
            prefixes = defaultdict(set)
            for field in fields:
                # Extract prefix (e.g., "applicant_" from "applicant_name")
                match = re.match(r'^([a-z]+_)', field.lower())
                if match:
                    prefix = match.group(1)
                    prefixes[prefix].add(field)
            
            # Add significant groups
            for prefix, group_fields in prefixes.items():
                if len(group_fields) >= 3:  # At least 3 related fields
                    field_groups[prefix].update(group_fields)
        
        return dict(field_groups)
    
    def generate_report(self):
        """Generate comprehensive report of common fields"""
        
        logger.info("Analyzing common fields across all forms...")
        
        # Find common fields
        common_fields = self.find_common_fields(min_forms=5)
        categorized = self.categorize_common_fields()
        field_groups = self.find_field_groups()
        
        # Generate report
        report = {
            'summary': {
                'total_forms': len(self.form_fields),
                'total_unique_fields': len(self.all_fields),
                'total_field_instances': sum(len(v) for v in self.all_fields.values()),
                'common_fields_found': len(common_fields)
            },
            'most_common_fields': {},
            'categorized_fields': categorized,
            'field_groups': {k: list(v) for k, v in field_groups.items()},
            'recommendations': []
        }
        
        # Get most common fields
        sorted_common = sorted(
            common_fields.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:20]  # Top 20 most common
        
        for label, info in sorted_common:
            report['most_common_fields'][label] = info
        
        # Add recommendations
        if 'court' in categorized:
            report['recommendations'].append(
                "Create a standard 'CourtInfo' object with fields for court name, "
                "location, file number, and judicial region"
            )
        
        if 'applicant' in categorized and 'respondent' in categorized:
            report['recommendations'].append(
                "Use standard 'Individual' objects for applicant and respondent "
                "with consistent field naming"
            )
        
        if 'lawyer' in categorized:
            report['recommendations'].append(
                "Create a 'LegalRepresentative' object with standard fields for "
                "lawyer information across all forms"
            )
        
        # Save report
        report_file = Path('common_fields_report.json')
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved to {report_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("COMMON FIELDS ANALYSIS REPORT")
        print("="*60)
        print(f"\nTotal forms analyzed: {report['summary']['total_forms']}")
        print(f"Total unique fields: {report['summary']['total_unique_fields']}")
        print(f"Common fields found: {report['summary']['common_fields_found']}")
        
        print("\n" + "-"*40)
        print("TOP 10 MOST COMMON FIELDS:")
        print("-"*40)
        
        for i, (label, info) in enumerate(sorted_common[:10], 1):
            print(f"\n{i}. {label.title()}")
            print(f"   Appears in {info['count']} forms")
            print(f"   Example: {info['variations'][0]['label']}")
        
        print("\n" + "-"*40)
        print("FIELDS BY CATEGORY:")
        print("-"*40)
        
        for category, fields in categorized.items():
            print(f"\n{category.upper()}: {len(fields)} unique fields")
            # Show top 3 in category
            top_fields = sorted(
                fields.items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )[:3]
            for field_label, info in top_fields:
                print(f"  - {field_label}: {info['count']} forms")
        
        print("\n" + "-"*40)
        print("RECOMMENDATIONS:")
        print("-"*40)
        for rec in report['recommendations']:
            print(f"• {rec}")
        
        return report
    
    def export_standard_fields(self):
        """Export a standardized field mapping for common elements"""
        
        categorized = self.categorize_common_fields()
        
        standard_mapping = {
            'court_info': {
                'court_name': {'type': 'text', 'required': True},
                'court_file_number': {'type': 'text', 'required': True},
                'court_location': {'type': 'text', 'required': False},
                'judicial_region': {'type': 'text', 'required': False},
            },
            'party_info': {
                'first_name': {'type': 'text', 'required': True},
                'last_name': {'type': 'text', 'required': True},
                'middle_name': {'type': 'text', 'required': False},
                'birthdate': {'type': 'date', 'required': False},
                'address': {
                    'street': {'type': 'text', 'required': True},
                    'city': {'type': 'text', 'required': True},
                    'province': {'type': 'text', 'required': True},
                    'postal_code': {'type': 'text', 'required': True},
                },
                'phone': {'type': 'phone', 'required': False},
                'email': {'type': 'email', 'required': False},
            },
            'lawyer_info': {
                'name': {'type': 'text', 'required': True},
                'firm': {'type': 'text', 'required': False},
                'lsuc_number': {'type': 'text', 'required': True},
                'address': {
                    'street': {'type': 'text', 'required': True},
                    'city': {'type': 'text', 'required': True},
                    'province': {'type': 'text', 'required': True},
                    'postal_code': {'type': 'text', 'required': True},
                },
                'phone': {'type': 'phone', 'required': True},
                'email': {'type': 'email', 'required': False},
                'fax': {'type': 'phone', 'required': False},
            },
            'child_info': {
                'full_name': {'type': 'text', 'required': True},
                'birthdate': {'type': 'date', 'required': True},
                'age': {'type': 'integer', 'required': False, 'calculated': True},
                'residing_with': {'type': 'text', 'required': False},
            }
        }
        
        # Save standard mapping
        mapping_file = Path('standard_field_mapping.json')
        with open(mapping_file, 'w') as f:
            json.dump(standard_mapping, f, indent=2)
        
        logger.info(f"Standard field mapping saved to {mapping_file}")
        
        return standard_mapping


def main():
    analyzer = CommonFieldAnalyzer()
    
    print("Loading all form data...")
    analyzer.load_all_forms()
    
    print("Analyzing common fields...")
    report = analyzer.generate_report()
    
    print("\nExporting standard field mappings...")
    standard_mapping = analyzer.export_standard_fields()
    
    print("\n" + "="*60)
    print("Analysis complete!")
    print(f"• Full report: common_fields_report.json")
    print(f"• Standard mappings: standard_field_mapping.json")
    print("="*60)


if __name__ == "__main__":
    main()