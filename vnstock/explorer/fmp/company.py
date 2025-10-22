"""
Module xử lý thông tin công ty từ FMP API.
Following VCI patterns for consistency.
"""

import pandas as pd
from typing import Optional
from vnstock.core.utils.logger import get_logger
from vnai import optimize_execution
from .config import FMPConfig, make_fmp_request

logger = get_logger(__name__)


class Company:
    """
    Class xử lý thông tin công ty từ FMP.
    """

    def __init__(self, symbol: str, api_key: Optional[str] = None,
                 show_log: Optional[bool] = True):
        """
        Khởi tạo Company instance.

        Tham số:
            symbol (str): Mã chứng khoán (ticker symbol)
            api_key (Optional[str]): FMP API key
            show_log (Optional[bool]): Hiển thị log
        """
        self.symbol = symbol.upper()
        self.config = FMPConfig(api_key=api_key, show_log=show_log)
        self.show_log = show_log

    @optimize_execution(processing_label="Đang truy xuất hồ sơ công ty")
    def profile(self) -> Optional[pd.DataFrame]:
        """
        Lấy thông tin hồ sơ công ty.

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa thông tin hồ sơ công ty
        """
        url = self.config.get_endpoint_url('profile', self.symbol)
        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log)

        if df is not None and not df.empty:
            if 'symbol' in df.columns:
                df['symbol'] = df['symbol'].str.upper()

        return df

    @optimize_execution(processing_label="Đang truy xuất thông tin điều hành")
    def executives(self) -> Optional[pd.DataFrame]:
        """
        Lấy thông tin ban điều hành công ty.

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa thông tin điều hành
        """
        url = self.config.get_endpoint_url('key_executives', self.symbol)
        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log)

        return df

    @optimize_execution(processing_label="Đang truy xuất tin tức công ty")
    def news(self, limit: int = 50) -> Optional[pd.DataFrame]:
        """
        Lấy tin tức liên quan đến công ty.

        Tham số:
            limit (int): Số lượng tin tức tối đa. Mặc định: 50

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa tin tức
        """
        url = self.config.get_endpoint_url('stock_news', self.symbol)
        url = f"{url}&limit={limit}"

        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log)

        if df is not None and not df.empty:
            # Chuyển đổi publishedDate thành datetime
            if 'publishedDate' in df.columns:
                df['publishedDate'] = pd.to_datetime(df['publishedDate'])

        return df

    @optimize_execution(processing_label="Đang truy xuất sự kiện kinh tế")
    def events(self) -> Optional[pd.DataFrame]:
        """
        Lấy các sự kiện kinh tế của công ty (earnings, dividends, splits).

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa thông tin sự kiện
        """
        url = self.config.get_endpoint_url(
            'stock_calendar_events', self.symbol)
        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log)

        return df

    @optimize_execution(processing_label="Đang truy xuất phân tích giá")
    def analyst_estimates(self) -> Optional[pd.DataFrame]:
        """
        Lấy dự báo giá từ các nhà phân tích.

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa dự báo giá
        """
        url = self.config.get_endpoint_url('analyst_estimates', self.symbol)
        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log)

        if df is not None and not df.empty:
            if 'symbol' in df.columns:
                df['symbol'] = df['symbol'].str.upper()

        return df

    @optimize_execution(processing_label="Đang truy xuất rating công ty")
    def rating(self) -> Optional[pd.DataFrame]:
        """
        Lấy xếp hạng công ty.

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa xếp hạng
        """
        url = self.config.get_endpoint_url('rating', self.symbol)
        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log)

        if df is not None and not df.empty:
            if 'symbol' in df.columns:
                df['symbol'] = df['symbol'].str.upper()

        return df

    @optimize_execution(processing_label="Đang truy xuất lịch sử rating")
    def rating_history(self, limit: int = 100) -> Optional[pd.DataFrame]:
        """
        Lấy lịch sử xếp hạng công ty.

        Tham số:
            limit (int): Số lượng bản ghi tối đa. Mặc định: 100

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa lịch sử xếp hạng
        """
        url = self.config.get_endpoint_url('historical_rating', self.symbol)
        url = f"{url}&limit={limit}"

        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log)

        if df is not None and not df.empty:
            if 'symbol' in df.columns:
                df['symbol'] = df['symbol'].str.upper()
            # Chuyển đổi date thành datetime
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])

        return df
