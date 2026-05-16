from typing import Any

from vnai import optimize_execution

from vnstock.ui._base import BaseDetailUI


class CommodityMarket(BaseDetailUI):
    """Commodity market data (e.g., Gold, Oil)."""

    @optimize_execution("UI")
    def ohlcv(
        self,
        start: str = None,
        end: str = None,
        interval: str = "1D",
        count: int = 100,
        source: str = "msn",
        **kwargs,
    ) -> Any:
        """Historical OHLCV for commodities."""
        # Handle parameter aliases
        interval = kwargs.pop("resolution", interval)
        count_back = kwargs.pop("length", count)
        return self._dispatch(
            "Market",
            "commodity",
            "ohlcv",
            start=start,
            end=end,
            interval=interval,
            count_back=count_back,
            source=source,
            **kwargs,
        )
