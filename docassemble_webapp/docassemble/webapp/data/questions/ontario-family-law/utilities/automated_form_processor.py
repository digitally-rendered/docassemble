#!/usr/bin/env python3
"""
Automated Ontario Family Law Forms Processor
Fully automated, repeatable workflow for processing all 46 forms
No manual coding required - just run and deploy
"""

import os
import sys
import json
import csv
import re
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('form_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class FormConfiguration:
    """Configuration for each form type"""
    form_number: str
    form_title: str
    form_type: str  # application, answer, motion, financial, order, etc.
    category: str  # divorce, custody, support, property, enforcement
    url: str
    filename: str
    requires_financial: bool = False
    has_children_section: bool = False
    has_property_section: bool = False
    dependencies: List[str] = field(default_factory=list)
    common_fields: List[str] = field(default_factory=list)
    custom_validation: Dict[str, str] = field(default_factory=dict)

class FormRegistry:
    """Registry of all Ontario family law forms with their metadata"""
    
    # Import the generated registry
    try:
        from form_registry_generated import FormRegistry as GeneratedRegistry
        FORMS = GeneratedRegistry.FORMS
    except ImportError:
        # Fallback to minimal set if generated registry not available
        FORMS = [
            FormConfiguration(
                form_number="4",
            form_title="Notice of Change in Representation",
            form_type="notice",
            category="procedural",
            url="https://ontariocourtforms.on.ca/en/family-law-rules-forms/",
            filename="form_4_notice_change_representation.pdf",
            common_fields=["lawyer_info", "party_info", "court_info"]
        ),
        FormConfiguration(
            form_number="6B",
            form_title="Affidavit of Service",
            form_type="affidavit",
            category="procedural",
            url="https://ontariocourtforms.on.ca/en/family-law-rules-forms/",
            filename="form_6b_affidavit_service.pdf",
            common_fields=["service_info", "party_info", "court_info"]
        ),
        FormConfiguration(
            form_number="8",
            form_title="Application (General)",
            form_type="application",
            category="general",
            url="https://ontariocourtforms.on.ca/en/family-law-rules-forms/",
            filename="form_8_application_general.pdf",
            requires_financial=True,
            has_children_section=True,
            has_property_section=True,
            common_fields=["applicant_info", "respondent_info", "children_info", "claims", "court_info"],
            dependencies=["13", "13.1"]
        ),
        FormConfiguration(
            form_number="8A",
            form_title="Application (Divorce)",
            form_type="application",
            category="divorce",
            url="https://ontariocourtforms.on.ca/en/family-law-rules-forms/",
            filename="form_8a_application_divorce.pdf",
            requires_financial=True,
            has_children_section=True,
            common_fields=["applicant_info", "respondent_info", "marriage_info", "children_info", "grounds", "court_info"],
            dependencies=["36", "13", "13.1"]
        ),
        FormConfiguration(
            form_number="10",
            form_title="Answer",
            form_type="answer",
            category="general",
            url="https://ontariocourtforms.on.ca/en/family-law-rules-forms/",
            filename="form_10_answer.pdf",
            requires_financial=True,
            has_children_section=True,
            common_fields=["respondent_info", "applicant_info", "response_claims", "court_info"],
            dependencies=["13", "13.1"]
        ),
        FormConfiguration(
            form_number="13",
            form_title="Financial Statement (Support Claims)",
            form_type="financial",
            category="support",
            url="https://ontariocourtforms.on.ca/en/family-law-rules-forms/",
            filename="form_13_financial_statement_support.pdf",
            requires_financial=True,
            common_fields=["party_info", "income_info", "expense_info", "asset_info", "debt_info"]
        ),
        FormConfiguration(
            form_number="13.1",
            form_title="Financial Statement (Property and Support Claims)",
            form_type="financial",
            category="property",
            url="https://ontariocourtforms.on.ca/en/family-law-rules-forms/",
            filename="form_13_1_financial_statement_property.pdf",
            requires_financial=True,
            has_property_section=True,
            common_fields=["party_info", "income_info", "expense_info", "property_info", "debt_info", "business_info"]
        ),
        FormConfiguration(
            form_number="14B",
            form_title="Motion Form",
            form_type="motion",
            category="general",
            url="https://ontariocourtforms.on.ca/en/family-law-rules-forms/",
            filename="form_14b_motion_form.pdf",
            common_fields=["moving_party_info", "responding_party_info", "relief_sought", "court_info"]
        ),
        FormConfiguration(
            form_number="15",
            form_title="Motion to Change",
            form_type="motion",
            category="variation",
            url="https://ontariocourtforms.on.ca/en/family-law-rules-forms/",
            filename="form_15_motion_to_change.pdf",
            requires_financial=True,
            has_children_section=True,
            common_fields=["moving_party_info", "responding_party_info", "existing_order", "changes_sought", "court_info"],
            dependencies=["13", "15A"]
        ),
        FormConfiguration(
            form_number="17A",
            form_title="Case Conference Brief",
            form_type="conference",
            category="procedural",
            url="https://ontariocourtforms.on.ca/en/family-law-rules-forms/",
            filename="form_17a_case_conference_brief.pdf",
            common_fields=["party_info", "issues", "settlement_position", "court_info"]
        ),
        FormConfiguration(
            form_number="25",
            form_title="Order (General)",
            form_type="order",
            category="general",
            url="https://ontariocourtforms.on.ca/en/family-law-rules-forms/",
            filename="form_25_order_general.pdf",
            common_fields=["party_info", "order_terms", "judge_info", "court_info"]
        ),
        FormConfiguration(
            form_number="25A",
            form_title="Divorce Order",
            form_type="order",
            category="divorce",
            url="https://ontariocourtforms.on.ca/en/family-law-rules-forms/",
            filename="form_25a_divorce_order.pdf",
            common_fields=["party_info", "divorce_terms", "judge_info", "court_info"]
        ),
        FormConfiguration(
            form_number="36",
            form_title="Affidavit for Divorce",
            form_type="affidavit",
            category="divorce",
            url="https://ontariocourtforms.on.ca/en/family-law-rules-forms/",
            filename="form_36_affidavit_divorce.pdf",
            has_children_section=True,
            common_fields=["applicant_info", "respondent_info", "marriage_info", "separation_info", "children_info", "reconciliation"]
        ),
        # Add remaining forms here...
    ]
    
    @classmethod
    def get_form(cls, form_number: str) -> Optional[FormConfiguration]:
        """Get form configuration by number"""
        for form in cls.FORMS:
            if form.form_number == form_number:
                return form
        return None
    
    @classmethod
    def get_all_forms(cls) -> List[FormConfiguration]:
        """Get all form configurations"""
        return cls.FORMS

class FieldMapping:
    """Intelligent field mapping system"""
    
    # Universal field mappings for Ontario forms
    FIELD_MAPPINGS = {
        # Party Information
        r"(applicant|petitioner|moving party).*name": {
            "variable": "applicant.name.text",
            "type": "text",
            "object": "Individual"
        },
        r"(respondent|responding party).*name": {
            "variable": "respondent.name.text",
            "type": "text",
            "object": "Individual"
        },
        r".*date.*birth": {
            "variable": "{party}.birthdate",
            "type": "date",
            "validation": "date_in_past"
        },
        r".*address": {
            "variable": "{party}.address.address",
            "type": "address",
            "object": "Address"
        },
        r".*phone": {
            "variable": "{party}.phone_number",
            "type": "phone",
            "validation": "phone_number_10"
        },
        r".*email": {
            "variable": "{party}.email",
            "type": "email",
            "validation": "email"
        },
        
        # Court Information
        r"court.*file.*number": {
            "variable": "court_info.file_number",
            "type": "text",
            "required": True
        },
        r"court.*location|municipality": {
            "variable": "court_info.location",
            "type": "dropdown",
            "choices": "ontario_court_locations"
        },
        
        # Financial Information
        r".*income.*employment": {
            "variable": "financial.employment_income",
            "type": "currency",
            "validation": "min:0"
        },
        r".*expense.*monthly": {
            "variable": "financial.monthly_expenses",
            "type": "currency",
            "validation": "min:0"
        },
        r".*asset.*value": {
            "variable": "financial.asset_value",
            "type": "currency",
            "validation": "min:0"
        },
        
        # Children Information
        r"child.*name": {
            "variable": "children[i].name.text",
            "type": "text",
            "object": "Individual"
        },
        r"child.*birth.*date": {
            "variable": "children[i].birthdate",
            "type": "date",
            "validation": "date_in_past"
        },
        r"child.*residing": {
            "variable": "children[i].residence",
            "type": "radio",
            "choices": ["applicant", "respondent", "both", "other"]
        },
        
        # Dates
        r".*marriage.*date": {
            "variable": "marriage_date",
            "type": "date",
            "validation": "date_in_past"
        },
        r".*separation.*date": {
            "variable": "separation_date",
            "type": "date",
            "validation": "date_in_past"
        },
        
        # Checkboxes for claims
        r"\[\s*\].*divorce": {
            "variable": "claims.divorce",
            "type": "checkbox",
            "default": False
        },
        r"\[\s*\].*custody": {
            "variable": "claims.custody",
            "type": "checkbox",
            "default": False
        },
        r"\[\s*\].*support": {
            "variable": "claims.support",
            "type": "checkbox",
            "default": False
        },
        r"\[\s*\].*property": {
            "variable": "claims.property",
            "type": "checkbox",
            "default": False
        }
    }
    
    @classmethod
    def map_field(cls, field_text: str, context: str = "") -> Dict[str, Any]:
        """Map a field to docassemble variable and type"""
        field_lower = field_text.lower()
        
        for pattern, mapping in cls.FIELD_MAPPINGS.items():
            if re.search(pattern, field_lower):
                return mapping.copy()
        
        # Default mapping
        return {
            "variable": cls._generate_variable_name(field_text),
            "type": "text"
        }
    
    @classmethod
    def _generate_variable_name(cls, field_text: str) -> str:
        """Generate a valid variable name from field text"""
        # Remove special characters and normalize
        var_name = re.sub(r'[^\w\s]', '', field_text)
        var_name = re.sub(r'\s+', '_', var_name)
        var_name = var_name.lower()[:50]
        return var_name if var_name else "field"

class AutomatedYAMLGenerator:
    """Generate production-ready docassemble YAML with no manual intervention"""
    
    def __init__(self, form_config: FormConfiguration):
        self.config = form_config
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def generate_complete_interview(self, fields: List[Dict]) -> str:
        """Generate complete, production-ready interview"""
        yaml_content = []
        
        # Metadata
        yaml_content.append(self._generate_metadata())
        
        # Includes
        yaml_content.append(self._generate_includes())
        
        # Features
        yaml_content.append(self._generate_features())
        
        # Objects
        yaml_content.append(self._generate_objects())
        
        # Code blocks for initialization
        yaml_content.append(self._generate_initialization())
        
        # Question blocks
        yaml_content.extend(self._generate_all_questions(fields))
        
        # Review screen
        yaml_content.append(self._generate_review_screen(fields))
        
        # Validation code
        yaml_content.append(self._generate_validation())
        
        # Attachment
        yaml_content.append(self._generate_attachment())
        
        # Event handlers
        yaml_content.append(self._generate_event_handlers())
        
        return "\n".join(yaml_content)
    
    def _generate_metadata(self) -> str:
        """Generate metadata block"""
        return f"""---
metadata:
  title: |
    {self.config.form_title}
  short title: |
    Form {self.config.form_number}
  description: |
    Ontario Family Law Form {self.config.form_number}: {self.config.form_title}
    
    This is an automated interview for completing the official Ontario court form.
    Generated automatically on {self.timestamp}
  authors:
    - name: Ontario Family Law Forms Automation System
      organization: Automated Form Processing
  revision_date: {datetime.now().strftime('%Y-%m-%d')}
  form_number: {self.config.form_number}
  form_category: {self.config.category}
  form_type: {self.config.form_type}
---"""
    
    def _generate_includes(self) -> str:
        """Generate includes block"""
        includes = ["docassemble.base:data/questions/basic-questions.yml"]
        
        # Add common Ontario forms include
        includes.append("ontario-family-law-common.yml")
        
        # Add financial statement if required
        if self.config.requires_financial:
            includes.append("ontario-financial-common.yml")
        
        # Add children module if needed
        if self.config.has_children_section:
            includes.append("ontario-children-common.yml")
        
        return f"""include:
{chr(10).join(f'  - {inc}' for inc in includes)}
---"""
    
    def _generate_features(self) -> str:
        """Generate features block"""
        return """features:
  navigation: True
  progress bar: True
  progress bar method: stepped
  show progress bar percentage: True
  navigation back button: True
  question back button: True
  review button: True
  hide navbar: False
  hide standard menu: False
  bootstrap theme: 
    - name: cosmo
    - version: 5
  css:
    - ontario-forms.css
  javascript:
    - ontario-forms.js
---"""
    
    def _generate_objects(self) -> str:
        """Generate objects block"""
        objects = []
        
        # Always include these
        objects.extend([
            "applicant: Individual",
            "respondent: Individual",
            "court_info: DAObject"
        ])
        
        # Add based on form configuration
        if self.config.has_children_section:
            objects.append("children: DAList.using(object_type=Individual, there_are_any=True)")
        
        if self.config.requires_financial:
            objects.append("financial: DAObject")
            objects.append("assets: DAList.using(object_type=Asset, there_are_any=True)")
            objects.append("debts: DAList.using(object_type=Debt, there_are_any=True)")
        
        if self.config.has_property_section:
            objects.append("properties: DAList.using(object_type=Property, there_are_any=True)")
        
        if self.config.form_type in ["motion", "application"]:
            objects.append("claims: DAObject")
        
        return f"""objects:
{chr(10).join(f'  - {obj}' for obj in objects)}
---"""
    
    def _generate_initialization(self) -> str:
        """Generate initialization code"""
        return f"""code: |
  form_number = "{self.config.form_number}"
  form_title = "{self.config.form_title}"
  form_category = "{self.config.category}"
  
  # Initialize tracking variables
  form_started = True
  form_complete = False
  validation_errors = []
  
  # Set defaults
  currency_symbol = "$"
  date_format = "DD/MM/YYYY"
  
  # Ontario-specific settings
  province = "Ontario"
  country = "Canada"
---"""
    
    def _generate_all_questions(self, fields: List[Dict]) -> List[str]:
        """Generate all question blocks"""
        questions = []
        
        # Group fields by logical sections
        sections = self._group_fields_by_section(fields)
        
        # Generate navigation
        questions.append(self._generate_navigation_screen(sections))
        
        # Generate questions for each section
        for section_name, section_fields in sections.items():
            questions.append(self._generate_section_questions(section_name, section_fields))
        
        return questions
    
    def _group_fields_by_section(self, fields: List[Dict]) -> Dict[str, List[Dict]]:
        """Group fields into logical sections"""
        sections = {
            "Court Information": [],
            "Party Information": [],
            "Children Information": [],
            "Financial Information": [],
            "Property Information": [],
            "Claims and Relief": [],
            "Additional Information": []
        }
        
        for field in fields:
            field_name = field.get('field_name', '').lower()
            
            if 'court' in field_name or 'file' in field_name:
                sections["Court Information"].append(field)
            elif any(word in field_name for word in ['applicant', 'respondent', 'party', 'name', 'address']):
                sections["Party Information"].append(field)
            elif 'child' in field_name:
                sections["Children Information"].append(field)
            elif any(word in field_name for word in ['income', 'expense', 'asset', 'debt', 'financial']):
                sections["Financial Information"].append(field)
            elif 'property' in field_name:
                sections["Property Information"].append(field)
            elif any(word in field_name for word in ['claim', 'relief', 'order', 'request']):
                sections["Claims and Relief"].append(field)
            else:
                sections["Additional Information"].append(field)
        
        # Remove empty sections
        return {k: v for k, v in sections.items() if v}
    
    def _generate_navigation_screen(self, sections: Dict) -> str:
        """Generate navigation screen"""
        section_list = "\n".join(f"  * **{name}** ({len(fields)} fields)" for name, fields in sections.items())
        
        return f"""question: |
  Form {self.config.form_number} - {self.config.form_title}
subquestion: |
  This interview will help you complete Form {self.config.form_number}.
  
  The following sections need to be completed:
  
{section_list}
  
  Click **Continue** to begin.
field: intro_screen_shown
section: Introduction
---"""
    
    def _generate_section_questions(self, section_name: str, fields: List[Dict]) -> str:
        """Generate questions for a section"""
        questions = f"""question: |
  {section_name}
subquestion: |
  Please provide the following information for {section_name.lower()}.
fields:"""
        
        for field in fields:
            field_mapping = FieldMapping.map_field(field.get('field_label', ''))
            
            field_line = f"\n  - {field['field_label']}: {field_mapping['variable']}"
            
            # Add field attributes
            if field_mapping.get('type') != 'text':
                field_line += f"\n    datatype: {field_mapping['type']}"
            
            if field.get('required') == 'True':
                field_line += "\n    required: True"
            
            if field_mapping.get('validation'):
                field_line += f"\n    validation: {field_mapping['validation']}"
            
            if field_mapping.get('choices'):
                field_line += f"\n    choices: {field_mapping['choices']}"
            
            if field.get('help_text'):
                field_line += f"\n    help: |\n      {field['help_text']}"
            
            questions += field_line
        
        questions += f"\nsection: {section_name}\n---"
        return questions
    
    def _generate_review_screen(self, fields: List[Dict]) -> str:
        """Generate review screen"""
        sections = self._group_fields_by_section(fields)
        
        review = """event: review_screen
question: |
  Review Your Information
subquestion: |
  Please review the information you have provided. Click on any section to make changes.
review:"""
        
        for section_name, section_fields in sections.items():
            review += f"\n  - note: |"
            review += f"\n      ### {section_name}"
            
            for field in section_fields:
                field_mapping = FieldMapping.map_field(field.get('field_label', ''))
                review += f"\n  - {field['field_label']}: {field_mapping['variable']}"
        
        review += "\n---"
        return review
    
    def _generate_validation(self) -> str:
        """Generate validation code"""
        return f"""code: |
  def validate_form_{self.config.form_number}():
    '''Validate form {self.config.form_number} fields'''
    errors = []
    
    # Check required fields
    if not defined('applicant.name.text') or not applicant.name.text:
      errors.append("Applicant name is required")
    
    if not defined('respondent.name.text') or not respondent.name.text:
      errors.append("Respondent name is required")
    
    if not defined('court_info.file_number') or not court_info.file_number:
      errors.append("Court file number is required")
    
    # Date validations
    if defined('separation_date') and defined('marriage_date'):
      if separation_date < marriage_date:
        errors.append("Separation date must be after marriage date")
    
    # Financial validations
    if '{self.config.requires_financial}' == 'True':
      if defined('financial.employment_income') and financial.employment_income < 0:
        errors.append("Income cannot be negative")
    
    return errors
  
  # Run validation
  validation_errors = validate_form_{self.config.form_number}()
---"""
    
    def _generate_attachment(self) -> str:
        """Generate attachment block"""
        return f"""mandatory: True
code: |
  form_complete = True
---
mandatory: True
question: |
  Form {self.config.form_number} is Complete
subquestion: |
  Your Form {self.config.form_number} ({self.config.form_title}) has been completed.
  
  % if len(validation_errors) > 0:
  <div class="alert alert-warning">
  <strong>Please note the following issues:</strong>
  <ul>
  % for error in validation_errors:
  <li>${{{{ error }}}}</li>
  % endfor
  </ul>
  </div>
  % endif
  
  You can now download your completed form below.
  
  **Next Steps:**
  
  1. Download and review your completed form
  2. Print the form
  3. Sign where indicated
  4. File with the court
  
  % if len({repr(self.config.dependencies)}) > 0:
  **You may also need to complete:**
  % for dep in {repr(self.config.dependencies)}:
  * Form ${{{{ dep }}}}
  % endfor
  % endif
  
attachment:
  name: Form {self.config.form_number}
  filename: form_{self.config.form_number}_{self.config.form_type}
  pdf template file: |
    % if defined('template_file'):
    ${{{{ template_file }}}}
    % else:
    form_{self.config.form_number.lower()}.pdf
    % endif
  editable: False
  fields: 
    # Fields will be mapped automatically from the interview variables
    # This is handled by the docassemble field mapping system
buttons:
  - Exit: exit
  - Start Over: restart
---"""
    
    def _generate_event_handlers(self) -> str:
        """Generate event handlers"""
        return """event: save_and_resume
code: |
  # Save current progress
  command('save_case')
  log(f"Form {form_number} saved at {current_datetime()}", "info")
---
event: form_error
question: |
  An Error Occurred
subquestion: |
  We encountered an error while processing your form.
  
  Error details: ${ error_message if defined('error_message') else 'Unknown error' }
  
  Please try again or contact support if the problem persists.
buttons:
  - Try Again: restart
  - Exit: exit
---"""

class AutomatedFormProcessor:
    """Main processor for automated form handling"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir or "automated_forms_output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.downloads_dir = self.output_dir / "downloads"
        self.csv_dir = self.output_dir / "csv"
        self.yaml_dir = self.output_dir / "yaml"
        self.templates_dir = self.output_dir / "templates"
        self.logs_dir = self.output_dir / "logs"
        
        for dir in [self.downloads_dir, self.csv_dir, self.yaml_dir, self.templates_dir, self.logs_dir]:
            dir.mkdir(exist_ok=True)
        
        # Track processing status
        self.status_file = self.output_dir / "processing_status.json"
        self.load_status()
    
    def load_status(self):
        """Load processing status from file"""
        if self.status_file.exists():
            with open(self.status_file, 'r') as f:
                self.status = json.load(f)
        else:
            self.status = {
                "processed_forms": {},
                "failed_forms": {},
                "last_run": None,
                "statistics": {}
            }
    
    def save_status(self):
        """Save processing status to file"""
        self.status["last_run"] = datetime.now().isoformat()
        with open(self.status_file, 'w') as f:
            json.dump(self.status, f, indent=2)
    
    def process_all_forms(self, force_reprocess: bool = False):
        """Process all 46 Ontario family law forms"""
        logger.info(f"Starting automated form processing at {datetime.now()}")
        
        forms = FormRegistry.get_all_forms()
        total_forms = len(forms)
        processed = 0
        failed = 0
        
        for form_config in forms:
            form_number = form_config.form_number
            
            # Check if already processed
            if not force_reprocess and form_number in self.status["processed_forms"]:
                logger.info(f"Form {form_number} already processed, skipping...")
                continue
            
            try:
                logger.info(f"Processing Form {form_number}: {form_config.form_title}")
                
                # Step 1: Download form
                form_path = self.download_form(form_config)
                
                # Step 2: Extract fields
                fields = self.extract_fields(form_path, form_config)
                
                # Step 3: Save to CSV
                csv_path = self.save_to_csv(form_config, fields)
                
                # Step 4: Generate YAML
                yaml_path = self.generate_yaml(form_config, fields)
                
                # Step 5: Validate YAML
                validation_result = self.validate_yaml(yaml_path)
                
                # Update status
                self.status["processed_forms"][form_number] = {
                    "processed_at": datetime.now().isoformat(),
                    "form_title": form_config.form_title,
                    "fields_count": len(fields),
                    "csv_path": str(csv_path),
                    "yaml_path": str(yaml_path),
                    "validation": validation_result
                }
                
                processed += 1
                logger.info(f"✓ Successfully processed Form {form_number}")
                
            except Exception as e:
                logger.error(f"✗ Failed to process Form {form_number}: {str(e)}")
                self.status["failed_forms"][form_number] = {
                    "failed_at": datetime.now().isoformat(),
                    "error": str(e)
                }
                failed += 1
            
            # Save status after each form
            self.save_status()
        
        # Generate summary report
        self.generate_summary_report(processed, failed, total_forms)
        
        logger.info(f"Processing complete: {processed} successful, {failed} failed out of {total_forms} total")
    
    def download_form(self, form_config: FormConfiguration) -> Path:
        """Download or locate form file"""
        # First try exact filename
        form_path = self.downloads_dir / form_config.filename
        
        if form_path.exists():
            logger.info(f"Form already downloaded: {form_path}")
            return form_path
        
        # Try to find the form with pattern matching
        # Look for files that contain the form number
        form_num_clean = form_config.form_number.replace(".", "_").lower()
        possible_patterns = [
            f"*form_{form_num_clean}_*",
            f"*form_{form_config.form_number.lower()}_*",
            f"*{form_num_clean}*",
        ]
        
        for pattern in possible_patterns:
            matching_files = list(self.downloads_dir.glob(pattern))
            if matching_files:
                form_path = matching_files[0]  # Take the first match
                logger.info(f"Found form file: {form_path}")
                return form_path
        
        # If still not found, log error
        logger.error(f"Could not find form file for Form {form_config.form_number} in {self.downloads_dir}")
        logger.info(f"Expected filename: {form_config.filename}")
        logger.info(f"Available files: {[f.name for f in self.downloads_dir.glob('*')][:5]}...")
        
        return form_path
    
    def extract_fields(self, form_path: Path, form_config: FormConfiguration) -> List[Dict]:
        """Extract fields from form"""
        logger.info(f"Extracting and classifying content from {form_path}")
        
        # Import the enhanced parser with content classification
        from table_aware_parser import TableAwareParser
        
        # Parse and extract fields from tables
        parser = TableAwareParser()
        parsed_content = parser.parse_form(str(form_path))
        
        # Get just the fields for CSV (backward compatibility)
        fields = []
        for field_data in parsed_content.get('fields', []):
            # Handle new format from table_aware_parser
            if 'label' in field_data:
                # New format
                fields.append({
                    'field_id': field_data.get('field_id', ''),
                    'field_name': field_data.get('label', ''),
                    'field_type': field_data.get('field_type', 'text'),
                    'field_label': field_data.get('label', ''),
                    'required': field_data.get('required', False),
                    'validation_rules': "",
                    'max_length': 100,
                    'page_number': field_data.get('page_number', 0),
                    'help_text': ''
                })
            else:
                # Old format with metadata
                metadata = field_data.get('metadata', {})
                fields.append({
                    'field_id': field_data.get('content_id', ''),
                    'field_name': metadata.get('label', ''),
                    'field_type': metadata.get('field_type', 'text'),
                    'field_label': field_data.get('cleaned_text', ''),
                    'required': metadata.get('required', False),
                    'validation_rules': "",
                    'max_length': 100,
                    'page_number': field_data.get('page_number', 0),
                    'help_text': ''
                })
        
        logger.info(f"Extracted {len(fields)} fields, {parsed_content.get('instructions_count', 0)} instructions")
        
        # Store the full parsed content for YAML generation
        self.last_parsed_content = parsed_content
        
        # Return the fields list directly (already in dict format)
        return fields
    
    def save_to_csv(self, form_config: FormConfiguration, fields: List[Dict]) -> Path:
        """Save fields to CSV"""
        csv_path = self.csv_dir / f"form_{form_config.form_number}_fields.csv"
        
        if fields:
            fieldnames = fields[0].keys()
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(fields)
        
        logger.info(f"Saved {len(fields)} fields to {csv_path}")
        return csv_path
    
    def generate_yaml(self, form_config: FormConfiguration, fields: List[Dict]) -> Path:
        """Generate YAML interview"""
        # Use comprehensive YAML generator with full parsed content
        from comprehensive_yaml_generator import generate_comprehensive_yaml
        
        # Use the stored parsed content if available, otherwise create minimal content
        if hasattr(self, 'last_parsed_content'):
            yaml_content = generate_comprehensive_yaml(form_config, self.last_parsed_content)
        else:
            # Fallback to clean generator if no parsed content
            from clean_yaml_generator import generate_clean_yaml
            yaml_content = generate_clean_yaml(form_config, fields)
        
        yaml_path = self.yaml_dir / f"form_{form_config.form_number}_interview.yml"
        with open(yaml_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        logger.info(f"Generated YAML interview: {yaml_path}")
        return yaml_path
    
    def validate_yaml(self, yaml_path: Path) -> Dict:
        """Validate generated YAML"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            import yaml
            with open(yaml_path, 'r') as f:
                yaml.safe_load(f.read())
            validation_result["valid"] = True
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(str(e))
        
        return validation_result
    
    def generate_summary_report(self, processed: int, failed: int, total: int):
        """Generate comprehensive summary report"""
        report = {
            "summary": {
                "total_forms": total,
                "processed": processed,
                "failed": failed,
                "success_rate": f"{(processed/total)*100:.1f}%" if total > 0 else "0%",
                "timestamp": datetime.now().isoformat()
            },
            "processed_forms": self.status["processed_forms"],
            "failed_forms": self.status["failed_forms"],
            "statistics": {
                "total_fields": sum(
                    form.get("fields_count", 0) 
                    for form in self.status["processed_forms"].values()
                ),
                "average_fields_per_form": sum(
                    form.get("fields_count", 0) 
                    for form in self.status["processed_forms"].values()
                ) / processed if processed > 0 else 0
            }
        }
        
        report_path = self.output_dir / "processing_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Also generate human-readable report
        readable_report = self.output_dir / "processing_report.txt"
        with open(readable_report, 'w') as f:
            f.write("Ontario Family Law Forms - Automated Processing Report\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Summary:\n")
            f.write(f"  Total Forms: {total}\n")
            f.write(f"  Successfully Processed: {processed}\n")
            f.write(f"  Failed: {failed}\n")
            f.write(f"  Success Rate: {(processed/total)*100:.1f}%\n\n")
            
            if self.status["processed_forms"]:
                f.write("Successfully Processed Forms:\n")
                for form_num, details in self.status["processed_forms"].items():
                    f.write(f"  ✓ Form {form_num}: {details['form_title']}\n")
                    f.write(f"    - Fields: {details['fields_count']}\n")
                    f.write(f"    - Valid: {details['validation']['valid']}\n")
            
            if self.status["failed_forms"]:
                f.write("\nFailed Forms:\n")
                for form_num, details in self.status["failed_forms"].items():
                    f.write(f"  ✗ Form {form_num}: {details['error']}\n")
        
        logger.info(f"Reports generated: {report_path} and {readable_report}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Automated Ontario Family Law Forms Processor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all forms
  python automated_form_processor.py
  
  # Force reprocess all forms
  python automated_form_processor.py --force
  
  # Use custom output directory
  python automated_form_processor.py --output /path/to/output
  
  # Process specific form
  python automated_form_processor.py --form 8A
        """
    )
    
    parser.add_argument('--force', action='store_true', 
                       help='Force reprocess all forms')
    parser.add_argument('--output', type=str, 
                       help='Output directory')
    parser.add_argument('--form', type=str, 
                       help='Process specific form number')
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = AutomatedFormProcessor(args.output)
    
    # Process forms
    if args.form:
        # Process single form
        form_config = FormRegistry.get_form(args.form)
        if form_config:
            processor.process_all_forms(force_reprocess=args.force)
        else:
            logger.error(f"Form {args.form} not found in registry")
    else:
        # Process all forms
        processor.process_all_forms(force_reprocess=args.force)

if __name__ == "__main__":
    main()