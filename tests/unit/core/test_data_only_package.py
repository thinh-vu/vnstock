"""
Tests for the data-only package boundary.

Baseline tests verifying:
- retained top-level data imports still work
- removed public exports are unavailable
- retained FMP provider credential behavior
"""

import sys
import types


def test_retained_data_imports_from_vnstock(monkeypatch):
    """All retained data extraction classes must be importable from vnstock."""
    fake_vnai = types.ModuleType("vnai")

    def optimize_execution(_name=None):
        def decorator(func):
            return func

        return decorator

    fake_vnai.optimize_execution = optimize_execution
    fake_vnai.setup = lambda: None
    monkeypatch.setitem(sys.modules, "vnai", fake_vnai)

    for module_name in list(sys.modules):
        if module_name == "vnstock" or module_name.startswith("vnstock."):
            monkeypatch.delitem(sys.modules, module_name, raising=False)

    import vnstock

    assert hasattr(vnstock, "Reference")
    assert hasattr(vnstock, "Market")
    assert hasattr(vnstock, "Fundamental")
    assert hasattr(vnstock, "Retail")
    assert hasattr(vnstock, "Quote")
    assert hasattr(vnstock, "Listing")
    assert hasattr(vnstock, "Company")
    assert hasattr(vnstock, "Finance")
    assert hasattr(vnstock, "Trading")
    assert hasattr(vnstock, "Fund")
    assert hasattr(vnstock, "Vnstock")


def test_removed_public_exports_not_in_vnstock(monkeypatch):
    """Broker, show_api, show_doc, and show_docs must not be exported from vnstock."""
    fake_vnai = types.ModuleType("vnai")

    def optimize_execution(_name=None):
        def decorator(func):
            return func

        return decorator

    fake_vnai.optimize_execution = optimize_execution
    fake_vnai.setup = lambda: None
    monkeypatch.setitem(sys.modules, "vnai", fake_vnai)

    for module_name in list(sys.modules):
        if module_name == "vnstock" or module_name.startswith("vnstock."):
            monkeypatch.delitem(sys.modules, module_name, raising=False)

    import vnstock

    assert "Broker" not in vnstock.__all__, "Broker must not be in vnstock.__all__"
    assert "show_api" not in vnstock.__all__, "show_api must not be in vnstock.__all__"
    assert "show_doc" not in vnstock.__all__, "show_doc must not be in vnstock.__all__"
    assert "show_docs" not in vnstock.__all__, (
        "show_docs must not be in vnstock.__all__"
    )


def test_removed_exports_not_in_vnstock_ui(monkeypatch):
    """Broker, show_api, and show_doc must not be exported from vnstock.ui."""
    fake_vnai = types.ModuleType("vnai")

    def optimize_execution(_name=None):
        def decorator(func):
            return func

        return decorator

    fake_vnai.optimize_execution = optimize_execution
    fake_vnai.setup = lambda: None
    monkeypatch.setitem(sys.modules, "vnai", fake_vnai)

    for module_name in list(sys.modules):
        if module_name == "vnstock" or module_name.startswith("vnstock."):
            monkeypatch.delitem(sys.modules, module_name, raising=False)

    import vnstock.ui as ui_module

    assert "Broker" not in ui_module.__all__, "Broker must not be in vnstock.ui.__all__"
    assert "show_api" not in ui_module.__all__, (
        "show_api must not be in vnstock.ui.__all__"
    )
    assert "show_doc" not in ui_module.__all__, (
        "show_doc must not be in vnstock.ui.__all__"
    )


def test_fmp_data_credentials_remain_provider_scoped(monkeypatch):
    """FMP data provider credentials must remain scoped to the FMP connector."""
    import pytest

    from vnstock.connector.fmp.config import FMPConfig

    monkeypatch.delenv("FMP_TOKEN", raising=False)
    monkeypatch.delenv("FMP_API_KEY", raising=False)

    with pytest.raises(ValueError, match="FMP API key not found"):
        FMPConfig(show_log=False)

    config = FMPConfig(api_key="direct-fmp-key", show_log=False)
    assert config.api_key == "direct-fmp-key"
