"""
UI Module - Unified Interface for vnstock
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from vnstock.ui.broker import Broker
    from vnstock.ui.fundamental import Fundamental
    from vnstock.ui.market import Market
    from vnstock.ui.reference import Reference
    from vnstock.ui.retail import Retail

__all__ = ["Reference", "Market", "Fundamental", "Retail", "Broker"]


def __getattr__(name: str) -> Any:
    """
    Lazy load UI modules using PEP 562.
    Allows IDE autocomplete and type hints to work correctly.
    """
    if name == "Reference":
        from vnstock.ui.reference import Reference as _Reference

        return _Reference
    elif name == "Market":
        from vnstock.ui.market import Market as _Market

        return _Market
    elif name == "Fundamental":
        from vnstock.ui.fundamental import Fundamental as _Fundamental

        return _Fundamental
    elif name == "Retail":
        from vnstock.ui.retail import Retail as _Retail

        return _Retail
    elif name == "Broker":
        from vnstock.ui.broker import Broker as _Broker

        return _Broker
    elif name == "show_api":
        from vnstock.ui.helper import show_api as _show_api

        return _show_api
    elif name == "show_doc":
        from vnstock.ui.helper import show_doc as _show_doc

        return _show_doc

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
