from typing import Any

import pandas as pd
from vnai import optimize_execution

from vnstock.ui._base import BaseDetailUI


class EquityFundamental(BaseDetailUI):
    """Equity fundamental data."""

    def _format_output(self, df: pd.DataFrame, orient: str = "report") -> pd.DataFrame:
        """Helper to format the financial DataFrame based on orientation."""
        if df.empty:
            return df

        # Clean up period names: replace '-Năm' with ''
        period_cols = getattr(df, "attrs", {}).get("periods", [])
        if not period_cols:
            # Fallback: all columns except known metadata
            metadata_cols = [
                "item",
                "item_en",
                "unit",
                "levels",
                "row_number",
                "item_id",
            ]
            period_cols = [c for c in df.columns if c not in metadata_cols]

        # Keep only the valid period columns that exist
        period_cols = [c for c in period_cols if c in df.columns]

        rename_dict = {}
        for p in period_cols:
            if isinstance(p, str) and p.endswith("-Năm"):
                rename_dict[p] = p.replace("-Năm", "")

        if rename_dict:
            df = df.rename(columns=rename_dict)
            if hasattr(df, "attrs") and "periods" in df.attrs:
                df.attrs["periods"] = [
                    rename_dict.get(p, p) for p in df.attrs["periods"]
                ]
            period_cols = [rename_dict.get(p, p) for p in period_cols]

        if orient == "time_series" and "item_id" in df.columns:
            # Set 'item_id' as index temporarily
            df_t = df.set_index("item_id")

            if period_cols:
                # Transpose only the period columns
                df_t = df_t[period_cols].transpose()

                # Reset index to make period a column
                df_t = df_t.reset_index()
                # Rename 'index' to 'period'
                df_t = df_t.rename(columns={"index": "period"})

                # Add ticker
                if hasattr(self, "symbol") and self.symbol:
                    df_t.insert(1, "ticker", self.symbol)

                # Sort ascending by period
                df = df_t.sort_values("period").reset_index(drop=True)

        return df

    @optimize_execution("UI")
    def income_statement(
        self, period: str = "year", orient: str = "report", **kwargs
    ) -> Any:
        """Get income statement."""
        df = self._dispatch(
            "Fundamental", "equity", "income_statement", period=period, **kwargs
        )
        if isinstance(df, pd.DataFrame):
            return self._format_output(df, orient)
        return df

    @optimize_execution("UI")
    def balance_sheet(
        self, period: str = "year", orient: str = "report", **kwargs
    ) -> Any:
        """Get balance sheet."""
        df = self._dispatch(
            "Fundamental", "equity", "balance_sheet", period=period, **kwargs
        )
        if isinstance(df, pd.DataFrame):
            return self._format_output(df, orient)
        return df

    @optimize_execution("UI")
    def cash_flow(self, period: str = "year", orient: str = "report", **kwargs) -> Any:
        """Get cash flow statement."""
        df = self._dispatch(
            "Fundamental", "equity", "cash_flow", period=period, **kwargs
        )
        if isinstance(df, pd.DataFrame):
            return self._format_output(df, orient)
        return df

    @optimize_execution("UI")
    def ratio(self, orient: str = "report", **kwargs) -> Any:
        """Get financial ratios."""
        df = self._dispatch("Fundamental", "equity", "ratio", **kwargs)
        if isinstance(df, pd.DataFrame):
            return self._format_output(df, orient)
        return df

    @optimize_execution("UI")
    def ratios(self, orient: str = "report", **kwargs) -> Any:
        """Get financial ratios (alias)."""
        return self.ratio(orient=orient, **kwargs)
