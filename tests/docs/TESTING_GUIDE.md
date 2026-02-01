# Vnstock Testing Guide

Comprehensive guide for running and maintaining the vnstock test suite.

## Quick Start

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Tests for specific module
pytest tests/unit/explorer/test_vci_quote.py -v

# Tests with specific marker
pytest -m "unit and vci" -v
```

### Generate Coverage Report
```bash
pytest tests/ --cov=vnstock --cov-report=html --cov-report=term-missing
```

## Test Structure

```
tests/
├── unit/                          # Fast, isolated unit tests
│   ├── api/                       # API layer tests
│   ├── explorer/                  # Data source explorer tests
│   │   ├── test_vci_*.py         # VCI data source tests
│   │   ├── test_tcbs_*.py        # TCBS data source tests
│   │   └── test_kbs_*.py         # KBS data source tests
│   └── core/                      # Core utilities tests
├── integration/                   # Integration tests with external services
│   └── test_vnstock_client.py    # End-to-end client tests
├── fixtures/                      # Shared test fixtures
│   └── symbols.py                # Symbol datasets
├── conftest.py                    # Pytest configuration and fixtures
├── conftest_enhancements.py       # Enhanced fixtures for advanced testing
└── TESTING_GUIDE.md              # This file
```

## Test Markers

Available pytest markers for organizing tests:

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (may call external services)
- `@pytest.mark.slow` - Slow tests (>5 seconds)
- `@pytest.mark.api` - API layer tests
- `@pytest.mark.explorer` - Explorer module tests
- `@pytest.mark.vci` - VCI data source specific tests
- `@pytest.mark.tcbs` - TCBS data source specific tests
- `@pytest.mark.kbs` - KBS data source specific tests
- `@pytest.mark.smoke` - Smoke tests (basic functionality)
- `@pytest.mark.regression` - Regression tests for fixed bugs

### Using Markers

```bash
# Run only unit tests
pytest -m unit

# Run unit tests excluding slow tests
pytest -m "unit and not slow"

# Run VCI-specific tests
pytest -m vci

# Run smoke tests
pytest -m smoke
```

## Running Tests Locally

### Prerequisites
```bash
# Install development dependencies
pip install -e ".[test]"

# Install additional testing tools
pip install pytest-xdist pytest-timeout pytest-mock pytest-cov
```

### Run Tests in Parallel
```bash
# Run tests using all available CPU cores
pytest tests/ -n auto

# Run tests using specific number of workers
pytest tests/ -n 4
```

### Run Tests with Timeout
```bash
# Set 30 second timeout per test
pytest tests/ --timeout=30
```

### Run Tests with Verbose Output
```bash
# Very verbose output
pytest tests/ -vv

# Show print statements
pytest tests/ -s

# Show local variables on failure
pytest tests/ -l
```

## Performance Testing

### Measure Test Execution Time
```bash
pytest tests/ --durations=10
```

### Profile Memory Usage
```bash
pytest tests/ --benchmark-only
```

## Coverage Requirements

- **Minimum coverage**: 29% (for unit tests without live integration)
- **Target coverage**: 80%+
- **Critical modules**: 90%+

### View Coverage Report
```bash
# Terminal report
pytest tests/ --cov=vnstock --cov-report=term-missing

# HTML report
pytest tests/ --cov=vnstock --cov-report=html
# Open htmlcov/index.html in browser
```

## Continuous Integration

### GitHub Actions Workflows

1. **test.yml** - Main test suite
   - Runs on: Ubuntu, macOS, Windows
   - Python versions: 3.10, 3.11, 3.12, 3.13
   - Includes: Unit tests, integration tests, coverage

2. **coverage-report.yml** - Coverage reporting
   - Generates coverage reports
   - Uploads to Codecov
   - Comments on PRs with coverage changes

3. **code-quality.yml** - Code quality checks
   - Linting with flake8
   - Code formatting with black
   - Import sorting with isort
   - Type checking with mypy

### Manual Trigger

```bash
# Run GitHub Actions locally (requires act)
act push -j test
act push -j code-quality
```

## Writing Tests

### Basic Unit Test Example
```python
import pytest
from vnstock.api import Quote

@pytest.mark.unit
@pytest.mark.api
def test_quote_initialization():
    """Test Quote class initialization."""
    quote = Quote(symbol='VCB')
    assert quote.symbol == 'VCB'
```

### Test with Fixtures
```python
@pytest.mark.unit
def test_quote_with_mock(mock_http_get, sample_quote_data):
    """Test Quote with mocked HTTP response."""
    quote = Quote(symbol='VCB')
    # Test implementation
    assert quote is not None
```

### Parametrized Tests
```python
@pytest.mark.unit
@pytest.mark.parametrize('symbol', ['VCB', 'ACB', 'TCB'])
def test_quote_multiple_symbols(symbol):
    """Test Quote with multiple symbols."""
    quote = Quote(symbol=symbol)
    assert quote.symbol == symbol
```

### Test with Performance Monitoring
```python
@pytest.mark.unit
def test_quote_performance(measure_perf):
    """Test Quote performance."""
    with measure_perf('test_quote_performance', threshold=1.0):
        quote = Quote(symbol='VCB')
        # Test implementation
```

### Test with Data Validation
```python
@pytest.mark.unit
def test_listing_data_validation(data_validator, mock_listing_data):
    """Test listing data validation."""
    import pandas as pd
    df = pd.DataFrame(mock_listing_data)
    
    schema = {
        'symbol': 'object',
        'name': 'object',
        'exchange': 'object'
    }
    
    errors = data_validator.validate_dataframe_schema(df, schema)
    assert len(errors) == 0
```

## Debugging Tests

### Run Single Test with Debugging
```bash
pytest tests/unit/api/test_quote.py::test_quote_initialization -vv -s
```

### Drop into Debugger on Failure
```bash
pytest tests/ --pdb
```

### Show Local Variables on Failure
```bash
pytest tests/ -l
```

### Capture Output
```bash
pytest tests/ -s  # Show print statements
pytest tests/ --capture=no  # Disable output capture
```

## Test Maintenance

### Update Tests After Code Changes
1. Run affected tests: `pytest tests/unit/explorer/test_vci_quote.py -v`
2. Check coverage: `pytest tests/ --cov=vnstock --cov-report=term-missing`
3. Update fixtures if needed in `conftest.py`
4. Add regression tests for bug fixes

### Common Issues

**Issue**: Tests fail due to network errors
- **Solution**: Use mocks instead of live API calls
- **Example**: Use `mock_http_get` fixture

**Issue**: Tests are slow
- **Solution**: Mark with `@pytest.mark.slow` and run separately
- **Command**: `pytest -m "not slow"`

**Issue**: Coverage is below threshold
- **Solution**: Add tests for uncovered code paths
- **Check**: `pytest --cov=vnstock --cov-report=term-missing`

## Best Practices

1. **Isolation**: Each test should be independent
2. **Clarity**: Test names should clearly describe what they test
3. **Speed**: Unit tests should complete in <1 second
4. **Mocking**: Mock external dependencies (APIs, databases)
5. **Fixtures**: Reuse fixtures instead of duplicating setup code
6. **Markers**: Use markers to organize and filter tests
7. **Coverage**: Aim for >80% code coverage
8. **Documentation**: Document complex test scenarios

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Coverage.py](https://coverage.readthedocs.io/)
- [GitHub Actions](https://docs.github.com/en/actions)
