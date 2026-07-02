"""Public entrypoint for the flat/open vnstock package."""

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


# Use standard vnstock classes
# Load UI and helper classes
from vnstock.ui import (  # noqa: E402
    Broker,
    Fundamental,
    Market,
    Reference,
    Retail,
    show_api,
    show_doc,
)

from .api.company import Company  # noqa: E402
from .api.financial import Finance  # noqa: E402
from .api.listing import Listing  # noqa: E402
from .api.quote import Quote  # noqa: E402
from .api.trading import Trading  # noqa: E402
from .explorer.fmarket import Fund  # noqa: E402

show_docs = show_doc  # Alias for better parity


# Market constants
# Load connector modules to register providers
from . import connector  # noqa: E402
from .constants import (  # noqa: E402
    EXCHANGES,
    INDEX_GROUPS,
    INDICES_INFO,
    INDICES_MAP,
    SECTOR_IDS,
)

# Flat access compatibility helpers
from .core.utils.auth import (  # noqa: E402
    change_api_key,
    check_status,
    register_user,
)

# Load explorer modules to register providers (lazy to avoid deadlock)
_explorer_modules_loaded = False


def _ensure_explorer_modules_loaded():
    """Lazy load explorer modules to avoid circular import deadlock."""
    global _explorer_modules_loaded
    if _explorer_modules_loaded:
        return
    try:
        from .explorer import kbs, msn, vci  # noqa: F401

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
    "Fund",
    "ui",
    "show_api",
    "show_doc",
    "Reference",
    "Market",
    "Fundamental",
    "Retail",
    "Broker",
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


def _ensure_vnai_initialized():
    """Compatibility no-op retained for legacy internal imports."""
    return None


# Lazy check for dependency compatibility (non-blocking, compact output)
try:
    from vnstock.core.utils.upgrade import update_notice

    update_notice(verbose=False)
except Exception:
    # Silently fail if notice check has any issues
    pass
