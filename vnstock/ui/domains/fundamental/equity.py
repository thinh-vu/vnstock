from typing import Any
from vnstock.ui._base import BaseDetailUI

class EquityFundamental(BaseDetailUI):
    """Equity fundamental data."""
    def income_statement(self, period: str = 'fiscal_year') -> Any:
        """Get income statement."""
        return self._dispatch('equity_fundamental', 'income_statement', period=period)

    def balance_sheet(self, period: str = 'fiscal_year') -> Any:
        """Get balance sheet."""
        return self._dispatch('equity_fundamental', 'balance_sheet', period=period)

    def cash_flow(self, period: str = 'fiscal_year') -> Any:
        """Get cash flow statement."""
        return self._dispatch('equity_fundamental', 'cash_flow', period=period)

    def ratios(self) -> Any:
        """Get financial ratios."""
        return self._dispatch('equity_fundamental', 'ratios')
