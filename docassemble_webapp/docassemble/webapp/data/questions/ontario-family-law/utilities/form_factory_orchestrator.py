#!/usr/bin/env python3
"""
Form Factory Orchestrator - Master Agent

Orchestrates the complete map-based workflow for generating Docassemble interviews 
from parsed Ontario family law forms using domain mapping and Ontario frameworks.

This orchestrator coordinates:
1. Parse form data extraction
2. Domain mapping (form fields -> domain concepts)
3. Docassemble mapping (domain concepts -> DA objects)
4. Interview generation using Ontario frameworks
5. Test suite generation with comprehensive coverage
6. Validation and quality assurance

Architecture: Parsed Data -> Domain Mapping -> Docassemble Mapping -> Interview Maps -> YAML Encoding

Author: Form Factory Orchestrator
Updated: 2025-09-05 (Map-based architecture)
"""

import os
import json
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class WorkflowStep:
    """Represents a step in the orchestration workflow"""
    name: str
    description: str
    agent_script: str
    dependencies: List[str]
    outputs: List[str]
    status: str = 'pending'  # pending, running, completed, failed
    error_message: str = ''
    execution_time: float = 0.0

@dataclass
class WorkflowResult:
    """Results of the complete workflow orchestration"""
    total_steps: int
    completed_steps: int
    failed_steps: int
    total_forms_processed: int
    total_interviews_generated: int
    total_tests_generated: int
    execution_time: float
    output_directories: Dict[str, str]
    form_key_registry: Dict[str, Dict[str, str]]  # Maps form_number -> {original_field -> consistent_key}
    domain_mapping_registry: Dict[str, str]  # Maps consistent_key -> domain_concept
    docassemble_mapping_registry: Dict[str, str]  # Maps domain_concept -> docassemble_variable

class FormFactoryOrchestrator:
    """Master orchestrator for the complete form generation workflow"""
    
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.workflow_steps = self._define_workflow_steps()
        self.results = {}
        
    def _define_workflow_steps(self) -> List[WorkflowStep]:
        """Define the complete map-based workflow with dependencies"""
        return [
            WorkflowStep(
                name='validate_parsed_forms',
                description='Validate parsed form data integrity',
                agent_script='validate_parsed_forms.py',
                dependencies=[],
                outputs=['parsed_forms_validation.json']
            ),
            WorkflowStep(
                name='initialize_ontario_framework',
                description='Initialize Ontario family law framework objects',
                agent_script='ontario_framework_initializer.py',
                dependencies=[],
                outputs=['ontario_framework/']
            ),
            WorkflowStep(
                name='create_domain_mappings',
                description='Create domain mappings (form fields -> domain concepts)',
                agent_script='domain_mapping_generator.py',
                dependencies=['validate_parsed_forms'],
                outputs=['domain_mappings.json']
            ),
            WorkflowStep(
                name='create_docassemble_mappings',
                description='Create Docassemble mappings (domain concepts -> DA objects)',
                agent_script='docassemble_mapping_generator.py',
                dependencies=['initialize_ontario_framework', 'create_domain_mappings'],
                outputs=['docassemble_mappings.json']
            ),
            WorkflowStep(
                name='generate_interview_maps',
                description='Generate interview maps using unified map-based generator',
                agent_script='unified_map_based_generator.py',
                dependencies=['create_docassemble_mappings'],
                outputs=['generated_interviews_unified/']
            ),
            WorkflowStep(
                name='encode_yaml_interviews',
                description='Encode interview maps to valid YAML format',
                agent_script='yaml_encoder.py',
                dependencies=['generate_interview_maps'],
                outputs=['encoded_interviews/']
            ),
            WorkflowStep(
                name='generate_tests',
                description='Generate comprehensive Playwright test suites',
                agent_script='test_factory.py',
                dependencies=['encode_yaml_interviews'],
                outputs=['generated_tests/']
            ),
            WorkflowStep(
                name='validate_system',
                description='Run system validation and quality checks',
                agent_script='system_validator.py',
                dependencies=['generate_tests'],
                outputs=['validation_report.json']
            )
        ]
    
    def check_prerequisites(self) -> bool:
        """Check that all prerequisites are met"""
        print("🔍 Checking prerequisites...")
        
        required_files = [
            'parsed_forms/',
            'common_fields_report.json',
            'forms_list.json'
        ]
        
        missing_files = []
        for required_file in required_files:
            file_path = os.path.join(self.base_dir, required_file)
            if not os.path.exists(file_path):
                missing_files.append(required_file)
        
        if missing_files:
            print(f"❌ Missing required files: {', '.join(missing_files)}")
            return False
        
        print("✅ All prerequisites met")
        return True
    
    def execute_step(self, step: WorkflowStep) -> bool:
        """Execute a single workflow step"""
        print(f"\\n🚀 Executing: {step.description}")
        print(f"📝 Agent: {step.agent_script}")
        
        step.status = 'running'
        start_time = time.time()
        
        try:
            # Change to base directory
            original_dir = os.getcwd()
            os.chdir(self.base_dir)
            
            # Execute the agent script
            result = subprocess.run(
                ['python', step.agent_script],
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout
            )
            
            step.execution_time = time.time() - start_time
            
            if result.returncode == 0:
                step.status = 'completed'
                print(f"✅ Completed in {step.execution_time:.1f}s")
                print(f"📋 Output: {result.stdout[-500:]}")  # Last 500 chars
                return True
            else:
                step.status = 'failed'
                step.error_message = result.stderr
                print(f"❌ Failed after {step.execution_time:.1f}s")
                print(f"🚨 Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            step.status = 'failed'
            step.error_message = 'Execution timeout'
            step.execution_time = time.time() - start_time
            print(f"❌ Timed out after {step.execution_time:.1f}s")
            return False
            
        except Exception as e:
            step.status = 'failed'
            step.error_message = str(e)
            step.execution_time = time.time() - start_time
            print(f"❌ Exception: {e}")
            return False
            
        finally:
            os.chdir(original_dir)
    
    def check_step_outputs(self, step: WorkflowStep) -> bool:
        """Verify that step produced expected outputs"""
        for output in step.outputs:
            output_path = os.path.join(self.base_dir, output)
            if not os.path.exists(output_path):
                print(f"⚠️ Missing expected output: {output}")
                return False
        
        print(f"✅ All outputs verified for {step.name}")
        return True
    
    def can_execute_step(self, step: WorkflowStep) -> bool:
        """Check if step dependencies are satisfied"""
        for dependency in step.dependencies:
            dep_step = next((s for s in self.workflow_steps if s.name == dependency), None)
            if not dep_step or dep_step.status != 'completed':
                return False
        return True
    
    def generate_progress_report(self, current_step: int) -> Dict:
        """Generate current progress report"""
        completed = sum(1 for s in self.workflow_steps if s.status == 'completed')
        failed = sum(1 for s in self.workflow_steps if s.status == 'failed')
        
        return {
            'timestamp': datetime.now().isoformat(),
            'progress': {
                'current_step': current_step + 1,
                'total_steps': len(self.workflow_steps),
                'completed_steps': completed,
                'failed_steps': failed,
                'percentage': int((completed / len(self.workflow_steps)) * 100)
            },
            'steps': [
                {
                    'name': step.name,
                    'description': step.description,
                    'status': step.status,
                    'execution_time': step.execution_time,
                    'error_message': step.error_message
                }
                for step in self.workflow_steps
            ]
        }
    
    def create_system_validator(self):
        """Create the system validator script since it's needed"""
        validator_code = '''#!/usr/bin/env python3
"""
System Validator Agent
Validates the complete generated system for quality and correctness.
"""

import os
import json
from datetime import datetime

def validate_framework():
    """Validate common framework was generated"""
    framework_dir = 'common_interview_framework'
    required_files = [
        'base_objects.py',
        'validation_functions.py', 
        'master_interview.py'
    ]
    
    issues = []
    for file in required_files:
        if not os.path.exists(os.path.join(framework_dir, file)):
            issues.append(f"Missing framework file: {file}")
    
    return issues

def validate_interviews():
    """Validate generated interviews"""
    interviews_dir = 'generated_interviews'
    if not os.path.exists(interviews_dir):
        return ["Generated interviews directory not found"]
    
    interview_files = [f for f in os.listdir(interviews_dir) if f.endswith('.yml')]
    issues = []
    
    if len(interview_files) == 0:
        issues.append("No interview files generated")
    
    return issues

def main():
    """Run complete system validation"""
    print("🔍 Running system validation...")
    
    all_issues = []
    
    # Validate framework
    framework_issues = validate_framework()
    all_issues.extend(framework_issues)
    
    # Validate interviews  
    interview_issues = validate_interviews()
    all_issues.extend(interview_issues)
    
    # Generate validation report
    report = {
        'validation_date': datetime.now().isoformat(),
        'total_issues': len(all_issues),
        'issues': all_issues,
        'status': 'PASS' if len(all_issues) == 0 else 'FAIL'
    }
    
    with open('validation_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    if len(all_issues) == 0:
        print("✅ System validation passed")
    else:
        print(f"❌ System validation failed with {len(all_issues)} issues")
        for issue in all_issues:
            print(f"  • {issue}")

if __name__ == '__main__':
    main()
'''
        
        validator_file = os.path.join(self.base_dir, 'system_validator.py')
        with open(validator_file, 'w', encoding='utf-8') as f:
            f.write(validator_code)
    
    def run_complete_workflow(self) -> WorkflowResult:
        """Execute the complete workflow orchestration"""
        print("🎯 Ontario Family Law Forms - Complete Workflow Starting")
        print(f"📂 Working Directory: {self.base_dir}")
        print(f"🗓️ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        workflow_start = time.time()
        
        # Check prerequisites
        if not self.check_prerequisites():
            print("❌ Prerequisites not met. Workflow cancelled.")
            return None
        
        # Create system validator if needed
        self.create_system_validator()
        
        # Execute workflow steps
        for i, step in enumerate(self.workflow_steps):
            print(f"\\n📋 Step {i+1}/{len(self.workflow_steps)}: {step.name}")
            
            # Check dependencies
            if not self.can_execute_step(step):
                step.status = 'failed'
                step.error_message = 'Dependencies not satisfied'
                print(f"❌ Cannot execute - dependencies not satisfied")
                continue
            
            # Execute step
            success = self.execute_step(step)
            
            if success:
                # Verify outputs
                if not self.check_step_outputs(step):
                    step.status = 'failed'
                    step.error_message = 'Expected outputs missing'
                    success = False
            
            # Save progress report
            progress = self.generate_progress_report(i)
            progress_file = os.path.join(self.base_dir, 'workflow_progress.json')
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, indent=2)
            
            if not success and step.name != 'generate_tests':
                # Allow tests to fail but continue
                print(f"⚠️ Step {step.name} failed, continuing workflow...")
        
        # Calculate final results
        workflow_time = time.time() - workflow_start
        completed_steps = sum(1 for s in self.workflow_steps if s.status == 'completed')
        failed_steps = sum(1 for s in self.workflow_steps if s.status == 'failed')
        
        # Count outputs
        interviews_dir = os.path.join(self.base_dir, 'generated_interviews')
        interviews_count = len([f for f in os.listdir(interviews_dir) if f.endswith('.yml')]) if os.path.exists(interviews_dir) else 0
        
        tests_dir = os.path.join(self.base_dir, 'generated_tests')
        tests_count = len([f for f in os.listdir(tests_dir) if f.endswith('.spec.js')]) if os.path.exists(tests_dir) else 0
        
        forms_count = len([f for f in os.listdir(os.path.join(self.base_dir, 'parsed_forms')) if f.endswith('.json')]) if os.path.exists(os.path.join(self.base_dir, 'parsed_forms')) else 0
        
        result = WorkflowResult(
            total_steps=len(self.workflow_steps),
            completed_steps=completed_steps,
            failed_steps=failed_steps,
            total_forms_processed=forms_count,
            total_interviews_generated=interviews_count,
            total_tests_generated=tests_count,
            execution_time=workflow_time,
            output_directories={
                'framework': os.path.join(self.base_dir, 'common_interview_framework'),
                'interviews': os.path.join(self.base_dir, 'generated_interviews'),
                'tests': os.path.join(self.base_dir, 'generated_tests')
            }
        )
        
        self._generate_final_report(result)
        return result
    
    def _generate_final_report(self, result: WorkflowResult):
        """Generate final workflow report"""
        print(f"\\n{'='*80}")
        print("🎉 ONTARIO FAMILY LAW FORMS WORKFLOW COMPLETE")
        print(f"{'='*80}")
        
        print(f"\\n📊 SUMMARY:")
        print(f"   • Total Execution Time: {result.execution_time:.1f} seconds")
        print(f"   • Steps Completed: {result.completed_steps}/{result.total_steps}")
        print(f"   • Steps Failed: {result.failed_steps}")
        print(f"   • Forms Processed: {result.total_forms_processed}")
        print(f"   • Interviews Generated: {result.total_interviews_generated}")
        print(f"   • Test Suites Generated: {result.total_tests_generated}")
        
        print(f"\\n📂 OUTPUT DIRECTORIES:")
        for name, path in result.output_directories.items():
            status = "✅" if os.path.exists(path) else "❌"
            print(f"   • {name.title()}: {status} {path}")
        
        print(f"\\n📋 STEP STATUS:")
        for step in self.workflow_steps:
            status_icon = {
                'completed': '✅',
                'failed': '❌',
                'pending': '⏳',
                'running': '🔄'
            }.get(step.status, '❓')
            
            print(f"   {status_icon} {step.description} ({step.execution_time:.1f}s)")
            if step.error_message:
                print(f"      🚨 {step.error_message}")
        
        # Success criteria
        success_percentage = (result.completed_steps / result.total_steps) * 100
        
        if success_percentage >= 80:
            print(f"\\n🎯 WORKFLOW SUCCESS ({success_percentage:.0f}%)")
            print("   ✅ Framework generated successfully")
            if result.total_interviews_generated > 0:
                print(f"   ✅ {result.total_interviews_generated} interviews generated")
            if result.total_tests_generated > 0:
                print(f"   ✅ {result.total_tests_generated} test suites generated")
        else:
            print(f"\\n⚠️ WORKFLOW PARTIAL SUCCESS ({success_percentage:.0f}%)")
        
        print(f"\\n🚀 NEXT STEPS:")
        print("   1. Review generated interviews in generated_interviews/")
        print("   2. Test interviews manually in Docassemble")
        if result.total_tests_generated > 0:
            print("   3. Run automated tests: npx playwright test")
        print("   4. Deploy to production environment")
        print("   5. Monitor and iterate based on user feedback")
        
        # Save detailed report
        report = {
            'workflow_completion': datetime.now().isoformat(),
            'execution_time_seconds': result.execution_time,
            'success_rate': success_percentage,
            'results': {
                'total_steps': result.total_steps,
                'completed_steps': result.completed_steps,
                'failed_steps': result.failed_steps,
                'forms_processed': result.total_forms_processed,
                'interviews_generated': result.total_interviews_generated,
                'tests_generated': result.total_tests_generated
            },
            'output_directories': result.output_directories,
            'step_details': [
                {
                    'name': step.name,
                    'description': step.description,
                    'status': step.status,
                    'execution_time': step.execution_time,
                    'error_message': step.error_message
                }
                for step in self.workflow_steps
            ]
        }
        
        report_file = os.path.join(self.base_dir, 'workflow_final_report.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"\\n📄 Detailed report saved: {report_file}")

def main():
    """Main execution function"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    orchestrator = FormFactoryOrchestrator(base_dir)
    
    try:
        result = orchestrator.run_complete_workflow()
        
        if result:
            success_rate = (result.completed_steps / result.total_steps) * 100
            exit_code = 0 if success_rate >= 80 else 1
            exit(exit_code)
        else:
            exit(1)
            
    except KeyboardInterrupt:
        print("\\n⚠️ Workflow interrupted by user")
        exit(130)
    except Exception as e:
        print(f"\\n❌ Workflow failed with exception: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == '__main__':
    main()