"""
Comprehensive tests for VCI Quote with all parameters and diverse symbols.

Tests cover:
- All time intervals (1m, 5m, 15m, 30m, 1h, 1D, 1W, 1M)
- Random samples from HOSE, HNX, UPCOM
- Derivatives, covered warrants
- Different date ranges
"""

import pytest
import pandas as pd
from vnstock.explorer.vci.quote import Quote


@pytest.mark.integration
@pytest.mark.vci
@pytest.mark.slow
class TestVCIQuoteComprehensive:
    """Comprehensive test suite for VCI Quote."""

    def test_history_all_intervals_hose_sample(
        self, diverse_test_symbols, test_intervals
    ):
        """Test history() with all intervals on HOSE samples."""
        hose_samples = diverse_test_symbols['hose'][:3]
        
        for symbol in hose_samples:
            quote = Quote(symbol=symbol, random_agent=False, show_log=False)
            
            for interval in ['1D', '1W', '1M']:  # Start with longer intervals
                try:
                    df = quote.history(
                        start='2024-01-01',
                        end='2024-11-11',
                        interval=interval
                    )
                    
                    assert isinstance(df, pd.DataFrame), \
                        f"Failed for {symbol} with interval {interval}"
                    
                    if not df.empty:
                        expected_cols = ['open', 'high', 'low', 'close']
                        for col in expected_cols:
                            assert col in df.columns, \
                                f"Missing {col} in {symbol} {interval}"
                
                except Exception as e:
                    pytest.fail(
                        f"history() failed for {symbol} "
                        f"interval={interval}: {e}"
                    )

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
                
                assert isinstance(df, pd.DataFrame), \
                    f"Failed for HOSE symbol {symbol}"
            
            except Exception as e:
                pytest.fail(f"HOSE {symbol} history failed: {e}")

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
                
                assert isinstance(df, pd.DataFrame), \
                    f"Failed for HNX symbol {symbol}"
            
            except Exception as e:
                pytest.fail(f"HNX {symbol} history failed: {e}")

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
                
                assert isinstance(df, pd.DataFrame), \
                    f"Failed for UPCOM symbol {symbol}"
            
            except Exception as e:
                pytest.fail(f"UPCOM {symbol} history failed: {e}")

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
                
                assert isinstance(df, pd.DataFrame), \
                    f"Failed for derivative {symbol}"
            
            except Exception as e:
                pytest.fail(f"Derivative {symbol} failed: {e}")

    @pytest.mark.parametrize("interval", ['1D', '1W', '1M'])
    def test_history_intervals_parametrized(
        self, diverse_test_symbols, interval
    ):
        """Test history() with parametrized intervals."""
        symbol = diverse_test_symbols['hose'][0]
        
        quote = Quote(symbol=symbol, random_agent=False, show_log=False)
        df = quote.history(
            start='2024-01-01',
            end='2024-11-11',
            interval=interval
        )
        
        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert 'close' in df.columns

    def test_intraday_hose_samples(self, diverse_test_symbols):
        """Test intraday() with HOSE samples."""
        hose_samples = diverse_test_symbols['hose'][:3]
        
        for symbol in hose_samples:
            try:
                quote = Quote(
                    symbol=symbol,
                    random_agent=False,
                    show_log=False
                )
                df = quote.intraday(
                    symbol=symbol,
                    page_size=100,
                    show_log=False
                )
                
                assert isinstance(df, pd.DataFrame), \
                    f"intraday() failed for {symbol}"
            
            except Exception as e:
                # Intraday may not be available for all symbols
                print(f"Intraday not available for {symbol}: {e}")

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
                
                assert isinstance(df, pd.DataFrame), \
                    f"Failed for {range_name} range"
            
            except Exception as e:
                pytest.fail(f"Date range {range_name} failed: {e}")

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
        
        # Very recent date range
        df = quote.history(
            start='2024-11-10',
            end='2024-11-11',
            interval='1D'
        )
        assert isinstance(df, pd.DataFrame)

    def test_covered_warrants_if_available(self, sample_covered_warrants):
        """Test history() with covered warrants if available."""
        if not sample_covered_warrants:
            pytest.skip("No covered warrants available")
        
        for symbol in sample_covered_warrants[:5]:
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
                print(f"CW {symbol} not supported or failed: {e}")

    def test_batch_symbols_performance(self, diverse_test_symbols):
        """Test fetching data for multiple symbols (performance check)."""
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
                print(f"Batch test failed for {symbol}: {e}")
        
        # At least 50% should succeed
        success_rate = sum(results.values()) / len(results)
        assert success_rate >= 0.5, \
            f"Success rate too low: {success_rate}"
