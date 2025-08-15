# Ontario Family Law Forms Wizard - E2E Tests

Comprehensive end-to-end test suite for the Ontario Family Law Forms Wizard using Playwright. This test suite validates all user pathways through the wizard interview and ensures correct form recommendations based on user scenarios.

## Overview

The Ontario Family Law Forms Wizard is a docassemble interview that helps users determine which legal forms they need based on their family law situation. This test suite covers:

- **Emergency pathways** - Cases requiring immediate filing
- **Married scenarios** - Divorce and separation cases
- **Common-law scenarios** - Support, custody, and property cases
- **Never lived together** - Paternity, child support, and custody cases

## Test Structure

```
playwright/
├── tests/                          # Test specification files
│   ├── emergency-pathways.spec.js  # Emergency filing scenarios
│   ├── married-pathways.spec.js    # Married couple scenarios
│   ├── common-law-pathways.spec.js # Common-law partnership scenarios
│   └── never-together-pathways.spec.js # Never lived together scenarios
├── pages/                          # Page Object Model classes
│   └── WizardPage.js               # Main wizard interaction class
├── fixtures/                       # Test data and scenarios
│   └── test-data.js                # Predefined test scenarios
├── utils/                          # Helper functions
│   └── test-helpers.js             # Common test utilities
├── screenshots/                    # Screenshot outputs on failure
├── package.json                    # Node.js dependencies
├── playwright.config.js            # Playwright configuration
└── README.md                       # This file
```

## Prerequisites

1. **Node.js** (version 18 or higher)
2. **Docassemble instance** running locally on port 8080
3. **Ontario Family Law Wizard** deployed at the expected URL

## Installation

1. Navigate to the playwright directory:
```bash
cd playwright
```

2. Install dependencies:
```bash
npm install
```

3. Install Playwright browsers:
```bash
npx playwright install
```

## Configuration

### Environment Variables

Set the following environment variable to customize the base URL:

```bash
export BASE_URL=http://localhost:8080  # Default value
```

### Playwright Configuration

The `playwright.config.js` file includes:
- **Multiple browser support** (Chromium, Firefox, WebKit)
- **Mobile device testing** (Pixel 5, iPhone 12)
- **Screenshot and video capture** on failures
- **Extended timeouts** for docassemble's slower responses
- **Detailed reporting** (HTML, JSON, JUnit formats)

## Running Tests

### Run All Tests
```bash
npm test
```

### Run Tests with Browser UI
```bash
npm run test:ui
```

### Run Tests in Headed Mode (Visible Browser)
```bash
npm run test:headed
```

### Run Specific Test Categories
```bash
npm run test:emergency        # Emergency pathways only
npm run test:married          # Married scenarios only
npm run test:common-law       # Common-law scenarios only
npm run test:never-together   # Never together scenarios only
```

### Debug Mode
```bash
npm run test:debug
```

### View Test Report
```bash
npm run report
```

## Test Scenarios Covered

### Emergency Pathways
- Emergency → Married → Divorce only
- Emergency → Married → Divorce + custody + support
- Emergency → Common-law → Multiple issues
- Emergency → Never together → Child support + custody

**Key Validations:**
- Emergency warning screens appear
- MIP requirement is bypassed
- Immediate filing timeline
- Emergency forms are prioritized
- Crisis resources are provided

### Married Pathways
- Uncontested divorce (with/without children)
- Contested divorce with additional orders
- Separation without divorce
- Various property value scenarios

**Key Validations:**
- Correct form selection (8A vs 8)
- Financial form selection based on property value
- Court jurisdiction (Superior vs Ontario Court)
- Timeline estimates
- MIP requirement handling

### Common-Law Pathways
- Custody only cases
- Support and property division
- Comprehensive multi-issue cases
- Restraining orders

**Key Validations:**
- No divorce options available
- Property rights differences from marriage
- Correct financial form selection
- Court jurisdiction for property claims

### Never Lived Together Pathways
- Child custody and support
- Paternity declarations
- Restraining orders only
- Combined multiple orders

**Key Validations:**
- Limited available orders
- No spousal support or property division
- Paternity form inclusion
- Simplified financial considerations

## Page Object Model

The `WizardPage` class provides methods for:

### Navigation
- `goto()` - Navigate to wizard
- `waitForQuestion(text)` - Wait for specific question
- `clickContinue()` - Click continue and wait

### Question Handling
- `handleIntroduction()` - Complete intro screen
- `handleEmergencyQuestion(boolean)` - Emergency situation
- `handleMipQuestion(status)` - MIP information
- `handleRelationshipStatus(status)` - Relationship type
- `handleOrdersSought(orders)` - Multi-select orders
- `handleDivorceComplexity(complexity)` - Contested/uncontested
- `handleFinancialSituation(data)` - Financial form fields

### Validation
- `getRecommendedForms()` - Extract recommended forms
- `isFormRecommended(name)` - Check specific form
- `getTimeline()` - Get estimated timeline
- `getCourt()` - Get court information
- `checkForErrors()` - Validate no errors present

## Test Data

The `test-data.js` fixture file contains predefined scenarios with:
- User input selections
- Expected form recommendations
- Expected timeline and court
- Financial data templates

Example scenario structure:
```javascript
{
  emergency_situation: false,
  mip_status: 'completed',
  relationship_status: 'married',
  orders: {
    divorce: true,
    custody: false,
    // ... other orders
  },
  financial_data: {
    property_value: 75000,
    support_involved: true,
    // ... other financial data
  },
  expected_forms: ['Form 8A', 'Form 36'],
  expected_timeline: '4-6 months',
  expected_court: 'Superior Court of Justice'
}
```

## Helper Functions

The `test-helpers.js` module provides utilities for:

### Flow Execution
- `runCompleteScenario()` - Execute full wizard flow
- `completeWizardFlow()` - Step through wizard
- `waitForDocassembleLoad()` - Handle slow responses

### Validation
- `validateRecommendedForms()` - Check form recommendations
- `validateTimelineAndCourt()` - Verify timing and jurisdiction
- `validateFinancialFormsPresence()` - Check financial form logic
- `validateCustodyFormsPresence()` - Check custody form logic
- `validateDivorceFormsPresence()` - Check divorce form logic

### Debugging
- `takeDebugScreenshot()` - Capture debugging screenshots
- `validateFormLinks()` - Check form URLs are valid

## Error Handling

Tests include comprehensive error handling for:
- Network timeouts and slow responses
- Missing form elements
- Invalid form recommendations
- Broken links to interviews
- Browser navigation issues

Screenshots are automatically captured on test failures and saved to `screenshots/` directory.

## Continuous Integration

The test suite is configured for CI environments with:
- **Retry logic** for flaky tests (2 retries on CI)
- **Parallel execution** disabled on CI for stability
- **Multiple output formats** (HTML, JSON, JUnit)
- **Headless execution** by default

### GitHub Actions Example
```yaml
- name: Run Playwright Tests
  run: |
    cd playwright
    npm ci
    npx playwright install
    npm test
  env:
    BASE_URL: http://localhost:8080
```

## Troubleshooting

### Common Issues

1. **Timeout Errors**
   - Increase timeout values in playwright.config.js
   - Check docassemble instance is running
   - Verify network connectivity

2. **Element Not Found**
   - Check if wizard YAML has changed
   - Update selectors in WizardPage.js
   - Verify test data matches current wizard structure

3. **Form Recommendations Don't Match**
   - Update expected_forms in test-data.js
   - Check wizard logic has changed
   - Verify financial thresholds are correct

4. **MIP Screen Not Appearing**
   - Verify emergency_situation is set correctly
   - Check wizard's MIP logic
   - Ensure non-emergency path is being followed

### Debug Mode

Use debug mode to step through tests interactively:
```bash
npm run test:debug -- --grep "specific test name"
```

This will:
- Open browser in headed mode
- Pause before each action
- Allow manual inspection of pages
- Show detailed error messages

### Screenshots and Videos

On test failure, Playwright automatically captures:
- **Screenshots** of the failing page
- **Videos** of the test execution (retained on failure)
- **Traces** for detailed debugging (on retry)

Access these in the `test-results/` directory after test execution.

## Contributing

When adding new test scenarios:

1. **Add test data** to `fixtures/test-data.js`
2. **Update Page Object Model** if new elements are needed
3. **Create test cases** following existing patterns
4. **Validate comprehensive coverage** of the new scenario
5. **Update this README** if new functionality is added

### Test Naming Convention
- Use descriptive test names: `should handle uncontested divorce with children`
- Group related tests in `describe` blocks
- Use `test.step()` for logical test phases
- Include scenario context in test names

### Assertion Guidelines
- Use specific assertions: `expect(form).toContain('Form 8A')`
- Validate both positive and negative cases
- Check intermediate states, not just final outcomes
- Include meaningful error messages in assertions

## Support

For issues with the test suite:
1. Check the troubleshooting section above
2. Review test failure screenshots and videos
3. Verify the wizard is functioning correctly in manual testing
4. Check for recent changes to the wizard YAML files

The test suite is designed to be maintainable and comprehensive, providing confidence that all wizard pathways function correctly for users seeking family law forms in Ontario.