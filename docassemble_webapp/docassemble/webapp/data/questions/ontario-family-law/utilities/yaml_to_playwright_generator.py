#!/usr/bin/env python3
"""
YAML to Playwright Test Generator
Reads Docassemble interview YAML files and generates comprehensive Playwright tests
"""

import yaml
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class YAMLInterviewParser:
    """Parse Docassemble YAML interviews to extract structure and flow"""
    
    def __init__(self, yaml_path: str):
        self.yaml_path = Path(yaml_path)
        self.blocks = []
        self.metadata = {}
        self.questions = []
        self.mandatory_blocks = []
        self.fields = {}
        self.objects = []
        self.events = []
        
    def parse(self) -> Dict:
        """Parse YAML file and extract interview structure"""
        with open(self.yaml_path, 'r') as f:
            content = f.read()
        
        # Split into blocks (separated by ---)
        raw_blocks = content.split('\n---\n')
        
        for block in raw_blocks:
            if not block.strip():
                continue
            
            try:
                parsed = yaml.safe_load(block)
                if parsed:
                    self.blocks.append(parsed)
                    self._process_block(parsed)
            except yaml.YAMLError as e:
                print(f"Warning: Could not parse block: {e}")
        
        return self._build_interview_structure()
    
    def _process_block(self, block: Dict):
        """Process individual YAML blocks"""
        if 'metadata' in block:
            self.metadata = block['metadata']
        
        elif 'question' in block:
            question_data = {
                'question': block.get('question', ''),
                'subquestion': block.get('subquestion', ''),
                'fields': block.get('fields', []),
                'continue_field': block.get('continue button field'),
                'event': block.get('event'),
                'buttons': block.get('buttons', []),
                'validation': block.get('validation code')
            }
            self.questions.append(question_data)
            
            # Extract field information
            for field in block.get('fields', []):
                if isinstance(field, dict):
                    self._extract_field_info(field)
        
        elif 'mandatory' in block and block.get('mandatory') == True:
            if 'code' in block:
                self.mandatory_blocks.append(block['code'])
        
        elif 'objects' in block:
            self.objects.extend(block['objects'])
        
        elif 'event' in block:
            self.events.append({
                'name': block['event'],
                'question': block.get('question', ''),
                'buttons': block.get('buttons', [])
            })
    
    def _extract_field_info(self, field: Dict):
        """Extract field information from question blocks"""
        # Handle different field formats
        if isinstance(field, dict):
            for key, value in field.items():
                if key not in ['datatype', 'required', 'help', 'default', 'validation code', 
                              'min', 'max', 'choices', 'code', 'hide if', 'show if']:
                    # This is the field label: variable pair
                    field_info = {
                        'label': key,
                        'variable': value if isinstance(value, str) else key,
                        'datatype': field.get('datatype', 'text'),
                        'required': field.get('required', False),
                        'validation': field.get('validation code'),
                        'choices': field.get('choices'),
                        'default': field.get('default')
                    }
                    self.fields[field_info['variable']] = field_info
    
    def _build_interview_structure(self) -> Dict:
        """Build complete interview structure"""
        # Extract interview flow from mandatory blocks
        flow = []
        for code in self.mandatory_blocks:
            # Extract variable references that drive the flow
            lines = code.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Remove comments and conditionals
                    if '#' in line:
                        line = line.split('#')[0].strip()
                    if line and not line.startswith('if '):
                        flow.append(line)
        
        return {
            'metadata': self.metadata,
            'questions': self.questions,
            'fields': self.fields,
            'objects': self.objects,
            'events': self.events,
            'flow': flow,
            'file_path': str(self.yaml_path)
        }


class PlaywrightTestGenerator:
    """Generate Playwright tests from parsed interview structure"""
    
    def __init__(self, interview_structure: Dict, form_number: str = None):
        self.structure = interview_structure
        self.form_number = form_number or self._extract_form_number()
        self.test_cases = []
        
    def _extract_form_number(self) -> str:
        """Extract form number from metadata or filename"""
        # Try metadata first
        if self.structure.get('metadata'):
            if 'form_number' in self.structure['metadata']:
                return self.structure['metadata']['form_number']
            
            # Try to extract from title
            title = self.structure['metadata'].get('title', '')
            match = re.search(r'Form\s+(\d+[A-Z]?\.?\d*)', str(title))
            if match:
                return match.group(1)
        
        # Try filename
        file_path = self.structure.get('file_path', '')
        match = re.search(r'form[_\s]?(\d+[A-Z]?\.?\d*)', file_path, re.I)
        if match:
            return match.group(1)
        
        return 'unknown'
    
    def generate_test_suite(self) -> str:
        """Generate complete Playwright test suite"""
        test_content = self._generate_header()
        test_content += self._generate_imports()
        test_content += self._generate_test_data()
        test_content += self._generate_main_test()
        test_content += self._generate_field_validation_tests()
        test_content += self._generate_navigation_tests()
        test_content += self._generate_edge_case_tests()
        
        return test_content
    
    def _generate_header(self) -> str:
        """Generate test file header"""
        title = self.structure.get('metadata', {}).get('title', f'Form {self.form_number}')
        return f"""/**
 * Playwright tests for Ontario Family Law Form {self.form_number}
 * Generated from YAML interview: {self.structure.get('file_path', 'unknown')}
 * Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 * 
 * Title: {title}
 */
"""
    
    def _generate_imports(self) -> str:
        """Generate import statements"""
        return """
const { test, expect } = require('@playwright/test');
const path = require('path');

// Test configuration
test.describe.configure({ mode: 'parallel' });

"""
    
    def _generate_test_data(self) -> str:
        """Generate test data based on fields"""
        test_data = "// Test data\nconst testData = {\n"
        
        for var_name, field_info in self.structure.get('fields', {}).items():
            datatype = field_info.get('datatype', 'text')
            
            if datatype == 'text':
                test_data += f"  '{var_name}': 'Test {field_info.get('label', 'Value')}',\n"
            elif datatype == 'email':
                test_data += f"  '{var_name}': 'test@example.com',\n"
            elif datatype == 'phone':
                test_data += f"  '{var_name}': '416-555-0123',\n"
            elif datatype == 'date':
                test_data += f"  '{var_name}': '2024-01-01',\n"
            elif datatype == 'currency':
                test_data += f"  '{var_name}': '1000.00',\n"
            elif datatype in ['yesno', 'yesnoradio']:
                test_data += f"  '{var_name}': true,\n"
            elif datatype == 'integer':
                test_data += f"  '{var_name}': 2,\n"
            else:
                test_data += f"  '{var_name}': 'Test Value',\n"
        
        test_data += "};\n\n"
        
        # Add invalid test data for validation testing
        test_data += """// Invalid test data for validation testing
const invalidData = {
  email: 'invalid-email',
  phone: '123',
  postal_code: 'INVALID',
  date: '2099-01-01', // Future date
  currency: '-100', // Negative value
};

"""
        return test_data
    
    def _generate_main_test(self) -> str:
        """Generate main happy path test"""
        form_title = self.structure.get('metadata', {}).get('title', f'Form {self.form_number}')
        
        test = f"""test.describe('Form {self.form_number} - Main Flow', () => {{
  test('Complete form with all required fields', async ({{ page }}) => {{
    // Navigate to the interview
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_{self.form_number}.yml');
    
    // Wait for the interview to load
    await page.waitForSelector('.da-page-header', {{ timeout: 10000 }});
    
"""
        
        # Generate field filling based on structure
        for question in self.structure.get('questions', []):
            if question.get('fields'):
                test += f"    // Fill fields for: {question.get('question', 'Question')}\n"
                
                for field in question['fields']:
                    if isinstance(field, dict):
                        for label, variable in field.items():
                            if label not in ['datatype', 'required', 'help', 'default']:
                                test += self._generate_field_fill(variable, field)
                
                # Click continue if there's a continue field
                if question.get('continue_field'):
                    test += "    await page.click('button:has-text(\"Continue\")');\n"
                    test += "    await page.waitForLoadState('networkidle');\n\n"
        
        test += """    // Verify completion
    await expect(page.locator('h1')).toContainText('Complete');
  });
});

"""
        return test
    
    def _generate_field_fill(self, variable: str, field_info: Dict) -> str:
        """Generate code to fill a specific field"""
        datatype = field_info.get('datatype', 'text')
        
        if isinstance(variable, str):
            if datatype in ['text', 'email', 'phone', 'currency']:
                return f"    await page.fill('[name=\"{variable}\"]', testData['{variable}'] || 'Test Value');\n"
            elif datatype == 'date':
                return f"    await page.fill('[name=\"{variable}\"]', testData['{variable}'] || '2024-01-01');\n"
            elif datatype in ['yesno', 'yesnoradio']:
                return f"    await page.click('[name=\"{variable}\"][value=\"True\"]');\n"
            elif datatype == 'radio':
                choices = field_info.get('choices', [])
                if choices:
                    return f"    await page.click('[name=\"{variable}\"][value=\"{choices[0]}\"]');\n"
            
        return f"    // TODO: Fill field {variable} (type: {datatype})\n"
    
    def _generate_field_validation_tests(self) -> str:
        """Generate field validation tests"""
        tests = f"""test.describe('Form {self.form_number} - Field Validation', () => {{
"""
        
        # Email validation
        email_fields = [v for v, f in self.structure.get('fields', {}).items() 
                       if f.get('datatype') == 'email']
        if email_fields:
            tests += """  test('Validate email fields', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_""" + self.form_number + """.yml');
    
    // Test invalid email
    await page.fill('[type="email"]', 'invalid-email');
    await page.click('button:has-text("Continue")');
    
    // Should show validation error
    await expect(page.locator('.da-has-error')).toBeVisible();
  });

"""
        
        # Phone validation
        phone_fields = [v for v, f in self.structure.get('fields', {}).items() 
                       if f.get('datatype') == 'phone']
        if phone_fields:
            tests += """  test('Validate phone number fields', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_""" + self.form_number + """.yml');
    
    // Test invalid phone
    await page.fill('[type="tel"]', '123');
    await page.click('button:has-text("Continue")');
    
    // Should show validation error
    await expect(page.locator('.da-has-error')).toBeVisible();
  });

"""
        
        # Required field validation
        required_fields = [v for v, f in self.structure.get('fields', {}).items() 
                          if f.get('required')]
        if required_fields:
            tests += """  test('Validate required fields', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_""" + self.form_number + """.yml');
    
    // Try to continue without filling required fields
    await page.click('button:has-text("Continue")');
    
    // Should show validation error
    await expect(page.locator('.da-has-error, .da-field-required')).toBeVisible();
  });

"""
        
        tests += "});\n\n"
        return tests
    
    def _generate_navigation_tests(self) -> str:
        """Generate navigation tests"""
        return f"""test.describe('Form {self.form_number} - Navigation', () => {{
  test('Navigate back through questions', async ({{ page }}) => {{
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_{self.form_number}.yml');
    
    // Move forward a few screens
    await page.click('button:has-text("Continue")');
    await page.waitForLoadState('networkidle');
    
    // Test back button
    const backButton = page.locator('button:has-text("Back")');
    if (await backButton.isVisible()) {{
      await backButton.click();
      await page.waitForLoadState('networkidle');
      
      // Verify we went back
      await expect(page).toHaveURL(/.*question.*/);
    }}
  }});
  
  test('Test progress bar updates', async ({{ page }}) => {{
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_{self.form_number}.yml');
    
    const progressBar = page.locator('.progress-bar, [role="progressbar"]');
    if (await progressBar.isVisible()) {{
      const initialProgress = await progressBar.getAttribute('aria-valuenow') || 
                             await progressBar.getAttribute('style');
      
      // Move forward
      await page.click('button:has-text("Continue")');
      await page.waitForLoadState('networkidle');
      
      const newProgress = await progressBar.getAttribute('aria-valuenow') || 
                         await progressBar.getAttribute('style');
      
      // Progress should have increased
      expect(newProgress).not.toBe(initialProgress);
    }}
  }});
}});

"""
    
    def _generate_edge_case_tests(self) -> str:
        """Generate edge case tests"""
        return f"""test.describe('Form {self.form_number} - Edge Cases', () => {{
  test('Handle session timeout gracefully', async ({{ page }}) => {{
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_{self.form_number}.yml');
    
    // Simulate long delay
    await page.waitForTimeout(1000);
    
    // Try to continue
    await page.click('button:has-text("Continue")');
    
    // Should either continue or show appropriate message
    await expect(page).not.toHaveURL(/.*error.*/);
  }});
  
  test('Handle browser refresh', async ({{ page }}) => {{
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_{self.form_number}.yml');
    
    // Fill some data
    const firstInput = page.locator('input[type="text"]').first();
    if (await firstInput.isVisible()) {{
      await firstInput.fill('Test Data');
    }}
    
    // Refresh page
    await page.reload();
    
    // Interview should resume
    await expect(page.locator('.da-page-header')).toBeVisible();
  }});
  
  test('Verify mobile responsiveness', async ({{ page }}) => {{
    // Set mobile viewport
    await page.setViewportSize({{ width: 375, height: 667 }});
    
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_{self.form_number}.yml');
    
    // Check that content is visible and accessible
    await expect(page.locator('.da-page-header')).toBeVisible();
    await expect(page.locator('button:has-text("Continue")')).toBeVisible();
    
    // Verify no horizontal scroll
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = await page.evaluate(() => window.innerWidth);
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth);
  }});
}});

// Performance tests
test.describe('Form {self.form_number} - Performance', () => {{
  test('Measure page load time', async ({{ page }}) => {{
    const startTime = Date.now();
    
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_{self.form_number}.yml');
    await page.waitForSelector('.da-page-header');
    
    const loadTime = Date.now() - startTime;
    
    // Page should load within 3 seconds
    expect(loadTime).toBeLessThan(3000);
    
    console.log(`Form {self.form_number} loaded in ${{loadTime}}ms`);
  }});
}});
"""


def generate_playwright_tests_from_yaml(yaml_path: str, output_dir: str = None) -> str:
    """Main function to generate Playwright tests from YAML"""
    # Parse the YAML interview
    parser = YAMLInterviewParser(yaml_path)
    structure = parser.parse()
    
    # Generate Playwright tests
    generator = PlaywrightTestGenerator(structure)
    test_content = generator.generate_test_suite()
    
    # Save to file if output directory specified
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        form_number = generator.form_number
        test_file = output_path / f'form_{form_number}_test.spec.js'
        
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        print(f"Generated test: {test_file}")
        return str(test_file)
    
    return test_content


def generate_tests_for_all_interviews(interview_dir: str, output_dir: str):
    """Generate Playwright tests for all YAML interviews in a directory"""
    interview_path = Path(interview_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    for yaml_file in interview_path.glob('*.yml'):
        try:
            print(f"Processing: {yaml_file.name}")
            
            # Parse and generate tests
            parser = YAMLInterviewParser(str(yaml_file))
            structure = parser.parse()
            
            generator = PlaywrightTestGenerator(structure)
            test_content = generator.generate_test_suite()
            
            # Save test file
            form_number = generator.form_number
            test_file = output_path / f'form_{form_number}_test.spec.js'
            
            with open(test_file, 'w') as f:
                f.write(test_content)
            
            results.append({
                'yaml_file': yaml_file.name,
                'form_number': form_number,
                'test_file': test_file.name,
                'questions': len(structure.get('questions', [])),
                'fields': len(structure.get('fields', {}))
            })
            
            print(f"  ✓ Generated test for Form {form_number}")
            
        except Exception as e:
            print(f"  ✗ Error processing {yaml_file.name}: {e}")
    
    # Save summary
    summary_file = output_path / 'test_generation_summary.json'
    with open(summary_file, 'w') as f:
        json.dump({
            'generated_at': datetime.now().isoformat(),
            'total_tests': len(results),
            'tests': results
        }, f, indent=2)
    
    print(f"\n✅ Generated {len(results)} Playwright test files")
    print(f"📁 Output: {output_path}")
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--all':
            # Generate tests for all interviews
            interview_dir = sys.argv[2] if len(sys.argv) > 2 else 'generated_interviews'
            output_dir = sys.argv[3] if len(sys.argv) > 3 else 'playwright_tests'
            
            generate_tests_for_all_interviews(interview_dir, output_dir)
        else:
            # Generate test for single YAML file
            yaml_file = sys.argv[1]
            output_dir = sys.argv[2] if len(sys.argv) > 2 else 'playwright_tests'
            
            generate_playwright_tests_from_yaml(yaml_file, output_dir)
    else:
        print("Usage:")
        print("  python yaml_to_playwright_generator.py <yaml_file> [output_dir]")
        print("  python yaml_to_playwright_generator.py --all [interview_dir] [output_dir]")
        print("\nExample:")
        print("  python yaml_to_playwright_generator.py form_8_interview.yml tests/")
        print("  python yaml_to_playwright_generator.py --all generated_interviews/ tests/")