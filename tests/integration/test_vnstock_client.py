"""
Integration tests for Vnstock main client interface.

Tests end-to-end workflows using the Vnstock class.
"""

import pytest
from vnstock import Vnstock


@pytest.mark.integration
class TestVnstockClient:
    """Test suite for Vnstock main client."""

    def test_vnstock_instantiation(self):
        """Test Vnstock can be instantiated."""
        stock = Vnstock(show_log=False)
        assert stock is not None

    def test_vnstock_stock_method(self):
        """Test Vnstock.stock() method."""
        stock = Vnstock(show_log=False)
        acb = stock.stock('ACB', source='VCI')
        assert acb is not None
        assert hasattr(acb, 'quote')
        assert hasattr(acb, 'company')
        assert hasattr(acb, 'finance')

    def test_vnstock_stock_components_quote(self):
        """Test StockComponents has working quote component."""
        stock = Vnstock(show_log=False)
        acb = stock.stock('ACB', source='VCI')
        assert hasattr(acb.quote, 'history')

    def test_vnstock_stock_components_company(self):
        """Test StockComponents has working company component."""
        stock = Vnstock(show_log=False)
        acb = stock.stock('ACB', source='VCI')
        assert hasattr(acb.company, 'overview')
        assert hasattr(acb.company, 'profile')

    def test_vnstock_stock_components_finance(self):
        """Test StockComponents has working finance component."""
        stock = Vnstock(show_log=False)
        acb = stock.stock('ACB', source='VCI')
        assert hasattr(acb.finance, 'balance_sheet')
        assert hasattr(acb.finance, 'income_statement')
        assert hasattr(acb.finance, 'cash_flow')

    def test_vnstock_supported_sources(self):
        """Test Vnstock supports expected sources."""
        expected_sources = ['VCI', 'TCBS', 'MSN']
        assert Vnstock.SUPPORTED_SOURCES == expected_sources

    @pytest.mark.parametrize("source", ['VCI', 'TCBS'])
    def test_vnstock_stock_with_different_sources(self, source):
        """Test Vnstock.stock() works with different sources."""
        stock = Vnstock(show_log=False)
        acb = stock.stock('ACB', source=source)
        assert acb is not None
        assert acb.source.upper() == source

    def test_vnstock_fx_method(self):
        """Test Vnstock.fx() method for forex data."""
        stock = Vnstock(show_log=False)
        fx = stock.fx('USDVND', source='MSN')
        assert fx is not None
        assert hasattr(fx, 'quote')

    def test_vnstock_crypto_method(self):
        """Test Vnstock.crypto() method."""
        stock = Vnstock(show_log=False)
        btc = stock.crypto('BTC')
        assert btc is not None
        assert hasattr(btc, 'quote')

    def test_vnstock_world_index_method(self):
        """Test Vnstock.world_index() method."""
        stock = Vnstock(show_log=False)
        dji = stock.world_index('DJI')
        assert dji is not None
        assert hasattr(dji, 'quote')
