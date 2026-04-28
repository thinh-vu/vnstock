from typing import Any, Optional
from vnstock.ui._base import BaseUI

class ListingReference(BaseUI):
    """Listing and market structure reference data."""
    def all_symbols(self, source: str = 'kbs') -> Any:
        """List all symbols currently trading."""
        return self._dispatch('listing', 'all_symbols', source=source)

    def industries(self, source: str = 'kbs') -> Any:
        """Get industry classification (ICB)."""
        return self._dispatch('listing', 'industries', source=source)
