"""History module for VCI."""

from typing import Optional, Union
from datetime import datetime
import pandas as pd
from vnai import optimize_execution
from vnstock.core.types import TimeFrame
from vnstock.core.utils.interval import normalize_interval
from .const import (
    _TRADING_URL, _INTERVAL_MAP, _RESAMPLE_MAP,
    _OHLC_MAP, _OHLC_DTYPE, _INTRADAY_URL,
    _INTRADAY_MAP, _INTRADAY_DTYPE, _PRICE_DEPTH_MAP, _INDEX_MAPPING
)
from vnstock.core.models import TickerModel
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.market import trading_hours
from vnstock.core.utils.parser import get_asset_type, convert_time_flexible
from vnstock.core.utils.validation import validate_symbol
from vnstock.core.utils.user_agent import get_headers
from vnstock.core.utils.client import send_request, ProxyConfig
from vnstock.core.utils.transform import ohlc_to_df, intraday_to_df

logger = get_logger(__name__)

# TimeFrame to interval key mapping
# Standard format: m/1m=minute, h/1H=hour, d/1D=day, w/1W=week, M/1M=month
_TIMEFRAME_MAP = {
    '1D': '1D',
    '1H': '1H',
    '1W': '1W',
    '1M': '1M',
    '1m': '1m',
    '5m': '5m',
    '15m': '15m',
    '30m': '30m'
}


class Quote:
    """
    The Quote class is used to fetch historical price data from VCI.

    Parameters:
        - symbol (required): the stock symbol to fetch data for.
        - random_agent (optional): whether to use random user agent.
            Default is False.
        - proxy_config (optional): proxy configuration. Default is None.
        - show_log (optional): whether to show log. Default is True.
    """

    def __init__(
        self,
        symbol,
        random_agent=False,
        proxy_config: Optional[ProxyConfig] = None,
        show_log=True
    ):
        self.symbol = validate_symbol(symbol)
        self.data_source = 'VCI'
        self._history = None  # Cache for historical data
        self.asset_type = get_asset_type(self.symbol)
        self.base_url = _TRADING_URL
        self.headers = get_headers(
            data_source=self.data_source,
            random_agent=random_agent
        )
        self.interval_map = _INTERVAL_MAP
        self.show_log = show_log
        self.proxy_config = (
            proxy_config if proxy_config is not None else ProxyConfig()
        )

        if not show_log:
            logger.setLevel('CRITICAL')

        if 'INDEX' in self.symbol:
            self.symbol = self._index_validation()

    def _index_validation(self) -> str:
        """
        If symbol contains 'INDEX' substring, validate it with
        _INDEX_MAPPING.
        """
        if self.symbol not in _INDEX_MAPPING.keys():
            valid_indices = ', '.join(_INDEX_MAPPING.keys())
            raise ValueError(
                f"Không tìm thấy mã chứng khoán {self.symbol}. "
                f"Các giá trị hợp lệ: {valid_indices}"
            )
        return _INDEX_MAPPING[self.symbol]

    def _input_validation(
        self,
        start: str,
        end: Optional[str],
        interval: Optional[str]
    ) -> tuple:
        """
        Validate input data and return TickerModel and interval_key.
        """
        timeframe = normalize_interval(interval)
        ticker = TickerModel(
            symbol=self.symbol,
            start=start,
            end=end,
            interval=str(timeframe)
        )

        interval_key = _TIMEFRAME_MAP.get(timeframe.value)
        if (
            interval_key is None or
            interval_key not in self.interval_map.keys()
        ):
            valid_intervals = ', '.join(self.interval_map.keys())
            msg = (
                f"Giá trị interval không hợp lệ: {interval}. "
                f"Vui lòng chọn: {valid_intervals}"
            )
            raise ValueError(msg)

        return ticker, interval_key

    @optimize_execution("VCI")
    def history(
        self,
        start: str,
        end: Optional[str] = None,
        interval: Optional[str] = "1D",
        show_log: Optional[bool] = False,
        count_back: Optional[int] = None,
        floating: Optional[int] = 2
    ) -> pd.DataFrame:
        """
        Tải lịch sử giá của mã chứng khoán từ nguồn dữ liệu VCI.

        Tham số:
            - start (bắt buộc): thời gian bắt đầu lấy dữ liệu,
              có thể là ngày dạng string kiểu "YYYY-MM-DD" hoặc
              "YYYY-MM-DD HH:MM:SS".
            - end (tùy chọn): thời gian kết thúc lấy dữ liệu.
              Mặc định là None, chương trình tự động lấy thời điểm
              hiện tại.
            - interval (tùy chọn): Khung thời gian trích xuất dữ liệu
              giá lịch sử. Giá trị nhận: 1m, 5m, 15m, 30m, 1H, 1D, 1W,
              1M. Mặc định là "1D".
            - show_log (tùy chọn): Hiển thị thông tin log giúp debug
              dễ dàng. Mặc định là False.
            - count_back (tùy chọn): Số lượng dữ liệu trả về từ thời
              điểm cuối.
            - floating (tùy chọn): Số chữ số thập phân cho giá.
              Mặc định là 2.
        """
        # Validate inputs
        ticker, interval_key = self._input_validation(
            start,
            end,
            interval
        )

        # Parse start time - support both date and datetime formats
        try:
            # Try datetime format first
            start_time = datetime.strptime(
                ticker.start,
                "%Y-%m-%d %H:%M:%S"
            )
        except ValueError:
            try:
                # Try date only format
                start_time = datetime.strptime(ticker.start, "%Y-%m-%d")
            except ValueError:
                raise ValueError(
                    f"Định dạng ngày không hợp lệ: {ticker.start}. "
                    f"Sử dụng định dạng YYYY-MM-DD hoặc "
                    f"YYYY-MM-DD HH:MM:SS"
                )

        # Calculate end timestamp
        if end is not None:
            try:
                # Try datetime format first
                end_time = datetime.strptime(
                    ticker.end,
                    "%Y-%m-%d %H:%M:%S"
                )
            except ValueError:
                try:
                    # Try date only format
                    end_time = datetime.strptime(
                        ticker.end,
                        "%Y-%m-%d"
                    ) + pd.Timedelta(days=1)
                except ValueError:
                    raise ValueError(
                        f"Định dạng ngày không hợp lệ: {ticker.end}. "
                        f"Sử dụng định dạng YYYY-MM-DD hoặc "
                        f"YYYY-MM-DD HH:MM:SS"
                    )

            if start_time > end_time:
                raise ValueError(
                    "Thời gian bắt đầu không thể lớn hơn "
                    "thời gian kết thúc."
                )
            end_stamp = int(end_time.timestamp())
        else:
            end_time = datetime.now() + pd.Timedelta(days=1)
            end_stamp = int(end_time.timestamp())

        interval_value = self.interval_map[interval_key]

        # Calculate count_back automatically if not provided
        auto_count_back = 1000
        business_days = pd.bdate_range(start=start_time, end=end_time)

        if count_back is None and end is not None:
            interval_mapped = interval_value

            if interval_mapped == "ONE_DAY":
                # Count business days (excluding weekends)
                auto_count_back = len(business_days) + 1
            elif interval_mapped == "ONE_HOUR":
                # Business days * trading hours per day (6.5 hours)
                auto_count_back = int(len(business_days) * 6.5 + 1)
            elif interval_mapped == "ONE_MINUTE":
                # Business days * trading minutes per day (390 min)
                auto_count_back = int(len(business_days) * 390 + 1)
        else:
            auto_count_back = (
                count_back if count_back is not None else 1000
            )

        # Prepare request
        url = f'{self.base_url}chart/OHLCChart/gap-chart'
        payload = {
            "timeFrame": interval_value,
            "symbols": [self.symbol],
            "to": end_stamp,
            "countBack": auto_count_back
        }

        # Use the send_request utility
        json_data = send_request(
            url=url,
            headers=self.headers,
            method="POST",
            payload=payload,
            show_log=show_log if show_log is not None else False,
            proxy_list=self.proxy_config.proxy_list,
            proxy_mode=self.proxy_config.proxy_mode,
            request_mode=self.proxy_config.request_mode,
            hf_proxy_url=self.proxy_config.hf_proxy_url
        )

        # Debug: log response structure
        if show_log:
            logger.info(f"API Response type: {type(json_data)}")
            data_len = (
                len(json_data) if hasattr(json_data, '__len__') else 'N/A'
            )
            logger.info(f"Response length: {data_len}")

        # Handle both list and dict responses
        if isinstance(json_data, list):
            # API returns list of OHLC data directly
            pass  # json_data is already in correct format
        elif isinstance(json_data, dict) and 'data' in json_data:
            # API returns dict with 'data' key
            json_data = json_data['data']

        # Transform VCI array format to row format
        if isinstance(json_data, list) and len(json_data) > 0:
            list_data = json_data
            symbol_data = list_data[0]
            if (
                isinstance(symbol_data, dict) and
                'o' in symbol_data and
                isinstance(symbol_data['o'], list)
            ):
                # Vectorized conversion using pandas
                json_data = pd.DataFrame({
                    't': symbol_data['t'],
                    'o': symbol_data['o'],
                    'h': symbol_data['h'],
                    'l': symbol_data['l'],
                    'c': symbol_data['c'],
                    'v': symbol_data['v']
                }).to_dict('records')

        if not json_data:
            raise ValueError(
                "Không tìm thấy dữ liệu. Vui lòng kiểm tra lại "
                "mã chứng khoán hoặc thời gian truy xuất."
            )

        # Use the ohlc_to_df utility
        df = ohlc_to_df(
            data=json_data,
            column_map=_OHLC_MAP,
            dtype_map=_OHLC_DTYPE,
            symbol=self.symbol,
            asset_type=self.asset_type,
            source=self.data_source,
            interval=interval_key,
            resample_map=_RESAMPLE_MAP
        )

        return df

    @optimize_execution("VCI")
    def intraday(
        self,
        page_size: Optional[int] = 100,
        last_time: Optional[Union[str, int, float]] = None,
        last_time_format: Optional[str] = None,
        show_log: bool = False
    ) -> pd.DataFrame:
        """
        Truy xuất dữ liệu khớp lệnh của mã chứng khoán bất kỳ từ
        nguồn dữ liệu VCI.

        Tham số:
            - page_size (tùy chọn): Số lượng dữ liệu trả về trong
              một lần request. Mặc định là 100.
            - last_time (tùy chọn): Thời gian cắt dữ liệu, dùng để
              lấy dữ liệu sau thời gian cắt. Có thể là epoch timestamp
              (int/float) hoặc chuỗi datetime. Mặc định là None.
            - last_time_format (tùy chọn): Định dạng để parse last_time
              nếu là chuỗi. Mặc định sẽ thử 'YYYY-MM-DD HH:MM:SS'
              và 'YYYY-MM-DD'.
            - show_log (tùy chọn): Hiển thị thông tin log giúp debug
              dễ dàng. Mặc định là False.
        """
        market_status = trading_hours("HOSE")
        if (
            market_status['is_trading_hour'] is False and
            market_status['data_status'] == 'preparing'
        ):
            raise ValueError(
                f"{market_status['time']}: Dữ liệu khớp lệnh không "
                f"thể truy cập trong thời gian chuẩn bị phiên mới. "
                f"Vui lòng quay lại sau."
            )

        if self.symbol is None:
            raise ValueError(
                "Vui lòng nhập mã chứng khoán cần truy xuất khi "
                "khởi tạo Trading Class."
            )

        if page_size and page_size > 30_000:
            logger.warning(
                "Bạn đang yêu cầu truy xuất quá nhiều dữ liệu, "
                "điều này có thể gây lỗi quá tải."
            )

        # Parse last_time to epoch timestamp
        parsed_last_time = convert_time_flexible(last_time, last_time_format)

        url = f'{self.base_url}{_INTRADAY_URL}/LEData/getAll'
        payload = {
            "symbol": self.symbol,
            "limit": page_size,
            "truncTime": parsed_last_time
        }

        # Fetch data using the send_request utility
        data = send_request(
            url=url,
            headers=self.headers,
            method="POST",
            payload=payload,
            show_log=show_log,
            proxy_list=self.proxy_config.proxy_list,
            proxy_mode=self.proxy_config.proxy_mode,
            request_mode=self.proxy_config.request_mode,
            hf_proxy_url=self.proxy_config.hf_proxy_url
        )

        # Ensure data is a list
        if isinstance(data, dict):
            data = data.get('data', []) if 'data' in data else []

        # Transform data using intraday_to_df utility
        df = intraday_to_df(
            data=data,
            column_map=_INTRADAY_MAP,
            dtype_map=_INTRADAY_DTYPE,
            symbol=self.symbol,
            asset_type=self.asset_type,
            source=self.data_source
        )

        return df

    @optimize_execution("VCI")
    def price_depth(
        self,
        show_log: Optional[bool] = False
    ) -> pd.DataFrame:
        """
        Truy xuất thống kê độ bước giá & khối lượng khớp lệnh của mã
        chứng khoán bất kỳ từ nguồn dữ liệu VCI.

        Tham số:
            - show_log (tùy chọn): Hiển thị thông tin log giúp debug
              dễ dàng. Mặc định là False.
        """
        market_status = trading_hours("HOSE")
        if (
            market_status['is_trading_hour'] is False and
            market_status['data_status'] == 'preparing'
        ):
            raise ValueError(
                f"{market_status['time']}: Dữ liệu khớp lệnh không "
                f"thể truy cập trong thời gian chuẩn bị phiên mới. "
                f"Vui lòng quay lại sau."
            )

        if self.symbol is None:
            raise ValueError(
                "Vui lòng nhập mã chứng khoán cần truy xuất khi "
                "khởi tạo Trading Class."
            )

        url = (
            f'{self.base_url}{_INTRADAY_URL}/'
            f'AccumulatedPriceStepVol/getSymbolData'
        )
        payload = {"symbol": self.symbol}

        # Fetch data using the send_request utility
        data = send_request(
            url=url,
            headers=self.headers,
            method="POST",
            payload=payload,
            show_log=show_log if show_log is not None else False,
            proxy_list=self.proxy_config.proxy_list,
            proxy_mode=self.proxy_config.proxy_mode,
            request_mode=self.proxy_config.request_mode,
            hf_proxy_url=self.proxy_config.hf_proxy_url
        )

        # Process the data to DataFrame
        df = pd.DataFrame(data)

        # Select columns in _PRICE_DEPTH_MAP and rename them
        df = df[_PRICE_DEPTH_MAP.keys()]
        df.rename(columns=_PRICE_DEPTH_MAP, inplace=True)

        df.source = self.data_source

        return df


# Register VCI Quote provider
from vnstock.core.registry import ProviderRegistry  # noqa: E402, F401
ProviderRegistry.register('quote', 'vci', Quote)
