from typing import Any

from vnstock.ui._base import BaseDetailUI


class WarrantMarket(BaseDetailUI):
    """Covered warrant market data."""

    def ohlcv(
        self,
        start: str = None,
        end: str = None,
        resolution: str = "1D",
        count: int = 100,
        source: str = "kbs",
        **kwargs,
    ) -> Any:
        """Historical OHLCV bars for Warrants."""
        # Handle parameter aliases
        interval = kwargs.pop("interval", resolution)
        count_back = kwargs.pop("length", count)
        return self._dispatch(
            "Market",
            "warrant",
            "ohlcv",
            start=start,
            end=end,
            interval=interval,
            count_back=count_back,
            source=source,
            **kwargs,
        )

    def quote(self, source: str = "kbs", **kwargs) -> Any:
        """Real-time pricing for Warrants."""
        return self._dispatch("Market", "warrant", "quote", source=source, **kwargs)

    def trades(self, source: str = "kbs", **kwargs) -> Any:
        """Tick-by-tick trades for Warrants."""
        # Handle interval clash
        kwargs.pop("interval", None)
        return self._dispatch("Market", "warrant", "trades", source=source, **kwargs)
