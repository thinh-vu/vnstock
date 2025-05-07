"""History module for TCBS."""

import requests
import pandas as pd
from typing import Dict, Optional, Union, List
from datetime import datetime, timedelta
from .const import (_BASE_URL, _STOCKS_URL, _FUTURE_URL, _INTERVAL_MAP, _OHLC_MAP, 
                    _OHLC_DTYPE, _INTRADAY_MAP, _INTRADAY_DTYPE, _INDEX_MAPPING)
from .models import TickerModel
from vnai import optimize_execution
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.market import trading_hours
from vnstock.core.utils.parser import get_asset_type
from vnstock.core.utils.user_agent import get_headers
from vnstock.core.utils import client, transform, validation

logger = get_logger(__name__)

class Quote:
    """
    TCBS data source for fetching stock market data, accommodating requests with large date ranges.
    """
    def __init__(self, symbol: str, random_agent: bool = False, show_log: bool = True):
        """Initialize the Quote object with the given symbol."""
        symbol = symbol.upper()
        self.data_source = 'TCBS'
        self._history = None  # Cache for backwards compatibility
        self.base_url = _BASE_URL
        self.headers = get_headers(data_source=self.data_source, random_agent=random_agent)
        self.interval_map = _INTERVAL_MAP
        self.show_log = show_log
        
        # Handle INDEX symbols using shared validation
        if 'INDEX' in symbol:
            self.symbol = validation.validate_symbol(symbol, _INDEX_MAPPING)
        else:
            self.symbol = symbol
            
        # Get asset type using existing utility
        self.asset_type = get_asset_type(symbol)
        
        if not show_log:
            logger.setLevel('CRITICAL')
    
    def _input_validation(self, start: str, end: str, interval: str) -> TickerModel:
        """Validate input data using shared validation utilities."""
        # Create ticker model
        ticker = TickerModel(symbol=self.symbol, start=start, end=end, interval=interval)
        
        # Validate interval
        validation.validate_interval(ticker.interval, self.interval_map)
        
        return ticker
    
    def _long_history(self, start: str, end: Optional[str], show_log: bool = False, 
                    asset_type: Optional[str] = None, _skip_long_check: bool = True) -> pd.DataFrame:
        """
        Truy xuất dữ liệu lịch sử dài hạn từ TCBS cho khung thời gian ngày
        """
        from datetime import timedelta
        
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
        
        combined_data = []
        current_start = start_date
        
        # Process each year chunk moving forward from start date
        while current_start <= end_date:
            try:
                # Calculate end date for this chunk (either next year or final end date)
                next_year_date = datetime(current_start.year + 1, current_start.month, 1)
                year_end = min(
                    next_year_date - timedelta(days=1),
                    end_date
                )
                
                # Format dates as strings
                year_start_str = current_start.strftime("%Y-%m-%d")
                year_end_str = year_end.strftime("%Y-%m-%d")
                
                if show_log:
                    logger.info(f"Fetching chunk from {year_start_str} to {year_end_str}")
                
                # Fetch data for this year chunk - pass the _skip_long_check parameter
                try:
                    data = self.history(
                        start=year_start_str, 
                        end=year_end_str, 
                        interval="1D", 
                        to_df=True, 
                        show_log=show_log, 
                        asset_type=asset_type,
                        _skip_long_check=True
                    )
                    combined_data.append(data)
                except Exception as e:
                    logger.error(f"Dữ liệu không tồn tại từ {year_start_str} đến {year_end_str}: {e}")
                
                # Move to next year's start (use the first day of the next month to avoid leap year issues)
                current_start = next_year_date
                
            except Exception as e:
                logger.error(f"Error processing year chunk: {str(e)}")
                # Move forward by a year even if an error occurs
                current_start = datetime(current_start.year + 1, current_start.month, 1)
        
        # If no data was found, raise an error
        if not combined_data:
            raise ValueError(f"Không tìm thấy dữ liệu cho {self.symbol} từ {start} đến {end}")
        
        # Combine all chunks
        df = pd.concat(combined_data, ignore_index=True)
        
        # Filter to ensure we only get data in the requested range
        df = df[(df['time'] >= start) & (df['time'] <= end)]
        
        return df

    @optimize_execution("TCBS")
    def history(self, start: str, end: Optional[str] = None, interval: Optional[str] = "1D", 
            to_df: bool = True, show_log: bool = False, count_back: Optional[int] = 365,
            asset_type: Optional[str] = None, _skip_long_check: bool = False) -> Dict:
        """
        Tham số:
            - start (bắt buộc): thời gian bắt đầu lấy dữ liệu, có thể là ngày dạng string kiểu "YYYY-MM-DD".
            - end (tùy chọn): thời gian kết thúc lấy dữ liệu. Mặc định là None (ngày hiện tại).
            - interval (tùy chọn): Khung thời gian trích xuất dữ liệu giá lịch sử (1m, 5m, 15m, 30m, 1H, 1D, 1W, 1M).
            - to_df (tùy chọn): Chuyển đổi dữ liệu trả về dưới dạng DataFrame (True) hoặc JSON (False).
            - show_log (tùy chọn): Hiển thị thông tin log giúp debug dễ dàng.
            - count_back (tùy chọn): Số lượng dữ liệu trả về từ thời điểm cuối. Mặc định là 365.
            - asset_type (tùy chọn): Loại tài sản (stock, index, derivative). Mặc định là None (tự xác định).
            - _skip_long_check (tùy chọn): Bỏ qua kiểm tra thời gian dài để tránh đệ quy vô hạn. Mặc định là False.
        """
        # Validate inputs
        ticker = self._input_validation(start, end, interval)
        
        if count_back is None:
            count_back = 365

        if asset_type is None:
            asset_type = self.asset_type

        # calculate days between start and end
        start_time = datetime.strptime(ticker.start, "%Y-%m-%d")
        end_time = datetime.strptime(ticker.end, "%Y-%m-%d")

        # validate if the end date is not earlier than the start date
        if end_time < start_time:
            raise ValueError("Thời gian kết thúc không thể sớm hơn thời gian bắt đầu.")

        days = (end_time - start_time).days

        # Only check for long date ranges if not explicitly skipped
        if not _skip_long_check and days > 365:
            return self._long_history(start, end, show_log, asset_type)
        else:
            if end is None:
                end_stamp = int(datetime.now().timestamp())
            else:
                end_stamp = int(end_time.timestamp())

            if interval in ["1D", "1W", "1M"]:
                end_point = "bars-long-term"
            elif interval in ["1m", "5m", "15m", "30m", "1H"]:
                end_point = "bars"

            # translate the interval to TCBS format
            interval_value = self.interval_map[ticker.interval]

            # Construct the URL for fetching data
            if asset_type == "derivative":
                url = f"{self.base_url}/{_FUTURE_URL}/v2/stock/{end_point}?resolution={interval_value}&ticker={self.symbol}&type={asset_type}&to={end_stamp}&countBack={count_back}"
            else:
                url = f"{self.base_url}/{_STOCKS_URL}/v2/stock/{end_point}?resolution={interval_value}&ticker={self.symbol}&type={asset_type}&to={end_stamp}&countBack={count_back}"

            if interval_value in ["1", "5", "15", "30", "60"]:
                # replace 'bars-long-term' with 'bars' in the url
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
            # convert df to json format 
            json_data = df.to_json(orient='records')
            return json_data
        
    def _as_df(self, history_data: Dict, asset_type: str, floating: Optional[int] = 2) -> pd.DataFrame:
        """
        Backward compatibility method that delegates to shared data_transform utility
        """
        from vnstock.core.utils import transform
        
        # Use the shared transformation utility
        return transform.ohlc_to_df(
            data=history_data,
            column_map=_OHLC_MAP,
            dtype_map=_OHLC_DTYPE,
            asset_type=asset_type,
            symbol=self.symbol,
            source=self.data_source,
            interval="1D"  # Default for long history
        )
    
    @optimize_execution("TCBS")
    def intraday(self, page_size: Optional[int]=100, page: Optional[int]=0, 
            to_df: Optional[bool]=True, show_log: bool=False) -> Dict:
        """
        Truy xuất dữ liệu khớp lệnh của mã chứng khoán bất kỳ từ nguồn dữ liệu TCBS
        """
        market_status = trading_hours(None)
        if market_status['is_trading_hour'] is False and market_status['data_status'] == 'preparing':
            raise ValueError(f"{market_status['time']}: Dữ liệu khớp lệnh không thể truy cập trong thời gian chuẩn bị phiên mới. Vui lòng quay lại sau.")

        # Validate input
        if self.symbol is None:
            raise ValueError("Vui lòng nhập mã chứng khoán cần truy xuất khi khởi tạo Trading Class.")
        
        # warning if page_size is greater than 30_000
        if page_size > 30_000:
            logger.warning("Bạn đang yêu cầu truy xuất quá nhiều dữ liệu, điều này có thể gây lỗi quá tải.")
        
        # Fetch data
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
            
            # Make request
            response = client.send_request(
                url=url,
                headers=self.headers,
                method="GET",
                params=params,
                show_log=show_log
            )
            
            data = response.get('data', [])
            combined_data.extend(data)
        
        # Transform data using shared utility
        df = transform.intraday_to_df(
            data=combined_data,
            column_map=_INTRADAY_MAP,
            dtype_map=_INTRADAY_DTYPE,
            symbol=self.symbol,
            asset_type=self.asset_type,
            source=self.data_source
        )

        # Reduce the time index by 7 hours to match the GMT+7 timezone
        df['time'] = df['time'] - pd.Timedelta(hours=7)
        
        return df if to_df else df.to_json(orient='records')


