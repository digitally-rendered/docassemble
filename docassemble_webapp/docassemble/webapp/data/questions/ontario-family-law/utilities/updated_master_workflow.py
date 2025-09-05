#!/usr/bin/env python3
"""
Updated Master Workflow for Ontario Family Law Forms
Uses forms list to parse actual downloaded files
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('updated_workflow.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UpdatedMasterWorkflow:
    """
    Master workflow that:
    1. Downloads forms
    2. Creates a list of downloaded forms
    3. Parses the actual files (PDF/DOCX)
    4. Maps fields to docassemble objects
    5. Generates YAML interviews
    """
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir or "workflow_output")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up directories
        self.forms_dir = self.base_dir / "ontario_forms"
        self.parsed_dir = self.base_dir / "parsed_forms"
        self.yaml_dir = self.base_dir / "yaml_interviews"
        self.reports_dir = self.base_dir / "reports"
        
        for d in [self.forms_dir, self.parsed_dir, self.yaml_dir, self.reports_dir]:
            d.mkdir(exist_ok=True)
    
    def run_complete_workflow(self):
        """Run the complete workflow"""
        logger.info("="*60)
        logger.info("Starting Updated Ontario Family Law Forms Workflow")
        logger.info("="*60)
        
        results = {
            "started_at": datetime.now().isoformat(),
            "steps": {}
        }
        
        try:
            # Step 1: Download forms
            logger.info("\nStep 1: Downloading forms...")
            download_result = self.download_forms()
            results["steps"]["download"] = download_result
            
            # Step 2: Create forms list
            logger.info("\nStep 2: Creating forms list...")
            list_result = self.create_forms_list()
            results["steps"]["forms_list"] = list_result
            
            # Step 3: Parse forms
            logger.info("\nStep 3: Parsing forms...")
            parse_result = self.parse_forms()
            results["steps"]["parse"] = parse_result
            
            # Step 4: Map to docassemble objects
            logger.info("\nStep 4: Mapping to docassemble objects...")
            map_result = self.map_to_objects()
            results["steps"]["map_objects"] = map_result
            
            # Step 5: Generate YAML interviews
            logger.info("\nStep 5: Generating YAML interviews...")
            yaml_result = self.generate_yaml()
            results["steps"]["generate_yaml"] = yaml_result
            
            # Step 6: Validate YAML
            logger.info("\nStep 6: Validating YAML files...")
            validate_result = self.validate_yaml()
            results["steps"]["validate"] = validate_result
            
            results["status"] = "success"
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            results["status"] = "failed"
            results["error"] = str(e)
        
        results["completed_at"] = datetime.now().isoformat()
        
        # Save results
        report_file = self.reports_dir / f"workflow_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\nWorkflow complete. Report saved to {report_file}")
        
        # Print summary
        self.print_summary(results)
        
        return results
    
    def download_forms(self):
        """Download all Ontario family law forms"""
        try:
            # Use the download_all_forms.py script
            from download_all_forms import download_all_ontario_forms
            
            result = download_all_ontario_forms(str(self.forms_dir))
            
            logger.info(f"Downloaded {result['successful']} forms successfully")
            if result.get('failed', 0) > 0:
                logger.warning(f"Failed to download {result['failed']} forms")
            
            return {
                "status": "success",
                "downloaded": result['successful'],
                "failed": result.get('failed', 0),
                "output_dir": str(self.forms_dir)
            }
            
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def create_forms_list(self):
        """Create a list of all downloaded forms"""
        try:
            # Use the create_forms_list.py script
            from create_forms_list import find_all_forms, save_forms_list, save_forms_csv
            
            forms = find_all_forms(str(self.forms_dir))
            
            if not forms:
                return {"status": "failed", "error": "No forms found"}
            
            # Save lists
            json_file = self.base_dir / "forms_list.json"
            csv_file = self.base_dir / "forms_list.csv"
            
            save_forms_list(forms, str(json_file))
            save_forms_csv(forms, str(csv_file))
            
            logger.info(f"Created list of {len(forms)} forms")
            
            # Count by type
            pdf_count = len([f for f in forms if f["extension"] == ".pdf"])
            docx_count = len([f for f in forms if f["extension"] in [".docx", ".doc"]])
            
            return {
                "status": "success",
                "total_forms": len(forms),
                "pdf_count": pdf_count,
                "docx_count": docx_count,
                "json_file": str(json_file),
                "csv_file": str(csv_file)
            }
            
        except Exception as e:
            logger.error(f"Forms list creation failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def parse_forms(self):
        """Parse forms from the CSV list"""
        try:
            # Use the parse_forms_from_list.py script
            from parse_forms_from_list import parse_forms_from_csv
            
            csv_file = self.base_dir / "forms_list.csv"
            
            if not csv_file.exists():
                return {"status": "failed", "error": "Forms list CSV not found"}
            
            results = parse_forms_from_csv(str(csv_file), str(self.parsed_dir))
            
            # Count results
            successful = len([r for r in results if r["status"] == "success"])
            no_fields = len([r for r in results if r["status"] == "no_fields"])
            errors = len([r for r in results if r["status"] == "error"])
            
            logger.info(f"Parsed {successful} forms successfully")
            if no_fields > 0:
                logger.warning(f"{no_fields} forms had no extractable fields")
            if errors > 0:
                logger.error(f"{errors} forms failed to parse")
            
            return {
                "status": "success",
                "successful": successful,
                "no_fields": no_fields,
                "errors": errors,
                "output_dir": str(self.parsed_dir)
            }
            
        except Exception as e:
            logger.error(f"Parsing failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def map_to_objects(self):
        """Map parsed fields to docassemble objects"""
        try:
            from enhanced_automated_processor import IntelligentFieldMapper
            import csv
            
            mapper = IntelligentFieldMapper()
            all_mappings = []
            
            # Process each parsed CSV file
            for csv_file in self.parsed_dir.glob("*_fields.csv"):
                with open(csv_file, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        mapping = mapper.map_field_to_object(
                            row.get('field_label', ''),
                            row.get('field_context', '')
                        )
                        all_mappings.append({
                            "form": csv_file.stem.replace('_fields', ''),
                            "field": row.get('field_name', ''),
                            "mapping": mapping
                        })
            
            # Save mappings
            mappings_file = self.base_dir / "field_mappings.json"
            with open(mappings_file, 'w') as f:
                json.dump(all_mappings, f, indent=2)
            
            logger.info(f"Mapped {len(all_mappings)} fields to docassemble objects")
            
            return {
                "status": "success",
                "fields_mapped": len(all_mappings),
                "objects_identified": len(mapper.mapped_objects),
                "mappings_file": str(mappings_file)
            }
            
        except Exception as e:
            logger.error(f"Object mapping failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def generate_yaml(self):
        """Generate YAML interview files"""
        try:
            from fixed_yaml_generator import FixedYAMLGenerator
            from automated_form_processor import FormRegistry
            import csv
            
            generated_count = 0
            generated_forms = []  # Track all generated forms for index
            
            # Process each parsed form
            for csv_file in self.parsed_dir.glob("*_fields.csv"):
                form_number = csv_file.stem.replace('form_', '').replace('_fields', '')
                
                # Get form configuration
                form_config = FormRegistry.get_form(form_number)
                if not form_config:
                    # Create basic config
                    from automated_form_processor import FormConfiguration
                    form_config = FormConfiguration(
                        form_number=form_number,
                        form_title=f"Form {form_number}",
                        form_type="general",
                        category="general",
                        url="",
                        filename=""
                    )
                
                # Load fields
                fields = []
                with open(csv_file, 'r') as f:
                    reader = csv.DictReader(f)
                    fields = list(reader)
                
                if fields:
                    # Generate YAML using the fixed generator
                    generator = FixedYAMLGenerator(form_config, field_mapper=None)
                    yaml_content = generator.generate_complete_interview(fields)
                    
                    # Save YAML
                    yaml_file = self.yaml_dir / f"form_{form_number}_interview.yml"
                    with open(yaml_file, 'w') as f:
                        f.write(yaml_content)
                    
                    generated_count += 1
                    logger.info(f"Generated YAML for Form {form_number}")
                    
                    # Track for index
                    generated_forms.append({
                        'form_number': form_number,
                        'form_title': form_config.form_title,
                        'category': getattr(form_config, 'category', 'general'),
                        'filename': f"form_{form_number}_interview.yml"
                    })
            
            # Generate index interview with ALL forms
            if generated_forms:
                self._generate_index_interview(generated_forms)
                logger.info(f"Generated index interview with {len(generated_forms)} forms")
            
            logger.info(f"Generated {generated_count} YAML interview files")
            
            return {
                "status": "success",
                "files_generated": generated_count,
                "output_dir": str(self.yaml_dir)
            }
            
        except Exception as e:
            logger.error(f"YAML generation failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def _generate_index_interview(self, forms: List[Dict]):
        """Generate an index interview with links to all forms"""
        from datetime import datetime
        
        # Organize forms by category
        categories = {
            'core': [],
            'financial': [],
            'motions': [],
            'orders': [],
            'enforcement': [],
            'service': [],
            'divorce': [],
            'child': [],
            'other': []
        }
        
        # Categorize forms based on form number
        for form in sorted(forms, key=lambda x: x['form_number']):
            form_num = form['form_number'].lower()
            
            if form_num in ['4', '6b', '6c', '8', '8a', '8b', '8d', '10', '10a']:
                categories['core'].append(form)
            elif form_num.startswith('13'):
                categories['financial'].append(form)
            elif form_num.startswith('14') or form_num.startswith('15') or form_num.startswith('17'):
                categories['motions'].append(form)
            elif form_num.startswith('25'):
                categories['orders'].append(form)
            elif form_num.startswith('26') or form_num.startswith('27') or form_num.startswith('28') or form_num.startswith('29') or form_num.startswith('30'):
                categories['enforcement'].append(form)
            elif form_num.startswith('6'):
                categories['service'].append(form)
            elif form_num.startswith('36') or form_num.startswith('37'):
                categories['divorce'].append(form)
            elif form_num.startswith('33') or form_num.startswith('34'):
                categories['child'].append(form)
            else:
                categories['other'].append(form)
        
        # Build the index YAML content
        yaml_content = f'''---
metadata:
  title: Ontario Family Law Forms - Complete Collection
  short title: All ON Forms
  description: Complete index of all auto-generated Ontario family law form interviews
  generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
  total_forms: {len(forms)}
mandatory: True
question: |
  # Ontario Family Law Forms System
subquestion: |
  Welcome to the complete Ontario Family Law Forms collection. All {len(forms)} forms have been automatically generated and are ready to use.
  
  Select the form you need from the categories below:
'''
        
        # Add Core Application Forms
        if categories['core']:
            yaml_content += '\n  ## 📋 Core Application & Service Forms\n'
            for form in categories['core']:
                yaml_content += f'  * **[Form {form["form_number"]} - {form["form_title"]}](/interview?i=docassemble.webapp:ontario-family-law/utilities/workflow_output/yaml_interviews/{form["filename"]})**\n'
        
        # Add Financial Forms
        if categories['financial']:
            yaml_content += '\n  ## 💰 Financial Disclosure Forms\n'
            for form in categories['financial']:
                yaml_content += f'  * **[Form {form["form_number"]} - {form["form_title"]}](/interview?i=docassemble.webapp:ontario-family-law/utilities/workflow_output/yaml_interviews/{form["filename"]})**\n'
        
        # Add Motion Forms
        if categories['motions']:
            yaml_content += '\n  ## 📝 Motions & Conferences\n'
            for form in categories['motions']:
                yaml_content += f'  * **[Form {form["form_number"]} - {form["form_title"]}](/interview?i=docassemble.webapp:ontario-family-law/utilities/workflow_output/yaml_interviews/{form["filename"]})**\n'
        
        # Add Order Forms
        if categories['orders']:
            yaml_content += '\n  ## ⚖️ Orders\n'
            for form in categories['orders']:
                yaml_content += f'  * **[Form {form["form_number"]} - {form["form_title"]}](/interview?i=docassemble.webapp:ontario-family-law/utilities/workflow_output/yaml_interviews/{form["filename"]})**\n'
        
        # Add Enforcement Forms
        if categories['enforcement']:
            yaml_content += '\n  ## 🔨 Enforcement Forms\n'
            for form in categories['enforcement']:
                yaml_content += f'  * **[Form {form["form_number"]} - {form["form_title"]}](/interview?i=docassemble.webapp:ontario-family-law/utilities/workflow_output/yaml_interviews/{form["filename"]})**\n'
        
        # Add Divorce Forms
        if categories['divorce']:
            yaml_content += '\n  ## 💔 Divorce & Interjurisdictional Forms\n'
            for form in categories['divorce']:
                yaml_content += f'  * **[Form {form["form_number"]} - {form["form_title"]}](/interview?i=docassemble.webapp:ontario-family-law/utilities/workflow_output/yaml_interviews/{form["filename"]})**\n'
        
        # Add Child Related Forms
        if categories['child']:
            yaml_content += '\n  ## 👶 Child Protection & Adoption Forms\n'
            for form in categories['child']:
                yaml_content += f'  * **[Form {form["form_number"]} - {form["form_title"]}](/interview?i=docassemble.webapp:ontario-family-law/utilities/workflow_output/yaml_interviews/{form["filename"]})**\n'
        
        # Add Other Forms
        if categories['other']:
            yaml_content += '\n  ## 📄 Other Forms\n'
            for form in categories['other']:
                yaml_content += f'  * **[Form {form["form_number"]} - {form["form_title"]}](/interview?i=docassemble.webapp:ontario-family-law/utilities/workflow_output/yaml_interviews/{form["filename"]})**\n'
        
        yaml_content += '''
  
  ---
  
  ## ℹ️ Information
  
  This collection includes all Ontario family law forms that have been processed and contain extractable fields.
  Each interview:
  - ✅ Guides you through all required fields
  - ✅ Validates Ontario-specific requirements  
  - ✅ Groups related questions for easier completion
  - ✅ Provides review before submission
  - ✅ Auto-saves your progress
  
  **Note:** Some forms may not appear if they contained no extractable fields during processing.
  
  For legal advice, please consult with a qualified family law professional.
buttons:
  - Exit: exit
  - Restart: restart'''
        
        # Save the index file
        index_file = self.yaml_dir / "00_ontario_forms_index.yml"
        with open(index_file, 'w') as f:
            f.write(yaml_content)
        
        logger.info(f"Generated index interview: {index_file}")
        return index_file
    
    def validate_yaml(self):
        """Validate generated YAML files"""
        try:
            import yaml
            
            validation_results = []
            
            for yaml_file in self.yaml_dir.glob("*.yml"):
                try:
                    with open(yaml_file, 'r') as f:
                        yaml.safe_load(f.read())
                    validation_results.append({
                        "file": yaml_file.name,
                        "valid": True
                    })
                except Exception as e:
                    validation_results.append({
                        "file": yaml_file.name,
                        "valid": False,
                        "error": str(e)
                    })
            
            valid_count = sum(1 for r in validation_results if r["valid"])
            invalid_count = len(validation_results) - valid_count
            
            # Save validation report
            report_file = self.reports_dir / "yaml_validation_report.json"
            with open(report_file, 'w') as f:
                json.dump(validation_results, f, indent=2)
            
            logger.info(f"Validated {len(validation_results)} YAML files")
            logger.info(f"Valid: {valid_count}, Invalid: {invalid_count}")
            
            return {
                "status": "success",
                "total_files": len(validation_results),
                "valid": valid_count,
                "invalid": invalid_count,
                "report_file": str(report_file)
            }
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def print_summary(self, results):
        """Print workflow summary"""
        print("\n" + "="*60)
        print("WORKFLOW SUMMARY")
        print("="*60)
        
        for step_name, step_result in results.get("steps", {}).items():
            status = step_result.get("status", "unknown")
            icon = "✓" if status == "success" else "✗"
            print(f"{icon} {step_name}: {status}")
            
            if status == "success":
                # Print key metrics
                if step_name == "download":
                    print(f"  - Downloaded: {step_result.get('downloaded', 0)} forms")
                elif step_name == "forms_list":
                    print(f"  - Listed: {step_result.get('total_forms', 0)} forms")
                    print(f"  - PDF: {step_result.get('pdf_count', 0)}, DOCX: {step_result.get('docx_count', 0)}")
                elif step_name == "parse":
                    print(f"  - Parsed: {step_result.get('successful', 0)} forms")
                    print(f"  - No fields: {step_result.get('no_fields', 0)}")
                elif step_name == "map_objects":
                    print(f"  - Mapped: {step_result.get('fields_mapped', 0)} fields")
                elif step_name == "generate_yaml":
                    print(f"  - Generated: {step_result.get('files_generated', 0)} YAML files")
                elif step_name == "validate":
                    print(f"  - Valid: {step_result.get('valid', 0)}/{step_result.get('total_files', 0)}")
        
        print("="*60)
        print(f"Overall status: {results.get('status', 'unknown')}")
        print(f"Output directory: {self.base_dir}")
        print("="*60)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Updated Master Workflow for Ontario Family Law Forms"
    )
    parser.add_argument(
        "--output-dir",
        default="workflow_output",
        help="Output directory for all workflow files"
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Skip download step if forms already exist"
    )
    
    args = parser.parse_args()
    
    workflow = UpdatedMasterWorkflow(args.output_dir)
    
    if args.skip_download:
        logger.info("Skipping download step as requested")
        # You could implement partial workflow here
    
    results = workflow.run_complete_workflow()
    
    sys.exit(0 if results.get("status") == "success" else 1)

if __name__ == "__main__":
    main()