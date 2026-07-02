"""
Cache layer for vnstock data providers.

Provides a configurable cache that stores provider responses to avoid
redundant HTTP requests. Backends: memory (in-process) and SQLite (persistent).

Configuration via CacheConfig (vnstock/core/settings.py) or environment variables:
    VNSTOCK_CACHE_ENABLED   : "true"/"false" (default: true)
    VNSTOCK_CACHE_BACKEND   : "memory" | "sqlite" (default: memory)
    VNSTOCK_CACHE_TTL       : integer seconds (default: 300)
    VNSTOCK_CACHE_MAX_SIZE  : max entries before eviction (default: 100)
    VNSTOCK_CACHE_PATH      : file path for sqlite backend (default: ~/.vnstock/cache.db)

Default TTL by data category (applied automatically by BaseUI._dispatch):
    Market data (price, ohlcv, intraday, trades)  : 3600 s  (1 hour)
    Reference / listing / company snapshot         : 86400 s (24 hours)
    Fundamental (financials, ratios)               : 86400 s (24 hours)
    Fund data                                      : 14400 s (4 hours)
    Retail / gold / forex                          : 3600 s  (1 hour)
    Anything else                                  : global config TTL

Usage::

    from vnstock.core.cache import get_cache_manager, make_cache_key, get_default_ttl

    cm = get_cache_manager()
    key = make_cache_key("KBS", "history", {"start": "2024-01-01"}, domain="Market")
    ttl = get_default_ttl("Market", "equity", "ohlcv")
    result = cm.get(key)
    if result is None:
        result = fetch_from_provider(...)
        cm.set(key, result, ttl=ttl)
"""

from __future__ import annotations

import hashlib
import json
import os
import pickle
import sqlite3
import threading
import time
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from vnstock.core.settings import CacheConfig


# ---------------------------------------------------------------------------
# Cache key helper
# ---------------------------------------------------------------------------


def make_cache_key(
    provider: str,
    method: str,
    kwargs: dict,
    *,
    domain: str = "",
    subdomain: str = "",
) -> str:
    """Return a deterministic SHA-256 hex digest scoped by domain + provider.

    Including ``domain`` and ``subdomain`` prevents key collisions between
    different data categories that happen to use the same method name
    (e.g. ``Market.equity.ohlcv`` vs ``Fundamental.equity.balance_sheet``
    both route through ``Quote.ohlcv``).

    Args:
        provider:  Provider/source name (e.g. ``"KBS"``).
        method:    Function name (e.g. ``"ohlcv"``).
        kwargs:    Call keyword arguments; sorted by key before hashing.
        domain:    Top-level UI domain (e.g. ``"Market"``).  Optional.
        subdomain: Sub-domain within the domain (e.g. ``"equity"``).  Optional.

    Returns:
        64-character lowercase hex string.
    """
    payload = json.dumps(
        {
            "domain": domain,
            "subdomain": subdomain,
            "provider": provider,
            "method": method,
            "kwargs": kwargs,
        },
        sort_keys=True,
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


# ---------------------------------------------------------------------------
# Smart TTL table
# ---------------------------------------------------------------------------

# Market data: live prices change every few seconds; 1-hour cache balances
# freshness vs HTTP load for backtesting / batch workflows.
_TTL_MARKET = 3600  # 1 hour

# Reference / listing / company: changes daily at most (new listings, filings).
_TTL_REFERENCE = 86400  # 24 hours

# Fundamental data: quarterly/annual; safe to cache for a full day.
_TTL_FUNDAMENTAL = 86400  # 24 hours

# Fund NAV / holdings: published daily, typically after market close.
_TTL_FUND = 14400  # 4 hours

# Retail (gold spot, exchange rates): hourly updates.
_TTL_RETAIL = 3600  # 1 hour

# Intraday tick trades: cache for 1 hour (same as market data).
_TTL_INTRADAY = 3600  # 1 hour

# Methods considered "market / real-time price" data
_MARKET_METHODS = frozenset(
    {"ohlcv", "history", "quote", "price_board", "price", "short", "full"}
)
# Methods considered "intraday tick" data
_INTRADAY_METHODS = frozenset({"intraday", "trades"})


def get_default_ttl(domain: str, subdomain: str = "", method: str = "") -> int:
    """Return the recommended cache TTL in seconds for the given data category.

    TTL hierarchy (highest specificity wins):
    1. Intraday tick methods → 5 min
    2. Market / price methods → 1 hour
    3. ``Market`` top-level domain → 1 hour
    4. ``Fundamental`` domain → 24 hours
    5. ``Reference`` domain → 24 hours
    6. ``fund`` subdomain → 4 hours
    7. ``Retail`` domain → 1 hour
    8. Default (unknown) → -1 (caller should fall back to global config)

    Args:
        domain:    Top-level UI domain name (e.g. ``"Market"``, ``"Reference"``).
        subdomain: Sub-domain within the domain (e.g. ``"equity"``).
        method:    Leaf method name (e.g. ``"ohlcv"``, ``"intraday"``).

    Returns:
        TTL in seconds, or ``-1`` if no specific rule matches (use global config).
    """
    m = method.lower()

    if m in _INTRADAY_METHODS:
        return _TTL_INTRADAY

    if m in _MARKET_METHODS:
        return _TTL_MARKET

    d = domain.lower()
    s = subdomain.lower()

    # Subdomain checks first (more specific than domain)
    if s == "fund" or d == "fund":
        return _TTL_FUND

    if d == "market":
        return _TTL_MARKET

    if d in ("reference", "listing"):
        return _TTL_REFERENCE

    if d == "fundamental":
        return _TTL_FUNDAMENTAL

    if d == "retail":
        return _TTL_RETAIL

    return -1  # no rule matched — caller falls back to global config


# ---------------------------------------------------------------------------
# Backend Protocol / implementations
# ---------------------------------------------------------------------------


class MemoryBackend:
    """In-process LRU cache with TTL.

    Stores ``{key: (pickled_bytes, expiry_float)}`` in an ordered dict.
    When ``max_size`` is exceeded, the oldest entry is evicted.
    Thread-safe via a single lock.
    """

    def __init__(self, max_size: int = 100) -> None:
        from collections import OrderedDict

        self._store: OrderedDict[str, tuple[bytes, float]] = OrderedDict()
        self._max_size = max_size
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[bytes]:
        with self._lock:
            if key not in self._store:
                return None
            value, expiry = self._store[key]
            if time.time() > expiry:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: bytes, ttl: int) -> None:
        expiry = time.time() + ttl
        with self._lock:
            if key in self._store:
                del self._store[key]
            self._store[key] = (value, expiry)
            # Evict oldest when over capacity
            while len(self._store) > self._max_size:
                self._store.popitem(last=False)

    def delete(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def stats(self) -> dict:
        with self._lock:
            now = time.time()
            live = sum(1 for _, (_, exp) in self._store.items() if exp > now)
            return {
                "backend": "memory",
                "entries": live,
                "total_stored": len(self._store),
                "max_size": self._max_size,
            }


class SQLiteBackend:
    """Persistent SQLite cache backend with TTL.

    Stores serialised blobs in ``cache(key, value, expires_at)`` table.
    Uses WAL journal mode for concurrent read safety.
    Lazy expiry sweep: expired rows removed on each ``get()`` and every 100
    ``set()`` calls.
    Thread-safe via a single lock.
    """

    _SWEEP_INTERVAL = 100  # sweep expired rows every N set() calls

    def __init__(self, path: str = "", max_size: int = 100) -> None:
        if not path:
            path = os.path.join(os.path.expanduser("~"), ".vnstock", "cache.db")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self._path = path
        self._max_size = max_size
        self._lock = threading.Lock()
        self._set_count = 0
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_db(self) -> None:
        with self._lock:
            conn = self._connect()
            conn.execute(
                "CREATE TABLE IF NOT EXISTS cache "
                "(key TEXT PRIMARY KEY, value BLOB, expires_at REAL)"
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_expires ON cache(expires_at)")
            conn.commit()
            conn.close()

    def get(self, key: str) -> Optional[bytes]:
        now = time.time()
        with self._lock:
            conn = self._connect()
            try:
                cur = conn.execute(
                    "SELECT value, expires_at FROM cache WHERE key = ?", (key,)
                )
                row = cur.fetchone()
                if row is None:
                    return None
                value, expires_at = row
                if now > expires_at:
                    conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                    conn.commit()
                    return None
                return bytes(value)
            finally:
                conn.close()

    def set(self, key: str, value: bytes, ttl: int) -> None:
        expiry = time.time() + ttl
        with self._lock:
            conn = self._connect()
            try:
                conn.execute(
                    "INSERT OR REPLACE INTO cache(key, value, expires_at) VALUES (?,?,?)",
                    (key, value, expiry),
                )
                conn.commit()
                self._set_count += 1
                # Periodic sweep and eviction
                if self._set_count % self._SWEEP_INTERVAL == 0:
                    conn.execute(
                        "DELETE FROM cache WHERE expires_at <= ?", (time.time(),)
                    )
                    # Evict oldest if still over max_size
                    conn.execute(
                        "DELETE FROM cache WHERE key IN "
                        "(SELECT key FROM cache ORDER BY expires_at ASC "
                        "LIMIT MAX(0, (SELECT COUNT(*) FROM cache) - ?))",
                        (self._max_size,),
                    )
                    conn.commit()
            finally:
                conn.close()

    def delete(self, key: str) -> None:
        with self._lock:
            conn = self._connect()
            conn.execute("DELETE FROM cache WHERE key = ?", (key,))
            conn.commit()
            conn.close()

    def clear(self) -> None:
        with self._lock:
            conn = self._connect()
            conn.execute("DELETE FROM cache")
            conn.commit()
            conn.close()

    def stats(self) -> dict:
        with self._lock:
            conn = self._connect()
            try:
                now = time.time()
                row = conn.execute(
                    "SELECT COUNT(*) FROM cache WHERE expires_at > ?", (now,)
                ).fetchone()
                live = row[0] if row else 0
                return {
                    "backend": "sqlite",
                    "entries": live,
                    "path": self._path,
                }
            finally:
                conn.close()


# ---------------------------------------------------------------------------
# CacheManager
# ---------------------------------------------------------------------------


class CacheManager:
    """High-level cache manager that wraps a backend with pickle serialisation.

    Usage::

        from vnstock.core.cache import get_cache_manager
        cm = get_cache_manager()
        result = cm.get(key)         # returns deserialized object or None
        cm.set(key, dataframe, 300)  # stores for 300s
        cm.clear()                   # flush all entries
        cm.stats()                   # {"backend": "memory", "entries": 5, ...}
    """

    def __init__(self, config: "CacheConfig") -> None:
        self.config = config
        if config.backend == "sqlite":
            self._backend: MemoryBackend | SQLiteBackend = SQLiteBackend(
                path=config.path, max_size=config.max_size
            )
        else:
            self._backend = MemoryBackend(max_size=config.max_size)

    def get(self, key: str) -> Optional[Any]:
        """Return cached value or ``None`` if disabled / missing / expired."""
        if not self.config.enabled:
            return None
        raw = self._backend.get(key)
        if raw is None:
            return None
        try:
            return pickle.loads(raw)  # noqa: S301 — trusted own data
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl: int) -> None:
        """Serialise and store *value* with the given *ttl* in seconds.

        Does nothing when cache is disabled.
        """
        if not self.config.enabled:
            return
        try:
            raw = pickle.dumps(value)
        except Exception:
            return
        self._backend.set(key, raw, ttl)

    def invalidate(self, key: str) -> None:
        """Remove a specific entry by key."""
        self._backend.delete(key)

    def clear(self) -> None:
        """Remove all cached entries."""
        self._backend.clear()

    def stats(self) -> dict:
        """Return backend statistics dict."""
        s = self._backend.stats()
        s["enabled"] = self.config.enabled
        s["ttl"] = self.config.ttl
        return s


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_cache_manager: Optional[CacheManager] = None
_cache_lock = threading.Lock()


def get_cache_manager() -> CacheManager:
    """Return the global CacheManager singleton (lazy init from global config)."""
    global _cache_manager
    if _cache_manager is None:
        with _cache_lock:
            if _cache_manager is None:
                from vnstock.core.settings import get_config

                _cache_manager = CacheManager(get_config().cache)
    return _cache_manager


def reset_cache_manager() -> None:
    """Reset the global singleton (primarily for testing)."""
    global _cache_manager
    with _cache_lock:
        _cache_manager = None
