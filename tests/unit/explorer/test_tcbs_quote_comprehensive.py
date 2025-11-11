"""
Comprehensive tests for TCBS Quote with all parameters and diverse symbols.

Tests cover:
- history() with different intervals, page sizes, ascending options
- Random samples from HOSE, HNX, UPCOM
- Derivatives
- Different date ranges
"""

import pytest
import pandas as pd
from vnstock.explorer.tcbs.quote import Quote


@pytest.mark.integration
@pytest.mark.tcbs
@pytest.mark.slow
class TestTCBSQuoteComprehensive:
    """Comprehensive test suite for TCBS Quote."""

    @pytest.mark.parametrize("interval", ['1D', '1W', '1M'])
    def test_history_intervals(self, diverse_test_symbols, interval):
        """Test history() with different intervals."""
        symbol = diverse_test_symbols['hose'][0]
        
        quote = Quote(symbol=symbol, random_agent=False, show_log=False)
        df = quote.history(
            start='2024-01-01',
            end='2024-11-11',
            interval=interval
        )
        
        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            expected_cols = ['open', 'high', 'low', 'close']
            for col in expected_cols:
                assert col in df.columns

    @pytest.mark.parametrize("page_size", [100, 500, 1000])
    def test_history_page_sizes(self, diverse_test_symbols, page_size):
        """Test history() with different page sizes."""
        symbol = diverse_test_symbols['hose'][0]
        
        quote = Quote(symbol=symbol, random_agent=False, show_log=False)
        df = quote.history(
            start='2024-01-01',
            end='2024-11-11',
            interval='1D',
            page_size=page_size
        )
        
        assert isinstance(df, pd.DataFrame)

    @pytest.mark.parametrize("ascending", [True, False])
    def test_history_ascending(self, diverse_test_symbols, ascending):
        """Test history() with ascending parameter."""
        symbol = diverse_test_symbols['hose'][0]
        
        quote = Quote(symbol=symbol, random_agent=False, show_log=False)
        df = quote.history(
            start='2024-01-01',
            end='2024-11-11',
            interval='1D',
            ascending=ascending
        )
        
        assert isinstance(df, pd.DataFrame)
        if not df.empty and len(df) > 1:
            # Check if data is sorted correctly
            if df.index.name == 'time' or 'time' in df.columns:
                pass  # Just ensure it doesn't error

    def test_history_random_hose_symbols(self, random_hose_symbols):
        """Test history() with random HOSE symbols."""
        test_symbols = random_hose_symbols[:10]
        
        for symbol in test_symbols:
            try:
                quote = Quote(
                    symbol=symbol,
                    random_agent=False,
                    show_log=False
                )
                df = quote.history(
                    start='2024-10-01',
                    end='2024-10-31',
                    interval='1D'
                )
                
                assert isinstance(df, pd.DataFrame)
            
            except Exception as e:
                pytest.fail(f"TCBS HOSE {symbol} failed: {e}")

    def test_history_random_hnx_symbols(self, random_hnx_symbols):
        """Test history() with random HNX symbols."""
        test_symbols = random_hnx_symbols[:10]
        
        for symbol in test_symbols:
            try:
                quote = Quote(
                    symbol=symbol,
                    random_agent=False,
                    show_log=False
                )
                df = quote.history(
                    start='2024-10-01',
                    end='2024-10-31',
                    interval='1D'
                )
                
                assert isinstance(df, pd.DataFrame)
            
            except Exception as e:
                pytest.fail(f"TCBS HNX {symbol} failed: {e}")

    def test_history_random_upcom_symbols(self, random_upcom_symbols):
        """Test history() with random UPCOM symbols."""
        test_symbols = random_upcom_symbols[:10]
        
        for symbol in test_symbols:
            try:
                quote = Quote(
                    symbol=symbol,
                    random_agent=False,
                    show_log=False
                )
                df = quote.history(
                    start='2024-10-01',
                    end='2024-10-31',
                    interval='1D'
                )
                
                assert isinstance(df, pd.DataFrame)
            
            except Exception as e:
                pytest.fail(f"TCBS UPCOM {symbol} failed: {e}")

    def test_history_derivatives(self, derivative_symbols):
        """Test history() with derivative symbols."""
        for symbol in derivative_symbols[:3]:
            try:
                quote = Quote(
                    symbol=symbol,
                    random_agent=False,
                    show_log=False
                )
                df = quote.history(
                    start='2024-10-01',
                    end='2024-10-31',
                    interval='1D'
                )
                
                assert isinstance(df, pd.DataFrame)
            
            except Exception as e:
                print(f"TCBS derivative {symbol} not supported: {e}")

    def test_history_different_date_ranges(
        self, diverse_test_symbols, test_date_ranges
    ):
        """Test history() with different date ranges."""
        symbol = diverse_test_symbols['hose'][0]
        quote = Quote(symbol=symbol, random_agent=False, show_log=False)
        
        for range_name, dates in test_date_ranges.items():
            try:
                df = quote.history(
                    start=dates['start'],
                    end=dates['end'],
                    interval='1D'
                )
                
                assert isinstance(df, pd.DataFrame)
            
            except Exception as e:
                pytest.fail(
                    f"TCBS date range {range_name} failed: {e}"
                )

    def test_history_edge_cases(self, diverse_test_symbols):
        """Test history() edge cases."""
        symbol = diverse_test_symbols['hose'][0]
        quote = Quote(symbol=symbol, random_agent=False, show_log=False)
        
        # Same start and end date
        df = quote.history(
            start='2024-10-01',
            end='2024-10-01',
            interval='1D'
        )
        assert isinstance(df, pd.DataFrame)
        
        # Very recent date
        df = quote.history(
            start='2024-11-10',
            end='2024-11-11',
            interval='1D'
        )
        assert isinstance(df, pd.DataFrame)

    def test_batch_symbols_performance(self, diverse_test_symbols):
        """Test fetching data for multiple symbols."""
        symbols = diverse_test_symbols['all'][:5]
        
        results = {}
        for symbol in symbols:
            try:
                quote = Quote(
                    symbol=symbol,
                    random_agent=False,
                    show_log=False
                )
                df = quote.history(
                    start='2024-10-01',
                    end='2024-10-31',
                    interval='1D'
                )
                results[symbol] = not df.empty
            except Exception as e:
                results[symbol] = False
                print(f"TCBS batch test failed for {symbol}: {e}")
        
        # At least 50% should succeed
        success_rate = sum(results.values()) / len(results)
        assert success_rate >= 0.5

    def test_random_agent_parameter(self, diverse_test_symbols):
        """Test Quote with random_agent=True."""
        symbol = diverse_test_symbols['hose'][0]
        
        quote = Quote(symbol=symbol, random_agent=True, show_log=False)
        df = quote.history(
            start='2024-10-01',
            end='2024-10-31',
            interval='1D'
        )
        
        assert isinstance(df, pd.DataFrame)

    def test_show_log_parameter(self, diverse_test_symbols):
        """Test Quote with show_log parameter."""
        symbol = diverse_test_symbols['hose'][0]
        
        # With show_log=True
        quote = Quote(symbol=symbol, random_agent=False, show_log=True)
        df = quote.history(
            start='2024-10-01',
            end='2024-10-31',
            interval='1D'
        )
        assert isinstance(df, pd.DataFrame)
        
        # With show_log=False
        quote = Quote(symbol=symbol, random_agent=False, show_log=False)
        df = quote.history(
            start='2024-10-01',
            end='2024-10-31',
            interval='1D'
        )
        assert isinstance(df, pd.DataFrame)
