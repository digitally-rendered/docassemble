#!/bin/bash

# Ontario Family Law Common Intake - Test Runner Script
# This script sets up and runs the Playwright tests for the common intake interview

set -e  # Exit on error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

echo "=================================================="
echo "Ontario Family Law Common Intake - Test Runner"
echo "=================================================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d 'v' -f 2 | cut -d '.' -f 1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "Error: Node.js version 18+ is required. Current version: $(node -v)"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed. Please install npm first."
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
    echo ""
fi

# Install Playwright browsers if needed
if [ ! -d "$HOME/.cache/ms-playwright" ]; then
    echo "Installing Playwright browsers..."
    npx playwright install
    echo ""
fi

# Set default Docassemble URL if not provided
if [ -z "$DOCASSEMBLE_URL" ]; then
    echo "DOCASSEMBLE_URL not set. Using default: http://localhost"
    export DOCASSEMBLE_URL="http://localhost"
else
    echo "Using DOCASSEMBLE_URL: $DOCASSEMBLE_URL"
fi

echo ""

# Parse command line arguments
TEST_MODE="headless"
TEST_SUITE="all"
BROWSER="chromium"

while [[ $# -gt 0 ]]; do
    case $1 in
        --headed)
            TEST_MODE="headed"
            shift
            ;;
        --debug)
            TEST_MODE="debug"
            shift
            ;;
        --ui)
            TEST_MODE="ui"
            shift
            ;;
        --browser)
            BROWSER="$2"
            shift 2
            ;;
        --suite)
            TEST_SUITE="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --headed        Run tests in headed mode (visible browser)"
            echo "  --debug         Run tests in debug mode"
            echo "  --ui            Open Playwright Test UI"
            echo "  --browser NAME  Run tests in specific browser (chromium, firefox, webkit)"
            echo "  --suite NAME    Run specific test suite (all, common-intake)"
            echo "  --help          Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  DOCASSEMBLE_URL  URL of the Docassemble instance (default: http://localhost)"
            echo ""
            echo "Examples:"
            echo "  $0                    # Run all tests in headless mode"
            echo "  $0 --headed           # Run tests with visible browser"
            echo "  $0 --browser firefox  # Run tests in Firefox"
            echo "  $0 --suite common-intake --headed  # Run common intake tests with visible browser"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Create directories for test results
mkdir -p test-results/{html,artifacts}
mkdir -p screenshots

echo "Test Configuration:"
echo "  Mode: $TEST_MODE"
echo "  Suite: $TEST_SUITE"
echo "  Browser: $BROWSER"
echo ""
echo "Starting tests..."
echo "=================================================="
echo ""

# Run the appropriate test command
case $TEST_MODE in
    headed)
        if [ "$TEST_SUITE" = "common-intake" ]; then
            npm run test:common-intake:headed
        else
            npm run test:headed -- --project=$BROWSER
        fi
        ;;
    debug)
        npx playwright test --debug --project=$BROWSER
        ;;
    ui)
        npx playwright test --ui
        ;;
    *)
        if [ "$TEST_SUITE" = "common-intake" ]; then
            npx playwright test test_common_intake_complete.spec.ts --project=$BROWSER
        else
            npx playwright test --project=$BROWSER
        fi
        ;;
esac

TEST_EXIT_CODE=$?

echo ""
echo "=================================================="

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed successfully!"
else
    echo "❌ Some tests failed. Check the test report for details."
    echo ""
    echo "To view the test report, run:"
    echo "  npm run report"
fi

echo "=================================================="
echo ""

# Open test report if tests failed and not in CI
if [ $TEST_EXIT_CODE -ne 0 ] && [ -z "$CI" ] && [ "$TEST_MODE" != "debug" ] && [ "$TEST_MODE" != "ui" ]; then
    read -p "Would you like to view the test report? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        npm run report
    fi
fi

exit $TEST_EXIT_CODE