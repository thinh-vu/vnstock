from typing import Any

from vnai import optimize_execution

from vnstock.ui._base import BaseUI


class SearchReference(BaseUI):
    """Search functionality."""

    @optimize_execution("UI")
    def symbol(self, query: str, locale: str = None, limit: int = 10) -> Any:
        """Search for symbols matching the query."""
        return self._dispatch(
            "Reference", "search", "symbol", query=query, locale=locale, limit=limit
        )

    @optimize_execution("UI")
    def info(self, query: str, locale: str = None, limit: int = 10) -> Any:
        """Search for detailed asset information."""
        return self._dispatch(
            "Reference", "search", "info", query=query, locale=locale, limit=limit
        )
