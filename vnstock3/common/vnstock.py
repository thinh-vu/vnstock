import importlib
from typing import Optional
from vnstock3.core.utils.logger import get_logger
from vnstock3.common.data.data_explorer import StockComponents, MSNComponents
from vnstock3.explorer.msn.const import _CURRENCY_ID_MAP, _GLOBAL_INDICES, _CRYPTO_ID_MAP

logger = get_logger(__name__)

class Vnstock:
    """
    Class (lớp) chính quản lý các chức năng của thư viện Vnstock.
    """
    
    SUPPORTED_SOURCES = ["VCI", "TCBS", "MSN"]
    msn_symbol_map = {**_CURRENCY_ID_MAP, **_GLOBAL_INDICES, **_CRYPTO_ID_MAP}

    def __init__(self, source:str="VCI"):
        self.source = source.upper()
        if self.source not in self.SUPPORTED_SOURCES:
            raise ValueError(F"Hiện tại chỉ có nguồn dữ liệu từ {', '.join(self.SUPPORTED_SOURCES)} được hỗ trợ.")
        self.source = source.upper()
        # self.utils = Utils(self)

    def stock(self, symbol: Optional[str]=None, source: Optional[str] = "VCI"):
        if symbol is None:
            self.symbol = 'VN30F1M'
            logger.info("Mã chứng khoán không được chỉ định, chương trình mặc định sử dụng VN30F1M")
        else:
            self.symbol = symbol
        return StockComponents(self.symbol, source)
    
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
