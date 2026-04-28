from typing import Any, Optional
from vnstock.ui._base import BaseDetailUI

class EquityMarket(BaseDetailUI):
    """Equity market data."""
    def ohlcv(self, start: Optional[str] = None, end: Optional[str] = None, resolution: str = '1D', count: int = 100, source: str = 'kbs', **kwargs) -> Any:
        """Get historical OHLCV data."""
        # Fix interval clash
        interval = kwargs.pop('interval', resolution)
        return self._dispatch('equity_market', 'ohlcv', start=start, end=end, interval=interval, count_back=count, source=source, **kwargs)

    def trades(self, source: str = 'kbs', **kwargs) -> Any:
        """Get intraday trades."""
        # Handle interval clash if any (intraday might use resolution/interval too)
        kwargs.pop('interval', None)
        return self._dispatch('equity_market', 'trades', source=source, **kwargs)

    def quote(self, source: str = 'kbs', **kwargs) -> Any:
        """Get real-time quote snapshot."""
        return self._dispatch('equity_market', 'quote', source=source, **kwargs)

