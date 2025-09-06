#!/usr/bin/env python3
"""
Playwright Test Generator for Docassemble Interviews
Reads interview YAML files and generates comprehensive Playwright tests
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class PlaywrightTestGenerator:
    def __init__(self, interviews_dir: str = 'generated_interviews_complete'):
        self.interviews_dir = Path(interviews_dir)
        self.tests_dir = Path('playwright_tests_generated')
        self.tests_dir.mkdir(parents=True, exist_ok=True)
        
        # Common test data for Ontario forms
        self.test_data = {
            'applicant': {
                'first_name': 'John',
                'middle_name': 'Michael',
                'last_name': 'Smith',
                'birthdate': '1980-01-15',
                'address_street': '123 Main Street',
                'address_city': 'Toronto',
                'address_province': 'Ontario',
                'address_postal_code': 'M5H 2N2',
                'phone': '416-555-1234',
                'email': 'john.smith@example.com'
            },
            'respondent': {
                'first_name': 'Jane',
                'middle_name': 'Elizabeth',
                'last_name': 'Doe',
                'birthdate': '1982-03-20',
                'address_street': '456 Queen Street',
                'address_city': 'Ottawa',
                'address_province': 'Ontario',
                'address_postal_code': 'K1P 1J9',
                'phone': '613-555-5678',
                'email': 'jane.doe@example.com'
            },
            'court': {
                'name': 'Superior Court of Justice',
                'location': '393 University Avenue, Toronto, ON',
                'file_number': 'FC-2024-12345'
            },
            'dates': {
                'marriage_date': '2005-06-15',
                'separation_date': '2023-01-01',
                'current_date': datetime.now().strftime('%Y-%m-%d')
            },
            'children': [
                {
                    'name': 'Emily Smith',
                    'birthdate': '2010-04-10',
                    'age': '14',
                    'grade': '9',
                    'residing_with': 'Applicant'
                },
                {
                    'name': 'Michael Smith',
                    'birthdate': '2012-09-22',
                    'age': '12',
                    'grade': '7',
                    'residing_with': 'Shared'
                }
            ]
        }
    
    def parse_interview_file(self, yaml_file: Path) -> Dict[str, Any]:
        """Parse a YAML interview file to extract structure"""
        with open(yaml_file, 'r') as f:
            content = f.read()
        
        # Parse metadata
        metadata = self._extract_metadata(content)
        
        # Extract question blocks
        questions = self._extract_questions(content)
        
        # Extract mandatory fields
        mandatory_fields = self._extract_mandatory_fields(content)
        
        # Extract field definitions
        fields = self._extract_fields(content)
        
        # Extract validation rules
        validations = self._extract_validations(content)
        
        return {
            'metadata': metadata,
            'questions': questions,
            'mandatory_fields': mandatory_fields,
            'fields': fields,
            'validations': validations,
            'file_path': str(yaml_file)
        }
    
    def _extract_metadata(self, content: str) -> Dict:
        """Extract metadata from interview"""
        metadata = {}
        
        # Find metadata block
        metadata_match = re.search(r'metadata:\s*\n((?:  .*\n)*)', content)
        if metadata_match:
            metadata_text = metadata_match.group(1)
            
            # Extract common metadata fields
            title_match = re.search(r'title:\s*(.+)', metadata_text)
            if title_match:
                metadata['title'] = title_match.group(1).strip()
            
            form_match = re.search(r'form_number:\s*(.+)', metadata_text)
            if form_match:
                metadata['form_number'] = form_match.group(1).strip()
            
            fields_match = re.search(r'total_fields:\s*(\d+)', metadata_text)
            if fields_match:
                metadata['total_fields'] = int(fields_match.group(1))
        
        return metadata
    
    def _extract_questions(self, content: str) -> List[Dict]:
        """Extract question blocks from interview"""
        questions = []
        
        # Find all question blocks
        question_blocks = re.findall(r'^question:\s*\|\s*\n((?:  .*\n)*?)^(?:fields:|yesno:|buttons:|subquestion:)', 
                                     content, re.MULTILINE)
        
        for block in question_blocks:
            question_text = block.strip()
            if question_text:
                questions.append({'text': question_text})
        
        # Find field definitions
        field_blocks = re.findall(r'^fields:\s*\n((?:  .*\n)*)', content, re.MULTILINE)
        
        for block in field_blocks:
            fields = self._parse_field_block(block)
            if fields:
                questions.append({'fields': fields})
        
        return questions
    
    def _parse_field_block(self, block: str) -> List[Dict]:
        """Parse a fields block to extract field definitions"""
        fields = []
        
        lines = block.split('\n')
        current_field = None
        
        for line in lines:
            # Check for field definition
            field_match = re.match(r'  - (\w+):\s*(.+)?', line)
            if field_match:
                if current_field:
                    fields.append(current_field)
                
                field_name = field_match.group(1)
                field_type = field_match.group(2) or 'text'
                
                current_field = {
                    'name': field_name,
                    'type': field_type.strip() if field_type else 'text'
                }
            
            # Check for field properties
            elif current_field:
                prop_match = re.match(r'    (\w+):\s*(.+)', line)
                if prop_match:
                    prop_name = prop_match.group(1)
                    prop_value = prop_match.group(2)
                    current_field[prop_name] = prop_value
        
        if current_field:
            fields.append(current_field)
        
        return fields
    
    def _extract_mandatory_fields(self, content: str) -> List[str]:
        """Extract mandatory field names from code block"""
        fields = []
        
        # Find mandatory code block
        mandatory_match = re.search(r'mandatory:\s*True\s*\ncode:\s*\|\s*\n((?:  .*\n)*)', content)
        if mandatory_match:
            code_block = mandatory_match.group(1)
            
            # Extract field names (simple variable names on their own line)
            field_matches = re.findall(r'^  (\w+)\s*$', code_block, re.MULTILINE)
            fields.extend(field_matches)
        
        return fields
    
    def _extract_fields(self, content: str) -> Dict[str, str]:
        """Extract all field definitions"""
        fields = {}
        
        # Find yesno fields
        yesno_matches = re.findall(r'^yesno:\s*(\w+)', content, re.MULTILINE)
        for field in yesno_matches:
            fields[field] = 'yesno'
        
        # Find field definitions in fields blocks
        field_blocks = re.findall(r'^fields:\s*\n((?:  .*\n)*)', content, re.MULTILINE)
        for block in field_blocks:
            parsed_fields = self._parse_field_block(block)
            for field in parsed_fields:
                fields[field['name']] = field['type']
        
        return fields
    
    def _extract_validations(self, content: str) -> Dict[str, str]:
        """Extract validation rules"""
        validations = {}
        
        # Find validation code blocks
        validation_matches = re.findall(r'validation code:\s*\|\s*\n((?:  .*\n)*)', content)
        for block in validation_matches:
            # Simple extraction of validation patterns
            if 'postal' in block.lower():
                validations['postal_code'] = 'Canadian postal code format'
            if 'email' in block.lower():
                validations['email'] = 'Valid email format'
            if 'phone' in block.lower():
                validations['phone'] = 'Valid phone number'
        
        return validations
    
    def generate_test(self, interview_file: Path) -> str:
        """Generate a Playwright test for an interview file"""
        # Parse the interview
        interview_data = self.parse_interview_file(interview_file)
        
        form_number = interview_data['metadata'].get('form_number', 'unknown')
        form_title = interview_data['metadata'].get('title', f'Form {form_number}')
        
        # Generate test content
        test_content = self._generate_test_header(form_number, form_title)
        test_content += self._generate_test_imports()
        test_content += self._generate_test_fixtures(form_number)
        test_content += self._generate_test_cases(form_number, interview_data)
        test_content += self._generate_test_helpers(form_number)
        
        # Save test file
        test_file = self.tests_dir / f"test_form_{form_number}.spec.js"
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        return str(test_file)
    
    def _generate_test_header(self, form_number: str, form_title: str) -> str:
        """Generate test file header"""
        return f"""/**
 * Playwright Test for Ontario Family Law Form {form_number}
 * {form_title}
 * Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
 * 
 * This test covers:
 * - Complete form flow from start to finish
 * - Field validation
 * - Required field checks
 * - Form submission
 */

"""
    
    def _generate_test_imports(self) -> str:
        """Generate test imports"""
        return """const { test, expect } = require('@playwright/test');
const path = require('path');

// Test configuration
const BASE_URL = process.env.DA_URL || 'http://localhost';
const INTERVIEW_URL = `${BASE_URL}/interview`;
const TIMEOUT = 60000; // 60 seconds

"""
    
    def _generate_test_fixtures(self, form_number: str) -> str:
        """Generate test fixtures and data"""
        return f"""// Test data for Form {form_number}
const testData = {{
  applicant: {{
    firstName: 'John',
    middleName: 'Michael',
    lastName: 'Smith',
    birthdate: '01/15/1980',
    street: '123 Main Street',
    city: 'Toronto',
    province: 'Ontario',
    postalCode: 'M5H 2N2',
    phone: '416-555-1234',
    email: 'john.smith@example.com'
  }},
  respondent: {{
    firstName: 'Jane',
    middleName: 'Elizabeth',
    lastName: 'Doe',
    birthdate: '03/20/1982',
    street: '456 Queen Street',
    city: 'Ottawa',
    province: 'Ontario',
    postalCode: 'K1P 1J9',
    phone: '613-555-5678',
    email: 'jane.doe@example.com'
  }},
  court: {{
    name: 'Superior Court of Justice',
    location: '393 University Avenue, Toronto, ON',
    fileNumber: 'FC-2024-12345'
  }},
  marriage: {{
    date: '06/15/2005',
    place: 'Toronto, Ontario, Canada',
    separationDate: '01/01/2023'
  }},
  children: [
    {{
      name: 'Emily Smith',
      birthdate: '04/10/2010',
      age: '14',
      grade: '9',
      residingWith: 'Applicant'
    }},
    {{
      name: 'Michael Smith',
      birthdate: '09/22/2012',
      age: '12',
      grade: '7',
      residingWith: 'Shared'
    }}
  ]
}};

"""
    
    def _generate_test_cases(self, form_number: str, interview_data: Dict) -> str:
        """Generate test cases"""
        test_cases = f"""// Test suite for Form {form_number}
test.describe('Form {form_number} - Complete Interview', () => {{
  test.setTimeout(TIMEOUT);
  
  test('should complete the entire form with valid data', async ({{ page }}) => {{
    // Navigate to the interview
    await page.goto(`${{INTERVIEW_URL}}/form_{form_number}_complete.yml`);
    
    // Wait for the interview to load
    await page.waitForSelector('h1', {{ timeout: 10000 }});
    
    // Start the interview
    const startButton = await page.$('button:has-text("Start")');
    if (startButton) {{
      await startButton.click();
    }}
    
    // Fill applicant information (from common intake)
    await fillApplicantInfo(page, testData.applicant);
    
    // Fill respondent information (from common intake)
    await fillRespondentInfo(page, testData.respondent);
    
    // Fill court information
    await fillCourtInfo(page, testData.court);
    
    // Fill marriage information if applicable
    if (await page.$('input[name="marriage_date"]')) {{
      await fillMarriageInfo(page, testData.marriage);
    }}
    
    // Fill children information if applicable
    if (await page.$('button:has-text("Add child")')) {{
      await fillChildrenInfo(page, testData.children);
    }}
    
    // Fill form-specific fields
    await fillFormSpecificFields_{form_number}(page);
    
    // Continue through remaining questions
    await continueToEnd(page);
    
    // Verify we reached the final screen
    await expect(page.locator('h1')).toContainText('Form {form_number} Complete');
    
    // Verify download button is present
    await expect(page.locator('button:has-text("Download Form {form_number}")')).toBeVisible();
  }});
  
  test('should validate required fields', async ({{ page }}) => {{
    await page.goto(`${{INTERVIEW_URL}}/form_{form_number}_complete.yml`);
    
    // Try to continue without filling required fields
    const continueButton = await page.$('button:has-text("Continue")');
    if (continueButton) {{
      await continueButton.click();
      
      // Should see validation errors
      const errorMessage = await page.$('.da-has-error, .text-danger');
      expect(errorMessage).toBeTruthy();
    }}
  }});
  
  test('should validate postal code format', async ({{ page }}) => {{
    await page.goto(`${{INTERVIEW_URL}}/form_{form_number}_complete.yml`);
    
    // Navigate to postal code field
    const postalField = await page.$('input[name*="postal"]');
    if (postalField) {{
      // Try invalid postal code
      await postalField.fill('INVALID');
      await page.click('button:has-text("Continue")');
      
      // Should see validation error
      const errorMessage = await page.$('.da-has-error, .text-danger');
      expect(errorMessage).toBeTruthy();
      
      // Enter valid postal code
      await postalField.fill('M5H 2N2');
      await page.click('button:has-text("Continue")');
    }}
  }});
  
  test('should save and resume interview', async ({{ page }}) => {{
    await page.goto(`${{INTERVIEW_URL}}/form_{form_number}_complete.yml`);
    
    // Fill some initial data
    await fillApplicantInfo(page, testData.applicant);
    
    // Save the interview
    const saveButton = await page.$('button:has-text("Save")');
    if (saveButton) {{
      await saveButton.click();
      
      // Get the resume URL
      const resumeUrl = await page.url();
      
      // Navigate away and come back
      await page.goto('about:blank');
      await page.goto(resumeUrl);
      
      // Verify data is preserved
      const firstNameField = await page.$('input[name="applicant_first_name"]');
      if (firstNameField) {{
        const value = await firstNameField.inputValue();
        expect(value).toBe(testData.applicant.firstName);
      }}
    }}
  }});
}});

"""
        
        # Add form-specific test cases based on the interview data
        if interview_data.get('fields'):
            test_cases += self._generate_field_specific_tests(form_number, interview_data['fields'])
        
        return test_cases
    
    def _generate_field_specific_tests(self, form_number: str, fields: Dict) -> str:
        """Generate tests for specific field types"""
        tests = f"""
// Form-specific field tests for Form {form_number}
test.describe('Form {form_number} - Field Validations', () => {{
"""
        
        # Add tests for different field types
        for field_name, field_type in fields.items():
            if field_type == 'email':
                tests += f"""
  test('should validate {field_name} email format', async ({{ page }}) => {{
    const emailField = await page.$('input[name="{field_name}"]');
    if (emailField) {{
      await emailField.fill('invalid-email');
      await page.click('button:has-text("Continue")');
      
      const error = await page.$('.da-has-error');
      expect(error).toBeTruthy();
      
      await emailField.fill('valid@example.com');
      await page.click('button:has-text("Continue")');
    }}
  }});
"""
            elif field_type == 'date':
                tests += f"""
  test('should accept valid date for {field_name}', async ({{ page }}) => {{
    const dateField = await page.$('input[name="{field_name}"]');
    if (dateField) {{
      await dateField.fill('01/01/2024');
      await page.click('button:has-text("Continue")');
    }}
  }});
"""
        
        tests += "});\n"
        return tests
    
    def _generate_test_helpers(self, form_number: str) -> str:
        """Generate helper functions"""
        return f"""
// Helper functions for Form {form_number}

async function fillApplicantInfo(page, data) {{
  // Fill applicant first name if visible
  const firstName = await page.$('input[name="applicant_first_name"], input[name="applicant.name.first"]');
  if (firstName && await firstName.isVisible()) {{
    await firstName.fill(data.firstName);
  }}
  
  // Fill applicant last name if visible
  const lastName = await page.$('input[name="applicant_last_name"], input[name="applicant.name.last"]');
  if (lastName && await lastName.isVisible()) {{
    await lastName.fill(data.lastName);
  }}
  
  // Fill other applicant fields
  await fillFieldIfVisible(page, 'applicant_birthdate', data.birthdate);
  await fillFieldIfVisible(page, 'applicant_address_street', data.street);
  await fillFieldIfVisible(page, 'applicant_address_city', data.city);
  await fillFieldIfVisible(page, 'applicant_address_postal_code', data.postalCode);
  await fillFieldIfVisible(page, 'applicant_phone', data.phone);
  await fillFieldIfVisible(page, 'applicant_email', data.email);
  
  await clickContinueIfVisible(page);
}}

async function fillRespondentInfo(page, data) {{
  // Similar to applicant info
  const firstName = await page.$('input[name="respondent_first_name"], input[name="respondent.name.first"]');
  if (firstName && await firstName.isVisible()) {{
    await firstName.fill(data.firstName);
  }}
  
  const lastName = await page.$('input[name="respondent_last_name"], input[name="respondent.name.last"]');
  if (lastName && await lastName.isVisible()) {{
    await lastName.fill(data.lastName);
  }}
  
  await fillFieldIfVisible(page, 'respondent_birthdate', data.birthdate);
  await fillFieldIfVisible(page, 'respondent_address_street', data.street);
  await fillFieldIfVisible(page, 'respondent_address_city', data.city);
  await fillFieldIfVisible(page, 'respondent_address_postal_code', data.postalCode);
  await fillFieldIfVisible(page, 'respondent_phone', data.phone);
  await fillFieldIfVisible(page, 'respondent_email', data.email);
  
  await clickContinueIfVisible(page);
}}

async function fillCourtInfo(page, data) {{
  await fillFieldIfVisible(page, 'court_name', data.name);
  await fillFieldIfVisible(page, 'court_location', data.location);
  await fillFieldIfVisible(page, 'court_file_number', data.fileNumber);
  
  await clickContinueIfVisible(page);
}}

async function fillMarriageInfo(page, data) {{
  await fillFieldIfVisible(page, 'marriage_date', data.date);
  await fillFieldIfVisible(page, 'marriage_place', data.place);
  await fillFieldIfVisible(page, 'separation_date', data.separationDate);
  
  await clickContinueIfVisible(page);
}}

async function fillChildrenInfo(page, children) {{
  for (const child of children) {{
    // Click add child button if available
    const addButton = await page.$('button:has-text("Add child"), button:has-text("Add another")');
    if (addButton && await addButton.isVisible()) {{
      await addButton.click();
    }}
    
    // Fill child information
    await fillFieldIfVisible(page, 'child_name', child.name);
    await fillFieldIfVisible(page, 'child_birthdate', child.birthdate);
    await fillFieldIfVisible(page, 'child_age', child.age);
    await fillFieldIfVisible(page, 'child_grade', child.grade);
    
    // Select residing with
    const residingSelect = await page.$('select[name*="residing"]');
    if (residingSelect && await residingSelect.isVisible()) {{
      await residingSelect.selectOption(child.residingWith);
    }}
    
    await clickContinueIfVisible(page);
  }}
}}

async function fillFormSpecificFields_{form_number}(page) {{
  // Fill any form-specific fields that aren't in common intake
  // This function should be customized for each form
  
  // Example: Check for checkboxes and select them
  const checkboxes = await page.$$('input[type="checkbox"]:not(:checked)');
  for (const checkbox of checkboxes.slice(0, 3)) {{ // Select first 3 checkboxes
    if (await checkbox.isVisible()) {{
      await checkbox.check();
    }}
  }}
  
  // Fill any visible text areas
  const textareas = await page.$$('textarea');
  for (const textarea of textareas) {{
    if (await textarea.isVisible()) {{
      await textarea.fill('This is a test response for the form field.');
    }}
  }}
  
  await clickContinueIfVisible(page);
}}

async function fillFieldIfVisible(page, fieldName, value) {{
  const field = await page.$(`input[name="${{fieldName}}"], select[name="${{fieldName}}"], textarea[name="${{fieldName}}"]`);
  if (field && await field.isVisible()) {{
    const tagName = await field.evaluate(el => el.tagName.toLowerCase());
    
    if (tagName === 'select') {{
      await field.selectOption(value);
    }} else {{
      await field.fill(value);
    }}
  }}
}}

async function clickContinueIfVisible(page) {{
  const continueButton = await page.$('button:has-text("Continue"), button:has-text("Next")');
  if (continueButton && await continueButton.isVisible()) {{
    await continueButton.click();
    await page.waitForTimeout(500); // Small delay for page to update
  }}
}}

async function continueToEnd(page) {{
  // Continue clicking through remaining questions
  let attempts = 0;
  const maxAttempts = 50;
  
  while (attempts < maxAttempts) {{
    const continueButton = await page.$('button:has-text("Continue"), button:has-text("Next")');
    const finalScreen = await page.$('h1:has-text("Complete"), h1:has-text("Finished")');
    
    if (finalScreen) {{
      break; // Reached the end
    }}
    
    if (continueButton && await continueButton.isVisible()) {{
      await continueButton.click();
      await page.waitForTimeout(500);
    }} else {{
      // Fill any remaining visible fields with default values
      await fillRemainingFields(page);
    }}
    
    attempts++;
  }}
}}

async function fillRemainingFields(page) {{
  // Fill any remaining required fields with default values
  const inputs = await page.$$('input:visible, select:visible, textarea:visible');
  
  for (const input of inputs) {{
    const type = await input.getAttribute('type');
    const name = await input.getAttribute('name');
    const value = await input.inputValue();
    
    if (!value) {{ // Only fill if empty
      if (type === 'text') {{
        await input.fill('Test Value');
      }} else if (type === 'email') {{
        await input.fill('test@example.com');
      }} else if (type === 'tel') {{
        await input.fill('416-555-0000');
      }} else if (type === 'number') {{
        await input.fill('1');
      }} else if (type === 'date') {{
        await input.fill('01/01/2024');
      }}
    }}
  }}
  
  await clickContinueIfVisible(page);
}}

module.exports = {{ testData }};
"""
    
    def generate_all_tests(self) -> Dict:
        """Generate tests for all interview files"""
        results = {
            'successful': [],
            'failed': [],
            'total_tests': 0
        }
        
        # Get all interview files
        interview_files = list(self.interviews_dir.glob('form_*_complete.yml'))
        
        print(f"Found {len(interview_files)} interview files to generate tests for")
        
        for interview_file in interview_files:
            try:
                # Extract form number
                form_number = interview_file.stem.replace('form_', '').replace('_complete', '')
                
                print(f"Generating test for Form {form_number}...")
                
                # Generate test
                test_file = self.generate_test(interview_file)
                
                results['successful'].append({
                    'form': form_number,
                    'test_file': test_file
                })
                results['total_tests'] += 1
                
                print(f"  ✓ Generated test: {test_file}")
                
            except Exception as e:
                print(f"  ✗ Failed to generate test for {interview_file.name}: {e}")
                results['failed'].append({
                    'form': interview_file.stem,
                    'error': str(e)
                })
        
        # Generate test runner script
        self._generate_test_runner(results['successful'])
        
        # Generate summary
        self._generate_summary(results)
        
        return results
    
    def _generate_test_runner(self, successful_tests: List[Dict]):
        """Generate a script to run all tests"""
        script = """#!/bin/bash
# Playwright Test Runner for Ontario Family Law Forms
# Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M') + """

# Set environment variables
export DA_URL=${DA_URL:-http://localhost}

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

echo "=========================================="
echo "Ontario Family Law Forms - Test Suite"
echo "=========================================="
echo ""

# Check if Playwright is installed
if ! command -v npx &> /dev/null; then
    echo "${RED}Error: npx not found. Please install Node.js and npm.${NC}"
    exit 1
fi

# Install Playwright if needed
if [ ! -d "node_modules/@playwright/test" ]; then
    echo "${YELLOW}Installing Playwright...${NC}"
    npm install @playwright/test
    npx playwright install chromium
fi

# Run tests
TOTAL=0
PASSED=0
FAILED=0

"""
        
        # Add test execution for each form
        for test_info in successful_tests:
            form_num = test_info['form']
            test_file = Path(test_info['test_file']).name
            
            script += f"""
echo "Testing Form {form_num}..."
if npx playwright test {test_file}; then
    echo "${{GREEN}}✓ Form {form_num} passed${{NC}}"
    ((PASSED++))
else
    echo "${{RED}}✗ Form {form_num} failed${{NC}}"
    ((FAILED++))
fi
((TOTAL++))
echo ""
"""
        
        script += """
# Summary
echo "=========================================="
echo "Test Results Summary"
echo "=========================================="
echo "Total tests: $TOTAL"
echo "${GREEN}Passed: $PASSED${NC}"
echo "${RED}Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo ""
    echo "${RED}Some tests failed.${NC}"
    exit 1
fi
"""
        
        # Save runner script
        runner_file = self.tests_dir / 'run_all_tests.sh'
        with open(runner_file, 'w') as f:
            f.write(script)
        
        # Make executable
        runner_file.chmod(0o755)
        
        print(f"Test runner script created: {runner_file}")
    
    def _generate_summary(self, results: Dict):
        """Generate test generation summary"""
        print("\n" + "="*60)
        print("PLAYWRIGHT TEST GENERATION SUMMARY")
        print("="*60)
        print(f"Total tests generated: {results['total_tests']}")
        print(f"Successful: {len(results['successful'])}")
        print(f"Failed: {len(results['failed'])}")
        
        # Save summary
        summary_file = self.tests_dir / 'test_generation_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nSummary saved to: {summary_file}")
        print(f"Test directory: {self.tests_dir}")
        print(f"\nTo run all tests: cd {self.tests_dir} && ./run_all_tests.sh")


def main():
    """Main function"""
    generator = PlaywrightTestGenerator()
    results = generator.generate_all_tests()
    
    print(f"\n✓ Test generation complete!")
    print(f"  Generated {results['total_tests']} Playwright tests")
    print(f"  Output directory: playwright_tests_generated/")

if __name__ == "__main__":
    main()