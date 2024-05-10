"""History module for tcbs."""

# Đồ thị giá, đồ thị dư mua dư bán, đồ thị mức giá vs khối lượng, thống kê hành vi thị tường
import pandas as pd
import requests
from datetime import datetime
from typing import Optional, Dict
from vnstock3.core.utils.parser import get_asset_type
from vnstock3.core.utils.logger import get_logger
from vnstock3.core.utils.user_agent import get_headers
from .models import TickerModel
from .const import _BASE_URL, _STOCKS_URL, _FUTURE_URL, _INTERVAL_MAP, _OHLC_MAP, _OHLC_DTYPE, _INTRADAY_MAP, _INTRADAY_DTYPE

logger = get_logger(__name__)

class Quote:
    """
    TCBS data source for fetching stock market data, accommodating requests with large date ranges.
    """
    def __init__(self, symbol, random_agent=False):
        self.symbol = symbol.upper()
        self.data_source = 'TCBS'
        self._history = None  # Cache for historical data
        self.asset_type = get_asset_type(self.symbol)
        self.base_url = _BASE_URL
        # self.headers = _TCBS_HEADERS
        self.headers = get_headers(data_source=self.data_source, random_agent=random_agent)
        self.interval_map = _INTERVAL_MAP

    def _input_validation(self, start: str, end: str, interval: str):
        """
        Validate input data
        """
        # Validate input data
        ticker = TickerModel(symbol=self.symbol, start=start, end=end, interval=interval)
        return ticker
    
    def history(self, start: str, end: Optional[str], interval: Optional[str] = "1D", to_df: bool =True, show_log: bool =False, count_back: Optional[int]=365, asset_type: Optional[str] = None) -> Dict:
        """
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
        
        if count_back is None:
            count_back = 365

        if asset_type is None:
            asset_type = self.asset_type

        if end is None:
            end_stamp = int(datetime.now().timestamp())
        else:
            end_stamp = int(datetime.strptime(ticker.end, "%Y-%m-%d").timestamp())

        if interval in ["1D", "1W", "1M"]:
            end_point = "bars-long-term"
        elif interval in ["1m", "5m", "15m", "30m", "1H"]:
            end_point = "bars"

        # translate the interval to TCBS format
        interval = self.interval_map[ticker.interval]

        # Construct the URL for fetching data
        if asset_type == "derivative":
            url = f"{self.base_url}/{_FUTURE_URL}/v2/stock/{end_point}?resolution={interval}&ticker={self.symbol}&type={asset_type}&to={end_stamp}&countBack={count_back}"
        else:
            url = f"{self.base_url}/{_STOCKS_URL}/v2/stock/{end_point}?resolution={interval}&ticker={self.symbol}&type={asset_type}&to={end_stamp}&countBack={count_back}"

        if interval in ["1m", "5m", "15m", "30m", "1H"]:
            # replace 'bars' with 'bars-long-term' in the url
            url = url.replace("bars-long-term", "bars")

        if show_log:
            logger.info(f"Tải dữ liệu từ {url}")

        # Send a GET request to fetch the data
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            raise ConnectionError(f"Tải dữ liệu không thành công: {response.status_code} - {response.reason}")

        json_data = response.json()['data']

        if show_log:
            logger.info(f'Truy xuất thành công dữ liệu {ticker.symbol} từ {ticker.start} đến {ticker.end}, khung thời gian {ticker.interval}.')

        df = self._as_df(json_data, asset_type)

        df.attrs['symbol'] = self.symbol
        df.category = self.asset_type
        df.source = self.data_source
        
        if to_df:
            return df
        else:
            # convert the time column to int value in seconds
            df['time'] = df['time'].astype("int64")
            # convert df to json format 
            json_data = df.to_dict(orient='records')
            return json_data
    
    def intraday(self, page_size: Optional[int]=100, page:Optional[int]=0, to_df: Optional[bool]=True, show_log: bool=False) -> Dict:
        """
        Truy xuất dữ liệu khớp lệnh của mã chứng khoán bất kỳ từ nguồn dữ liệu TCBS

        Tham số:
            - page_size (tùy chọn): Số lượng dữ liệu trả về trong một lần request. Mặc định là 100. Không giới hạn số lượng tối đa. Tăng số này lên để lấy toàn bộ dữ liêu, ví dụ 10_000.
            - page (tùy chọn): Số trang dữ liệu cần lấy. Mặc định là 0.
            - to_df (tùy chọn): Chuyển đổi dữ liệu lịch sử trả về dưới dạng DataFrame. Mặc định là True. Đặt là False để trả về dữ liệu dạng JSON.
            - show_log (tùy chọn): Hiển thị thông tin log giúp debug dễ dàng. Mặc định là False.
        """
        # if self.symbol is not defined, raise ValueError
        if self.symbol is None:
            raise ValueError("Vui lòng nhập mã chứng khoán cần truy xuất khi khởi tạo Trading Class.")
        combined_data = []
        total_pages = (page_size // 100) + (1 if page_size % 100 != 0 else 0)

        for i in range(total_pages):
            current_size = min(100, page_size - 100 * i)
            url = f'{self.base_url}/{_STOCKS_URL}/v1/intraday/{self.symbol}/his/paging'
            params = {
                'page': page + i,
                'size': current_size,
                'headIndex': -1
            }
            if show_log:
                logger.info(f'Requested URL: {url} with params: {params}')
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code != 200:
                raise ConnectionError(f"Tải dữ liệu không thành công: {response.status_code} - {response.reason}")

            data = response.json()['data']
            combined_data.extend(data)
            if show_log:
                logger.info(f"Data:\n {data}")
        # cleanup data
        df = pd.DataFrame(combined_data)
        # select columns in _INTRADAY_MAP values
        df = df[_INTRADAY_MAP.keys()]
        # rename columns
        df.rename(columns=_INTRADAY_MAP, inplace=True)

        # replace BU with Buy Up, SD with Sell Down in action column
        df['match_type'] = df['match_type'].replace({'BU': 'Buy', 'SD': 'Sell', '':'ATO/ATC'})

        # rearrange columns, use the exact order in _INTRADAY_MAP
        df = df[_INTRADAY_MAP.values()]

        # apply _INTRADAY_DTYPE to columns
        df = df.astype(_INTRADAY_DTYPE)

        df.attrs['symbol'] = self.symbol
        df.category = self.asset_type
        df.source = self.data_source
        
        if to_df:
            return df
        else:
            json_data = df.to_json(orient='records')
            return json_data

    def _as_df(self, history_data: Dict, asset_type: str, floating: Optional[int] = 2) -> pd.DataFrame:
        """
        Convert fetched historical stock data into a Pandas DataFrame.
        """
        if asset_type is None:
            asset_type = self.asset_type

        df = pd.DataFrame(history_data)
        
        # rename columns using OHLC_MAP
        df.rename(columns=_OHLC_MAP, inplace=True)

        # parse the df['time'] from string to datetime, it can be in format of "2023-01-01 00:00:00" or "2023-01-01"
        df["time"] = pd.to_datetime(df["time"], errors='coerce')    

        # If 'time' is timezone-aware, make it timezone-naive
        if df["time"].dt.tz is not None:
            df["time"] = df["time"].dt.tz_localize(None)  # Remove timezone information

        if asset_type not in ["index", "derivative"]:            
            # divide open, high, low, close, volume by 1000
            df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].div(1000)

        # round open, high, low, close to 2 decimal places
        df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].round(floating)

        # set datatype for each column using _OHLC_DTYPE
        for col, dtype in _OHLC_DTYPE.items():
            df[col] = df[col].astype(dtype)

        # Define column order for clarity and maintainability
        column_order = ['time', 'open', 'high', 'low', 'close', 'volume']
        # Reorder columns for the final DataFrame
        df = df[column_order]

        # Set metadata attributes
        df.name = self.symbol
        df.category = asset_type
        df.source = "TCBS" 

        return df