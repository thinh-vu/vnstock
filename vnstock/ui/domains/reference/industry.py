from typing import Any
from vnstock.ui._base import BaseUI

class IndustryReference(BaseUI):
    """Industry classification reference."""
    def __init__(self, symbol: str = None, **kwargs):
        super().__init__(**kwargs)
        self.symbol = symbol

    def __call__(self, symbol: str = None) -> 'IndustryReference':
        """Allow calling the domain object with a symbol."""
        self.symbol = symbol
        return self

    def list(self, source: str = None) -> Any:
        """Get industry classification (ICB)."""
        from vnstock.core.utils.env import is_colab
        if source is None:
            if is_colab():
                source = 'kbs'
            else:
                source = 'vci'
        return self._dispatch('Reference', 'industry', 'list', source=source)


    def sectors(self, source: str = 'kbs') -> Any:
        """List symbols grouped by industry sectors."""
        return self._dispatch('Reference', 'industry', 'sectors', source=source)

