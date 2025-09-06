# vnstock/api/financial.py

from typing import Any
from tenacity import retry, stop_after_attempt, wait_exponential
from vnstock.config import Config
from vnstock.base import BaseAdapter, dynamic_method


class Finance(BaseAdapter):
    _module_name = "financial"
    """
    Adapter for financial reports:
      - balance_sheet
      - income_statement
      - cash_flow
      - ratio

    Usage:
        f = Finance(source="vci", symbol="VCI", period="quarter", get_all=True, show_log=True)
        df_bs = f.balance_sheet(period="annual", lang="en", dropna=True)
        df_is = f.income_statement(lang="vi")
        df_cf = f.cash_flow()
        df_rat = f.ratio(flatten_columns=True, separator="_")
    """

    def __init__(
        self,
        source: str,
        symbol: str,
        period: str = "quarter",
        get_all: bool = True,
        show_log: bool = False
    ):
        # Store parameters for later use
        self.source = source
        self.symbol = symbol if symbol else ""
        self.period = period
        self.get_all = get_all
        self.show_log = show_log
        
        # Validate the source to only accept vci or tcbs
        if source.lower() not in ["vci", "tcbs"]:
            raise ValueError("Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'TCBS'.")
        
        # BaseAdapter will discover vnstock.explorer.<real_source>.financial
        # and pass only the kwargs its __init__ accepts (symbol, period, get_all, show_log).
        super().__init__(
            source=source,
            symbol=symbol,
            period=period,
            get_all=get_all,
            show_log=show_log
        )

    @retry(
        stop=stop_after_attempt(Config.RETRIES),
        wait=wait_exponential(
            multiplier=Config.BACKOFF_MULTIPLIER,
            min=Config.BACKOFF_MIN,
            max=Config.BACKOFF_MAX
        )
    )
    @dynamic_method
    def balance_sheet(self, *args: Any, **kwargs: Any) -> Any:
        """Retrieve balance sheet data."""
        pass

    @retry(
        stop=stop_after_attempt(Config.RETRIES),
        wait=wait_exponential(
            multiplier=Config.BACKOFF_MULTIPLIER,
            min=Config.BACKOFF_MIN,
            max=Config.BACKOFF_MAX
        )
    )
    @dynamic_method
    def income_statement(self, *args: Any, **kwargs: Any) -> Any:
        """Retrieve income statement data."""
        pass

    @retry(
        stop=stop_after_attempt(Config.RETRIES),
        wait=wait_exponential(
            multiplier=Config.BACKOFF_MULTIPLIER,
            min=Config.BACKOFF_MIN,
            max=Config.BACKOFF_MAX
        )
    )
    @dynamic_method
    def cash_flow(self, *args: Any, **kwargs: Any) -> Any:
        """Retrieve cash flow data."""
        pass

    @retry(
        stop=stop_after_attempt(Config.RETRIES),
        wait=wait_exponential(
            multiplier=Config.BACKOFF_MULTIPLIER,
            min=Config.BACKOFF_MIN,
            max=Config.BACKOFF_MAX
        )
    )
    @dynamic_method
    def ratio(self, *args: Any, **kwargs: Any) -> Any:
        """Retrieve financial ratio data."""
        pass
        
    def _delegate_to_provider(self, method_name: str, symbol: str = None, **kwargs: Any) -> Any:
        """
        Delegate method call to the provider with symbol update if needed.

        Args:
            method_name (str): Method name to call.
            symbol (str, optional): Symbol to use.
            **kwargs: Additional parameters.

        Returns:
            Any: Result from the provider.
        """
        # Standard vnstock implementation
        original_symbol = None
        try:
            if symbol:
                original_symbol = self.symbol
                self.symbol = symbol.upper()
                self._update_provider()
                
            # Get the method from the provider
            method = getattr(self.provider, method_name)
            return method(**kwargs)
        finally:
            if original_symbol:
                self.symbol = original_symbol
                self._update_provider()
