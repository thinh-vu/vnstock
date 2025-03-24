"""History module for VCI."""

from typing import Dict, Optional, Union
from datetime import datetime
import pandas as pd
from vnai import optimize_execution
from .const import (
    _TRADING_URL, _CHART_URL, _INTERVAL_MAP, 
    _OHLC_MAP, _RESAMPLE_MAP, _OHLC_DTYPE, _INTRADAY_URL, 
    _INTRADAY_MAP, _INTRADAY_DTYPE, _PRICE_DEPTH_MAP, _INDEX_MAPPING
)
from .models import TickerModel
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.market import trading_hours
from vnstock.core.utils.parser import get_asset_type
from vnstock.core.utils.user_agent import get_headers
from vnstock.core.utils.client import send_request
from vnstock.core.utils.transform import ohlc_to_df, intraday_to_df

logger = get_logger(__name__)

class Quote:
    """
    Cấu hình truy cập dữ liệu lịch sử giá chứng khoán từ VCI.
    """
    def __init__(self, symbol, random_agent=False, show_log=True):
        self.symbol = symbol.upper()
        self.data_source = 'VCI'
        self._history = None  # Cache for historical data
        self.asset_type = get_asset_type(self.symbol)
        self.base_url = _TRADING_URL
        self.headers = get_headers(data_source=self.data_source, random_agent=random_agent)
        self.interval_map = _INTERVAL_MAP
        self.show_log = show_log

        if not show_log:
            logger.setLevel('CRITICAL')

        if 'INDEX' in self.symbol:
            self.symbol = self._index_validation()

    def _index_validation(self) -> str:
        """
        If symbol contains 'INDEX' substring, validate it with _INDEX_MAPPING.
        """
        if self.symbol not in _INDEX_MAPPING.keys():
            raise ValueError(f"Không tìm thấy mã chứng khoán {self.symbol}. Các giá trị hợp lệ: {', '.join(_INDEX_MAPPING.keys())}")
        return _INDEX_MAPPING[self.symbol]

    def _input_validation(self, start: str, end: str, interval: str):
        """
        Validate input data
        """
        ticker = TickerModel(symbol=self.symbol, start=start, end=end, interval=interval)

        if ticker.interval not in self.interval_map:
            raise ValueError(f"Giá trị interval không hợp lệ: {ticker.interval}. Vui lòng chọn: 1m, 5m, 15m, 30m, 1H, 1D, 1W, 1M")

        return ticker

    @optimize_execution("VCI")
    def history(self, start: str, end: Optional[str]=None, interval: Optional[str]="1D", 
                to_df: Optional[bool]=True, show_log: Optional[bool]=False, 
                count_back: Optional[int]=None, floating: Optional[int]=2) -> Union[pd.DataFrame, str]:
        """
        Tải lịch sử giá của mã chứng khoán từ nguồn dữ liệu VCI.

        Tham số:
            - start (bắt buộc): thời gian bắt đầu lấy dữ liệu, có thể là ngày dạng string kiểu "YYYY-MM-DD" hoặc "YYYY-MM-DD HH:MM:SS".
            - end (tùy chọn): thời gian kết thúc lấy dữ liệu. Mặc định là None, chương trình tự động lấy thời điểm hiện tại.
            - interval (tùy chọn): Khung thời gian trích xuất dữ liệu giá lịch sử. Giá trị nhận: 1m, 5m, 15m, 30m, 1H, 1D, 1W, 1M. Mặc định là "1D".
            - to_df (tùy chọn): Chuyển đổi dữ liệu lịch sử trả về dưới dạng DataFrame. Mặc định là True. Đặt là False để trả về dạng JSON.
            - show_log (tùy chọn): Hiển thị thông tin log giúp debug dễ dàng. Mặc định là False.
            - count_back (tùy chọn): Số lượng dữ liệu trả về từ thời điểm cuối.
            - floating (tùy chọn): Số chữ số thập phân cho giá. Mặc định là 2.
        """
        # Validate inputs
        ticker = self._input_validation(start, end, interval)

        start_time = datetime.strptime(ticker.start, "%Y-%m-%d")
        
        # Calculate end timestamp
        if end is not None:
            end_time = datetime.strptime(ticker.end, "%Y-%m-%d") + pd.Timedelta(days=1)
            if start_time > end_time:
                raise ValueError("Thời gian bắt đầu không thể lớn hơn thời gian kết thúc.")
            end_stamp = int(end_time.timestamp())
        else:
            end_stamp = int((datetime.now() + pd.Timedelta(days=1)).timestamp())

        start_stamp = int(start_time.timestamp())
        interval_value = self.interval_map[ticker.interval]

        # Prepare request
        url = self.base_url + _CHART_URL
        payload = {
            "timeFrame": interval_value,
            "symbols": [self.symbol],
            "from": start_stamp,
            "to": end_stamp
        }

        # Use the send_request utility from api_client
        json_data = send_request(
            url=url, 
            headers=self.headers, 
            method="POST", 
            payload=payload, 
            show_log=show_log
        )

        if not json_data:
            raise ValueError("Không tìm thấy dữ liệu. Vui lòng kiểm tra lại mã chứng khoán hoặc thời gian truy xuất.")
        
        # Use the ohlc_to_df utility from data_transform
        df = ohlc_to_df(
            data=json_data[0], 
            column_map=_OHLC_MAP, 
            dtype_map=_OHLC_DTYPE, 
            asset_type=self.asset_type, 
            symbol=self.symbol, 
            source=self.data_source, 
            interval=ticker.interval, 
            floating=floating,
            resample_map=_RESAMPLE_MAP
        )

        if count_back is not None:
            df = df.tail(count_back)

        if to_df:
            return df
        else:
            return df.to_json(orient='records')

    @optimize_execution("VCI")
    def intraday(self, page_size: Optional[int]=100, last_time: Optional[str]=None, 
                to_df: Optional[bool]=True, show_log: bool=False) -> Union[pd.DataFrame, str]:
        """
        Truy xuất dữ liệu khớp lệnh của mã chứng khoán bất kỳ từ nguồn dữ liệu VCI

        Tham số:
            - page_size (tùy chọn): Số lượng dữ liệu trả về trong một lần request. Mặc định là 100. 
            - last_time (tùy chọn): Thời gian cắt dữ liệu, dùng để lấy dữ liệu sau thời gian cắt. Mặc định là None.
            - to_df (tùy chọn): Chuyển đổi dữ liệu lịch sử trả về dưới dạng DataFrame. Mặc định là True.
            - show_log (tùy chọn): Hiển thị thông tin log giúp debug dễ dàng. Mặc định là False.
        """
        market_status = trading_hours(None)
        if market_status['is_trading_hour'] is False and market_status['data_status'] == 'preparing':
            raise ValueError(f"{market_status['time']}: Dữ liệu khớp lệnh không thể truy cập trong thời gian chuẩn bị phiên mới. Vui lòng quay lại sau.")

        if self.symbol is None:
            raise ValueError("Vui lòng nhập mã chứng khoán cần truy xuất khi khởi tạo Trading Class.")

        if page_size > 30_000:
            logger.warning("Bạn đang yêu cầu truy xuất quá nhiều dữ liệu, điều này có thể gây lỗi quá tải.")

        url = f'{self.base_url}{_INTRADAY_URL}/LEData/getAll'
        payload = {
            "symbol": self.symbol,
            "limit": page_size,
            "truncTime": last_time
        }

        # Fetch data using the send_request utility
        data = send_request(
            url=url, 
            headers=self.headers, 
            method="POST", 
            payload=payload, 
            show_log=show_log
        )

        # Transform data using intraday_to_df utility
        df = intraday_to_df(
            data=data, 
            column_map=_INTRADAY_MAP, 
            dtype_map=_INTRADAY_DTYPE, 
            symbol=self.symbol, 
            asset_type=self.asset_type, 
            source=self.data_source
        )

        if to_df:
            return df
        else:
            return df.to_json(orient='records')

    @optimize_execution("VCI")
    def price_depth(self, to_df: Optional[bool]=True, show_log: Optional[bool]=False) -> Union[pd.DataFrame, str]:
        """
        Truy xuất thống kê độ bước giá & khối lượng khớp lệnh của mã chứng khoán bất kỳ từ nguồn dữ liệu VCI.

        Tham số:
            - to_df (tùy chọn): Chuyển đổi dữ liệu lịch sử trả về dưới dạng DataFrame. Mặc định là True.
            - show_log (tùy chọn): Hiển thị thông tin log giúp debug dễ dàng. Mặc định là False.
        """
        market_status = trading_hours(None)
        if market_status['is_trading_hour'] is False and market_status['data_status'] == 'preparing':
            raise ValueError(f"{market_status['time']}: Dữ liệu khớp lệnh không thể truy cập trong thời gian chuẩn bị phiên mới. Vui lòng quay lại sau.")

        if self.symbol is None:
            raise ValueError("Vui lòng nhập mã chứng khoán cần truy xuất khi khởi tạo Trading Class.")

        url = f'{self.base_url}{_INTRADAY_URL}/AccumulatedPriceStepVol/getSymbolData'
        payload = {
            "symbol": self.symbol
        }

        # Fetch data using the send_request utility
        data = send_request(
            url=url, 
            headers=self.headers, 
            method="POST", 
            payload=payload, 
            show_log=show_log
        )

        # Process the data to DataFrame
        df = pd.DataFrame(data)
        
        # Select columns in _PRICE_DEPTH_MAP values and rename them
        df = df[_PRICE_DEPTH_MAP.keys()]
        df.rename(columns=_PRICE_DEPTH_MAP, inplace=True)
        
        df.source = self.data_source

        if to_df:
            return df
        else:
            return df.to_json(orient='records')
