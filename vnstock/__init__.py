import vnai

# Lazy import Vnstock to avoid circular import deadlock
_Vnstock = None

def _get_vnstock():
    """Lazy load Vnstock class."""
    global _Vnstock
    if _Vnstock is None:
        from vnstock.common.client import Vnstock as _VnstockClass
        _Vnstock = _VnstockClass
    return _Vnstock

# Create a lazy proxy for Vnstock
class Vnstock:
    """Lazy proxy for vnstock.common.client.Vnstock to avoid circular import."""
    def __new__(cls, *args, **kwargs):
        actual_class = _get_vnstock()
        return actual_class(*args, **kwargs)

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

# User authentication and API key registration
from .core.utils.auth import (
    register_user,
    change_api_key,
    check_status,
)

# Load connector modules to register providers
# Tải các module connector để đăng ký các provider
from . import connector

# Load explorer modules to register providers (lazy to avoid deadlock)
# Tải các module explorer để đăng ký các provider (lazy để tránh deadlock)
_explorer_modules_loaded = False

def _ensure_explorer_modules_loaded():
    """Lazy load explorer modules to avoid circular import deadlock."""
    global _explorer_modules_loaded
    if _explorer_modules_loaded:
        return
    try:
        from .explorer import vci, tcbs, msn, kbs  # noqa: F401
        _explorer_modules_loaded = True
    except Exception as e:
        _explorer_modules_loaded = True  # Mark as loaded to avoid retry loops
        import warnings
        warnings.warn(f"Failed to load explorer modules: {e}", stacklevel=2)

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
    # Authentication
    "register_user",
    "change_api_key",
    "check_status",
]

# Delay vnai.setup() to avoid circular import deadlock
_vnai_initialized = False

def _ensure_vnai_initialized():
    """Ensure vnai is initialized (called on first use)."""
    global _vnai_initialized
    if _vnai_initialized:
        return
    try:
        vnai.setup()
        _vnai_initialized = True
    except Exception:
        _vnai_initialized = True  # Mark as initialized to avoid retry loops

# Lazy check for dependency compatibility (non-blocking, compact output)
try:
    from vnstock.core.utils.upgrade import update_notice
    update_notice(verbose=False)
except Exception:
    # Silently fail if notice check has any issues
    pass
