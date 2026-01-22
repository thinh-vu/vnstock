"""Quote module for KB Securities (KBS) data source."""

import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Optional, Union, List
from vnai import agg_execution
from vnstock.core.models import TickerModel
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.parser import get_asset_type
from vnstock.core.utils.lookback import get_start_date_from_lookback, interpret_lookback_length
from vnstock.core.utils.client import send_request, ProxyConfig
from vnstock.core.utils.transform import process_match_types
from vnstock.core.utils.user_agent import get_headers
from vnstock.core.registry import ProviderRegistry  # noqa: E402, F401
from vnstock.explorer.kbs.const import (
    _IIS_BASE_URL, _STOCK_DATA_URL, _SAS_HISTORICAL_QUOTES_URL,
    _OHLC_MAP, _OHLC_DTYPE, _INTERVAL_MAP, _RESAMPLE_MAP,
    _INTRADAY_MAP, _INTRADAY_DTYPE
)

logger = get_logger(__name__)


class Quote:
    """
    Lớp truy cập dữ liệu giá lịch sử từ KB Securities (KBS).
    """

    def __init__(
        self,
        symbol: str,
        random_agent: Optional[bool] = False,
        proxy_config: Optional[ProxyConfig] = None,
        show_log: Optional[bool] = False,
        proxy_mode: Optional[str] = None,
        proxy_list: Optional[List[str]] = None,
    ):
        """
        Khởi tạo Quote client cho KBS.

        Args:
            symbol: Mã chứng khoán (VD: 'ACB', 'VNM').
            random_agent: Sử dụng user agent ngẫu nhiên. Mặc định False.
            proxy_config: Cấu hình proxy. Mặc định None.
            show_log: Hiển thị log debug. Mặc định False.
            proxy_mode: Chế độ proxy (try, rotate, random, single). Mặc định None.
            proxy_list: Danh sách proxy URLs. Mặc định None.
        """
        self.symbol = symbol.upper()
        self.data_source = 'KBS'
        self.asset_type = get_asset_type(self.symbol)
        self.base_url = _IIS_BASE_URL
        self.headers = get_headers(data_source=self.data_source, random_agent=random_agent)
        self.show_log = show_log
        self.interval_map = _INTERVAL_MAP
        
        # Handle proxy configuration
        if proxy_config is None:
            # Create ProxyConfig from individual arguments
            p_mode = proxy_mode if proxy_mode else 'try'
            # If user provides list, set request_mode to PROXY
            req_mode = 'direct'
            if proxy_list and len(proxy_list) > 0:
                req_mode = 'proxy'
                
            self.proxy_config = ProxyConfig(
                proxy_mode=p_mode,
                proxy_list=proxy_list,
                request_mode=req_mode
            )
        else:
            self.proxy_config = proxy_config

        if not show_log:
            logger.setLevel('CRITICAL')

    def _input_validation(self, start: Optional[str], end: str, interval: str) -> TickerModel:
        """
        Validate input parameters.

        Args:
            start: Ngày bắt đầu (YYYY-MM-DD hoặc DD-MM-YYYY).
            end: Ngày kết thúc (YYYY-MM-DD hoặc DD-MM-YYYY).
            interval: Khung thời gian (1m, 5m, 15m, 30m, 1H, 1D, 1W, 1M).

        Returns:
            TickerModel instance với dữ liệu đã validate.

        Raises:
            ValueError: Nếu interval không hợp lệ.
        """
        ticker = TickerModel(symbol=self.symbol, start=start, end=end, interval=interval)
        
        if interval not in self.interval_map:
            valid_intervals = ', '.join(self.interval_map.keys())
            raise ValueError(
                f"Giá trị interval không hợp lệ: {interval}. "
                f"Vui lòng chọn: {valid_intervals}"
            )
        
        return ticker

    def _format_date_for_api(self, date_str: str) -> str:
        """
        Chuyển đổi ngày từ YYYY-MM-DD sang DD-MM-YYYY cho API KBS.

        Args:
            date_str: Ngày dạng YYYY-MM-DD.

        Returns:
            Ngày dạng DD-MM-YYYY.
        """
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return dt.strftime("%d-%m-%Y")
        except ValueError:
            # Nếu đã đúng format DD-MM-YYYY thì trả về như cũ
            return date_str

    @agg_execution("KBS")
    def history(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None,
        interval: Optional[str] = "1D",
        to_df: Optional[bool] = True,
        show_log: Optional[bool] = False,
        count_back: Optional[int] = None,
        floating: Optional[int] = 2,
        length: Optional[Union[str, int]] = None,
        get_all: Optional[bool] = False
    ) -> Union[pd.DataFrame, str]:
        """
        Tải lịch sử giá của mã chứng khoán từ KBS.

        Args:
            start: Ngày bắt đầu (YYYY-MM-DD hoặc DD-MM-YYYY). Bắt buộc nếu không có length hoặc count_back.
            end: Ngày kết thúc (YYYY-MM-DD hoặc DD-MM-YYYY). Mặc định None (lấy đến hiện tại).
            interval: Khung thời gian trích xuất dữ liệu. Giá trị nhận: 1m, 5m, 15m, 30m, 1H, 1D, 1W, 1M. Mặc định "1D".
            to_df: Trả về DataFrame. Mặc định True. False để trả về JSON.
            show_log: Hiển thị log debug.
            count_back: Số lượng nến (bars) cần lấy.
            floating: Số chữ số thập phân cho giá. Mặc định 2.
            length: Khoảng thời gian phân tích (vd: '3M', 150, '150'). Nhận giá trị chuỗi (vd 3M), số ngày (int/str), hoặc số bars (vd '100b').
            get_all: Lấy tất cả các cột từ API response. Mặc định False (chỉ lấy cột chuẩn hóa).

        Returns:
            DataFrame hoặc JSON string chứa dữ liệu OHLCV.

        Examples:
            >>> quote = Quote('ACB')
            >>> df = quote.history(start='2024-01-01', end='2024-12-31', interval='1D')
            >>> print(df.columns.tolist())
            ['time', 'open', 'high', 'low', 'close', 'volume']
            
            >>> # Sử dụng length để lấy dữ liệu 1 tháng gần nhất
            >>> df_1m = quote.history(length='1M', interval='1D')
            
            >>> # Lấy 100 nến dữ liệu
            >>> df_100 = quote.history(count_back=100, interval='1D')
            
            >>> # Lấy dữ liệu 150 ngày
            >>> df_150d = quote.history(length=150, interval='1D')
            
            >>> # Lấy dữ liệu 3 tháng với kết thúc vào ngày cụ thể
            >>> df_3m = quote.history(end='2024-12-31', length='3M', interval='1D')
            
            >>> # Lấy tất cả các cột (bao gồm cả cột value)
            >>> df_all = quote.history(length='1M', interval='1D', get_all=True)
        """
        # Set end date to today if not provided
        if end is None:
            end = datetime.now().strftime("%Y-%m-%d")

        # Calculate start if not provided
        if start is None:
            # Check if length defines bars
            if length is not None:
                length_str = str(length)
                if length_str.endswith('b'):
                    # Length defines number of bars
                    count_back = int(length_str[:-1])
                    # For bars-based length, we need to estimate start date
                    # This is approximate and will be refined by count_back later
                    start = get_start_date_from_lookback(lookback_length=length_str, end_date=end)
                else:
                    # Length defines time period
                    start = get_start_date_from_lookback(lookback_length=length_str, end_date=end)
            elif count_back is not None:
                # For count_back, estimate start date based on interval
                if interval == '1D':
                    start = (datetime.strptime(end, "%Y-%m-%d") - timedelta(days=count_back * 2)).strftime("%Y-%m-%d")
                elif interval == '1H':
                    start = (datetime.strptime(end, "%Y-%m-%d") - timedelta(days=count_back // 6)).strftime("%Y-%m-%d")
                elif interval == '1m':
                    start = (datetime.strptime(end, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
                else:
                    start = get_start_date_from_lookback(lookback_length='1M', end_date=end)
            else:
                raise ValueError(
                    "Tham số 'start' là bắt buộc nếu không cung cấp "
                    "'length' hoặc 'count_back'."
                )

        # Validate inputs (only if start is provided)
        if start is not None:
            ticker = self._input_validation(start, end, interval)
        else:
            # Create a minimal ticker model for validation of interval only
            # Use end as start temporarily since start is None
            ticker = TickerModel(symbol=self.symbol, start=end, end=end, interval=interval)
            # Override start with None for later processing
            ticker.start = start

        # Convert dates to KBS format (DD-MM-YYYY)
        start_date_kbs = self._format_date_for_api(start)  # Use calculated start
        end_date_kbs = self._format_date_for_api(end)

        # Get the KBS API endpoint suffix for the interval
        interval_suffix = self.interval_map[interval]
        
        # Build URL based on interval
        url = f'{_STOCK_DATA_URL}/{self.symbol}/data_{interval_suffix}'
        params = {
            'sdate': start_date_kbs,
            'edate': end_date_kbs,
        }

        # Make API request
        json_data = send_request(
            url=url,
            headers=self.headers,
            method="GET",
            params=params,
            show_log=show_log or self.show_log,
            proxy_list=self.proxy_config.proxy_list,
            proxy_mode=self.proxy_config.proxy_mode,
            request_mode=self.proxy_config.request_mode
        )

        if not json_data:
            raise ValueError(
                f"Không tìm thấy dữ liệu cho mã {self.symbol}. "
                "Vui lòng kiểm tra lại mã chứng khoán hoặc khoảng thời gian."
            )

        # Extract OHLC data based on interval
        data_key = f'data_{interval_suffix}'
        if data_key not in json_data:
            raise ValueError(
                f"Không tìm thấy dữ liệu cho interval {interval}. "
                f"Vui lòng kiểm tra lại khoảng thời gian hoặc interval."
            )

        ohlc_data = json_data[data_key]

        if not ohlc_data:
            raise ValueError(
                f"Dữ liệu trống cho mã {self.symbol} với interval {interval}."
            )

        if not to_df:
            return json.dumps(ohlc_data)

        # Convert to DataFrame
        df = pd.DataFrame(ohlc_data)

        # Handle 'va' column - remove from standard output, keep as 'value' if get_all=True
        va_column = None
        if 'va' in df.columns:
            va_column = df['va'].copy()
            if not get_all:
                # Remove 'va' column from standard output
                df = df.drop(columns=['va'])

        # Rename columns
        df = df.rename(columns=_OHLC_MAP)

        # Add 'value' column if get_all=True and 'va' was present
        if get_all and va_column is not None:
            df['value'] = va_column

        # Convert time column to datetime
        df['time'] = pd.to_datetime(df['time'])

        # Sort by time
        df = df.sort_values('time').reset_index(drop=True)

        # Set data types
        for col, dtype in _OHLC_DTYPE.items():
            if col in df.columns:
                df[col] = df[col].astype(dtype)
        
        # Set data type for 'value' column if present
        if 'value' in df.columns:
            df['value'] = df['value'].astype('float64')

        # Apply floating point precision to OHLC columns
        ohlc_cols = ['open', 'high', 'low', 'close']
        for col in ohlc_cols:
            if col in df.columns:
                df[col] = df[col].round(floating)

        # Trim data to start time if needed
        df = df[df['time'] >= pd.to_datetime(start)].reset_index(drop=True)

        # Apply count_back if specified
        if count_back is not None:
            df = df.tail(count_back).reset_index(drop=True)

        # Add metadata
        df.attrs['symbol'] = self.symbol
        df.attrs['source'] = self.data_source
        df.attrs['interval'] = interval
        df.attrs['length'] = length
        df.attrs['start'] = start 
        df.attrs['end'] = end

        if show_log or self.show_log:
            logger.info(
                f'Truy xuất thành công {len(df)} bản ghi giá cho {self.symbol} '
                f'({interval}) từ {start_date_kbs} đến {end_date_kbs}.'
            )

        return df

    @agg_execution("KBS")
    def intraday(
        self,
        page_size: Optional[int] = 100,
        page: Optional[int] = 1,
        to_df: Optional[bool] = True,
        get_all: Optional[bool] = False,
        show_log: Optional[bool] = False,
    ) -> Union[pd.DataFrame, str]:
        """
        Truy xuất dữ liệu khớp lệnh intraday (real-time matching data) của mã chứng khoán từ KBS.
        
        Mặc định trả về các cột chuẩn hóa (time, price, volume, match_type, id).
        Sử dụng get_all=True để lấy tất cả các cột từ API response.

        Args:
            page_size: Số lượng bản ghi trên mỗi trang (mặc định 100).
                       Thường 1 ngày có thể lên đến 100K dòng (VN30 derivatives) hoặc 50-70K (cổ phiếu cơ sở).
            page: Trang dữ liệu (mặc định 1).
            to_df: Trả về DataFrame. Mặc định True. False để trả về JSON.
            get_all: Lấy tất cả các cột từ API response. Mặc định False (chỉ lấy cột chuẩn hóa).
            show_log: Hiển thị log debug.

        Returns:
            DataFrame hoặc JSON string chứa dữ liệu khớp lệnh intraday.
            
            **Cột chuẩn hóa (Core columns):**
            - time: Thời gian giao dịch (YYYY-MM-DD HH:MM:SS)
            - price: Giá khớp
            - volume: Khối lượng khớp
            - match_type: Loại khớp lệnh (buy, sell, atc, ato)
            - id: ID giao dịch (từ KBS: timestamp + price + volume)
            
            **Cột bổ sung (nếu get_all=True):**
            - trading_date: Ngày giao dịch (DD/MM/YYYY)
            - symbol: Mã chứng khoán
            - price_change: Thay đổi giá so với lần trước
            - accumulated_volume: Khối lượng tích lũy
            - accumulated_value: Giá trị tích lũy

        Examples:
            >>> quote = Quote('ACB')
            
            >>> # Lấy 100 bản ghi (cột chuẩn hóa)
            >>> df = quote.intraday(page_size=100)
            
            >>> # Lấy trang thứ 2
            >>> df_page2 = quote.intraday(page=2, page_size=100)
            
            >>> # Lấy tất cả các cột
            >>> df_all = quote.intraday(get_all=True)
        """
        # Build URL for intraday trade history
        url = f'{_IIS_BASE_URL}/trade/history/{self.symbol}'
        
        # Add pagination parameters
        params = {
            'page': page,
            'limit': page_size,
        }

        # Make API request
        json_data = send_request(
            url=url,
            headers=self.headers,
            method="GET",
            params=params,
            show_log=show_log or self.show_log,
            proxy_list=self.proxy_config.proxy_list,
            proxy_mode=self.proxy_config.proxy_mode,
            request_mode=self.proxy_config.request_mode
        )

        if not json_data or 'data' not in json_data:
            raise ValueError(
                f"Không tìm thấy dữ liệu intraday cho mã {self.symbol}. "
                "Vui lòng kiểm tra lại mã chứng khoán hoặc thử lại sau."
            )

        intraday_data = json_data.get('data', [])

        if not intraday_data:
            raise ValueError(
                f"Dữ liệu intraday trống cho mã {self.symbol}."
            )

        if not to_df:
            return json.dumps(intraday_data)

        # Convert to DataFrame
        df = pd.DataFrame(intraday_data)

        # Rename columns using mapping
        df = df.rename(columns=_INTRADAY_MAP)

        # Convert timestamp to datetime
        # KBS format: "2026-01-14 14:27:23:15" (with milliseconds as :MS instead of .MS)
        if 'timestamp' in df.columns:
            df['timestamp'] = df['timestamp'].apply(
                lambda x: pd.to_datetime(x.rsplit(':', 1)[0]) if isinstance(x, str) else x
            )

        # Set data types
        for col, dtype in _INTRADAY_DTYPE.items():
            if col in df.columns:
                try:
                    df[col] = df[col].astype(dtype)
                except (ValueError, TypeError):
                    # Keep original type if conversion fails
                    pass

        # Sort by timestamp (newest first)
        df = df.sort_values('timestamp', ascending=False).reset_index(drop=True)

        # Create standardized DataFrame with core columns
        standardized_df = pd.DataFrame()
        
        # time: Full timestamp (YYYY-MM-DD HH:MM:SS)
        if 'timestamp' in df.columns:
            standardized_df['time'] = df['timestamp']
        
        # price: Match price
        if 'price' in df.columns:
            standardized_df['price'] = df['price']
        
        # volume: Match volume (KBS uses 'match_volume')
        if 'match_volume' in df.columns:
            standardized_df['volume'] = df['match_volume']
        
        # match_type: Trade side ('B' = buy, 'S' = sell)
        # Use existing process_match_types utility for ATO/ATC logic
        if 'side' in df.columns:
            # Map KBS side values to match_type format
            standardized_df['match_type'] = df['side'].fillna('')
        
        # Apply the standard process_match_types function
        if 'match_type' in standardized_df.columns:
            # Ensure time column is datetime for process_match_types
            standardized_df['time'] = pd.to_datetime(standardized_df['time'])
            standardized_df = process_match_types(
                standardized_df, 
                asset_type=self.asset_type, 
                source='KBS'
            )
            # Convert to lowercase for final output
            standardized_df['match_type'] = standardized_df['match_type'].str.lower()
        
        # id: Generate ID from timestamp, price, and volume (KBS doesn't have transaction ID)
        if 'timestamp' in df.columns:
            # Create unique ID combining timestamp, price, and volume
            standardized_df['id'] = (
                df['timestamp'].astype(str).str.replace(' ', '_').str.replace(':', '') + 
                '_' + df['price'].astype(str).str.replace('.', '') +
                '_' + df['match_volume'].astype(str)
            )
        
        # Select columns based on get_all parameter
        if get_all:
            # Add all KBS-specific columns to standardized columns
            kbs_specific_cols = [
                'trading_date', 'symbol', 'price_change', 
                'accumulated_volume', 'accumulated_value'
            ]
            for col in kbs_specific_cols:
                if col in df.columns:
                    standardized_df[col] = df[col]
            result_df = standardized_df
        else:
            # Return only core standardized columns
            result_df = standardized_df[['time', 'price', 'volume', 'match_type', 'id']]

        # Add metadata
        result_df.attrs['symbol'] = self.symbol
        result_df.attrs['source'] = self.data_source
        result_df.attrs['page'] = page
        result_df.attrs['page_size'] = page_size
        result_df.attrs['get_all'] = get_all

        if show_log or self.show_log:
            logger.info(
                f'Truy xuất thành công {len(result_df)} bản ghi khớp lệnh intraday cho {self.symbol} '
                f'(trang {page}, page_size={page_size}).'
            )

        return result_df


# Register KBS Quote provider
from vnstock.core.registry import ProviderRegistry  # noqa: E402, F401
ProviderRegistry.register('quote', 'kbs', Quote)