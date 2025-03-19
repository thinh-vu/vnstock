import importlib
from typing import Optional
import logging
from vnstock.core.utils.logger import get_logger
from vnstock.common.data.data_explorer import StockComponents, MSNComponents, Fund
from vnstock.explorer.msn.const import _CURRENCY_ID_MAP, _GLOBAL_INDICES, _CRYPTO_ID_MAP

logger = get_logger(__name__)

class Vnstock:
    """
    Class (lớp) chính quản lý các chức năng của thư viện Vnstock.
    """
    
    SUPPORTED_SOURCES = ["VCI", "TCBS", "MSN"]
    msn_symbol_map = {**_CURRENCY_ID_MAP, **_GLOBAL_INDICES, **_CRYPTO_ID_MAP}

    def __init__(self, symbol:str=None, source:str="VCI", show_log:bool=True):
        """
        Hàm khởi tạo của lớp Vnstock.
        
        Tham số:
            - source (str): Nguồn dữ liệu chứng khoán. Mặc định là 'VCI' (Vietstock). Các giá trị hợp lệ là 'VCI', 'TCBS', 'MSN'.
            - show_log (bool): Hiển thị log hoạt động của chương trình. Mặc định là True.
        """
        self.symbol = symbol
        self.source = source.upper()
        self.show_log = show_log
        if self.source not in self.SUPPORTED_SOURCES:
            raise ValueError(F"Hiện tại chỉ có nguồn dữ liệu từ {', '.join(self.SUPPORTED_SOURCES)} được hỗ trợ.")
        self.source = source.upper()
        # if show_log is False, disable logging
        if not show_log:
            logger.setLevel(logging.CRITICAL)
        # self.utils = Utils(self)

    def stock(self, symbol: Optional[str]=None, source: Optional[str] = None):
        if symbol is None:
            self.symbol = 'VN30F1M'
            logger.info("Mã chứng khoán không được chỉ định, chương trình mặc định sử dụng VN30F1M")
        else:
             self.symbol = symbol
 
        if source is None:
            source = self.source
        else:
            self.symbol = symbol
             
        return StockComponents(self.symbol, source, show_log=self.show_log)
    
    def fx(self, symbol: Optional[str]='EURUSD', source: Optional[str] = "MSN"):
        if symbol:
            self.symbol = self.msn_symbol_map[symbol]
        return MSNComponents(self.symbol, source)
    
    def crypto(self, symbol: Optional[str]='BTC', source: Optional[str] = "MSN"):
        if symbol:
            self.symbol = self.msn_symbol_map[symbol]
        return MSNComponents(self.symbol, source)
    
    def world_index(self, symbol: Optional[str]='DJI', source: Optional[str] = "MSN"):
        if symbol:
            self.symbol = self.msn_symbol_map[symbol]
        return MSNComponents(self.symbol, source)
    
    def fund(self, source: Optional[str] = "FMARKET"):
        return Fund(source)
