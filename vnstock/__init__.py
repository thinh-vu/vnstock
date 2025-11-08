import vnai
from vnstock.common.client import Vnstock

# Sử dụng các lớp từ vnstock tiêu chuẩn
from .api.quote import Quote
from .api.company import Company
from .api.financial import Finance
from .api.listing import Listing
from .api.trading import Trading
from .api.screener import Screener
from .explorer.fmarket import Fund

# Market constants
from .constants import (
    INDICES_INFO,
    INDICES_MAP,
    INDEX_GROUPS,
    SECTOR_IDS,
    EXCHANGES,
)

# Load connector modules to register providers
# Tải các module connector để đăng ký các provider
from . import connector

# Load explorer modules to register providers
# Tải các module explorer để đăng ký các provider
from .explorer import vci, tcbs, msn  # noqa: F401

__all__ = [
    "Vnstock",
    "Quote",
    "Listing",
    "Company",
    "Finance",
    "Trading",
    "Screener",
    "Fund",
    "connector",
    "INDICES_INFO",
    "INDICES_MAP",
    "INDEX_GROUPS",
    "SECTOR_IDS",
    "EXCHANGES",
]

vnai.setup()
