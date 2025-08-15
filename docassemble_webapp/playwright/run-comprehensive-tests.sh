#!/bin/bash

# Ontario Family Law Wizard - Comprehensive Test Suite Runner
# Run this script to execute all comprehensive tests for the enhanced wizard

echo "======================================================"
echo "Ontario Family Law Wizard - Comprehensive Test Suite"
echo "======================================================"
echo ""

# Check if playwright is installed
if ! command -v npx &> /dev/null; then
    echo "❌ npm/npx not found. Please install Node.js and npm first."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ package.json not found. Please run this script from the playwright directory."
    exit 1
fi

# Install dependencies if needed
echo "📦 Checking Playwright installation..."
if [ ! -d "node_modules/@playwright" ]; then
    echo "Installing Playwright..."
    npm install
    npx playwright install
fi

echo ""
echo "🧪 Running Comprehensive Test Suite..."
echo "======================================"
echo ""

# Test 1: Basic Loading and Error Handling
echo "1️⃣ Testing basic wizard loading and error handling..."
npx playwright test tests/ontario-family-law-wizard-comprehensive.spec.js --reporter=line
test1_result=$?

echo ""
echo "2️⃣ Testing Person objects (applicant/respondent parties)..."
npx playwright test tests/person-objects-enhanced.spec.js --reporter=line
test2_result=$?

echo ""
echo "3️⃣ Testing Individual objects (lawyers) and Organization objects (law firms)..."
npx playwright test tests/lawyer-individual-organization.spec.js --reporter=line
test3_result=$?

echo ""
echo "4️⃣ Testing comprehensive field validation..."
npx playwright test tests/validation-comprehensive.spec.js --reporter=line
test4_result=$?

echo ""
echo "5️⃣ Testing workflow scenarios..."
npx playwright test tests/workflow-scenarios-comprehensive.spec.js --reporter=line
test5_result=$?

echo ""
echo "======================================================"
echo "📊 TEST SUITE SUMMARY"
echo "======================================================"

total_tests=5
passed_tests=0

if [ $test1_result -eq 0 ]; then
    echo "✅ Basic Loading & Error Handling: PASSED"
    ((passed_tests++))
else
    echo "❌ Basic Loading & Error Handling: FAILED"
fi

if [ $test2_result -eq 0 ]; then
    echo "✅ Person Objects: PASSED"
    ((passed_tests++))
else
    echo "❌ Person Objects: FAILED"
fi

if [ $test3_result -eq 0 ]; then
    echo "✅ Individual & Organization Objects: PASSED"
    ((passed_tests++))
else
    echo "❌ Individual & Organization Objects: FAILED"
fi

if [ $test4_result -eq 0 ]; then
    echo "✅ Field Validation: PASSED"
    ((passed_tests++))
else
    echo "❌ Field Validation: FAILED"
fi

if [ $test5_result -eq 0 ]; then
    echo "✅ Workflow Scenarios: PASSED"
    ((passed_tests++))
else
    echo "❌ Workflow Scenarios: FAILED"
fi

echo ""
echo "📈 Results: $passed_tests/$total_tests test suites passed"

if [ $passed_tests -eq $total_tests ]; then
    echo ""
    echo "🎉 ALL TESTS PASSED! The Ontario Family Law Wizard is working correctly with:"
    echo "   • Enhanced Person objects for parties"
    echo "   • Individual objects for lawyers" 
    echo "   • Organization objects for law firms"
    echo "   • Comprehensive field validation"
    echo "   • All workflow scenarios"
    echo ""
    exit 0
else
    echo ""
    echo "⚠️  Some tests failed. Check the output above for details."
    echo "   Run individual test files for more detailed debugging."
    echo ""
    echo "Individual test commands:"
    echo "  npx playwright test tests/ontario-family-law-wizard-comprehensive.spec.js --headed"
    echo "  npx playwright test tests/person-objects-enhanced.spec.js --headed"
    echo "  npx playwright test tests/lawyer-individual-organization.spec.js --headed"
    echo "  npx playwright test tests/validation-comprehensive.spec.js --headed"
    echo "  npx playwright test tests/workflow-scenarios-comprehensive.spec.js --headed"
    echo ""
    exit 1
fi