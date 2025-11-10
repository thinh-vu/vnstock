"""
Type definitions for vnstock library.

This module provides:
- Enums for data categories, provider types, market types
- Protocols for provider interfaces
- TypedDict for structured return types
"""

from enum import Enum
from typing import (
    Protocol,
    TypedDict,
    Optional,
    List,
    Dict,
    Any,
    runtime_checkable,
)
from datetime import datetime
import pandas as pd


# ============================================================================
# ENUMS
# ============================================================================

class DataCategory(str, Enum):
    """Categories of data that can be fetched from providers."""
    QUOTE = "quote"
    COMPANY = "company"
    FINANCIAL = "financial"
    TRADING = "trading"
    LISTING = "listing"
    SCREENER = "screener"


class ProviderType(str, Enum):
    """Type of data provider."""
    SCRAPING = "scraping"  # Web scraping sources (VCI, TCBS, MSN)
    API = "api"            # REST API partners (FMP, XNO, Binance, DNSE)


class MarketType(str, Enum):
    """Market types supported by the library."""
    STOCK = "stock"
    INDEX = "index"
    DERIVATIVE = "derivative"
    BOND = "bond"
    FUND = "fund"
    COMMODITY = "commodity"
    CRYPTO = "crypto"
    FOREX = "forex"


class ExchangeType(str, Enum):
    """Stock exchange types."""
    HOSE = "HOSE"  # Ho Chi Minh Stock Exchange
    HNX = "HNX"    # Hanoi Stock Exchange
    UPCOM = "UPCOM"  # Unlisted Public Company Market
    ALL = "ALL"    # All exchanges


class TimeFrame(str, Enum):
    """
    Time frames for historical data.
    
    Unified from legacy TimeResolutions in constants.py.
    Standard format: '1m', '5m', '1H', '1D', '1W', '1M'
    """
    # Minute intervals
    MINUTE_1 = "1m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    MINUTE_30 = "30m"
    # Hour intervals
    HOUR_1 = "1H"
    HOUR_4 = "4h"
    # Day/Week/Month intervals (standardized format)
    DAY_1 = "1D"
    DAILY = "1D"  # Alias for DAY_1
    WEEK_1 = "1W"
    WEEKLY = "1W"  # Alias for WEEK_1
    MONTH_1 = "1M"
    MONTHLY = "1M"  # Alias for MONTH_1


class DataSource(str, Enum):
    """
    Data sources supported by vnstock.
    
    Unified from legacy DataSources in constants.py.
    Maps to provider names in registry system.
    """
    VCI = "vci"
    TCBS = "tcbs"
    MSN = "msn"
    DNSE = "dnse"
    BINANCE = "binance"
    FMP = "fmp"
    XNO = "xno"
    FMARKET = "fmarket"  # Fund market
    
    @classmethod
    def all_sources(cls) -> list:
        """Get list of all available data sources."""
        return [s.value for s in cls]


# ============================================================================
# TYPED DICTS - Return Types
# ============================================================================

class ProviderInfo(TypedDict):
    """Information about a registered provider."""
    name: str
    category: DataCategory
    type: ProviderType
    class_path: str
    supported_methods: List[str]


class QuoteData(TypedDict, total=False):
    """Quote data structure."""
    symbol: str
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    value: Optional[float]


class CompanyProfile(TypedDict, total=False):
    """Company profile data structure."""
    symbol: str
    company_name: str
    exchange: str
    industry: str
    sector: str
    website: Optional[str]
    employees: Optional[int]
    description: Optional[str]


class FinancialData(TypedDict, total=False):
    """Financial statement data structure."""
    symbol: str
    period: str
    year: int
    quarter: Optional[int]
    revenue: Optional[float]
    profit: Optional[float]
    eps: Optional[float]
    roe: Optional[float]


# ============================================================================
# PROTOCOLS - Provider Interfaces
# ============================================================================

@runtime_checkable
class QuoteProvider(Protocol):
    """Protocol for quote data providers."""
    
    def history(
        self,
        symbol: str,
        start: str,
        end: str,
        interval: str = "1D",
        **kwargs
    ) -> pd.DataFrame:
        """
        Fetch historical price data.
        
        Args:
            symbol: Stock symbol
            start: Start date (YYYY-MM-DD)
            end: End date (YYYY-MM-DD)
            interval: Time interval (1D, 1W, 1M, etc.)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            DataFrame with columns: time, open, high, low, close, volume
        """
        ...
    
    def intraday(
        self,
        symbol: str,
        page_size: int = 100,
        **kwargs
    ) -> pd.DataFrame:
        """
        Fetch intraday trading data.
        
        Args:
            symbol: Stock symbol
            page_size: Number of records to fetch
            **kwargs: Additional provider-specific parameters
            
        Returns:
            DataFrame with intraday trading data
        """
        ...


@runtime_checkable
class CompanyProvider(Protocol):
    """Protocol for company data providers."""
    
    def profile(self, symbol: str, **kwargs) -> Dict[str, Any]:
        """
        Fetch company profile information.
        
        Args:
            symbol: Stock symbol
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dictionary with company profile data
        """
        ...
    
    def officers(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        Fetch company officers/executives information.
        
        Args:
            symbol: Stock symbol
            **kwargs: Additional provider-specific parameters
            
        Returns:
            DataFrame with officers data
        """
        ...
    
    def shareholders(
        self,
        symbol: str,
        page_size: int = 100,
        **kwargs
    ) -> pd.DataFrame:
        """
        Fetch major shareholders information.
        
        Args:
            symbol: Stock symbol
            page_size: Number of records to fetch
            **kwargs: Additional provider-specific parameters
            
        Returns:
            DataFrame with shareholders data
        """
        ...


@runtime_checkable
class FinancialProvider(Protocol):
    """Protocol for financial data providers."""
    
    def balance_sheet(
        self,
        symbol: str,
        period: str = "quarter",
        **kwargs
    ) -> pd.DataFrame:
        """
        Fetch balance sheet data.
        
        Args:
            symbol: Stock symbol
            period: 'quarter' or 'year'
            **kwargs: Additional provider-specific parameters
            
        Returns:
            DataFrame with balance sheet data
        """
        ...
    
    def income_statement(
        self,
        symbol: str,
        period: str = "quarter",
        **kwargs
    ) -> pd.DataFrame:
        """
        Fetch income statement data.
        
        Args:
            symbol: Stock symbol
            period: 'quarter' or 'year'
            **kwargs: Additional provider-specific parameters
            
        Returns:
            DataFrame with income statement data
        """
        ...
    
    def cash_flow(
        self,
        symbol: str,
        period: str = "quarter",
        **kwargs
    ) -> pd.DataFrame:
        """
        Fetch cash flow statement data.
        
        Args:
            symbol: Stock symbol
            period: 'quarter' or 'year'
            **kwargs: Additional provider-specific parameters
            
        Returns:
            DataFrame with cash flow data
        """
        ...
    
    def ratios(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        Fetch financial ratios.
        
        Args:
            symbol: Stock symbol
            **kwargs: Additional provider-specific parameters
            
        Returns:
            DataFrame with financial ratios
        """
        ...


@runtime_checkable
class TradingProvider(Protocol):
    """Protocol for trading data providers."""
    
    def price_board(
        self,
        symbols: Optional[List[str]] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Fetch real-time price board data.
        
        Args:
            symbols: List of symbols (None = all)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            DataFrame with price board data
        """
        ...
    
    def price_depth(self, symbol: str, **kwargs) -> Dict[str, Any]:
        """
        Fetch order book / price depth data.
        
        Args:
            symbol: Stock symbol
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dictionary with bid/ask levels
        """
        ...


@runtime_checkable
class ListingProvider(Protocol):
    """Protocol for listing data providers."""
    
    def all_symbols(self, **kwargs) -> List[str]:
        """
        Get list of all available symbols.
        
        Args:
            **kwargs: Additional provider-specific parameters
            
        Returns:
            List of symbol strings
        """
        ...
    
    def symbols_by_exchange(self, exchange: str, **kwargs) -> List[str]:
        """
        Get symbols filtered by exchange.
        
        Args:
            exchange: Exchange code (HOSE, HNX, UPCOM)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            List of symbol strings
        """
        ...
    
    def symbols_by_industries(self, **kwargs) -> pd.DataFrame:
        """
        Get symbols grouped by industries.
        
        Args:
            **kwargs: Additional provider-specific parameters
            
        Returns:
            DataFrame with symbol and industry mapping
        """
        ...


@runtime_checkable
class ScreenerProvider(Protocol):
    """Protocol for stock screener providers."""
    
    def screen(
        self,
        criteria: Dict[str, Any],
        **kwargs
    ) -> pd.DataFrame:
        """
        Screen stocks based on criteria.
        
        Args:
            criteria: Dictionary of screening criteria
            **kwargs: Additional provider-specific parameters
            
        Returns:
            DataFrame with filtered stocks
        """
        ...


# ============================================================================
# STANDARD CONSTANTS
# ============================================================================

class FileTypes:
    """
    MIME type mappings for file uploads.
    
    Supports common file formats for messaging and file sharing.
    """
    MIME_TYPES = {
        # Image formats
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'bmp': 'image/bmp',
        'webp': 'image/webp',
        'ico': 'image/x-icon',
        'svg': 'image/svg+xml',
        # Document formats
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.'
                'wordprocessingml.document',
        'txt': 'text/plain',
        'rtf': 'application/rtf',
        # Spreadsheet formats
        'xls': 'application/vnd.ms-excel',
        'xlsx': 'application/vnd.openxmlformats-officedocument.'
                'spreadsheetml.sheet',
        'csv': 'text/csv',
        'tsv': 'text/tab-separated-values',
        # Presentation formats
        'ppt': 'application/vnd.ms-powerpoint',
        'pptx': 'application/vnd.openxmlformats-officedocument.'
                'presentationml.presentation',
        # Data formats
        'json': 'application/json',
        'xml': 'application/xml',
        'yaml': 'application/yaml',
        # Archive formats
        'zip': 'application/zip',
        'rar': 'application/x-rar-compressed',
        '7z': 'application/x-7z-compressed',
        'tar': 'application/x-tar',
        'gz': 'application/gzip',
        # Audio formats
        'mp3': 'audio/mpeg',
        'wav': 'audio/wav',
        'flac': 'audio/flac',
        'aac': 'audio/aac',
        # Video formats
        'mp4': 'video/mp4',
        'avi': 'video/x-msvideo',
        'mov': 'video/quicktime',
        'mkv': 'video/x-matroska',
        'webm': 'video/webm',
    }
    
    @staticmethod
    def get_mime_type(file_extension: str) -> str:
        """
        Get MIME type for a file extension.
        
        Args:
            file_extension: File extension (with or without dot)
            
        Returns:
            MIME type string, defaults to 'application/octet-stream'
        """
        ext = file_extension.lstrip('.').lower()
        return FileTypes.MIME_TYPES.get(ext, 'application/octet-stream')


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


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_protocol_for_category(category: DataCategory) -> Protocol:
    """
    Get the Protocol class for a given data category.
    
    Args:
        category: Data category enum
        
    Returns:
        Protocol class for the category
        
    Raises:
        ValueError: If category is not supported
    """
    protocol_map = {
        DataCategory.QUOTE: QuoteProvider,
        DataCategory.COMPANY: CompanyProvider,
        DataCategory.FINANCIAL: FinancialProvider,
        DataCategory.TRADING: TradingProvider,
        DataCategory.LISTING: ListingProvider,
        DataCategory.SCREENER: ScreenerProvider,
    }
    
    protocol = protocol_map.get(category)
    if protocol is None:
        raise ValueError(f"No protocol defined for category: {category}")
    
    return protocol


def validate_provider_interface(provider: Any, category: DataCategory) -> bool:
    """
    Validate if a provider implements the required protocol.
    
    Args:
        provider: Provider instance to validate
        category: Expected data category
        
    Returns:
        True if provider implements the protocol
        
    Raises:
        TypeError: If provider doesn't implement required protocol
    """
    protocol = get_protocol_for_category(category)
    
    if not isinstance(provider, protocol):
        raise TypeError(
            f"Provider {provider.__class__.__name__} does not implement "
            f"{protocol.__name__} protocol for category {category}"
        )
    
    return True
