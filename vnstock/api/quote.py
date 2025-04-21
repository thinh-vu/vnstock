"""
vnstock/api/quote.py

Unified Quote adapter with dynamic method detection and parameter filtering.
"""

from typing import Any
from tenacity import retry, stop_after_attempt, wait_exponential
from vnstock.config import Config
from vnstock.base import BaseAdapter, dynamic_method


class Quote(BaseAdapter):
    _module_name = "quote"
    """
    Adapter for historical and intraday quote data.

    Usage:
        q = Quote(source="vci", symbol="VCI", random_agent=False, show_log=True)
        df = q.history(start="2024-01-01", end="2024-04-18", interval="1D")
        df2 = q.intraday(page_size=100)
        depth = q.price_depth()
    """
    def __init__(
        self,
        source: str = "vci",
        symbol: str = "",
        random_agent: bool = False,
        show_log: bool = False
    ):
        # Validate the source to only accept vci or tcbs or msn
        if source.lower() not in ["vci", "tcbs", "msn"]:
            raise ValueError("Lớp Quote chỉ nhận giá trị tham số source là 'VCI' hoặc 'TCBS' hoặc 'MSN'.")
        # BaseAdapter will discover vnstock.explorer.<real_source>.quote
        # and pass only the kwargs its __init__ accepts (symbol, random_agent, show_log).
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
    def history(self, *args: Any, **kwargs: Any) -> Any:
        """
        Load historical OHLC data for the symbol.

        Forwards only supported kwargs to provider.history().
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
    def intraday(self, *args: Any, **kwargs: Any) -> Any:
        """
        Load intraday trade data for the symbol.
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
    def price_depth(self, *args: Any, **kwargs: Any) -> Any:
        """
        Load price depth (order book) data for the symbol.
        """
        pass
