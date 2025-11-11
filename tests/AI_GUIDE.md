# 🤖 AI Quick Reference: Vnstock Test Modification Guide

**Goal**: Help AI understand and modify vnstock tests efficiently.

---

## 🎯 Quick Navigation

### "I need to..."

**Add a new test for VCI Quote**
```
1. Go to: tests/unit/explorer/test_vci_quote_comprehensive.py
2. Add test method to TestVCIQuoteComprehensive class
3. Use fixture: random_hose_symbols (or diverse_test_symbols)
4. Mark with: @pytest.mark.vci, @pytest.mark.integration (if live API)
5. Run: pytest tests/unit/explorer/test_vci_quote_comprehensive.py -v
```

**Test a new TCBS method**
```
1. Go to: tests/unit/explorer/test_tcbs_quote_comprehensive.py
2. Add test method to TestTCBSQuoteComprehensive class
3. Use parametrize for multiple parameters
4. Mark with: @pytest.mark.tcbs, @pytest.mark.integration
5. Run: pytest tests/unit/explorer/test_tcbs_quote_comprehensive.py -v
```

**Test API adapter for new source**
```
1. Create: tests/unit/api/test_newsource.py
2. Import: from vnstock.api.quote import Quote
3. Test initialization and delegation
4. Run: pytest tests/unit/api/test_newsource.py -v
```

**Create mock responses for API testing**
```
1. Use fixture: mock_response_factory
2. Create mock: mock = mock_response_factory(json_data={...})
3. Pass to function: assert mock.json() == {...}
4. Or use @patch: @patch('requests.get', return_value=mock)
```

**Fix a failing test**
```
1. Run: pytest tests/unit/path/to/test.py -v
2. Check error message
3. Use pdb: pytest tests/unit/path/to/test.py -v -s --pdb
4. Or check fixtures: pytest --fixtures | grep fixture_name
```

---

## 📚 File Structure Reference

### Test File Locations by Type

```
tests/unit/api/
  ├── test_quote.py         # Quote adapter (VCI, TCBS, MSN)
  ├── test_listing.py       # Listing adapter
  ├── test_company.py       # Company adapter
  └── test_finance.py       # Finance adapter

tests/unit/explorer/
  ├── test_vci_quote_comprehensive.py
  ├── test_vci_listing_comprehensive.py
  ├── test_vci_company_finance_comprehensive.py
  ├── test_vci_quote_with_proxy.py      # Proxy integration
  ├── test_tcbs_quote_comprehensive.py
  └── test_tcbs_screener_trading_comprehensive.py

tests/unit/core/
  └── test_proxy_manager.py  # ProxyManager utility

tests/fixtures/
  └── symbols.py            # Symbol generators

tests/conftest.py           # Shared fixtures & config
tests/ARCHITECTURE.md       # This structure explained
```

### Key Files to Understand

| File                | Purpose          | When to Modify              |
| ------------------- | ---------------- | --------------------------- |
| conftest.py         | Fixtures & mocks | Add new mock/fixture        |
| fixtures/symbols.py | Real symbols     | Add new symbol provider     |
| pytest.ini          | Test config      | Add marker, change coverage |
| ARCHITECTURE.md     | Test guide       | Document pattern            |

---

## 🔑 Core Fixtures (Copy-Paste Reference)

### Using Symbol Fixtures

```python
# Single symbol from HOSE
def test_quote(self, random_hose_symbols):
    symbol = random_hose_symbols[0]
    quote = Quote(symbol=symbol)
    # Test with real symbol

# Multiple symbols from different exchanges
def test_multiple(self, diverse_test_symbols):
    hose = diverse_test_symbols['hose']  # 10 HOSE
    hnx = diverse_test_symbols['hnx']    # 10 HNX
    upcom = diverse_test_symbols['upcom']  # 10 UPCOM
    all_symbols = diverse_test_symbols['all']  # All 30

# 100 random symbols per exchange
def test_batch(self, random_hose_symbols):
    assert len(random_hose_symbols) == 100
    for symbol in random_hose_symbols[:10]:  # Test first 10
        quote = Quote(symbol=symbol)
```

### Using Mock Fixtures

```python
# Mock response factory
def test_api(self, mock_response_factory):
    mock = mock_response_factory(
        json_data={'close': 100.0, 'volume': 1000},
        status_code=200
    )
    assert mock.json()['close'] == 100.0

# Mock requests globally
def test_quote(self, mock_http_get):
    # mock_http_get is now patched
    response = requests.get('https://...')
    assert response.status_code == 200

# Mock with @patch decorator (for complex scenarios)
from unittest.mock import patch

@patch('requests.get')
def test_quote(self, mock_get, mock_response_factory):
    mock_get.return_value = mock_response_factory(
        json_data={'close': 100.0}
    )
    # Your test here
```

### Using DataFrame Validators

```python
def test_listing(self, df_validators):
    listing = Listing()
    df = listing.all_symbols()
    
    # Validator examples
    validators = df_validators
    assert validators['has_columns'](df, ['symbol', 'name'])
    assert validators['no_empty'](df, 'symbol')
    assert validators['all_numeric'](df, 'price')
```

---

## 📝 Common Test Patterns

### Pattern 1: Test All Intervals

```python
@pytest.mark.parametrize('interval', ['1m', '5m', '15m', '30m', '1h', '1D', '1W', '1M'])
def test_history_all_intervals(self, interval):
    """Test quote history with each interval."""
    quote = Quote(symbol='ACB')
    df = quote.history(start='2024-01-01', interval=interval)
    assert df is not None
    assert len(df) > 0
```

### Pattern 2: Test Multiple Symbols

```python
def test_multiple_symbols(self, diverse_test_symbols):
    """Test quote for symbols from all exchanges."""
    symbols = diverse_test_symbols['all']
    
    for symbol in symbols:
        quote = Quote(symbol=symbol)
        assert quote.symbol == symbol
        # Additional assertions
```

### Pattern 3: Test Parameters

```python
@pytest.mark.parametrize('lang', ['vi', 'en'])
@pytest.mark.parametrize('period', ['year', 'quarter'])
def test_financial_params(self, lang, period):
    """Test financial with language & period combinations."""
    finance = Finance(symbol='ACB')
    df = finance.income_statement(period=period, lang=lang)
    assert df is not None
```

### Pattern 4: Mock API Response

```python
@patch('requests.get')
def test_quote_with_mock(self, mock_get, mock_response_factory):
    """Test quote with mocked API response."""
    mock_get.return_value = mock_response_factory(
        json_data={'data': [{'close': 100.0, 'volume': 1000}]}
    )
    
    quote = Quote(symbol='ACB')
    df = quote.history()
    assert df is not None
```

### Pattern 5: Test Error Handling

```python
def test_invalid_symbol(self):
    """Test quote with invalid symbol."""
    with pytest.raises(ValueError):
        Quote(symbol='INVALID_SYMBOL_XYZ')

def test_api_timeout(self, monkeypatch):
    """Test quote when API times out."""
    def mock_timeout(*args, **kwargs):
        raise requests.Timeout("API timeout")
    
    monkeypatch.setattr("requests.get", mock_timeout)
    
    with pytest.raises(requests.Timeout):
        Quote(symbol='ACB').history()
```

---

## 🧪 Test Execution Quick Commands

```bash
# Run specific test
pytest tests/unit/explorer/test_vci_quote_comprehensive.py::TestVCIQuoteComprehensive::test_history_basic -v

# Run with print output (debug)
pytest tests/unit/test_file.py -v -s

# Stop on first failure
pytest tests/unit/ -x

# Run slowest tests first
pytest tests/unit/ --durations=5

# Run with coverage for specific module
pytest tests/unit/ --cov=vnstock.explorer.vci --cov-report=term-missing

# Run only VCI tests
pytest tests/unit/ -m vci -v

# Run everything except integration
pytest tests/unit/ -m "not integration" -q

# Watch mode (requires pytest-watch)
ptw tests/unit/ -- -v
```

---

## 🐛 Debugging Failed Tests

### Step 1: Read the Error
```bash
pytest tests/unit/test_file.py -v
# Look for: AssertionError, AttributeError, TypeError, etc.
```

### Step 2: Add Debug Output
```bash
pytest tests/unit/test_file.py -v -s
# -s shows print() outputs
```

### Step 3: Use pdb (Python Debugger)
```bash
pytest tests/unit/test_file.py -v --pdb
# Or add breakpoint in test:
# import pdb; pdb.set_trace()
```

### Step 4: Check Fixture Issues
```bash
# List all available fixtures
pytest --fixtures

# Check specific fixture
pytest --fixtures | grep "symbol"

# Trace fixture execution
pytest tests/unit/test_file.py -v --setup-show
```

### Step 5: Mock Issues
```python
# Wrong: Module not patched correctly
@patch('vnstock.explorer.quote.requests')  # ❌

# Correct: Patch where it's USED
@patch('vnstock.api.quote.requests')       # ✅

# Debug patch
from unittest.mock import patch, MagicMock
with patch('requests.get') as mock_get:
    mock_get.return_value = MagicMock()
    mock_get.assert_called()  # Check if called
```

---

## ✨ Best Practices

### ✅ DO

```python
# Use fixtures
def test_example(self, random_hose_symbols):
    symbol = random_hose_symbols[0]

# Mark tests appropriately
@pytest.mark.integration
@pytest.mark.slow
def test_live_api():
    pass

# Use parametrize for variants
@pytest.mark.parametrize('symbol', ['ACB', 'VCB', 'TCB'])
def test_multiple(symbol):
    pass

# Mock external APIs
@patch('requests.get')
def test_api(mock_get):
    pass

# Clear assertion messages
assert symbol is not None, "Symbol should not be None"
```

### ❌ DON'T

```python
# Hardcoded test data
symbol = 'ACB'  # ❌ Use fixture instead

# Unpatched external calls in unit tests
requests.get('https://api.example.com')  # ❌ Mock it

# Long running tests without marking
def test_real_api():  # ❌ Add @pytest.mark.integration

# Vague assertions
assert df is not None  # ❌ Add specific checks
assert df['close'].mean() > 0  # ✅ Better

# Global state modifications
symbol = 'ACB'  # ❌ Tests should be independent
```

---

## 🎓 Learning Path

1. **Start**: Read tests/ARCHITECTURE.md (5 min)
2. **Understand**: Check conftest.py fixtures (10 min)
3. **Copy**: Use existing test as template (5 min)
4. **Implement**: Write new test (10 min)
5. **Run**: pytest tests/unit/your_test.py -v (2 min)
6. **Debug**: Use pdb if needed (10 min)
7. **Refine**: Check coverage (5 min)

---

## 📞 Quick Help

**Q: How do I know which fixture to use?**
A: Run `pytest --fixtures` or check conftest.py

**Q: Test is calling real API, how to mock?**
A: Use `@patch('module.path.requests.get')` or `mock_response_factory`

**Q: Coverage is too low, what do I do?**
A: Run integration tests with `pytest tests/unit/ -m integration`

**Q: How do I skip a test?**
A: Use `@pytest.mark.skip(reason="...")` or `pytest.skip("...")`

**Q: How do I test multiple scenarios?**
A: Use `@pytest.mark.parametrize` decorator

**Q: Test passes locally but fails in CI?**
A: Check: dependencies, paths, environment variables, time zones

---

## 📦 Key Imports for Tests

```python
import pytest                    # Test framework
import pandas as pd             # DataFrame handling
from unittest.mock import patch, MagicMock  # Mocking
import requests                 # HTTP library
from vnstock.api.quote import Quote          # API adapters
from vnstock.explorer.vci import Quote       # Data source explorers
```

---

## 🚀 Template: New Test File

```python
"""Tests for [feature/module]."""

import pytest
from unittest.mock import patch
from vnstock.api.quote import Quote


@pytest.mark.unit
@pytest.mark.api
class TestMyNewFeature:
    """Test [feature/module] functionality."""
    
    def test_basic_functionality(self):
        """Test basic usage."""
        obj = Quote(symbol='ACB')
        assert obj is not None
    
    def test_with_symbols(self, diverse_test_symbols):
        """Test with real symbols."""
        symbols = diverse_test_symbols['hose']
        for symbol in symbols[:5]:  # Test first 5
            quote = Quote(symbol=symbol)
            assert quote.symbol == symbol
    
    @patch('requests.get')
    def test_with_mock(self, mock_get, mock_response_factory):
        """Test with mocked response."""
        mock_get.return_value = mock_response_factory(
            json_data={'close': 100.0}
        )
        quote = Quote(symbol='ACB')
        assert quote is not None
    
    @pytest.mark.parametrize('interval', ['1D', '1W', '1M'])
    def test_parameters(self, interval):
        """Test with different parameters."""
        quote = Quote(symbol='ACB')
        # Use interval in test
```

---

**Last Updated**: November 12, 2025  
**For AI Analysis**: Yes ✅  
**Difficulty Level**: Intermediate  
**Time to Implement**: 15-30 minutes per new test
