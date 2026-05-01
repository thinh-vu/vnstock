from typing import Any

from vnai import optimize_execution

from vnstock.ui._base import BaseDetailUI


class ETFMarket(BaseDetailUI):
    """ETF market data."""

    @optimize_execution("UI")
    def ohlcv(
        self,
        start: str = None,
        end: str = None,
        resolution: str = "1D",
        count: int = 100,
        source: str = "kbs",
        **kwargs,
    ) -> Any:
        """Historical OHLCV bars for ETFs."""
        # Handle parameter aliases
        interval = kwargs.pop("interval", resolution)
        count_back = kwargs.pop("length", count)
        return self._dispatch(
            "Market",
            "etf",
            "ohlcv",
            start=start,
            end=end,
            interval=interval,
            count_back=count_back,
            source=source,
            **kwargs,
        )

    @optimize_execution("UI")
    def quote(self, source: str = "kbs", **kwargs) -> Any:
        """Real-time pricing for ETFs."""
        return self._dispatch("Market", "etf", "quote", source=source, **kwargs)

    @optimize_execution("UI")
    def trades(self, source: str = "kbs", **kwargs) -> Any:
        """Tick-by-tick trades for ETFs."""
        # Handle interval clash
        kwargs.pop("interval", None)
        return self._dispatch("Market", "etf", "trades", source=source, **kwargs)
