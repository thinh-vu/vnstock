"""
vnstock/core/constants.py

Constants used throughout the vnstock package.

NOTE: This module provides backward compatibility.
New code should use types.py (DataSource, TimeFrame enums).
"""

# Import from types.py for unified definitions
from vnstock.core.types import (
    DataSource as _DataSource,
    TimeFrame as _TimeFrame,
)


class DataSources:
    """
    DEPRECATED: Use vnstock.core.types.DataSource enum instead.
    
    Data sources supported by vnstock.
    """
    VCI = _DataSource.VCI.value
    TCBS = _DataSource.TCBS.value
    MSN = _DataSource.MSN.value
    DNSE = _DataSource.DNSE.value
    BINANCE = _DataSource.BINANCE.value
    FMP = _DataSource.FMP.value
    XNO = _DataSource.XNO.value
    
    ALL_SOURCES = _DataSource.all_sources()


class TimeResolutions:
    """
    DEPRECATED: Use vnstock.core.types.TimeFrame enum instead.
    
    Time resolutions for historical data.
    """
    MINUTE_1 = _TimeFrame.MINUTE_1.value
    MINUTE_5 = _TimeFrame.MINUTE_5.value
    MINUTE_15 = _TimeFrame.MINUTE_15.value
    MINUTE_30 = _TimeFrame.MINUTE_30.value
    HOUR_1 = _TimeFrame.HOUR_1.value
    DAILY = _TimeFrame.DAILY.value
    WEEKLY = _TimeFrame.WEEKLY.value
    MONTHLY = _TimeFrame.MONTHLY.value


class ParameterNames:
    """Standardized parameter names."""
    SYMBOL = "symbol"
    START = "start"
    END = "end"
    INTERVAL = "interval"
    PAGE = "page"
    PAGE_SIZE = "page_size"


class MethodNames:
    """Method names for dynamic method detection."""
    HISTORY = "history"
    INTRADAY = "intraday"
    PRICE_DEPTH = "price_depth"
