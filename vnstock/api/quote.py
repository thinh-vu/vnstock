"""
vnstock/api/quote.py

Unified Quote adapter with dynamic method detection and parameter filtering.
Module quản lý dữ liệu giá chứng khoán với phát hiện phương thức động và lọc tham số.
"""

from typing import Any, Optional
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential
from vnstock.config import Config
from vnstock.base import BaseAdapter, dynamic_method
from vnstock.core.types import (
    ParameterNames as P,
    MethodNames as M,
    DataSource,
    TimeFrame,
)

# Backward compatibility aliases
DataSources = DataSource
TimeResolutions = TimeFrame


class Quote(BaseAdapter):
    _module_name = "quote"
    """
    Adapter for historical and intraday quote data.
    Bộ điều hợp dữ liệu giá lịch sử và trong ngày.

    Usage/Cách sử dụng:
        q = Quote(source="vci", symbol="VCI", random_agent=False, show_log=True)
        df = q.history(start_date="2024-01-01", end_date="2024-04-18", resolution=TimeResolutions.DAILY)
        df2 = q.intraday(page_size=100)
        depth = q.price_depth()
    """
    def __init__(
        self,
        source: str = DataSources.VCI,
        symbol: str = "",
        random_agent: bool = False,
        show_log: bool = False
    ):
        """
        Initialize a Quote instance.
        Khởi tạo một đối tượng Quote.

        Args:
            source (str): Data source (VCI, TCBS, MSN). Nguồn dữ liệu (VCI, TCBS, MSN).
            symbol (str): Stock symbol. Mã chứng khoán.
            random_agent (bool): Use random user agent for requests. Sử dụng user agent ngẫu nhiên cho các yêu cầu.
            show_log (bool): Show log messages. Hiển thị thông báo nhật ký.
        """
        # Store parameters for later use
        self.source = source
        self.symbol = symbol if symbol else ""
        self.random_agent = random_agent
        self.show_log = show_log
        
        # Validate the source to only accept vci or tcbs or msn
        all_sources = DataSources.all_sources()
        if source.lower() not in [s.lower() for s in all_sources]:
            sources_str = ', '.join(all_sources)
            raise ValueError(
                f"Lớp Quote chỉ nhận giá trị tham số source là {sources_str}."
            )
        
        # BaseAdapter will discover vnstock.explorer.<real_source>.quote
        # and pass only the kwargs its __init__ accepts (symbol, random_agent, show_log).
        super().__init__(
            source=source,
            symbol=symbol,
            random_agent=random_agent,
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
    def history(self, symbol: Optional[str] = None, start: str = None, end: str = None, 
               interval: str = TimeResolutions.DAILY, **kwargs: Any) -> pd.DataFrame:
        """
        Load historical OHLC data for the symbol.
        Tải dữ liệu OHLC lịch sử cho mã chứng khoán.

        Args:
            symbol (str, optional): Stock symbol. Mã chứng khoán.
            start (str): Start time in format YYYY-MM-DD or YYYY-MM-DD HH:MM:SS.
                        Thời gian bắt đầu định dạng YYYY-MM-DD hoặc YYYY-MM-DD HH:MM:SS.
            end (str): End time in format YYYY-MM-DD or YYYY-MM-DD HH:MM:SS.
                      Thời gian kết thúc định dạng YYYY-MM-DD hoặc YYYY-MM-DD HH:MM:SS.
            interval (str, optional): Data interval (1m, 5m, 15m, 30m, 1H, D, 1W, 1M).
                                     Khoảng thời gian dữ liệu (1m, 5m, 15m, 30m, 1H, D, 1W, 1M).

        Returns:
            pandas.DataFrame: Historical price data. Dữ liệu giá lịch sử.
            
        Examples:
            >>> quote = Quote(symbol="VCI", source="vci")
            >>> df = quote.history(start="2024-01-01", end="2024-04-18")
            >>> df = quote.history(symbol="FPT", start="2024-01-01", end="2024-04-18", interval=TimeResolutions.WEEKLY)
            >>> df = quote.history(symbol="FPT", start="2024-01-01 09:00:00", end="2024-01-01 14:30:00", interval=TimeResolutions.MINUTE_5)
        """
        # Support for backward compatibility with old parameter names
        if 'resolution' in kwargs:
            interval = kwargs.pop('resolution')
            
        # Prepare parameters
        params = {}
        if start:
            params[P.START] = start
        if end:
            params[P.END] = end
        if interval:
            params[P.INTERVAL] = interval
            
        # Add any remaining kwargs
        params.update(kwargs)
            
        return self._delegate_to_provider(M.HISTORY, symbol, **params)

    @retry(
        stop=stop_after_attempt(Config.RETRIES),
        wait=wait_exponential(
            multiplier=Config.BACKOFF_MULTIPLIER,
            min=Config.BACKOFF_MIN,
            max=Config.BACKOFF_MAX
        )
    )
    @dynamic_method
    def intraday(self, symbol: Optional[str] = None, page_size: int = 100, page: int = 1, **kwargs: Any) -> pd.DataFrame:
        """
        Load intraday trade data for the symbol.
        Tải dữ liệu giao dịch trong ngày cho mã chứng khoán.

        Args:
            symbol (str, optional): Stock symbol. Mã chứng khoán.
            page_size (int, optional): Number of records to return. Số lượng bản ghi trả về.
            page (int, optional): Page number. Số trang.

        Returns:
            pandas.DataFrame: Intraday trade data. Dữ liệu giao dịch trong ngày.
            
        Examples:
            >>> quote = Quote(symbol="VCI", source="vci")
            >>> df = quote.intraday()
            >>> df = quote.intraday(symbol="FPT", page_size=200)
        """
        # Prepare parameters
        params = {
            P.PAGE_SIZE: page_size,
            P.PAGE: page
        }
        
        # Add any remaining kwargs
        params.update(kwargs)
        
        return self._delegate_to_provider(M.INTRADAY, symbol, **params)

    @retry(
        stop=stop_after_attempt(Config.RETRIES),
        wait=wait_exponential(
            multiplier=Config.BACKOFF_MULTIPLIER,
            min=Config.BACKOFF_MIN,
            max=Config.BACKOFF_MAX
        )
    )
    @dynamic_method
    def price_depth(self, symbol: Optional[str] = None, **kwargs: Any) -> pd.DataFrame:
        """
        Load price depth (order book) data for the symbol.
        Tải dữ liệu độ sâu giá (sổ lệnh) cho mã chứng khoán.

        Args:
            symbol (str, optional): Stock symbol. Mã chứng khoán.

        Returns:
            pandas.DataFrame: Price depth data. Dữ liệu độ sâu giá.
            
        Examples:
            >>> quote = Quote(symbol="VCI", source="vci")
            >>> df = quote.price_depth()
            >>> df = quote.price_depth(symbol="FPT")
        """
        return self._delegate_to_provider(M.PRICE_DEPTH, symbol, **kwargs)
        
    def _delegate_to_provider(self, method_name: str, symbol: Optional[str] = None, **kwargs: Any) -> Any:
        """
        Delegate method call to the provider with symbol update if needed.
        Ủy thác cuộc gọi phương thức cho nhà cung cấp với cập nhật mã chứng khoán nếu cần.

        Args:
            method_name (str): Method name to call. Tên phương thức cần gọi.
            symbol (str, optional): Symbol to use. Mã chứng khoán cần sử dụng.
            **kwargs: Additional parameters. Các tham số bổ sung.

        Returns:
            Any: Result from the provider. Kết quả từ nhà cung cấp.
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
