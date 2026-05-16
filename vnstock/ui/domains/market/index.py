from typing import Any

from vnai import optimize_execution

from vnstock.ui._base import BaseDetailUI


class IndexMarket(BaseDetailUI):
    """Index market data."""

    @optimize_execution("UI")
    def ohlcv(
        self,
        start: str = None,
        end: str = None,
        interval: str = "1D",
        count: int = 100,
        source: str = "kbs",
        **kwargs,
    ) -> Any:
        """Historical OHLCV bars for indices."""
        # Handle parameter aliases
        interval = kwargs.pop("resolution", interval)
        count_back = kwargs.pop("length", count)

        # Switch source for global indices if scope is global
        if self.params.get("scope") == "global" and source == "kbs":
            source = "msn"

        return self._dispatch(
            "Market",
            "index",
            "ohlcv",
            start=start,
            end=end,
            interval=interval,
            count_back=count_back,
            source=source,
            **kwargs,
        )
