from typing import Any, Optional
from vnstock.ui._base import BaseDetailUI

class IndexMarket(BaseDetailUI):
    """Index market data."""
    def ohlcv(self, start: Optional[str] = None, end: Optional[str] = None, resolution: str = '1D', count: int = 100, source: str = 'kbs', **kwargs) -> Any:
        """Historical OHLCV bars for indices."""
        # Fix interval clash
        interval = kwargs.pop('interval', resolution)
        return self._dispatch('Market', 'index', 'ohlcv', start=start, end=end, interval=interval, count_back=count, source=source, **kwargs)



