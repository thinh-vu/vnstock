import logging
import importlib
import pandas as pd
from typing import Optional, Any, Dict
from vnstock.core.utils.logger import get_logger
from vnstock.explorer.msn.const import _CURRENCY_ID_MAP, _GLOBAL_INDICES, _CRYPTO_ID_MAP
from vnstock.core.utils.parser import get_asset_type
# from functools import wraps

logger = get_logger(__name__)
class StockComponents:
    """
    Class (lớp) quản lý các chức năng của thư viện Vnstock liên quan đến cổ phiếu.
    """
    SUPPORTED_SOURCES = ["VCI", "TCBS", "MSN"]

    def __init__(self, symbol: str, source: str = "VCI", show_log:bool=True):
        """
        Khởi tạo lớp (class) với mã chứng khoán và nguồn dữ liệu được chọn.

        Tham số:
            - symbol (str): Mã chứng khoán cần truy xuất thông tin.
            - source (str): Nguồn dữ liệu cần truy xuất thông tin. Mặc định là 'VCI'.
            - show_log (bool): mặc định là True để hiển thị đầy đủ cảnh báo, đặt False nếu muốn tắt logger.
        """
        if symbol is not None:
            self.symbol = symbol.upper()
        else:
            self.symbol = 'VN30F1M'

        self.asset_type = get_asset_type(self.symbol)

        if source is not None:
            self.source = source.upper()
        self.show_log = show_log
        if self.source not in self.SUPPORTED_SOURCES:
            raise ValueError(f"Hiện tại chỉ có nguồn dữ liệu từ {', '.join(self.SUPPORTED_SOURCES)} được hỗ trợ.")
        if not show_log:
            logger.setLevel(logging.CRITICAL)
        self._initialize_components()

    def _initialize_components(self):
        if self.source not in self.SUPPORTED_SOURCES:
            raise ValueError(f"Hiện tại chỉ có nguồn dữ liệu từ {', '.join(self.SUPPORTED_SOURCES)} được hỗ trợ.")

        if self.asset_type == "stock":
            self.company = Company(self.symbol, source=self.source)
            self.finance = Finance(self.symbol, source=self.source)
        else:
            self.company = None
            self.finance = None
            logger.info("Mã chứng khoán không phải cổ phiếu, không thể truy xuất thông tin công ty và tài chính.")
        
        if self.source in ['VCI', 'TCBS']:
            self.listing = Listing(source='VCI')
            self.screener = Screener(source='TCBS')
            self.quote = Quote(self.symbol, self.source)
            self.trading = Trading(self.symbol, source=self.source)
        
            if self.source == 'TCBS':
                logger.info("Nguồn TCBS hiện không cung cấp thông tin niêm yết. Dữ liệu được tự động trả về từ VCI.")
            
            elif self.source == 'VCI':
                logger.info("Nguồn VCI hiện không hỗ trợ tính năng bộ lọc cổ phiếu. Dữ liệu được tự động trả về từ TCBS.")
        elif self.source == 'MSN':
            self.quote = Quote(self.symbol, 'MSN')
            self.listing = Listing(source='MSN')

    def update_symbol(self, symbol: str):
        """
        Update the symbol for all sub-components.
        """
        self.symbol = symbol.upper()
        self._initialize_components()

# Các class (lớp) dưới đây sẽ được sử dụng để điều hướng nguồn dữ liệu cụ thể từ các nguồn dữ liệu khác nhau.
class Quote:
    """
    Class (lớp) quản lý các nguồn dữ liệu được tiêu chuẩn hoá cho dữ liệu đồ thị nến, dữ liệu trả về tuỳ thuộc vào nguồn dữ liệu sẵn có được chọn.
    """
    SUPPORTED_SOURCES = ["VCI", "TCBS", "MSN"]

    def __init__(self, symbol: str, source: str = "VCI"):
        """
        Class (lớp) quản lý các nguồn dữ liệu được tiêu chuẩn hoá cho dữ liệu đồ thị nến, dữ liệu trả về tuỳ thuộc vào nguồn dữ liệu sẵn có được chọn.
        """
        self.source = source.upper()
        if self.source not in self.SUPPORTED_SOURCES:
            raise ValueError(f"Hiện tại chỉ có nguồn dữ liệu từ {', '.join(self.SUPPORTED_SOURCES)} được hỗ trợ.")
        self.symbol = symbol.upper()
        self.source_module = f"vnstock.explorer.{source.lower()}"
        self.data_source = self._load_data_source()

    def _load_data_source(self):
        """
        Điều hướng lớp (class) nguồn dữ liệu được lựa chọn.
        """
        module = importlib.import_module(self.source_module)
        if self.source == "MSN":
            return module.Quote(self.symbol.lower())
        else:
            return module.Quote(self.symbol)
    
    def _update_data_source(self, symbol: Optional[str] = None):
        """
        Update the data source if a new symbol is provided.
        """
        if self.source != 'MSN':
            if symbol:
                self.symbol = symbol.upper()
                self.data_source = self._load_data_source()
        else:
            self.data_source = self._load_data_source()
        
    def history(self, symbol: Optional[str] = None, **kwargs):
        """
        Truy xuất dữ liệu giá lịch sử từ nguồn dữ liệu được chọn.
        """
        if self.source == "MSN":
            symbol_map = {**_CURRENCY_ID_MAP, **_GLOBAL_INDICES, **_CRYPTO_ID_MAP}
            if symbol:
                self.symbol = symbol_map[symbol]
                logger.info(f"Chuyển đổi mã chứng khoán {symbol} sang mã chứng khoán MSN: {self.symbol}")
                self._update_data_source(symbol=self.symbol)
                return self.data_source.history(**kwargs)
        else:
            if symbol:
                self.symbol = symbol.upper()
            self._update_data_source(self.symbol)
            return self.data_source.history(**kwargs)
        
        self._update_data_source(self.symbol)
        return self.data_source.history(**kwargs)
    
    def intraday(self, symbol: Optional[str] = None, **kwargs):
        """
        Truy xuất dữ liệu giao dịch trong ngày từ nguồn dữ liệu được chọn.
        """
        # if symbol is provided, override the symbol
        self._update_data_source(symbol)
        return self.data_source.intraday(**kwargs)
    
    def price_depth(self, symbol: Optional[str] = None, **kwargs):
        """
        Truy xuất dữ liệu KLGD theo bước giá từ nguồn dữ liệu được chọn.
        """
        self._update_data_source(symbol)
        return self.data_source.price_depth(**kwargs)

class Listing:
    """
    Class (lớp) quản lý các nguồn dữ liệu được tiêu chuẩn hoá cho thông tin niêm yết, dữ liệu trả về tuỳ thuộc vào nguồn dữ liệu sẵn có được chọn.
    """
    
    SUPPORTED_SOURCES = ["VCI", "MSN"]
    def __init__(self, source: str = "VCI"):
        """
        Khởi tạo lớp (class) với nguồn dữ liệu được chọn.
        """
        self.source = source.upper()
        if self.source not in self.SUPPORTED_SOURCES:
            raise ValueError(f"Hiện tại chỉ có nguồn dữ liệu từ {', '.join(self.SUPPORTED_SOURCES)} được hỗ trợ.")
        self.source_module = f"vnstock.explorer.{self.source.lower()}"
        self.data_source = self._load_data_source()

    def _load_data_source(self):
        """
        Điều hướng lớp (class) nguồn dữ liệu được lựa chọn.
        """
        module = importlib.import_module(self.source_module)
        return module.Listing()

    def all_symbols(self, **kwargs):
        """
        Liệt kê tất cả các mã chứng khoán từ nguồn dữ liệu được chọn.
        """
        return self.data_source.all_symbols(**kwargs)
    
    def symbols_by_industries(self, **kwargs):
        """
        Liệt kê tất cả các mã chứng khoán theo ngành icb từ nguồn dữ liệu được chọn.
        """
        return self.data_source.symbols_by_industries(**kwargs)
    
    def symbols_by_exchange(self, **kwargs):
        """
        Liệt kê tất cả các mã chứng khoán theo sàn giao dịch từ nguồn dữ liệu được chọn.
        """
        return self.data_source.symbols_by_exchange(**kwargs)
    
    def symbols_by_group(self, group='VN30', **kwargs):
        """
        Liệt kê tất cả mã chứng khoán theo nhóm phân loại. Ví dụ HOSE, VN30, VNMidCap, VNSmallCap, VNAllShare, VN100, ETF, HNX, HNX30, HNXCon, HNXFin, HNXLCap, HNXMSCap, HNXMan, UPCOM, FU_INDEX (mã chỉ số hợp đồng tương lai)
        """
        return self.data_source.symbols_by_group(group, **kwargs)

    def industries_icb(self, **kwargs):
        """
        Liệt kê tất cả thông tin các ngành icb từ nguồn dữ liệu được chọn.
        """
        return self.data_source.industries_icb(**kwargs)
    
    def all_future_indices(self, **kwargs):
        """
        Liệt kê tất cả thông tin các mã hợp đồng tương lai.
        """
        return self.data_source.all_future_indices(**kwargs)

    def all_covered_warrant(self, **kwargs):
        """
        Liệt kê tất cả thông tin các mã chứng quyền.
        """
        return self.data_source.all_covered_warrant(**kwargs)

    def all_bonds(self, **kwargs):
        """
        Liệt kê tất cả thông tin các mã trái phiếu hiện hành.
        """
        return self.data_source.all_bonds(**kwargs)
    
    def all_government_bonds(self, **kwargs):
        """
        Liệt kê tất cả thông tin các mã trái phiếu chính phủ.
        """
        return self.data_source.all_government_bonds(**kwargs)
    
class Trading:
    """
    Class (lớp) quản lý các nguồn dữ liệu được tiêu chuẩn hoá cho thông tin giao dịch.
    """
    SUPPORTED_SOURCES = ["VCI", "TCBS"]
    def __init__(self, symbol:Optional[str]='VN30F1M', source: str = "VCI"):
        """
        Khởi tạo lớp (class) với nguồn dữ liệu được chọn.
        """
        self.symbol = symbol.upper()
        self.source = source.upper()
        if self.source not in self.SUPPORTED_SOURCES:
            raise ValueError(f"Hiện tại chỉ có nguồn dữ liệu từ {', '.join(self.SUPPORTED_SOURCES)} được hỗ trợ.")
        self.source_module = f"vnstock.explorer.{source.lower()}"
        self.data_source = self._load_data_source()

    def _load_data_source(self):
        """
        Điều hướng lớp (class) nguồn dữ liệu được lựa chọn.
        """
        module = importlib.import_module(self.source_module)
        return module.Trading(self.symbol)
    
    def _update_data_source(self, symbol: Optional[str] = None):
        """
        Cập nhật nguồn dữ liệu nếu mã chứng khoán mới được nhập.
        """
        if symbol:
            self.symbol = symbol.upper()
        self.data_source = self._load_data_source()
    
    def price_board(self, symbols_list:list, **kwargs):
        """
        Truy xuất dữ liệu giao dịch trong ngày từ nguồn dữ liệu được chọn.
        """
        return self.data_source.price_board(symbols_list, **kwargs)
    
class Company:
    """
    Class (lớp) quản lý các nguồn dữ liệu được tiêu chuẩn hoá cho thông tin giao dịch.
    """
    def __init__(self, symbol:Optional[str]='ACB', source: str = "TCBS"):
        """
        Initializes the DataExplorer with the specified source and symbol.
        """
        self.symbol = symbol.upper()
        # validate the source to only VCI are available so far
        if source.upper() not in ["TCBS", "VCI"]:
            raise ValueError("Hiện tại chỉ có nguồn dữ liệu từ TCBS & VCI được hỗ trợ.")
        self.source_module = f"vnstock.explorer.{source.lower()}"
        self.data_source = self._load_data_source()

    def _load_data_source(self):
        """
        Điều hướng lớp (class) nguồn dữ liệu được lựa chọn.
        """
        module = importlib.import_module(self.source_module)
        return module.Company(self.symbol)
    
    def _update_data_source(self, symbol: Optional[str] = None):
        """
        Cập nhật nguồn dữ liệu nếu mã chứng khoán mới được nhập.
        """
        if symbol:
            self.symbol = symbol.upper()
            self.data_source = self._load_data_source()

    def overview(self, **kwargs):
        """
        Truy xuất thông tin giới thiệu công ty.
        """
        return self.data_source.overview(**kwargs)

    def profile(self, **kwargs):
        """
        Truy xuất thông tin giới thiệu công ty.
        """
        return self.data_source.profile(**kwargs)
    
    def shareholders(self, **kwargs):
        """
        Truy xuất dữ liệu cổ đông lớn.
        """
        return self.data_source.shareholders(**kwargs)
    
    def insider_deals(self, **kwargs):
        """
        Truy xuất dữ liệu giao dịch nội bộ.
        """
        return self.data_source.insider_deals(**kwargs)
    
    def subsidiaries(self, **kwargs):
        """
        Truy xuất dữ liệu công ty con, công ty liên kết.
        """
        return self.data_source.subsidiaries(**kwargs)
    
    def officers(self, **kwargs):
        """
        Truy xuất thông tin lãnh đạo công ty.
        """
        return self.data_source.officers(**kwargs)
    
    def events(self, **kwargs):
        """
        Truy xuất thông tin sự kiện liên quan.
        """
        return self.data_source.events(**kwargs)
    
    def news(self, **kwargs):
        """
        Truy xuất tin tức liên quan.
        """
        return self.data_source.news(**kwargs)
    
    def dividends(self, **kwargs):
        """
        Truy xuất lịch sử chia cổ tức của công ty.
        """
        return self.data_source.dividends(**kwargs)

class Finance:
    """
    Lớp quản lý các nguồn dữ liệu được tiêu chuẩn hoá cho thông tin tài chính doanh nghiệp.
    
    Attributes:
        symbol (str): Mã chứng khoán
        period (str): Kỳ báo cáo ('quarter' hoặc 'annual')
        source (str): Nguồn dữ liệu ('TCBS' hoặc 'VCI')
        get_all (bool): Lấy tất cả dữ liệu có sẵn
    """
    SUPPORTED_SOURCES = ["TCBS", "VCI"]
    SUPPORTED_PERIODS = ["quarter", "annual"]

    def __init__(
        self, 
        symbol: str, 
        period: str = 'quarter', 
        source: str = 'TCBS', 
        get_all: bool = True
    ):
        """
        Khởi tạo đối tượng Finance.
        
        Args:
            symbol: Mã chứng khoán
            period: Kỳ báo cáo ('quarter' hoặc 'annual')
            source: Nguồn dữ liệu ('TCBS' hoặc 'VCI')
            get_all: Lấy tất cả dữ liệu có sẵn
        """
        self.symbol = symbol.upper()
        
        # Validate period
        self.period = period.lower()
        if self.period not in self.SUPPORTED_PERIODS:
            raise ValueError(f"Kỳ báo cáo phải là một trong {', '.join(self.SUPPORTED_PERIODS)}")
        
        self.get_all = get_all
        
        # Validate source
        self.source = source.upper()
        if self.source not in self.SUPPORTED_SOURCES:
            raise ValueError(
                f"Hiện tại chỉ có nguồn dữ liệu từ {', '.join(self.SUPPORTED_SOURCES)} "
                "được hỗ trợ thông tin báo cáo tài chính."
            )
        
        self.source_module = f"vnstock.explorer.{self.source.lower()}"
        try:
            self.data_source = self._load_data_source()
        except (ImportError, AttributeError) as e:
            logger.error(f"Không thể tải module nguồn dữ liệu: {e}")
            raise

    def _load_data_source(self):
        """
        Điều hướng lớp (class) nguồn dữ liệu được lựa chọn.
        
        Returns:
            Object: Instance của lớp Finance từ module nguồn dữ liệu
        """
        module = importlib.import_module(self.source_module)
        return module.Finance(self.symbol)
    
    def _update_data_source(self, symbol: Optional[str] = None):
        """
        Cập nhật nguồn dữ liệu nếu mã chứng khoán mới được nhập.
        
        Args:
            symbol: Mã chứng khoán mới (nếu có)
        """
        if symbol:
            self.symbol = symbol.upper()
            try:
                self.data_source = self._load_data_source()
            except (ImportError, AttributeError) as e:
                logger.error(f"Không thể cập nhật nguồn dữ liệu: {e}")
                raise

    def _process_kwargs(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Xử lý tham số kwargs dựa trên nguồn dữ liệu.
        
        Args:
            kwargs: Các tham số bổ sung
            
        Returns:
            Dict: Các tham số đã được xử lý
        """
        allowed_kwargs = ['lang', 'dropna', 'period', 'dropna', 'show_log']
        processed_kwargs = {k: v for k, v in kwargs.items() if k in allowed_kwargs}
        
        if self.source == 'TCBS':
            if 'lang' in processed_kwargs:
                logger.info('Nguồn TCBS chỉ hỗ trợ báo cáo tiếng Việt')
                processed_kwargs.pop('lang')
            if 'dropna' in processed_kwargs:
                logger.info('Tham số dropna không được hỗ trợ cho nguồn dữ liệu TCBS')
                processed_kwargs.pop('dropna')

        # Add period and get_all to kwargs if not explicitly provided
        if 'period' not in processed_kwargs:
            processed_kwargs['period'] = self.period
            
        return processed_kwargs

    def _get_financial_data(self, data_type: str, symbol: Optional[str] = None, **kwargs) -> Any:
        """
        Phương thức chung để lấy dữ liệu tài chính.
        
        Args:
            data_type: Loại dữ liệu tài chính cần lấy
            symbol: Mã chứng khoán (nếu khác với mã đã khởi tạo)
            **kwargs: Các tham số bổ sung
        """
        self._update_data_source(symbol)
        processed_kwargs = self._process_kwargs(kwargs)
        
        try:
            method = getattr(self.data_source, data_type)
            return method(**processed_kwargs)
        except AttributeError:
            logger.error(f"Nguồn dữ liệu {self.source} không hỗ trợ dữ liệu {data_type}")
            raise
        except Exception as e:
            logger.error(f"Lỗi khi lấy dữ liệu {data_type}: {e}")
            raise

    def balance_sheet(self, symbol: Optional[str] = None, **kwargs) -> Any:
        """
        Truy xuất bảng cân đối kế toán.
        
        Args:
            symbol: Mã chứng khoán (nếu khác với mã đã khởi tạo)
            **kwargs: Các tham số bổ sung
        """
        return self._get_financial_data('balance_sheet', symbol, **kwargs)
    
    def income_statement(self, symbol: Optional[str] = None, **kwargs) -> Any:
        """
        Truy xuất báo cáo kết quả kinh doanh.
        
        Args:
            symbol: Mã chứng khoán (nếu khác với mã đã khởi tạo)
            **kwargs: Các tham số bổ sung
        """
        return self._get_financial_data('income_statement', symbol, **kwargs)
    
    def cash_flow(self, symbol: Optional[str] = None, **kwargs) -> Any:
        """
        Truy xuất báo cáo lưu chuyển tiền tệ.
        
        Args:
            symbol: Mã chứng khoán (nếu khác với mã đã khởi tạo)
            **kwargs: Các tham số bổ sung
        """
        return self._get_financial_data('cash_flow', symbol, **kwargs)
    
    def ratio(self, symbol: Optional[str] = None, **kwargs) -> Any:
        """
        Truy xuất các chỉ số tài chính.
        
        Args:
            symbol: Mã chứng khoán (nếu khác với mã đã khởi tạo)
            **kwargs: Các tham số bổ sung
        """
        return self._get_financial_data('ratio', symbol, **kwargs)

class Screener: 
    """
    Class (lớp) quản lý dữ liệu bộ lọc cổ phiếu. Hiện tại chỉ hỗ trợ nguồn dữ liệu từ TCBS.
    """
    def __init__(self, source: str = "TCBS"):
        self.source = source.upper()
        self.source_module = f"vnstock.explorer.{source.lower()}"
        self.data_source = self._load_data_source()

        if self.source not in ['TCBS']:
            raise ValueError(f"Hiện tại chỉ có nguồn dữ liệu từ {', '.join(self.SUPPORTED_SOURCES)} được hỗ trợ.")
        
    def _load_data_source(self, random_agent:bool=False):
        """
        Điều hướng lớp (class) nguồn dữ liệu được lựa chọn.
        """
        module = importlib.import_module(self.source_module)
        return module.Screener(random_agent)
    
    def stock (self, **kwargs):
        """
        Truy xuất danh sách cổ phiếu theo các tiêu chí được chỉ định.
        """
        allowed_kwargs = ['params', 'limit', 'lang']
        processed_kwargs = {k: v for k, v in kwargs.items() if k in allowed_kwargs}
        return self.data_source.stock(**processed_kwargs)

class Fund:
    def __init__(self, source: str = "FMARKET", random_agent:bool=False):
        """
        Class (lớp) quản lý các nguồn dữ liệu được tiêu chuẩn hoá cho dữ liệu đồ thị nến, dữ liệu trả về tuỳ thuộc vào nguồn dữ liệu sẵn có được chọn.
        """
        self.source = source.upper()
        self.supported_sources = ["FMARKET"]
        if self.source not in self.supported_sources:
            raise ValueError(f"Hiện tại chỉ có nguồn dữ liệu từ {', '.join(self.supported_sources)} được hỗ trợ.")
        self.random_agent = random_agent
        self.source_module = f"vnstock.explorer.{source.lower()}"
        self.data_source = self._load_data_source(random_agent)
        self.details = self.data_source.details

    def _load_data_source(self, random_agent:bool=False):
        """
        Điều hướng lớp (class) nguồn dữ liệu được lựa chọn.
        """
        module = importlib.import_module(self.source_module)
        return module.Fund(random_agent)
    
    def listing(self, fund_type:str="") -> pd.DataFrame:
        """
        Truy xuất danh sách tất cả các quỹ mở hiện có trên Fmarket thông qua API. Xem trực tiếp tại https://fmarket.vn

        Tham số:
        ----------
            fund_type (str): Loại quỹ cần lọc. Mặc định là rỗng để lấy tất cả các quỹ. Các loại quỹ hợp lệ bao gồm: 'BALANCED', 'BOND', 'STOCK'
        
        Trả về:
        -------
            pd.DataFrame: DataFrame chứa thông tin của tất cả các quỹ mở hiện có trên Fmarket. 
        """
        return self.data_source.listing(fund_type)
    
    def filter(self, symbol:str="") -> pd.DataFrame:
        """
        Truy xuất danh sách quỹ theo tên viết tắt (short_name) và mã id của quỹ. Mặc định là rỗng để liệt kê tất cả các quỹ.

        Tham số:
        ----------
            symbol (str): Tên viết tắt của quỹ cần tìm kiếm. Mặc định là rỗng để lấy tất cả các quỹ.

        Trả về:
        -------
            pd.DataFrame: DataFrame chứa thông tin của quỹ cần tìm kiếm.
        """
        return self.data_source.filter(symbol)

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