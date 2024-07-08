"""History module for VCI."""

# Đồ thị giá, đồ thị dư mua dư bán, đồ thị mức giá vs khối lượng, thống kê hành vi thị tường
from typing import Dict, Optional
from datetime import datetime
from .const import _BASE_URL, _CHART_URL, _INTERVAL_MAP, _OHLC_MAP, _RESAMPLE_MAP, _OHLC_DTYPE, _INTRADAY_URL, _INTRADAY_MAP, _INTRADAY_DTYPE, _PRICE_DEPTH_MAP
from .models import TickerModel
import pandas as pd
import requests
import json
from vnstock3.core.utils.parser import get_asset_type
from vnstock3.core.utils.logger import get_logger
from vnstock3.core.utils.user_agent import get_headers

logger = get_logger(__name__)

class Quote:
    """
    Cấu hình truy cập dữ liệu lịch sử giá chứng khoán từ VCI.
    """
    def __init__(self, symbol, random_agent=False):
        self.symbol = symbol.upper()
        self.data_source = 'VCI'
        self._history = None  # Cache for historical data
        self.asset_type = get_asset_type(self.symbol)
        self.base_url = _BASE_URL
        self.headers = get_headers(data_source=self.data_source, random_agent=random_agent)
        self.interval_map = _INTERVAL_MAP

    def _input_validation(self, start: str, end: str, interval: str):
        """
        Validate input data
        """
        # Validate input data
        ticker = TickerModel(symbol=self.symbol, start=start, end=end, interval=interval)

        # if interval is not in the interval_map, raise an error
        if ticker.interval not in self.interval_map:
            raise ValueError(f"Giá trị interval không hợp lệ: {ticker.interval}. Vui lòng chọn: 1m, 5m, 15m, 30m, 1H, 1D, 1W, 1M")
        
        return ticker

    def history(self, start: str, end: Optional[str], interval: Optional[str] = "1D", to_df: Optional[bool]=True, show_log: Optional[bool]=False, count_back: Optional[int]=None) -> Dict:
        """
        Tải lịch sử giá của mã chứng khoán từ nguồn dữ liệu VN Direct.

        Tham số:
            - start (bắt buộc): thời gian bắt đầu lấy dữ liệu, có thể là ngày dạng string kiểu "YYYY-MM-DD" hoặc "YYYY-MM-DD HH:MM:SS".
            - end (tùy chọn): thời gian kết thúc lấy dữ liệu. Mặc định là None, chương trình tự động lấy thời điểm hiện tại. Có thể nhập ngày dạng string kiểu "YYYY-MM-DD" hoặc "YYYY-MM-DD HH:MM:SS". 
            - interval (tùy chọn): Khung thời gian trích xuất dữ liệu giá lịch sử. Giá trị nhận: 1m, 5m, 15m, 30m, 1H, 1D, 1W, 1M. Mặc định là "1D".
            - to_df (tùy chọn): Chuyển đổi dữ liệu lịch sử trả về dưới dạng DataFrame. Mặc định là True. Đặt là False để trả về dữ liệu dạng JSON.
            - show_log (tùy chọn): Hiển thị thông tin log giúp debug dễ dàng. Mặc định là False.
            - count_back (tùy chọn): Số lượng dữ liệu trả về từ thời điểm cuối. Mặc định là 365.
        """
        # Validate inputs
        ticker = self._input_validation(start, end, interval)

        start_time = datetime.strptime(ticker.start, "%Y-%m-%d")
        end_time = datetime.strptime(ticker.end, "%Y-%m-%d")

        if start_time > end_time:
            raise ValueError("Thời gian bắt đầu không thể lớn hơn thời gian kết thúc.")

        # convert start and end date to timestamp
        if end is None:
            end_stamp = int(datetime.now().timestamp())
        else:
            end_stamp = int(end_time.timestamp())

        start_stamp = int(start_time.timestamp())        
        
        interval = self.interval_map[ticker.interval]

        # Construct the URL for fetching data
        url = self.base_url + _CHART_URL

        payload = json.dumps({
        "timeFrame": interval,
        "symbols": [
            self.symbol
        ],
        "from": start_stamp,
        "to": end_stamp
        })

        if show_log:
            logger.info(f"Tải dữ liệu từ {url}\npayload: {payload}")

        # Send a GET request to fetch the data
        response = requests.post(url, headers=self.headers, data=payload)

        if response.status_code != 200:
            raise ConnectionError(f"Failed to fetch data: {response.status_code} - {response.reason}")

        json_data = response.json()

        if show_log:
            logger.info(f'Truy xuất thành công dữ liệu {ticker.symbol} từ {ticker.start} đến {ticker.end}, khung thời gian {ticker.interval}.')

        df = self._as_df(history_data=json_data[0], asset_type=self.asset_type, interval=ticker.interval)

        if count_back is not None:
            df = df.tail(count_back)

        if to_df:
            return df
        else:
            json_data = df.to_json(orient='records')
            return json_data
    
    def intraday(self, page_size: Optional[int]=100, last_time: Optional[str]=None, to_df: Optional[bool]=True, show_log: bool=False) -> Dict:
        """
        Truy xuất dữ liệu khớp lệnh của mã chứng khoán bất kỳ từ nguồn dữ liệu VCI

        Tham số:
            - page_size (tùy chọn): Số lượng dữ liệu trả về trong một lần request. Mặc định là 100. Không giới hạn số lượng tối đa. Tăng số này lên để lấy toàn bộ dữ liêu, ví dụ 10_000.
            - trunc_time (tùy chọn): Thời gian cắt dữ liệu, dùng để lấy dữ liệu sau thời gian cắt. Mặc định là None.
            - to_df (tùy chọn): Chuyển đổi dữ liệu lịch sử trả về dưới dạng DataFrame. Mặc định là True. Đặt là False để trả về dữ liệu dạng JSON.
            - show_log (tùy chọn): Hiển thị thông tin log giúp debug dễ dàng. Mặc định là False.
        """
        # if self.symbol is not defined, raise ValueError
        if self.symbol is None:
            raise ValueError("Vui lòng nhập mã chứng khoán cần truy xuất khi khởi tạo Trading Class.")
        
        # convert a string to timestamp
        if last_time is not None:
            last_time = int(datetime.strptime(last_time, "%Y-%m-%d %H:%M:%S").timestamp())

        url = f'{self.base_url}{_INTRADAY_URL}/LEData/getAll'

        payload = json.dumps({
        "symbol": self.symbol,
        "limit": page_size,
        "truncTime": last_time
        })

        if show_log:
            logger.info(f'Requested URL: {url} with query payload: {payload}')
        response = requests.post(url, headers=self.headers, data=payload)

        if response.status_code != 200:
            raise ConnectionError(f"Tải dữ liệu không thành công: {response.status_code} - {response.reason}")

        data = response.json()
        df = pd.DataFrame(data)

        # select columns in _INTRADAY_MAP values
        df = df[_INTRADAY_MAP.keys()]
        # rename columns
        df.rename(columns=_INTRADAY_MAP, inplace=True)
        # replace b with Buy, s with Sell, unknown with ATO/ATC in match_type column
        df['match_type'] = df['match_type'].replace({'b': 'Buy', 's': 'Sell', 'unknown': 'ATO/ATC'})

        # convert time to datetime
        df['time'] = pd.to_datetime(df['time'].astype(int), unit='s')
        # convert UTC time to Asia/Ho_Chi_Minh timezone by adding 7 hours
        df['time'] = df['time'] + pd.Timedelta(hours=7)

        # sort by time
        df = df.sort_values(by='time')

        # apply _INTRADAY_DTYPE to columns
        df = df.astype(_INTRADAY_DTYPE)

        df.name = self.symbol
        df.category = self.asset_type
        df.source = self.data_source

        if to_df:
            return df
        else:
            json_data = df.to_json(orient='records')
            return json_data
        
    def price_depth(self, to_df:Optional[bool]=True, show_log:Optional[bool]=False):
        """
        Truy xuất thống kê độ bước giá & khối lượng khớp lệnh của mã chứng khoán bất kỳ từ nguồn dữ liệu VCI.

        Tham số:
            - to_df (tùy chọn): Chuyển đổi dữ liệu lịch sử trả về dưới dạng DataFrame. Mặc định là True. Đặt là False để trả về dữ liệu dạng JSON.
            - show_log (tùy chọn): Hiển thị thông tin log giúp debug dễ dàng. Mặc định là False.
        """
        # if self.symbol is not defined, raise ValueError
        if self.symbol is None:
            raise ValueError("Vui lòng nhập mã chứng khoán cần truy xuất khi khởi tạo Trading Class.")
        
        url = f'{self.base_url}{_INTRADAY_URL}/AccumulatedPriceStepVol/getSymbolData'
        payload = json.dumps({
            "symbol": self.symbol
        })

        if show_log:
            logger.info(f'Requested URL: {url} with query payload: {payload}')
        response = requests.post(url, headers=self.headers, data=payload)

        if response.status_code != 200:
            raise ConnectionError(f"Tải dữ liệu không thành công: {response.status_code} - {response.reason}")

        data = response.json()
        df = pd.DataFrame(data)

        # select columns in _INTRADAY_MAP values
        df = df[_PRICE_DEPTH_MAP.keys()]
        # rename columns
        df.rename(columns=_PRICE_DEPTH_MAP, inplace=True)
        
        df.source = self.data_source

        if to_df:
            return df
        else:
            json_data = df.to_json(orient='records')
            return json_data

    def _as_df(self, history_data: Dict, asset_type: str, interval: str, floating: Optional[int] = 2) -> pd.DataFrame:
        """
        Converts stock price history data from JSON format to DataFrame.

        Parameters:
            - history_data: Stock price history data in JSON format.
        Returns:
            - DataFrame: Stock price history data as a DataFrame.
        """
        if not history_data:
            raise ValueError("Input data is empty or not provided.")

        # Select and rename columns directly using a dictionary comprehension
        columns_of_interest = {key: _OHLC_MAP[key] for key in _OHLC_MAP.keys() & history_data.keys()}
        df = pd.DataFrame(history_data)[columns_of_interest.keys()].rename(columns=_OHLC_MAP)
        # rearrange columns by open, high, low, close, volume, time
        df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
        
        # Ensure 'time' column data are numeric (integers), then convert to datetime
        df['time'] = pd.to_datetime(df['time'].astype(int), unit='s').dt.tz_localize('UTC') # Localize the original time to UTC
        # Convert UTC time to Asia/Ho_Chi_Minh timezone, make sure time is correct for minute and hour interval
        df['time'] = df['time'].dt.tz_convert('Asia/Ho_Chi_Minh')

        if asset_type not in ["index", "derivative"]:            
            # divide open, high, low, close, volume by 1000
            df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].div(1000)

        # round open, high, low, close to 2 decimal places
        df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].round(floating)

        # if self.resolution is not in 1m, 1H, 1D, resample the data
        if interval not in ["1m", "1H", "1D"]:
            df = df.set_index('time').resample(_RESAMPLE_MAP[interval]).agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).reset_index()

        # set datatype for each column using _OHLC_DTYPE
        for col, dtype in _OHLC_DTYPE.items():
            if dtype == "datetime64[ns]":
                df[col] = df[col].dt.tz_localize(None)  # Remove timezone information
            df[col] = df[col].astype(dtype)

        # Set metadata attributes
        df.name = self.symbol
        df.category = self.asset_type
        df.source = "VCI"

        return df



