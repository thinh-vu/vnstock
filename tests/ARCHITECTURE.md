# Vnstock Test Architecture & Quick Guide

**For AI: This guide helps you understand, modify, and extend vnstock tests efficiently.**

---

## 📁 Directory Structure (Clean & Organized)

```
tests/
├── conftest.py                      # 🔑 Shared fixtures, mocks, config
├── fixtures/
│   ├── __init__.py
│   └── symbols.py                   # Real symbols from VCI API (HOSE/HNX/UPCOM)
│
├── unit/                            # Fast unit tests (~4 sec)
│   ├── api/
│   │   ├── test_quote.py            # Quote adapter (VCI, TCBS, MSN)
│   │   └── test_listing.py          # Listing adapter (VCI, MSN)
│   │
│   ├── core/
│   │   └── test_proxy_manager.py    # ProxyManager utility (18 tests)
│   │
│   └── explorer/
│       ├── test_vci_quote_comprehensive.py    # VCI Quote variants
│       ├── test_vci_listing_comprehensive.py  # VCI Listing methods
│       ├── test_vci_company_finance_comprehensive.py
│       ├── test_tcbs_quote_comprehensive.py   # TCBS Quote
│       ├── test_tcbs_screener_trading_comprehensive.py
│       └── test_vci_quote_with_proxy.py       # Proxy integration
│
├── integration/                     # Real API calls (skip by default)
│   └── test_vnstock_client.py       # End-to-end workflows
│
└── report/
    ├── coverage_html/               # Generated HTML coverage report
    ├── coverage.xml                 # Coverage for CI/CD
    └── junit-results.xml            # JUnit format for CI systems
```

---

## 🧩 Key Components Explained

### 1️⃣ **conftest.py** - Test Configuration Hub

**What it contains**:
```python
# HTTP Response Mocking
MockResponse          # Fake HTTP response object
mock_response_factory # Create customizable mock responses
mock_http_get/post    # Patch requests.get/post

# DataFrame Validators
df_validators         # Dict of validation helpers for assertions

# Logging Control
disable_logging       # Auto-disable logging in all tests

# Sample Data
sample_data_fixtures  # Test data generators
```

**How to use**:
```python
def test_quote(mock_response_factory):
    # Create mock response
    mock = mock_response_factory(
        json_data={'close': 100.0},
        status_code=200
    )
    
    # Your test code
    assert mock.status_code == 200
```

---

### 2️⃣ **fixtures/symbols.py** - Real Symbol Data

**What it provides**:
```python
real_symbols_dataset()        # Fetch from live VCI API
  ├── 'hose': 300+ symbols
  ├── 'hnx': 150+ symbols
  └── 'upcom': 100+ symbols

random_hose_symbols          # 100 random HOSE stocks
random_hnx_symbols           # 100 random HNX stocks
random_upcom_symbols         # 100 random UPCOM stocks

diverse_test_symbols         # 30 symbols (10 each exchange)
all_test_symbols             # All above combined

test_intervals               # ['1m', '5m', ..., '1M']
test_date_ranges             # Various date range fixtures
```

**How to use**:
```python
def test_quote(random_hose_symbols):
    symbol = random_hose_symbols[0]
    # Test with real symbol
    quote = Quote(symbol=symbol)
```

---

### 3️⃣ **examples/** - Runnable Demo Code

**What it contains**:
```
examples/
├── __init__.py
└── proxy_examples.py        # 8 working ProxyManager examples
```

**proxy_examples.py includes**:
- Example 1: Fetch free proxies from proxyscrape
- Example 2: Test proxies for connectivity
- Example 3: Get fastest proxy
- Example 4: Create custom proxy objects
- Example 5: Integrate proxy with VCI Quote
- Example 6: Proxy rotation for batch processing
- Example 7: Complete workflow (fetch → test → select)
- Example 8: Error handling & fallback

**How to run**:
```bash
python -m tests.examples.proxy_examples
```

**Why here and not in core utils**:
✅ These are demo/tutorial code, not core utilities
✅ Located in tests for easy discovery by developers
✅ Referenced by PROXY_GUIDE.md in docs/

---

### 4️⃣ **Test Files Organization**

#### **API Layer** (`test_api_*`)
- Purpose: Test adapter pattern & parameter filtering
- Scope: Small, fast unit tests
- Mocking: All external calls mocked

#### **Explorer Layer** (`test_vci_*, test_tcbs_*`)
- Purpose: Comprehensive parameter testing
- Scope: All intervals, periods, languages, filters
- Markers: `@pytest.mark.integration` (real API calls)

#### **Proxy Integration** (`test_vci_quote_with_proxy.py`)
- Purpose: ProxyManager + VCI Quote integration
- Scope: 8 tests covering proxy patterns
- Status: ✅ 8/8 passing

---

## 🚀 Quick Command Reference

### Run Tests

```bash
# Unit tests only (fast, ~4 sec)
pytest tests/unit/ -m "not integration" -q

# With verbose output
pytest tests/unit/ -m "not integration" -v

# ProxyManager tests only
pytest tests/unit/core/test_proxy_manager.py -v

# VCI Quote tests
pytest tests/unit/explorer/test_vci_quote_comprehensive.py -v

# All tests (includes real API calls)
pytest tests/unit/ -v

# Quick smoke tests
pytest tests/ -m smoke -q
```

### Coverage Reports

```bash
# Generate HTML report
pytest tests/unit/ -m "not integration" --cov=vnstock --cov-report=html

# View coverage in terminal
pytest tests/unit/ -m "not integration" --cov=vnstock --cov-report=term-missing

# Coverage for specific module
pytest tests/unit/ -m "not integration" --cov=vnstock.core.utils
```

### Debug Tests

```bash
# Show print statements
pytest tests/unit/test_file.py -s -v

# Stop on first failure
pytest tests/unit/ -x

# Run specific test
pytest tests/unit/test_file.py::TestClass::test_method -v

# Show slowest tests
pytest tests/unit/ --durations=10
```

---

## 📝 How to Add New Tests

### Step 1: Create Test File
```python
# tests/unit/explorer/test_mynewsource.py

import pytest
from vnstock.explorer.mysource import MyClass

@pytest.mark.unit
@pytest.mark.mysource
class TestMyNewSource:
    """Test MyNewSource functionality."""
    
    def test_basic_functionality(self):
        obj = MyClass()
        assert obj is not None
```

### Step 2: Add Marker (if needed)
```ini
# pytest.ini - markers section
markers =
    mysource: Tests for MyNewSource
```

### Step 3: Use Fixtures (if needed)
```python
def test_with_symbols(self, diverse_test_symbols):
    symbols = diverse_test_symbols['hose']  # 10 HOSE symbols
    for symbol in symbols:
        # Test each symbol
        
def test_with_mocks(self, mock_response_factory):
    mock = mock_response_factory({'data': [...]})
    # Use mock in test
```

### Step 4: Run & Verify
```bash
pytest tests/unit/explorer/test_mynewsource.py -v
```

---

## 🎯 Test Markers Reference

```python
@pytest.mark.unit          # Fast, isolated tests
@pytest.mark.integration   # May call external APIs
@pytest.mark.slow          # Takes >5 seconds
@pytest.mark.api           # API layer (adapters)
@pytest.mark.explorer      # Explorer layer (data sources)
@pytest.mark.vci           # VCI specific
@pytest.mark.tcbs          # TCBS specific
@pytest.mark.core          # Core utilities
```

**Usage**:
```bash
pytest -m unit              # Only unit tests
pytest -m "not integration" # Skip integration tests
pytest -m slow -v           # Slow tests verbose
```

---

## 📊 Current Test Coverage

| Module           | Coverage | Status                         |
| ---------------- | -------- | ------------------------------ |
| proxy_manager.py | 81%      | ✅ Excellent                    |
| core/utils       | 70-92%   | ✅ Good                         |
| api/             | 50-76%   | ✅ Good                         |
| explorer/        | 17-38%   | ⚠️ Integration-dependent        |
| **Total**        | **29%**  | ✅ Acceptable (unit tests only) |

**Note**: 29% is correct for unit tests. Integration tests run separately with real APIs.

---

## 🔧 Fixtures Cheat Sheet

```python
# Symbol fixtures
def test_example(random_hose_symbols):
    symbol = random_hose_symbols[0]  # One symbol
    
def test_example(diverse_test_symbols):
    all_symbols = diverse_test_symbols['all']  # 30 symbols
    hose = diverse_test_symbols['hose']  # 10 HOSE symbols
    
# Mock fixtures
def test_example(mock_response_factory):
    mock = mock_response_factory(json_data={'key': 'value'})
    
# Validation fixtures
def test_example(df_validators):
    validators = df_validators
    assert validators['has_required_columns'](df, ['A', 'B'])
```

---

## ⚠️ Common Pitfalls & Solutions

### Problem: "Test is slow"
**Solution**: Add `@pytest.mark.slow` and `@pytest.mark.integration`
```python
@pytest.mark.integration
@pytest.mark.slow
def test_real_api_call():
    # This won't run in default test suite
```

### Problem: "Can't find fixture"
**Solution**: Check `conftest.py` or `fixtures/symbols.py`
```bash
pytest --fixtures | grep your_fixture_name
```

### Problem: "Mock not working"
**Solution**: Patch correct import path
```python
@patch('vnstock.explorer.vci.quote.requests.get')  # ✅ Correct
def test_example(mock_get):
    ...
```

### Problem: "Coverage is low"
**Solution**: Expected for unit tests without integration
```bash
# Run integration tests for full coverage
pytest tests/unit/ --cov=vnstock --cov-report=html
```

---

## 📚 Related Documentation

- **PROXY_GUIDE.md** - How to use ProxyManager
- **COVERAGE_STRATEGY.md** - Coverage goals & optimization
- **SESSION_5_FINAL_REPORT.md** - Complete session summary

---

## 🎓 Architecture Overview for AI

### Test Execution Flow
```
pytest runs
├── Load conftest.py (fixtures)
├── Load pytest.ini (markers, config)
├── Discover tests/ (test_*.py)
├── Apply markers (@pytest.mark.*)
├── Execute tests
│   ├── Unit tests (all mocked) → Fast ✅
│   ├── Integration tests (real API) → Slow ⏱️
│   └── Proxy tests (mixed) → Medium ⏳
└── Generate reports
    ├── coverage.xml (CI/CD)
    ├── coverage_html/ (view in browser)
    └── junit-results.xml (test results)
```

### When Modifying Tests
1. Check `conftest.py` for available fixtures
2. Use real symbols from `fixtures/symbols.py`
3. Mock external APIs with `mock_response_factory`
4. Add markers for proper test organization
5. Run `pytest tests/unit/ -m "not integration"` to verify
6. Check coverage: `--cov-report=html`

---

## ✅ Checklist for Test Maintenance

- [ ] New test file created in correct location
- [ ] Fixture used from conftest.py or symbols.py
- [ ] External APIs mocked
- [ ] Test markers added
- [ ] pytest.ini updated if new markers
- [ ] Tests pass: `pytest tests/unit/ -q`
- [ ] Coverage checked: `--cov=vnstock`
- [ ] Documentation updated if new patterns
- [ ] Slow/integration tests marked appropriately
- [ ] No hardcoded paths or external dependencies

---

**Last Updated**: November 12, 2025  
**Test Status**: ✅ All 36 unit tests passing  
**Coverage**: 29% (unit tests), 81% ProxyManager  
**Ready for AI**: Yes - use this guide for context ✨
