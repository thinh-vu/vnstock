# Proposal: Cache Layer

## Problem

Every call to `Quote.history()`, `Quote.intraday()`, `Trading.price_board()`, or any other data method hits a live provider HTTP endpoint. This causes:
- Unnecessary latency for repeated identical queries (same symbol, same date range, same interval)
- Increased rate-limit exposure on provider APIs
- Inability to work offline or in test environments without live credentials

## Proposed Change

Add a configurable cache layer that stores provider responses and serves them on subsequent identical calls without re-fetching from the network.

**Key design decisions:**
- **Storage backends:** memory (in-process dict, default) and SQLite (file-based, survives restarts). Redis is excluded to avoid adding a mandatory external dependency.
- **Configurable via `CacheConfig`** (already defined in `vnstock/core/settings.py`): `enabled`, `ttl`, `max_size`, plus new `backend` (`"memory"` | `"sqlite"`) and `path` (file path for SQLite).
- **Cache key** = deterministic hash of `(provider, method, serialized_kwargs)`.
- **TTL enforcement:** entries expire after `CacheConfig.ttl` seconds (default 300s).
- **Integration point:** `BaseUI._dispatch()` wraps the execute step — check cache before calling provider, write to cache on success.
- **Bypass:** callers can pass `use_cache=False` or set `cache_ttl=0` per call to force a live fetch.

## Scope

- **In scope:** `CacheManager` class, memory backend, SQLite backend, `CacheConfig` extension, `_dispatch()` integration, env-var config, unit tests.
- **Out of scope:** Redis, distributed invalidation, cross-process invalidation, automatic cache warm-up.

## Breaking Changes

None. Cache is disabled by default (`enabled=False`). No public API changes.
