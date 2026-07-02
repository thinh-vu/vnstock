"""
Cache layer for vnstock data providers.

Provides a configurable cache that stores provider responses to avoid
redundant HTTP requests. Backends: memory (in-process) and SQLite (persistent).

Configuration via CacheConfig (vnstock/core/settings.py) or environment variables:
    VNSTOCK_CACHE_ENABLED   : "true"/"false" (default: false)
    VNSTOCK_CACHE_BACKEND   : "memory" | "sqlite" (default: memory)
    VNSTOCK_CACHE_TTL       : integer seconds (default: 300)
    VNSTOCK_CACHE_MAX_SIZE  : max entries before eviction (default: 100)
    VNSTOCK_CACHE_PATH      : file path for sqlite backend (default: ~/.vnstock/cache.db)

Usage::

    from vnstock.core.cache import get_cache_manager, make_cache_key

    cm = get_cache_manager()
    key = make_cache_key("KBS", "history", {"start": "2024-01-01", "end": "2024-12-31"})
    result = cm.get(key)
    if result is None:
        result = fetch_from_provider(...)
        cm.set(key, result, ttl=300)
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


def make_cache_key(provider: str, method: str, kwargs: dict) -> str:
    """Return a deterministic SHA-256 hex digest for the given call parameters.

    Args:
        provider: Provider/source name (e.g. ``"KBS"``).
        method:   Function name (e.g. ``"history"``).
        kwargs:   Call keyword arguments; sorted by key before hashing.

    Returns:
        64-character lowercase hex string.
    """
    payload = json.dumps(
        {"provider": provider, "method": method, "kwargs": kwargs},
        sort_keys=True,
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


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
