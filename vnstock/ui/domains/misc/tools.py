from typing import Any

from vnstock.ui._base import BaseUI


class Misc(BaseUI):
    """Miscellaneous market tools."""

    def exchange_rate(self, date: str = "") -> Any:
        return self._dispatch("misc", "exchange_rate", date=date)

    def gold_price_sjc(self, date: str = None) -> Any:
        return self._dispatch("misc", "gold_price_sjc", date=date)

    def gold_price_btmc(self) -> Any:
        return self._dispatch("misc", "gold_price_btmc")
