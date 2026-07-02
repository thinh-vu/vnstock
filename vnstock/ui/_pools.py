"""
Provider pool configuration for the vnstock load-balancer router.

Each key is a pool identifier matching the (domain, [subdomain,] method) pattern
used by BaseUI._dispatch(). The value is an ordered list of providers that support
that capability; the router will round-robin over healthy entries.

To add a new provider to a pool, append its source string to the relevant list.
To add a new pool for a new method, add a new entry following the pattern below.

Only methods with >= 2 providers benefit from load-balancing.  Single-provider
entries are allowed for completeness but behave as passthrough.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

# Pool key type: tuple of (domain, [subdomain,] method) strings
PoolKey = Tuple[str, ...]

POOLS: Dict[PoolKey, List[str]] = {
    # ── Market / Unified UI nested entries ────────────────────────────────────
    # key = (domain, subdomain, method)
    ("Market", "equity", "ohlcv"): ["KBS", "VCI", "DNSE"],
    ("Market", "equity", "trades"): ["KBS", "VCI", "DNSE"],
    ("Market", "equity", "quote"): ["KBS", "VCI", "DNSE"],
    ("Market", "etf", "ohlcv"): ["KBS", "VCI"],
    ("Market", "futures", "ohlcv"): ["KBS", "DNSE"],
    ("Market", "warrant", "ohlcv"): ["KBS", "VCI"],
    ("Market", "index", "ohlcv"): ["KBS", "VCI"],
    # ── Legacy flat domain entries ─────────────────────────────────────────────
    # key = (domain, method)
    ("equity_market", "ohlcv"): ["KBS", "VCI", "DNSE"],
    ("equity_market", "price_board"): ["KBS", "VCI", "DNSE"],
    ("equity_market", "intraday"): ["KBS", "VCI", "DNSE"],
}


def _build_pool_key(
    domain_name: str,
    method_name: str,
    consumed_subdomain: str | None = None,
) -> PoolKey:
    """Build a POOLS lookup key from dispatch context.

    Args:
        domain_name: Top-level MAP domain (e.g. ``"Market"``, ``"equity_market"``).
        method_name: Method name within the domain (e.g. ``"equity"``, ``"ohlcv"``).
        consumed_subdomain: When the dispatch consumed a nested subdomain key from
            args (e.g. the ``"ohlcv"`` inside ``Market -> equity -> ohlcv``), pass
            it here so the key becomes ``(domain, method, subdomain)``.

    Returns:
        Tuple used as POOLS dict key.
    """
    if consumed_subdomain is not None:
        return (domain_name, method_name, consumed_subdomain)
    return (domain_name, method_name)
