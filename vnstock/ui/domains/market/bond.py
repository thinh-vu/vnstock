from typing import Any, Optional

from vnai import optimize_execution

from vnstock.ui._base import BaseDetailUI


class BondMarket(BaseDetailUI):
    """Bond market data."""

    @optimize_execution("UI")
    def ohlcv(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None,
        resolution: str = "1D",
        count: int = 100,
        source: str = "kbs",
        **kwargs,
    ) -> Any:
        """Get historical OHLCV data."""
        interval = kwargs.pop("interval", resolution)
        count_back = kwargs.pop("length", count)
        return self._dispatch(
            "bond_market",
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
        kwargs.pop("interval", None)
        return self._dispatch("bond_market", "trades", source=source, **kwargs)

    @optimize_execution("UI")
    def quote(self, source: str = "kbs", **kwargs) -> Any:
        """Get real-time quote snapshot."""
        return self._dispatch("bond_market", "quote", source=source, **kwargs)
