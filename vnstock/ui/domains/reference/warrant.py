from typing import Any
from vnai import optimize_execution
from vnstock.ui._base import BaseUI

class WarrantReference(BaseUI):
    """Access covered warrant reference data."""
    def __init__(self, symbol: str = None, **kwargs):
        super().__init__(**kwargs)
        self.symbol = symbol

    def __call__(self, symbol: str = None) -> 'WarrantReference':
        """Allow calling the domain object with a symbol."""
        self.symbol = symbol
        return self





    @optimize_execution("UI")
    def list(self, source: str = 'kbs') -> Any:
        """List all covered warrants."""
        return self._dispatch('Reference', 'warrant', 'list', source=source)
