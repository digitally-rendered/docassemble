# Ontario Family Law Wizard - Comprehensive Test Suite

This directory contains comprehensive Playwright tests for the enhanced Ontario Family Law Wizard, focusing on testing the new object-oriented architecture with Person, Individual, and Organization objects.

## Test Architecture Overview

The wizard now uses enhanced object types:
- **Person objects** for parties (applicant, respondent) - people in legal proceedings
- **Individual objects** for lawyers - need full personal/professional details  
- **Organization objects** for law firms - business entities
- Comprehensive field validation and error handling

## Test Files

### 1. `ontario-family-law-wizard-comprehensive.spec.js`
**Purpose**: Basic functionality and enhanced object integration tests

**Key Tests**:
- Wizard loads without errors
- Error handling works properly 
- Person objects work for applicant/respondent
- Individual objects work for lawyers
- Organization objects work for law firms
- Field validation functions correctly

### 2. `person-objects-enhanced.spec.js`
**Purpose**: Comprehensive testing of Person objects for party information

**Key Tests**:
- Enhanced Person object data collection (applicant)
- Enhanced Person object data collection (respondent)
- Person object required field validation
- Address field handling in Person objects
- Contact information variations (phone/email formats)
- Multiple party scenario handling

**Features Tested**:
- First/middle/last names, other names/aliases
- Gender, birthdate fields
- Primary and alternative phone/email
- Complete address with unit/suite, province, country
- Postal code validation

### 3. `lawyer-individual-organization.spec.js`
**Purpose**: Testing Individual objects (lawyers) and Organization objects (law firms)

**Key Tests**:
- Individual object data for user lawyer
- Organization object data for law firm
- Both Individual and Organization object integration
- Other party lawyer Individual objects
- Required field validation for lawyers/firms
- No lawyer scenario handling
- Unknown lawyer status handling

**Features Tested**:
- Lawyer professional information (bar number, title)
- Law firm business details (legal name, business number)
- Contact information for both individuals and organizations
- Address handling for professional entities

### 4. `validation-comprehensive.spec.js`
**Purpose**: Comprehensive field validation testing across all object types

**Key Tests**:
- Person object required field validation
- Email format validation
- Phone number format validation
- Postal code format validation (Canadian)
- Date field validation
- Financial form validation
- Numeric field validation
- Checkbox/radio button validation
- Validation error display and user feedback

**Validation Rules Tested**:
- Required field enforcement
- Email format (RFC compliant)
- Canadian phone formats
- Canadian postal code formats (A1A 1A1)
- Date ranges and format validation
- Numeric field constraints

### 5. `workflow-scenarios-comprehensive.spec.js`
**Purpose**: End-to-end workflow testing with different family law scenarios

**Key Workflows**:
- Emergency divorce scenario
- Uncontested divorce (no children)
- Contested divorce (children + support)
- Common-law support and custody
- Never lived together (paternity + support)
- Property division and exclusive possession
- Enforcement and contempt
- Complete workflow with lawyers for both parties

**Each Workflow Tests**:
- Proper form recommendations
- Appropriate financial form triggering
- Correct party information collection
- Lawyer information when applicable
- Court information collection

## Running the Tests

### Quick Start - Run All Tests
```bash
# Make script executable (first time only)
chmod +x run-comprehensive-tests.sh

# Run complete test suite
./run-comprehensive-tests.sh
```

### Individual Test Files
```bash
# Basic functionality and object integration
npx playwright test tests/ontario-family-law-wizard-comprehensive.spec.js

# Person objects (parties)
npx playwright test tests/person-objects-enhanced.spec.js

# Individual/Organization objects (lawyers/firms)
npx playwright test tests/lawyer-individual-organization.spec.js

# Field validation
npx playwright test tests/validation-comprehensive.spec.js

# Workflow scenarios
npx playwright test tests/workflow-scenarios-comprehensive.spec.js
```

### Debug Mode
```bash
# Run with browser visible for debugging
npx playwright test tests/person-objects-enhanced.spec.js --headed

# Run with debug mode (step through)
npx playwright test tests/validation-comprehensive.spec.js --debug

# Generate test report
npx playwright test --reporter=html
npx playwright show-report
```

## Test Data and Scenarios

### Person Object Test Data
- **Applicant**: John David Smith, multiple contact methods, Toronto address
- **Respondent**: Jane Marie Doe, alternative contact info, different address
- **Validation**: Tests empty fields, partial completion, format validation

### Individual Object Test Data (Lawyers)
- **User Lawyer**: Sarah Jane Legal, professional credentials, law firm association
- **Other Lawyer**: Michael Attorney, different firm, contact variations
- **Validation**: Professional fields, bar numbers, credentials

### Organization Object Test Data (Law Firms)
- **Primary Firm**: Smith & Associates Law Firm, full business details
- **Secondary Firm**: Big Law Associates, different structure
- **Validation**: Business registration, professional addresses

### Workflow Test Scenarios
1. **Emergency Cases**: Urgent filing requirements, expedited process
2. **Simple Divorce**: Uncontested, no children, minimal complexity
3. **Complex Divorce**: Multiple issues, financial forms, comprehensive data
4. **Common-Law**: Support and custody without marriage
5. **Never Together**: Paternity establishment, support determination
6. **Property Cases**: Division of assets, exclusive possession
7. **Enforcement**: Contempt, compliance, existing orders

## Expected Test Results

### Success Indicators
- ✅ All object types collect data properly
- ✅ Field validation works consistently
- ✅ Error handling is robust
- ✅ Workflows complete successfully
- ✅ Appropriate forms are recommended

### Common Issues to Watch For
- ❌ Object field name mismatches (base64 encoding issues)
- ❌ Validation not triggering properly
- ❌ Workflow navigation breaking at transitions
- ❌ Error handling not catching all scenarios
- ❌ Form recommendations not matching case complexity

## Debugging Failed Tests

### 1. Check Browser Console
```bash
# Run with console output visible
npx playwright test tests/person-objects-enhanced.spec.js --headed
```

### 2. Screenshot on Failure
Tests automatically take screenshots on failure:
```
playwright/test-results/[test-name]/test-failed-1.png
```

### 3. Test Trace
Generate detailed trace for analysis:
```bash
npx playwright test tests/validation-comprehensive.spec.js --trace on
npx playwright show-trace test-results/[test-name]/trace.zip
```

### 4. Step-by-Step Debug
```bash
npx playwright test tests/lawyer-individual-organization.spec.js --debug
```

## Test Environment Requirements

### Prerequisites
- Node.js 18+ installed
- Playwright installed (`npm install @playwright/test`)
- DocAssemble server running on `localhost:8080`
- Ontario Family Law Wizard deployed and accessible

### Server Setup
```bash
# Ensure DocAssemble server is running
# Wizard should be accessible at:
# http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml
```

### Configuration
Tests are configured for:
- **Target**: `localhost:8080`
- **Timeout**: 30 seconds per test
- **Retries**: 1 retry on failure
- **Browser**: Chromium (can be changed in playwright.config.js)

## Maintenance and Updates

### When to Update Tests
- Object structure changes in the wizard
- New field validation rules added
- Workflow logic modifications
- New forms or scenarios added

### Adding New Tests
1. Follow existing test patterns
2. Use helper functions for common operations
3. Include both positive and negative test cases
4. Add appropriate console logging
5. Update this README with new test descriptions

### Test Performance
- Full suite runtime: ~15-20 minutes
- Individual files: ~2-5 minutes each
- Optimize by running specific test files during development

## Integration with CI/CD

These tests can be integrated into continuous integration:

```yaml
# Example GitHub Actions
- name: Install Playwright
  run: |
    npm install
    npx playwright install
    
- name: Run Comprehensive Tests
  run: ./run-comprehensive-tests.sh
```

## Troubleshooting

### Common Issues
1. **Wizard not loading**: Check DocAssemble server status
2. **Object field errors**: Verify field names in wizard YAML
3. **Validation not working**: Check validation function imports
4. **Timeout issues**: Increase wait times for slower responses

### Support Resources
- Playwright documentation: https://playwright.dev/
- DocAssemble documentation: https://docassemble.org/
- Test logs: Check console output for detailed error information