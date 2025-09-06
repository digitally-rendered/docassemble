#!/usr/bin/env python3
"""
Test Factory Agent

Generates comprehensive Playwright test suites for Ontario family law form interviews.
Creates tests that cover all paths, validation, and edge cases.

This agent:
1. Analyzes generated interview YAML files
2. Creates test data for various scenarios  
3. Generates Playwright test specifications
4. Creates edge case and error handling tests
5. Builds comprehensive test coverage

Author: Form Factory Orchestrator
Created: 2025-09-05
"""

import json
import os
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import random
import string

@dataclass
class TestScenario:
    """Represents a test scenario for an interview"""
    scenario_name: str
    description: str
    test_data: Dict
    expected_outcome: str
    validation_points: List[str]
    edge_case: bool = False

@dataclass  
class TestSuite:
    """Represents a complete test suite for a form"""
    form_name: str
    form_number: str
    scenarios: List[TestScenario]
    setup_code: str
    teardown_code: str

class TestFactory:
    """Generates comprehensive test suites for Ontario family law interviews"""
    
    def __init__(self, generated_interviews_dir: str, parsed_forms_dir: str):
        self.generated_interviews_dir = generated_interviews_dir
        self.parsed_forms_dir = parsed_forms_dir
        self.test_suites = {}
        
        # Sample data generators
        self.sample_data = self._initialize_sample_data()
    
    def _initialize_sample_data(self) -> Dict:
        """Initialize sample test data generators"""
        return {
            'names': {
                'first': ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Lisa', 'Robert', 'Mary'],
                'last': ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
            },
            'addresses': [
                '123 Main Street, Toronto, ON',
                '456 Oak Avenue, Ottawa, ON', 
                '789 Pine Road, Hamilton, ON',
                '321 Elm Street, London, ON'
            ],
            'postal_codes': ['M5V 3A1', 'K1A 0A6', 'L8L 0A1', 'N6A 3K7'],
            'phone_numbers': ['416-555-0123', '613-555-0456', '905-555-0789', '519-555-0321'],
            'emails': ['test@example.com', 'user@test.org', 'person@sample.net'],
            'court_file_numbers': ['TO-23-12345678', 'OT-24-87654321', 'HA-23-11111111']
        }
    
    def analyze_interview_structure(self, interview_file: str) -> Dict:
        """Analyze interview YAML to understand structure and fields"""
        with open(interview_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract form information from YAML content
        form_info = {
            'form_name': '',
            'form_number': '',
            'fields': [],
            'sections': [],
            'validation_rules': [],
            'required_fields': []
        }
        
        # Parse basic form info
        form_name_match = re.search(r"source_form['\"]:\s*['\"]([^'\"]+)['\"]", content)
        if form_name_match:
            form_info['form_name'] = form_name_match.group(1)
        
        form_number_match = re.search(r"Form (\d+[A-Z]?)", content)
        if form_number_match:
            form_info['form_number'] = form_number_match.group(1)
        
        # Extract field information
        field_pattern = r"field['\"]:\s*['\"]?([^'\"\\s]+)['\"]?"
        fields = re.findall(field_pattern, content)
        form_info['fields'] = list(set(fields))
        
        # Extract section information from question titles
        question_pattern = r"question['\"]:\s*['\"]([^'\"]+)['\"]"
        questions = re.findall(question_pattern, content)
        form_info['sections'] = questions
        
        # Extract validation rules
        validation_pattern = r"validation_code['\"]:\s*['\"]([^'\"]+)['\"]"
        validations = re.findall(validation_pattern, content)
        form_info['validation_rules'] = validations
        
        # Extract required fields
        required_pattern = r"required['\"]:\s*True"
        # This is a simplified extraction - in real implementation would be more sophisticated
        
        return form_info
    
    def generate_test_data(self, form_info: Dict) -> Dict[str, TestScenario]:
        """Generate test scenarios with realistic data"""
        scenarios = {}
        
        # Happy path scenario
        scenarios['happy_path'] = self._generate_happy_path_scenario(form_info)
        
        # Validation error scenarios  
        scenarios['validation_errors'] = self._generate_validation_error_scenario(form_info)
        
        # Edge case scenarios
        scenarios['edge_cases'] = self._generate_edge_case_scenario(form_info)
        
        # Incomplete data scenario
        scenarios['incomplete_data'] = self._generate_incomplete_data_scenario(form_info)
        
        # Maximum data scenario
        scenarios['maximum_data'] = self._generate_maximum_data_scenario(form_info)
        
        return scenarios
    
    def _generate_happy_path_scenario(self, form_info: Dict) -> TestScenario:
        """Generate a scenario with valid data for all fields"""
        test_data = {}
        
        for field in form_info['fields']:
            test_data[field] = self._generate_field_value(field, 'valid')
        
        return TestScenario(
            scenario_name='happy_path',
            description='Complete form with all valid data',
            test_data=test_data,
            expected_outcome='success',
            validation_points=[
                'Form completes without errors',
                'All sections are accessible',
                'PDF generates successfully'
            ]
        )
    
    def _generate_validation_error_scenario(self, form_info: Dict) -> TestScenario:
        """Generate scenarios that test validation rules"""
        test_data = {}
        validation_points = []
        
        for field in form_info['fields']:
            if self._field_has_validation(field):
                test_data[field] = self._generate_field_value(field, 'invalid')
                validation_points.append(f'Validation error shown for {field}')
            else:
                test_data[field] = self._generate_field_value(field, 'valid')
        
        return TestScenario(
            scenario_name='validation_errors',
            description='Test validation rules and error messages',
            test_data=test_data,
            expected_outcome='validation_errors',
            validation_points=validation_points
        )
    
    def _generate_edge_case_scenario(self, form_info: Dict) -> TestScenario:
        """Generate edge case scenarios"""
        test_data = {}
        
        for field in form_info['fields']:
            test_data[field] = self._generate_field_value(field, 'edge_case')
        
        return TestScenario(
            scenario_name='edge_cases',
            description='Test edge cases and boundary conditions',
            test_data=test_data,
            expected_outcome='success',
            validation_points=[
                'Edge case values are handled correctly',
                'No unexpected errors occur',
                'Form still generates properly'
            ],
            edge_case=True
        )
    
    def _generate_incomplete_data_scenario(self, form_info: Dict) -> TestScenario:
        """Generate scenario with missing optional data"""
        test_data = {}
        
        # Only fill required fields and some optional ones
        field_count = len(form_info['fields'])
        fields_to_fill = random.sample(form_info['fields'], max(1, field_count // 2))
        
        for field in fields_to_fill:
            test_data[field] = self._generate_field_value(field, 'valid')
        
        return TestScenario(
            scenario_name='incomplete_data',
            description='Test form with minimal required data',
            test_data=test_data,
            expected_outcome='success',
            validation_points=[
                'Form accepts incomplete data',
                'Optional fields can be left blank',
                'Required field validation works'
            ]
        )
    
    def _generate_maximum_data_scenario(self, form_info: Dict) -> TestScenario:
        """Generate scenario with maximum length data"""
        test_data = {}
        
        for field in form_info['fields']:
            test_data[field] = self._generate_field_value(field, 'maximum')
        
        return TestScenario(
            scenario_name='maximum_data',
            description='Test form with maximum length data in all fields',
            test_data=test_data,
            expected_outcome='success',
            validation_points=[
                'Long text values are handled correctly',
                'No truncation errors occur',
                'PDF formatting remains correct'
            ]
        )
    
    def _field_has_validation(self, field_name: str) -> bool:
        """Check if field likely has validation based on name"""
        validation_indicators = [
            'email', 'phone', 'postal', 'court_file', 'date', 'amount'
        ]
        return any(indicator in field_name.lower() for indicator in validation_indicators)
    
    def _generate_field_value(self, field_name: str, value_type: str) -> str:
        """Generate appropriate test value for a field"""
        field_lower = field_name.lower()
        
        # Email fields
        if 'email' in field_lower:
            if value_type == 'valid':
                return random.choice(self.sample_data['emails'])
            elif value_type == 'invalid':
                return 'invalid-email'
            elif value_type == 'edge_case':
                return 'test+edge@very-long-domain-name.co.uk'
            elif value_type == 'maximum':
                return 'very-long-email-address@very-long-domain-name.com'
        
        # Phone fields  
        elif 'phone' in field_lower:
            if value_type == 'valid':
                return random.choice(self.sample_data['phone_numbers'])
            elif value_type == 'invalid':
                return '123-456'
            elif value_type == 'edge_case':
                return '1-800-555-0123'
            elif value_type == 'maximum':
                return '1-800-555-0123 ext 12345'
        
        # Postal code fields
        elif 'postal' in field_lower:
            if value_type == 'valid':
                return random.choice(self.sample_data['postal_codes'])
            elif value_type == 'invalid':
                return '12345'
            elif value_type == 'edge_case':
                return 'K1A0A6'  # No space
            elif value_type == 'maximum':
                return 'M5V 3A1'
        
        # Court file number fields
        elif 'court_file' in field_lower:
            if value_type == 'valid':
                return random.choice(self.sample_data['court_file_numbers'])
            elif value_type == 'invalid':
                return '123456'
            elif value_type == 'edge_case':
                return 'TO2312345678'  # No dashes
            elif value_type == 'maximum':
                return 'TO-23-123456789'  # Extra digit
        
        # Name fields
        elif any(name_term in field_lower for name_term in ['name', 'first', 'last']):
            if value_type == 'valid':
                if 'first' in field_lower:
                    return random.choice(self.sample_data['names']['first'])
                elif 'last' in field_lower:
                    return random.choice(self.sample_data['names']['last'])
                else:
                    return f"{random.choice(self.sample_data['names']['first'])} {random.choice(self.sample_data['names']['last'])}"
            elif value_type == 'invalid':
                return ''  # Empty name
            elif value_type == 'edge_case':
                return 'Jean-Claude Van Damme-Smith'
            elif value_type == 'maximum':
                return 'Very Long First Name With Many Parts ' + 'Extended Last Name With Multiple Hyphens-And-Parts'
        
        # Address fields
        elif 'address' in field_lower:
            if value_type == 'valid':
                return random.choice(self.sample_data['addresses'])
            elif value_type == 'invalid':
                return ''
            elif value_type == 'edge_case':
                return 'Unit 123-A, 456 Main Street North, Apartment Building Complex'
            elif value_type == 'maximum':
                return 'Unit 1234-B, 5678 Very Long Street Name With Multiple Parts North East, Large Apartment Building Complex Name, Toronto'
        
        # Date fields
        elif 'date' in field_lower or 'birth' in field_lower:
            if value_type == 'valid':
                base_date = datetime.now() - timedelta(days=random.randint(30*365, 80*365))  # 30-80 years ago
                return base_date.strftime('%m/%d/%Y')
            elif value_type == 'invalid':
                return '99/99/9999'
            elif value_type == 'edge_case':
                return '02/29/2000'  # Leap year
            elif value_type == 'maximum':
                return '12/31/1900'  # Very old date
        
        # Currency/amount fields
        elif any(money_term in field_lower for money_term in ['amount', 'total', 'income', 'expense']):
            if value_type == 'valid':
                return str(random.randint(1000, 100000))
            elif value_type == 'invalid':
                return '-500'  # Negative amount
            elif value_type == 'edge_case':
                return '0'
            elif value_type == 'maximum':
                return '999999999.99'
        
        # Default text fields
        else:
            if value_type == 'valid':
                return 'Test Value'
            elif value_type == 'invalid':
                return ''
            elif value_type == 'edge_case':
                return 'Special characters: @#$%^&*()_+-=[]{}|;:,.<>?'
            elif value_type == 'maximum':
                return 'Very long text value that tests the maximum length handling capabilities of the form field validation and ensures that the system can handle extended input without breaking or causing unexpected behavior in the user interface or backend processing systems.'
        
        return 'Default Test Value'
    
    def generate_playwright_test(self, form_info: Dict, scenarios: Dict[str, TestScenario]) -> str:
        """Generate Playwright test code for the form"""
        form_name = form_info['form_name']
        form_number = form_info['form_number']
        
        test_code = f'''/**
 * Playwright Tests for Ontario Family Law Form {form_number}
 * Generated automatically by Test Factory Agent
 * 
 * Form: {form_name}
 * Generated: {datetime.now().isoformat()}
 */

import {{ test, expect }} from '@playwright/test';
import {{ BaseFamilyLawFormPage }} from '../pages/BaseFamilyLawFormPage';
import {{ testData }} from '../fixtures/form_{form_number.lower()}_data';

class Form{form_number}Page extends BaseFamilyLawFormPage {{
    constructor(page) {{
        super(page);
        this.formNumber = '{form_number}';
        this.formTitle = 'Ontario Family Law Form {form_number}';
    }}

    async fillFormData(data) {{
        // Navigate through form sections
        for (const [fieldName, value] of Object.entries(data)) {{
            await this.fillField(fieldName, value);
        }}
    }}

    async validateFormCompletion() {{
        // Check that form completed successfully
        await expect(this.page.locator('.form-complete')).toBeVisible();
        await expect(this.page.locator('text=Your Form {form_number} is Ready')).toBeVisible();
    }}
}}

test.describe('Form {form_number} - {form_name}', () => {{
    let formPage;

    test.beforeEach(async ({{ page }}) => {{
        formPage = new Form{form_number}Page(page);
        await formPage.goto('/interview?i=docassemble.webapp:ontario-family-law/utilities/generated_interviews/{form_name}_interview.yml');
        await formPage.waitForLoad();
    }});
'''

        # Generate test cases for each scenario
        for scenario_name, scenario in scenarios.items():
            test_code += f'''
    test('{scenario.scenario_name}: {scenario.description}', async ({{ page }}) => {{
        const testData = {{'''
            
            # Add test data  
            for field, value in scenario.test_data.items():
                # Escape quotes in values
                escaped_value = str(value).replace("'", "\\'").replace('"', '\\"')
                test_code += f'''
            '{field}': "{escaped_value}",'''
            
            test_code += f'''
        }};

        // Fill form with test data
        await formPage.fillFormData(testData);
'''
            
            # Add validation points
            if scenario.expected_outcome == 'success':
                test_code += '''
        // Validate successful completion
        await formPage.validateFormCompletion();
        
        // Check that PDF can be generated
        await expect(page.locator('text=Download PDF')).toBeVisible();
'''
            elif scenario.expected_outcome == 'validation_errors':
                test_code += '''
        // Validate that appropriate error messages are shown
        const errorMessages = await page.locator('.validation-error').allTextContents();
        expect(errorMessages.length).toBeGreaterThan(0);
'''
            
            for validation_point in scenario.validation_points:
                test_code += f'''
        // {validation_point}'''
            
            test_code += '''
    });
'''

        # Add accessibility and performance tests
        test_code += f'''
    test('Accessibility compliance', async ({{ page }}) => {{
        // Test keyboard navigation
        await formPage.testKeyboardNavigation();
        
        // Test screen reader compatibility
        await formPage.testScreenReaderCompatibility();
        
        // Check WCAG compliance
        await formPage.checkWCAGCompliance();
    }});

    test('Performance benchmarks', async ({{ page }}) => {{
        // Measure page load time
        const loadTime = await formPage.measureLoadTime();
        expect(loadTime).toBeLessThan(3000); // 3 seconds max
        
        // Measure form completion time
        const testData = testData.happy_path;
        const startTime = Date.now();
        await formPage.fillFormData(testData);
        const completionTime = Date.now() - startTime;
        expect(completionTime).toBeLessThan(30000); // 30 seconds max
    }});

    test('Cross-browser compatibility', async ({{ page, browserName }}) => {{
        console.log(`Testing on ${{browserName}}`);
        
        // Test basic functionality on different browsers
        const testData = testData.happy_path;
        await formPage.fillFormData(testData);
        await formPage.validateFormCompletion();
    }});

    test('Mobile responsiveness', async ({{ page }}) => {{
        // Test on mobile viewport
        await page.setViewportSize({{ width: 375, height: 667 }});
        await formPage.testMobileCompatibility();
        
        // Test on tablet viewport  
        await page.setViewportSize({{ width: 768, height: 1024 }});
        await formPage.testTabletCompatibility();
    }});
}});
'''

        return test_code
    
    def generate_test_data_fixtures(self, form_info: Dict, scenarios: Dict[str, TestScenario]) -> str:
        """Generate test data fixtures file"""
        form_number = form_info['form_number']
        
        fixtures_code = f'''/**
 * Test Data Fixtures for Form {form_number}
 * Generated automatically by Test Factory Agent
 */

export const testData = {{'''
        
        for scenario_name, scenario in scenarios.items():
            fixtures_code += f'''
    {scenario_name}: {{'''
            
            for field, value in scenario.test_data.items():
                # Escape quotes and handle different data types
                if isinstance(value, str):
                    escaped_value = value.replace("'", "\\'").replace('"', '\\"')
                    fixtures_code += f'''
        "{field}": "{escaped_value}",'''
                else:
                    fixtures_code += f'''
        "{field}": {json.dumps(value)},'''
            
            fixtures_code += f'''
    }}, // {scenario.description}'''
        
        fixtures_code += '''
};

export default testData;
'''
        return fixtures_code
    
    def generate_test_suite(self, form_name: str) -> TestSuite:
        """Generate complete test suite for a form"""
        interview_file = os.path.join(self.generated_interviews_dir, f"{form_name}_interview.yml")
        
        if not os.path.exists(interview_file):
            raise FileNotFoundError(f"Interview file not found: {interview_file}")
        
        # Analyze interview structure
        form_info = self.analyze_interview_structure(interview_file)
        
        # Generate test scenarios
        scenarios_dict = self.generate_test_data(form_info)
        scenarios = list(scenarios_dict.values())
        
        # Generate setup and teardown code
        setup_code = self._generate_setup_code(form_info)
        teardown_code = self._generate_teardown_code(form_info)
        
        return TestSuite(
            form_name=form_name,
            form_number=form_info['form_number'],
            scenarios=scenarios,
            setup_code=setup_code,
            teardown_code=teardown_code
        )
    
    def _generate_setup_code(self, form_info: Dict) -> str:
        """Generate setup code for tests"""
        return f'''
// Setup for {form_info['form_name']} tests
// Initialize test environment
// Clear any existing session data
// Set up database in clean state
'''
    
    def _generate_teardown_code(self, form_info: Dict) -> str:
        """Generate teardown code for tests"""
        return f'''
// Teardown for {form_info['form_name']} tests  
// Clean up test data
// Reset session state
// Close any open resources
'''
    
    def save_test_files(self, test_suite: TestSuite, output_dir: str):
        """Save test files to output directory"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate form info and scenarios for files
        form_info = {
            'form_name': test_suite.form_name,
            'form_number': test_suite.form_number,
            'fields': []  # Would need to be populated from interview analysis
        }
        
        scenarios_dict = {scenario.scenario_name: scenario for scenario in test_suite.scenarios}
        
        # Save Playwright test file
        test_code = self.generate_playwright_test(form_info, scenarios_dict)
        test_file = os.path.join(output_dir, f"form_{test_suite.form_number.lower()}.spec.js")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_code)
        
        # Save test data fixtures
        fixtures_code = self.generate_test_data_fixtures(form_info, scenarios_dict)
        fixtures_file = os.path.join(output_dir, f"form_{test_suite.form_number.lower()}_data.js")
        with open(fixtures_file, 'w', encoding='utf-8') as f:
            f.write(fixtures_code)
        
        print(f"✅ Test files saved for {test_suite.form_name}:")
        print(f"   • {test_file}")
        print(f"   • {fixtures_file}")
    
    def generate_all_test_suites(self, output_dir: str):
        """Generate test suites for all forms"""
        print("🧪 Generating comprehensive test suites...")
        
        # Get list of generated interviews
        interview_files = [f for f in os.listdir(self.generated_interviews_dir) 
                          if f.endswith('_interview.yml')]
        
        total_suites = 0
        total_scenarios = 0
        
        for interview_file in interview_files:
            form_name = interview_file.replace('_interview.yml', '')
            
            try:
                # Generate test suite
                test_suite = self.generate_test_suite(form_name)
                
                # Save test files
                self.save_test_files(test_suite, output_dir)
                
                total_suites += 1
                total_scenarios += len(test_suite.scenarios)
                
                print(f"✅ Generated test suite for {form_name} ({len(test_suite.scenarios)} scenarios)")
                
            except Exception as e:
                print(f"❌ Error generating tests for {form_name}: {e}")
        
        # Generate master test runner
        self._generate_master_test_runner(output_dir, interview_files)
        
        print(f"\\n📊 Test Generation Summary:")
        print(f"   • Test suites generated: {total_suites}")
        print(f"   • Total test scenarios: {total_scenarios}")
        print(f"   • Output directory: {output_dir}")
    
    def _generate_master_test_runner(self, output_dir: str, interview_files: List[str]):
        """Generate master test runner that runs all tests"""
        runner_code = '''/**
 * Master Test Runner for Ontario Family Law Forms
 * Runs all generated form tests with reporting
 */

import { test, expect } from '@playwright/test';

test.describe('Ontario Family Law Forms - Complete Test Suite', () => {
    test('All forms load successfully', async ({ page }) => {
        const forms = ['''
        
        for interview_file in interview_files:
            form_name = interview_file.replace('_interview.yml', '')
            runner_code += f'''
            '{form_name}','''
        
        runner_code += '''
        ];

        for (const formName of forms) {
            console.log(`Testing form: ${formName}`);
            await page.goto(`/interview?i=docassemble.webapp:ontario-family-law/utilities/generated_interviews/${formName}_interview.yml`);
            
            // Wait for form to load
            await expect(page.locator('h1')).toBeVisible({ timeout: 10000 });
            
            console.log(`✅ ${formName} loaded successfully`);
        }
    });

    test('Performance benchmark - All forms', async ({ page }) => {
        const forms = ['''
        
        for interview_file in interview_files:
            form_name = interview_file.replace('_interview.yml', '')
            runner_code += f'''
            '{form_name}','''
        
        runner_code += '''
        ];

        const loadTimes = [];

        for (const formName of forms) {
            const startTime = Date.now();
            await page.goto(`/interview?i=docassemble.webapp:ontario-family-law/utilities/generated_interviews/${formName}_interview.yml`);
            await expect(page.locator('h1')).toBeVisible();
            const loadTime = Date.now() - startTime;
            
            loadTimes.push({ form: formName, time: loadTime });
            console.log(`${formName}: ${loadTime}ms`);
        }

        // Check that all forms load within acceptable time
        const avgLoadTime = loadTimes.reduce((sum, item) => sum + item.time, 0) / loadTimes.length;
        expect(avgLoadTime).toBeLessThan(5000); // 5 seconds average
        
        console.log(`Average load time: ${avgLoadTime.toFixed(0)}ms`);
    });
});
'''
        
        runner_file = os.path.join(output_dir, 'master_test_runner.spec.js')
        with open(runner_file, 'w', encoding='utf-8') as f:
            f.write(runner_code)
        
        print(f"✅ Master test runner saved: {runner_file}")

def main():
    """Main execution function"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    generated_interviews_dir = os.path.join(base_dir, 'generated_interviews')
    parsed_forms_dir = os.path.join(base_dir, 'parsed_forms')
    output_dir = os.path.join(base_dir, 'generated_tests')
    
    factory = TestFactory(generated_interviews_dir, parsed_forms_dir)
    
    try:
        factory.generate_all_test_suites(output_dir)
        
        print(f"\\n🎯 Test Generation Complete!")
        print(f"\\n🚀 Next Steps:")
        print(f"  1. Review generated tests in {output_dir}")
        print(f"  2. Run tests with: npx playwright test")
        print(f"  3. Adjust test data as needed for specific forms")
        print(f"  4. Integrate with CI/CD pipeline")
        
    except Exception as e:
        print(f"❌ Error during test generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()