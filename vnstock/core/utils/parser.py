import re
import requests
from typing import Dict
from pytz import timezone
from datetime import datetime, timedelta
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

def get_asset_type(symbol: str) -> str:
    """
    Xác định loại tài sản dựa trên mã chứng khoán được cung cấp.

    Tham số: 
        - symbol (str): Mã chứng khoán hoặc mã chỉ số.
    
    Trả về:
        - 'index' nếu mã chứng khoán là mã chỉ số.
        - 'stock' nếu mã chứng khoán là mã cổ phiếu.
        - 'derivative' nếu mã chứng khoán là mã hợp đồng tương lai hoặc quyền chọn.
        - 'coveredWarr' nếu mã chứng khoán là mã chứng quyền.
    """
    symbol = symbol.upper()
    if symbol in ['VNINDEX', 'HNXINDEX', 'UPCOMINDEX', 'VN30', 'VN100', 'HNX30', 'VNSML', 'VNMID', 'VNALL', 'VNREAL', 'VNMAT', 'VNIT', 'VNHEAL', 'VNFINSELECT', 'VNFIN', 'VNENE', 'VNDIAMOND', 'VNCONS', 'VNCOND']:
        return 'index'
    elif len(symbol) == 3:
        return 'stock'
    elif len(symbol) in [7, 9]:
        fm_pattern = re.compile(r'VN30F\d{1,2}M')
        ym_pattern = re.compile(r'VN30F\d{4}')
        gb_pattern = re.compile(r'[A-Z]{3}\d{5}')
        bond_pattern = re.compile(r'[A-Z]{3}\d{6}')
        if bond_pattern.match(symbol) or gb_pattern.match(symbol):
            return 'bond'
        elif fm_pattern.match(symbol) or ym_pattern.match(symbol):
            return 'derivative'
        else:
            raise ValueError('Invalid derivative symbol. Symbol must be in format of VN30F1M, VN30F2024, GB10F2024')
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

def json_cleaning(json_data: Dict, map_dict: Dict[str, str]) -> Dict:
    """
    Chuẩn hóa dữ liệu JSON trả về từ API theo định dạng tiêu chuẩn.

    Tham số:
        - json_data: Dữ liệu JSON trả về từ API.
        - map_dict: Bản đồ ánh xạ tên cột cũ sang tên cột mới. Mặc định là _OHLC_MAP.
    Trả về:
        - Dict: Dữ liệu JSON đã được chuẩn hóa.
    """
    # Filter and rename keys based on the map_dict
    cleaned_dict = {
                    map_dict[key]: value for key, value in json_data.items() if key in map_dict
                    }
    return cleaned_dict

def api_response_check(response: requests.Response) -> dict:
    """
    Handle common errors when fetching data from an API.

    Parameters:
    - response (requests.Response): The HTTP response object from the data fetch request.

    Returns:
    - dict: The JSON data from the response if successful.

    Raises:
    - ValueError: If the response contains an error or invalid JSON.
    """
    # Check for non-200 status codes
    if response.status_code != 200:
        logger.error(f"Request failed with status code {response.status_code}. Details: {response.text}")
        raise ValueError(f"Error fetching data: {response.status_code} - {response.text}")
    
    # Attempt to parse the response as JSON
    try:
        data = response.json()
    except ValueError as e:
        logger.error("Invalid JSON response received.")
        raise ValueError("Failed to parse JSON response.") from e
    
    # Check if the data is empty
    if not data:
        raise ValueError("No data found in the response. Please check the request or try again later.")
    
    return data

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

def time_in_date_string(time_string, print_errors=True):
    """
    Check if a time component is present in the input string.
    """
    try:
        date_part, time_part = time_string.split(' ')
        if ':' in time_part:
            hours, minutes, *seconds = map(int, time_part.split(':'))
            if 0 <= hours <= 23 and 0 <= minutes <= 59 and all(0 <= s <= 59 for s in seconds):
                return True
            else:
                if print_errors:
                    print("Invalid time components.")
                return False
        else:
            return False
    except ValueError:
        if print_errors:
            print("Unable to split into date and time components. Assuming it's a date only.")
        return False
    
def decd(byte_data):
    from cryptography.fernet import Fernet
    import base64
    kb = UA['Chrome'].replace(' ', '').ljust(32)[:32].encode('utf-8')
    kb64 = base64.urlsafe_b64encode(kb)
    cipher = Fernet(kb64)
    return cipher.decrypt(byte_data).decode('utf-8')