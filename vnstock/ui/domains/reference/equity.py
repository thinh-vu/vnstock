from typing import Any
from vnstock.ui._base import BaseUI

class EquityReference(BaseUI):
    """Equity symbols and grouping reference."""
    def __init__(self, symbol: str = None, **kwargs):
        super().__init__(**kwargs)
        self.symbol = symbol

    def __call__(self, symbol: str = None) -> 'EquityReference':
        """Allow calling the domain object with a symbol."""
        self.symbol = symbol
        return self


    def list(self, source: str = 'kbs') -> Any:
        """List all equity symbols."""
        return self._dispatch('Reference', 'equity', 'list', source=source)

    def list_by_industry(self, source: str = None) -> Any:
        """List equities grouped by ICB industry."""
        from vnstock.core.utils.env import is_colab
        if source is None:
            if is_colab():
                source = 'kbs'
                print("💡 Tip: Detect Google Colab environment. Switching to KBS as default source for industry data (VCI may block Google IP).")
            else:
                source = 'vci'
        return self._dispatch('Reference', 'equity', 'list_by_industry', source=source)

    def list_by_exchange(self, source: str = 'kbs') -> Any:
        """List symbols by exchange/board."""
        return self._dispatch('Reference', 'equity', 'list_by_exchange', source=source)

    def list_by_group(self, group: str = 'VN30', source: str = 'kbs') -> Any:
        """List equities by predefined group (e.g., VN30, HOSE)."""
        target = group or self.symbol
        return self._dispatch('Reference', 'equity', 'list_by_group', group=target, source=source)

