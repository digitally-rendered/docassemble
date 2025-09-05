#!/usr/bin/env python3
"""
Incremental Parser System
- Saves CSV for each parser per file
- Uses advanced parsers to validate simpler ones
- Improves simple parsers incrementally
"""

import os
import json
import csv
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict, field
from datetime import datetime
import pandas as pd
import logging

# Import our parsers
from intelligent_form_parser import IntelligentFormParser
from unified_parser_with_gcp import UnifiedFormParser
from comprehensive_form_parser import FormParser as ComprehensiveFormParser, PDFFormParser, WordFormParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ParserResult:
    """Result from a parser run"""
    parser_name: str
    form_path: str
    form_hash: str
    timestamp: str
    fields: List[Dict]
    metadata: Dict = field(default_factory=dict)
    
    @property
    def csv_filename(self) -> str:
        """Generate CSV filename for this result"""
        form_name = Path(self.form_path).stem
        return f"parser_results/{self.parser_name}/{form_name}_{self.form_hash[:8]}.csv"
    
    @property
    def json_filename(self) -> str:
        """Generate JSON filename for this result"""
        form_name = Path(self.form_path).stem
        return f"parser_results/{self.parser_name}/{form_name}_{self.form_hash[:8]}.json"

class IncrementalParserSystem:
    """
    System for incrementally improving parsers
    """
    
    def __init__(self, cache_dir: str = "parser_results"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for each parser
        self.parser_dirs = {
            'simple': self.cache_dir / 'simple',
            'intelligent': self.cache_dir / 'intelligent',
            'unified': self.cache_dir / 'unified'
        }
        
        for dir_path in self.parser_dirs.values():
            dir_path.mkdir(exist_ok=True)
        
        # Load improvement patterns learned from advanced parsers
        self.improvement_patterns = self._load_improvement_patterns()
    
    def get_file_hash(self, file_path: str) -> str:
        """Get hash of file for cache validation"""
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def load_cached_result(self, parser_name: str, form_path: str) -> Optional[ParserResult]:
        """Load cached parser result if available and valid"""
        try:
            form_hash = self.get_file_hash(form_path)
            form_name = Path(form_path).stem
            
            # Look for matching cached result
            parser_dir = self.parser_dirs.get(parser_name)
            if not parser_dir:
                return None
            
            # Find files matching this form
            for json_file in parser_dir.glob(f"{form_name}_*.json"):
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    result = ParserResult(**data)
                    
                    # Check if hash matches (file unchanged)
                    if result.form_hash == form_hash:
                        logger.info(f"Loaded cached {parser_name} results for {form_name}")
                        return result
        
        except Exception as e:
            logger.debug(f"Could not load cache for {parser_name}/{form_path}: {e}")
        
        return None
    
    def save_result(self, result: ParserResult):
        """Save parser result to cache"""
        # Save JSON
        json_path = self.cache_dir / result.json_filename
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, 'w') as f:
            json.dump(asdict(result), f, indent=2)
        
        # Save CSV
        csv_path = self.cache_dir / result.csv_filename
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(csv_path, 'w', newline='') as f:
            if result.fields:
                # Get all unique keys from all fields
                all_keys = set()
                for field in result.fields:
                    all_keys.update(field.keys())
                
                writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
                writer.writeheader()
                writer.writerows(result.fields)
        
        logger.info(f"Saved {result.parser_name} results to {csv_path.name}")
    
    def parse_with_simple(self, form_path: str, use_improvements: bool = True) -> ParserResult:
        """Parse with simple parser (potentially improved)"""
        # Check cache first
        cached = self.load_cached_result('simple', form_path)
        if cached and not use_improvements:
            return cached
        
        logger.info(f"Parsing {Path(form_path).name} with simple parser...")
        
        # Use comprehensive parser as our "simple" parser
        # Determine file type and use appropriate parser
        file_ext = Path(form_path).suffix.lower()
        form_number = Path(form_path).stem.split('_')[0] if '_' in Path(form_path).stem else "form"
        
        if file_ext == '.pdf':
            parser = PDFFormParser(form_path, form_number)
        else:
            parser = WordFormParser(form_path, form_number)
        
        fields = parser.extract_fields()
        
        # Apply improvements learned from advanced parsers
        if use_improvements:
            fields = self._apply_improvements(fields, 'simple')
        
        # Create result
        result = ParserResult(
            parser_name='simple',
            form_path=form_path,
            form_hash=self.get_file_hash(form_path),
            timestamp=datetime.now().isoformat(),
            fields=[asdict(f) for f in fields],
            metadata={'improvements_applied': use_improvements}
        )
        
        self.save_result(result)
        return result
    
    def parse_with_intelligent(self, form_path: str) -> ParserResult:
        """Parse with intelligent parser"""
        # Check cache first
        cached = self.load_cached_result('intelligent', form_path)
        if cached:
            return cached
        
        logger.info(f"Parsing {Path(form_path).name} with intelligent parser...")
        
        parser = IntelligentFormParser(form_path, use_ocr=True, use_ai=False)
        fields = parser.parse()
        
        # Create result
        result = ParserResult(
            parser_name='intelligent',
            form_path=form_path,
            form_hash=self.get_file_hash(form_path),
            timestamp=datetime.now().isoformat(),
            fields=[asdict(f) for f in fields],
            metadata={'ocr_used': True, 'ai_used': False}
        )
        
        self.save_result(result)
        return result
    
    def parse_with_unified(self, form_path: str, use_gcp: bool = False) -> ParserResult:
        """Parse with unified parser"""
        # Check cache first
        cached = self.load_cached_result('unified', form_path)
        if cached and not use_gcp:  # Re-run if GCP settings changed
            return cached
        
        logger.info(f"Parsing {Path(form_path).name} with unified parser...")
        
        parser = UnifiedFormParser(form_path, use_gcp=use_gcp)
        fields, validation_report = parser.parse_comprehensive()
        
        # Create result
        result = ParserResult(
            parser_name='unified',
            form_path=form_path,
            form_hash=self.get_file_hash(form_path),
            timestamp=datetime.now().isoformat(),
            fields=[asdict(f) for f in fields],
            metadata={'gcp_used': use_gcp, 'validation_report': validation_report}
        )
        
        self.save_result(result)
        return result
    
    def validate_and_improve(self, form_path: str) -> Dict:
        """
        Run all parsers, validate results, and improve simple parser
        """
        validation = {
            'form': form_path,
            'timestamp': datetime.now().isoformat(),
            'results': {},
            'improvements': [],
            'consistency': {}
        }
        
        # Run all parsers
        simple_result = self.parse_with_simple(form_path, use_improvements=False)
        intelligent_result = self.parse_with_intelligent(form_path)
        unified_result = self.parse_with_unified(form_path)
        
        validation['results'] = {
            'simple': len(simple_result.fields),
            'intelligent': len(intelligent_result.fields),
            'unified': len(unified_result.fields)
        }
        
        # Find fields that advanced parsers found but simple didn't
        simple_fields = self._normalize_fields(simple_result.fields)
        intelligent_fields = self._normalize_fields(intelligent_result.fields)
        unified_fields = self._normalize_fields(unified_result.fields)
        
        # Fields found by advanced but not simple
        missed_by_simple = (intelligent_fields | unified_fields) - simple_fields
        
        if missed_by_simple:
            logger.info(f"Simple parser missed {len(missed_by_simple)} fields")
            
            # Learn patterns from missed fields
            improvements = self._learn_patterns(
                missed_by_simple,
                intelligent_result.fields + unified_result.fields
            )
            
            validation['improvements'] = improvements
            
            # Save improvements
            self._save_improvements(form_path, improvements)
            
            # Re-run simple parser with improvements
            improved_result = self.parse_with_simple(form_path, use_improvements=True)
            validation['results']['simple_improved'] = len(improved_result.fields)
        
        # Calculate consistency scores
        all_fields = simple_fields | intelligent_fields | unified_fields
        common_fields = simple_fields & intelligent_fields & unified_fields
        
        validation['consistency'] = {
            'total_unique_fields': len(all_fields),
            'common_to_all': len(common_fields),
            'consistency_score': len(common_fields) / max(1, len(all_fields))
        }
        
        return validation
    
    def _normalize_fields(self, fields: List[Dict]) -> Set[Tuple]:
        """Normalize fields for comparison"""
        normalized = set()
        
        for field in fields:
            # Create normalized tuple (type, label_prefix)
            field_type = field.get('field_type', 'text').lower()
            field_label = field.get('field_label', '').lower()
            
            # Clean label
            field_label = field_label.replace('\u2002', ' ')
            field_label = ' '.join(field_label.split())[:30]  # First 30 chars
            
            normalized.add((field_type, field_label))
        
        return normalized
    
    def _learn_patterns(self, missed_fields: Set[Tuple], source_fields: List[Dict]) -> List[Dict]:
        """Learn patterns from fields that were missed"""
        patterns = []
        
        for field_type, field_label in missed_fields:
            # Find the original field data
            for source_field in source_fields:
                source_label = source_field.get('field_label', '').lower()
                source_label = ' '.join(source_label.split())[:30]
                
                if source_label == field_label:
                    # Extract pattern information
                    pattern = {
                        'field_type': field_type,
                        'keywords': self._extract_keywords(source_field),
                        'indicators': self._extract_indicators(source_field),
                        'context': source_field.get('context', ''),
                        'confidence_boost': 0.1
                    }
                    patterns.append(pattern)
                    break
        
        return patterns
    
    def _extract_keywords(self, field: Dict) -> List[str]:
        """Extract keywords from a field"""
        label = field.get('field_label', '').lower()
        keywords = []
        
        # Common form keywords
        form_keywords = [
            'name', 'date', 'address', 'phone', 'email', 'number',
            'amount', 'value', 'income', 'applicant', 'respondent',
            'court', 'file', 'birth', 'age', 'gender', 'postal'
        ]
        
        for keyword in form_keywords:
            if keyword in label:
                keywords.append(keyword)
        
        return keywords
    
    def _extract_indicators(self, field: Dict) -> List[str]:
        """Extract visual indicators from a field"""
        label = field.get('field_label', '')
        indicators = []
        
        # Check for common indicators
        if '___' in label:
            indicators.append('underscores')
        if ':' in label:
            indicators.append('colon')
        if '$' in label:
            indicators.append('currency')
        if '[ ]' in label or '□' in label:
            indicators.append('checkbox')
        if '( )' in label or '○' in label:
            indicators.append('radio')
        if '\u2002' in label:
            indicators.append('unicode_space')
        
        return indicators
    
    def _apply_improvements(self, fields: List, parser_name: str) -> List:
        """Apply learned improvements to parser results"""
        # Load improvements for this parser
        improvements = self._load_improvements(parser_name)
        
        if not improvements:
            return fields
        
        logger.info(f"Applying {len(improvements)} improvements to {parser_name} parser")
        
        # This would be where we apply the learned patterns
        # For now, just return the original fields
        # In a real implementation, we would:
        # 1. Add new field detection patterns
        # 2. Adjust confidence scores
        # 3. Improve field type detection
        
        return fields
    
    def _save_improvements(self, form_path: str, improvements: List[Dict]):
        """Save learned improvements"""
        improvements_file = self.cache_dir / 'improvements.json'
        
        try:
            if improvements_file.exists():
                with open(improvements_file, 'r') as f:
                    all_improvements = json.load(f)
            else:
                all_improvements = {}
            
            form_name = Path(form_path).stem
            all_improvements[form_name] = improvements
            
            with open(improvements_file, 'w') as f:
                json.dump(all_improvements, f, indent=2)
        
        except Exception as e:
            logger.error(f"Failed to save improvements: {e}")
    
    def _load_improvements(self, parser_name: str) -> List[Dict]:
        """Load improvements for a parser"""
        improvements_file = self.cache_dir / 'improvements.json'
        
        if not improvements_file.exists():
            return []
        
        try:
            with open(improvements_file, 'r') as f:
                return json.load(f).get(parser_name, [])
        except:
            return []
    
    def _load_improvement_patterns(self) -> Dict:
        """Load all improvement patterns"""
        improvements_file = self.cache_dir / 'improvements.json'
        
        if not improvements_file.exists():
            return {}
        
        try:
            with open(improvements_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def process_all_forms(self, forms_dir: str) -> pd.DataFrame:
        """Process all forms and return summary DataFrame"""
        results = []
        
        for root, dirs, files in os.walk(forms_dir):
            for file in files:
                if file.lower().endswith(('.docx', '.pdf')):
                    form_path = os.path.join(root, file)
                    print(f"\nProcessing: {file}")
                    
                    validation = self.validate_and_improve(form_path)
                    
                    # Create summary row
                    row = {
                        'form': file,
                        'simple_fields': validation['results'].get('simple', 0),
                        'intelligent_fields': validation['results'].get('intelligent', 0),
                        'unified_fields': validation['results'].get('unified', 0),
                        'simple_improved': validation['results'].get('simple_improved', 0),
                        'consistency_score': validation['consistency']['consistency_score'],
                        'improvements_count': len(validation['improvements'])
                    }
                    results.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(results)
        
        # Save summary
        df.to_csv(self.cache_dir / 'processing_summary.csv', index=False)
        
        return df

def main():
    """Main function"""
    print("=" * 80)
    print("INCREMENTAL PARSER SYSTEM")
    print("=" * 80)
    
    system = IncrementalParserSystem()
    
    # Process all forms
    df = system.process_all_forms("workflow_output/ontario_forms")
    
    # Print summary
    print("\n" + "=" * 80)
    print("PROCESSING SUMMARY")
    print("=" * 80)
    
    print(df.to_string())
    
    # Statistics
    print("\n" + "-" * 80)
    print("STATISTICS")
    print("-" * 80)
    
    print(f"Total forms processed: {len(df)}")
    print(f"Average consistency score: {df['consistency_score'].mean():.2%}")
    print(f"Total improvements learned: {df['improvements_count'].sum()}")
    
    if 'simple_improved' in df.columns:
        improvement = df['simple_improved'].sum() - df['simple_fields'].sum()
        print(f"Total fields gained through improvements: {improvement}")
    
    print("\n" + "=" * 80)
    print("Results saved to: parser_results/")
    print("Summary saved to: parser_results/processing_summary.csv")

if __name__ == "__main__":
    main()