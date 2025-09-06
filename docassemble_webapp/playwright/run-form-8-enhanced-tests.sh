#!/bin/bash

# Script to run Form 8 Enhanced Interview tests
# This script tests the enhanced Form 8 interview with proper validation

echo "================================================"
echo "Form 8 Enhanced Interview Test Suite"
echo "================================================"
echo ""

# Set environment variables
export DOCASSEMBLE_URL=${DOCASSEMBLE_URL:-"http://localhost"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Testing against: $DOCASSEMBLE_URL"
echo ""

# Check if playwright is installed
if ! command -v npx &> /dev/null; then
    echo -e "${RED}Error: npx not found. Please install Node.js and npm.${NC}"
    exit 1
fi

# Check if Playwright is installed
if ! npx playwright --version &> /dev/null 2>&1; then
    echo -e "${YELLOW}Playwright not installed. Installing...${NC}"
    npm install -D @playwright/test
    npx playwright install
fi

# Function to run tests with proper error handling
run_test() {
    local test_name=$1
    local test_file=$2
    
    echo -e "${YELLOW}Running: $test_name${NC}"
    
    if npx playwright test "$test_file" --reporter=list; then
        echo -e "${GREEN}✓ $test_name passed${NC}"
        return 0
    else
        echo -e "${RED}✗ $test_name failed${NC}"
        return 1
    fi
}

# Run the enhanced Form 8 tests
echo "Starting Form 8 Enhanced Interview tests..."
echo "----------------------------------------"

# Run all tests
run_test "Form 8 Enhanced - All Tests" "tests/ontario-forms/form-08-enhanced.spec.js"

# Run specific test suites if needed
if [ "$1" == "--detailed" ]; then
    echo ""
    echo "Running detailed test breakdown..."
    echo "----------------------------------------"
    
    npx playwright test tests/ontario-forms/form-08-enhanced.spec.js \
        --grep "Interview Loading" \
        --reporter=list
    
    npx playwright test tests/ontario-forms/form-08-enhanced.spec.js \
        --grep "Court Information" \
        --reporter=list
    
    npx playwright test tests/ontario-forms/form-08-enhanced.spec.js \
        --grep "Ontario-Specific Validations" \
        --reporter=list
    
    npx playwright test tests/ontario-forms/form-08-enhanced.spec.js \
        --grep "Complete Interview Flow" \
        --reporter=list
fi

# Generate HTML report if tests were run
if [ -d "test-results" ]; then
    echo ""
    echo "Generating HTML report..."
    npx playwright show-report
fi

echo ""
echo "================================================"
echo "Test run complete!"
echo "================================================"

# Exit with appropriate code
if [ $? -eq 0 ]; then
    echo -e "${GREEN}All tests passed successfully!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Check the report for details.${NC}"
    exit 1
fi