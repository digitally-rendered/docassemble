# Ontario Family Law Interview Tests

## Overview

This directory contains comprehensive Playwright tests for the Ontario Family Law Docassemble interviews. The tests cover functionality, validation, navigation, and edge cases for each interview.

## Test Coverage

### Common Intake Interview (`test_common_intake.spec.ts`)

**Scenarios Tested:**
- ✅ Happy path with all fields filled
- ✅ Minimal required fields only
- ✅ Field validation (required fields)
- ✅ Optional field handling
- ✅ Back button navigation
- ✅ Summary screen verification
- ✅ Special characters and complex names
- ✅ Date validation
- ✅ Session persistence
- ✅ Browser refresh handling
- ✅ Keyboard navigation
- ✅ Performance benchmarks

**Edge Cases Tested:**
- Very long names (100+ characters)
- Future and past dates
- Whitespace-only input
- Rapid form submission
- Copy-paste functionality
- Tab navigation
- Multiple back navigations

## Setup Instructions

### Prerequisites

1. Node.js 18+ installed
2. Docassemble instance running (local or remote)
3. Interview deployed to Docassemble

### Installation

```bash
# Navigate to tests directory
cd /Users/draw/development/docassemble/docassemble_webapp/docassemble/webapp/data/questions/ontario-family-law/tests

# Install dependencies
npm install

# Install Playwright browsers
npm run install
```

### Configuration

Set your Docassemble URL in environment variable:

```bash
export DOCASSEMBLE_URL=http://your-docassemble-instance.com
```

Or modify the `baseURL` in `playwright.config.ts`.

## Running Tests

### Run All Tests

```bash
# Run all tests in headless mode
npm test

# Run tests with browser visible
npm run test:headed

# Run tests in debug mode
npm run test:debug

# Run tests with UI mode (interactive)
npm run test:ui
```

### Run Specific Tests

```bash
# Run only common intake tests
npm run test:single

# Run specific test suite
npx playwright test test_common_intake.spec.ts

# Run specific test
npx playwright test -g "should complete interview with all fields filled"
```

### Run Tests by Browser

```bash
# Chrome only
npm run test:chrome

# Firefox only
npm run test:firefox

# WebKit/Safari only
npm run test:webkit

# Mobile browsers
npm run test:mobile
```

### Continuous Integration

```bash
# Run tests in CI mode (with retries)
npm run test:ci
```

## Test Reports

### View HTML Report

After running tests:

```bash
npm run report
```

### Test Artifacts

Test results are saved in:
- `playwright-report/` - HTML report
- `test-results/` - Screenshots, videos, traces
- `test-results/junit.xml` - JUnit XML report
- `test-results/results.json` - JSON report

## Development

### Generate Tests with Codegen

Use Playwright's code generator to create new tests:

```bash
npm run codegen
```

### Watch Mode

Run tests automatically when files change:

```bash
npm run test:watch
```

### Debugging Failed Tests

1. **Screenshots**: Automatically captured on failure in `test-results/`
2. **Videos**: Saved for failed tests in `test-results/`
3. **Traces**: View detailed execution traces:
   ```bash
   npx playwright show-trace test-results/trace.zip
   ```

## Test Structure

### Page Object Pattern

Tests use the Page Object Model for maintainability:

```typescript
class CommonIntakePage {
  // Navigation methods
  async navigateToInterview()
  async clickContinue()
  async clickBack()
  
  // Form interaction methods  
  async fillPersonalInfo(data)
  async clearField(fieldName)
  
  // Assertion methods
  async expectToBeOnIntroScreen()
  async expectValidationError(fieldName)
  async verifySummaryContent(expectedData)
}
```

### Test Organization

```
describe('Feature Area')
  describe('Scenario Group')
    test('Specific test case')
```

## Best Practices

1. **Test Isolation**: Each test runs independently
2. **Data Cleanup**: Tests clean up after themselves
3. **Explicit Waits**: Use proper wait strategies for dynamic content
4. **Meaningful Assertions**: Clear error messages for debugging
5. **Performance Monitoring**: Track load and navigation times

## Troubleshooting

### Common Issues

1. **Timeout Errors**
   - Increase timeout in `playwright.config.ts`
   - Check if Docassemble server is responsive

2. **Element Not Found**
   - Verify selectors match current Docassemble version
   - Check for dynamic content loading

3. **Session Issues**
   - Clear Docassemble cache
   - Ensure clean test environment

### Debug Commands

```bash
# Run with verbose logging
DEBUG=pw:api npm test

# Run single test with trace
npx playwright test --trace on -g "test name"

# Show browser DevTools
npx playwright test --debug
```

## Contributing

### Adding New Tests

1. Create new spec file: `test_[interview_name].spec.ts`
2. Follow existing patterns and helpers
3. Include comprehensive test coverage
4. Update this README with new test details

### Test Checklist

- [ ] Happy path scenarios
- [ ] All validation rules
- [ ] Navigation flows
- [ ] Edge cases
- [ ] Performance benchmarks
- [ ] Accessibility checks
- [ ] Mobile responsiveness

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm ci
      - run: npm run install:deps
      - run: npm run test:ci
      - uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: test-results
          path: test-results/
```

## Support

For issues or questions about the tests, please refer to:
- Playwright documentation: https://playwright.dev
- Docassemble documentation: https://docassemble.org