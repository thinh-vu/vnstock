from typing import Any
from vnstock.ui._base import BaseDetailUI

class FuturesMarket(BaseDetailUI):
    """Futures market data."""
    def ohlcv(self, start: str = None, end: str = None, resolution: str = '1D', count: int = 100, source: str = 'kbs', **kwargs) -> Any:
        """Historical OHLCV bars for Futures."""
        # Fix interval clash
        interval = kwargs.pop('interval', resolution)
        return self._dispatch('Market', 'futures', 'ohlcv', start=start, end=end, interval=interval, count_back=count, source=source, **kwargs)

    def quote(self, source: str = 'kbs', **kwargs) -> Any:
        """Real-time pricing for Futures."""
        return self._dispatch('Market', 'futures', 'quote', source=source, **kwargs)

    def trades(self, source: str = 'kbs', **kwargs) -> Any:
        """Tick-by-tick trades for Futures."""
        # Handle interval clash
        kwargs.pop('interval', None)
        return self._dispatch('Market', 'futures', 'trades', source=source, **kwargs)

