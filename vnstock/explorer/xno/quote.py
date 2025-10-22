"""
Module xử lý dữ liệu giá chứng khoán từ XNO API.
CHỈ SỬ DỤNG 2 ENDPOINTS RIÊNG CỦA XNO.
Following VCI patterns for consistency.
"""

import pandas as pd
from typing import Optional
from vnstock.core.utils.logger import get_logger
from vnai import optimize_execution
from .config import XNOConfig, make_xno_request, normalize_xno_dataframe
from .const import _OHLC_RENAME, _SUPPORTED_TIMEFRAMES

logger = get_logger(__name__)


class Quote:
    """
    Class xử lý dữ liệu giá chứng khoán từ XNO.
    Chỉ sử dụng 2 endpoints riêng: api-v2 và lambda.
    """

    def __init__(self, symbol: str, api_key: Optional[str] = None,
                 show_log: Optional[bool] = True):
        """
        Khởi tạo Quote instance.

        Tham số:
            symbol (str): Mã chứng khoán (ticker symbol)
            api_key (Optional[str]): XNO API key
            show_log (Optional[bool]): Hiển thị log
        """
        self.symbol = symbol.upper()
        self.config = XNOConfig(api_key=api_key, show_log=show_log)
        self.show_log = show_log

    @optimize_execution(
        processing_label="Đang truy xuất lịch sử từ XNO API v2"
    )
    def history(self, timeframe: str = 'd',
                start_date: Optional[str] = None,
                end_date: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Lấy dữ liệu lịch sử từ XNO API v2 endpoint.

        Tham số:
            timeframe (str): Khung thời gian ('m', 'h', 'd', 'w', 'M')
                            m = minute, h = hour, d = day,
                            w = week, M = month
                            Mặc định: 'd' (day)
            start_date (Optional[str]): Ngày bắt đầu (YYYY-MM-DD)
            end_date (Optional[str]): Ngày kết thúc (YYYY-MM-DD)

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa OHLCV data
        """
        if timeframe not in _SUPPORTED_TIMEFRAMES:
            if self.show_log:
                logger.error(
                    f"Timeframe không hợp lệ: {timeframe}. "
                    f"Chọn từ: {_SUPPORTED_TIMEFRAMES}"
                )
            return None

        # Build URL - XNO API v2 endpoint
        # Format: /quant-data/v1/stocks/{symbol}/ohlcv/{resolution}
        url = (f"{self.config.api_base}/quant-data/v1/stocks/"
               f"{self.symbol}/ohlcv/{timeframe}")
        headers = self.config.get_headers()

        # Build params
        params = {}
        if start_date:
            # Convert to unix timestamp
            import pandas as pd
            params['from'] = int(pd.Timestamp(start_date).timestamp())
        else:
            params['from'] = 0

        if end_date:
            import pandas as pd
            params['to'] = int(pd.Timestamp(end_date).timestamp())
        else:
            params['to'] = 9999999999

        # Build query string
        query_str = '&'.join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{url}?{query_str}"

        # Make request
        df = make_xno_request(
            full_url,
            headers=headers,
            timeout=self.config.timeout,
            show_log=self.show_log
        )

        if df is not None and not df.empty:
            # Rename columns theo vnstock standard
            df = self._normalize_ohlcv_columns(df)

            # Normalize dates
            df = normalize_xno_dataframe(df, show_log=self.show_log)

            # Sort by date
            if 'time' in df.columns:
                df = df.sort_values('time').reset_index(drop=True)

        return df

    @optimize_execution(
        processing_label="Đang truy xuất dữ liệu chart từ XNO Lambda"
    )
    def chart(self, start_date: Optional[str] = None,
              end_date: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Lấy dữ liệu chart từ XNO Lambda endpoint.

        Tham số:
            start_date (Optional[str]): Ngày bắt đầu (YYYY-MM-DD)
            end_date (Optional[str]): Ngày kết thúc (YYYY-MM-DD)

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa dữ liệu chart
        """
        # Build URL - XNO Lambda endpoint
        url = f"{self.config.lambda_base}/chart/OHLCChart/gap-chart"
        headers = self.config.get_headers()

        # Build params
        params = {'symbol': self.symbol}

        if start_date:
            params['from'] = start_date
        if end_date:
            params['to'] = end_date

        # Build query string
        query_str = '&'.join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{url}?{query_str}"

        # Make request
        df = make_xno_request(
            full_url,
            headers=headers,
            timeout=self.config.timeout,
            show_log=self.show_log
        )

        if df is not None and not df.empty:
            # Rename columns theo vnstock standard
            df = self._normalize_ohlcv_columns(df)

            # Normalize dates
            df = normalize_xno_dataframe(df, show_log=self.show_log)

            # Sort by date
            if 'time' in df.columns:
                df = df.sort_values('time').reset_index(drop=True)

        return df

    def _normalize_ohlcv_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Chuẩn hóa tên cột OHLCV theo vnstock standard.

        Tham số:
            df (pd.DataFrame): DataFrame cần chuẩn hóa

        Returns:
            pd.DataFrame: DataFrame đã chuẩn hóa
        """
        # Rename columns nếu có trong mapping
        rename_dict = {}
        for xno_col, vnstock_col in _OHLC_RENAME.items():
            if xno_col in df.columns:
                rename_dict[xno_col] = vnstock_col

        if rename_dict:
            df = df.rename(columns=rename_dict)

        # Convert epoch timestamp to datetime for 'time' column
        if 'time' in df.columns:
            # Check if it's numeric (epoch)
            if pd.api.types.is_numeric_dtype(df['time']):
                # Determine if it's seconds or milliseconds
                sample = df['time'].dropna().iloc[0] if len(df) > 0 else 0
                unit = 'ms' if sample > 10_000_000_000 else 's'
                df['time'] = pd.to_datetime(df['time'], unit=unit, errors='coerce')

        # Ensure numeric columns
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Ensure column order
        standard_cols = ['time', 'open', 'high', 'low', 'close', 'volume']
        existing_cols = [c for c in standard_cols if c in df.columns]
        other_cols = [c for c in df.columns if c not in standard_cols]

        df = df[existing_cols + other_cols]

        return df
