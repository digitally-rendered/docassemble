#!/usr/bin/env python3
"""
Structured Interview Generator using Domain Object Mapping
Generates Docassemble interviews using the structured builder and domain mappings
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from docassemble_interview_builder import (
    InterviewBuilder, Metadata, Features, Question, EventScreen,
    ReviewScreen, ReviewItem, CodeBlock, MandatoryBlock, ObjectDeclaration,
    create_introduction_screen, create_completion_screen, 
    create_standard_features, create_validation_code
)
from domain_object_mapper import DomainObjectMapper, DomainEntity, DomainField
from error_handling_template import (
    generate_error_handling_includes,
    generate_error_handling_features,
    generate_error_handling_objects,
    generate_error_handling_code,
    generate_error_display_questions,
    generate_error_handling_review
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StructuredInterviewGenerator:
    """Generate interviews using structured components and domain mappings"""
    
    def __init__(self):
        self.output_dir = Path('workflow_output/structured_interviews')
        self.output_dir.mkdir(exist_ok=True)
        self.mapper = DomainObjectMapper()
        
    def generate_all_interviews(self):
        """Generate interviews for all forms"""
        # Load relationship data to get all forms
        relationship_data = self.mapper.relationship_data
        
        if not relationship_data:
            logger.error("No relationship data found")
            return 0
        
        generated_count = 0
        form_numbers = list(relationship_data.get('forms', {}).keys())
        
        for form_num in form_numbers:
            try:
                interview_file = self.generate_form_interview(form_num)
                if interview_file:
                    generated_count += 1
                    logger.info(f"Generated structured interview for Form {form_num}")
            except Exception as e:
                logger.error(f"Failed to generate Form {form_num}: {e}")
        
        # Generate master index
        self._generate_master_index(form_numbers)
        
        logger.info(f"Generated {generated_count} structured interviews")
        return generated_count
    
    def generate_form_interview(self, form_number: str) -> Optional[Path]:
        """Generate a single form interview using structured components"""
        
        # Load domain data
        entities, fields = self.mapper.load_form_data(form_number)
        
        if not fields:
            logger.warning(f"No fields found for Form {form_number}")
            return None
        
        # Create the interview builder
        builder = InterviewBuilder()
        
        # 1. Set metadata
        form_info = self.mapper.relationship_data.get('forms', {}).get(form_number, {})
        metadata = self._create_metadata(form_number, form_info, len(fields), len(entities))
        builder.set_metadata(metadata)
        
        # 2. Add includes (including error handling)
        builder.add_include("docassemble.base:data/questions/basic-questions.yml")
        if self._needs_financial_module(entities, fields):
            builder.add_include("docassemble.base:data/questions/financial.yml")
        
        # 3. Set features with error handling
        has_tables = form_info.get('table_count', 0) > 0
        features = create_standard_features(review=True, tables=has_tables)
        # Add debug features
        features.debug = True
        features.question_help_button = True
        features.question_back_button = True
        features.progress_bar = True
        features.progress_bar_method = "percentage"
        builder.set_features(features)
        
        # 4. Add object declarations from domain mapping
        objects = self.mapper.create_object_declarations(entities)
        for obj in objects:
            builder.add_object(obj)
        
        # Add error handling objects
        builder.add_object(ObjectDeclaration(name="error_log", object_type="DAList.using(object_type=DAObject, there_are_any=False)"))
        builder.add_object(ObjectDeclaration(name="debug_info", object_type="DAObject"))
        
        # 5. Add error handling code blocks
        error_code = generate_error_handling_code()
        # Parse the error code into individual blocks
        code_sections = error_code.split('---')
        for section in code_sections:
            if 'code:' in section:
                # Extract just the code part
                code_lines = section.split('code: |')[1] if 'code: |' in section else ""
                if code_lines.strip():
                    builder.add_code(CodeBlock(code=code_lines.strip()))
        
        # 6. Add validation code
        if self._needs_validation(fields):
            builder.add_code(CodeBlock(code=create_validation_code()))
        
        # 6. Add calculation functions if needed
        calc_code = self._generate_calculation_code(entities, fields)
        if calc_code:
            builder.add_code(CodeBlock(code=calc_code))
        
        # 7. Add mandatory flow
        flow = self.mapper.get_mandatory_flow(entities)
        builder.add_mandatory(MandatoryBlock(code=flow))
        
        # 8. Add introduction
        intro = self._create_introduction(form_number, entities, fields)
        builder.add_question(intro)
        
        # 9. Add entity questions
        for entity in entities:
            question = self.mapper.create_entity_question(entity, fields)
            if question:
                builder.add_question(question)
                
                # Add list collection question if needed
                if entity.cardinality == 'multiple':
                    list_question = self._create_list_collection_question(entity)
                    builder.add_question(list_question)
        
        # 10. Add orphan fields (not belonging to any entity)
        orphan_fields = [f for f in fields if not f.entity_id]
        if orphan_fields:
            orphan_question = self._create_orphan_fields_question(orphan_fields)
            builder.add_question(orphan_question)
        
        # 11. Add error display questions
        error_questions = generate_error_display_questions()
        # Parse and add error display questions
        question_sections = error_questions.split('---')
        for section in question_sections:
            if 'event:' in section or 'question:' in section:
                # These need to be added as raw YAML since they're event screens
                pass  # We'll handle these in the to_yaml method
        
        # 12. Add review screen with error handling
        review = self._create_review_screen(entities, fields)
        builder.add_review(review)
        
        # 13. Add completion screen
        completion = self._create_completion_screen(form_number)
        builder.add_event(completion)
        
        # Generate and save YAML with error handling additions
        yaml_content = builder.to_yaml()
        
        # Insert modules section after metadata
        lines = yaml_content.split('\n')
        new_lines = []
        inserted_modules = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            # Insert modules after first --- separator (after metadata)
            if not inserted_modules and line.strip() == '---' and i > 0:
                new_lines.append("modules:")
                new_lines.append("  - .debug_helpers")
                new_lines.append("  - docassemble.base.util")
                new_lines.append("---")
                inserted_modules = True
        
        yaml_content = '\n'.join(new_lines)
        
        # Append error handling questions directly
        error_questions = generate_error_display_questions()
        yaml_content += "\n" + error_questions
        
        output_file = self.output_dir / f"form_{form_number}_interview.yml"
        
        with open(output_file, 'w') as f:
            f.write(yaml_content)
        
        return output_file
    
    def _create_metadata(self, form_number: str, form_info: Dict, field_count: int, entity_count: int) -> Metadata:
        """Create metadata for the form"""
        
        # Try to get form title from analysis
        title = f"Ontario Family Law Form {form_number}"
        
        # Add more descriptive titles for known forms
        form_titles = {
            '13': 'Financial Statement (Support Claims)',
            '13.1': 'Financial Statement (Property and Support Claims)',
            '13A': 'Certificate of Financial Disclosure',
            '13B': 'Net Family Property Statement',
            '13C': 'Comparison of Net Family Properties',
            '8': 'Application (General)',
            '10': 'Answer',
            '14B': 'Motion Form',
            '15': 'Motion to Change',
            '25': 'Order (General)',
            '36': 'Affidavit for Divorce'
        }
        
        if form_number in form_titles:
            title = f"Form {form_number}: {form_titles[form_number]}"
        
        return Metadata(
            title=title,
            short_title=f"Form {form_number}",
            description=f"Structured interview with {field_count} fields and {entity_count} entities",
            authors=[{
                "name": "Structured Interview Generator",
                "organization": "Ontario Family Law Automation"
            }],
            form_number=form_number,
            form_category=self._get_form_category(form_number),
            tags=["ontario", "family-law", form_number]
        )
    
    def _get_form_category(self, form_number: str) -> str:
        """Determine form category"""
        if '13' in form_number or '26' in form_number:
            return 'financial'
        elif '8' in form_number or '10' in form_number:
            return 'application'
        elif '14' in form_number or '15' in form_number or '17' in form_number:
            return 'motion'
        elif '25' in form_number:
            return 'order'
        elif '36' in form_number:
            return 'divorce'
        else:
            return 'general'
    
    def _needs_financial_module(self, entities: List[DomainEntity], fields: List[DomainField]) -> bool:
        """Check if financial module is needed"""
        # Check entities
        for entity in entities:
            if entity.entity_type == 'financial':
                return True
        
        # Check field types
        for field in fields:
            if field.field_type in ['currency', 'income', 'expense', 'asset', 'debt']:
                return True
        
        return False
    
    def _needs_validation(self, fields: List[DomainField]) -> bool:
        """Check if validation code is needed"""
        for field in fields:
            if field.needs_validation():
                return True
        return False
    
    def _generate_calculation_code(self, entities: List[DomainEntity], fields: List[DomainField]) -> Optional[str]:
        """Generate calculation functions if needed"""
        calc_fields = [f for f in fields if 'total' in f.field_label.lower() or 'sum' in f.field_label.lower()]
        
        if not calc_fields:
            return None
        
        code_lines = ["# Calculation functions"]
        
        # Generate basic total functions
        for entity in entities:
            if entity.cardinality == 'multiple' and entity.entity_type == 'financial':
                var_name = entity.get_variable_name()
                code_lines.append(f"""
def calculate_{var_name}_total():
    '''Calculate total for {entity.entity_name}'''
    return calculate_total({var_name}, 'amount')
""")
        
        # Add net worth calculation for financial forms
        if any('13' in str(f.field_id) for f in fields):
            code_lines.append("""
def calculate_net_worth():
    '''Calculate net worth (assets - liabilities)'''
    total_assets = calculate_total(assets, 'value') if defined('assets') else 0
    total_debts = calculate_total(debts, 'amount') if defined('debts') else 0
    return total_assets - total_debts

def calculate_monthly_surplus():
    '''Calculate monthly surplus (income - expenses)'''
    total_income = calculate_total(income_sources, 'monthly_amount') if defined('income_sources') else 0
    total_expenses = calculate_total(expenses, 'monthly_amount') if defined('expenses') else 0
    return total_income - total_expenses
""")
        
        return '\n'.join(code_lines) if len(code_lines) > 1 else None
    
    def _create_introduction(self, form_number: str, entities: List[DomainEntity], fields: List[DomainField]) -> Question:
        """Create introduction screen"""
        
        # Build content list based on entities
        content_sections = []
        
        person_entities = [e for e in entities if e.entity_type == 'person']
        if person_entities:
            content_sections.append("- Personal information for parties involved")
        
        financial_entities = [e for e in entities if e.entity_type == 'financial']
        if financial_entities:
            content_sections.append("- Financial information and calculations")
        
        property_entities = [e for e in entities if e.entity_type == 'property']
        if property_entities:
            content_sections.append("- Property and asset details")
        
        if not content_sections:
            content_sections.append("- Form information")
        
        # Count sections
        num_sections = len(entities) + (1 if any(not f.entity_id for f in fields) else 0)
        
        content = f"""This structured interview will help you complete Form {form_number}.

You will be asked about:
{chr(10).join(content_sections)}

Total sections: {num_sections}
Fields to complete: {len(fields)}"""
        
        return create_introduction_screen(
            title=f"Form {form_number} Interview",
            content=content,
            button_label="Begin Interview"
        )
    
    def _create_list_collection_question(self, entity: DomainEntity) -> Question:
        """Create a question for collecting more items in a list"""
        var_name = entity.get_variable_name()
        
        return Question(
            question=f"Are there more {entity.entity_name.lower()} items to add?",
            yesno=f"{var_name}.there_is_another"
        )
    
    def _create_orphan_fields_question(self, orphan_fields: List[DomainField]) -> Question:
        """Create question for fields not belonging to any entity"""
        field_defs = self.mapper.create_field_definitions(orphan_fields)
        
        return Question(
            question="Additional Information",
            fields=field_defs,
            continue_button_field="additional_info_complete"
        )
    
    def _create_review_screen(self, entities: List[DomainEntity], fields: List[DomainField]) -> ReviewScreen:
        """Create review screen with actual fields"""
        review_items = [{"note": "### Review Your Information"}]
        
        # Add key fields from each entity
        for entity in entities[:10]:  # Limit to prevent huge review screens
            entity_fields = [f for f in fields if f.entity_id == entity.entity_id][:3]
            
            for field in entity_fields:
                var_name = entity.get_variable_name()
                if entity.cardinality == 'multiple':
                    # Skip list items in review (too complex)
                    continue
                
                field_name = self.mapper._sanitize_field_name(field.field_name)
                review_items.append(ReviewItem(
                    label=field.field_label,
                    field=f"{var_name}.{field_name}"
                ))
        
        # Add some orphan fields
        orphan_fields = [f for f in fields if not f.entity_id][:5]
        for field in orphan_fields:
            review_items.append(ReviewItem(
                label=field.field_label,
                field=self.mapper._sanitize_field_name(field.field_name)
            ))
        
        return ReviewScreen(
            review_items=review_items,
            question="Review Your Answers",
            subquestion="Please review all information before submitting. Click any item to edit.",
            continue_button_field="review_complete"
        )
    
    def _create_completion_screen(self, form_number: str) -> EventScreen:
        """Create completion screen"""
        content = f"""Your Form {form_number} has been completed successfully.

**Next Steps:**
1. Download your completed form
2. Review all information carefully
3. Print and sign where required
4. File with the appropriate Ontario court

**Important:** This is a structured, auto-generated form. Please review carefully before submission."""
        
        return create_completion_screen(
            title=f"Form {form_number} Complete",
            content=content,
            event_name="form_complete"
        )
    
    def _generate_master_index(self, form_numbers: List[str]):
        """Generate master index using structured builder"""
        builder = InterviewBuilder()
        
        # Create metadata
        metadata = Metadata(
            title="Ontario Family Law Forms - Structured Interviews",
            short_title="Forms Index",
            description="Index of all structured interviews with domain mappings",
            authors=[{
                "name": "Structured Interview System",
                "organization": "Ontario Family Law"
            }]
        )
        builder.set_metadata(metadata)
        
        # Create content
        content_lines = [
            f"This system contains {len(form_numbers)} structured interviews using domain object mapping.",
            "",
            "Each interview includes:",
            "- Domain entities mapped to Docassemble objects",
            "- Structured field definitions with proper validation",
            "- Calculation functions for financial forms",
            "- Entity-based question organization",
            "",
            "## Available Forms",
            ""
        ]
        
        # Categorize forms
        categories = {
            'Financial Forms': [],
            'Applications': [],
            'Motions': [],
            'Orders': [],
            'Other Forms': []
        }
        
        for form_num in sorted(form_numbers):
            form_info = self.mapper.relationship_data.get('forms', {}).get(form_num, {})
            link = f"[Form {form_num}](/interview?i=docassemble.webapp:ontario-family-law/utilities/workflow_output/structured_interviews/form_{form_num}_interview.yml)"
            
            if '13' in form_num or '26' in form_num:
                categories['Financial Forms'].append(link)
            elif '8' in form_num or '10' in form_num:
                categories['Applications'].append(link)
            elif '14' in form_num or '15' in form_num or '17' in form_num:
                categories['Motions'].append(link)
            elif '25' in form_num:
                categories['Orders'].append(link)
            else:
                categories['Other Forms'].append(link)
        
        for category, forms in categories.items():
            if forms:
                content_lines.append(f"### {category}")
                for form in forms:
                    content_lines.append(f"- {form}")
                content_lines.append("")
        
        # Create index question
        index_question = Question(
            question="# Ontario Family Law Structured Interviews",
            subquestion='\n'.join(content_lines)
        )
        builder.add_question(index_question)
        
        # Add mandatory
        builder.add_mandatory(MandatoryBlock(code="True", mandatory=True))
        
        # Generate and save
        yaml_content = builder.to_yaml()
        index_file = self.output_dir / '00_structured_index.yml'
        
        with open(index_file, 'w') as f:
            f.write(yaml_content)
        
        logger.info(f"Generated master index: {index_file}")


def main():
    """Generate all structured interviews"""
    generator = StructuredInterviewGenerator()
    
    # First, test domain mappings
    logger.info("Testing domain mappings...")
    generator.mapper.load_form_data("13")
    generator.mapper.export_mappings()
    
    # Generate all interviews
    logger.info("Generating structured interviews...")
    count = generator.generate_all_interviews()
    
    print(f"\nSuccessfully generated {count} structured interviews")
    print(f"Output directory: workflow_output/structured_interviews")
    print(f"Domain mappings: workflow_output/domain_mappings.json")
    print(f"Index file: workflow_output/structured_interviews/00_structured_index.yml")


if __name__ == "__main__":
    main()