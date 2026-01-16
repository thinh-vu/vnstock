"""History module for TCBS."""

import requests
import pandas as pd
from typing import Dict, Optional, Union
from datetime import datetime, timedelta
from vnai import optimize_execution
from vnstock.core.utils.interval import normalize_interval
from vnstock.core.utils.deprecation import deprecate_provider
from .const import (
    _BASE_URL, _STOCKS_URL, _FUTURE_URL, _INTERVAL_MAP,
    _OHLC_MAP, _OHLC_DTYPE, _INTRADAY_MAP, _INTRADAY_DTYPE,
    _INDEX_MAPPING
)
from vnstock.core.models import TickerModel
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.market import trading_hours
from vnstock.core.utils.parser import get_asset_type
from vnstock.core.utils.validation import validate_symbol
from vnstock.core.utils.user_agent import get_headers
from vnstock.core.utils import client, transform, validation
from vnstock.core.utils.lookback import get_start_date_from_lookback, interpret_lookback_length

logger = get_logger(__name__)

# TimeFrame to interval key mapping
# Standard format: m/1m=minute, h/1H=hour, d/1D=day, w/1W=week, M/1M=month
_TIMEFRAME_MAP = {
    '1m': '1m',
    '5m': '5m',
    '15m': '15m',
    '30m': '30m',
    '1H': '1H',
    '1D': '1D',
    '1W': '1W',
    '1M': '1M'
}


@deprecate_provider(
    provider_name='TCBS',
    version='3.4.0',
    removal_version='3.5.0',
    alternative='VCI',
    reason='TCBS API is no longer publicly accessible as of March 1, 2026'
)
class Quote:
    """
    TCBS data source for fetching stock market data, accommodating
    requests with large date ranges.
    
    .. deprecated:: 3.4.0
        TCBS provider is deprecated and will be removed in version 3.5.0.
        Use VCI provider instead.
    """

    def __init__(
        self,
        symbol: str,
        random_agent: bool = False,
        show_log: bool = True,
        proxy_mode: str = "try",
        proxy_list: Optional[list] = None
    ):
        """Initialize the Quote object with the given symbol."""
        symbol = validate_symbol(symbol)
        self.data_source = 'TCBS'
        self._history = None  # Cache for backwards compatibility
        self.base_url = _BASE_URL
        self.headers = get_headers(
            data_source=self.data_source,
            random_agent=random_agent
        )
        self.interval_map = _INTERVAL_MAP
        self.show_log = show_log
        self.proxy_mode = proxy_mode
        self.proxy_list = proxy_list

        # Handle INDEX symbols using shared validation
        if 'INDEX' in symbol:
            self.symbol = validation.validate_symbol(
                symbol,
                _INDEX_MAPPING
            )
        else:
            self.symbol = symbol

        # Get asset type using existing utility
        self.asset_type = get_asset_type(symbol)

        if not show_log:
            logger.setLevel('CRITICAL')
    
    def _input_validation(
        self,
        start: Optional[str],
        end: Optional[str],
        interval: Optional[str]
    ) -> TickerModel:
        """Validate input data using shared validation utilities."""
        # Validate required parameters (start can now be None if length/count_back provided)
        if not end:
            raise ValueError("Vui lòng cung cấp ngày kết thúc (end)")
        if not interval:
            raise ValueError("Vui lòng cung cấp khung thời gian (interval)")

        # Normalize interval to standard format
        timeframe = normalize_interval(interval)

        # Map TimeFrame values to TCBS interval keys
        interval_key = _TIMEFRAME_MAP.get(timeframe.value)
        if interval_key is None or interval_key not in self.interval_map:
            msg = (
                f"Giá trị interval không hợp lệ: {interval}. "
                f"Vui lòng chọn: {', '.join(self.interval_map.keys())}"
            )
            raise ValueError(msg)

        # Create ticker model with normalized interval
        ticker = TickerModel(
            symbol=self.symbol,
            start=start,
            end=end,
            interval=interval_key
        )

        return ticker
    
    def _long_history(
        self,
        start: str,
        end: Optional[str],
        show_log: bool = False,
        asset_type: Optional[str] = None,
        _skip_long_check: bool = True
    ) -> pd.DataFrame:
        """
        Truy xuất dữ liệu lịch sử dài hạn từ TCBS cho khung
        thời gian ngày
        """
        if not end:
            end = datetime.now().strftime("%Y-%m-%d")

        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")

        combined_data = []
        current_start = start_date

        # Process each year chunk moving forward from start date
        while current_start <= end_date:
            try:
                # Calculate end date for this chunk
                next_year_date = datetime(
                    current_start.year + 1,
                    current_start.month,
                    1
                )
                year_end = min(
                    next_year_date - timedelta(days=1),
                    end_date
                )

                # Format dates as strings
                year_start_str = current_start.strftime("%Y-%m-%d")
                year_end_str = year_end.strftime("%Y-%m-%d")

                if show_log:
                    msg = (
                        f"Fetching chunk from {year_start_str} "
                        f"to {year_end_str}"
                    )
                    logger.info(msg)

                # Fetch data for this year chunk
                try:
                    data = self.history(
                        start=year_start_str,
                        end=year_end_str,
                        interval="1D",
                        show_log=show_log,
                        asset_type=asset_type,
                        _skip_long_check=True,
                        # Pass defaults or instance configs here if needed,
                        # currently history uses instance defaults if not provided
                    )
                    combined_data.append(data)
                except Exception as e:
                    msg = (
                        f"Dữ liệu không tồn tại từ "
                        f"{year_start_str} đến {year_end_str}: {e}"
                    )
                    logger.error(msg)

                # Move to next year's start
                current_start = next_year_date

            except Exception as e:
                logger.error(f"Error processing year chunk: {str(e)}")
                # Move forward by a year even if an error occurs
                current_start = datetime(
                    current_start.year + 1,
                    current_start.month,
                    1
                )

        # If no data was found, raise an error
        if not combined_data:
            raise ValueError(
                f"Không tìm thấy dữ liệu cho {self.symbol} "
                f"từ {start} đến {end}"
            )

        # Combine all chunks
        df = pd.concat(combined_data, ignore_index=True)

        # Filter to ensure we only get data in the requested range
        df = df[(df['time'] >= start) & (df['time'] <= end)]

        return df

    @optimize_execution("TCBS")
    def history(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None,
        interval: Optional[str] = "1D",
        show_log: bool = False,
        count_back: Optional[int] = 365,
        asset_type: Optional[str] = None,
        _skip_long_check: bool = False,
        length: Optional[Union[str, int]] = None,
        proxy_mode: Optional[str] = None,
        proxy_list: Optional[list] = None
    ) -> pd.DataFrame:
        """
        Tham số:
            - start (tùy chọn): thời gian bắt đầu lấy dữ liệu.
              Bắt buộc nếu không có length hoặc count_back.
            - end (tùy chọn): thời gian kết thúc lấy dữ liệu.
              Mặc định là None (ngày hiện tại).
            - interval (tùy chọn): Khung thời gian. Mặc định "1D".
            - length (tùy chọn): Khoảng thời gian phân tích (vd: '3M', 150, '150').
              Nhận giá trị chuỗi (vd 3M), số ngày (int/str), hoặc số bars (vd '100b').
            - count_back (tùy chọn): Số lượng nến (bars) cần lấy.
            - show_log (tùy chọn): Hiển thị log.
            - asset_type (tùy chọn): Loại tài sản (stock, index,
              derivative). Mặc định là None (tự xác định).
            - _skip_long_check (tùy chọn): Bỏ qua kiểm tra thời
              gian dài để tránh đệ quy vô hạn. Mặc định là False.
        """
        # Calculate start if not provided
        if start is None:
            # Check if length defines bars
            if length is not None:
                bars_from_len, len_remainder = interpret_lookback_length(length)
                if bars_from_len is not None:
                    count_back = bars_from_len
                    length = None
                else:
                    length = len_remainder
            
            if length is not None:
                start = get_start_date_from_lookback(
                    lookback_length=length,
                    end_date=end
                )
            elif count_back is not None:
                start = get_start_date_from_lookback(
                    bars=count_back,
                    interval=interval,
                    end_date=end
                )
            else:
                raise ValueError(
                    "Tham số 'start' là bắt buộc nếu không cung cấp "
                    "'length' hoặc 'count_back'."
                )

        # Validate inputs
        if end is None:
            end = datetime.now().strftime("%Y-%m-%d")

        ticker = self._input_validation(start, end, interval)
        
        if count_back is None:
            count_back = 365

        if asset_type is None:
            asset_type = self.asset_type

        # calculate days between start and end
        start_time = datetime.strptime(ticker.start, "%Y-%m-%d")
        end_time_str = ticker.end if ticker.end else (
            datetime.now().strftime("%Y-%m-%d")
        )
        end_time = datetime.strptime(end_time_str, "%Y-%m-%d")

        # validate if the end date is not earlier than the start date
        if end_time < start_time:
            raise ValueError(
                "Thời gian kết thúc không thể sớm hơn "
                "thời gian bắt đầu."
            )

        days = (end_time - start_time).days

        # Only check for long date ranges if not explicitly skipped
        if not _skip_long_check and days > 365:
            return self._long_history(start, end, show_log, asset_type)
        else:
            if end is None:
                end_stamp = int(datetime.now().timestamp())
            else:
                end_stamp = int(end_time.timestamp())

            # Normalize interval for API endpoint selection
            timeframe = normalize_interval(ticker.interval)
            
            # Map TimeFrame enum value to interval key (e.g., D -> 1D)
            interval_key = _TIMEFRAME_MAP.get(timeframe.value)
            if interval_key is None:
                raise ValueError(
                    f"Invalid timeframe value: {timeframe.value}"
                )
            
            if interval_key in ["1D", "1W", "1M"]:
                end_point = "bars-long-term"
            elif interval_key in ["1m", "5m", "15m", "30m", "1H"]:
                end_point = "bars"
            else:
                end_point = "bars"

            # Translate the interval to TCBS format
            interval_value = self.interval_map[interval_key]

            # Construct the URL for fetching data
            if asset_type == "derivative":
                url = (
                    f"{self.base_url}/{_FUTURE_URL}/v2/stock/{end_point}"
                    f"?resolution={interval_value}&ticker={self.symbol}"
                    f"&type={asset_type}&to={end_stamp}&countBack={count_back}"
                )
            else:
                url = (
                    f"{self.base_url}/{_STOCKS_URL}/v2/stock/{end_point}"
                    f"?resolution={interval_value}&ticker={self.symbol}"
                    f"&type={asset_type}&to={end_stamp}&countBack={count_back}"
                )

            if interval_value in ["1", "5", "15", "30", "60"]:
                # replace 'bars-long-term' with 'bars' in the url
                url = url.replace("bars-long-term", "bars")

            if show_log:
                logger.info(f"Tải dữ liệu từ {url}")

            # Send a request to fetch the data using client wrapper
            # Use instance defaults if not overridden
            req_mode = client.RequestMode.DIRECT 
            p_mode = proxy_mode or self.proxy_mode
            p_list = proxy_list or self.proxy_list
            
            if p_mode == "auto" or (p_list is not None and len(p_list) > 0):
                req_mode = client.RequestMode.PROXY
                
            response_json = client.send_request(
                url=url,
                headers=self.headers,
                show_log=show_log and False, # Reduce noise, we logged above
                request_mode=req_mode,
                proxy_mode=p_mode,
                proxy_list=p_list
            )

            # client.send_request returns the json payload directly
            json_data = response_json.get('data')
            if json_data is None:
                 # Try fallback if structure differs or check for error
                 # But TCBS usually returns 'data' key on 200
                 pass

            if show_log:
                msg = (
                    f'Truy xuất thành công dữ liệu {ticker.symbol} '
                    f'từ {ticker.start} đến {ticker.end}, '
                    f'khung thời gian {ticker.interval}.'
                )
                logger.info(msg)

            df = self._as_df(json_data, asset_type)

        df.attrs['symbol'] = self.symbol
        df.category = self.asset_type
        df.source = self.data_source
        
        return df
        
    def _as_df(
        self,
        history_data: Dict,
        asset_type: str,
        floating: Optional[int] = 2
    ) -> pd.DataFrame:
        """
        Backward compatibility method that delegates to shared
        data_transform utility
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
    def intraday(
        self,
        page_size: Optional[int] = 100,
        page: Optional[int] = 0,
        show_log: bool = False
    ) -> pd.DataFrame:
        """
        Truy xuất dữ liệu khớp lệnh của mã chứng khoán bất kỳ
        từ nguồn dữ liệu TCBS
        """
        # Handle None defaults
        if page_size is None:
            page_size = 100
        if page is None:
            page = 0

        market_status = trading_hours("HOSE")
        if (
            market_status['is_trading_hour'] is False and
            market_status['data_status'] == 'preparing'
        ):
            raise ValueError(
                f"{market_status['time']}: Dữ liệu khớp lệnh "
                f"không thể truy cập trong thời gian chuẩn bị "
                f"phiên mới. Vui lòng quay lại sau."
            )

        # Validate input
        if self.symbol is None:
            raise ValueError(
                "Vui lòng nhập mã chứng khoán cần truy xuất "
                "khi khởi tạo Trading Class."
            )

        # warning if page_size is greater than 30_000
        if page_size > 30_000:
            logger.warning(
                "Bạn đang yêu cầu truy xuất quá nhiều dữ liệu, "
                "điều này có thể gây lỗi quá tải."
            )

        # Fetch data
        combined_data = []
        total_pages = (
            (page_size // 100) +
            (1 if page_size % 100 != 0 else 0)
        )

        for i in range(total_pages):
            current_size = min(100, page_size - 100 * i)
            url = (
                f'{self.base_url}/{_STOCKS_URL}/v1/intraday/'
                f'{self.symbol}/his/paging'
            )
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

        # Reduce the time index by 7 hours to match GMT+7 timezone
        df['time'] = df['time'] - pd.Timedelta(hours=7)

        return df


# Register TCBS Quote provider
from vnstock.core.registry import ProviderRegistry  # noqa: E402, F401
ProviderRegistry.register('quote', 'tcbs', Quote)


