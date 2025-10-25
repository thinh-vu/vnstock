"""
Data access layer providing unified interface to multiple data sources.

This module implements the facade pattern to access quote, company, finance,
trading, listing, and screener data from various sources (VCI, TCBS, MSN, FMP).
"""

import logging
import importlib
from typing import Optional, Any, Dict
from functools import lru_cache
from tenacity import retry, stop_after_attempt, wait_exponential

from vnstock.core.utils.logger import get_logger
from vnstock.explorer.msn.const import (
    _CURRENCY_ID_MAP,
    _GLOBAL_INDICES,
    _CRYPTO_ID_MAP,
)
from vnstock.core.utils.parser import get_asset_type

logger = get_logger(__name__)


class Config:
    """Global configuration for data layer."""
    DEFAULT_SOURCE = "VCI"
    DEFAULT_TIMEOUT = 30  # seconds
    DEFAULT_RETRIES = 3
    CACHE_SIZE = 128
    LOG_LEVEL = logging.INFO

    @classmethod
    def setup(cls, **kwargs):
        """Update configuration settings."""
        for key, value in kwargs.items():
            if hasattr(cls, key):
                setattr(cls, key, value)
                logger.info(f"Config updated: {key}={value}")


class BaseComponent:
    """Base class for all data access components."""

    SUPPORTED_SOURCES = []

    def __init__(self, symbol: Optional[str] = None,
                 source: str = Config.DEFAULT_SOURCE):
        """
        Initialize base component.

        Args:
            symbol: Stock/asset symbol
            source: Data source (VCI, TCBS, MSN, FMP, etc.)

        Raises:
            ValueError: If source not in SUPPORTED_SOURCES
        """
        self.symbol = symbol.upper() if symbol else None
        self.source = source.upper()
        self._validate_source()
        self.source_module = f"vnstock.explorer.{self.source.lower()}"
        self.data_source = self._load_data_source()

    def _validate_source(self) -> None:
        """Validate that source is supported by this component."""
        if self.source not in self.SUPPORTED_SOURCES:
            sources_str = ', '.join(self.SUPPORTED_SOURCES)
            raise ValueError(
                f"Supported sources: {sources_str}. Got: {self.source}"
            )

    def _load_data_source(self):
        """Load and return the actual data source module instance."""
        raise NotImplementedError(
            "Subclasses must implement _load_data_source()"
        )


class StockComponents(BaseComponent):
    """Unified access to stock data and related information."""

    SUPPORTED_SOURCES = ["VCI", "TCBS", "MSN", "FMP"]

    def __init__(self, symbol: str, source: str = Config.DEFAULT_SOURCE,
                 show_log: bool = True):
        """
        Initialize stock components.

        Args:
            symbol: Stock symbol (e.g., 'ACB', 'VNM')
            source: Data source (VCI, TCBS, MSN, FMP)
            show_log: Whether to display log messages

        Raises:
            ValueError: If source not supported
        """
        super().__init__(symbol, source)
        self.show_log = show_log

        # FMP assumes all symbols are stocks (international)
        if self.source == 'FMP':
            self.asset_type = 'stock'
        else:
            self.asset_type = get_asset_type(self.symbol)

        if not show_log:
            logger.setLevel(logging.CRITICAL)

        self._initialize_components()

    def _initialize_components(self):
        """Initialize quote, company, finance, trading components."""
        # Initialize company and finance for stocks
        if self.source == 'FMP' or self.asset_type == "stock":
            self.company = Company(self.symbol, source=self.source)
            self.finance = Finance(self.symbol, source=self.source)
        else:
            self.company = None
            self.finance = None
            logger.info(
                "Not a stock. Company and finance data unavailable."
            )

        # Initialize source-specific components
        if self.source in ['VCI', 'TCBS']:
            self.listing = Listing(source='VCI')
            self.screener = Screener(source='TCBS')
            self.quote = Quote(self.symbol, self.source)
            self.trading = Trading(self.symbol, source=self.source)

            if self.source == 'TCBS':
                logger.info("TCBS listing data fallback to VCI")
        elif self.source == 'MSN':
            self.quote = Quote(self.symbol, 'MSN')
            self.listing = Listing(source='MSN')
            self.trading = None
            self.screener = None
        elif self.source == 'FMP':
            self.quote = Quote(self.symbol, 'FMP')
            self.listing = Listing(source='FMP')
            self.trading = None
            self.screener = None

    def _load_data_source(self):
        """StockComponents manages multiple sources."""
        return self

    def update_symbol(self, symbol: str):
        """Switch to a different symbol."""
        self.symbol = symbol.upper()
        self._initialize_components()


class Quote(BaseComponent):
    """Historical and real-time price data."""

    SUPPORTED_SOURCES = ["VCI", "TCBS", "MSN", "FMP"]

    def __init__(self, symbol: str, source: str = Config.DEFAULT_SOURCE):
        super().__init__(symbol, source)

    def _load_data_source(self):
        """Load quote data source module."""
        module = importlib.import_module(self.source_module)
        if self.source == "MSN":
            return module.Quote(self.symbol.lower())
        else:
            return module.Quote(self.symbol)

    def _update_data_source(self, symbol: Optional[str] = None):
        """Update symbol and reload data source if needed."""
        if symbol:
            self.symbol = symbol.upper()
            self.data_source = self._load_data_source()

    @retry(
        stop=stop_after_attempt(Config.DEFAULT_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def history(self, symbol: Optional[str] = None, **kwargs):
        """Fetch historical price data."""
        if self.source == "MSN":
            symbol_map = {
                **_CURRENCY_ID_MAP,
                **_GLOBAL_INDICES,
                **_CRYPTO_ID_MAP
            }
            if symbol and symbol in symbol_map:
                self.symbol = symbol_map[symbol]
                logger.debug(f"MSN symbol mapping: {symbol} -> {self.symbol}")
        self._update_data_source(symbol)
        return self.data_source.history(**kwargs)

    @retry(
        stop=stop_after_attempt(Config.DEFAULT_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def intraday(self, symbol: Optional[str] = None, **kwargs):
        """Fetch intraday trading data."""
        self._update_data_source(symbol)
        return self.data_source.intraday(**kwargs)

    @retry(
        stop=stop_after_attempt(Config.DEFAULT_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def price_depth(self, symbol: Optional[str] = None, **kwargs):
        """Fetch order book depth data."""
        self._update_data_source(symbol)
        return self.data_source.price_depth(**kwargs)


class Listing(BaseComponent):
    """Symbol listing and grouping data."""

    SUPPORTED_SOURCES = ["VCI", "MSN", "FMP"]

    def __init__(self, source: str = Config.DEFAULT_SOURCE):
        # Don't need symbol for listing data
        super().__init__(symbol=None, source=source)

    def _load_data_source(self):
        """Load listing data source module."""
        module = importlib.import_module(self.source_module)
        return module.Listing()

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def all_symbols(self, **kwargs):
        """Get all available symbols."""
        return self.data_source.all_symbols(**kwargs)

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def symbols_by_industries(self, **kwargs):
        """Get symbols grouped by industry."""
        return self.data_source.symbols_by_industries(**kwargs)

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def symbols_by_exchange(self, **kwargs):
        """Get symbols for specific exchange."""
        return self.data_source.symbols_by_exchange(**kwargs)

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def symbols_by_group(self, group='VN30', **kwargs):
        """Get symbols for market group (VN30, HNX, etc.)."""
        return self.data_source.symbols_by_group(group, **kwargs)

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def industries_icb(self, **kwargs):
        """Get ICB industry classification."""
        return self.data_source.industries_icb(**kwargs)

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def all_future_indices(self, **kwargs):
        """Get all available futures indices."""
        return self.data_source.all_future_indices(**kwargs)

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def all_covered_warrant(self, **kwargs):
        """Get all covered warrants."""
        return self.data_source.all_covered_warrant(**kwargs)

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def all_bonds(self, **kwargs):
        """Get all bonds."""
        return self.data_source.all_bonds(**kwargs)

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def all_government_bonds(self, **kwargs):
        """Get all government bonds."""
        return self.data_source.all_government_bonds(**kwargs)


class Trading(BaseComponent):
    """Real-time trading data and market board information."""

    SUPPORTED_SOURCES = ["VCI", "TCBS"]

    def __init__(self, symbol: Optional[str] = 'VN30F1M',
                 source: str = Config.DEFAULT_SOURCE):
        super().__init__(symbol, source)

    def _load_data_source(self):
        """Load trading data source module."""
        module = importlib.import_module(self.source_module)
        return module.Trading(self.symbol)

    def _update_data_source(self, symbol: Optional[str] = None):
        """Update symbol and reload data source if needed."""
        if symbol:
            self.symbol = symbol.upper()
        self.data_source = self._load_data_source()

    @retry(
        stop=stop_after_attempt(Config.DEFAULT_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def price_board(self, symbols_list: list, **kwargs):
        """Fetch price board for multiple symbols."""
        return self.data_source.price_board(symbols_list, **kwargs)


class Company(BaseComponent):
    """Company profile, management, ownership information."""

    SUPPORTED_SOURCES = ["TCBS", "VCI", "FMP"]

    def __init__(self, symbol: Optional[str] = 'ACB',
                 source: str = "TCBS"):
        super().__init__(symbol, source)

    def _load_data_source(self):
        """Load company data source module."""
        module = importlib.import_module(self.source_module)
        return module.Company(self.symbol)

    def _update_data_source(self, symbol: Optional[str] = None):
        """Update symbol and reload data source if needed."""
        if symbol:
            self.symbol = symbol.upper()
            self.data_source = self._load_data_source()

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def overview(self, **kwargs):
        """Get company overview."""
        return self.data_source.overview(**kwargs)

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def profile(self, **kwargs):
        """Get detailed company profile."""
        return self.data_source.profile(**kwargs)

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def shareholders(self, **kwargs):
        """Get major shareholders."""
        return self.data_source.shareholders(**kwargs)

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def insider_deals(self, **kwargs):
        """Get insider trading activity."""
        return self.data_source.insider_deals(**kwargs)

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def subsidiaries(self, **kwargs):
        """Get subsidiaries and affiliates."""
        return self.data_source.subsidiaries(**kwargs)

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def officers(self, **kwargs):
        """Get management team."""
        return self.data_source.officers(**kwargs)

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def events(self, **kwargs):
        """Get company events."""
        return self.data_source.events(**kwargs)

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def news(self, **kwargs):
        """Get company news."""
        return self.data_source.news(**kwargs)

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def dividends(self, **kwargs):
        """Get dividend payment history."""
        return self.data_source.dividends(**kwargs)

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def affiliate(self, **kwargs):
        """Get affiliated companies."""
        return self.data_source.affiliate(**kwargs)

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def trading_stats(self, **kwargs):
        """Get trading statistics."""
        return self.data_source.trading_stats(**kwargs)

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def ratio_summary(self, **kwargs):
        """Get financial ratio summary."""
        return self.data_source.ratio_summary(**kwargs)


class Finance(BaseComponent):
    """Financial statements and ratios."""

    SUPPORTED_SOURCES = ["TCBS", "VCI", "FMP"]
    SUPPORTED_PERIODS = ["quarter", "annual"]

    def __init__(
        self,
        symbol: str,
        period: str = 'quarter',
        source: str = 'TCBS',
        get_all: bool = True
    ):
        """
        Initialize finance component.

        Args:
            symbol: Stock symbol
            period: Reporting period (quarter or annual)
            source: Data source
            get_all: Whether to fetch all historical data

        Raises:
            ValueError: If period not in SUPPORTED_PERIODS
        """
        super().__init__(symbol, source)
        self.period = period.lower()
        if self.period not in self.SUPPORTED_PERIODS:
            periods_str = ', '.join(self.SUPPORTED_PERIODS)
            raise ValueError(
                f"Period must be one of {periods_str}. Got: {period}"
            )
        self.get_all = get_all

    def _load_data_source(self):
        """Load finance data source module."""
        module = importlib.import_module(self.source_module)
        return module.Finance(self.symbol)

    def _update_data_source(self, symbol: Optional[str] = None):
        """Update symbol and reload data source if needed."""
        if symbol:
            self.symbol = symbol.upper()
            try:
                self.data_source = self._load_data_source()
            except (ImportError, AttributeError) as e:
                logger.error(f"Failed to update data source: {e}")
                raise

    def _process_kwargs(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Filter and validate kwargs for the specific source."""
        allowed_kwargs = ['lang', 'dropna', 'period', 'show_log']
        processed = {k: v for k, v in kwargs.items()
                     if k in allowed_kwargs}

        # Handle TCBS-specific constraints
        if self.source == 'TCBS':
            if 'lang' in processed:
                logger.warning('TCBS only supports Vietnamese reports')
                processed.pop('lang')
            if 'dropna' in processed:
                logger.warning('dropna not supported for TCBS')
                processed.pop('dropna')

        if 'period' not in processed:
            processed['period'] = self.period

        return processed

    def _get_financial_data(self, data_type: str,
                            symbol: Optional[str] = None, **kwargs) -> Any:
        """Generic method to fetch financial data."""
        self._update_data_source(symbol)
        processed_kwargs = self._process_kwargs(kwargs)

        try:
            method = getattr(self.data_source, data_type)
            return method(**processed_kwargs)
        except AttributeError:
            logger.error(
                f"{self.source} does not support {data_type}"
            )
            raise
        except Exception as e:
            logger.error(f"Error fetching {data_type}: {e}")
            raise

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def balance_sheet(self, symbol: Optional[str] = None,
                      **kwargs) -> Any:
        """Get balance sheet."""
        return self._get_financial_data('balance_sheet', symbol, **kwargs)

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def income_statement(self, symbol: Optional[str] = None,
                         **kwargs) -> Any:
        """Get income statement."""
        return self._get_financial_data('income_statement', symbol, **kwargs)

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def cash_flow(self, symbol: Optional[str] = None,
                  **kwargs) -> Any:
        """Get cash flow statement."""
        return self._get_financial_data('cash_flow', symbol, **kwargs)

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def ratio(self, symbol: Optional[str] = None, **kwargs) -> Any:
        """Get financial ratios."""
        return self._get_financial_data('ratio', symbol, **kwargs)


class Screener(BaseComponent):
    """Stock screening and filtering."""

    SUPPORTED_SOURCES = ["TCBS"]

    def __init__(self, source: str = "TCBS"):
        # Don't need symbol for screener
        super().__init__(symbol=None, source=source)

    def _load_data_source(self):
        """Load screener data source module."""
        module = importlib.import_module(self.source_module)
        return module.Screener()

    @retry(
        stop=stop_after_attempt(Config.DEFAULT_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def stock(self, **kwargs):
        """Screen stocks with criteria."""
        allowed_kwargs = ['params', 'limit', 'lang']
        processed = {k: v for k, v in kwargs.items()
                     if k in allowed_kwargs}
        return self.data_source.stock(**processed)


class Fund(BaseComponent):
    """Fund/Mutual fund data."""

    SUPPORTED_SOURCES = ["FMARKET"]

    def __init__(self, source: str = "FMARKET", random_agent: bool = False):
        """
        Initialize fund component.

        Args:
            source: Data source (FMARKET)
            random_agent: Use random user agent for requests
        """
        self.random_agent = random_agent
        super().__init__(symbol=None, source=source)
        self.details = self.data_source.details

    def _load_data_source(self):
        """Load fund data source module."""
        module = importlib.import_module(self.source_module)
        return module.Fund(random_agent=self.random_agent)

    def listing(self, **kwargs):
        """Get list of open funds."""
        return self.data_source.listing(**kwargs)


class MSNComponents:
    """Unified component access for MSN data (forex, crypto, indices)."""

    def __init__(self, symbol: Optional[str] = 'EURUSD',
                 source: str = "MSN"):
        """
        Initialize MSN components.

        Args:
            symbol: Symbol or symbol ID
            source: Data source (must be MSN)

        Raises:
            ValueError: If source is not MSN
        """
        self.original_symbol = symbol.upper() if symbol else None
        self.source = source.upper()

        if self.source != "MSN":
            raise ValueError("MSN components only support MSN source")

        # Map symbol to MSN symbol ID if needed
        symbol_map = {
            **_CURRENCY_ID_MAP,
            **_GLOBAL_INDICES,
            **_CRYPTO_ID_MAP
        }
        if self.original_symbol in symbol_map:
            self.symbol = symbol_map[self.original_symbol]
            logger.debug(
                f"Symbol mapping: {self.original_symbol} -> {self.symbol}"
            )
        else:
            self.symbol = self.original_symbol
            logger.debug(f"No mapping for {self.original_symbol}, using as-is")

        self._initialize_components()

    def _initialize_components(self):
        """Initialize quote and listing components."""
        self.quote = Quote(self.symbol, self.source)
        self.listing = Listing(source=self.source)

    def update_symbol(self, symbol: str):
        """Switch to a different symbol."""
        self.symbol = symbol.upper()
        self._initialize_components()


class FMPComponents:
    """Unified component access for FMP international market data."""

    def __init__(self, symbol: Optional[str] = 'AAPL',
                 source: str = "FMP",
                 api_key: Optional[str] = None):
        """
        Initialize FMP components.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            source: Data source (must be FMP)
            api_key: FMP API key (optional)

        Raises:
            ValueError: If source is not FMP
        """
        self.original_symbol = symbol.upper() if symbol else None
        self.symbol = self.original_symbol
        self.source = source.upper()
        self.api_key = api_key

        if self.source != "FMP":
            raise ValueError("FMP components only support FMP source")

        self._initialize_components()

    def _initialize_components(self):
        """Initialize all FMP data access components."""
        self.quote = Quote(self.symbol, self.source)
        self.listing = Listing(source=self.source)
        self.company = Company(self.symbol, source=self.source)
        self.finance = Finance(self.symbol, source=self.source)

    def update_symbol(self, symbol: str):
        """Switch to a different symbol."""
        self.symbol = symbol.upper()
        self._initialize_components()
