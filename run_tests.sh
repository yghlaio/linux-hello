#!/bin/bash
# Test runner script for Face Authentication System
# Runs all tests in an isolated virtual environment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_VENV="$SCRIPT_DIR/test_venv"

echo "=========================================="
echo "Face Authentication System - Test Runner"
echo "=========================================="
echo

# Create test virtual environment if it doesn't exist
if [ ! -d "$TEST_VENV" ]; then
    echo "Creating test virtual environment..."
    python3 -m venv "$TEST_VENV"
    echo "✓ Test virtual environment created"
else
    echo "Using existing test virtual environment"
fi

# Activate virtual environment
source "$TEST_VENV/bin/activate"

# Install/upgrade dependencies
echo
echo "Installing dependencies..."
pip install --upgrade pip -q
pip install -r "$SCRIPT_DIR/requirements.txt" -q
pip install -r "$SCRIPT_DIR/requirements-test.txt" -q
echo "✓ Dependencies installed"

# Run tests
echo
echo "Running tests..."
echo "=========================================="
echo

cd "$SCRIPT_DIR"

# Run pytest with coverage
pytest tests/ \
    --verbose \
    --cov=. \
    --cov-report=term-missing \
    --cov-report=html:test_coverage \
    --ignore=venv \
    --ignore=myenv \
    --ignore=test_venv \
    "$@"

TEST_EXIT_CODE=$?

echo
echo "=========================================="
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed!"
fi
echo "=========================================="
echo
echo "Coverage report generated in: test_coverage/index.html"
echo

# Deactivate virtual environment
deactivate

exit $TEST_EXIT_CODE
