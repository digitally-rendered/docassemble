#!/usr/bin/env python3
"""
Unified Parser Orchestrator
Integrates advanced document parser with existing parsing infrastructure
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import importlib
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to import existing parsers
EXISTING_PARSERS = {}

try:
    from intelligent_field_name_parser import IntelligentFieldNameParser
    EXISTING_PARSERS['intelligent_field_name'] = IntelligentFieldNameParser
except ImportError:
    logger.warning("IntelligentFieldNameParser not available")

try:
    from improved_form_parser import ImprovedFormParser
    EXISTING_PARSERS['improved_form'] = ImprovedFormParser
except ImportError:
    logger.warning("ImprovedFormParser not available")

try:
    from docx_longform_extractor import DocxLongFormExtractor
    EXISTING_PARSERS['docx_longform'] = DocxLongFormExtractor
except ImportError:
    logger.warning("DocxLongFormExtractor not available")

try:
    from field_label_enhancer import enhance_form_8_labels
    EXISTING_PARSERS['field_label_enhancer'] = enhance_form_8_labels
except ImportError:
    logger.warning("field_label_enhancer not available")

try:
    from context_enhanced_parser import ContextEnhancedParser
    EXISTING_PARSERS['context_enhanced'] = ContextEnhancedParser
except ImportError:
    logger.warning("ContextEnhancedParser not available")

try:
    from precise_field_mapper import PreciseFieldMapper
    EXISTING_PARSERS['precise_field_mapper'] = PreciseFieldMapper
except ImportError:
    logger.warning("PreciseFieldMapper not available")

# Try to import advanced parser
try:
    from advanced_document_parser import (
        AdvancedDocumentParser, 
        ExtractionMethod,
        ExtractedField,
        FieldType
    )
    ADVANCED_PARSER_AVAILABLE = True
except ImportError:
    ADVANCED_PARSER_AVAILABLE = False
    logger.warning("AdvancedDocumentParser not available - install requirements_advanced_parser.txt")


@dataclass
class UnifiedField:
    """Unified field representation across all parsers"""
    field_id: str
    field_name: str
    field_label: str
    field_type: str
    value: Optional[Any] = None
    confidence: float = 0.0
    source_parser: str = "unknown"
    alternatives: List[Dict] = None
    metadata: Dict = None
    validation_status: str = "unvalidated"
    
    def __post_init__(self):
        if self.alternatives is None:
            self.alternatives = []
        if self.metadata is None:
            self.metadata = {}


class ParserAdapter:
    """Adapts different parser outputs to unified format"""
    
    @staticmethod
    def adapt_intelligent_parser(result: Dict) -> List[UnifiedField]:
        """Adapt IntelligentFieldNameParser output"""
        fields = []
        
        if 'fields' in result:
            for field_data in result['fields']:
                unified = UnifiedField(
                    field_id=field_data.get('field_id', ''),
                    field_name=field_data.get('field_name', ''),
                    field_label=field_data.get('field_label', ''),
                    field_type=field_data.get('field_type', 'text'),
                    confidence=field_data.get('confidence_score', 0.7),
                    source_parser='intelligent_field_name',
                    metadata={
                        'original_control_name': field_data.get('original_control_name'),
                        'nearby_text': field_data.get('nearby_text'),
                        'section': field_data.get('section')
                    }
                )
                fields.append(unified)
                
        return fields
    
    @staticmethod
    def adapt_improved_parser(result: List[Dict]) -> List[UnifiedField]:
        """Adapt ImprovedFormParser output"""
        fields = []
        
        for field_data in result:
            unified = UnifiedField(
                field_id=field_data.get('field_id', ''),
                field_name=field_data.get('field_name', ''),
                field_label=field_data.get('field_label', ''),
                field_type=field_data.get('field_type', 'text'),
                confidence=0.6,  # Default confidence for this parser
                source_parser='improved_form',
                metadata={
                    'table_name': field_data.get('table_name'),
                    'table_row': field_data.get('table_row'),
                    'page_number': field_data.get('page_number')
                }
            )
            fields.append(unified)
            
        return fields
    
    @staticmethod
    def adapt_docx_longform(result: List) -> List[UnifiedField]:
        """Adapt DocxLongFormExtractor output"""
        fields = []
        
        for field_data in result:
            if hasattr(field_data, '__dict__'):
                field_dict = field_data.__dict__
            else:
                field_dict = field_data
                
            unified = UnifiedField(
                field_id=field_dict.get('field_id', ''),
                field_name=field_dict.get('field_key', ''),
                field_label=field_dict.get('prompt', ''),
                field_type='longtext',  # This parser focuses on long-form fields
                confidence=0.8,
                source_parser='docx_longform',
                metadata={
                    'instructions': field_dict.get('instructions'),
                    'min_lines': field_dict.get('min_lines'),
                    'category': field_dict.get('category')
                }
            )
            fields.append(unified)
            
        return fields
    
    @staticmethod
    def adapt_advanced_parser(result: Dict) -> List[UnifiedField]:
        """Adapt AdvancedDocumentParser output"""
        fields = []
        
        if 'fields' in result:
            for field_data in result['fields']:
                unified = UnifiedField(
                    field_id=field_data.get('field_id', ''),
                    field_name=field_data.get('field_name', ''),
                    field_label=field_data.get('field_label', ''),
                    field_type=field_data.get('field_type', 'text'),
                    value=field_data.get('value'),
                    confidence=field_data.get('confidence', 0.0),
                    source_parser='advanced_document',
                    alternatives=field_data.get('alternatives', []),
                    metadata=field_data.get('metadata', {}),
                    validation_status=field_data.get('validation_status', 'unvalidated')
                )
                fields.append(unified)
                
        return fields


class FieldReconciler:
    """Reconciles fields from multiple parsers"""
    
    @staticmethod
    def reconcile_fields(field_sets: List[List[UnifiedField]]) -> List[UnifiedField]:
        """
        Reconcile fields from multiple parsers
        Uses confidence scores and voting to determine best values
        """
        
        if not field_sets:
            return []
            
        # Group fields by similar names/labels
        field_groups = {}
        
        for fields in field_sets:
            for field in fields:
                # Create grouping key
                key = FieldReconciler._create_grouping_key(field)
                if key not in field_groups:
                    field_groups[key] = []
                field_groups[key].append(field)
        
        # Reconcile each group
        reconciled = []
        for key, group in field_groups.items():
            best_field = FieldReconciler._select_best_field(group)
            reconciled.append(best_field)
            
        return reconciled
    
    @staticmethod
    def _create_grouping_key(field: UnifiedField) -> str:
        """Create key for grouping similar fields"""
        # Normalize field name for grouping
        name_parts = []
        
        # Try field name
        if field.field_name:
            normalized = field.field_name.lower().replace('_', '').replace('-', '')
            name_parts.append(normalized[:20])  # Use first 20 chars
            
        # Try field label
        if field.field_label:
            label_normalized = field.field_label.lower()[:30]
            name_parts.append(label_normalized)
            
        return '|'.join(name_parts) if name_parts else 'unknown'
    
    @staticmethod
    def _select_best_field(group: List[UnifiedField]) -> UnifiedField:
        """Select best field from a group"""
        
        if len(group) == 1:
            return group[0]
            
        # Score each field
        scored_fields = []
        for field in group:
            score = FieldReconciler._calculate_field_score(field)
            scored_fields.append((score, field))
            
        # Sort by score and select best
        scored_fields.sort(key=lambda x: x[0], reverse=True)
        best_field = scored_fields[0][1]
        
        # Add alternatives from other fields
        for score, field in scored_fields[1:]:
            best_field.alternatives.append({
                'field_name': field.field_name,
                'field_label': field.field_label,
                'value': field.value,
                'confidence': field.confidence,
                'source': field.source_parser
            })
            
        # Update confidence based on agreement
        agreement_score = FieldReconciler._calculate_agreement(group)
        best_field.confidence = (best_field.confidence + agreement_score) / 2
        
        return best_field
    
    @staticmethod
    def _calculate_field_score(field: UnifiedField) -> float:
        """Calculate quality score for a field"""
        score = 0.0
        
        # Base confidence
        score += field.confidence * 10
        
        # Bonus for meaningful names
        if field.field_name and not field.field_name.startswith('field_'):
            score += 2
            
        # Bonus for descriptive labels
        if field.field_label and len(field.field_label) > 5:
            score += 2
            
        # Bonus for validated fields
        if field.validation_status == 'valid':
            score += 3
            
        # Bonus for having a value
        if field.value:
            score += 1
            
        # Parser-specific weights
        parser_weights = {
            'advanced_document': 1.5,
            'intelligent_field_name': 1.3,
            'context_enhanced': 1.2,
            'docx_longform': 1.1,
            'improved_form': 1.0
        }
        
        weight = parser_weights.get(field.source_parser, 1.0)
        score *= weight
        
        return score
    
    @staticmethod
    def _calculate_agreement(group: List[UnifiedField]) -> float:
        """Calculate agreement score among fields"""
        
        if len(group) <= 1:
            return 1.0
            
        # Check label agreement
        labels = [f.field_label for f in group if f.field_label]
        if labels:
            unique_labels = set(labels)
            label_agreement = 1.0 / len(unique_labels)
        else:
            label_agreement = 0.5
            
        # Check name agreement
        names = [f.field_name for f in group if f.field_name]
        if names:
            unique_names = set(names)
            name_agreement = 1.0 / len(unique_names)
        else:
            name_agreement = 0.5
            
        return (label_agreement + name_agreement) / 2


class UnifiedParserOrchestrator:
    """Main orchestrator for unified parsing"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.adapter = ParserAdapter()
        self.reconciler = FieldReconciler()
        
        # Initialize available parsers
        self.parsers = self._initialize_parsers()
        logger.info(f"Initialized with {len(self.parsers)} parsers")
        
    def _initialize_parsers(self) -> Dict[str, Any]:
        """Initialize all available parsers"""
        parsers = {}
        
        # Add existing parsers
        for name, parser_class in EXISTING_PARSERS.items():
            try:
                if callable(parser_class):
                    parsers[name] = parser_class
                else:
                    parsers[name] = parser_class()
                logger.info(f"Initialized parser: {name}")
            except Exception as e:
                logger.error(f"Failed to initialize {name}: {e}")
                
        # Add advanced parser if available
        if ADVANCED_PARSER_AVAILABLE:
            try:
                parsers['advanced'] = AdvancedDocumentParser(self.config)
                logger.info("Initialized advanced parser")
            except Exception as e:
                logger.error(f"Failed to initialize advanced parser: {e}")
                
        return parsers
    
    def parse_document(self, 
                       document_path: Path,
                       form_type: Optional[str] = None,
                       use_parsers: Optional[List[str]] = None,
                       reconcile_results: bool = True) -> Dict[str, Any]:
        """
        Parse document using multiple parsers
        
        Args:
            document_path: Path to document
            form_type: Type of form (e.g., 'form_8')
            use_parsers: List of parser names to use (None = use all)
            reconcile_results: Whether to reconcile results from multiple parsers
            
        Returns:
            Unified parsing results
        """
        
        if not document_path.exists():
            raise FileNotFoundError(f"Document not found: {document_path}")
            
        # Determine which parsers to use
        if use_parsers:
            active_parsers = {k: v for k, v in self.parsers.items() if k in use_parsers}
        else:
            active_parsers = self.parsers
            
        # Run each parser
        all_results = []
        parser_results = {}
        
        for parser_name, parser in active_parsers.items():
            try:
                logger.info(f"Running parser: {parser_name}")
                result = self._run_parser(parser_name, parser, document_path, form_type)
                
                if result:
                    # Adapt to unified format
                    unified_fields = self._adapt_result(parser_name, result)
                    all_results.append(unified_fields)
                    parser_results[parser_name] = {
                        'fields': unified_fields,
                        'raw_result': result
                    }
                    logger.info(f"{parser_name} extracted {len(unified_fields)} fields")
                    
            except Exception as e:
                logger.error(f"Parser {parser_name} failed: {e}")
                
        # Reconcile results if requested
        if reconcile_results and len(all_results) > 1:
            final_fields = self.reconciler.reconcile_fields(all_results)
            logger.info(f"Reconciled to {len(final_fields)} final fields")
        elif all_results:
            # Flatten all results
            final_fields = [field for fields in all_results for field in fields]
        else:
            final_fields = []
            
        # Prepare final result
        result = {
            'document_path': str(document_path),
            'form_type': form_type or self._detect_form_type(document_path),
            'parsers_used': list(parser_results.keys()),
            'total_fields': len(final_fields),
            'fields': [asdict(f) for f in final_fields],
            'parser_details': {
                name: {
                    'field_count': len(data['fields']),
                    'sample_fields': [asdict(f) for f in data['fields'][:3]]
                }
                for name, data in parser_results.items()
            },
            'reconciliation_applied': reconcile_results and len(all_results) > 1
        }
        
        return result
    
    def _run_parser(self, parser_name: str, parser: Any, 
                   document_path: Path, form_type: Optional[str]) -> Any:
        """Run a specific parser"""
        
        if parser_name == 'advanced':
            return parser.parse_document(document_path, form_type)
            
        elif parser_name == 'intelligent_field_name':
            parser_instance = parser(form_type or 'unknown')
            return parser_instance.parse_docx_file(document_path)
            
        elif parser_name == 'improved_form':
            if hasattr(parser, 'parse_form'):
                return parser.parse_form(document_path)
            
        elif parser_name == 'docx_longform':
            extractor = parser(str(document_path))
            return extractor.extract_all_longform_fields()
            
        elif parser_name == 'field_label_enhancer':
            # This is a function, not a class
            if callable(parser):
                return parser()
                
        elif parser_name == 'context_enhanced':
            if hasattr(parser, 'parse'):
                return parser.parse(document_path)
                
        elif parser_name == 'precise_field_mapper':
            if hasattr(parser, 'map_fields'):
                return parser.map_fields(document_path)
                
        return None
    
    def _adapt_result(self, parser_name: str, result: Any) -> List[UnifiedField]:
        """Adapt parser result to unified format"""
        
        if parser_name == 'advanced':
            return self.adapter.adapt_advanced_parser(result)
        elif parser_name == 'intelligent_field_name':
            return self.adapter.adapt_intelligent_parser(result)
        elif parser_name == 'improved_form':
            return self.adapter.adapt_improved_parser(result)
        elif parser_name == 'docx_longform':
            return self.adapter.adapt_docx_longform(result)
        else:
            # Generic adaptation
            if isinstance(result, list):
                return self.adapter.adapt_improved_parser(result)
            elif isinstance(result, dict) and 'fields' in result:
                return self.adapter.adapt_intelligent_parser(result)
                
        return []
    
    def _detect_form_type(self, document_path: Path) -> str:
        """Detect form type from filename"""
        filename = document_path.stem.lower()
        
        # Extract form number
        import re
        match = re.search(r'form[_\s-]?(\d+[a-z]?)', filename)
        if match:
            return f"form_{match.group(1)}"
            
        return "unknown"
    
    def compare_parsers(self, document_path: Path) -> Dict[str, Any]:
        """
        Run all parsers and compare their outputs
        Useful for evaluating parser performance
        """
        
        # Run without reconciliation to see individual results
        result = self.parse_document(
            document_path,
            reconcile_results=False
        )
        
        # Analyze differences
        comparison = {
            'document': str(document_path),
            'parser_comparison': {}
        }
        
        # Get all unique field names across parsers
        all_field_names = set()
        parser_fields = {}
        
        for field_data in result['fields']:
            field = UnifiedField(**field_data)
            all_field_names.add(field.field_name)
            
            if field.source_parser not in parser_fields:
                parser_fields[field.source_parser] = []
            parser_fields[field.source_parser].append(field)
            
        # Compare coverage
        for parser_name, fields in parser_fields.items():
            field_names = {f.field_name for f in fields}
            comparison['parser_comparison'][parser_name] = {
                'total_fields': len(fields),
                'unique_fields': len(field_names),
                'coverage': len(field_names) / len(all_field_names) if all_field_names else 0,
                'average_confidence': sum(f.confidence for f in fields) / len(fields) if fields else 0,
                'sample_fields': [f.field_name for f in fields[:5]]
            }
            
        return comparison


def main():
    """Example usage"""
    
    # Initialize orchestrator
    config = {
        'google_doc_ai_enabled': False,
        'azure_form_recognizer_enabled': False,
        'aws_textract_enabled': False
    }
    
    orchestrator = UnifiedParserOrchestrator(config)
    
    # Parse a document
    document_path = Path("test_download/core_applications/form_8_-_application_general_flr-8-jun25-en.docx")
    
    if document_path.exists():
        # Run unified parsing
        result = orchestrator.parse_document(
            document_path,
            form_type='form_8',
            reconcile_results=True
        )
        
        # Save results
        output_path = Path("parsed_forms/form_8_unified_extraction.json")
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
            
        print(f"Unified extraction complete. Results saved to {output_path}")
        print(f"Total fields extracted: {result['total_fields']}")
        print(f"Parsers used: {', '.join(result['parsers_used'])}")
        
        # Compare parsers
        comparison = orchestrator.compare_parsers(document_path)
        
        comparison_path = Path("parsed_forms/form_8_parser_comparison.json")
        with open(comparison_path, 'w') as f:
            json.dump(comparison, f, indent=2)
            
        print(f"\nParser comparison saved to {comparison_path}")
        
        for parser_name, stats in comparison['parser_comparison'].items():
            print(f"\n{parser_name}:")
            print(f"  - Fields: {stats['total_fields']}")
            print(f"  - Coverage: {stats['coverage']:.1%}")
            print(f"  - Avg Confidence: {stats['average_confidence']:.2f}")
            
    else:
        print(f"Document not found: {document_path}")


if __name__ == "__main__":
    main()