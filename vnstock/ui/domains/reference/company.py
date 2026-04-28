from typing import Any, Optional
from vnai import optimize_execution
from vnstock.ui._base import BaseDetailUI

class CompanyReference(BaseDetailUI):
    """Company-specific reference data."""
    def __call__(self, symbol: str) -> 'CompanyReference':
        """Allow calling the domain object with a symbol."""
        self.symbol = symbol
        return self

    @optimize_execution("UI")
    def info(self, source: str = 'kbs') -> Any:
        """Get company info/overview."""
        return self._dispatch('company', 'info', source=source)

    @optimize_execution("UI")
    def shareholders(self, source: str = 'kbs') -> Any:
        """Get list of major shareholders."""
        return self._dispatch('company', 'shareholders', source=source)

    @optimize_execution("UI")
    def officers(self, source: str = 'kbs') -> Any:
        """Get list of company officers/leadership."""
        return self._dispatch('company', 'officers', source=source)

    @optimize_execution("UI")
    def subsidiaries(self, source: str = 'kbs') -> Any:
        """Get list of subsidiaries and associated companies."""
        return self._dispatch('company', 'subsidiaries', source=source)

    @optimize_execution("UI")
    def ownership(self, source: str = 'kbs') -> Any:
        """Get company ownership structure."""
        return self._dispatch('company', 'ownership', source=source)

    @optimize_execution("UI")
    def insider_trading(self, source: str = 'kbs') -> Any:
        """Get insider trading history."""
        return self._dispatch('company', 'insider_trading', source=source)

    @optimize_execution("UI")
    def capital_history(self, source: str = 'kbs') -> Any:
        """Get capital change history."""
        return self._dispatch('company', 'capital_history', source=source)

    @optimize_execution("UI")
    def news(self, source: str = 'kbs') -> Any:
        """Get latest news related to the company."""
        return self._dispatch('company', 'news', source=source)

    @optimize_execution("UI")
    def events(self, source: str = 'kbs') -> Any:
        """Get upcoming corporate events."""
        return self._dispatch('company', 'events', source=source)
