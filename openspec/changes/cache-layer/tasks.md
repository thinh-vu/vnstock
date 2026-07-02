# Tasks: Cache Layer

## 1. Baseline Tests (Red)

- [x] 1.1 Create `tests/unit/core/test_cache_manager.py` with failing tests: `MemoryBackend` get/set/ttl/eviction, `SQLiteBackend` get/set/ttl/persist, `make_cache_key` determinism and collision, `CacheManager` disabled → no caching, `CacheManager.clear()`, `CacheManager.stats()`
- [x] 1.2 Create `tests/unit/ui/test_dispatch_cache.py` with failing tests: cache HIT skips provider call, cache MISS calls provider and stores result, `use_cache=False` bypasses cache, `cache_ttl=<n>` overrides TTL, cache disabled globally → no caching

## 2. `CacheConfig` Extension

- [x] 2.1 Add `backend` and `path` fields to `CacheConfig`
- [x] 2.2 Add env var reading in `VnstockConfig._load_from_env()`
- [x] 2.3 Update `to_dict()` and `from_dict()`

## 3. `CacheManager` Implementation

- [x] 3.1 Create `vnstock/core/cache.py` with `CacheBackend` Protocol interface (`get`, `set`, `delete`, `clear`, `stats`)
- [x] 3.2 Implement `MemoryBackend`: `{key: (pickled_bytes, expiry_float)}` dict; LRU eviction when `max_size` exceeded; TTL check on `get()`; `threading.Lock` for thread safety
- [x] 3.3 Implement `SQLiteBackend`: `~/.vnstock/cache.db` default path; table `cache(key TEXT PRIMARY KEY, value BLOB, expires_at REAL)`; WAL journal mode; lazy expiry sweep (delete expired on `get()` and on every 100th `set()`); `threading.Lock`
- [x] 3.4 Implement `make_cache_key(provider, method, kwargs) -> str`: sort kwargs by key, `json.dumps` canonical form, `hashlib.sha256(...).hexdigest()`
- [x] 3.5 Implement `CacheManager(config)`: selects backend by `config.backend`; `get()` deserialises with `pickle.loads`; `set()` serialises with `pickle.dumps`; `clear()` and `stats()` delegate to backend
- [x] 3.6 Add module-level singleton `get_cache_manager() -> CacheManager` (lazy init from `get_config().cache`)

## 4. Wire into `_dispatch()`

- [x] 4.1 In `BaseUI._dispatch()`: pop `use_cache` and `cache_ttl` from kwargs before processing (so they don't leak into provider calls)
- [x] 4.2 After router source selection (step 3b), before multi-symbol handling (step 4): check `get_cache_manager()` if enabled; return cached result on HIT
- [x] 4.3 After successful `_execute_dispatch()`: write result to cache with appropriate TTL (per-call `cache_ttl` takes priority over global `config.ttl`)
- [x] 4.4 Ensure `use_cache=False` result is NOT written to cache

## 5. Documentation

- [x] 5.1 Add docstring to `CacheManager` with usage example and env var reference
- [x] 5.2 Add `# cache configuration` comment block in `CacheConfig` listing all env vars
- [x] 5.3 Update `CHANGELOG.md` with cache layer entry
- [x] 5.4 Update `AGENTS.md` to note `vnstock/core/cache.py` and `CacheConfig` extension

## 6. Verification

- [x] 6.1 Run `PYTHONPATH=. pytest tests/unit/core/test_cache_manager.py tests/unit/ui/test_dispatch_cache.py -v` — all pass
- [x] 6.2 Run `python -m ruff check vnstock/core/cache.py vnstock/core/settings.py vnstock/ui/_base.py` — zero errors
- [x] 6.3 Run `python -m ruff format --check vnstock/core/cache.py vnstock/core/settings.py vnstock/ui/_base.py`
- [x] 6.4 Run `python -m compileall -q vnstock/core/cache.py`
- [x] 6.5 Smoke test: `PYTHONPATH=. python -c "from vnstock.core.cache import get_cache_manager; m = get_cache_manager(); print(m.stats())"`
