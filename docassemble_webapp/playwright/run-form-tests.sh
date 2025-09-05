#!/bin/bash

# Ontario Family Law Forms - Playwright Test Runner
# This script runs comprehensive tests for Ontario family law Docassemble interviews

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="${BASE_URL:-http://localhost:8080}"
TEST_TIMEOUT="${TEST_TIMEOUT:-300000}" # 5 minutes default
WORKERS="${WORKERS:-2}"
RETRIES="${RETRIES:-1}"

# Test categories
declare -a TEST_CATEGORIES=(
    "form-validation"
    "workflow-paths"
    "table-operations"
    "document-uploads"
    "edge-cases"
    "performance"
)

# Function to print colored output
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check prerequisites
check_prerequisites() {
    print_color "$YELLOW" "Checking prerequisites..."
    
    # Check if npm is installed
    if ! command -v npm &> /dev/null; then
        print_color "$RED" "npm is not installed. Please install Node.js and npm."
        exit 1
    fi
    
    # Check if Playwright is installed
    if [ ! -d "node_modules/@playwright" ]; then
        print_color "$YELLOW" "Installing Playwright dependencies..."
        npm install
        npx playwright install chromium
    fi
    
    # Check if Docassemble is accessible
    if ! curl -s -o /dev/null -w "%{http_code}" "$BASE_URL" | grep -q "200\|302"; then
        print_color "$RED" "Docassemble is not accessible at $BASE_URL"
        print_color "$YELLOW" "Please ensure Docassemble is running and accessible."
        exit 1
    fi
    
    print_color "$GREEN" "Prerequisites check passed!"
}

# Function to run tests for a specific form
run_form_tests() {
    local form_number=$1
    local test_category=$2
    
    print_color "$YELLOW" "Running tests for Form ${form_number} - Category: ${test_category}"
    
    local test_file="tests/form-${form_number}-${test_category}.spec.js"
    
    if [ -f "$test_file" ]; then
        npx playwright test "$test_file" \
            --workers="$WORKERS" \
            --retries="$RETRIES" \
            --timeout="$TEST_TIMEOUT" \
            --reporter=list \
            --reporter=html
        
        if [ $? -eq 0 ]; then
            print_color "$GREEN" "✓ Form ${form_number} - ${test_category} tests passed"
        else
            print_color "$RED" "✗ Form ${form_number} - ${test_category} tests failed"
            return 1
        fi
    else
        print_color "$YELLOW" "No tests found for Form ${form_number} - ${test_category}"
    fi
}

# Function to run comprehensive tests for Form 13
run_form_13_tests() {
    print_color "$YELLOW" "\n=== Running Comprehensive Form 13 Tests ==="
    
    npx playwright test tests/form-13-comprehensive.spec.js \
        --workers="$WORKERS" \
        --retries="$RETRIES" \
        --timeout="$TEST_TIMEOUT" \
        --reporter=list \
        --reporter=html \
        --reporter=json
    
    local test_result=$?
    
    if [ $test_result -eq 0 ]; then
        print_color "$GREEN" "✓ All Form 13 tests passed successfully!"
    else
        print_color "$RED" "✗ Some Form 13 tests failed. Check the report for details."
    fi
    
    return $test_result
}

# Function to run tests for all forms
run_all_form_tests() {
    print_color "$YELLOW" "\n=== Running Tests for All Ontario Family Law Forms ==="
    
    local failed_tests=0
    
    # List of all Ontario family law forms
    declare -a FORM_NUMBERS=(
        "8" "8A" "10" "12" "13" "13.1" "13A" "13B" "13C"
        "14" "14A" "14B" "14C" "15" "15A" "15B" "15C"
        "17" "17A" "17B" "17C" "17D" "17E" "17F"
        "20" "20.1" "20.2" "20A" "20B" "20C" "20D"
        "23" "23A" "23B" "23C" "25" "25A" "25B" "25C" "25D" "25E" "25F"
        "26" "26A" "26B" "26C" "27" "27A" "27B" "27C"
        "28" "28A" "28B" "28C" "29" "30" "30.1" "31" "32"
        "33" "33A" "33B" "33B.1" "33B.2" "33C" "33D" "33E" "33F"
        "34" "34A" "34B" "34C" "34D" "34E" "34F" "34G" "34H" "34I" "34J" "34K" "34L"
        "35.1" "36" "36A" "36B" "37" "37A" "37B" "37C"
    )
    
    for form in "${FORM_NUMBERS[@]}"; do
        for category in "${TEST_CATEGORIES[@]}"; do
            run_form_tests "$form" "$category"
            if [ $? -ne 0 ]; then
                ((failed_tests++))
            fi
        done
    done
    
    if [ $failed_tests -eq 0 ]; then
        print_color "$GREEN" "\n✓ All tests passed successfully!"
    else
        print_color "$RED" "\n✗ $failed_tests test suites failed"
    fi
    
    return $failed_tests
}

# Function to run smoke tests
run_smoke_tests() {
    print_color "$YELLOW" "\n=== Running Smoke Tests ==="
    
    npx playwright test tests/smoke-tests.spec.js \
        --workers=1 \
        --retries=0 \
        --timeout=60000 \
        --reporter=list
    
    if [ $? -eq 0 ]; then
        print_color "$GREEN" "✓ Smoke tests passed"
    else
        print_color "$RED" "✗ Smoke tests failed"
        return 1
    fi
}

# Function to run performance tests
run_performance_tests() {
    print_color "$YELLOW" "\n=== Running Performance Tests ==="
    
    npx playwright test tests/performance.spec.js \
        --workers=1 \
        --retries=0 \
        --timeout="$TEST_TIMEOUT" \
        --reporter=list \
        --reporter=json
    
    if [ $? -eq 0 ]; then
        print_color "$GREEN" "✓ Performance tests passed"
        
        # Parse and display performance metrics
        if [ -f "test-results/results.json" ]; then
            print_color "$YELLOW" "\nPerformance Metrics:"
            # Add JSON parsing logic here if needed
        fi
    else
        print_color "$RED" "✗ Performance tests failed"
        return 1
    fi
}

# Function to generate test report
generate_report() {
    print_color "$YELLOW" "\n=== Generating Test Report ==="
    
    # Open HTML report if tests were run
    if [ -d "playwright-report" ]; then
        print_color "$GREEN" "Test report generated at: playwright-report/index.html"
        
        # Try to open report in browser
        if command -v open &> /dev/null; then
            open playwright-report/index.html
        elif command -v xdg-open &> /dev/null; then
            xdg-open playwright-report/index.html
        else
            print_color "$YELLOW" "Please open playwright-report/index.html in your browser to view the report."
        fi
    fi
}

# Function to clean up test artifacts
cleanup() {
    print_color "$YELLOW" "\nCleaning up test artifacts..."
    
    # Remove old screenshots
    find playwright/screenshots -name "*.png" -mtime +7 -delete 2>/dev/null
    
    # Remove old test results
    find test-results -name "*.json" -mtime +7 -delete 2>/dev/null
    
    print_color "$GREEN" "Cleanup complete!"
}

# Main script execution
main() {
    print_color "$GREEN" "╔════════════════════════════════════════════════════════╗"
    print_color "$GREEN" "║   Ontario Family Law Forms - Playwright Test Suite    ║"
    print_color "$GREEN" "╚════════════════════════════════════════════════════════╝"
    
    # Parse command line arguments
    case "${1:-all}" in
        "form13")
            check_prerequisites
            run_form_13_tests
            ;;
        "smoke")
            check_prerequisites
            run_smoke_tests
            ;;
        "performance")
            check_prerequisites
            run_performance_tests
            ;;
        "all")
            check_prerequisites
            run_all_form_tests
            ;;
        "form")
            if [ -z "$2" ]; then
                print_color "$RED" "Please specify a form number. Usage: $0 form <number>"
                exit 1
            fi
            check_prerequisites
            for category in "${TEST_CATEGORIES[@]}"; do
                run_form_tests "$2" "$category"
            done
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"--help"|"-h")
            echo "Usage: $0 [command] [options]"
            echo ""
            echo "Commands:"
            echo "  form13      - Run comprehensive Form 13 tests"
            echo "  smoke       - Run quick smoke tests"
            echo "  performance - Run performance tests"
            echo "  all         - Run all tests (default)"
            echo "  form <num>  - Run tests for a specific form"
            echo "  cleanup     - Clean up old test artifacts"
            echo "  help        - Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  BASE_URL     - Docassemble base URL (default: http://localhost:8080)"
            echo "  TEST_TIMEOUT - Test timeout in ms (default: 300000)"
            echo "  WORKERS      - Number of parallel workers (default: 2)"
            echo "  RETRIES      - Number of retries for failed tests (default: 1)"
            ;;
        *)
            print_color "$RED" "Unknown command: $1"
            echo "Run '$0 help' for usage information"
            exit 1
            ;;
    esac
    
    # Generate report if tests were run
    if [ "$1" != "cleanup" ] && [ "$1" != "help" ]; then
        generate_report
    fi
    
    print_color "$GREEN" "\n=== Test execution complete ==="
}

# Run main function
main "$@"