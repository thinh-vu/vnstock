from typing import TYPE_CHECKING, Any

from vnai import optimize_execution

from vnstock.ui._base import BaseUI

if TYPE_CHECKING:
    from vnstock.ui.domains.market.commodity_market import CommodityMarket
    from vnstock.ui.domains.market.crypto import CryptoMarket
    from vnstock.ui.domains.market.equity import EquityMarket
    from vnstock.ui.domains.market.etf import ETFMarket
    from vnstock.ui.domains.market.forex import ForexMarket
    from vnstock.ui.domains.market.fund import FundMarket
    from vnstock.ui.domains.market.futures import FuturesMarket
    from vnstock.ui.domains.market.index import IndexMarket
    from vnstock.ui.domains.market.warrant import WarrantMarket


class Market(BaseUI):
    """
    Market Data Layer (Layer 2).
    """

    @optimize_execution("UI")
    def quote(self, symbol: Any = None, **kwargs) -> Any:
        """Global real-time quote for one or more symbols."""
        if symbol is None:
            raise ValueError("Tham số 'symbol' là bắt buộc cho phương thức quote().")
        return self._dispatch("Market", "quote", symbols_list=symbol, **kwargs)

    @optimize_execution("UI")
    def equity(self, symbol: str = None, **kwargs) -> "EquityMarket":
        """Access equity market data."""
        from vnstock.ui.domains.market.equity import EquityMarket

        return EquityMarket(symbol=symbol, **kwargs)

    @optimize_execution("UI")
    def index(self, symbol: str = None, **kwargs) -> "IndexMarket":
        """Access index market data."""
        from vnstock.ui.domains.market.index import IndexMarket

        return IndexMarket(symbol=symbol, **kwargs)

    @optimize_execution("UI")
    def etf(self, symbol: str = None, **kwargs) -> "ETFMarket":
        """Access ETF market data."""
        from vnstock.ui.domains.market.etf import ETFMarket

        return ETFMarket(symbol=symbol, **kwargs)

    @optimize_execution("UI")
    def futures(self, symbol: str = None, **kwargs) -> "FuturesMarket":
        """Access futures market data."""
        from vnstock.ui.domains.market.futures import FuturesMarket

        return FuturesMarket(symbol=symbol, **kwargs)

    @optimize_execution("UI")
    def warrant(self, symbol: str = None, **kwargs) -> "WarrantMarket":
        """Access warrant market data."""
        from vnstock.ui.domains.market.warrant import WarrantMarket

        return WarrantMarket(symbol=symbol, **kwargs)

    @optimize_execution("UI")
    def fund(self, symbol: str = None, **kwargs) -> "FundMarket":
        """Access Mutual Fund market data."""
        from vnstock.ui.domains.market.fund import FundMarket

        return FundMarket(symbol=symbol, **kwargs)

    @optimize_execution("UI")
    def crypto(self, symbol: str = None, **kwargs) -> "CryptoMarket":
        """Access crypto market data."""
        from vnstock.ui.domains.market.crypto import CryptoMarket

        return CryptoMarket(symbol=symbol, **kwargs)

    @optimize_execution("UI")
    def forex(self, symbol: str = None, **kwargs) -> "ForexMarket":
        """Access forex market data."""
        from vnstock.ui.domains.market.forex import ForexMarket

        return ForexMarket(symbol=symbol, **kwargs)

    @optimize_execution("UI")
    def commodity(self, symbol: str = None, **kwargs) -> "CommodityMarket":
        """Access commodity market data."""
        from vnstock.ui.domains.market.commodity_market import CommodityMarket

        return CommodityMarket(symbol=symbol, **kwargs)
