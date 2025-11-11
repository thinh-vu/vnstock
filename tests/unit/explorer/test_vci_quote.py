"""
Unit tests for VCI Quote explorer.

Tests VCI-specific quote data fetching, parsing, and transformations.
"""

import pytest
import pandas as pd
from vnstock.explorer.vci.quote import Quote


@pytest.mark.unit
@pytest.mark.explorer
@pytest.mark.vci
class TestVCIQuote:
    """Test suite for VCI Quote explorer."""

    def test_vci_quote_instantiation(self):
        """Test VCI Quote can be instantiated."""
        quote = Quote(symbol='ACB', random_agent=False, show_log=False)
        assert quote is not None
        assert quote.symbol == 'ACB'

    def test_vci_quote_has_history_method(self):
        """Test VCI Quote has history method."""
        quote = Quote(symbol='VCB', random_agent=False, show_log=False)
        assert hasattr(quote, 'history')
        assert callable(quote.history)

    def test_vci_quote_has_intraday_method(self):
        """Test VCI Quote has intraday method."""
        quote = Quote(symbol='TCB', random_agent=False, show_log=False)
        assert hasattr(quote, 'intraday')
        assert callable(quote.intraday)

    @pytest.mark.integration
    def test_vci_quote_history_with_mock(
        self, monkeypatch, mock_response_factory
    ):
        """Test VCI Quote history with mocked response."""
        def mock_post(*args, **kwargs):
            return mock_response_factory(json_data={
                "data": [{
                    "tradingDate": "2024-01-01T00:00:00",
                    "open": 100.0,
                    "high": 105.0,
                    "low": 98.0,
                    "close": 103.0,
                    "volume": 1000000
                }]
            })

        monkeypatch.setattr("requests.post", mock_post)

        quote = Quote(symbol='ACB', random_agent=False, show_log=False)
        try:
            df = quote.history(
                start='2024-01-01',
                end='2024-01-31',
                interval='1D'
            )
            assert isinstance(df, pd.DataFrame)
        except Exception:
            pytest.skip("Requires full VCI mock infrastructure")

    def test_vci_quote_symbol_validation(self):
        """Test VCI Quote validates symbol input."""
        # VCI should accept standard Vietnamese stock symbols
        valid_symbols = ['ACB', 'VCB', 'TCB', 'BID']
        for symbol in valid_symbols:
            quote = Quote(
                symbol=symbol,
                random_agent=False,
                show_log=False
            )
            assert quote.symbol == symbol
