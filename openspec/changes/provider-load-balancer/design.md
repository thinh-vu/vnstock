# Design: Provider Load Balancer

## Architecture

```
BaseUI._dispatch(domain, method, *args, **kwargs)
    │
    ├─ Caller passed source= explicitly → skip router, use as-is (backward compat)
    │
    ├─ Build pool_key = (domain, method)  [or (domain, subdomain, method)]
    │       │
    │       ├─ pool_key not in POOLS → use MAP default source (unchanged behavior)
    │       │
    │       └─ pool_key in POOLS
    │               │
    │               └─ router.pick(pool_key) → source string
    │                       (round-robin over healthy providers)
    │
    ├─ Execute dispatch with selected source
    │
    ├─ SUCCESS → return result; set df.attrs["source_used"] = source
    │
    └─ FAILURE (Timeout / ConnectionError / HTTP 5xx / HTTP 429)
            │
            ├─ router.mark_failed(pool_key, source, is_rate_limit)
            │
            └─ retry with router.pick(pool_key) → next provider
                    (max len(pool) attempts total)
```

## Components

### `vnstock/core/router.py`

```python
class ProviderRouter:
    COOLDOWN_SECS = 60           # for timeout/5xx
    RATE_LIMIT_COOLDOWN_SECS = 300  # for HTTP 429

    def pick(self, pool_key, providers) -> str: ...
    def mark_failed(self, pool_key, source, is_rate_limit=False) -> None: ...
    def reset(self) -> None: ...  # for testing

router = ProviderRouter()  # module-level singleton
```

- `_counters: dict` — `pool_key -> int` round-robin index
- `_cooldowns: dict` — `(pool_key, source) -> float` expiry timestamp
- `threading.Lock` for thread safety
- `pick()`: filters out sources whose cooldown has not expired, then selects `_counters[pool_key] % len(active)` and increments counter
- If all sources are in cooldown: use the one whose cooldown expires soonest (best-effort)

### `vnstock/ui/_pools.py`

Declares multi-provider pools. Only entries with ≥ 2 providers are meaningful, but single-provider entries are allowed (router becomes passthrough).

```python
POOLS = {
    ("Market", "equity", "ohlcv"):   ["KBS", "VCI", "DNSE"],
    ("Market", "equity", "trades"):  ["KBS", "VCI", "DNSE"],
    ("Market", "equity", "quote"):   ["KBS", "VCI", "DNSE"],
    ("Market", "etf",    "ohlcv"):   ["KBS", "VCI"],
    ("Market", "futures","ohlcv"):   ["KBS", "DNSE"],
    ("Market", "warrant","ohlcv"):   ["KBS", "VCI"],
    ("Market", "index",  "ohlcv"):   ["KBS", "VCI"],
    ("equity_market", "ohlcv"):      ["KBS", "VCI", "DNSE"],
    ("equity_market", "price_board"):["KBS", "VCI", "DNSE"],
    ("equity_market", "intraday"):   ["KBS", "VCI", "DNSE"],
}
```

### `_dispatch()` changes

After step 3 (metadata unpack) and before step 4 (multi-symbol handling):

```python
# 3b. Load-balancer source override
from vnstock.ui._pools import POOLS
from vnstock.core.router import router

if kwargs.get("source") is None:  # caller did not override
    pool_key = _build_pool_key(domain_name, method_name, args)
    if pool_key in POOLS:
        kwargs["source"] = router.pick(pool_key, POOLS[pool_key])
        _pool_key_for_retry = pool_key
```

Retry wrapper wraps the existing execute block:

```python
_attempts = 0
_max_attempts = len(POOLS.get(_pool_key_for_retry, [None]))
while _attempts < max(_max_attempts, 1):
    try:
        result = <existing dispatch code>
        if isinstance(result, pd.DataFrame) and _pool_key_for_retry:
            result.attrs["source_used"] = kwargs["source"]
        return result
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError,
            ProviderError) as e:
        if _pool_key_for_retry:
            is_rl = _is_rate_limit(e)
            router.mark_failed(_pool_key_for_retry, kwargs["source"], is_rl)
            kwargs["source"] = router.pick(_pool_key_for_retry, POOLS[_pool_key_for_retry])
        _attempts += 1
        if _attempts >= _max_attempts:
            raise
```

## Error Classification

| Exception / HTTP | Cooldown | `is_rate_limit` |
|---|---|---|
| `requests.Timeout` | 60s | False |
| `requests.ConnectionError` | 60s | False |
| HTTP 429 (string match in exception) | 300s | True |
| HTTP 5xx (string match in exception) | 60s | False |

Detection: providers currently propagate errors via `raise ValueError(...)` or `raise requests.HTTPError(...)`. We match on exception type + message substring.

## Decisions

1. **In-process singleton** — simpler, sufficient for notebook / single-process use. No file I/O.
2. **Caller `source=` bypasses router** — backward compatibility, allows explicit override.
3. **`df.attrs["source_used"]`** — non-breaking metadata, standard pandas mechanism.
4. **No new public kwargs** — completely transparent to existing callers.
5. **Pool key building** — `(domain_name, method_name)` for flat MAP entries; `(domain_name, subdomain, method_name)` for nested entries (detected from whether `args[0]` was consumed as subdomain).
