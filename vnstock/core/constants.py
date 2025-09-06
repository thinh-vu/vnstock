"""
vnstock/core/constants.py

Constants used throughout the vnstock package.
Các hằng số được sử dụng trong gói vnstock.
"""

class DataSources:
    """
    Data sources supported by vnstock.
    Các nguồn dữ liệu được hỗ trợ bởi vnstock.
    """
    VCI = "vci"
    TCBS = "tcbs"
    MSN = "msn"
    DNSE = "dnse"
    BINANCE = "binance"
    
    ALL_SOURCES = [VCI, TCBS, MSN, DNSE, BINANCE]


class TimeResolutions:
    """
    Time resolutions for historical data.
    Độ phân giải thời gian cho dữ liệu lịch sử.
    """
    MINUTE_1 = "1m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    MINUTE_30 = "30m"
    HOUR_1 = "1H"
    DAILY = "D"
    WEEKLY = "1W"
    MONTHLY = "1M"


class ParameterNames:
    """
    Standardized parameter names.
    Tên tham số chuẩn hóa.
    """
    SYMBOL = "symbol"
    START = "start"
    END = "end"
    INTERVAL = "interval"
    PAGE = "page"
    PAGE_SIZE = "page_size"


class MethodNames:
    """
    Method names for dynamic method detection.
    Tên phương thức cho phát hiện phương thức động.
    """
    HISTORY = "history"
    INTRADAY = "intraday"
    PRICE_DEPTH = "price_depth"
