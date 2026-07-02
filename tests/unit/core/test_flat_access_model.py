import importlib
import sys
import types

import pytest


def test_import_vnstock_without_user_key_does_not_initialize_access_control(
    monkeypatch, capsys
):
    """Importing vnstock must not initialize user registration or tier state."""
    monkeypatch.delenv("VNSTOCK_API_KEY", raising=False)

    calls = []
    fake_vnai = types.ModuleType("vnai")

    def optimize_execution(_name=None):
        def decorator(func):
            return func

        return decorator

    def setup():
        calls.append("setup")

    fake_vnai.optimize_execution = optimize_execution
    fake_vnai.setup = setup
    monkeypatch.setitem(sys.modules, "vnai", fake_vnai)

    for module_name in list(sys.modules):
        if module_name == "vnstock" or module_name.startswith("vnstock."):
            monkeypatch.delitem(sys.modules, module_name, raising=False)

    import vnstock  # noqa: F401

    output = capsys.readouterr().out
    assert calls == []
    assert "VNSTOCK_API_KEY" not in output
    assert "Tier" not in output
    assert "Guest" not in output
    assert "Community" not in output
    assert "Sponsor" not in output


def test_legacy_auth_helpers_are_inert(monkeypatch, capsys):
    """Legacy helpers stay importable but no longer persist keys or query tiers."""
    fake_vnai = types.ModuleType("vnai")

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("vnai access-control API must not be called")

    fake_vnai.setup_api_key = fail_if_called
    fake_vnai.check_api_key_status = fail_if_called
    monkeypatch.setitem(sys.modules, "vnai", fake_vnai)

    from vnstock.core.utils.auth import change_api_key, check_status, register_user

    assert register_user(api_key="existing-system-key") is True
    assert change_api_key("another-existing-system-key") is True

    status = check_status()
    output = capsys.readouterr().out

    assert status == {"access_model": "open", "registration_required": False}
    assert "registration is no longer required" in output
    assert "Tier" not in output
    assert "Guest" not in output
    assert "Community" not in output
    assert "Sponsor" not in output


def test_unified_ui_dispatch_ignores_sponsor_package(monkeypatch):
    """Unified UI dispatch must use native registry entries only."""
    import importlib.util

    from vnstock.ui._base import BaseUI
    from vnstock.ui._registry import MAP

    native_module = types.ModuleType("vnstock.flat_native_test")
    native_module.open_data = lambda: "native"

    sponsor_root = types.ModuleType("vnstock_data")
    sponsor_ui = types.ModuleType("vnstock_data.ui")
    sponsor_reference = types.ModuleType("vnstock_data.ui.reference")

    class SponsorClass:
        def open_data(self):
            return "sponsor"

    sponsor_reference.BaseUI = SponsorClass

    real_find_spec = importlib.util.find_spec

    def find_spec(name, *args, **kwargs):
        if name == "vnstock_data":
            return object()
        return real_find_spec(name, *args, **kwargs)

    monkeypatch.setitem(sys.modules, "vnstock.flat_native_test", native_module)
    monkeypatch.setitem(sys.modules, "vnstock_data", sponsor_root)
    monkeypatch.setitem(sys.modules, "vnstock_data.ui", sponsor_ui)
    monkeypatch.setitem(sys.modules, "vnstock_data.ui.reference", sponsor_reference)
    monkeypatch.setattr(importlib.util, "find_spec", find_spec)
    monkeypatch.setitem(
        MAP,
        "company",
        {"open_data": ("api", "flat_native_test", None, "open_data", None)},
    )

    assert BaseUI()._dispatch("company", "open_data") == "native"


def test_fmp_credentials_are_provider_scoped(monkeypatch):
    """External provider credentials must not use vnstock user registration keys."""
    from vnstock.connector.fmp.config import FMPConfig

    monkeypatch.setenv("VNSTOCK_API_KEY", "vnstock-user-key")
    monkeypatch.delenv("FMP_TOKEN", raising=False)
    monkeypatch.delenv("FMP_API_KEY", raising=False)

    with pytest.raises(ValueError, match="FMP API key not found"):
        FMPConfig(show_log=False)

    config = FMPConfig(api_key="direct-fmp-key", show_log=False)

    assert config.api_key == "direct-fmp-key"


def test_dnse_connector_removed():
    """DNSE broker connector no longer provides a Trade class."""

    import pytest

    with pytest.raises((ImportError, AttributeError)):
        trade_module = importlib.import_module("vnstock.connector.dnse.trade")
        trade_module.Trade  # noqa: B018


def test_notification_module_removed(monkeypatch):
    """vnstock.bot.notify no longer provides a Messenger class."""
    import pytest

    with pytest.raises(ImportError):
        from vnstock.bot.notify import Messenger  # noqa: F401
