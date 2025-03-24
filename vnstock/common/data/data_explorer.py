import logging
import importlib
import pandas as pd
from typing import Optional, Any, Dict
from functools import lru_cache
from tenacity import retry, stop_after_attempt, wait_exponential

from vnstock.core.utils.logger import get_logger
from vnstock.explorer.msn.const import _CURRENCY_ID_MAP, _GLOBAL_INDICES, _CRYPTO_ID_MAP
from vnstock.core.utils.parser import get_asset_type

logger = get_logger(__name__)

class Config:
    DEFAULT_SOURCE = "VCI"
    DEFAULT_TIMEOUT = 30  # seconds
    DEFAULT_RETRIES = 3
    CACHE_SIZE = 128
    LOG_LEVEL = logging.INFO
    
    @classmethod
    def setup(cls, **kwargs):
        for key, value in kwargs.items():
            if hasattr(cls, key):
                setattr(cls, key, value)
                logger.info(f"Updated config: {key}={value}")

class BaseComponent:
    SUPPORTED_SOURCES = []
    
    def __init__(self, symbol: Optional[str] = None, source: str = Config.DEFAULT_SOURCE):
        self.symbol = symbol.upper() if symbol else None
        self.source = source.upper()
        self._validate_source()
        self.source_module = f"vnstock.explorer.{self.source.lower()}"
        self.data_source = self._load_data_source()
    
    def _validate_source(self) -> None:
        if self.source not in self.SUPPORTED_SOURCES:
            raise ValueError(f"Chỉ có nguồn dữ liệu từ {', '.join(self.SUPPORTED_SOURCES)} được hỗ trợ.")
    
    def _load_data_source(self):
        raise NotImplementedError("Phương thức này phải được triển khai bởi các lớp con")

class StockComponents(BaseComponent):
    SUPPORTED_SOURCES = ["VCI", "TCBS", "MSN"]

    def __init__(self, symbol: str, source: str = Config.DEFAULT_SOURCE, show_log: bool = True):
        super().__init__(symbol, source)
        self.show_log = show_log
        self.asset_type = get_asset_type(self.symbol)
        if not show_log:
            logger.setLevel(logging.CRITICAL)
        self._initialize_components()

    def _initialize_components(self):
        if self.asset_type == "stock":
            self.company = Company(self.symbol, source=self.source)
            self.finance = Finance(self.symbol, source=self.source)
        else:
            self.company = None
            self.finance = None
            logger.info("Không phải là mã chứng khoán, thông tin công ty và tài chính không khả dụng.")
        
        if self.source in ['VCI', 'TCBS']:
            self.listing = Listing(source='VCI')
            self.screener = Screener(source='TCBS')
            self.quote = Quote(self.symbol, self.source)
            self.trading = Trading(self.symbol, source=self.source)
        
            if self.source == 'TCBS':
                logger.info("TCBS không cung cấp thông tin danh sách. Dữ liệu tự động trả về từ VCI.")
            # elif self.source == 'VCI':
            #     logger.info("Nguồn VCI không hỗ trợ dữ liệu bộ lọc cổ phiếu. Dữ liệu tự động trả về từ TCBS.")
        elif self.source == 'MSN':
            self.quote = Quote(self.symbol, 'MSN')
            self.listing = Listing(source='MSN')

    def _load_data_source(self):
        """
        StockComponents không trực tiếp tải một nguồn dữ liệu đơn lẻ 
        mà khởi tạo nhiều thành phần khác nhau.
        
        Returns:
            self: Trả về chính đối tượng này vì nó quản lý nhiều nguồn dữ liệu.
        """
        # This class doesn't need to load a specific data source like other components
        # Instead, it initializes multiple components in _initialize_components
        return self

    def update_symbol(self, symbol: str):
        self.symbol = symbol.upper()
        self._initialize_components()

class Quote(BaseComponent):
    SUPPORTED_SOURCES = ["VCI", "TCBS", "MSN"]

    def __init__(self, symbol: str, source: str = Config.DEFAULT_SOURCE):
        super().__init__(symbol, source)

    def _load_data_source(self):
        module = importlib.import_module(self.source_module)
        return module.Quote(self.symbol.lower() if self.source == "MSN" else self.symbol)
    
    def _update_data_source(self, symbol: Optional[str] = None):
        if symbol:
            self.symbol = symbol.upper()
            self.data_source = self._load_data_source()
    
    @retry(stop=stop_after_attempt(Config.DEFAULT_RETRIES), wait=wait_exponential(multiplier=1, min=2, max=10))
    def history(self, symbol: Optional[str] = None, **kwargs):
        if self.source == "MSN":
            symbol_map = {**_CURRENCY_ID_MAP, **_GLOBAL_INDICES, **_CRYPTO_ID_MAP}
            if symbol:
                self.symbol = symbol_map[symbol]
                logger.info(f"Chuyển đổi {symbol} thành tên mã MSN: {self.symbol}")
        self._update_data_source(symbol)
        return self.data_source.history(**kwargs)
    
    @retry(stop=stop_after_attempt(Config.DEFAULT_RETRIES), wait=wait_exponential(multiplier=1, min=2, max=10))
    def intraday(self, symbol: Optional[str] = None, **kwargs):
        self._update_data_source(symbol)
        return self.data_source.intraday(**kwargs)
    
    @retry(stop=stop_after_attempt(Config.DEFAULT_RETRIES), wait=wait_exponential(multiplier=1, min=2, max=10))
    def price_depth(self, symbol: Optional[str] = None, **kwargs):
        self._update_data_source(symbol)
        return self.data_source.price_depth(**kwargs)

class Listing(BaseComponent):
    SUPPORTED_SOURCES = ["VCI", "MSN"]

    def __init__(self, source: str = Config.DEFAULT_SOURCE):
        super().__init__(source=source)

    def _load_data_source(self):
        module = importlib.import_module(self.source_module)
        return module.Listing()

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def all_symbols(self, **kwargs):
        return self.data_source.all_symbols(**kwargs)
    
    @lru_cache(maxsize=Config.CACHE_SIZE)
    def symbols_by_industries(self, **kwargs):
        return self.data_source.symbols_by_industries(**kwargs)
    
    @lru_cache(maxsize=Config.CACHE_SIZE)
    def symbols_by_exchange(self, **kwargs):
        return self.data_source.symbols_by_exchange(**kwargs)
    
    @lru_cache(maxsize=Config.CACHE_SIZE)
    def symbols_by_group(self, group='VN30', **kwargs):
        return self.data_source.symbols_by_group(group, **kwargs)

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def industries_icb(self, **kwargs):
        return self.data_source.industries_icb(**kwargs)
    
    @lru_cache(maxsize=Config.CACHE_SIZE)
    def all_future_indices(self, **kwargs):
        return self.data_source.all_future_indices(**kwargs)

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def all_covered_warrant(self, **kwargs):
        return self.data_source.all_covered_warrant(**kwargs)

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def all_bonds(self, **kwargs):
        return self.data_source.all_bonds(**kwargs)
    
    @lru_cache(maxsize=Config.CACHE_SIZE)
    def all_government_bonds(self, **kwargs):
        return self.data_source.all_government_bonds(**kwargs)

class Trading(BaseComponent):
    SUPPORTED_SOURCES = ["VCI", "TCBS"]

    def __init__(self, symbol: Optional[str] = 'VN30F1M', source: str = Config.DEFAULT_SOURCE):
        super().__init__(symbol, source)

    def _load_data_source(self):
        module = importlib.import_module(self.source_module)
        return module.Trading(self.symbol)
    
    def _update_data_source(self, symbol: Optional[str] = None):
        if symbol:
            self.symbol = symbol.upper()
        self.data_source = self._load_data_source()
    
    @retry(stop=stop_after_attempt(Config.DEFAULT_RETRIES), wait=wait_exponential(multiplier=1, min=2, max=10))
    def price_board(self, symbols_list: list, **kwargs):
        return self.data_source.price_board(symbols_list, **kwargs)

class Company(BaseComponent):
    SUPPORTED_SOURCES = ["TCBS", "VCI"]

    def __init__(self, symbol: Optional[str] = 'ACB', source: str = "TCBS"):
        super().__init__(symbol, source)

    def _load_data_source(self):
        module = importlib.import_module(self.source_module)
        return module.Company(self.symbol)
    
    def _update_data_source(self, symbol: Optional[str] = None):
        if symbol:
            self.symbol = symbol.upper()
            self.data_source = self._load_data_source()

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def overview(self, **kwargs):
        return self.data_source.overview(**kwargs)

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def profile(self, **kwargs):
        return self.data_source.profile(**kwargs)
    
    @lru_cache(maxsize=Config.CACHE_SIZE)
    def shareholders(self, **kwargs):
        return self.data_source.shareholders(**kwargs)
    
    @lru_cache(maxsize=Config.CACHE_SIZE)
    def insider_deals(self, **kwargs):
        return self.data_source.insider_deals(**kwargs)
    
    @lru_cache(maxsize=Config.CACHE_SIZE)
    def subsidiaries(self, **kwargs):
        return self.data_source.subsidiaries(**kwargs)
    
    @lru_cache(maxsize=Config.CACHE_SIZE)
    def officers(self, **kwargs):
        return self.data_source.officers(**kwargs)
    
    @lru_cache(maxsize=Config.CACHE_SIZE)
    def events(self, **kwargs):
        return self.data_source.events(**kwargs)
    
    @lru_cache(maxsize=Config.CACHE_SIZE)
    def news(self, **kwargs):
        return self.data_source.news(**kwargs)
    
    @lru_cache(maxsize=Config.CACHE_SIZE)
    def dividends(self, **kwargs):
        return self.data_source.dividends(**kwargs)

class Finance(BaseComponent):
    SUPPORTED_SOURCES = ["TCBS", "VCI"]
    SUPPORTED_PERIODS = ["quarter", "annual"]

    def __init__(
        self, 
        symbol: str, 
        period: str = 'quarter', 
        source: str = 'TCBS', 
        get_all: bool = True
    ):
        super().__init__(symbol, source)
        self.period = period.lower()
        if self.period not in self.SUPPORTED_PERIODS:
            raise ValueError(f"Period must be one of {', '.join(self.SUPPORTED_PERIODS)}")
        self.get_all = get_all

    def _load_data_source(self):
        module = importlib.import_module(self.source_module)
        return module.Finance(self.symbol)
    
    def _update_data_source(self, symbol: Optional[str] = None):
        if symbol:
            self.symbol = symbol.upper()
            try:
                self.data_source = self._load_data_source()
            except (ImportError, AttributeError) as e:
                logger.error(f"Cannot update data source: {e}")
                raise

    def _process_kwargs(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        allowed_kwargs = ['lang', 'dropna', 'period', 'show_log']
        processed_kwargs = {k: v for k, v in kwargs.items() if k in allowed_kwargs}
        
        if self.source == 'TCBS':
            if 'lang' in processed_kwargs:
                logger.info('TCBS only supports Vietnamese reports')
                processed_kwargs.pop('lang')
            if 'dropna' in processed_kwargs:
                logger.info('Tham số dropna không được hỗ trợ cho nguồn dữ liệu TCBS')
                processed_kwargs.pop('dropna')

        if 'period' not in processed_kwargs:
            processed_kwargs['period'] = self.period
            
        return processed_kwargs

    def _get_financial_data(self, data_type: str, symbol: Optional[str] = None, **kwargs) -> Any:
        self._update_data_source(symbol)
        processed_kwargs = self._process_kwargs(kwargs)
        
        try:
            method = getattr(self.data_source, data_type)
            return method(**processed_kwargs)
        except AttributeError:
            logger.error(f"Nguồn dữ liệu {self.source} không hỗ trợ dữ liệu {data_type}")
            raise
        except Exception as e:
            logger.error(f"Lỗi khi truy xuất dữ liệu {data_type}: {e}")
            raise

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def balance_sheet(self, symbol: Optional[str] = None, **kwargs) -> Any:
        return self._get_financial_data('balance_sheet', symbol, **kwargs)
    
    @lru_cache(maxsize=Config.CACHE_SIZE)
    def income_statement(self, symbol: Optional[str] = None, **kwargs) -> Any:
        return self._get_financial_data('income_statement', symbol, **kwargs)
    
    @lru_cache(maxsize=Config.CACHE_SIZE)
    def cash_flow(self, symbol: Optional[str] = None, **kwargs) -> Any:
        return self._get_financial_data('cash_flow', symbol, **kwargs)
    
    @lru_cache(maxsize=Config.CACHE_SIZE)
    def ratio(self, symbol: Optional[str] = None, **kwargs) -> Any:
        return self._get_financial_data('ratio', symbol, **kwargs)

class Screener(BaseComponent): 
    SUPPORTED_SOURCES = ["TCBS"]

    def __init__(self, source: str = "TCBS"):
        super().__init__(source=source)

    def _load_data_source(self):
        module = importlib.import_module(self.source_module)
        return module.Screener()
    
    @retry(stop=stop_after_attempt(Config.DEFAULT_RETRIES), wait=wait_exponential(multiplier=1, min=2, max=10))
    def stock(self, **kwargs):
        allowed_kwargs = ['params', 'limit', 'lang']
        processed_kwargs = {k: v for k, v in kwargs.items() if k in allowed_kwargs}
        return self.data_source.stock(**processed_kwargs)

class Fund(BaseComponent):
    SUPPORTED_SOURCES = ["FMARKET"]

    def __init__(self, source: str = "FMARKET", random_agent: bool = False):
        super().__init__(source=source)
        self.random_agent = random_agent
        self.details = self.data_source.details

    def _load_data_source(self):
        module = importlib.import_module(self.source_module)
        return module.Fund(self.random_agent)

class MSNComponents:
    """
    Class (lớp) quản lý các chức năng của thư viện Vnstock liên quan đến thị trường ngoại hối.
    """
    def __init__(self, symbol: Optional[str]='EURUSD', source: str = "MSN"):
        self.symbol = symbol.upper()
        self.source = source.upper()
        if self.source not in ["MSN"]:
            raise ValueError("Hiện tại chỉ có nguồn dữ liệu từ MSN được hỗ trợ.")
        self._initialize_components()

    def _initialize_components(self):
        # Initialize each sub-component with the current symbol
        self.quote = Quote(self.symbol, self.source)
        self.listing = Listing(source=self.source)

        if self.source != "MSN":    
            logger.warning("Thông tin niêm yết sẽ được truy xuất từ MSN")

    def update_symbol(self, symbol: str):
        """
        Update the symbol for all sub-components.
        """
        self.symbol = symbol.upper()
        self._initialize_components()
