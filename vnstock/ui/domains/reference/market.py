from typing import Any
from vnstock.ui._base import BaseUI

class MarketReference(BaseUI):
    """Market status and metadata."""
    def __init__(self, symbol: str = None, **kwargs):
        super().__init__(**kwargs)
        self.symbol = symbol

    def __call__(self, symbol: str = None) -> 'MarketReference':
        """Allow calling the domain object with a symbol."""
        self.symbol = symbol
        return self

    def status(self) -> Any:
        """Retrieve live stock market status (OPEN, CLOSED, etc.)."""
        return self._dispatch('Reference', 'market', 'status')
