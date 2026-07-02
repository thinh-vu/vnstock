"""Compatibility helpers for the flat vnstock access model."""

from __future__ import annotations

from typing import Any

_OPEN_ACCESS_STATUS = {"access_model": "open", "registration_required": False}
_OPEN_ACCESS_MESSAGE = (
    "vnstock registration is no longer required; using flat open access model."
)


def register_user(api_key: str | None = None) -> bool:
    """
    Compatibility shim for older code that called user registration.

    The flat access model does not register vnstock users or persist package-level
    keys. The optional ``api_key`` argument is accepted and ignored so existing
    imports and notebooks can continue without side effects.
    """
    _ = api_key
    print(_OPEN_ACCESS_MESSAGE)
    return True


def change_api_key(api_key: str) -> bool:
    """
    Compatibility shim for older code that changed package-level user keys.

    Provider-specific credentials should be passed to the relevant connector;
    this helper no longer stores keys or changes package access behavior.
    """
    _ = api_key
    print(_OPEN_ACCESS_MESSAGE)
    return True


def check_status() -> dict[str, Any]:
    """Return the flat package access status without remote access checks."""
    print(_OPEN_ACCESS_MESSAGE)
    return _OPEN_ACCESS_STATUS.copy()
