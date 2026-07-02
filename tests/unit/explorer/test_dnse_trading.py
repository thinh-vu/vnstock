"""
Unit tests for DNSE Trading explorer.

TDD baseline — these tests are red until the implementation is created.
"""

import pytest


@pytest.mark.unit
@pytest.mark.explorer
class TestDNSETradingInstantiation:
    """Basic instantiation tests for DNSE Trading."""

    def test_trading_instantiation(self):
        """DNSE Trading can be instantiated without a symbol."""
        from vnstock.explorer.dnse.trading import Trading

        t = Trading(show_log=False)
        assert t is not None
        assert t.data_source == "DNSE"

    def test_trading_instantiation_with_symbol(self):
        """DNSE Trading can be instantiated with a symbol."""
        from vnstock.explorer.dnse.trading import Trading

        t = Trading(symbol="ACB", show_log=False)
        assert t.symbol == "ACB"

    def test_provider_registered_after_import(self):
        """ProviderRegistry resolves 'trading'/'dnse' after module import."""
        import vnstock.explorer.dnse.trading  # noqa: F401 — triggers self-registration
        from vnstock.core.registry import ProviderRegistry

        cls = ProviderRegistry.get("trading", "dnse")
        assert cls is not None
        assert cls.__name__ == "Trading"

    def test_price_board_requires_symbols_list(self):
        """price_board() raises ValueError when symbols_list is empty."""
        from vnstock.explorer.dnse.trading import Trading

        t = Trading(show_log=False)
        with pytest.raises(ValueError):
            t.price_board(symbols_list=[])
