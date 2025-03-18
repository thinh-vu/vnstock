"""History module for MSN."""

# Đồ thị giá, đồ thị dư mua dư bán, đồ thị mức giá vs khối lượng, thống kê hành vi thị tường
import pandas as pd
import requests
from datetime import datetime
from typing import Optional, Dict
from vnai import optimize_execution
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.user_agent import get_headers
from vnstock.explorer.msn.listing import Listing
from vnstock.explorer.msn.helper import msn_apikey
from vnstock.explorer.msn.models import TickerModel 
from vnstock.explorer.msn.helper import get_asset_type
from .const import _BASE_URL, _RESAMPLE_MAP, _OHLC_MAP, _OHLC_DTYPE

logger = get_logger(__name__)

class Quote:
    """
    MSN data source for fetching stock market data, accommodating requests with large date ranges.
    """
    def __init__(self, symbol_id:str, api_version='20240430', random_agent:Optional[bool]=False):
        self.data_source = 'MSN'
        self.symbol_id = symbol_id.lower()
        self.asset_type = get_asset_type(symbol_id)
        self.base_url = _BASE_URL
        self.headers = get_headers(data_source=self.data_source, random_agent=random_agent)
        self.apikey = msn_apikey(headers=self.headers, version=api_version)

    def _input_validation(self, start: str, end: str, interval: str):
        """
        Validate input data
        """
        # Validate input data
        ticker = TickerModel(symbol=self.symbol_id, start=start, end=end, interval=interval)
        return ticker
    

    @optimize_execution('MSN')
    def history(self, start: str, end: Optional[str], interval: Optional[str] = "1D", to_df: bool =True, show_log: bool =False, count_back: Optional[int]=365, asset_type: Optional[str] = None) -> Dict:
        """
        Tham số:
            - start (bắt buộc): thời gian bắt đầu lấy dữ liệu, có thể là ngày dạng string kiểu "YYYY-MM-DD" hoặc "YYYY-MM-DD HH:MM:SS".
            - end (tùy chọn): thời gian kết thúc lấy dữ liệu. Mặc định là None, chương trình tự động lấy thời điểm hiện tại. Có thể nhập ngày dạng string kiểu "YYYY-MM-DD" hoặc "YYYY-MM-DD HH:MM:SS". 
            - interval (tùy chọn): Khung thời gian trích xuất dữ liệu giá lịch sử. Giá trị duy nhất được hỗ trợ là "1D".
            - to_df (tùy chọn): Chuyển đổi dữ liệu lịch sử trả về dưới dạng DataFrame. Mặc định là True. Đặt là False để trả về dữ liệu dạng JSON.
            - show_log (tùy chọn): Hiển thị thông tin log giúp debug dễ dàng. Mặc định là False.
            - count_back (tùy chọn): Số lượng dữ liệu trả về từ thời điểm cuối. Mặc định là 365.
        """

        # Validate inputs
        ticker = self._input_validation(start, end, interval)
        
        if count_back is None:
            count_back = 365

        # interval should be in 1D, 1W, 1M
        if interval not in _RESAMPLE_MAP.keys():
            raise ValueError("Giá trị interval được phép chỉ bao gồm 1D, 1W, 1M cho nguồn dữ liệu từ MSN.")

        if self.asset_type == "crypto":
            url = f"{_BASE_URL}/Cryptocurrency/chart"
        else:
            url = f"{_BASE_URL}/Charts/TimeRange"

        params = {"apikey": self.apikey,
                  'StartTime': f'{start}T17:00:00.000Z',
                    'EndTime': f'{end}T16:59:00.858Z',
                    'timeframe' : 1, 
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

        df = self._as_df(json_data, interval)

        # index df's data by start and end date
        df = df[(df['time'] >= ticker.start) & (df['time'] <= ticker.end)]

        df.source = self.data_source

        if count_back is not None:
            df = df.tail(count_back)
        
        if to_df:
            return df
        else:
            # convert the time column to int value in seconds
            df['time'] = df['time'].astype("int64")
            # convert df to json format 
            json_data = df.to_dict(orient='records')
            return json_data
    
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
