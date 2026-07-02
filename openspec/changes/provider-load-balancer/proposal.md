# Proposal: Provider Load Balancer

## Problem

Source selection in the Unified UI is currently static: every MAP entry hardcodes a single provider (e.g. `"KBS"`). When multiple providers support the same capability (OHLCV, intraday ticks, price board), the user gets no benefit from redundancy — one provider outage or rate-limit means the call fails even though alternatives exist.

## Proposed Change

Add automatic, transparent provider selection using round-robin load balancing with failover:

- A `ProviderRouter` singleton (`vnstock/core/router.py`) tracks a round-robin counter and per-provider cooldown state (in-process memory only).
- A `POOLS` config (`vnstock/ui/_pools.py`) declares which providers support each `(domain, method)` key.
- `BaseUI._dispatch()` consults the router before instantiating a provider; on failure it retries with the next healthy provider up to `len(pool)` times.
- Behavior is completely transparent: no API changes, no new kwargs required. `df.attrs["source_used"]` records which provider actually served the request.

## Scope

- **In scope:** `BaseUI._dispatch()` routing layer, new `ProviderRouter`, new `POOLS` config, unit tests.
- **Out of scope:** persistent state across processes, external health-check endpoints, streaming data, FMP/MSN (these have no multi-provider alternatives currently).

## Breaking Changes

None. Callers that pass `source=` explicitly bypass the router entirely.
