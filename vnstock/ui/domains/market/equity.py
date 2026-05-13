from typing import Any, Optional

from vnai import optimize_execution

from vnstock.ui._base import BaseDetailUI


class EquityMarket(BaseDetailUI):
    """Equity market data."""

    @optimize_execution("UI")
    def ohlcv(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None,
        interval: str = "1D",
        count: int = 100,
        source: str = "kbs",
        **kwargs,
    ) -> Any:
        """Get historical OHLCV data."""
        # Handle parameter aliases
        interval = kwargs.pop("resolution", interval)
        count_back = kwargs.pop("length", count)
        return self._dispatch(
            "equity_market",
            "ohlcv",
            start=start,
            end=end,
            interval=interval,
            count_back=count_back,
            source=source,
            **kwargs,
        )

    @optimize_execution("UI")
    def trades(self, source: str = "kbs", **kwargs) -> Any:
        """Get intraday trades."""
        # Handle interval clash if any (intraday might use resolution/interval too)
        kwargs.pop("interval", None)
        return self._dispatch("equity_market", "trades", source=source, **kwargs)

    @optimize_execution("UI")
    def quote(self, source: str = "kbs", **kwargs) -> Any:
        """Get real-time quote snapshot."""
        return self._dispatch("equity_market", "quote", source=source, **kwargs)
