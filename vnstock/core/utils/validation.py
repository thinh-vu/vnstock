"""Validation utilities for vnstock data sources."""

from typing import Dict, Optional, Tuple, Union, Any
from datetime import datetime, timedelta
import pandas as pd
from vnstock.core.utils.parser import parse_timestamp, get_asset_type
from vnstock.core.utils.logger import get_logger

logger = get_logger(__name__)

def validate_symbol(symbol: str, symbol_map: Optional[Dict[str, str]] = None) -> str:
    """
    Validate and normalize ticker symbol with optional mapping for special cases.
    
    Parameters:
        - symbol: Stock/index symbol
        - symbol_map: Optional mapping dictionary (e.g., for INDEX values)
        
    Returns:
        - Validated and normalized symbol
        
    Raises:
        - ValueError: If symbol is invalid or not found in the mapping
    """
    symbol = symbol.upper()
    
    # Apply mapping if provided (e.g., INDEX mapping)
    if symbol_map and symbol in symbol_map:
        return symbol_map[symbol]
    
    else:
        # Additional validation already handled by get_asset_type, so we can reuse it
        get_asset_type(symbol)  # This will raise ValueError if symbol is invalid
        
        return symbol

def validate_date_range(start: str, end: Optional[str] = None) -> Tuple[datetime, datetime]:
    """
    Validate date range and return normalized datetime objects.
    
    Parameters:
        - start: Start date in YYYY-MM-DD format
        - end: End date in YYYY-MM-DD format, defaults to current date
        
    Returns:
        - Tuple of (start_datetime, end_datetime)
        
    Raises:
        - ValueError: If dates are invalid or start is after end
    """
    try:
        start_time = datetime.strptime(start, "%Y-%m-%d")
        
        if end is None:
            end_time = datetime.now() + timedelta(days=1)
        else:
            end_time = datetime.strptime(end, "%Y-%m-%d") + timedelta(days=1)
            
        if start_time > end_time:
            raise ValueError("Thời gian bắt đầu không thể lớn hơn thời gian kết thúc.")
            
        return start_time, end_time
        
    except ValueError as e:
        if "does not match format" in str(e):
            raise ValueError(f"Định dạng ngày không hợp lệ. Vui lòng sử dụng định dạng YYYY-MM-DD.")
        raise

def convert_to_timestamps(dates: Tuple[datetime, datetime]) -> Tuple[int, int]:
    """
    Convert datetime objects to Unix timestamps.
    
    Parameters:
        - dates: Tuple of (start_datetime, end_datetime)
        
    Returns:
        - Tuple of (start_timestamp, end_timestamp)
    """
    # Reuse existing parse_timestamp function where appropriate
    start_stamp = int(dates[0].timestamp())
    end_stamp = int(dates[1].timestamp())
    
    return start_stamp, end_stamp

def validate_interval(interval: str, interval_map: Dict[str, str]) -> str:
    """
    Validate and map interval parameter to data source specific value.
    
    Parameters:
        - interval: Time interval (e.g., 1D, 1H)
        - interval_map: Dictionary mapping intervals to API-specific values
        
    Returns:
        - Validated interval value
        
    Raises:
        - ValueError: If interval is invalid
    """
    if interval not in interval_map:
        valid_options = ', '.join(interval_map.keys())
        raise ValueError(f"Giá trị interval không hợp lệ: {interval}. Vui lòng chọn: {valid_options}")
    
    return interval_map[interval]

def validate_pagination(page_size: int, page: int = 0, max_page_size: int = 100) -> Tuple[int, int]:
    """
    Validate pagination parameters for API requests.
    
    Parameters:
        - page_size: Number of items per page
        - page: Page number (0-based)
        - max_page_size: Maximum allowed page size
        
    Returns:
        - Tuple of (normalized_page_size, total_pages)
        
    Raises:
        - ValueError: If pagination parameters are invalid
    """
    if page_size <= 0:
        raise ValueError("Page size must be greater than 0.")
    
    if page < 0:
        raise ValueError("Page number must be non-negative.")
    
    # Calculate how many pages needed for the requested page_size
    total_pages = (page_size // max_page_size) + (1 if page_size % max_page_size != 0 else 0)
    
    return min(page_size, max_page_size), total_pages

def validate_model_input(model_data: Dict[str, Any], required_fields: list) -> None:
    """
    Validate data model inputs against required fields.
    
    Parameters:
        - model_data: Dictionary of input data 
        - required_fields: List of required field names
        
    Raises:
        - ValueError: If required fields are missing
    """
    missing_fields = [field for field in required_fields if field not in model_data]
    
    if missing_fields:
        raise ValueError(f"Thiếu các trường bắt buộc: {', '.join(missing_fields)}")
