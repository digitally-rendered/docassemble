#!/bin/bash

# Ontario Family Law - Common Intake Enhanced with Validation Tests
# This script runs comprehensive Playwright tests for the common_intake_enhanced_with_validation.yml interview

set -e

echo "🏛️  Ontario Family Law - Common Intake Enhanced Tests"
echo "=================================================="
echo ""

# Check if we're in the right directory
if [ ! -f "test_common_intake_validation_comprehensive.spec.ts" ]; then
    echo "❌ Error: test_common_intake_validation_comprehensive.spec.ts not found"
    echo "Please run this script from the tests directory"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if Playwright is installed
if [ ! -d "node_modules/@playwright" ]; then
    echo "🎭 Installing Playwright..."
    npm install @playwright/test
    npx playwright install
fi

# Function to run tests with error handling
run_test() {
    local test_name="$1"
    local test_pattern="$2"
    echo "🧪 Running: $test_name"
    echo "----------------------------------------"
    
    if npx playwright test test_common_intake_validation_comprehensive.spec.ts -g "$test_pattern" --reporter=line; then
        echo "✅ $test_name - PASSED"
    else
        echo "❌ $test_name - FAILED"
        FAILED_TESTS+=("$test_name")
    fi
    echo ""
}

# Array to track failed tests
FAILED_TESTS=()

echo "🚀 Starting Test Suite..."
echo ""

# Critical tests first
echo "🔥 CRITICAL TESTS"
echo "=================="
run_test "Interview Load Test" "interview loads without errors"
run_test "Divorce Flow (Core)" "divorce without children reaches summary"

echo "📊 MAJOR FLOW TESTS"
echo "==================="
run_test "Custody with Children" "custody case with children table interface"
run_test "Emergency Restraining Order" "emergency restraining order flow"
run_test "Property Division with Lawyers" "property division with lawyers flow"

echo "🔍 VALIDATION TESTS"
echo "==================="
run_test "Conditional Fields" "conditional fields display correctly"
run_test "Field Validation" "field validation works correctly"

echo "🧸 CHILDREN TABLE TESTS"
echo "======================="
run_test "Children Delete Function" "children table delete works correctly"

echo ""
echo "📈 SUMMARY REPORT"
echo "================="

if [ ${#FAILED_TESTS[@]} -eq 0 ]; then
    echo "🎉 ALL TESTS PASSED!"
    echo ""
    echo "✅ Interview loads successfully"
    echo "✅ All major flows complete to summary"
    echo "✅ Children table interface works correctly"
    echo "✅ Conditional fields display properly"
    echo "✅ Validation rules enforce correctly"
    echo ""
    echo "🚀 Ready for production!"
else
    echo "⚠️  SOME TESTS FAILED"
    echo ""
    echo "Failed tests:"
    for test in "${FAILED_TESTS[@]}"; do
        echo "  ❌ $test"
    done
    echo ""
    echo "🔧 Please review failures and fix before deployment"
    exit 1
fi

echo ""
echo "📁 Test artifacts saved to:"
echo "  - Screenshots: test-results/"
echo "  - Videos: test-results/" 
echo "  - HTML Report: Run 'npx playwright show-report' to view"

echo ""
echo "🎭 To run individual tests:"
echo "  npx playwright test test_common_intake_validation_comprehensive.spec.ts -g 'test name'"
echo ""
echo "To debug with UI:"
echo "  npx playwright test test_common_intake_validation_comprehensive.spec.ts --ui"

echo ""
echo "✨ Test run completed!"