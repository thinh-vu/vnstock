"""History module for MSN."""

# Đồ thị giá, đồ thị dư mua dư bán, đồ thị mức giá vs khối lượng, thống kê
# hành vi thị tường
import pandas as pd
import requests
from datetime import datetime
from typing import Optional, Dict
from vnai import optimize_execution
from vnstock.core.types import TimeFrame
from vnstock.core.utils.interval import normalize_interval
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.user_agent import get_headers
from vnstock.explorer.msn.listing import Listing
from vnstock.explorer.msn.helper import msn_apikey
from vnstock.core.models import TickerModel
from vnstock.explorer.msn.helper import get_asset_type
from .const import _BASE_URL, _RESAMPLE_MAP, _OHLC_MAP, _OHLC_DTYPE, _CRYPTO_ID_MAP, _CURRENCY_ID_MAP, _GLOBAL_INDICES

logger = get_logger(__name__)


class Quote:
    """
    MSN data source for fetching stock market data, accommodating requests with large date ranges.
    """
    def __init__(self, symbol_id:str, api_version='20240430', random_agent:Optional[bool]=False):
        self.data_source = 'MSN'
        symbol_id_upper = symbol_id.upper()
        # Resolve SecId from common maps if symbol is passed instead of ID
        if symbol_id_upper in _CRYPTO_ID_MAP:
            self.symbol_id = _CRYPTO_ID_MAP[symbol_id_upper]
        elif symbol_id_upper in _CURRENCY_ID_MAP:
            self.symbol_id = _CURRENCY_ID_MAP[symbol_id_upper]
        elif symbol_id_upper in _GLOBAL_INDICES:
            self.symbol_id = _GLOBAL_INDICES[symbol_id_upper]
        else:
            self.symbol_id = symbol_id.lower()
            
        self.asset_type = get_asset_type(self.symbol_id)
        self.base_url = _BASE_URL
        self.headers = get_headers(data_source=self.data_source, random_agent=random_agent)
        self.apikey = msn_apikey(headers=self.headers, version=api_version)

    def _input_validation(self, start: Optional[str], end: Optional[str], interval: Optional[str]):
        """
        Validate input data
        """
        # Normalize interval to standard format (e.g., '1D', '1H', '1W', '1M')
        timeframe = normalize_interval(interval)

        # Get standardized interval value
        timeframe_value = timeframe.value

        # Validate interval is supported by MSN
        if timeframe_value not in _RESAMPLE_MAP.keys():
            msg = (
                f"Giá trị interval không hợp lệ: {timeframe_value}. "
                f"MSN chỉ hỗ trợ: 1D, 1W, 1M"
            )
            raise ValueError(msg)

        # Create ticker model with standardized interval
        ticker = TickerModel(
            symbol=self.symbol_id, start=start, end=end,
            interval=timeframe_value
        )
        return ticker
    @optimize_execution('MSN')
    def history(self, start: Optional[str] = None, end: Optional[str] = None, interval: Optional[str] = "1D", show_log: bool = False, count_back: Optional[int] = 365, asset_type: Optional[str] = None) -> pd.DataFrame:
        """
        Truy xuất dữ liệu giá lịch sử.
        Fetch historical price data.

        Args:
            - start (required): Thời gian bắt đầu lấy dữ liệu, dạng string kiểu "YYYY-MM-DD" hoặc "YYYY-MM-DD HH:MM:SS". (Start time for data fetching, string format "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS").
            - end (optional): Thời gian kết thúc lấy dữ liệu. Mặc định là None. String format "YYYY-MM-DD" hoặc "YYYY-MM-DD HH:MM:SS". (End time for data fetching. Default is None. String format "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS").
            - interval (optional): Khung thời gian trích xuất dữ liệu giá lịch sử. Hỗ trợ "1D". (Timeframe for historical data. Supported value is "1D").
            - show_log (optional): Hiển thị thông tin log giúp debug dễ dàng. Mặc định là False. (Show log info for debugging. Default is False).
            - count_back (optional): Số lượng dữ liệu trả về từ thời điểm cuối. Mặc định là 365. (Number of records to return from the end. Default is 365).
        """

        # Default dates if not provided
        if start is None:
            start = '2000-01-01'
        if end is None:
            end = datetime.now().strftime("%Y-%m-%d")

        # Validate inputs
        ticker = self._input_validation(start, end, interval)
        
        if count_back is None:
            count_back = 365

        # Normalize interval for resample mapping
        timeframe = normalize_interval(ticker.interval)
        timeframe_value = timeframe.value

        if timeframe_value not in _RESAMPLE_MAP.keys():
            msg = (
                f"Giá trị interval không hợp lệ: {timeframe_value}. "
                f"MSN chỉ hỗ trợ: 1D, 1W, 1M"
            )
            raise ValueError(msg)

        if self.asset_type == "crypto":
            url = f"{_BASE_URL}/Cryptocurrency/chart"
        else:
            url = f"{_BASE_URL}/Charts/TimeRange"

        params = {
            "apikey": self.apikey,
            'StartTime': f'{start}T17:00:00.000Z',
            'EndTime': f'{end}T16:59:00.858Z',
            'timeframe': 1,
                    "ocid": "finance-utils-peregrine",
                    "cm": "vi-vn",
                    "it": "web",
                    "scn": "ANON",
                    "ids": self.symbol_id,
                    "type": "All",
                    "wrapodata": "false",
                    "disableSymbol": "false"
                }

        if show_log:
            logger.info(f"Tải dữ liệu từ {url} cho {ticker.symbol} từ {ticker.start} đến {ticker.end}, khung thời gian {ticker.interval}.\nParams: {params}")

        # Send a GET request to fetch the data
        response = requests.request("GET", url, headers=self.headers, params=params)

        if response.status_code != 200:
            raise ConnectionError(f"Tải dữ liệu không thành công: {response.status_code} - {response.reason}")

        json_data = response.json()[0]['series']

        if show_log:
            logger.info(f'Truy xuất thành công dữ liệu {ticker.symbol} từ {ticker.start} đến {ticker.end}, khung thời gian {ticker.interval}.')

        df = self._as_df(json_data, timeframe_value)

        # index df's data by start and end date
        df = df[(df['time'] >= ticker.start) & (df['time'] <= ticker.end)]

        df.source = self.data_source

        if count_back is not None:
            df = df.tail(count_back)
        
        return df
    
    def _as_df(self, history_data: Dict, interval:str, floating: Optional[int] = 2) -> pd.DataFrame:
        """
        Convert fetched historical stock data into a Pandas DataFrame.
        """
        df = pd.DataFrame(history_data)
        df.drop(columns=['priceHigh', 'priceLow', 'startTime', 'endTime'], inplace=True)
        
        # rename columns using OHLC_MAP
        df.rename(columns=_OHLC_MAP, inplace=True)

        # parse the df['time'] from string to datetime, it can be in format of "2023-01-01 00:00:00" or "2023-01-01"
        df["time"] = pd.to_datetime(df["time"], errors='coerce')

        # add 7 hours to time to convert from UTC to Asia/Ho_Chi_Minh
        df['time'] = df['time'] + pd.Timedelta(hours=7)
        # remove hours info from time
        df['time'] = df['time'].dt.floor('D')

        # round open, high, low, close to 2 decimal places
        df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].round(floating)

        # set datatype for each column using _OHLC_DTYPE
        for col, dtype in _OHLC_DTYPE.items():
            if df[col].dtype.name == 'datetime64[ns, UTC]':
                df[col] = df[col].dt.tz_localize(None)
            else:
                df[col] = df[col].astype(dtype)

        # Define column order for clarity and maintainability
        column_order = ['time', 'open', 'high', 'low', 'close', 'volume']
        # Reorder columns for the final DataFrame
        df = df[column_order]

        if interval not in ["1D"]:
            df = df.set_index('time').resample(_RESAMPLE_MAP[interval]).agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).reset_index()
        
        if self.asset_type == "currency":
            df.drop(columns=['volume'], inplace=True)
        
        # replace value -99999901.0	by NaN
        df = df.replace(-99999901.0, None)
        # drop rows with NaN values in open, high, low
        df = df.dropna(subset=['open', 'high', 'low'])

        return df


# Register MSN Quote provider
from vnstock.core.registry import ProviderRegistry  # noqa: E402, F401
ProviderRegistry.register('quote', 'msn', Quote)
