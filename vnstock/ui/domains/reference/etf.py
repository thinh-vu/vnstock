from typing import Any
from vnstock.ui._base import BaseUI

class ETFReference(BaseUI):
    """ETF reference data."""
    def __init__(self, symbol: str = None, **kwargs):
        super().__init__(**kwargs)
        self.symbol = symbol

    def __call__(self, symbol: str = None) -> 'ETFReference':
        """Allow calling the domain object with a symbol."""
        self.symbol = symbol
        return self



    def list(self, source: str = 'kbs') -> Any:
        """List all Exchange-Traded Funds (ETFs)."""
        return self._dispatch('Reference', 'etf', 'list', source=source)
