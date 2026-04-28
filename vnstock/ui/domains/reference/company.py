from typing import Any, Optional
from vnstock.ui._base import BaseDetailUI

class CompanyReference(BaseDetailUI):
    """Company-specific reference data."""
    def __call__(self, symbol: str) -> 'CompanyReference':
        """Allow calling the domain object with a symbol."""
        self.symbol = symbol
        return self

    def info(self, source: str = 'kbs') -> Any:
        """Get company info/overview."""
        return self._dispatch('company', 'info', source=source)

    def shareholders(self, source: str = 'kbs') -> Any:
        """Get list of major shareholders."""
        return self._dispatch('company', 'shareholders', source=source)

    def officers(self, source: str = 'kbs') -> Any:
        """Get list of company officers/leadership."""
        return self._dispatch('company', 'officers', source=source)

    def subsidiaries(self, source: str = 'kbs') -> Any:
        """Get list of subsidiaries and associated companies."""
        return self._dispatch('company', 'subsidiaries', source=source)

    def ownership(self, source: str = 'kbs') -> Any:
        """Get company ownership structure."""
        return self._dispatch('company', 'ownership', source=source)

    def insider_trading(self, source: str = 'kbs') -> Any:
        """Get insider trading history."""
        return self._dispatch('company', 'insider_trading', source=source)

    def capital_history(self, source: str = 'kbs') -> Any:
        """Get capital change history."""
        return self._dispatch('company', 'capital_history', source=source)

    def news(self, source: str = 'kbs') -> Any:
        """Get latest news related to the company."""
        return self._dispatch('company', 'news', source=source)

    def events(self, source: str = 'kbs') -> Any:
        """Get upcoming corporate events."""
        return self._dispatch('company', 'events', source=source)
