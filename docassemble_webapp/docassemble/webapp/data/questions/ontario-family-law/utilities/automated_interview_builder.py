#!/usr/bin/env python3
"""
Automated Interview Builder
Automatically builds working Docassemble interviews from parsed data
Tests each component before adding more complexity
"""

import yaml
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class InterviewComponent:
    """Represents a component of the interview"""
    component_type: str  # 'metadata', 'objects', 'question', 'code', 'event'
    content: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    validated: bool = False


@dataclass
class InterviewBuilder:
    """Builds interviews from components"""
    components: List[InterviewComponent] = field(default_factory=list)
    
    def add_component(self, component: InterviewComponent) -> bool:
        """Add a component if valid"""
        if self._validate_component(component):
            self.components.append(component)
            component.validated = True
            return True
        return False
    
    def _validate_component(self, component: InterviewComponent) -> bool:
        """Validate a component before adding"""
        # Check dependencies exist
        existing_types = {c.component_type for c in self.components}
        existing_types.add('base')  # Base is always available
        for dep in component.dependencies:
            if dep not in existing_types:
                logger.warning(f"Missing dependency: {dep}")
                return False
        
        # Validate content structure
        if component.component_type == 'metadata':
            return 'title' in component.content
        elif component.component_type == 'objects':
            return isinstance(component.content, list)
        elif component.component_type == 'question':
            return 'question' in component.content
        elif component.component_type == 'code':
            return 'code' in component.content
        elif component.component_type == 'event':
            return 'event' in component.content and 'question' in component.content
        
        return True
    
    def to_yaml(self) -> str:
        """Convert to valid Docassemble YAML"""
        yaml_blocks = []
        
        for component in self.components:
            if component.component_type == 'metadata':
                yaml_blocks.append(yaml.dump({'metadata': component.content}, 
                                            default_flow_style=False, sort_keys=False))
            elif component.component_type == 'objects':
                # Handle objects specially - they should be a simple list
                yaml_blocks.append(yaml.dump({'objects': component.content}, 
                                            default_flow_style=False, sort_keys=False))
            else:
                yaml_blocks.append(yaml.dump(component.content, 
                                            default_flow_style=False, sort_keys=False))
        
        return '---\n' + '---\n'.join(yaml_blocks)


class AutomatedInterviewGenerator:
    """Automatically generates working interviews from parsed data"""
    
    def __init__(self):
        self.output_dir = Path('../')
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Load data sources
        self.parsed_fields = self._load_parsed_fields()
        self.domain_mappings = self._load_domain_mappings()
        
        # Track successful patterns
        self.working_patterns = []
        
    def _load_parsed_fields(self) -> List[Dict]:
        """Load parsed form fields"""
        path = Path('workflow_output/enhanced_parsed_forms/form_13_fields.json')
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return []
    
    def _load_domain_mappings(self) -> Dict:
        """Load domain mappings"""
        path = Path('workflow_output/domain_mappings.json')
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return {}
    
    def generate_working_interview(self, form_number: str = "13") -> Tuple[bool, Path]:
        """Generate a working interview automatically"""
        
        logger.info(f"Starting automated generation for Form {form_number}")
        
        # Create builder
        builder = InterviewBuilder()
        
        # Phase 1: Core components (always needed)
        self._add_core_components(builder, form_number)
        
        # Phase 2: Data collection components
        self._add_data_components(builder, form_number)
        
        # Phase 3: Logic components
        self._add_logic_components(builder)
        
        # Phase 4: Summary components
        self._add_summary_components(builder)
        
        # Generate YAML
        yaml_content = builder.to_yaml()
        
        # Save file
        output_file = self.output_dir / f'form_{form_number}_automated.yml'
        output_file.write_text(yaml_content)
        
        logger.info(f"Generated: {output_file}")
        
        # Validate the generated YAML
        is_valid = self._validate_yaml(yaml_content)
        
        return is_valid, output_file
    
    def _add_core_components(self, builder: InterviewBuilder, form_number: str):
        """Add core required components"""
        
        # 1. Metadata (always first)
        metadata = InterviewComponent(
            component_type='metadata',
            content={
                'title': f'Form {form_number} - Financial Statement',
                'short title': f'Form {form_number}'
            }
        )
        builder.add_component(metadata)
        
        # 2. Objects - content should be just the list, not wrapped in 'objects' key
        objects = InterviewComponent(
            component_type='objects',
            content=[
                {'applicant': 'Individual'},
                {'financial_data': 'DAObject'}
            ],
            dependencies=['metadata']
        )
        builder.add_component(objects)
        
        # 3. Mandatory flow
        flow = InterviewComponent(
            component_type='code',
            content={
                'mandatory': True,
                'code': '|\n  intro_seen\n  applicant.name.first\n  financial_data_collected\n  show_summary'
            },
            dependencies=['metadata']  # Changed from 'objects' to 'metadata'
        )
        builder.add_component(flow)
    
    def _add_data_components(self, builder: InterviewBuilder, form_number: str):
        """Add data collection components from parsed fields"""
        
        # Intro screen
        intro = InterviewComponent(
            component_type='question',
            content={
                'question': f'Form {form_number} Financial Statement',
                'subquestion': 'This interview will collect your financial information.',
                'continue button field': 'intro_seen'
            },
            dependencies=['metadata']
        )
        builder.add_component(intro)
        
        # Applicant info
        applicant = InterviewComponent(
            component_type='question',
            content={
                'question': 'Your Information',
                'fields': [
                    {'First Name': 'applicant.name.first'},
                    {'Last Name': 'applicant.name.last'}
                ]
            },
            dependencies=['metadata']  # Fixed dependency
        )
        builder.add_component(applicant)
        
        # Financial data - use simplified fields
        financial_fields = self._extract_simple_financial_fields()
        
        financial = InterviewComponent(
            component_type='question',
            content={
                'question': 'Financial Information',
                'subquestion': 'Enter your monthly amounts',
                'fields': financial_fields,
                'continue button field': 'financial_data_collected'
            },
            dependencies=['metadata']  # Fixed dependency
        )
        builder.add_component(financial)
    
    def _extract_simple_financial_fields(self) -> List[Dict]:
        """Extract simplified financial fields"""
        
        # Use simple, working field structure
        fields = [
            {
                'Monthly Income': 'financial_data.income',
                'datatype': 'currency',
                'default': 0
            },
            {
                'Monthly Expenses': 'financial_data.expenses',
                'datatype': 'currency',
                'default': 0
            }
        ]
        
        # If we have parsed data, try to add real fields
        if self.parsed_fields and len(self.parsed_fields) > 342:
            # We know income fields are around index 342
            for i in range(342, min(345, len(self.parsed_fields))):
                field = self.parsed_fields[i]
                if field.get('field_type') == 'currency':
                    # Create simple field name
                    field_name = f"field_{i}"
                    label = field.get('field_label', '')[:30]  # Truncate label
                    
                    fields.append({
                        label: f'financial_data.{field_name}',
                        'datatype': 'currency',
                        'default': 0,
                        'required': False
                    })
        
        return fields
    
    def _add_logic_components(self, builder: InterviewBuilder):
        """Add calculation logic"""
        
        calc = InterviewComponent(
            component_type='code',
            content={
                'code': '|\n  financial_data.net = financial_data.income - financial_data.expenses'
            },
            dependencies=['metadata']  # Fixed dependency
        )
        builder.add_component(calc)
    
    def _add_summary_components(self, builder: InterviewBuilder):
        """Add summary screen"""
        
        summary = InterviewComponent(
            component_type='event',
            content={
                'event': 'show_summary',
                'question': 'Summary',
                'subquestion': '|\n  **Name:** ${ applicant }\n  \n  **Monthly Income:** ${ currency(financial_data.income) }\n  \n  **Monthly Expenses:** ${ currency(financial_data.expenses) }\n  \n  **Net:** ${ currency(financial_data.net) }',
                'buttons': [
                    {'Exit': 'exit'}
                ]
            },
            dependencies=['metadata']  # Fixed dependency
        )
        builder.add_component(summary)
    
    def _validate_yaml(self, yaml_content: str) -> bool:
        """Validate the generated YAML"""
        try:
            # Parse as YAML
            documents = list(yaml.safe_load_all(yaml_content))
            
            # Check for required elements
            has_metadata = False
            has_mandatory = False
            has_question = False
            
            for doc in documents:
                if doc:
                    if 'metadata' in doc:
                        has_metadata = True
                    if 'mandatory' in doc:
                        has_mandatory = True
                    if 'question' in doc:
                        has_question = True
            
            is_valid = has_metadata and has_mandatory and has_question
            
            if is_valid:
                logger.info("✅ YAML validation passed")
            else:
                logger.warning(f"⚠️ YAML missing elements - metadata:{has_metadata}, mandatory:{has_mandatory}, question:{has_question}")
            
            return is_valid
            
        except yaml.YAMLError as e:
            logger.error(f"❌ YAML parsing error: {e}")
            return False


class BatchInterviewGenerator:
    """Generate interviews for multiple forms"""
    
    def __init__(self):
        self.generator = AutomatedInterviewGenerator()
        self.results = []
    
    def generate_all_forms(self):
        """Generate interviews for all available forms"""
        
        # Find all parsed form files
        parsed_dir = Path('workflow_output/enhanced_parsed_forms')
        if not parsed_dir.exists():
            parsed_dir = Path('parsed_forms')
        
        form_files = list(parsed_dir.glob('form_*_fields.json'))
        
        logger.info(f"Found {len(form_files)} forms to process")
        
        for form_file in form_files:
            # Extract form number
            form_number = form_file.stem.replace('form_', '').replace('_fields', '')
            
            logger.info(f"Processing Form {form_number}...")
            
            try:
                success, output_file = self.generator.generate_working_interview(form_number)
                self.results.append({
                    'form': form_number,
                    'success': success,
                    'file': str(output_file)
                })
            except Exception as e:
                logger.error(f"Failed to generate Form {form_number}: {e}")
                self.results.append({
                    'form': form_number,
                    'success': False,
                    'error': str(e)
                })
        
        # Save results
        self._save_results()
    
    def _save_results(self):
        """Save generation results"""
        
        results_file = Path('../generation_results.json')
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Print summary
        successful = sum(1 for r in self.results if r.get('success'))
        print(f"\n{'='*60}")
        print(f"GENERATION COMPLETE")
        print(f"{'='*60}")
        print(f"✅ Successful: {successful}/{len(self.results)}")
        print(f"📄 Results saved to: {results_file}")
        
        # Create index
        self._create_index()
    
    def _create_index(self):
        """Create an index of generated interviews"""
        
        index_content = """---
metadata:
  title: Auto-Generated Forms Index
---
mandatory: True
question: |
  Auto-Generated Ontario Family Law Forms
subquestion: |
  ## Successfully Generated Forms
  
"""
        
        for result in self.results:
            if result.get('success'):
                form_num = result['form']
                file_name = Path(result['file']).name
                index_content += f"  - [Form {form_num}](/interview?i=docassemble.webapp:ontario-family-law/{file_name})\n"
        
        index_content += """
  
buttons:
  - Exit: exit"""
        
        index_file = Path('../auto_generated_index.yml')
        index_file.write_text(index_content)
        print(f"📑 Index created: {index_file}")


def main():
    print("=" * 60)
    print("AUTOMATED INTERVIEW BUILDER")
    print("=" * 60)
    
    # Single form test
    generator = AutomatedInterviewGenerator()
    success, output_file = generator.generate_working_interview("13")
    
    if success:
        print(f"\n✅ Successfully generated Form 13")
        print(f"📄 Test at: http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/{output_file.name}")
    else:
        print(f"\n❌ Generation failed - check logs")
    
    # Batch generation
    print("\nStarting batch generation...")
    batch = BatchInterviewGenerator()
    batch.generate_all_forms()


if __name__ == "__main__":
    main()