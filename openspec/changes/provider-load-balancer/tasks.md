# Tasks: Provider Load Balancer

## 1. Baseline Tests (Red)

- [x] 1.1 Create `tests/unit/core/test_provider_router.py` with failing tests: round-robin picks providers in order, cooldown skips provider, all-in-cooldown falls back to least-recently-failed, mark_failed sets cooldown, thread-safety smoke test
- [x] 1.2 Create `tests/unit/ui/test_dispatch_load_balancer.py` with failing tests: explicit `source=` bypasses router, pool entry triggers router.pick(), failover retries on simulated provider error, `df.attrs["source_used"]` is set

## 2. ProviderRouter

- [x] 2.1 Create `vnstock/core/router.py` with `ProviderRouter` class: `_counters`, `_cooldowns`, `_lock`; `COOLDOWN_SECS=60`, `RATE_LIMIT_COOLDOWN_SECS=300`
- [x] 2.2 Implement `pick(pool_key, providers) -> str`: filter expired cooldowns, round-robin on healthy subset; if all in cooldown pick soonest-to-expire
- [x] 2.3 Implement `mark_failed(pool_key, source, is_rate_limit=False)`: set cooldown expiry timestamp
- [x] 2.4 Implement `reset()` for test isolation
- [x] 2.5 Add module-level singleton `router = ProviderRouter()`

## 3. POOLS Config

- [x] 3.1 Create `vnstock/ui/_pools.py` with `POOLS` dict covering market data methods that have multi-provider support: `("Market","equity","ohlcv")`, `("Market","equity","trades")`, `("Market","equity","quote")`, `("Market","etf","ohlcv")`, `("Market","futures","ohlcv")`, `("Market","warrant","ohlcv")`, `("Market","index","ohlcv")`, flat legacy entries `("equity_market","ohlcv")`, `("equity_market","price_board")`, `("equity_market","intraday")`
- [x] 3.2 Add helper `_build_pool_key(domain_name, method_name, consumed_subdomain=None) -> tuple` to compute the pool key consistently

## 4. Wire into _dispatch()

- [x] 4.1 Import `POOLS` and `router` in `vnstock/ui/_base.py` (lazy, inside method to avoid circular imports)
- [x] 4.2 After step 3 metadata unpack: if `kwargs.get("source") is None` and pool_key in POOLS, call `router.pick()` to override `kwargs["source"]`; record `_pool_key_for_retry` and `_using_router` flag
- [x] 4.3 Wrap existing execute block (steps 4-5) in a retry loop: catch `requests.exceptions.Timeout`, `ConnectionError`, `ValueError` with HTTP status in message; call `router.mark_failed()` and retry up to `len(pool)` times; re-raise if all fail
- [x] 4.4 Add `_is_rate_limit(exc) -> bool` helper: check for "429" or "rate limit" in exception message/args
- [x] 4.5 After successful return of DataFrame, set `result.attrs["source_used"] = kwargs["source"]` when router was used

## 5. Documentation

- [x] 5.1 Add docstring to `ProviderRouter` explaining round-robin + cooldown design
- [x] 5.2 Add `# load-balancing` comment block in `_pools.py` listing how to add a new provider to a pool
- [x] 5.3 Update `CHANGELOG.md` with load-balancer entry
- [x] 5.4 Update `AGENTS.md` to note the router and POOLS config

## 6. Verification

- [x] 6.1 Run `PYTHONPATH=. pytest tests/unit/core/test_provider_router.py tests/unit/ui/test_dispatch_load_balancer.py -v` — all pass
- [x] 6.2 Run `python -m ruff check vnstock/core/router.py vnstock/ui/_pools.py vnstock/ui/_base.py` — zero errors
- [x] 6.3 Run `python -m ruff format --check vnstock/core/router.py vnstock/ui/_pools.py vnstock/ui/_base.py`
- [x] 6.4 Run `python -m compileall -q vnstock/core/router.py vnstock/ui/_pools.py vnstock/ui/_base.py`
- [x] 6.5 Manual smoke: `PYTHONPATH=. python -c "from vnstock.core.router import router; print(router.pick(('Market','equity','ohlcv'), ['KBS','VCI','DNSE']))"` — prints a provider name
