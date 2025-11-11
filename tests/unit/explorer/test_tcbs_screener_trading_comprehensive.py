"""
Comprehensive tests for TCBS Screener, Trading, and other modules.

Tests cover:
Screener:
- stock() with various params filters
- Different exchange combinations
- Limit parameter variations

Trading:
- price_board() with multiple symbols
- price_depth() for market depth data
"""

import pytest
import pandas as pd
from vnstock.explorer.tcbs.screener import Screener
from vnstock.explorer.tcbs.trading import Trading


@pytest.mark.integration
@pytest.mark.tcbs
class TestTCBSScreenerComprehensive:
    """Comprehensive test suite for TCBS Screener."""

    def test_screener_basic(self):
        """Test basic stock screening."""
        screener = Screener()
        
        df = screener.stock(
            params={"exchangeName": "HOSE,HNX,UPCOM"},
            limit=50
        )
        
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert 'ticker' in df.columns or 'symbol' in df.columns

    @pytest.mark.parametrize("exchange", [
        "HOSE",
        "HNX",
        "UPCOM",
        "HOSE,HNX",
        "HOSE,HNX,UPCOM"
    ])
    def test_screener_exchanges(self, exchange):
        """Test screener with different exchange combinations."""
        screener = Screener()
        
        df = screener.stock(
            params={"exchangeName": exchange},
            limit=50
        )
        
        assert isinstance(df, pd.DataFrame)
        # May be empty for some exchanges
        if not df.empty:
            assert 'ticker' in df.columns or 'symbol' in df.columns

    @pytest.mark.parametrize("limit", [10, 50, 100, 500, 1000])
    def test_screener_limits(self, limit):
        """Test screener with different limit values."""
        screener = Screener()
        
        df = screener.stock(
            params={"exchangeName": "HOSE,HNX,UPCOM"},
            limit=limit
        )
        
        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            # Result may be less than limit if not enough matches
            assert len(df) <= limit

    @pytest.mark.parametrize("lang", ['vi', 'en'])
    def test_screener_language(self, lang):
        """Test screener with different languages."""
        screener = Screener()
        
        df = screener.stock(
            params={"exchangeName": "HOSE"},
            limit=50,
            lang=lang
        )
        
        assert isinstance(df, pd.DataFrame)

    def test_screener_price_filters(self):
        """Test screener with price filters."""
        screener = Screener()
        
        # Filter by price range
        df = screener.stock(
            params={
                "exchangeName": "HOSE,HNX,UPCOM",
                "lastPrice": {
                    "min": 10,
                    "max": 100
                }
            },
            limit=100
        )
        
        assert isinstance(df, pd.DataFrame)

    def test_screener_volume_filters(self):
        """Test screener with volume filters."""
        screener = Screener()
        
        df = screener.stock(
            params={
                "exchangeName": "HOSE,HNX,UPCOM",
                "totalVol": {
                    "min": 100000
                }
            },
            limit=100
        )
        
        assert isinstance(df, pd.DataFrame)

    def test_screener_market_cap_filters(self):
        """Test screener with market cap filters."""
        screener = Screener()
        
        df = screener.stock(
            params={
                "exchangeName": "HOSE",
                "marketCap": {
                    "min": 1000000000000  # 1 trillion VND
                }
            },
            limit=50
        )
        
        assert isinstance(df, pd.DataFrame)

    def test_screener_combined_filters(self):
        """Test screener with multiple combined filters."""
        screener = Screener()
        
        df = screener.stock(
            params={
                "exchangeName": "HOSE",
                "lastPrice": {"min": 10, "max": 100},
                "totalVol": {"min": 100000}
            },
            limit=50
        )
        
        assert isinstance(df, pd.DataFrame)


@pytest.mark.integration
@pytest.mark.tcbs
class TestTCBSTradingComprehensive:
    """Comprehensive test suite for TCBS Trading."""

    def test_price_board_single_symbol(self, diverse_test_symbols):
        """Test price_board() with single symbol."""
        symbol = diverse_test_symbols['hose'][0]
        trading = Trading()
        
        df = trading.price_board(symbols_list=[symbol])
        
        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert 'ticker' in df.columns or 'symbol' in df.columns

    def test_price_board_multiple_symbols(self, diverse_test_symbols):
        """Test price_board() with multiple symbols."""
        symbols = diverse_test_symbols['hose'][:5]
        trading = Trading()
        
        df = trading.price_board(symbols_list=symbols)
        
        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert len(df) <= len(symbols)

    def test_price_board_mixed_exchanges(self, diverse_test_symbols):
        """Test price_board() with symbols from different exchanges."""
        symbols = (
            diverse_test_symbols['hose'][:2] +
            diverse_test_symbols['hnx'][:2] +
            diverse_test_symbols['upcom'][:2]
        )
        trading = Trading()
        
        df = trading.price_board(symbols_list=symbols)
        
        assert isinstance(df, pd.DataFrame)

    def test_price_board_derivatives(self, derivative_symbols):
        """Test price_board() with derivative symbols."""
        if not derivative_symbols:
            pytest.skip("No derivative symbols available")
        
        trading = Trading()
        df = trading.price_board(symbols_list=derivative_symbols[:3])
        
        assert isinstance(df, pd.DataFrame)

    def test_price_board_large_batch(self, random_hose_symbols):
        """Test price_board() with large number of symbols."""
        symbols = random_hose_symbols[:20]
        trading = Trading()
        
        df = trading.price_board(symbols_list=symbols)
        
        assert isinstance(df, pd.DataFrame)

    def test_price_depth_single_symbol(self, diverse_test_symbols):
        """Test price_depth() for market depth data."""
        symbol = diverse_test_symbols['hose'][0]
        trading = Trading()
        
        try:
            df = trading.price_depth(symbol=symbol)
            assert isinstance(df, pd.DataFrame)
        except AttributeError:
            # price_depth may not be available
            pytest.skip("price_depth method not available")
        except Exception as e:
            print(f"price_depth not available: {e}")

    def test_price_board_empty_list(self):
        """Test price_board() with empty symbol list."""
        trading = Trading()
        
        try:
            df = trading.price_board(symbols_list=[])
            assert isinstance(df, pd.DataFrame)
        except Exception:
            # May raise error for empty list
            pass

    def test_price_board_invalid_symbols(self):
        """Test price_board() with invalid symbols."""
        trading = Trading()
        
        df = trading.price_board(
            symbols_list=['INVALID1', 'INVALID2']
        )
        
        # Should return DataFrame, possibly empty
        assert isinstance(df, pd.DataFrame)
