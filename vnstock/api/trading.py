"""
vnstock/api/trading.py

Unified Trading adapter with dynamic method detection and parameter filtering.
"""

from typing import Any
from tenacity import retry, stop_after_attempt, wait_exponential
from vnstock.config import Config
from vnstock.base import BaseAdapter, dynamic_method


class Trading(BaseAdapter):
    _module_name = "trading"
    """
    Adapter for trading data: trading_stats, side_stats, price_board.

    Usage:
        t = Trading(source="vci", symbol="VCI", random_agent=False, show_log=True)
        df = t.trading_stats(start="2024-01-01", end="2024-12-31", limit=1000)
        bids, asks = t.side_stats(dropna=True)
        board = t.price_board(symbols_list=["VCI", "VCB"], **kwargs)
    """
    def __init__(
        self,
        source: str = "vci",
        symbol: str = None,
        random_agent: bool = False,
        show_log: bool = False
    ):
        # Store parameters for later use
        self.source = source
        self.symbol = symbol if symbol else ""
        self.random_agent = random_agent
        self.show_log = show_log
        
        # Validate to accept vci, tcbs as source
        if source.lower() not in ["vci", "tcbs"]:
            raise ValueError("Lớp Trading chỉ nhận giá trị tham số source là 'VCI' hoặc 'TCBS'.")
        
        super().__init__(
            source=source,
            symbol=symbol,
            random_agent=random_agent,
            show_log=show_log
        )

    @retry(
        stop=stop_after_attempt(Config.RETRIES),
        wait=wait_exponential(
            multiplier=Config.BACKOFF_MULTIPLIER,
            min=Config.BACKOFF_MIN,
            max=Config.BACKOFF_MAX
        )
    )
    @dynamic_method
    def trading_stats(self, *args: Any, **kwargs: Any) -> Any:
        """
        Retrieve trading statistics for the given symbol.
        """
        pass

    @retry(
        stop=stop_after_attempt(Config.RETRIES),
        wait=wait_exponential(
            multiplier=Config.BACKOFF_MULTIPLIER,
            min=Config.BACKOFF_MIN,
            max=Config.BACKOFF_MAX
        )
    )
    @dynamic_method
    def side_stats(self, *args: Any, **kwargs: Any) -> Any:
        """
        Retrieve bid/ask side statistics for the given symbol.
        """
        pass

    @retry(
        stop=stop_after_attempt(Config.RETRIES),
        wait=wait_exponential(
            multiplier=Config.BACKOFF_MULTIPLIER,
            min=Config.BACKOFF_MIN,
            max=Config.BACKOFF_MAX
        )
    )
    @dynamic_method
    def price_board(self, *args: Any, **kwargs: Any) -> Any:
        """
        Retrieve the price board (order book) for a list of symbols.
        """
        pass

    @retry(
        stop=stop_after_attempt(Config.RETRIES),
        wait=wait_exponential(
            multiplier=Config.BACKOFF_MULTIPLIER,
            min=Config.BACKOFF_MIN,
            max=Config.BACKOFF_MAX
        )
    )

    @dynamic_method
    def price_history(self, *args: Any, **kwargs: Any) -> Any:
        """
        Retrieve the price history for a list of symbols.
        """
        pass

    @retry(
        stop=stop_after_attempt(Config.RETRIES),
        wait=wait_exponential(
            multiplier=Config.BACKOFF_MULTIPLIER,
            min=Config.BACKOFF_MIN,
            max=Config.BACKOFF_MAX
        )
    )
        
    @dynamic_method
    def foreign_trade(self, *args: Any, **kwargs: Any) -> Any:
        """
        Retrieve foreign trade data for the given symbol.
        """
        pass

    @retry(
        stop=stop_after_attempt(Config.RETRIES),
        wait=wait_exponential(
            multiplier=Config.BACKOFF_MULTIPLIER,
            min=Config.BACKOFF_MIN,
            max=Config.BACKOFF_MAX
        )
    )
    @dynamic_method
    def prop_trade(self, *args: Any, **kwargs: Any) -> Any:
        """
        Retrieve property trade data for the given symbol.
        """
        pass

    @retry(
        stop=stop_after_attempt(Config.RETRIES),
        wait=wait_exponential(
            multiplier=Config.BACKOFF_MULTIPLIER,
            min=Config.BACKOFF_MIN,
            max=Config.BACKOFF_MAX
        )
    )
    @dynamic_method
    def insider_deal(self, *args: Any, **kwargs: Any) -> Any:
        """
        Retrieve insider deal data for the given symbol.
        """
        pass

    @retry(
        stop=stop_after_attempt(Config.RETRIES),
        wait=wait_exponential(
            multiplier=Config.BACKOFF_MULTIPLIER,
            min=Config.BACKOFF_MIN,
            max=Config.BACKOFF_MAX
        )
    )
    @dynamic_method
    def order_stats(self, *args: Any, **kwargs: Any) -> Any:
        """
        Retrieve order statistics for the given symbol.
        """
        pass
            
    def _delegate_to_provider(self, method_name: str, symbol: str = None, **kwargs: Any) -> Any:
        """
        Delegate method call to the provider with symbol update if needed.

        Args:
            method_name (str): Method name to call.
            symbol (str, optional): Symbol to use.
            **kwargs: Additional parameters.

        Returns:
            Any: Result from the provider.
        """
        # Standard vnstock implementation
        original_symbol = None
        try:
            if symbol:
                original_symbol = self.symbol
                self.symbol = symbol.upper()
                self._update_provider()
                
            # Get the method from the provider
            method = getattr(self.provider, method_name)
            return method(**kwargs)
        finally:
            if original_symbol:
                self.symbol = original_symbol
                self._update_provider()
