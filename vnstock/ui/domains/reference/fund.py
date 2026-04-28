from typing import Any
from vnstock.ui._base import BaseUI

class FundReference(BaseUI):
    """Mutual fund reference data."""
    def __init__(self, symbol: str = None, **kwargs):
        super().__init__(**kwargs)
        self.symbol = symbol

    def __call__(self, symbol: str = None) -> 'FundReference':
        """Allow calling the domain object with a symbol."""
        self.symbol = symbol
        return self



    def list(self, source: str = 'kbs') -> Any:
        """List all funds."""
        return self._dispatch('Reference', 'fund', 'list', source=source)

    def top_holding(self, symbol: str = None, source: str = 'fmarket') -> Any:
        """Get top holdings for a specific fund."""
        target = symbol or self.symbol
        return self._dispatch('Reference', 'fund', 'top_holding', symbol=target, source=source)

    def industry_holding(self, symbol: str = None, source: str = 'fmarket') -> Any:
        """Get industry allocation for a specific fund."""
        target = symbol or self.symbol
        return self._dispatch('Reference', 'fund', 'industry_holding', symbol=target, source=source)

    def nav_report(self, symbol: str = None, source: str = 'fmarket') -> Any:
        """Get NAV growth report for a specific fund."""
        target = symbol or self.symbol
        return self._dispatch('Reference', 'fund', 'nav_report', symbol=target, source=source)

    def asset_holding(self, symbol: str = None, source: str = 'fmarket') -> Any:
        """Get asset allocation for a specific fund."""
        target = symbol or self.symbol
        return self._dispatch('Reference', 'fund', 'asset_holding', symbol=target, source=source)
