# Spec: Provider Router

## Requirements

### REQ-1: Transparent automatic source selection
When a caller does not pass `source=`, the system SHALL automatically select a provider from the pool for the requested method. The caller's code requires no changes.

**Scenario:** `Market().equity.ohlcv(symbol="VCB", start="2024-01-01", end="2024-12-31")` — no `source=` argument — succeeds and returns a DataFrame regardless of which provider is selected.

### REQ-2: Round-robin distribution
Successive calls to the same `(domain, method)` SHALL rotate through available providers in round-robin order when all providers are healthy.

**Scenario:** Three consecutive calls to `equity.ohlcv` with providers `[KBS, VCI, DNSE]` shall select `KBS`, `VCI`, `DNSE` in that sequence (then repeat).

### REQ-3: Automatic failover on error
When a provider raises a retriable error (Timeout, ConnectionError, HTTP 5xx, HTTP 429), the system SHALL retry with the next provider in the pool. The caller receives a successful result if any provider succeeds.

**Scenario:** KBS returns HTTP 503; system retries with VCI; VCI succeeds; caller gets DataFrame.

### REQ-4: Provider cooldown after failure
After a provider failure, that provider SHALL be skipped for a cooldown window:
- Timeout / 5xx: 60 seconds
- HTTP 429 (rate limit): 300 seconds

**Scenario:** KBS times out; subsequent calls within 60s skip KBS and use VCI or DNSE.

### REQ-5: Graceful degradation when all providers are in cooldown
If all pool providers are in cooldown, the router SHALL select the one whose cooldown expires soonest and attempt it anyway (best-effort).

**Scenario:** All three providers are in cooldown; router picks the least-recently-failed one; call proceeds.

### REQ-6: Explicit source= bypasses router
When the caller passes `source="KBS"` (or any source string), the router SHALL NOT override it. Behavior is identical to current hardcoded dispatch.

**Scenario:** `Market().equity.ohlcv(symbol="VCB", source="VCI")` — always uses VCI regardless of router state.

### REQ-7: source_used metadata on DataFrame results
When the router selects a provider, the returned DataFrame SHALL have `df.attrs["source_used"]` set to the provider name actually used.

**Scenario:** After a KBS failover to VCI, `result.attrs["source_used"] == "VCI"`.

### REQ-8: Thread safety
The router singleton SHALL be safe to use from multiple threads without data corruption.

### REQ-9: No persistent state
Router state (counters, cooldowns) is in-process memory only. State resets on process restart / re-import. No file I/O.

### REQ-10: Single-provider pool is passthrough
A pool entry with only one provider behaves like the current static routing — no retry possible, errors propagate normally.
