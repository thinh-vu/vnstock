from typing import Any
from vnstock.ui._base import BaseDetailUI

class FundMarket(BaseDetailUI):
    """Mutual Fund market data and compositions."""
    def nav(self, **kwargs) -> Any:
        """Historical NAVs for the fund."""
        return self._dispatch('Market', 'fund', 'nav', **kwargs)

    def history(self, **kwargs) -> Any:
        """Historical NAVs for the fund (alias for nav)."""
        return self._dispatch('Market', 'fund', 'history', **kwargs)

    def top_holding(self, **kwargs) -> Any:
        """Top holdings of the fund."""
        return self._dispatch('Market', 'fund', 'top_holding', **kwargs)

    def industry_holding(self, **kwargs) -> Any:
        """Industry allocation of the fund."""
        return self._dispatch('Market', 'fund', 'industry_holding', **kwargs)
    
    def asset_holding(self, **kwargs) -> Any:
        """Asset class allocation of the fund."""
        return self._dispatch('Market', 'fund', 'asset_holding', **kwargs)
