"""
Validation utilities for vnstock data sources.

Self-contained module with no dependencies on parser.py to avoid
circular imports.
"""

from typing import Dict, Optional, Tuple, Any
from vnstock.core.utils.parser import get_asset_type
from datetime import datetime, timedelta
import re


def validate_symbol(
    symbol: str,
    symbol_map: Optional[Dict[str, str]] = None
) -> str:
    """Validate and normalize ticker symbol."""
    if symbol is None:
        raise ValueError("Symbol không được để trống.")
    if not isinstance(symbol, str):
        raise ValueError("Symbol phải là một chuỗi.")
    if len(symbol) < 3 or len(symbol) > 10:
        raise ValueError("Symbol phải có độ dài từ 3 đến 10 ký tự.")
    
    symbol = symbol.upper()
    
    if symbol_map and symbol in symbol_map:
        return symbol_map[symbol]
    
    else:
        # Additional validation already handled by get_asset_type, so we can reuse it
        get_asset_type(symbol)  # This will raise ValueError if symbol is invalid
        
        return symbol


def validate_date_range(
    start: str,
    end: Optional[str] = None
) -> Tuple[datetime, datetime]:
    """Validate date range and return datetime objects."""
    try:
        start_time = datetime.strptime(start, "%Y-%m-%d")
        
        if end is None:
            end_time = datetime.now() + timedelta(days=1)
        else:
            end_time = datetime.strptime(end, "%Y-%m-%d")
            end_time += timedelta(days=1)
            
        if start_time > end_time:
            raise ValueError(
                "Thời gian bắt đầu không thể lớn hơn thời gian kết thúc."
            )
            
        return start_time, end_time
        
    except ValueError as e:
        if "does not match format" in str(e):
            raise ValueError(
                "Định dạng ngày không hợp lệ. "
                "Vui lòng sử dụng định dạng YYYY-MM-DD."
            )
        raise


def convert_to_timestamps(
    dates: Tuple[datetime, datetime]
) -> Tuple[int, int]:
    """Convert datetime objects to Unix timestamps."""
    start_stamp = int(dates[0].timestamp())
    end_stamp = int(dates[1].timestamp())
    return start_stamp, end_stamp


def validate_interval(
    interval: str,
    interval_map: Dict[str, str]
) -> str:
    """Validate and map interval to data source specific value."""
    if interval not in interval_map:
        valid_options = ', '.join(interval_map.keys())
        raise ValueError(
            f"Giá trị interval không hợp lệ: {interval}. "
            f"Vui lòng chọn: {valid_options}"
        )
    return interval_map[interval]


def validate_pagination(
    page_size: int,
    page: int = 0,
    max_page_size: int = 100
) -> Tuple[int, int]:
    """Validate pagination parameters."""
    if page_size <= 0:
        raise ValueError("Page size must be greater than 0.")
    if page < 0:
        raise ValueError("Page number must be non-negative.")
    
    total_pages = (page_size // max_page_size)
    if page_size % max_page_size != 0:
        total_pages += 1
    
    return min(page_size, max_page_size), total_pages


def validate_model_input(
    model_data: Dict[str, Any],
    required_fields: list
) -> None:
    """Validate data model inputs against required fields."""
    missing_fields = [
        field for field in required_fields
        if field not in model_data
    ]
    
    if missing_fields:
        raise ValueError(
            f"Thiếu các trường bắt buộc: {', '.join(missing_fields)}"
        )
