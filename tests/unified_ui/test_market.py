import pytest

from vnstock.ui.domains.market.equity import EquityMarket
from vnstock.ui.market import Market


def test_market_instantiation():
    """Test Market class can be instantiated."""
    market = Market()
    assert market is not None


def test_market_equity_domain():
    """Test Market.equity() returns EquityMarket."""
    market = Market()
    equity = market.equity(symbol="FPT")
    assert isinstance(equity, EquityMarket)


def test_market_quote_missing_symbol():
    """Test Market.quote() raises ValueError when symbol is missing."""
    market = Market()
    with pytest.raises(ValueError, match="Tham số 'symbol' là bắt buộc"):
        market.quote()
