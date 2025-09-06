#!/bin/bash

# Run Form 8 Interview Tests
# This script runs the Playwright tests for the Form 8 interview

echo "================================================"
echo "Form 8 Interview Test Suite"
echo "================================================"
echo ""

# Set environment variables
export DOCASSEMBLE_URL=${DOCASSEMBLE_URL:-"http://localhost"}
export HEADLESS=${HEADLESS:-false}

echo "Test Configuration:"
echo "  - URL: $DOCASSEMBLE_URL"
echo "  - Mode: $([ "$HEADLESS" = "true" ] && echo "Headless" || echo "Headed")"
echo ""

# Check if Playwright is installed
if ! command -v npx &> /dev/null; then
    echo "❌ Error: npx is not installed. Please install Node.js and npm."
    exit 1
fi

# Check if Playwright is configured
if [ ! -f "playwright.config.js" ]; then
    echo "⚠️ Warning: playwright.config.js not found. Using default configuration."
fi

# Run the tests
echo "Starting Form 8 tests..."
echo "------------------------"

if [ "$1" = "debug" ]; then
    echo "Running in debug mode..."
    npx playwright test tests/ontario-forms/form-08-general.spec.js --debug
elif [ "$1" = "ui" ]; then
    echo "Running with Playwright UI..."
    npx playwright test tests/ontario-forms/form-08-general.spec.js --ui
elif [ "$1" = "headed" ]; then
    echo "Running in headed mode..."
    npx playwright test tests/ontario-forms/form-08-general.spec.js --headed
elif [ "$1" = "specific" ] && [ -n "$2" ]; then
    echo "Running specific test: $2"
    npx playwright test tests/ontario-forms/form-08-general.spec.js -g "$2"
else
    # Run all tests
    npx playwright test tests/ontario-forms/form-08-general.spec.js
fi

# Check test results
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All Form 8 tests passed!"
else
    echo ""
    echo "❌ Some tests failed. Check the output above for details."
    echo ""
    echo "To debug failing tests, run:"
    echo "  ./run-form-8-tests.sh debug"
    echo ""
    echo "To run tests with UI:"
    echo "  ./run-form-8-tests.sh ui"
    echo ""
    echo "To run a specific test:"
    echo "  ./run-form-8-tests.sh specific \"test name\""
fi

echo ""
echo "Test reports available at: playwright-report/"
echo "Run 'npx playwright show-report' to view the HTML report"