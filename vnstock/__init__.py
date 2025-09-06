import vnai
from vnstock.common.vnstock import Vnstock

# Sử dụng các lớp từ vnstock tiêu chuẩn
from .api.quote import Quote
from .api.company import Company
from .api.financial import Finance
from .api.listing import Listing
from .api.trading import Trading
from .api.screener import Screener
from .explorer.fmarket import Fund

__all__ = ["Vnstock", "Quote", "Listing", "Company", "Finance", "Trading", "Screener", "Fund"]

vnai.setup()