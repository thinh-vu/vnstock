"""
Provider load-balancer router for vnstock Unified UI.

Provides round-robin source selection with per-provider cooldown on failure.
State is in-process memory only; resets on process restart.
"""

from __future__ import annotations

import threading
import time
from typing import Dict, List, Tuple


class ProviderRouter:
    """Round-robin load balancer with failure cooldown for data providers.

    Usage::

        from vnstock.core.router import router   # module-level singleton

        source = router.pick(("Market", "equity", "ohlcv"), ["KBS", "VCI", "DNSE"])
        try:
            result = dispatch(source, ...)
        except SomeProviderError:
            router.mark_failed(key, source, is_rate_limit=False)
            source = router.pick(key, providers)  # retry with next

    Design decisions:
    - In-process singleton: no file I/O, resets on restart.
    - Round-robin over healthy (non-cooldown) providers.
    - When all providers are in cooldown, pick the one expiring soonest (best-effort).
    - Thread-safe via a single lock.
    """

    COOLDOWN_SECS: float = 60.0
    RATE_LIMIT_COOLDOWN_SECS: float = 300.0

    def __init__(self) -> None:
        self._lock = threading.Lock()
        # pool_key -> current round-robin counter
        self._counters: Dict[Tuple, int] = {}
        # (pool_key, source) -> expiry timestamp (float, epoch seconds)
        self._cooldowns: Dict[Tuple, float] = {}

    def pick(self, pool_key: tuple, providers: List[str]) -> str:
        """Return the next healthy provider for *pool_key* using round-robin.

        If all providers are in cooldown, returns the one whose cooldown
        expires soonest (best-effort fallback).

        Args:
            pool_key: Hashable identifier for the pool, e.g.
                      ``("Market", "equity", "ohlcv")``.
            providers: Ordered list of provider names (e.g. ``["KBS", "VCI", "DNSE"]``).

        Returns:
            Provider name string.
        """
        if not providers:
            raise ValueError("providers list must not be empty")
        if len(providers) == 1:
            return providers[0]

        now = time.time()
        with self._lock:
            healthy = [
                p for p in providers if self._cooldowns.get((pool_key, p), 0) <= now
            ]

            if healthy:
                idx = self._counters.get(pool_key, 0) % len(healthy)
                chosen = healthy[idx]
                self._counters[pool_key] = (idx + 1) % len(healthy)
                return chosen

            # All in cooldown: pick the one expiring soonest
            best = min(
                providers,
                key=lambda p: self._cooldowns.get((pool_key, p), 0),
            )
            return best

    def mark_failed(
        self, pool_key: tuple, source: str, is_rate_limit: bool = False
    ) -> None:
        """Record a provider failure and set its cooldown window.

        Args:
            pool_key: Same key used in :meth:`pick`.
            source: Provider name that failed.
            is_rate_limit: If ``True``, use the longer rate-limit cooldown
                           (``RATE_LIMIT_COOLDOWN_SECS``).
        """
        cooldown = (
            self.RATE_LIMIT_COOLDOWN_SECS if is_rate_limit else self.COOLDOWN_SECS
        )
        expiry = time.time() + cooldown
        with self._lock:
            self._cooldowns[(pool_key, source)] = expiry

    def reset(self) -> None:
        """Clear all counters and cooldowns. Intended for testing."""
        with self._lock:
            self._counters.clear()
            self._cooldowns.clear()


# Module-level singleton — import and use this directly.
router = ProviderRouter()
