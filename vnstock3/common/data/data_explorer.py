import importlib
from typing import Optional
from vnstock3.core.utils.logger import get_logger
from vnstock3.explorer.msn.const import _CURRENCY_ID_MAP, _GLOBAL_INDICES, _CRYPTO_ID_MAP
from functools import wraps

logger = get_logger(__name__)

# def property(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         try:
#             result = func(*args, **kwargs)
#             print(f"Completed property: {func.__name__}")
#             return result
#         except Exception as e:
#             print(f"property failed: {func.__name__}, Error: {e}")
#             raise
#     return wrapper

class Vnstock:
    """
    Class (lớp) chính quản lý các chức năng của thư viện Vnstock.
    """
    def __init__(self, source:str="VCI"):
        if source.upper() not in ["VCI", "TCBS", "VND"]:
            raise ValueError("Hiện tại chỉ có nguồn dữ liệu từ VCI và TCBS được hỗ trợ.")
        self.source = source.upper()
        # self.utils = Utils(self)

    def stock(self, symbol: Optional[str], source: Optional[str] = "VCI"):
        return StockComponents(symbol, source)
    
    def fx(self, symbol: Optional[str]='EURUSD', source: Optional[str] = "MSN"):
        return MSNComponents(symbol, source)
    
    def crypto(self, symbol: Optional[str]='BTC', source: Optional[str] = "MSN"):
        return MSNComponents(symbol, source)
    
    def world_index(self, symbol: Optional[str]='DJI', source: Optional[str] = "MSN"):
        return MSNComponents(symbol, source)


class StockComponents:
    """
    Class (lớp) quản lý các chức năng của thư viện Vnstock liên quan đến cổ phiếu.
    """
    def __init__(self, symbol: str, source: str = "VCI"):
        self.symbol = symbol.upper()
        if source.upper() not in ["VCI", "TCBS", "VND"]:
            raise ValueError("Hiện tại chỉ có nguồn dữ liệu từ VCI và TCBS được hỗ trợ.")
        self.source = source.upper()
        self._initialize_components()

    def _initialize_components(self):
        # Initialize each sub-component with the current symbol
        self.quote = Quote(self.symbol, self.source)
        
        if self.source not in ["VCI", "TCBS"]:
            self.listing = Listing(source='VCI')
            self.trading = Trading(self.symbol, source='VCI')
            logger.warning("Thông tin niêm yết & giao dịch sẽ được truy xuất từ VCI")
        elif self.source == "TCBS":
            self.listing = Listing(source='VCI')
            self.trading = Trading(self.symbol, source=self.source)
            self.company = Company(self.symbol, source=self.source)
            logger.warning("Thông tin niêm yết sẽ được truy xuất từ TCBS")
        else:
            self.listing = Listing(source=self.source)
            self.trading = Trading(self.symbol, source=self.source)

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
    def __init__(self, symbol: str, source: str = "VCI"):
        """
        Class (lớp) quản lý các nguồn dữ liệu được tiêu chuẩn hoá cho dữ liệu đồ thị nến, dữ liệu trả về tuỳ thuộc vào nguồn dữ liệu sẵn có được chọn.
        """
        self.source = source.upper()
        if self.source not in ["VCI", "TCBS", "VND", "MSN"]:
            raise ValueError("Hiện tại chỉ có nguồn dữ liệu từ VCI, TCBS, VND, và MSN được hỗ trợ.")
        self.symbol = symbol.upper()
        self.source_module = f"vnstock3.explorer.{source.lower()}"
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

    def history(self, symbol:Optional[str]='VN30F1M', **kwargs):
        """
        Truy xuất dữ liệu giá lịch sử từ nguồn dữ liệu được chọn.
        """
        if self.source == "MSN":
            symbol_map = {**_CURRENCY_ID_MAP, **_GLOBAL_INDICES, **_CRYPTO_ID_MAP}
            if symbol is not None:
                original_symbol = self.symbol
                self.symbol = symbol_map[self.symbol]
                self._update_data_source(symbol=self.symbol)
                return self.data_source.history(**kwargs)
        else:
            # if symbol is provided, override the symbol
            if symbol is not None:
                self.symbol = symbol.upper()
            self._update_data_source(symbol)
            return self.data_source.history(**kwargs)
    
    def intraday(self, symbol:Optional[str], **kwargs):
        """
        Truy xuất dữ liệu giao dịch trong ngày từ nguồn dữ liệu được chọn.
        """
        # if symbol is provided, override the symbol
        if symbol is not None:
            self.symbol = symbol.upper()
        self._update_data_source(symbol)
        return self.data_source.intraday(**kwargs)
    
    def price_depth(self, symbol:Optional[str], **kwargs):
        """
        Truy xuất dữ liệu KLGD theo bước giá từ nguồn dữ liệu được chọn.
        """
        # if symbol is provided, override the symbol
        if symbol is not None:
            self.symbol = symbol.upper()
        self._update_data_source(symbol)
        return self.data_source.price_depth(**kwargs)
    
class Listing:
    """
    Class (lớp) quản lý các nguồn dữ liệu được tiêu chuẩn hoá cho thông tin niêm yết, dữ liệu trả về tuỳ thuộc vào nguồn dữ liệu sẵn có được chọn.
    """
    def __init__(self, source: str = "VCI"):
        """
        Initializes the DataExplorer with the specified source and symbol.
        """
        # validate the source to only VCI are available so far
        if source.upper() not in ["VCI", "MSN"]:
            raise ValueError("Hiện tại chỉ có nguồn dữ liệu từ VCI được hỗ trợ.")
        self.source_module = f"vnstock3.explorer.{source.lower()}"
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
    def __init__(self, symbol:Optional[str]='VN30F1M', source: str = "VCI"):
        """
        Initializes the DataExplorer with the specified source and symbol.
        """
        self.symbol = symbol.upper()
        # validate the source to only VCI are available so far
        if source.upper() not in ["VCI", "TCBS"]:
            raise ValueError("Hiện tại chỉ có nguồn dữ liệu từ VCI và TCBS được hỗ trợ.")
        self.source_module = f"vnstock3.explorer.{source.lower()}"
        self.data_source = self._load_data_source()

    def _load_data_source(self):
        """
        Điều hướng lớp (class) nguồn dữ liệu được lựa chọn.
        """
        module = importlib.import_module(self.source_module)
        return module.Trading(self.symbol)
    
    def _update_data_source(self, symbol: Optional[str] = None):
        """
        Update the data source if a new symbol is provided.
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
        if source.upper() not in ["TCBS"]:
            raise ValueError("Hiện tại chỉ có nguồn dữ liệu từ TCBS được hỗ trợ.")
        self.source_module = f"vnstock3.explorer.{source.lower()}"
        self.data_source = self._load_data_source()

    def _load_data_source(self):
        """
        Điều hướng lớp (class) nguồn dữ liệu được lựa chọn.
        """
        module = importlib.import_module(self.source_module)
        return module.Company(self.symbol)
    
    def _update_data_source(self, symbol: Optional[str] = None):
        """
        Update the data source if a new symbol is provided.
        """
        if symbol:
            self.symbol = symbol.upper()
            self.data_source = self._load_data_source()

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
    """
    def __init__(self, symbol:str, period:Optional[str]='quarter', source:Optional[str]='TCBS', get_all:Optional[bool]=True):
        self.symbol = symbol.upper()
        self.period = period
        self.get_all = get_all
        if source.upper() not in ["TCBS" , "VCI"]:
            raise ValueError("Hiện tại chỉ có nguồn dữ liệu từ TCBS và VCI được hỗ trợ thông tin báo cáo tài chính.")
        self.source_module = f"vnstock3.explorer.{source.lower()}"
        self.data_source = self._load_data_source()

    def _load_data_source(self):
        """
        Điều hướng lớp (class) nguồn dữ liệu được lựa chọn.
        """
        module = importlib.import_module(self.source_module)
        return module.Finance(self.symbol)
    
    def _update_data_source(self, symbol: Optional[str] = None):
        """
        Update the data source if a new symbol is provided.
        """
        if symbol:
            self.symbol = symbol.upper()
            self.data_source = self._load_data_source()

    def balance_sheet(self, **kwargs):
        """
        Truy xuất bảng cân đối kế toán.
        """
        return self.data_source.balance_sheet(**kwargs)

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