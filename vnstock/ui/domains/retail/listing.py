from typing import Any, Optional

from vnstock.ui._base import BaseUI


class Retail(BaseUI):
    """Retail market data (Gold, Exchange Rates)."""

    def gold(self, source: str = "sjc", date: Optional[str] = None) -> Any:
        """
        Retrieve gold price from various sources.

        Args:
            source (str): 'sjc' or 'btmc'.
            date (str, optional): Date in format YYYY-MM-DD.
        """
        method = f"gold_price_{source.lower()}"
        return self._dispatch("retail", method, date=date)

    def exchange_rate(self, date: str = "") -> Any:
        """Get exchange rate from Vietcombank."""
        return self._dispatch("retail", "exchange_rate", date=date)
