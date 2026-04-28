from typing import Any
from vnstock.ui._base import BaseUI

class BondReference(BaseUI):
    """Bond/Debt reference data."""
    def __init__(self, symbol: str = None, **kwargs):
        super().__init__(**kwargs)
        self.symbol = symbol

    def __call__(self, symbol: str = None) -> 'BondReference':
        """Allow calling the domain object with a symbol."""
        self.symbol = symbol
        return self

    def list(self, bond_type: str = 'all', source: str = None) -> Any:

        """List all debt/bonds."""
        valid_types = ['all', 'corporate', 'government']
        if bond_type not in valid_types:
            raise ValueError(f"Invalid bond_type: {bond_type}. Must be one of {valid_types}.")
            
        if bond_type == 'corporate':
            return self._dispatch('Reference', 'bond', 'corporate', source=source)
        elif bond_type == 'government':
            return self._dispatch('Reference', 'bond', 'government', source=source)
            
        # If 'all', combine both
        import pandas as pd
        corp = self._dispatch('Reference', 'bond', 'corporate', source=source)
        try:
             gov = self._dispatch('Reference', 'bond', 'government', source=source)
        except Exception:
             gov = pd.Series(dtype='object')
             
        df_corp = pd.DataFrame({'symbol': corp, 'type': 'corporate'}) if not corp.empty else pd.DataFrame(columns=['symbol', 'type'])
        df_gov = pd.DataFrame({'symbol': gov, 'type': 'government'}) if not gov.empty else pd.DataFrame(columns=['symbol', 'type'])
        
        return pd.concat([df_corp, df_gov], ignore_index=True)

