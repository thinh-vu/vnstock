from typing import Any, Optional

from vnstock.ui._base import BaseUI


class Commodity(BaseUI):
    """Commodity market data (Gold, T-Bill)."""

    def gold(self, source: str = "sjc", date: Optional[str] = None) -> Any:
        """
        Retrieve gold price from various sources.

        Args:
            source (str): 'sjc' or 'btmc'.
            date (str, optional): Date in format YYYY-MM-DD.
        """
        method = f"gold_price_{source.lower()}"
        if source.lower() == "sjc":
            return self._dispatch("retail", method, date=date)
        return self._dispatch("retail", method)

    def exchange_rate(self, date: str = "") -> Any:
        """Get exchange rate from Vietcombank."""
        return self._dispatch("retail", "exchange_rate", date=date)


# Compatibility alias for Retail domain
class Retail(Commodity):
    pass
