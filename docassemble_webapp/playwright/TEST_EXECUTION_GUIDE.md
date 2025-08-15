# Ontario Family Law Wizard - Test Execution Guide

## Prerequisites

1. **Docassemble Instance**: Ensure docassemble is running on http://localhost:8080
2. **Node.js**: Version 14+ installed
3. **Dependencies**: Run `npm install` in the playwright directory

## Quick Start

### Run All Tests
```bash
npm test
```

### Run Specific Test Suites

#### By Test File
```bash
# Common-law scenarios
npx playwright test common-law-pathways.spec.js

# Emergency scenarios  
npx playwright test emergency-pathways.spec.js

# Field validation
npx playwright test field-validation-edge-cases.spec.js

# Married scenarios
npx playwright test married-pathways.spec.js

# Never together scenarios
npx playwright test never-together-pathways.spec.js
```

#### By Test Description (grep)
```bash
# All validation tests
npm test -- --grep "validation"

# All emergency tests
npm test -- --grep "Emergency"

# All common-law tests
npm test -- --grep "Common-Law"

# Specific scenario
npm test -- --grep "should handle custody only case"
```

## Debug Mode

### Run Tests with UI (Headed Mode)
```bash
npm test -- --headed
```

### Run with Playwright Inspector
```bash
npm test -- --debug
```

### Run Single Test with Debug
```bash
npx playwright test --debug --grep "test name here"
```

### Slow Motion Mode (see each action)
```bash
PWDEBUG=1 npm test -- --headed --workers=1
```

## Test Reports

### Generate HTML Report
```bash
npm test -- --reporter=html
npx playwright show-report
```

### Generate JSON Report
```bash
npm test -- --reporter=json > test-results.json
```

### Generate JUnit XML (for CI/CD)
```bash
npm test -- --reporter=junit
```

### Multiple Reporters
```bash
npm test -- --reporter=html,json,list
```

## Troubleshooting

### Tests Timing Out

If tests are timing out, try:

1. **Increase timeout in specific test**:
```javascript
test('my test', async ({ page }) => {
  test.setTimeout(60000); // 60 seconds
  // test code
});
```

2. **Run with fewer workers**:
```bash
npm test -- --workers=1
```

3. **Check docassemble is responsive**:
```bash
curl http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml
```

### Tests Failing on Selectors

1. **Update selectors in WizardPage.js**: The page object model may need updates if the wizard HTML changes

2. **Run in debug mode to see actual HTML**:
```bash
npm test -- --debug --grep "failing test name"
```

3. **Take screenshots for debugging**:
```javascript
await page.screenshot({ path: 'debug.png', fullPage: true });
```

### Flaky Tests

For tests that pass sometimes but fail others:

1. **Add retries**:
```bash
npm test -- --retries=3
```

2. **Run serially instead of parallel**:
```bash
npm test -- --workers=1
```

3. **Add explicit waits**:
```javascript
await page.waitForLoadState('networkidle');
await page.waitForTimeout(1000);
```

## Performance Testing

### Measure Test Execution Time
```bash
time npm test
```

### Run Performance Profiling
```bash
npm test -- --reporter=json > results.json
# Analyze results.json for slow tests
```

### Generate Trace Files
```bash
npm test -- --trace=on
# Traces will be in test-results folder
npx playwright show-trace test-results/[test-name]/trace.zip
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Playwright Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: npm ci
      - run: npx playwright install
      - run: npm test
      - uses: actions/upload-artifact@v2
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
```

### GitLab CI Example
```yaml
playwright-tests:
  image: mcr.microsoft.com/playwright:v1.40.0
  script:
    - npm ci
    - npm test
  artifacts:
    when: always
    paths:
      - playwright-report/
    expire_in: 30 days
```

## Best Practices

### 1. Test Organization
- Group related tests in describe blocks
- Use meaningful test names
- Keep tests independent (no shared state)

### 2. Selectors
- Prefer data-testid attributes when available
- Use text content as fallback
- Avoid fragile CSS selectors

### 3. Waits
- Use explicit waits over arbitrary timeouts
- Wait for specific conditions, not time
- Use `waitForLoadState('networkidle')` for docassemble

### 4. Assertions
- Make assertions specific and meaningful
- Check for both presence and content
- Verify error states explicitly

### 5. Test Data
- Use fixtures for test data
- Keep test data realistic
- Test edge cases and boundaries

## Maintenance

### Update Tests After Wizard Changes
1. Run tests to identify failures
2. Update WizardPage.js for new selectors
3. Update test scenarios for new flows
4. Run full test suite to verify

### Regular Test Review
- Weekly: Review flaky tests
- Monthly: Update test data
- Quarterly: Review test coverage
- Annually: Major test refactoring

## Quick Commands Reference

```bash
# Run all tests
npm test

# Run specific file
npx playwright test [filename]

# Run with grep
npm test -- --grep "pattern"

# Debug mode
npm test -- --debug

# Headed mode
npm test -- --headed

# Generate report
npm test -- --reporter=html

# Show report
npx playwright show-report

# Update snapshots
npm test -- --update-snapshots

# Run single test
npx playwright test -g "test name"

# Run with trace
npm test -- --trace=on

# Show trace
npx playwright show-trace [trace.zip]
```

## Support

For issues or questions:
1. Check the error messages and stack traces
2. Review the TEST_COVERAGE_SUMMARY.md
3. Run tests in debug mode
4. Check docassemble logs
5. Review playwright documentation: https://playwright.dev