"""
Module xử lý dữ liệu giá chứng khoán từ FMP API.
Following VCI patterns for consistency.
"""

import pandas as pd
from typing import Optional
from vnstock.core.utils.logger import get_logger
from vnai import optimize_execution
from .config import FMPConfig, make_fmp_request
from .const import _OHLCV_MAP

logger = get_logger(__name__)


class Quote:
    """
    Class xử lý dữ liệu giá chứng khoán từ FMP.
    """

    def __init__(self, symbol: str, api_key: Optional[str] = None,
                 show_log: Optional[bool] = True):
        """
        Khởi tạo Quote instance.

        Tham số:
            symbol (str): Mã chứng khoán (ticker symbol)
            api_key (Optional[str]): FMP API key
            show_log (Optional[bool]): Hiển thị log
        """
        self.symbol = symbol.upper()
        self.config = FMPConfig(api_key=api_key, show_log=show_log)
        self.show_log = show_log

    @optimize_execution(processing_label="Đang truy xuất dữ liệu giá realtime")
    def realtime(self) -> Optional[pd.DataFrame]:
        """
        Lấy dữ liệu giá realtime cho mã chứng khoán.

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa dữ liệu giá realtime
        """
        url = self.config.get_endpoint_url('quote_short', self.symbol)
        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log)

        if df is not None and not df.empty:
            if 'symbol' in df.columns:
                df['symbol'] = df['symbol'].str.upper()

        return df

    @optimize_execution(processing_label="Đang truy xuất dữ liệu giá full quote")
    def full_quote(self) -> Optional[pd.DataFrame]:
        """
        Lấy dữ liệu quote đầy đủ cho mã chứng khoán.

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa dữ liệu quote đầy đủ
        """
        url = self.config.get_endpoint_url('quote', self.symbol)
        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log)

        if df is not None and not df.empty:
            if 'symbol' in df.columns:
                df['symbol'] = df['symbol'].str.upper()

        return df

    @optimize_execution(processing_label="Đang truy xuất dữ liệu lịch sử")
    def history(self, start_date: Optional[str] = None,
                end_date: Optional[str] = None,
                period: str = 'daily') -> Optional[pd.DataFrame]:
        """
        Lấy dữ liệu lịch sử giá chứng khoán.

        Tham số:
            start_date (Optional[str]): Ngày bắt đầu (YYYY-MM-DD)
            end_date (Optional[str]): Ngày kết thúc (YYYY-MM-DD)
            period (str): Chu kỳ dữ liệu ('daily', 'weekly', 'monthly')
                         Mặc định: 'daily'

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa dữ liệu lịch sử
        """
        # Mapping period to FMP endpoint
        endpoint_map = {
            'daily': 'historical_chart_1day',
            '1D': 'historical_chart_1day',
            'weekly': 'historical_chart_1week',
            '1W': 'historical_chart_1week',
            'monthly': 'historical_chart_1month',
            '1M': 'historical_chart_1month',
        }

        if period not in endpoint_map:
            if self.show_log:
                logger.error(f"Period không hợp lệ: {period}")
            return None

        endpoint_name = endpoint_map[period]
        url = self.config.get_endpoint_url(endpoint_name, self.symbol)

        # Add date filters if provided
        if start_date:
            url = f"{url}&from={start_date}"
        if end_date:
            url = f"{url}&to={end_date}"

        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log)

        if df is not None and not df.empty:
            # Chuẩn hóa tên cột theo vnstock standard
            df = self._normalize_ohlcv_columns(df)

            # Đảm bảo date column là datetime
            if 'time' in df.columns:
                df['time'] = pd.to_datetime(df['time'])
                df = df.sort_values('time', ascending=True).reset_index(drop=True)

        return df

    @optimize_execution(processing_label="Đang truy xuất dữ liệu intraday")
    def intraday(self, interval: str = '1min',
                 start_date: Optional[str] = None,
                 end_date: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Lấy dữ liệu intraday cho mã chứng khoán.

        Tham số:
            interval (str): Khoảng thời gian ('1min', '5min', '15min',
                           '30min', '1hour', '4hour')
                           Mặc định: '1min'
            start_date (Optional[str]): Ngày bắt đầu (YYYY-MM-DD)
            end_date (Optional[str]): Ngày kết thúc (YYYY-MM-DD)

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa dữ liệu intraday
        """
        # Mapping interval to FMP endpoint
        interval_map = {
            '1min': 'historical_chart_1min',
            '5min': 'historical_chart_5min',
            '15min': 'historical_chart_15min',
            '30min': 'historical_chart_30min',
            '1hour': 'historical_chart_1hour',
            '4hour': 'historical_chart_4hour',
        }

        if interval not in interval_map:
            if self.show_log:
                logger.error(f"Interval không hợp lệ: {interval}")
            return None

        endpoint_name = interval_map[interval]
        url = self.config.get_endpoint_url(endpoint_name, self.symbol)

        # Add date filters if provided
        if start_date:
            url = f"{url}&from={start_date}"
        if end_date:
            url = f"{url}&to={end_date}"

        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log)

        if df is not None and not df.empty:
            # Chuẩn hóa tên cột theo vnstock standard
            df = self._normalize_ohlcv_columns(df)

            # Đảm bảo date column là datetime
            if 'time' in df.columns:
                df['time'] = pd.to_datetime(df['time'])
                df = df.sort_values('time', ascending=True).reset_index(drop=True)

        return df

    def _normalize_ohlcv_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Chuẩn hóa tên cột OHLCV theo vnstock standard.

        Tham số:
            df (pd.DataFrame): DataFrame cần chuẩn hóa

        Returns:
            pd.DataFrame: DataFrame đã chuẩn hóa
        """
        # Rename columns theo mapping
        rename_dict = {}
        for fmp_col, vnstock_col in _OHLCV_MAP.items():
            if fmp_col in df.columns:
                rename_dict[fmp_col] = vnstock_col

        if rename_dict:
            df = df.rename(columns=rename_dict)

        return df
