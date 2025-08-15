#!/bin/bash
# Script to run Playwright tests in smaller batches to avoid timeouts

echo "Running Ontario Family Law Wizard Tests in Batches"
echo "=================================================="

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Initialize counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test file and track results
run_test_suite() {
    local test_file=$1
    local suite_name=$2
    
    echo -e "\n${YELLOW}Running $suite_name...${NC}"
    
    # Run the test and capture the exit code
    npx playwright test "$test_file" --timeout=30000 --reporter=list
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ $suite_name passed${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ $suite_name failed${NC}"
        ((FAILED_TESTS++))
    fi
    
    ((TOTAL_TESTS++))
    
    # Wait between test suites to let docassemble recover
    echo "Waiting 5 seconds before next batch..."
    sleep 5
}

# Run each test suite individually
echo "Starting test execution..."

run_test_suite "tests/emergency-pathways.spec.js" "Emergency Pathways"
run_test_suite "tests/married-pathways.spec.js" "Married Pathways"
run_test_suite "tests/common-law-pathways.spec.js" "Common-Law Pathways"
run_test_suite "tests/never-together-pathways.spec.js" "Never Together Pathways"

# Print summary
echo -e "\n=================================================="
echo -e "${YELLOW}Test Summary:${NC}"
echo -e "Total test suites: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"

# Generate HTML report
echo -e "\n${YELLOW}Generating HTML report...${NC}"
npx playwright show-report

# Exit with appropriate code
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}All test suites passed!${NC}"
    exit 0
else
    echo -e "\n${RED}Some test suites failed. Please check the report.${NC}"
    exit 1
fi