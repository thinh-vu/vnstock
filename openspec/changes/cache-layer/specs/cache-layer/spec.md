# Spec: Cache Layer

## Requirements

### REQ-1: Cache is disabled by default
Out of the box, `CacheConfig.enabled = False`. No caching, no overhead, no behaviour change from current.

**Scenario:** Fresh install with no env vars set — all provider calls hit the network as before.

### REQ-2: Enable via config or env var
Cache is enabled by setting `CacheConfig.enabled = True` programmatically, or by setting `VNSTOCK_CACHE_ENABLED=true` env var before import.

**Scenario:** `os.environ["VNSTOCK_CACHE_ENABLED"] = "true"` before importing vnstock → subsequent dispatch calls check the cache.

### REQ-3: Memory backend (default)
When `backend = "memory"`, responses are stored in an in-process LRU dict. State is lost on process restart. Maximum entries capped by `max_size`.

**Scenario:** Two identical `Quote.history()` calls in the same process — second call returns without network request.

### REQ-4: SQLite backend (persistent)
When `backend = "sqlite"`, responses are stored in a SQLite file at `path` (default `~/.vnstock/cache.db`). Survives process restarts. Thread-safe via WAL mode.

**Scenario:** After process restart with `VNSTOCK_CACHE_BACKEND=sqlite`, a previously cached daily OHLCV query returns from disk within TTL.

### REQ-5: TTL expiry
Cached entries expire after `ttl` seconds (default 300). Expired entries are treated as misses and the provider is called.

**Scenario:** An entry cached with TTL=10 is not returned after 11 seconds.

### REQ-6: Per-call bypass
Caller can pass `use_cache=False` to force a live provider fetch, ignoring the cache for that call. Result is NOT written to cache.

**Scenario:** `Market().equity.ohlcv(symbol="VCB", use_cache=False)` always hits the network.

### REQ-7: Per-call TTL override
Caller can pass `cache_ttl=<seconds>` to override the global TTL for that specific call.

**Scenario:** `Market().equity.ohlcv(symbol="VCB", cache_ttl=86400)` caches the result for 24 hours.

### REQ-8: Cache key is deterministic and collision-free
The same `(provider, method, kwargs)` always produces the same key. Different args produce different keys. Key is a hex digest (SHA-256).

**Scenario:** `history(start="2024-01-01", end="2024-12-31")` and `history(start="2024-06-01", end="2024-12-31")` produce different cache keys.

### REQ-9: `source_used` and `df.attrs` are preserved
When a result is served from cache, `df.attrs["source_used"]` (set by the load-balancer) is preserved as stored.

### REQ-10: `CacheManager.clear()` removes all entries
`get_cache_manager().clear()` empties the entire cache store for the active backend.

### REQ-11: `CacheManager.stats()` returns backend statistics
Returns a dict with at least `{"backend": str, "entries": int, "enabled": bool}`.

### REQ-12: No new mandatory dependencies
Memory backend requires only stdlib. SQLite backend requires only `sqlite3` (stdlib). No `redis`, `diskcache`, or third-party packages.
