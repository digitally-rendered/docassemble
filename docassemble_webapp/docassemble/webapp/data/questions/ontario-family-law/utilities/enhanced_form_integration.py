#!/usr/bin/env python3
"""
Enhanced Form Integration - Integrates common interview generator with existing parsing infrastructure
Uses existing automated_form_processor.py and field_validation_mapper.py
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

# Import existing infrastructure (keep this!)
sys.path.append(str(Path(__file__).parent))

from automated_form_processor import AutomatedFormProcessor, FormConfiguration
from field_validation_mapper import FieldValidator, ValidatedField
from common_interview_generator import CommonInterviewGenerator, InterviewDocument

logger = logging.getLogger(__name__)

@dataclass
class EnhancedFormResult:
    """Result of enhanced form processing"""
    form_number: str
    form_title: str
    common_interview_yaml: str
    parsed_fields_count: int
    validation_score: float
    generated_file_path: str
    processing_time: float

class EnhancedFormIntegrator:
    """Integrates existing parsing with new common interview generation"""
    
    def __init__(self):
        # Use existing infrastructure (don't change this!)
        self.form_processor = AutomatedFormProcessor()
        self.field_validator = FieldValidator()
        
        # New generation system
        self.interview_generator = CommonInterviewGenerator()
        
        # Load existing form registry
        self.forms_registry = self._load_existing_registry()
        
        logger.info("Enhanced Form Integrator initialized with existing infrastructure")
    
    def _load_existing_registry(self) -> Dict[str, FormConfiguration]:
        """Load existing forms registry from automated_form_processor"""
        try:
            registry_path = Path(__file__).parent / "ontario_forms_registry.json"
            if registry_path.exists():
                with open(registry_path, 'r') as f:
                    registry_data = json.load(f)
                
                forms_registry = {}
                for form_id, form_info in registry_data.items():
                    forms_registry[form_id] = FormConfiguration(
                        form_number=form_id,
                        form_title=form_info.get("title", ""),
                        form_type=form_info.get("type", "application"),
                        category=form_info.get("category", "general"),
                        url=form_info.get("url", ""),
                        filename=form_info.get("filename", "")
                    )
                
                logger.info(f"Loaded {len(forms_registry)} forms from existing registry")
                return forms_registry
            
        except Exception as e:
            logger.error(f"Error loading forms registry: {e}")
        
        return {}
    
    def _load_existing_parsed_fields(self, form_number: str) -> Tuple[List[Dict], List[ValidatedField]]:
        """Load existing parsed fields from utilities/parsed_forms/"""
        
        parsed_fields = []
        validated_fields = []
        
        try:
            # Load JSON parsed data (existing work!)
            parsed_file = Path(__file__).parent / "parsed_forms" / f"form_{form_number}_fields.json"
            
            if parsed_file.exists():
                with open(parsed_file, 'r') as f:
                    parsed_fields = json.load(f)
                
                logger.info(f"Loaded {len(parsed_fields)} parsed fields for Form {form_number}")
                
                # Convert to ValidatedField objects using existing mapper
                parser_results = {"existing_parser": parsed_fields}
                validated_fields, validation_report = self.field_validator.validate_fields(parser_results)
                
                logger.info(f"Validated {len(validated_fields)} fields for Form {form_number}")
            
        except Exception as e:
            logger.warning(f"Could not load parsed fields for Form {form_number}: {e}")
        
        return parsed_fields, validated_fields
    
    def generate_enhanced_interview(self, form_number: str) -> EnhancedFormResult:
        """Generate enhanced interview using existing parsing + new generation"""
        
        start_time = datetime.now()
        logger.info(f"Starting enhanced generation for Form {form_number}")
        
        # Load existing parsed and validated fields (reuse all existing work!)
        parsed_fields, validated_fields = self._load_existing_parsed_fields(form_number)
        
        # Generate base interview using common components
        base_interview = self.interview_generator.generate_interview(form_number)
        
        # Enhance interview with form-specific fields from existing parsing
        enhanced_interview = self._enhance_interview_with_parsed_fields(
            base_interview, 
            form_number,
            parsed_fields, 
            validated_fields
        )
        
        # Generate final YAML
        final_yaml = enhanced_interview.to_yaml()
        
        # Write to output file
        output_dir = Path(__file__).parent / "generated_interviews"
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"form_{form_number}_enhanced.yml"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_yaml)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Calculate validation score
        validation_score = self._calculate_validation_score(validated_fields)
        
        # Get form title
        form_config = self.forms_registry.get(form_number)
        form_title = form_config.form_title if form_config else f"Form {form_number}"
        
        result = EnhancedFormResult(
            form_number=form_number,
            form_title=form_title,
            common_interview_yaml=final_yaml,
            parsed_fields_count=len(parsed_fields),
            validation_score=validation_score,
            generated_file_path=str(output_file.absolute()),
            processing_time=processing_time
        )
        
        logger.info(f"Enhanced generation completed for Form {form_number} in {processing_time:.2f}s")
        
        return result
    
    def _enhance_interview_with_parsed_fields(self, 
                                            base_interview: InterviewDocument,
                                            form_number: str,
                                            parsed_fields: List[Dict],
                                            validated_fields: List[ValidatedField]) -> InterviewDocument:
        """Enhance base interview with form-specific fields from existing parsing"""
        
        # Don't replace common sections - enhance them
        enhanced_interview = base_interview
        
        # Add form-specific questions from parsed fields
        if validated_fields:
            form_specific_questions = self._generate_form_specific_questions(validated_fields)
            
            if form_specific_questions:
                from common_interview_generator import InterviewSection
                
                form_section = InterviewSection(
                    section_id="form_specific_fields",
                    title="Form-Specific Information",
                    yaml_objects=form_specific_questions,
                    order=75  # Between common sections and review
                )
                
                enhanced_interview.add_section(form_section)
                
                logger.info(f"Added {len(form_specific_questions)} form-specific questions")
        
        # Add form-specific validation
        if validated_fields:
            additional_validation = self._generate_field_validation_code(validated_fields)
            enhanced_interview.validation_code.extend(additional_validation)
        
        # Update metadata to indicate enhancement
        enhanced_interview.metadata.update({
            "enhanced_with_parsed_fields": True,
            "parsed_fields_count": len(parsed_fields),
            "validated_fields_count": len(validated_fields),
            "enhancement_date": datetime.now().isoformat()
        })
        
        return enhanced_interview
    
    def _generate_form_specific_questions(self, validated_fields: List[ValidatedField]) -> List[Dict[str, Any]]:
        """Generate form-specific questions from validated fields"""
        
        questions = []
        
        # Group fields by confidence and context
        high_confidence_fields = [f for f in validated_fields if f.consensus_score > 0.8]
        
        # Only include most relevant fields
        relevant_fields = self._filter_relevant_fields(high_confidence_fields)
        
        # Generate questions for field groups
        field_groups = self._group_fields_by_context(relevant_fields)
        
        for context, fields in field_groups.items():
            if len(fields) <= 5:  # Don't create overly complex questions
                question = self._create_question_from_field_group(context, fields)
                if question:
                    questions.append(question)
        
        return questions
    
    def _filter_relevant_fields(self, fields: List[ValidatedField]) -> List[ValidatedField]:
        """Filter fields to most relevant ones that aren't covered by common components"""
        
        # Fields covered by common components (skip these)
        common_field_patterns = [
            "name", "address", "phone", "email", "birthdate", "court", "file_number",
            "marriage_date", "separation_date", "income", "assets", "debts", "children"
        ]
        
        relevant_fields = []
        
        for field in fields:
            field_name_lower = field.canonical_name.lower()
            
            # Skip if covered by common components
            is_common = any(pattern in field_name_lower for pattern in common_field_patterns)
            
            if not is_common and field.consensus_score > 0.7:
                relevant_fields.append(field)
        
        # Limit to most confident fields
        relevant_fields.sort(key=lambda f: f.consensus_score, reverse=True)
        return relevant_fields[:20]  # Max 20 additional fields
    
    def _group_fields_by_context(self, fields: List[ValidatedField]) -> Dict[str, List[ValidatedField]]:
        """Group fields by page/context"""
        
        groups = {}
        
        for field in fields:
            # Use page number as primary grouping
            context = f"Page {field.page_number}" if field.page_number else "Additional Information"
            
            if context not in groups:
                groups[context] = []
            
            groups[context].append(field)
        
        # Limit group sizes
        filtered_groups = {}
        for context, field_list in groups.items():
            if len(field_list) <= 5:
                filtered_groups[context] = field_list
        
        return filtered_groups
    
    def _create_question_from_field_group(self, context: str, fields: List[ValidatedField]) -> Dict[str, Any]:
        """Create a Docassemble question from a group of fields"""
        
        question_fields = []
        
        for field in fields:
            field_def = {
                field.field_label or field.canonical_name: f"form_specific.{field.canonical_name}"
            }
            
            # Add datatype based on field type
            if field.field_type == "date":
                field_def["datatype"] = "date"
            elif field.field_type == "currency":
                field_def["datatype"] = "currency"
            elif field.field_type == "number":
                field_def["datatype"] = "number"
            
            # Make field optional since these are form-specific additions
            field_def["required"] = False
            
            question_fields.append(field_def)
        
        if not question_fields:
            return None
        
        return {
            "question": f"Additional Information - {context}",
            "subquestion": "Please provide any additional information specific to your form",
            "fields": question_fields,
            "required": False
        }
    
    def _generate_field_validation_code(self, validated_fields: List[ValidatedField]) -> List[str]:
        """Generate validation code for form-specific fields"""
        
        validation_lines = []
        
        for field in validated_fields:
            if field.validation_rules:
                for rule in field.validation_rules:
                    validation_lines.append(f"# Validation for {field.canonical_name}")
                    validation_lines.append(rule)
        
        return validation_lines
    
    def _calculate_validation_score(self, validated_fields: List[ValidatedField]) -> float:
        """Calculate overall validation score"""
        
        if not validated_fields:
            return 0.0
        
        total_score = sum(field.consensus_score for field in validated_fields)
        return total_score / len(validated_fields)
    
    def generate_all_enhanced_interviews(self) -> Dict[str, EnhancedFormResult]:
        """Generate enhanced interviews for all forms with parsed data"""
        
        logger.info("Starting enhanced generation for all forms")
        
        results = {}
        
        # Get all forms with parsed data
        parsed_forms_dir = Path(__file__).parent / "parsed_forms"
        
        if not parsed_forms_dir.exists():
            logger.error("Parsed forms directory not found!")
            return results
        
        # Find all parsed form files
        form_numbers = set()
        for file_path in parsed_forms_dir.glob("form_*_fields.json"):
            form_number = file_path.stem.replace("form_", "").replace("_fields", "")
            form_numbers.add(form_number)
        
        logger.info(f"Found {len(form_numbers)} forms with parsed data")
        
        # Generate enhanced interview for each form
        for form_number in sorted(form_numbers):
            try:
                logger.info(f"Processing Form {form_number}...")
                result = self.generate_enhanced_interview(form_number)
                results[form_number] = result
                logger.info(f"✅ Form {form_number} completed successfully")
                
            except Exception as e:
                logger.error(f"❌ Error processing Form {form_number}: {e}")
                continue
        
        return results
    
    def generate_processing_report(self, results: Dict[str, EnhancedFormResult]) -> str:
        """Generate processing report"""
        
        report_lines = [
            "Enhanced Form Generation Report",
            "=" * 40,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Forms Processed: {len(results)}",
            ""
        ]
        
        # Summary statistics
        total_fields = sum(r.parsed_fields_count for r in results.values())
        avg_validation = sum(r.validation_score for r in results.values()) / len(results) if results else 0
        total_time = sum(r.processing_time for r in results.values())
        
        report_lines.extend([
            "Summary Statistics:",
            f"  Total Parsed Fields: {total_fields:,}",
            f"  Average Validation Score: {avg_validation:.2f}",
            f"  Total Processing Time: {total_time:.2f} seconds",
            ""
        ])
        
        # Individual form results
        report_lines.append("Individual Form Results:")
        for form_number, result in sorted(results.items()):
            report_lines.extend([
                f"  Form {form_number}: {result.form_title}",
                f"    Parsed Fields: {result.parsed_fields_count}",
                f"    Validation Score: {result.validation_score:.2f}",
                f"    Processing Time: {result.processing_time:.2f}s",
                f"    Output File: {Path(result.generated_file_path).name}",
                ""
            ])
        
        # Files generated
        report_lines.extend([
            "Generated Files:",
            *[f"  {Path(r.generated_file_path).name}" for r in results.values()],
            "",
            "✅ All files are ready for use in Docassemble!"
        ])
        
        return "\n".join(report_lines)

def main():
    """Main execution function"""
    
    print("🚀 Enhanced Form Integration - Using Existing Infrastructure")
    print("=" * 60)
    print("✅ Keeping: automated_form_processor.py")
    print("✅ Keeping: field_validation_mapper.py") 
    print("✅ Keeping: All parsed form data in utilities/parsed_forms/")
    print("✅ Adding: Common interview components")
    print("✅ Adding: Enhanced YAML object generation")
    print()
    
    # Initialize integrator
    integrator = EnhancedFormIntegrator()
    
    # Generate all enhanced interviews
    results = integrator.generate_all_enhanced_interviews()
    
    # Generate and display report
    report = integrator.generate_processing_report(results)
    print(report)
    
    # Save report to file
    report_file = Path(__file__).parent / "generated_interviews" / "processing_report.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\n📄 Report saved to: {report_file}")
    print(f"📁 Generated interviews in: {Path(__file__).parent / 'generated_interviews'}")

if __name__ == "__main__":
    main()