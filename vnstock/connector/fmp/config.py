"""
Configuration and utility functions for FMP connector.
Following VCI patterns for consistency.
"""

import os
import requests
import pandas as pd
from pandas import json_normalize
from typing import Optional
from vnstock.core.utils.logger import get_logger
from .const import _FMP_DOMAIN, _ENDPOINTS, _DEFAULT_TIMEOUT, _DEFAULT_API_KEY

logger = get_logger(__name__)

FMP_DOMAIN = 'https://financialmodelingprep.com/stable'
DEFAULT_API_KEY = 'YOUR_API_KEY'


class FMPConfig:
    """
    Configuration class for FMP API.
    Following VCI patterns for consistency.
    """

    def __init__(self, api_key: Optional[str] = None,
                 show_log: Optional[bool] = True):
        """
        Khởi tạo cấu hình FMP.

        Tham số:
            api_key (Optional[str]): FMP API key
            show_log (Optional[bool]): Hiển thị log
        """
        self.api_key = api_key or self._get_api_key()
        self.domain = _FMP_DOMAIN
        self.timeout = _DEFAULT_TIMEOUT
        self.show_log = show_log

        if not show_log:
            logger.setLevel('CRITICAL')

    def _get_api_key(self) -> str:
        """Lấy API key từ biến môi trường."""
        # Thử FMP_TOKEN trước (như trong terminal)
        api_key = os.getenv('FMP_TOKEN')
        if not api_key:
            api_key = os.getenv('FMP_API_KEY')

        if api_key:
            logger.info("Sử dụng API key từ biến môi trường")
            return api_key

        logger.warning("Không tìm thấy FMP API key. Sử dụng demo key.")
        return _DEFAULT_API_KEY

    def get_endpoint_url(self, endpoint_name: str,
                         symbol: str = None,
                         query: str = None) -> str:
        """
        Xây dựng URL endpoint hoàn chỉnh theo format mới của FMP.
        Format: https://financialmodelingprep.com/stable/endpoint?params

        Tham số:
            endpoint_name (str): Tên endpoint từ _ENDPOINTS
            symbol (str): Mã chứng khoán (tùy chọn)
            query (str): Query string cho search endpoint (tùy chọn)

        Returns:
            str: URL API hoàn chỉnh
        """
        if endpoint_name not in _ENDPOINTS:
            raise ValueError(f"Endpoint không tồn tại: {endpoint_name}")

        endpoint = _ENDPOINTS[endpoint_name]
        url = f"{self.domain}{endpoint}"

        # Xử lý parameters
        params = []
        
        if query:
            # Cho search endpoint
            params.append(f"query={query}")
        elif symbol:
            # Cho các endpoint khác cần symbol
            params.append(f"symbol={symbol}")
        
        # Thêm API key
        params.append(f"apikey={self.api_key}")
        
        # Ghép params
        url = f"{url}?{'&'.join(params)}"
        return url


def make_fmp_request(url: str, timeout: int = _DEFAULT_TIMEOUT,
                     show_log: bool = True) -> Optional[pd.DataFrame]:
    """
    Thực hiện HTTP request tới FMP API và trả về DataFrame.
    Following VCI patterns for error handling and logging.

    Tham số:
        url (str): URL API hoàn chỉnh
        timeout (int): Thời gian timeout (giây)
        show_log (bool): Hiển thị log

    Returns:
        Optional[pd.DataFrame]: Dữ liệu trả về dạng DataFrame hoặc None
    """
    if show_log:
        logger.info(f"Gửi request tới: {url}")

    try:
        response = requests.get(url, timeout=timeout)

        if response.status_code == 200:
            data = response.json()

            if isinstance(data, list):
                if len(data) == 0:
                    if show_log:
                        logger.warning("API trả về dữ liệu rỗng")
                    return pd.DataFrame()
                return pd.DataFrame(data)

            elif isinstance(data, dict):
                # Handle historical data format từ FMP
                if 'historical' in data:
                    historical_data = data['historical']
                    df = pd.DataFrame(historical_data)
                    # Thêm metadata nếu cần
                    if 'symbol' in data:
                        df['symbol'] = data['symbol']
                    return df
                else:
                    return json_normalize(data)
            else:
                if show_log:
                    logger.error(f"Kiểu dữ liệu không mong đợi: {type(data)}")
                return None

        elif response.status_code == 403:
            error_msg = "Truy cập API bị từ chối. Kiểm tra gói đăng ký."
            if show_log:
                logger.error(error_msg)
            return None

        elif response.status_code == 429:
            error_msg = "Vượt quá giới hạn request. Thử lại sau."
            if show_log:
                logger.error(error_msg)
            return None

        else:
            error_msg = f"Lỗi API {response.status_code}: {response.text}"
            if show_log:
                logger.error(error_msg)
            return None

    except requests.exceptions.Timeout:
        if show_log:
            logger.error("Request timeout")
        return None

    except requests.exceptions.RequestException as e:
        if show_log:
            logger.error(f"Request thất bại: {e}")
        return None

    except Exception as e:
        if show_log:
            logger.error(f"Lỗi không mong đợi: {e}")
        return None


def normalize_dataframe(df: pd.DataFrame,
                       date_columns: list = None,
                       show_log: bool = True) -> pd.DataFrame:
    """
    Chuẩn hóa DataFrame: convert date columns, numeric columns.

    Tham số:
        df (pd.DataFrame): DataFrame cần chuẩn hóa
        date_columns (list): Danh sách cột date cần convert
        show_log (bool): Hiển thị log

    Returns:
        pd.DataFrame: DataFrame đã chuẩn hóa
    """
    if df is None or df.empty:
        return df

    from .const import _DATE_COLUMNS

    # Convert date columns
    if date_columns is None:
        date_columns = _DATE_COLUMNS

    for col in date_columns:
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            except Exception as e:
                if show_log:
                    logger.warning(f"Không thể convert {col} sang datetime: {e}")

    # Convert symbol to uppercase
    if 'symbol' in df.columns:
        df['symbol'] = df['symbol'].str.upper()

    # Convert numeric columns if they're strings
    numeric_candidates = ['price', 'change', 'changePercentage', 'volume',
                         'marketCap', 'revenue', 'netIncome', 'eps']

    for col in numeric_candidates:
        if col in df.columns and df[col].dtype == 'object':
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            except Exception:
                pass

    return df
