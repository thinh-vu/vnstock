"""
Pytest configuration and shared fixtures for vnstock test suite.

CORE FIXTURES (for AI understanding):
====================================

HTTP Mocking:
  - mock_response_factory: Create custom mock responses
  - mock_http_get: Mock requests.get globally
  - mock_http_post: Mock requests.post globally
  
Symbol Data:
  - Imported from tests.fixtures.symbols
  - real_symbols_dataset: Live API data (HOSE/HNX/UPCOM)
  - random_hose_symbols, random_hnx_symbols, etc: 100 random per exchange
  - diverse_test_symbols: 30 symbols (10 per exchange)
  
Utilities:
  - df_validators: Dictionary of DataFrame validation helpers
  - disable_logging: Auto-disable logging noise in tests (autouse)

USAGE EXAMPLES:
===============

Mock HTTP Response:
    def test_api(mock_response_factory):
        mock = mock_response_factory({'close': 100.0})
        assert mock.json()['close'] == 100.0

Use Symbols:
    def test_quote(random_hose_symbols):
        symbol = random_hose_symbols[0]
        quote = Quote(symbol=symbol)

Validate DataFrame:
    def test_listing(df_validators):
        df = listing.all_symbols()
        assert df_validators['has_columns'](df, ['symbol', 'name'])
"""

import json
from typing import Dict, List, Optional
import pytest
import pandas as pd
import requests

# Import symbol fixtures from local fixtures module
pytest_plugins = ['fixtures.symbols']


# ============================================================================
# HTTP Mocking Fixtures - For testing API calls without network access
# ============================================================================

class MockResponse:
    """Mock HTTP response object that simulates requests.Response.
    
    Attributes:
        json_data: Parsed JSON response body
        status_code: HTTP status code (200, 404, etc)
        text: Raw response text
        content: Response content as bytes
    """

    def __init__(self, json_data: Optional[Dict] = None,
                 status_code: int = 200,
                 text: str = ""):
        self._json_data = json_data or {}
        self.status_code = status_code
        self.text = text or json.dumps(json_data or {})
        self.content = self.text.encode('utf-8')

    def json(self):
        """Return parsed JSON data from response."""
        return self._json_data

    def raise_for_status(self):
        """Raise HTTPError if status code indicates an error."""
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


@pytest.fixture
def mock_response_factory():
    """Factory for creating customized mock HTTP responses.
    
    Returns a function to create MockResponse objects with custom data.
    
    Example:
        mock = mock_response_factory(
            json_data={'close': 100.0},
            status_code=200
        )
        assert mock.status_code == 200
    """
    def _create(json_data=None, status_code=200, text=""):
        return MockResponse(json_data, status_code, text)
    return _create


@pytest.fixture
def mock_successful_response(mock_response_factory):
    """Mock successful HTTP response with standard empty data structure."""
    return mock_response_factory(json_data={"data": {}})


@pytest.fixture
def mock_http_get(monkeypatch, mock_response_factory):
    """Mock requests.get globally for all tests using this fixture.
    
    Returns empty 200 response by default.
    Can be overridden per test with @patch or by setting side_effect.
    """
    def _mock_get(*args, **kwargs):
        return mock_response_factory(json_data={"data": []})
    
    monkeypatch.setattr("requests.get", _mock_get)
    return _mock_get


@pytest.fixture
def mock_http_post(monkeypatch, mock_response_factory):
    """Mock requests.post globally for all tests using this fixture.
    
    Returns empty 200 response by default.
    Can be overridden per test with @patch or by setting side_effect.
    """
    def _mock_post(*args, **kwargs):
        return mock_response_factory(json_data={"data": []})
    
    monkeypatch.setattr("requests.post", _mock_post)
    return _mock_post


# ============================================================================
# VCI-specific Mocking
# ============================================================================


@pytest.fixture
def mock_vci_company(monkeypatch):
    """Mock VCI Company._fetch_data."""
    def _mock_fetch(*args, **kwargs):
        return {
            "CompanyListingInfo": {
                "icbName4": "Bán lẻ phức hợp",
                "ticker": "AAA",
                "organName": "Test Company"
            }
        }
    
    monkeypatch.setattr(
        "vnstock.explorer.vci.company.Company._fetch_data",
        _mock_fetch
    )


@pytest.fixture
def mock_vci_send_request(monkeypatch):
    """Mock vnstock.core.utils.client.send_request for VCI."""
    def _mock_send(*args, **kwargs):
        return {"data": {}}
    
    monkeypatch.setattr(
        "vnstock.core.utils.client.send_request",
        _mock_send
    )


# ============================================================================
# TCBS-specific Mocking
# ============================================================================

@pytest.fixture
def mock_tcbs_response(monkeypatch, mock_response_factory):
    """Mock TCBS API responses."""
    def _mock_get(*args, **kwargs):
        return mock_response_factory(json_data={"data": []})
    
    monkeypatch.setattr("requests.get", _mock_get)


# ============================================================================
# MSN-specific Mocking
# ============================================================================

@pytest.fixture
def mock_msn_apikey(monkeypatch):
    """Mock MSN API key generation."""
    monkeypatch.setattr(
        "vnstock.explorer.msn.quote.msn_apikey",
        lambda *args, **kwargs: "mock_api_key"
    )


# ============================================================================
# DataFrame Validation Helpers
# ============================================================================

def assert_is_dataframe(obj, msg="Expected pandas DataFrame"):
    """Assert object is a pandas DataFrame."""
    assert isinstance(obj, pd.DataFrame), msg


def assert_has_columns(df: pd.DataFrame, columns: List[str]):
    """Assert DataFrame has expected columns."""
    missing = set(columns) - set(df.columns)
    assert not missing, f"Missing columns: {missing}"


def assert_not_empty(df: pd.DataFrame):
    """Assert DataFrame is not empty."""
    assert not df.empty, "DataFrame should not be empty"


def assert_column_types(df: pd.DataFrame, type_map: Dict[str, type]):
    """Assert DataFrame columns have expected types."""
    for col, expected_type in type_map.items():
        if col in df.columns:
            actual_type = df[col].dtype
            assert actual_type == expected_type, \
                f"Column {col}: expected {expected_type}, got {actual_type}"


@pytest.fixture
def df_validators():
    """Provide DataFrame validation helpers."""
    return {
        'is_dataframe': assert_is_dataframe,
        'has_columns': assert_has_columns,
        'not_empty': assert_not_empty,
        'column_types': assert_column_types,
    }


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_stock_symbols():
    """Sample stock symbols for testing."""
    return ['VCB', 'ACB', 'TCB', 'BID', 'VNM']


@pytest.fixture
def sample_date_range():
    """Sample date range for testing."""
    return {
        'start': '2024-01-01',
        'end': '2024-03-31'
    }


@pytest.fixture
def sample_listing_data():
    """Sample listing data payload."""
    return [
        {
            "symbol": "AAA",
            "organ_name": "Company A",
            "type": "STOCK",
            "exchange": "HOSE"
        },
        {
            "symbol": "BBB",
            "organ_name": "Company B",
            "type": "STOCK",
            "exchange": "HNX"
        },
    ]


@pytest.fixture
def sample_quote_data():
    """Sample quote/price data payload."""
    return [
        {
            "time": "2024-01-01",
            "open": 100.0,
            "high": 105.0,
            "low": 98.0,
            "close": 103.0,
            "volume": 1000000
        },
        {
            "time": "2024-01-02",
            "open": 103.0,
            "high": 108.0,
            "low": 102.0,
            "close": 107.0,
            "volume": 1200000
        },
    ]


# ============================================================================
# Test Configuration
# ============================================================================

@pytest.fixture(autouse=True)
def disable_logging(monkeypatch):
    """Disable logging during tests to reduce noise."""
    import logging
    
    # Create a null logger
    null_logger = logging.getLogger('null')
    null_logger.setLevel(logging.CRITICAL)
    
    # Mock getLogger to return the null logger
    monkeypatch.setattr(
        logging, 'getLogger',
        lambda name='': null_logger
    )


@pytest.fixture
def temp_cache_dir(tmp_path):
    """Provide temporary directory for cache during tests."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir


# ============================================================================
# Performance Testing Utilities
# ============================================================================

@pytest.fixture
def benchmark_threshold():
    """Default performance thresholds for benchmarking."""
    return {
        'parsing': 0.1,  # seconds per 1000 records
        'api_call': 2.0,  # seconds per API call
        'memory': 100,  # MB max memory increase
    }
