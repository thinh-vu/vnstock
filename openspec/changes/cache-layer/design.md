# Design: Cache Layer

## Architecture

```
User call → BaseUI._dispatch()
                │
                ├─ cache disabled or use_cache=False → skip to provider
                │
                ├─ Build cache_key = sha256(provider + method + sorted_kwargs)
                │
                ├─ CacheManager.get(cache_key)
                │       ├─ HIT  → return cached DataFrame/dict (deserialise)
                │       └─ MISS → continue to provider
                │
                ├─ Execute provider (existing dispatch logic)
                │
                └─ CacheManager.set(cache_key, result, ttl)
                        └─ backend: MemoryBackend | SQLiteBackend
```

## Components

### `vnstock/core/cache.py` — `CacheManager` + backends

```python
class CacheBackend(Protocol):
    def get(self, key: str) -> Optional[bytes]: ...
    def set(self, key: str, value: bytes, ttl: int) -> None: ...
    def delete(self, key: str) -> None: ...
    def clear(self) -> None: ...
    def stats(self) -> dict: ...

class MemoryBackend:
    """LRU dict with TTL check. In-process only, resets on restart."""
    # Stores {key: (value_bytes, expiry_float)}
    # Evicts oldest when max_size exceeded.

class SQLiteBackend:
    """SQLite file backend. Survives restarts. Thread-safe via WAL mode."""
    # Table: cache(key TEXT PRIMARY KEY, value BLOB, expires_at REAL)
    # Index on expires_at for fast expiry sweeps.
    # Lazy cleanup: expired rows removed on each get() and periodically on set().

class CacheManager:
    def __init__(self, config: CacheConfig): ...
    def get(self, key: str) -> Optional[Any]: ...          # deserialise from bytes
    def set(self, key: str, value: Any, ttl: int) -> None: # serialise to bytes
    def invalidate(self, key: str) -> None: ...
    def clear(self) -> None: ...
    def stats(self) -> dict: ...

def make_cache_key(provider: str, method: str, kwargs: dict) -> str:
    """SHA-256 of canonical JSON representation of (provider, method, kwargs)."""
```

**Serialisation:** `pickle` for DataFrames (fast, exact column types preserved). Non-DataFrame results (dict, list) also pickled.

### `CacheConfig` extension (`vnstock/core/settings.py`)

New fields added to existing `CacheConfig`:
```python
backend: str = "memory"    # "memory" | "sqlite"
path: str = ""             # file path for sqlite backend; "" → ~/.vnstock/cache.db
```

New env vars read by `VnstockConfig._load_from_env()`:
- `VNSTOCK_CACHE_ENABLED` → `cache.enabled` (bool)
- `VNSTOCK_CACHE_TTL` → `cache.ttl` (int, seconds)
- `VNSTOCK_CACHE_BACKEND` → `cache.backend` ("memory" | "sqlite")
- `VNSTOCK_CACHE_PATH` → `cache.path` (str, file path)
- `VNSTOCK_CACHE_MAX_SIZE` → `cache.max_size` (int)

### Module-level singleton

```python
# vnstock/core/cache.py (bottom)
from vnstock.core.settings import get_config
_cache_manager: Optional[CacheManager] = None

def get_cache_manager() -> CacheManager:
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager(get_config().cache)
    return _cache_manager
```

### `_dispatch()` integration (`vnstock/ui/_base.py`)

After step 3b (router source selection), before step 4 (multi-symbol):

```python
# Cache check
_use_cache = kwargs.pop("use_cache", None)
_call_ttl  = kwargs.pop("cache_ttl", None)
_cache_key = None

from vnstock.core.cache import get_cache_manager, make_cache_key
_cm = get_cache_manager()

if _cm.config.enabled and _use_cache is not False:
    _cache_key = make_cache_key(kwargs.get("source",""), function_name, kwargs)
    cached = _cm.get(_cache_key)
    if cached is not None:
        return cached
```

After successful result:
```python
if _cache_key is not None:
    ttl = _call_ttl if _call_ttl is not None else _cm.config.ttl
    _cm.set(_cache_key, result, ttl)
```

## Decisions

1. **pickle for serialisation** — preserves DataFrame dtypes, attrs, MultiIndex exactly. Security note: only trusted data is cached (own provider responses), so pickle is acceptable.
2. **SQLite WAL mode** — allows concurrent reads from multiple threads without blocking writers.
3. **LRU eviction in MemoryBackend** — when `max_size` is reached, oldest-inserted entry is removed.
4. **Disabled by default** — `CacheConfig.enabled = False`. Zero overhead when not used.
5. **`use_cache=False` per-call bypass** — caller can force live fetch without changing global config.
6. **`cache_ttl=<int>` per-call TTL** — caller can override TTL for a single call (e.g. `cache_ttl=3600` for daily data).
7. **No Redis** — avoids mandatory external infrastructure. Can be added as a third backend later.

## TTL Guidelines (informational, not enforced)

| Data type          | Suggested TTL |
|--------------------|---------------|
| OHLCV daily        | 86400s (1 day) |
| OHLCV intraday 1m  | 300s (5 min)  |
| Intraday tick tape | 60s           |
| Price board        | 10s           |
| Company / listing  | 3600s (1 hr)  |
| Fundamental        | 86400s        |

Default TTL of 300s in `CacheConfig` is a reasonable middle ground.
