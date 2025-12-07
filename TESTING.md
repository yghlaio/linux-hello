# Testing Guide

## Quick Start

Run all tests in an isolated virtual environment:

```bash
cd /path/to/linux-hello
chmod +x run_tests.sh
./run_tests.sh
```

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_mocks.py            # Mock utilities for testing
├── test_config.py           # Configuration module tests
├── test_models.py           # Database model tests
├── test_actions.py          # Action handler tests
├── test_event_hooks.py      # Event hook tests
├── test_face_auth_integration.py  # Face auth integration tests
└── test_cli.py              # CLI command tests
```

## Running Specific Tests

```bash
# Activate test environment
source test_venv/bin/activate

# Run specific test file
pytest tests/test_config.py -v

# Run specific test class
pytest tests/test_models.py::TestDatabase -v

# Run specific test method
pytest tests/test_config.py::TestConfig::test_load_config -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Deactivate
deactivate
```

## Test Categories

### Unit Tests
- `test_config.py` - Configuration management
- `test_models.py` - Database operations
- `test_actions.py` - System actions
- `test_event_hooks.py` - Event handling

### Integration Tests
- `test_face_auth_integration.py` - Face authentication flow
- `test_cli.py` - Command-line interface

## Coverage Report

After running tests, view the coverage report:

```bash
xdg-open test_coverage/index.html
```

## Isolated Testing

All tests run in an isolated `test_venv` virtual environment:
- No system modifications
- No files created outside project directory
- Safe to run repeatedly
