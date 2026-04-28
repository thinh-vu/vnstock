from typing import Any
from vnstock.ui._base import BaseUI

class Market(BaseUI):
    """
    Market Data Layer (Layer 2).
    """
    def quote(self, symbol: Any = None, **kwargs) -> Any:
        """Global real-time quote for one or more symbols."""
        if symbol is None:
             raise ValueError("Tham số 'symbol' là bắt buộc cho phương thức quote().")
        return self._dispatch('Market', 'quote', symbols_list=symbol, **kwargs)
    def equity(self, symbol: str = None) -> 'EquityMarket':
        """Access equity market data."""
        from vnstock.ui.domains.market.equity import EquityMarket
        return EquityMarket(symbol=symbol)

    def index(self, symbol: str = None) -> 'IndexMarket':
        """Access index market data."""
        from vnstock.ui.domains.market.index import IndexMarket
        return IndexMarket(symbol=symbol)

    def etf(self, symbol: str = None) -> 'ETFMarket':
        """Access ETF market data."""
        from vnstock.ui.domains.market.etf import ETFMarket
        return ETFMarket(symbol=symbol)

    def futures(self, symbol: str = None) -> 'FuturesMarket':
        """Access futures market data."""
        from vnstock.ui.domains.market.futures import FuturesMarket
        return FuturesMarket(symbol=symbol)

    def warrant(self, symbol: str = None) -> 'WarrantMarket':
        """Access warrant market data."""
        from vnstock.ui.domains.market.warrant import WarrantMarket
        return WarrantMarket(symbol=symbol)

    def fund(self, symbol: str = None) -> 'FundMarket':
        """Access Mutual Fund market data."""
        from vnstock.ui.domains.market.fund import FundMarket
        return FundMarket(symbol=symbol)

    def crypto(self, symbol: str = None) -> 'CryptoMarket':
        """Access crypto market data."""
        from vnstock.ui.domains.market.crypto import CryptoMarket
        return CryptoMarket(symbol=symbol)

    def forex(self, symbol: str = None) -> 'ForexMarket':
        """Access forex market data."""
        from vnstock.ui.domains.market.forex import ForexMarket
        return ForexMarket(symbol=symbol)

    def commodity(self, symbol: str = None) -> 'CommodityMarket':
        """Access commodity market data."""
        from vnstock.ui.domains.market.commodity_market import CommodityMarket
        return CommodityMarket(symbol=symbol)
