"""
Configuration and utility functions for XNO connector.
Following vnstock coding standards and VCI patterns.
"""

import os
import time
import json
import requests
import pandas as pd
from typing import Optional, Dict, Any, List, Union
from vnstock.core.utils.logger import get_logger
from .const import (
    _XNO_API_BASE,
    _XNO_LAMBDA_BASE,
    _DEFAULT_TIMEOUT,
    _REQUEST_DELAY,
    _DATE_COLUMNS
)

logger = get_logger(__name__)


class XNOConfig:
    """
    Configuration class for XNO API.
    Following VCI patterns for consistency.
    """

    def __init__(self, api_key: Optional[str] = None,
                 show_log: Optional[bool] = True):
        """
        Khởi tạo cấu hình XNO.

        Tham số:
            api_key (Optional[str]): XNO API key
            show_log (Optional[bool]): Hiển thị log
        """
        # Assign show_log first (needed by _get_api_key)
        self.show_log = show_log
        
        self.api_key = api_key or self._get_api_key()
        self.api_base = _XNO_API_BASE
        self.lambda_base = _XNO_LAMBDA_BASE
        self.timeout = _DEFAULT_TIMEOUT

        if not show_log:
            logger.setLevel('CRITICAL')

    def _get_api_key(self) -> str:
        """Lấy API key từ biến môi trường."""
        api_key = os.getenv('XNO_API_KEY')
        if not api_key:
            api_key = os.getenv('XNO_TOKEN')

        if api_key:
            if self.show_log:
                logger.info("Sử dụng API key từ biến môi trường")
            return api_key

        # No API key found - raise error with instructions
        error_msg = (
            "XNO API key không được set trong biến môi trường.\n"
            "Vui lòng set một trong các biến môi trường sau:\n"
            "  - export XNO_API_KEY='your_api_key_here'\n"
            "  - export XNO_TOKEN='your_api_key_here'\n"
            "\n"
            "Hoặc truyền api_key trực tiếp cho XNOQuote:\n"
            "  quote = XNOQuote(symbol='ACB', api_key='your_key')\n"
            "\n"
            "Liên hệ vnstock để nhận API key"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    def get_endpoint_url(self, endpoint_name: str,
                         use_lambda: bool = False) -> str:
        """
        Xây dựng URL endpoint hoàn chỉnh.

        Tham số:
            endpoint_name (str): Tên endpoint
            use_lambda (bool): Sử dụng Lambda base URL

        Returns:
            str: URL API hoàn chỉnh
        """
        base = self.lambda_base if use_lambda else self.api_base
        return f"{base}{endpoint_name}"

    def get_headers(self) -> Dict[str, str]:
        """
        Lấy headers cho request.

        Returns:
            Dict[str, str]: Headers dictionary
        """
        return {
            "Authorization": self.api_key,
            "accept": "application/json"
        }


def make_xno_request(url: str,
                     headers: Dict[str, str],
                     timeout: int = _DEFAULT_TIMEOUT,
                     show_log: bool = True,
                     method: str = 'GET',
                     data: Optional[Dict] = None) -> Optional[pd.DataFrame]:
    """
    Thực hiện HTTP request tới XNO API và trả về DataFrame.
    Following VCI patterns for error handling and logging.

    Tham số:
        url (str): URL API hoàn chỉnh
        headers (Dict[str, str]): Request headers
        timeout (int): Thời gian timeout (giây)
        show_log (bool): Hiển thị log
        method (str): HTTP method ('GET' hoặc 'POST')
        data (Optional[Dict]): Data cho POST request

    Returns:
        Optional[pd.DataFrame]: Dữ liệu trả về dạng DataFrame hoặc None
    """
    if show_log:
        logger.info(f"Gửi {method} request tới: {url[:80]}...")

    try:
        if method.upper() == 'POST':
            response = requests.post(url, headers=headers,
                                   json=data, timeout=timeout)
        else:
            response = requests.get(url, headers=headers, timeout=timeout)

        if response.status_code == 200:
            # Try to parse response
            parsed_data = parse_xno_response(response.text, show_log)

            if parsed_data is not None:
                if isinstance(parsed_data, pd.DataFrame):
                    return parsed_data
                elif isinstance(parsed_data, list):
                    if len(parsed_data) == 0:
                        if show_log:
                            logger.warning("API trả về dữ liệu rỗng")
                        return pd.DataFrame()
                    return pd.DataFrame(parsed_data)
                elif isinstance(parsed_data, dict):
                    # Check if it's OHLCV dict format {t, o, h, l, c, v}
                    if all(k in parsed_data for k in ['t', 'o', 'h', 'l', 'c']):
                        # Create DataFrame from arrays
                        n = len(parsed_data['t'])
                        df = pd.DataFrame({
                            't': parsed_data['t'],
                            'o': parsed_data['o'],
                            'h': parsed_data['h'],
                            'l': parsed_data['l'],
                            'c': parsed_data['c'],
                            'v': parsed_data.get('v', [None] * n)
                        })
                        return df
                    else:
                        return pd.json_normalize(parsed_data)
            else:
                if show_log:
                    logger.warning("Không thể parse response")
                return None

        elif response.status_code == 401:
            error_msg = "API key không hợp lệ hoặc hết hạn"
            if show_log:
                logger.error(error_msg)
            return None

        elif response.status_code == 429:
            error_msg = "Vượt quá giới hạn request. Thử lại sau."
            if show_log:
                logger.error(error_msg)
            return None

        else:
            error_msg = f"Lỗi API {response.status_code}: {response.text[:200]}"
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


def _scan_all_json_blocks(text: str) -> List[Any]:
    """
    Quét tất cả khối JSON (object/array) nối tiếp trong text.
    Xử lý lỗi 'Extra data' khi có nhiều JSON blocks.

    Tham số:
        text (str): Response text

    Returns:
        List[Any]: Danh sách các JSON blocks đã parse
    """
    s = text.lstrip()
    i, n = 0, len(s)
    blocks: List[Any] = []

    while i < n:
        # Skip to next JSON opening
        while i < n and s[i] not in "{[":
            i += 1
        if i >= n:
            break

        opening = s[i]
        closing = "}" if opening == "{" else "]"
        depth = 0
        in_str = False
        esc = False
        j = i

        # Find matching closing bracket
        while j < n:
            ch = s[j]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
            else:
                if ch == '"':
                    in_str = True
                elif ch == opening:
                    depth += 1
                elif ch == closing:
                    depth -= 1
                    if depth == 0:
                        j += 1
                        break
            j += 1

        if depth != 0:
            break

        # Try to parse this block
        block = s[i:j]
        try:
            obj = json.loads(block)
            blocks.append(obj)
        except Exception:
            pass
        i = j

    return blocks


def _merge_ohlcv_dict_blocks(blocks: List[dict]) -> dict:
    """
    Gộp nhiều dict OHLCV {t,o,h,l,c,(v)} thành một dict.

    Tham số:
        blocks (List[dict]): Danh sách dict blocks

    Returns:
        dict: Dict đã merge
    """
    keys = set().union(*[set(b.keys()) for b in blocks])
    merged: Dict[str, List[Any]] = {}

    for k in keys:
        buf: List[Any] = []
        for b in blocks:
            v = b.get(k, None)
            if isinstance(v, list):
                buf.extend(v)
            else:
                if k == "v":
                    # Fill with None if v missing
                    buf.extend([None] * len(b.get("t", [])))
        if buf:
            merged[k] = buf

    return merged


def parse_xno_response(text: str,
                       show_log: bool = True) -> Optional[Union[Dict, List, pd.DataFrame]]:
    """
    Parse XNO API response với relaxed JSON parsing.
    Xử lý: standard JSON, multiple JSON blocks, NDJSON, CSV.

    Tham số:
        text (str): Response text
        show_log (bool): Hiển thị log

    Returns:
        Optional[Union[Dict, List, pd.DataFrame]]: Parsed data
    """
    if not text or len(text) == 0:
        return None

    # Try standard JSON first
    try:
        data = json.loads(text)
        return data
    except json.JSONDecodeError as e:
        if show_log:
            logger.debug(f"Standard JSON failed: {e}")

    # Try scanning multiple JSON blocks (XNO API returns this format)
    blocks = _scan_all_json_blocks(text)
    if blocks:
        # Check if all blocks are OHLCV dicts
        if all(isinstance(b, dict) and
               {"t", "o", "h", "l", "c"}.issubset(b.keys())
               for b in blocks):
            # Merge OHLCV blocks
            merged = _merge_ohlcv_dict_blocks(blocks)
            return merged
        elif len(blocks) == 1:
            return blocks[0]
        else:
            return blocks

    # Try NDJSON (newline-delimited JSON)
    items = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    if items:
        if isinstance(items[0], list):
            # Flatten nested lists
            flat = []
            for item in items:
                if isinstance(item, list):
                    flat.extend(item)
            return flat
        return items

    # Try CSV fallback
    try:
        import io
        df = pd.read_csv(io.StringIO(text))
        return df
    except Exception:
        pass

    if show_log:
        logger.warning("Không thể parse response data")
    return None


def normalize_xno_dataframe(df: pd.DataFrame,
                           date_columns: List[str] = None,
                           show_log: bool = True) -> pd.DataFrame:
    """
    Chuẩn hóa DataFrame từ XNO: convert date columns, rename columns.

    Tham số:
        df (pd.DataFrame): DataFrame cần chuẩn hóa
        date_columns (List[str]): Danh sách cột date cần convert
        show_log (bool): Hiển thị log

    Returns:
        pd.DataFrame: DataFrame đã chuẩn hóa
    """
    if df is None or df.empty:
        return df

    # Convert date columns
    if date_columns is None:
        date_columns = _DATE_COLUMNS

    for col in date_columns:
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            except Exception as e:
                if show_log:
                    logger.warning(
                        f"Không thể convert {col} sang datetime: {e}"
                    )

    # Convert symbol/ticker to uppercase if exists
    for col in ['symbol', 'ticker', 'Symbol', 'Ticker']:
        if col in df.columns:
            try:
                df[col] = df[col].str.upper()
            except Exception:
                pass

    return df


def rate_limit_delay():
    """Delay để tránh rate limit."""
    time.sleep(_REQUEST_DELAY)
