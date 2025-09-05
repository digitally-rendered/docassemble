# Ontario Family Law Forms - Playwright Test Suite Guide

## Overview

This comprehensive Playwright test suite provides end-to-end testing for all 46 Ontario family law Docassemble interviews. The test framework uses the Page Object Model pattern for maintainability and includes extensive test coverage for validation, workflows, edge cases, and performance.

## Test Suite Structure

```
playwright/
├── pages/                          # Page Object Models
│   ├── BaseFamilyLawFormPage.js   # Base class with common functionality
│   ├── Form13Page.js               # Form 13 specific page object
│   └── WizardPage.js               # Existing wizard page object
├── tests/                          # Test specifications
│   ├── form-13-comprehensive.spec.js  # Comprehensive Form 13 tests
│   └── [other form tests]
├── fixtures/                       # Test data
│   ├── form-13-test-data.js      # Form 13 test scenarios
│   └── test-data.js               # Common test data
├── utils/                          # Utilities
│   ├── test-helpers.js            # Test helper functions
│   └── interview-helpers.js       # Interview-specific helpers
├── run-form-tests.sh              # Main test runner script
└── playwright.config.js           # Playwright configuration
```

## Key Features

### 1. Page Object Model Architecture

The test suite uses a hierarchical Page Object Model:

- **BaseFamilyLawFormPage**: Base class with common functionality for all forms
- **Form-specific Pages**: Extend the base class with form-specific methods
- **Reusable Components**: Common patterns extracted into helper methods

### 2. Comprehensive Test Coverage

Each form is tested for:

- **Happy Path**: Complete form with valid data
- **Field Validation**: Required fields, format validation, Ontario-specific rules
- **Table Operations**: Add/edit/delete rows in financial tables
- **Document Uploads**: File upload functionality and validation
- **Conditional Logic**: Skip patterns and conditional questions
- **Edge Cases**: Special characters, maximum lengths, boundary values
- **Performance**: Load times and PDF generation speed
- **Navigation**: Browser back/forward, session persistence

### 3. Ontario-Specific Validations

The suite includes specific validations for Ontario requirements:

- Postal code format (K1A 0B1)
- Phone numbers (416-555-0123)
- SIN validation
- LSO numbers for lawyers
- Court file numbers
- Ontario court names and locations

### 4. Data-Driven Testing

Test data is organized into scenarios:

```javascript
const scenarios = {
  minimal: { /* minimum required data */ },
  complete: { /* all fields filled */ },
  highNetWorth: { /* complex financial scenario */ },
  businessOwner: { /* self-employed scenario */ },
  supportRecipient: { /* limited income scenario */ }
};
```

## Running Tests

### Prerequisites

1. Ensure Docassemble is running and accessible
2. Install dependencies:
```bash
cd /Users/draw/development/docassemble/docassemble_webapp/playwright
npm install
npx playwright install chromium
```

### Running Form 13 Tests

```bash
# Run comprehensive Form 13 tests
./run-form-tests.sh form13

# Run with custom configuration
BASE_URL=http://docassemble.example.com ./run-form-tests.sh form13
```

### Running All Tests

```bash
# Run tests for all 46 forms
./run-form-tests.sh all

# Run smoke tests only
./run-form-tests.sh smoke

# Run performance tests
./run-form-tests.sh performance
```

### Running Specific Test Categories

```bash
# Run tests for a specific form
./run-form-tests.sh form 8A

# Run with Playwright UI mode for debugging
npx playwright test --ui

# Run specific test file
npx playwright test tests/form-13-comprehensive.spec.js

# Run with headed browser for debugging
npx playwright test --headed --workers=1
```

## Test Scenarios

### Form 13 - Financial Statement

The Form 13 test suite includes:

1. **Basic Completion Test**
   - Minimal required information
   - Single income source
   - Basic expenses

2. **Complete Financial Disclosure**
   - Multiple income sources
   - Detailed expense categories
   - Assets and debts
   - Tax documents
   - Bank statements

3. **High Net Worth Scenario**
   - Executive compensation
   - Investment income
   - Multiple properties
   - Business ownership
   - Complex asset structure

4. **Business Owner Scenario**
   - Self-employment income
   - Business assets
   - Business expenses
   - Dividend income

5. **Support Recipient Scenario**
   - Limited income
   - Government benefits
   - Support payments
   - Minimal assets

## Writing Tests for New Forms

To add tests for a new form:

1. **Create Page Object**:
```javascript
// pages/Form8Page.js
const { BaseFamilyLawFormPage } = require('./BaseFamilyLawFormPage');

class Form8Page extends BaseFamilyLawFormPage {
  constructor(page) {
    super(page, 'form-8');
  }
  
  // Add form-specific methods
  async fillApplicationDetails(data) {
    // Implementation
  }
}
```

2. **Create Test Specification**:
```javascript
// tests/form-8-comprehensive.spec.js
const { test, expect } = require('@playwright/test');
const { Form8Page } = require('../pages/Form8Page');

test.describe('Form 8 - Application Tests', () => {
  // Test cases
});
```

3. **Add Test Data**:
```javascript
// fixtures/form-8-test-data.js
const testScenarios = {
  minimal: { /* data */ },
  complete: { /* data */ }
};
```

## Test Reports

Tests generate multiple report formats:

- **HTML Report**: Interactive report with screenshots and traces
- **JSON Report**: Machine-readable results for CI/CD
- **JUnit XML**: Integration with test management tools

View reports:
```bash
# Open HTML report
open playwright-report/index.html

# View JSON results
cat test-results/results.json
```

## Debugging Failed Tests

### Using Playwright Inspector

```bash
# Run with inspector
PWDEBUG=1 npx playwright test tests/form-13-comprehensive.spec.js
```

### Screenshots and Videos

Failed tests automatically capture:
- Screenshots at point of failure
- Video recordings (for failed tests)
- Test traces for debugging

Find artifacts in:
- `playwright/screenshots/`
- `test-results/`

### Common Issues and Solutions

1. **Session Timeout**
   - Tests include session handling
   - Automatic retry on timeout

2. **Network Issues**
   - Configured timeouts for slow responses
   - Retry logic for flaky operations

3. **Dynamic Content**
   - Explicit waits for Docassemble processing
   - Network idle detection

## Performance Benchmarks

Expected performance metrics:

- Form load time: < 10 seconds
- Page navigation: < 5 seconds
- PDF generation: < 30 seconds
- Complete form submission: < 5 minutes

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: npm ci
      - run: npx playwright install
      - run: ./run-form-tests.sh all
      - uses: actions/upload-artifact@v2
        if: always()
        with:
          name: test-results
          path: |
            playwright-report/
            test-results/
```

## Extending the Test Suite

### Adding New Validation Rules

```javascript
// In BaseFamilyLawFormPage.js
validateOntarioHealthCard(healthCardNumber) {
  const pattern = /^\d{10}[A-Z]{2}$/;
  return pattern.test(healthCardNumber);
}
```

### Adding New Test Categories

1. Create test specification file
2. Add to TEST_CATEGORIES in run-form-tests.sh
3. Implement test cases

### Custom Test Data Generation

```javascript
// Generate random test data
const testData = generateRandomTestData();

// Or use specific scenario
const testData = getTestData('businessOwner');
```

## Best Practices

1. **Test Independence**: Each test should run independently
2. **Data Cleanup**: Tests should not depend on previous test data
3. **Explicit Waits**: Use explicit waits rather than sleep
4. **Meaningful Assertions**: Clear error messages for failures
5. **Screenshot on Failure**: Automatic screenshots for debugging
6. **Retry Logic**: Handle transient failures gracefully

## Maintenance

### Regular Tasks

- Update test data for law changes
- Add tests for new form versions
- Review and update performance benchmarks
- Clean up old test artifacts: `./run-form-tests.sh cleanup`

### Troubleshooting

Enable verbose logging:
```bash
DEBUG=pw:api npx playwright test
```

Run single test in headed mode:
```bash
npx playwright test --headed --workers=1 -g "test name"
```

## Support

For issues or questions about the test suite:
1. Check test logs in `playwright-report/`
2. Review screenshots in `playwright/screenshots/`
3. Examine test traces for detailed debugging
4. Refer to Playwright documentation: https://playwright.dev