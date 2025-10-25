"""
Data validation models for vnstock library.

This module provides Pydantic BaseModel classes for data validation
across all data sources (VCI, TCBS, MSN, etc.).

Consolidated from:
- vnstock/explorer/vci/models.py
- vnstock/explorer/tcbs/models.py
- vnstock/explorer/msn/models.py
"""

from pydantic import BaseModel
from typing import Optional

# ============================================================================
# CORE MODELS - Used across multiple data sources
# ============================================================================


class TickerModel(BaseModel):
    """
    Validates ticker symbol and date range parameters.
    
    Used by:
    - VCI quote data fetching
    - TCBS quote data fetching
    - MSN quote data fetching
    """
    symbol: str
    start: str
    end: Optional[str] = None
    interval: Optional[str] = "1D"


# ============================================================================
# TCBS-SPECIFIC MODELS
# ============================================================================


class PaginationModel(BaseModel):
    """
    Pagination parameters for TCBS API requests.
    
    Attributes:
        page: Starting page number for pagination
        size: Number of results per page
        period: Number of reporting periods to fetch
    """
    page: int
    size: int
    period: int


class FinancialReportModel(BaseModel):
    """
    Financial report request parameters for TCBS.
    
    Attributes:
        type: Type of financial report
        frequency: Reporting frequency (quarter, year, etc.)
    """
    type: str
    frequency: str


# ============================================================================
# CONSTANTS
# ============================================================================

# Pandas data type mapping for historical price data
# Used by TCBS and other sources for consistent data type conversion
HISTORY_PRICE_DTYPE = {
    "time": "datetime64[ns]",
    "open": "float64",
    "high": "float64",
    "low": "float64",
    "close": "float64",
    "volume": "int64",
}
