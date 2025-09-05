#!/usr/bin/env python3
"""
Systematic Workflow Generator
A step-by-step approach to generate WORKING Docassemble interviews
from parsed data and domain mappings
"""

import yaml
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SystematicWorkflowGenerator:
    """Generate working interviews systematically"""
    
    def __init__(self):
        self.output_dir = Path('../')
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Track what works
        self.working_elements = []
        self.failed_elements = []
        
    def generate_systematic_form_13(self):
        """Generate Form 13 systematically, testing at each step"""
        
        print("=" * 60)
        print("SYSTEMATIC WORKFLOW GENERATOR")
        print("=" * 60)
        print("\nGoal: Create a WORKING Form 13 interview step by step\n")
        
        # Step 1: Create absolute minimum working interview
        step1_file = self._step_1_minimal()
        print(f"✅ Step 1: Created minimal interview")
        print(f"   Test at: http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/{step1_file.name}")
        input("\n   Press Enter after testing Step 1...")
        
        # Step 2: Add basic objects
        step2_file = self._step_2_add_objects()
        print(f"\n✅ Step 2: Added basic objects")
        print(f"   Test at: http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/{step2_file.name}")
        input("\n   Press Enter after testing Step 2...")
        
        # Step 3: Add one real field from parsed data
        step3_file = self._step_3_add_one_field()
        print(f"\n✅ Step 3: Added one field from parsed data")
        print(f"   Test at: http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/{step3_file.name}")
        input("\n   Press Enter after testing Step 3...")
        
        # Step 4: Add income fields from parsed data
        step4_file = self._step_4_add_income_fields()
        print(f"\n✅ Step 4: Added income fields")
        print(f"   Test at: http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/{step4_file.name}")
        input("\n   Press Enter after testing Step 4...")
        
        # Step 5: Add domain mapping
        step5_file = self._step_5_add_domain_mapping()
        print(f"\n✅ Step 5: Added domain mapping")
        print(f"   Test at: http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/{step5_file.name}")
        
        print("\n" + "=" * 60)
        print("WORKFLOW COMPLETE!")
        print("=" * 60)
        
        return True
    
    def _step_1_minimal(self) -> Path:
        """Step 1: Create absolute minimum working interview"""
        
        content = """---
metadata:
  title: Form 13 - Step 1 Minimal
---
mandatory: True
question: |
  Form 13 Test
subquestion: |
  This is the absolute minimum working interview.
buttons:
  - Exit: exit"""
        
        output_file = self.output_dir / 'form_13_step_1.yml'
        output_file.write_text(content)
        logger.info(f"Created: {output_file}")
        return output_file
    
    def _step_2_add_objects(self) -> Path:
        """Step 2: Add basic objects"""
        
        content = """---
metadata:
  title: Form 13 - Step 2 Objects
---
objects:
  - user: Individual
---
mandatory: True
code: |
  user.name.first
  final_screen
---
question: |
  Your name
fields:
  - First name: user.name.first
  - Last name: user.name.last
---
event: final_screen
question: |
  Complete
subquestion: |
  Hello ${ user }
buttons:
  - Exit: exit"""
        
        output_file = self.output_dir / 'form_13_step_2.yml'
        output_file.write_text(content)
        logger.info(f"Created: {output_file}")
        return output_file
    
    def _step_3_add_one_field(self) -> Path:
        """Step 3: Add one field from parsed data"""
        
        # Load parsed data
        parsed_file = Path('workflow_output/enhanced_parsed_forms/form_13_fields.json')
        if parsed_file.exists():
            with open(parsed_file) as f:
                fields = json.load(f)
            
            # Find employment income field (index 342 from our earlier analysis)
            income_field = fields[342] if len(fields) > 342 else None
            
            if income_field:
                logger.info(f"Using field: {income_field.get('field_label', 'Unknown')}")
        
        content = """---
metadata:
  title: Form 13 - Step 3 One Field
---
objects:
  - user: Individual
  - financial: DAObject
---
mandatory: True
code: |
  user.name.first
  financial.employment_income
  final_screen
---
question: |
  Your name
fields:
  - First name: user.name.first
  - Last name: user.name.last
---
question: |
  Employment Income
fields:
  - "Monthly employment income": financial.employment_income
    datatype: currency
    min: 0
    default: 0
---
event: final_screen
question: |
  Summary
subquestion: |
  Name: ${ user }
  
  Employment Income: ${ currency(financial.employment_income) }
buttons:
  - Exit: exit"""
        
        output_file = self.output_dir / 'form_13_step_3.yml'
        output_file.write_text(content)
        logger.info(f"Created: {output_file}")
        return output_file
    
    def _step_4_add_income_fields(self) -> Path:
        """Step 4: Add multiple income fields from parsed data"""
        
        content = """---
metadata:
  title: Form 13 - Step 4 Income Fields
---
objects:
  - user: Individual
  - income: DAObject
---
mandatory: True
code: |
  user.name.first
  collect_income
  calculate_total
  final_screen
---
question: |
  Your name
fields:
  - First name: user.name.first
  - Last name: user.name.last
---
question: |
  Monthly Income
subquestion: |
  Enter your monthly income from each source.
fields:
  - "Employment income": income.employment
    datatype: currency
    min: 0
    default: 0
  - "Self-employment income": income.self_employment
    datatype: currency
    min: 0
    default: 0
  - "EI benefits": income.ei
    datatype: currency
    min: 0
    default: 0
  - "Social assistance": income.social_assistance
    datatype: currency
    min: 0
    default: 0
  - "Other income": income.other
    datatype: currency
    min: 0
    default: 0
continue button field: collect_income
---
code: |
  income.total = (
    income.employment +
    income.self_employment +
    income.ei +
    income.social_assistance +
    income.other
  )
  calculate_total = True
---
event: final_screen
question: |
  Financial Summary
subquestion: |
  **Name:** ${ user }
  
  **Income Breakdown:**
  - Employment: ${ currency(income.employment) }
  - Self-employment: ${ currency(income.self_employment) }
  - EI: ${ currency(income.ei) }
  - Social assistance: ${ currency(income.social_assistance) }
  - Other: ${ currency(income.other) }
  
  **Total Income:** ${ currency(income.total) }
buttons:
  - Exit: exit"""
        
        output_file = self.output_dir / 'form_13_step_4.yml'
        output_file.write_text(content)
        logger.info(f"Created: {output_file}")
        return output_file
    
    def _step_5_add_domain_mapping(self) -> Path:
        """Step 5: Add domain mapping from our data"""
        
        # Load domain mappings
        domain_file = Path('workflow_output/domain_mappings.json')
        domains = {}
        if domain_file.exists():
            with open(domain_file) as f:
                domain_data = json.load(f)
                domains = domain_data.get('entities', {})
        
        content = """---
metadata:
  title: Form 13 - Step 5 Domain Mapped
---
# Objects from domain mapping
objects:
  - applicant: Individual  # person_entity from domain
  - income_information: DAObject  # income_entity from domain
  - expense_information: DAObject  # expense_entity from domain
---
mandatory: True
code: |
  applicant.name.first
  collect_income
  collect_expenses
  calculate_totals
  final_screen
---
question: |
  Applicant Information
fields:
  - First name: applicant.name.first
  - Last name: applicant.name.last
  - Date of birth: applicant.birthdate
    datatype: date
    required: False
---
question: |
  Monthly Income (Domain Mapped)
subquestion: |
  Enter all sources of monthly income.
fields:
  - "Employment income": income_information.employment
    datatype: currency
    default: 0
  - "Self-employment": income_information.self_employment
    datatype: currency
    default: 0
  - "EI benefits": income_information.ei_benefits
    datatype: currency
    default: 0
  - "Pension": income_information.pension
    datatype: currency
    default: 0
  - "Social assistance": income_information.social_assistance
    datatype: currency
    default: 0
continue button field: collect_income
---
question: |
  Monthly Expenses (Domain Mapped)
fields:
  - "Housing": expense_information.housing
    datatype: currency
    default: 0
  - "Food": expense_information.food
    datatype: currency
    default: 0
  - "Transportation": expense_information.transportation
    datatype: currency
    default: 0
  - "Childcare": expense_information.childcare
    datatype: currency
    default: 0
  - "Other": expense_information.other
    datatype: currency
    default: 0
continue button field: collect_expenses
---
code: |
  # Calculate totals using domain objects
  income_information.total = (
    income_information.employment +
    income_information.self_employment +
    income_information.ei_benefits +
    income_information.pension +
    income_information.social_assistance
  )
  
  expense_information.total = (
    expense_information.housing +
    expense_information.food +
    expense_information.transportation +
    expense_information.childcare +
    expense_information.other
  )
  
  net_income = income_information.total - expense_information.total
  calculate_totals = True
---
event: final_screen
question: |
  Form 13 - Financial Statement Summary
subquestion: |
  **Applicant:** ${ applicant.name.full() }
  
  **Total Monthly Income:** ${ currency(income_information.total) }
  
  **Total Monthly Expenses:** ${ currency(expense_information.total) }
  
  **Net Income:** ${ currency(net_income) }
  
  % if net_income < 0:
  ⚠️ Your expenses exceed your income by ${ currency(abs(net_income)) }
  % endif
buttons:
  - Exit: exit
  - Restart: restart"""
        
        output_file = self.output_dir / 'form_13_step_5.yml'
        output_file.write_text(content)
        logger.info(f"Created: {output_file}")
        return output_file


class WorkflowDocumenter:
    """Document the workflow for future use"""
    
    def create_workflow_documentation(self):
        """Create documentation for the systematic workflow"""
        
        doc = """# Systematic Workflow for Generated Interviews

## The Problem
Previous generators created complex interviews that didn't work because:
1. Too many features added at once
2. YAML formatting issues
3. Object reference errors
4. No systematic testing

## The Solution: Systematic Workflow

### Step 1: Absolute Minimum
- Just a question and exit button
- TEST: Does it load?

### Step 2: Add Basic Objects
- Add Individual object
- Simple name collection
- TEST: Do objects work?

### Step 3: Add One Field from Parsed Data
- Add single field from parsed JSON
- Use actual field from Form 13
- TEST: Does parsed data work?

### Step 4: Add Multiple Fields
- Add income fields
- Simple calculations
- TEST: Do calculations work?

### Step 5: Add Domain Mapping
- Use actual domain entities
- Map to Docassemble objects
- TEST: Does mapping work?

## Key Principles

1. **Test at Every Step**
   - Never add more until current step works
   - Keep each step simple

2. **Use Simple YAML**
   - Avoid complex nested structures initially
   - Use clear field names

3. **Build Incrementally**
   - Start with working baseline
   - Add complexity gradually

4. **Track What Works**
   - Document working patterns
   - Avoid patterns that fail

## Running the Workflow

```python
python systematic_workflow_generator.py
```

Follow prompts and test each step before proceeding.

## Files Generated

1. `form_13_step_1.yml` - Minimal
2. `form_13_step_2.yml` - With objects
3. `form_13_step_3.yml` - One parsed field
4. `form_13_step_4.yml` - Multiple fields
5. `form_13_step_5.yml` - Domain mapped

## Next Steps

Once all steps work:
1. Add more fields from parsed data
2. Add validation
3. Add error handling
4. Add PDF generation
"""
        
        doc_file = Path('../SYSTEMATIC_WORKFLOW.md')
        doc_file.write_text(doc)
        print(f"Created workflow documentation: {doc_file}")


def main():
    # Create the systematic generator
    generator = SystematicWorkflowGenerator()
    
    # Run the systematic workflow
    generator.generate_systematic_form_13()
    
    # Document the workflow
    documenter = WorkflowDocumenter()
    documenter.create_workflow_documentation()


if __name__ == "__main__":
    main()