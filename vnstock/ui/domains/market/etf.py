from typing import Any
from vnstock.ui._base import BaseDetailUI

class ETFMarket(BaseDetailUI):
    """ETF market data."""
    def ohlcv(self, start: str = None, end: str = None, resolution: str = '1D', count: int = 100, source: str = 'kbs', **kwargs) -> Any:
        """Historical OHLCV bars for ETFs."""
        # Fix interval clash
        interval = kwargs.pop('interval', resolution)
        return self._dispatch('Market', 'etf', 'ohlcv', start=start, end=end, interval=interval, count_back=count, source=source, **kwargs)

    def quote(self, source: str = 'kbs', **kwargs) -> Any:
        """Real-time pricing for ETFs."""
        return self._dispatch('Market', 'etf', 'quote', source=source, **kwargs)

    def trades(self, source: str = 'kbs', **kwargs) -> Any:
        """Tick-by-tick trades for ETFs."""
        # Handle interval clash
        kwargs.pop('interval', None)
        return self._dispatch('Market', 'etf', 'trades', source=source, **kwargs)

