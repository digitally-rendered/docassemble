#!/usr/bin/env python3
"""
Master Workflow Orchestrator for Ontario Family Law Forms
Fully automated, scalable, and repeatable processing pipeline
"""

import os
import sys
import json
import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import asdict
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('master_workflow.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MasterWorkflow:
    """
    Master workflow orchestrator that manages the entire form processing pipeline
    """
    
    def __init__(self, config_file: str = None):
        """Initialize the master workflow"""
        self.config_file = config_file or "workflow_config.json"
        self.load_configuration()
        self.setup_directories()
        self.workflow_status = {
            "started_at": None,
            "completed_at": None,
            "current_step": None,
            "steps_completed": [],
            "errors": [],
            "warnings": []
        }
    
    def load_configuration(self):
        """Load workflow configuration"""
        if Path(self.config_file).exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            # Default configuration
            self.config = {
                "workflow_name": "Ontario Family Law Forms Processing",
                "version": "2.0.0",
                "base_dir": "/Users/draw/development/docassemble/docassemble_webapp/docassemble/webapp/data/questions/ontario-family-law/utilities",
                "output_dir": "workflow_output",
                "steps": {
                    "download": {
                        "enabled": True,
                        "script": "download_all_forms.py",
                        "output": "ontario_forms"
                    },
                    "parse": {
                        "enabled": True,
                        "script": "comprehensive_form_parser.py",
                        "use_enhanced": True,
                        "output": "parsed_data"
                    },
                    "map_objects": {
                        "enabled": True,
                        "script": "enhanced_automated_processor.py",
                        "output": "mapped_objects"
                    },
                    "generate_yaml": {
                        "enabled": True,
                        "output": "yaml_interviews"
                    },
                    "validate": {
                        "enabled": True,
                        "script": "validate_interviews.py",
                        "output": "validation_reports"
                    },
                    "test": {
                        "enabled": False,
                        "script": "test_interviews.py",
                        "output": "test_results"
                    },
                    "deploy": {
                        "enabled": False,
                        "target": "../",
                        "backup": True
                    }
                },
                "forms": {
                    "process_all": True,
                    "specific_forms": [],
                    "exclude_forms": []
                },
                "options": {
                    "force_reprocess": False,
                    "parallel_processing": False,
                    "max_workers": 4,
                    "generate_documentation": True,
                    "create_backups": True,
                    "use_docassemble_objects": True,
                    "ontario_specific": True
                }
            }
            # Save default configuration
            self.save_configuration()
    
    def save_configuration(self):
        """Save current configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        logger.info(f"Configuration saved to {self.config_file}")
    
    def setup_directories(self):
        """Setup required directories"""
        self.base_dir = Path(self.config["base_dir"])
        self.output_dir = self.base_dir / self.config["output_dir"]
        
        # Create main output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create step-specific directories
        for step, step_config in self.config["steps"].items():
            if step_config.get("enabled") and step_config.get("output"):
                step_dir = self.output_dir / step_config["output"]
                step_dir.mkdir(parents=True, exist_ok=True)
        
        # Create additional directories
        (self.output_dir / "logs").mkdir(exist_ok=True)
        (self.output_dir / "reports").mkdir(exist_ok=True)
        (self.output_dir / "backups").mkdir(exist_ok=True)
    
    def run_workflow(self):
        """Run the complete workflow"""
        self.workflow_status["started_at"] = datetime.now().isoformat()
        logger.info("=" * 60)
        logger.info(f"Starting {self.config['workflow_name']} v{self.config['version']}")
        logger.info("=" * 60)
        
        try:
            # Step 1: Download Forms
            if self.config["steps"]["download"]["enabled"]:
                self.run_step("download", self.download_forms)
            
            # Step 2: Parse Forms
            if self.config["steps"]["parse"]["enabled"]:
                self.run_step("parse", self.parse_forms)
            
            # Step 3: Map to Docassemble Objects
            if self.config["steps"]["map_objects"]["enabled"]:
                self.run_step("map_objects", self.map_to_objects)
            
            # Step 4: Generate YAML Interviews
            if self.config["steps"]["generate_yaml"]["enabled"]:
                self.run_step("generate_yaml", self.generate_yaml_interviews)
            
            # Step 5: Validate Generated Files
            if self.config["steps"]["validate"]["enabled"]:
                self.run_step("validate", self.validate_interviews)
            
            # Step 6: Run Tests (if enabled)
            if self.config["steps"]["test"]["enabled"]:
                self.run_step("test", self.run_tests)
            
            # Step 7: Deploy (if enabled)
            if self.config["steps"]["deploy"]["enabled"]:
                self.run_step("deploy", self.deploy_interviews)
            
            # Generate final report
            self.generate_final_report()
            
        except Exception as e:
            logger.error(f"Workflow failed: {str(e)}")
            self.workflow_status["errors"].append(str(e))
        finally:
            self.workflow_status["completed_at"] = datetime.now().isoformat()
            self.save_workflow_status()
    
    def run_step(self, step_name: str, step_function):
        """Run a workflow step with error handling"""
        logger.info(f"\n{'='*40}")
        logger.info(f"Step: {step_name.upper()}")
        logger.info(f"{'='*40}")
        
        self.workflow_status["current_step"] = step_name
        
        try:
            result = step_function()
            self.workflow_status["steps_completed"].append({
                "step": step_name,
                "completed_at": datetime.now().isoformat(),
                "status": "success",
                "result": result
            })
            logger.info(f"✓ {step_name} completed successfully")
            return result
        except Exception as e:
            error_msg = f"Step {step_name} failed: {str(e)}"
            logger.error(error_msg)
            self.workflow_status["errors"].append(error_msg)
            self.workflow_status["steps_completed"].append({
                "step": step_name,
                "completed_at": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e)
            })
            raise
    
    def download_forms(self) -> Dict:
        """Download all Ontario family law forms"""
        logger.info("Downloading Ontario family law forms...")
        
        output_dir = self.output_dir / self.config["steps"]["download"]["output"]
        
        # Import and run download script
        from download_all_forms import download_all_ontario_forms
        
        result = download_all_ontario_forms(str(output_dir))
        
        # Count downloaded forms
        pdf_files = list(output_dir.glob("*.pdf"))
        docx_files = list(output_dir.glob("*.docx"))
        
        return {
            "pdf_count": len(pdf_files),
            "docx_count": len(docx_files),
            "total_forms": len(pdf_files) + len(docx_files),
            "output_dir": str(output_dir)
        }
    
    def parse_forms(self) -> Dict:
        """Parse forms and extract fields"""
        logger.info("Parsing forms to extract fields...")
        
        forms_dir = self.output_dir / self.config["steps"]["download"]["output"]
        parse_output_dir = self.output_dir / self.config["steps"]["parse"]["output"]
        
        if self.config["steps"]["parse"].get("use_enhanced"):
            # Use enhanced parser with object mapping
            from automated_form_processor import AutomatedFormProcessor
            processor = AutomatedFormProcessor(str(parse_output_dir))
            
            # Copy downloaded forms to the processor's downloads directory
            import shutil
            for form_file in forms_dir.glob("*"):
                if form_file.suffix in ['.pdf', '.docx']:
                    dest_path = processor.downloads_dir / form_file.name
                    shutil.copy2(form_file, dest_path)
                    logger.info(f"Copied {form_file.name} to {dest_path}")
            
            processor.process_all_forms(force_reprocess=self.config["options"]["force_reprocess"])
            
            return {
                "processed_forms": len(processor.status["processed_forms"]),
                "failed_forms": len(processor.status["failed_forms"]),
                "output_dir": str(parse_output_dir)
            }
        else:
            # Use basic parser
            from comprehensive_form_parser import process_all_forms
            process_all_forms(str(forms_dir), str(parse_output_dir))
            
            csv_files = list((parse_output_dir / "csv_files").glob("*.csv"))
            return {
                "csv_files": len(csv_files),
                "output_dir": str(parse_output_dir)
            }
    
    def map_to_objects(self) -> Dict:
        """Map fields to docassemble objects"""
        logger.info("Mapping fields to docassemble objects...")
        
        if not self.config["options"]["use_docassemble_objects"]:
            logger.info("Object mapping disabled, skipping...")
            return {"status": "skipped"}
        
        parse_output_dir = self.output_dir / self.config["steps"]["parse"]["output"]
        map_output_dir = self.output_dir / self.config["steps"]["map_objects"]["output"]
        
        from enhanced_automated_processor import IntelligentFieldMapper
        
        mapper = IntelligentFieldMapper()
        mapped_count = 0
        
        # Process each CSV file
        csv_dir = parse_output_dir / "csv_files"
        if csv_dir.exists():
            for csv_file in csv_dir.glob("*_fields.csv"):
                import csv
                with open(csv_file, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        mapping = mapper.map_field_to_object(
                            row.get('field_label', ''),
                            row.get('field_context', '')
                        )
                        mapped_count += 1
        
        # Save object mappings
        mappings_file = map_output_dir / "object_mappings.json"
        with open(mappings_file, 'w') as f:
            json.dump({
                "mapped_objects": {k: asdict(v) if hasattr(v, '__dict__') else str(v) 
                          for k, v in mapper.mapped_objects.items()},
                "total_fields_mapped": mapped_count
            }, f, indent=2, default=str)
        
        return {
            "objects_identified": len(mapper.mapped_objects),
            "fields_mapped": mapped_count,
            "mappings_file": str(mappings_file)
        }
    
    def generate_yaml_interviews(self) -> Dict:
        """Generate YAML interview files"""
        logger.info("Generating YAML interview files...")
        
        yaml_output_dir = self.output_dir / self.config["steps"]["generate_yaml"]["output"]
        
        if self.config["options"]["use_docassemble_objects"]:
            # Use enhanced generator with object mapping
            from enhanced_automated_processor import EnhancedYAMLGenerator, IntelligentFieldMapper
            from automated_form_processor import FormRegistry
            
            generated_count = 0
            for form_config in FormRegistry.get_all_forms():
                try:
                    mapper = IntelligentFieldMapper()
                    generator = EnhancedYAMLGenerator(form_config, mapper)
                    
                    # Get fields from CSV
                    csv_file = self.output_dir / "parsed_data" / "csv" / f"form_{form_config.form_number}_fields.csv"
                    if csv_file.exists():
                        fields = []
                        import csv
                        with open(csv_file, 'r') as f:
                            reader = csv.DictReader(f)
                            fields = list(reader)
                        
                        yaml_content = generator.generate_complete_interview(fields)
                        
                        yaml_file = yaml_output_dir / f"form_{form_config.form_number}_interview.yml"
                        with open(yaml_file, 'w') as f:
                            f.write(yaml_content)
                        
                        generated_count += 1
                        logger.info(f"Generated: {yaml_file.name}")
                except Exception as e:
                    logger.error(f"Failed to generate YAML for form {form_config.form_number}: {e}")
        else:
            # Use basic generator
            from comprehensive_form_parser import YAMLGenerator
            csv_dir = self.output_dir / "parsed_data" / "csv_files"
            
            generated_count = 0
            for csv_file in csv_dir.glob("*_fields.csv"):
                generator = YAMLGenerator(str(csv_file), str(yaml_output_dir))
                form_number = csv_file.stem.replace("_fields", "")
                generator.generate_yaml(form_number, f"Form {form_number}")
                generated_count += 1
        
        return {
            "yaml_files_generated": generated_count,
            "output_dir": str(yaml_output_dir)
        }
    
    def validate_interviews(self) -> Dict:
        """Validate generated interview files"""
        logger.info("Validating generated interviews...")
        
        yaml_dir = self.output_dir / self.config["steps"]["generate_yaml"]["output"]
        validation_output_dir = self.output_dir / self.config["steps"]["validate"]["output"]
        
        import yaml
        
        validation_results = []
        for yaml_file in yaml_dir.glob("*.yml"):
            try:
                with open(yaml_file, 'r') as f:
                    yaml.safe_load(f.read())
                validation_results.append({
                    "file": yaml_file.name,
                    "valid": True,
                    "errors": []
                })
            except Exception as e:
                validation_results.append({
                    "file": yaml_file.name,
                    "valid": False,
                    "errors": [str(e)]
                })
        
        # Save validation report
        report_file = validation_output_dir / "validation_report.json"
        with open(report_file, 'w') as f:
            json.dump(validation_results, f, indent=2)
        
        valid_count = sum(1 for r in validation_results if r["valid"])
        
        return {
            "total_files": len(validation_results),
            "valid_files": valid_count,
            "invalid_files": len(validation_results) - valid_count,
            "report_file": str(report_file)
        }
    
    def run_tests(self) -> Dict:
        """Run automated tests on generated interviews"""
        logger.info("Running automated tests...")
        
        # Placeholder for test implementation
        return {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0
        }
    
    def deploy_interviews(self) -> Dict:
        """Deploy interviews to docassemble"""
        logger.info("Deploying interviews...")
        
        if not self.config["steps"]["deploy"]["enabled"]:
            return {"status": "skipped"}
        
        yaml_dir = self.output_dir / self.config["steps"]["generate_yaml"]["output"]
        target_dir = Path(self.config["steps"]["deploy"]["target"])
        
        # Create backup if requested
        if self.config["steps"]["deploy"]["backup"]:
            backup_dir = self.output_dir / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup existing files
            for existing_file in target_dir.glob("form_*.yml"):
                shutil.copy2(existing_file, backup_dir)
            logger.info(f"Backed up existing files to {backup_dir}")
        
        # Copy new files
        deployed_count = 0
        for yaml_file in yaml_dir.glob("*.yml"):
            target_file = target_dir / yaml_file.name
            shutil.copy2(yaml_file, target_file)
            deployed_count += 1
            logger.info(f"Deployed: {yaml_file.name}")
        
        return {
            "files_deployed": deployed_count,
            "target_directory": str(target_dir)
        }
    
    def generate_final_report(self):
        """Generate comprehensive final report"""
        logger.info("\nGenerating final report...")
        
        report = {
            "workflow": self.config["workflow_name"],
            "version": self.config["version"],
            "execution": {
                "started_at": self.workflow_status["started_at"],
                "completed_at": self.workflow_status["completed_at"],
                "duration": self._calculate_duration()
            },
            "steps": self.workflow_status["steps_completed"],
            "errors": self.workflow_status["errors"],
            "warnings": self.workflow_status["warnings"],
            "summary": self._generate_summary()
        }
        
        # Save JSON report
        report_file = self.output_dir / "reports" / f"workflow_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save human-readable report
        readable_report = self.output_dir / "reports" / f"workflow_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(readable_report, 'w') as f:
            f.write(f"{self.config['workflow_name']} - Execution Report\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Started: {self.workflow_status['started_at']}\n")
            f.write(f"Completed: {self.workflow_status['completed_at']}\n")
            f.write(f"Duration: {self._calculate_duration()}\n\n")
            
            f.write("Steps Completed:\n")
            for step in self.workflow_status["steps_completed"]:
                status_icon = "✓" if step["status"] == "success" else "✗"
                f.write(f"  {status_icon} {step['step']}: {step['status']}\n")
            
            if self.workflow_status["errors"]:
                f.write("\nErrors:\n")
                for error in self.workflow_status["errors"]:
                    f.write(f"  - {error}\n")
            
            f.write("\nSummary:\n")
            summary = self._generate_summary()
            for key, value in summary.items():
                f.write(f"  {key}: {value}\n")
        
        logger.info(f"Reports saved to {report_file} and {readable_report}")
    
    def _calculate_duration(self) -> str:
        """Calculate workflow duration"""
        if self.workflow_status["started_at"] and self.workflow_status["completed_at"]:
            start = datetime.fromisoformat(self.workflow_status["started_at"])
            end = datetime.fromisoformat(self.workflow_status["completed_at"])
            duration = end - start
            return str(duration)
        return "N/A"
    
    def _generate_summary(self) -> Dict:
        """Generate workflow summary"""
        summary = {
            "total_steps": len(self.workflow_status["steps_completed"]),
            "successful_steps": sum(1 for s in self.workflow_status["steps_completed"] if s["status"] == "success"),
            "failed_steps": sum(1 for s in self.workflow_status["steps_completed"] if s["status"] == "failed"),
            "errors_count": len(self.workflow_status["errors"]),
            "warnings_count": len(self.workflow_status["warnings"])
        }
        
        # Add step-specific summaries
        for step in self.workflow_status["steps_completed"]:
            if step["status"] == "success" and "result" in step:
                result = step["result"]
                if isinstance(result, dict):
                    for key, value in result.items():
                        summary[f"{step['step']}_{key}"] = value
        
        return summary
    
    def save_workflow_status(self):
        """Save workflow status to file"""
        status_file = self.output_dir / "workflow_status.json"
        with open(status_file, 'w') as f:
            json.dump(self.workflow_status, f, indent=2)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Master Workflow for Ontario Family Law Forms Processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This is the master workflow orchestrator for processing all 46 Ontario family law forms.
It manages the complete pipeline from download to deployment with no manual intervention required.

Examples:
  # Run complete workflow
  python master_workflow.py
  
  # Run with custom configuration
  python master_workflow.py --config my_config.json
  
  # Generate default configuration
  python master_workflow.py --generate-config
  
  # Run specific steps only
  python master_workflow.py --steps download parse generate_yaml
  
  # Force reprocess all forms
  python master_workflow.py --force
        """
    )
    
    parser.add_argument('--config', type=str, help='Configuration file')
    parser.add_argument('--generate-config', action='store_true', help='Generate default configuration')
    parser.add_argument('--steps', nargs='+', help='Run specific steps only')
    parser.add_argument('--force', action='store_true', help='Force reprocess all forms')
    parser.add_argument('--parallel', action='store_true', help='Enable parallel processing')
    
    args = parser.parse_args()
    
    # Initialize workflow
    workflow = MasterWorkflow(config_file=args.config)
    
    if args.generate_config:
        workflow.save_configuration()
        print(f"Configuration saved to {workflow.config_file}")
        return
    
    # Apply command line overrides
    if args.force:
        workflow.config["options"]["force_reprocess"] = True
    
    if args.parallel:
        workflow.config["options"]["parallel_processing"] = True
    
    if args.steps:
        # Disable all steps except specified
        for step in workflow.config["steps"]:
            workflow.config["steps"][step]["enabled"] = step in args.steps
    
    # Run workflow
    workflow.run_workflow()
    
    print("\n" + "=" * 60)
    print("Workflow Complete!")
    print("=" * 60)
    print(f"Output directory: {workflow.output_dir}")
    print(f"Check {workflow.output_dir}/reports for detailed reports")

if __name__ == "__main__":
    main()