import re
import requests
import pandas as pd
import numpy as np
from pytz import timezone
from datetime import datetime, timedelta
from typing import Dict, Union, Literal, Any, Optional
from vnstock.core.config.const import UA
from vnstock.core.utils.logger import get_logger

logger = get_logger(__name__)

def parse_timestamp(time_value):
    """
    Convert a datetime object or a string representation of time to a Unix timestamp.
    Parameters:
        - time_value: A datetime object or a string representation of time. Supported formats are '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', and '%Y-%m-%d' or datetime object.
    """
    try:
        if isinstance(time_value, datetime):
            time_value = timezone('Asia/Ho_Chi_Minh').localize(time_value)
        elif isinstance(time_value, str):
            if ' ' in time_value and ':' in time_value.split(' ')[1]:
                try:
                    time_value = datetime.strptime(time_value, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    time_value = datetime.strptime(time_value, '%Y-%m-%d %H:%M')
            else:
                time_value = datetime.strptime(time_value, '%Y-%m-%d')
        else:
            print("Invalid input type. Supported types are datetime or string.")
            return None

        timestamp = int(time_value.timestamp())
        return timestamp
    except ValueError:
        print("Invalid timestamp format")
        return None

# Utility to convert timestamps to Vietnam timezone
def localize_timestamp (
    timestamp: Union[pd.Series, int, float, list, np.ndarray, pd.Timestamp, Any], 
    unit: Literal['s', 'ms', 'us', 'ns'] = 's',
    return_scalar: bool = False,
    return_string: bool = False,
    string_format: str = '%Y-%m-%d %H:%M:%S'
) -> Union[pd.Series, pd.Timestamp, str]:
    """
    Convert timestamp values to Vietnam timezone (UTC+7).
    
    Parameters:
        timestamp: Timestamp value(s) - can be Series, list, array, or scalar
        unit: Unit for timestamp conversion ('s' for seconds, 'ms' for milliseconds, etc.)
        return_scalar: If True and input can be treated as scalar, return a single value
        return_string: If True, return string representation(s) instead of datetime objects
        string_format: Format for datetime strings if return_string=True
        
    Returns:
        - Series of datetime objects (default)
        - Series of formatted strings (if return_string=True)
        - Single Timestamp (if return_scalar=True and input is scalar-like)
        - Formatted string (if return_scalar=True, return_string=True and input is scalar-like)
        
    Examples:
        # Convert a single timestamp (returns Series by default)
        convert_to_vietnam_time(1647851234)
        
        # Convert a single timestamp (return scalar Timestamp)
        convert_to_vietnam_time(1647851234, return_scalar=True)
        
        # Convert a single timestamp (return string)
        convert_to_vietnam_time(1647851234, return_string=True)
        
        # Convert multiple timestamps to string Series
        convert_to_vietnam_time([1647851234, 1647851235], return_string=True)
    """
    # Determine if input should be treated as a scalar value
    treat_as_scalar = False
    
    # Direct scalar types
    if np.isscalar(timestamp) or isinstance(timestamp, (pd.Timestamp, datetime)):
        treat_as_scalar = True
        timestamp_series = pd.Series([timestamp])
    # Series with one element
    elif isinstance(timestamp, pd.Series) and len(timestamp) == 1:
        treat_as_scalar = True
        timestamp_series = timestamp
    # List, array, etc. with one element
    elif hasattr(timestamp, '__len__') and len(timestamp) == 1:
        treat_as_scalar = True
        timestamp_series = pd.Series(timestamp)
    # Other cases - treat as non-scalar
    else:
        timestamp_series = pd.Series(timestamp) if not isinstance(timestamp, pd.Series) else timestamp
    
    # Convert to datetime with timezone
    dt_series = pd.to_datetime(timestamp_series, unit=unit)
    vietnam_series = dt_series.dt.tz_localize('UTC').dt.tz_convert('Asia/Ho_Chi_Minh')
    
    # Apply string formatting if requested
    if return_string:
        vietnam_series = vietnam_series.dt.strftime(string_format)
    
    # Return scalar if requested and input was scalar-like
    if return_scalar and treat_as_scalar:
        return vietnam_series.iloc[0]
    
    return vietnam_series

def get_asset_type(symbol: str) -> str:
    """
    Xác định loại tài sản dựa trên mã chứng khoán được cung cấp.

    Tham số: 
        - symbol (str): Mã chứng khoán hoặc mã chỉ số.
    
    Trả về:
        - 'index' nếu mã chứng khoán là mã chỉ số.
        - 'stock' nếu mã chứng khoán là mã cổ phiếu.
        - 'derivative' nếu mã chứng khoán là mã hợp đồng tương lai hoặc quyền chọn.
        - 'bond' nếu mã chứng khoán là mã trái phiếu (chính phủ hoặc doanh nghiệp).
        - 'coveredWarr' nếu mã chứng khoán là mã chứng quyền.
    """
    symbol = symbol.upper()
    
    # Index symbols
    if symbol in [
        'VNINDEX', 'HNXINDEX', 'UPCOMINDEX', 'VN30', 'VN100', 'HNX30',
        'VNSML', 'VNMID', 'VNALL', 'VNREAL', 'VNMAT', 'VNIT', 'VNHEAL',
        'VNFINSELECT', 'VNFIN', 'VNENE', 'VNDIAMOND', 'VNCONS', 'VNCOND'
    ]:
        return 'index'
    
    # Stock symbols (assumed to have 3 characters)
    elif len(symbol) == 3:
        return 'stock'
    
    # For symbols that could be derivative or bond (length 7 or 9)
    elif len(symbol) in [7, 9]:
        # VN30 derivative patterns:
        fm_pattern = re.compile(r'^VN30F\d{1,2}M$')
        ym_pattern = re.compile(r'^VN30F\d{4}$')
        
        # Bond patterns:
        # Government bond: e.g., GB05F2506 or GB10F2024
        gov_bond_pattern = re.compile(r'^GB\d{2}F\d{4}$')
        # Company bond: e.g., BAB122032; exclude those starting with VN30F.
        comp_bond_pattern = re.compile(r'^(?!VN30F)[A-Z]{3}\d{6}$')
        
        if gov_bond_pattern.match(symbol) or comp_bond_pattern.match(symbol):
            return 'bond'
        elif fm_pattern.match(symbol) or ym_pattern.match(symbol):
            return 'derivative'
        else:
            raise ValueError('Invalid derivative or bond symbol. Symbol must be in format of VN30F1M, VN30F2024, GB10F2024, or for company bonds, e.g., BAB122032')
    
    # Covered warrant symbols (assumed to have 8 characters)
    elif len(symbol) == 8:
        return 'coveredWarr'
    
    else:
        raise ValueError('Invalid symbol. Your symbol format is not recognized!')

def camel_to_snake(name):
    """
    Chuyển đổi tên biến từ dạng CamelCase sang snake_case.

    Tham số:
        - name (str): Tên biến dạng CamelCase.

    Trả về:
        - str: Tên biến dạng snake_case.
    """
    str1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    output = re.sub('([a-z0-9])([A-Z])', r'\1_\2', str1).lower()
    # replace . with _
    output = output.replace('.', '_')
    return output

def flatten_data(json_data, parent_key='', sep='_'):
    """
    Làm phẳng dữ liệu JSON thành dạng dict tiêu chuẩn.

    Tham số:
        - json_data: Dữ liệu JSON trả về từ API.
        - parent_key: Key cha của dữ liệu JSON.
        - sep: Ký tự phân cách giữa các key.
    """
    items = []
    for k, v in json_data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_data(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def last_n_days(n):
    """
    Return a date value in YYYY-MM-DD format for last n days. If n = 0, return today's date.
    """
    date_value = (datetime.today() - timedelta(days=n)).strftime('%Y-%m-%d')
    return date_value
    
def decd(byte_data):
    from cryptography.fernet import Fernet
    import base64
    kb = UA['Chrome'].replace(' ', '').ljust(32)[:32].encode('utf-8')
    kb64 = base64.urlsafe_b64encode(kb)
    cipher = Fernet(kb64)
    return cipher.decrypt(byte_data).decode('utf-8')