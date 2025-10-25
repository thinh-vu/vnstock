"""
FMP Quote connector for vnstock.

Module xử lý dữ liệu giá chứng khoán từ FMP API.
Following VCI patterns for consistency.
"""

import pandas as pd
from typing import Optional
from vnstock.core.base.registry import ProviderRegistry
from vnstock.core.types import DataCategory, ProviderType, TimeFrame
from vnstock.core.utils.interval import normalize_interval
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.transform import resample_ohlcv
from .config import FMPConfig, make_fmp_request
from .const import _OHLCV_MAP

logger = get_logger(__name__)


@ProviderRegistry.register(DataCategory.QUOTE, "fmp", ProviderType.API)
class Quote:
    """
    FMP Quote provider for vnstock.
    
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

    def realtime(self) -> Optional[pd.DataFrame]:
        """
        Lấy dữ liệu giá realtime cho mã chứng khoán.

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa dữ liệu giá realtime
        """
        url = self.config.get_endpoint_url('quote_short', self.symbol)
        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log or False)

        if df is not None and not df.empty:
            if 'symbol' in df.columns:
                df['symbol'] = df['symbol'].str.upper()

        return df

    def full_quote(self) -> Optional[pd.DataFrame]:
        """
        Lấy dữ liệu quote đầy đủ cho mã chứng khoán.

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa dữ liệu quote đầy đủ
        """
        url = self.config.get_endpoint_url('quote', self.symbol)
        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log or False)

        if df is not None and not df.empty:
            if 'symbol' in df.columns:
                df['symbol'] = df['symbol'].str.upper()

        return df

    def history(self, start: Optional[str] = None,
                end: Optional[str] = None,
                interval: str = '1D',
                adj_type: str = 'full') -> Optional[pd.DataFrame]:
        """
        Lấy dữ liệu lịch sử giá EOD chứng khoán.

        Phương thức này luôn trả về dữ liệu End-Of-Day. Hỗ trợ:
        - 1D: Dữ liệu daily trực tiếp từ API
        - 1W, 1M: Resample từ dữ liệu 1D

        Để lấy dữ liệu intraday, sử dụng phương thức intraday().

        Tham số:
            start (Optional[str]): Ngày bắt đầu (YYYY-MM-DD)
            end (Optional[str]): Ngày kết thúc (YYYY-MM-DD)
            interval (str): Khoảng thời gian EOD
                           - '1D': Daily (trực tiếp)
                           - '1W': Weekly (resample từ 1D)
                           - '1M': Monthly (resample từ 1D)
                           Mặc định: '1D'
            adj_type (str): Loại điều chỉnh giá
                           - 'light': Dữ liệu nhẹ
                           - 'full': Dữ liệu đầy đủ (default)
                           - 'non-split-adjusted': Không điều chỉnh tách
                           - 'dividend-adjusted': Điều chỉnh cổ tức
                         Mặc định: 'full'

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa dữ liệu EOD
        """
        # Normalize interval to standard format
        timeframe = normalize_interval(interval)
        
        # Chỉ hỗ trợ EOD intervals
        eod_intervals = [
            TimeFrame.DAY_1, 
            TimeFrame.WEEK_1, 
            TimeFrame.MONTH_1
        ]

        if timeframe not in eod_intervals:
            if self.show_log:
                logger.error(
                    f"Interval không hợp lệ: {timeframe}. "
                    f"history() chỉ hỗ trợ EOD: 1D, 1W, 1M. "
                    f"Dùng intraday() cho dữ liệu phút."
                )
            return None

        # Lấy dữ liệu 1D từ EOD endpoint
        url = (f"{self.config.domain}/historical-price-eod/"
               f"{adj_type}?symbol={self.symbol}&apikey="
               f"{self.config.api_key}")

        if start:
            url = f"{url}&from={start}"
        if end:
            url = f"{url}&to={end}"

        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log or False)

        if df is not None and not df.empty:
            # Chuẩn hóa tên cột theo vnstock standard
            df = self._normalize_ohlcv_columns(df)

            # Đảm bảo date column là datetime
            if 'time' in df.columns:
                df['time'] = pd.to_datetime(df['time'])
                df = df.sort_values('time', ascending=True)

                # Resample nếu cần 1W hoặc 1M
                if str(timeframe) in ['1W', '1M']:
                    df = resample_ohlcv(df, str(timeframe))

                df = df.reset_index(drop=True)

        return df

    def intraday(self, interval: str = '1min',
                 start: Optional[str] = None,
                 end: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Lấy dữ liệu intraday (dữ liệu theo phút/giờ) cho mã chứng khoán.

        Phương thức này luôn trả về dữ liệu intraday. Để lấy dữ liệu EOD,
        sử dụng phương thức history().

        Tham số:
            interval (str): Khoảng thời gian intraday
                           - '1min': 1 phút (default)
                           - '5min': 5 phút
                           - '15min': 15 phút
                           - '30min': 30 phút
                           - '1hour': 1 giờ
                           - '4hour': 4 giờ
            start (Optional[str]): Ngày bắt đầu (YYYY-MM-DD)
            end (Optional[str]): Ngày kết thúc (YYYY-MM-DD)

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa dữ liệu intraday
        """
        # Chỉ hỗ trợ intraday intervals
        intraday_intervals = ['1min', '5min', '15min', '30min',
                              '1hour', '4hour']

        if interval not in intraday_intervals:
            if self.show_log:
                logger.error(
                    f"Interval không hợp lệ: {interval}. "
                    f"intraday() chỉ hỗ trợ: {intraday_intervals}. "
                    f"Dùng history() cho dữ liệu EOD (1D, 1W, 1M)."
                )
            return None

        # Mapping interval to FMP endpoint
        interval_map = {
            '1min': 'historical-chart/1min',
            '5min': 'historical-chart/5min',
            '15min': 'historical-chart/15min',
            '30min': 'historical-chart/30min',
            '1hour': 'historical-chart/1hour',
            '4hour': 'historical-chart/4hour',
        }

        # Xây dựng URL:
        # https://financialmodelingprep.com/stable/historical-chart/1min
        interval_path = interval_map[interval]
        url = (f"{self.config.domain}/{interval_path}?"
               f"symbol={self.symbol}&apikey={self.config.api_key}")

        # Add date filters if provided
        if start:
            url = f"{url}&from={start}"
        if end:
            url = f"{url}&to={end}"

        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log or False)

        if df is not None and not df.empty:
            # Chuẩn hóa tên cột theo vnstock standard
            df = self._normalize_ohlcv_columns(df)

            # Đảm bảo date column là datetime
            if 'time' in df.columns:
                df['time'] = pd.to_datetime(df['time'])
                df = df.sort_values('time', ascending=True).reset_index(
                    drop=True)

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
