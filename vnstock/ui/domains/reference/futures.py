from typing import Any
from vnstock.ui._base import BaseUI

class FuturesReference(BaseUI):
    """Access index futures reference data."""
    def __init__(self, symbol: str = None, **kwargs):
        super().__init__(**kwargs)
        self.symbol = symbol

    def __call__(self, symbol: str = None) -> 'FuturesReference':
        """Allow calling the domain object with a symbol."""
        self.symbol = symbol
        return self

    def info(self, symbol: str = None, source: str = 'kbs') -> Any:
        """Get information and contract specifications for a specific futures."""
        target = symbol or self.symbol
        return self._dispatch('Reference', 'futures', 'info', symbol=target, source=source)



    def list(self, source: str = 'kbs') -> Any:
        """List all futures instruments."""
        return self._dispatch('Reference', 'futures', 'list', source=source)
