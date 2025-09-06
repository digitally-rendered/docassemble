#!/bin/bash
# Playwright Test Runner for Ontario Family Law Forms
# Generated: 2025-09-05 15:03

# Set environment variables
export DA_URL=${DA_URL:-http://localhost}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Ontario Family Law Forms - Test Suite"
echo "=========================================="
echo ""

# Check if Playwright is installed
if ! command -v npx &> /dev/null; then
    echo "${RED}Error: npx not found. Please install Node.js and npm.${NC}"
    exit 1
fi

# Install Playwright if needed
if [ ! -d "node_modules/@playwright/test" ]; then
    echo "${YELLOW}Installing Playwright...${NC}"
    npm install @playwright/test
    npx playwright install chromium
fi

# Run tests
TOTAL=0
PASSED=0
FAILED=0


echo "Testing Form 25F..."
if npx playwright test test_form_25F.spec.js; then
    echo "${GREEN}✓ Form 25F passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 25F failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 10..."
if npx playwright test test_form_10.spec.js; then
    echo "${GREEN}✓ Form 10 passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 10 failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 36A..."
if npx playwright test test_form_36A.spec.js; then
    echo "${GREEN}✓ Form 36A passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 36A failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 26..."
if npx playwright test test_form_26.spec.js; then
    echo "${GREEN}✓ Form 26 passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 26 failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 8A..."
if npx playwright test test_form_8A.spec.js; then
    echo "${GREEN}✓ Form 8A passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 8A failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 34..."
if npx playwright test test_form_34.spec.js; then
    echo "${GREEN}✓ Form 34 passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 34 failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 43..."
if npx playwright test test_form_43.spec.js; then
    echo "${GREEN}✓ Form 43 passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 43 failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 37B..."
if npx playwright test test_form_37B.spec.js; then
    echo "${GREEN}✓ Form 37B passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 37B failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 43B..."
if npx playwright test test_form_43B.spec.js; then
    echo "${GREEN}✓ Form 43B passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 43B failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 27..."
if npx playwright test test_form_27.spec.js; then
    echo "${GREEN}✓ Form 27 passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 27 failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 14C..."
if npx playwright test test_form_14C.spec.js; then
    echo "${GREEN}✓ Form 14C passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 14C failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 34I..."
if npx playwright test test_form_34I.spec.js; then
    echo "${GREEN}✓ Form 34I passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 34I failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 13B..."
if npx playwright test test_form_13B.spec.js; then
    echo "${GREEN}✓ Form 13B passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 13B failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 29B..."
if npx playwright test test_form_29B.spec.js; then
    echo "${GREEN}✓ Form 29B passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 29B failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 14B..."
if npx playwright test test_form_14B.spec.js; then
    echo "${GREEN}✓ Form 14B passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 14B failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 17C..."
if npx playwright test test_form_17C.spec.js; then
    echo "${GREEN}✓ Form 17C passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 17C failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 13C..."
if npx playwright test test_form_13C.spec.js; then
    echo "${GREEN}✓ Form 13C passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 13C failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 6C..."
if npx playwright test test_form_6C.spec.js; then
    echo "${GREEN}✓ Form 6C passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 6C failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 15B..."
if npx playwright test test_form_15B.spec.js; then
    echo "${GREEN}✓ Form 15B passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 15B failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 29..."
if npx playwright test test_form_29.spec.js; then
    echo "${GREEN}✓ Form 29 passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 29 failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 17F..."
if npx playwright test test_form_17F.spec.js; then
    echo "${GREEN}✓ Form 17F passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 17F failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 17A..."
if npx playwright test test_form_17A.spec.js; then
    echo "${GREEN}✓ Form 17A passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 17A failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 13A..."
if npx playwright test test_form_13A.spec.js; then
    echo "${GREEN}✓ Form 13A passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 13A failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 28..."
if npx playwright test test_form_28.spec.js; then
    echo "${GREEN}✓ Form 28 passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 28 failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 29A..."
if npx playwright test test_form_29A.spec.js; then
    echo "${GREEN}✓ Form 29A passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 29A failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 15C..."
if npx playwright test test_form_15C.spec.js; then
    echo "${GREEN}✓ Form 15C passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 15C failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 6B..."
if npx playwright test test_form_6B.spec.js; then
    echo "${GREEN}✓ Form 6B passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 6B failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 8..."
if npx playwright test test_form_8.spec.js; then
    echo "${GREEN}✓ Form 8 passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 8 failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 13..."
if npx playwright test test_form_13.spec.js; then
    echo "${GREEN}✓ Form 13 passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 13 failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 34F..."
if npx playwright test test_form_34F.spec.js; then
    echo "${GREEN}✓ Form 34F passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 34F failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 34A..."
if npx playwright test test_form_34A.spec.js; then
    echo "${GREEN}✓ Form 34A passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 34A failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 37..."
if npx playwright test test_form_37.spec.js; then
    echo "${GREEN}✓ Form 37 passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 37 failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 30..."
if npx playwright test test_form_30.spec.js; then
    echo "${GREEN}✓ Form 30 passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 30 failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 25..."
if npx playwright test test_form_25.spec.js; then
    echo "${GREEN}✓ Form 25 passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 25 failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 8B..."
if npx playwright test test_form_8B.spec.js; then
    echo "${GREEN}✓ Form 8B passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 8B failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 37A..."
if npx playwright test test_form_37A.spec.js; then
    echo "${GREEN}✓ Form 37A passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 37A failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 4..."
if npx playwright test test_form_4.spec.js; then
    echo "${GREEN}✓ Form 4 passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 4 failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 25C..."
if npx playwright test test_form_25C.spec.js; then
    echo "${GREEN}✓ Form 25C passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 25C failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 33F..."
if npx playwright test test_form_33F.spec.js; then
    echo "${GREEN}✓ Form 33F passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 33F failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 15..."
if npx playwright test test_form_15.spec.js; then
    echo "${GREEN}✓ Form 15 passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 15 failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 8D..."
if npx playwright test test_form_8D.spec.js; then
    echo "${GREEN}✓ Form 8D passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 8D failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 43A..."
if npx playwright test test_form_43A.spec.js; then
    echo "${GREEN}✓ Form 43A passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 43A failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 34G..."
if npx playwright test test_form_34G.spec.js; then
    echo "${GREEN}✓ Form 34G passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 34G failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

echo "Testing Form 36..."
if npx playwright test test_form_36.spec.js; then
    echo "${GREEN}✓ Form 36 passed${NC}"
    ((PASSED++))
else
    echo "${RED}✗ Form 36 failed${NC}"
    ((FAILED++))
fi
((TOTAL++))
echo ""

# Summary
echo "=========================================="
echo "Test Results Summary"
echo "=========================================="
echo "Total tests: $TOTAL"
echo "${GREEN}Passed: $PASSED${NC}"
echo "${RED}Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo ""
    echo "${RED}Some tests failed.${NC}"
    exit 1
fi
