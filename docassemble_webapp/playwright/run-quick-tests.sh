#!/bin/bash

echo "Running Quick Test Suite for Ontario Family Law Wizard"
echo "======================================================="
echo ""

# Run basic loading test
echo "1. Testing basic wizard loading..."
npx playwright test --grep "should load wizard without errors" --reporter=line

# Run field validation tests
echo ""
echo "2. Testing field validation..."
npx playwright test --grep "should validate empty required fields" --reporter=line

# Run a simple workflow
echo ""
echo "3. Testing simple divorce workflow..."
npx playwright test --grep "should handle divorce with property scenario" --reporter=line

# Generate summary
echo ""
echo "======================================================="
echo "Quick Test Suite Complete"
echo ""
echo "For full test suite, run: npm test"
echo "For detailed report, run: npm test -- --reporter=html"