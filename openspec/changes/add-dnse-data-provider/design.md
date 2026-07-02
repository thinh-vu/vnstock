## Context

`vnstock` is a flat/open data extraction library for Vietnamese and global financial markets. Market data today comes from two providers for Vietnamese equities: KBS and VCI. DNSE (DragonFly Securities) operates a publicly accessible REST/JSON market data API (`services.entrade.com.vn`) that provides OHLCV history, real-time price board, and intraday tick tape for Vietnamese equities. The existing explorer layer (`vnstock/explorer/kbs/`, `vnstock/explorer/vci/`) defines a clear, repeatable pattern for adding new data providers.

The original DNSE connector (`vnstock/connector/dnse/`) was removed during the broker-execution cleanup; it contained only login/order/account methods. The market data endpoints are entirely separate and do not require broker login.

## Goals / Non-Goals

**Goals:**
- Implement a `vnstock/explorer/dnse/` module with `Quote` and `Trading` classes matching the KBS/VCI structural pattern
- Ensure output DataFrames are column-compatible with KBS/VCI equivalents (same standard column names, same dtypes, same price units in VND)
- Register DNSE in `ProviderRegistry`, `DataSource` enum, and `vnstock/ui/_registry.py::MAP`
- Allow users to select DNSE via `source="DNSE"` wherever KBS/VCI are accepted
- Add unit tests following the existing `tests/unit/` pattern

**Non-Goals:**
- DNSE broker execution (login, orders, account) — removed and out of scope
- WebSocket/streaming from DNSE — streaming adapter is a separate roadmap item
- Using `vnstock/connector/dnse/` for data — the connector layer is for auth-gated connectors; public market data belongs in `explorer/`
- Changing the Unified UI domain structure — DNSE is a new source choice, not a new domain

## Decisions

### D1: Use `explorer/dnse/` not `connector/dnse/`

**Chosen**: `vnstock/explorer/dnse/`  
**Rationale**: DNSE market data endpoints are publicly accessible (no login required). All public-endpoint providers live in `explorer/`. The `connector/` layer is reserved for API-key-gated or auth-gated services (FMP). Mixing concerns in `connector/` would break the architectural boundary.  
**Alternative**: Extend `connector/dnse/` — rejected because it implies credential management that does not apply to public endpoints.

### D2: Consistent output schema with KBS/VCI

**Chosen**: Rename all raw DNSE API fields to standard column names (`time`, `open`, `high`, `low`, `close`, `volume`) via `_OHLC_MAP` in `const.py`.  
**Rationale**: Callers who switch `source=` must receive structurally identical DataFrames. Any DNSE-specific extra fields should be available only via `get_all=True`, matching KBS/VCI behavior.

### D3: Price unit normalization

**Chosen**: DNSE API returns prices in actual VND (not VND×1000 like KBS). No division is needed; values are returned as-is.  
**Rationale**: KBS divides by 1000 because its internal representation uses thousands. DNSE native values are already in VND. Applying the KBS divisor would produce incorrect prices.  
**Alternative**: Divide by 1000 for consistency with KBS raw format — rejected because the standard output is VND (not raw API format), so KBS and DNSE outputs should both arrive in VND.

### D4: DNSE API endpoints

The DNSE Entrade API base: `https://services.entrade.com.vn`

| Method | Endpoint | Notes |
|--------|----------|-------|
| OHLCV history | `GET /chart-api/v2/ohlcs/stock?resolution={resolution}&symbol={symbol}&from={from_ts}&to={to_ts}` | Unix timestamps; resolutions: `1`, `5`, `15`, `30`, `60`, `D`, `W`, `M` |
| Intraday tick | `GET /dnse-order-api/v2/user/transaction-buy-sell-history?symbol={symbol}&date={date}` | Returns matched trades for a session date |
| Price board | `GET /chart-api/v2/quotes?symbols={sym1,sym2,...}` | Snapshot of current prices, BBO |

**Note**: These endpoints are publicly accessible without authentication headers beyond standard browser User-Agent.

### D5: Interval mapping

| User interval | DNSE resolution |
|---|---|
| `1m` | `1` |
| `5m` | `5` |
| `15m` | `15` |
| `30m` | `30` |
| `1H` / `1h` | `60` |
| `1D` / `D` | `D` |
| `1W` / `W` | `W` |
| `1M` / `M` | `M` |

### D6: Timestamp handling

DNSE history endpoint uses Unix timestamps. The `Quote.history()` method converts `start`/`end` date strings to Unix timestamps before building the URL. Returned timestamps (in epoch seconds) are converted to `datetime` objects in `Asia/Ho_Chi_Minh` (UTC+7) timezone.

### D7: Registration pattern

Follow the exact KBS/VCI bottom-of-file registration:

```python
from vnstock.core.registry import ProviderRegistry  # noqa: E402
ProviderRegistry.register("quote", "dnse", Quote)
```

Add `"dnse"` to `DataSource` enum in `vnstock/core/types.py` so `BaseAdapter` source validation passes.

### D8: MAP entries in `_registry.py`

Add DNSE as an alternative source for existing MAP keys (do not add new domains). Users select DNSE by passing `source="DNSE"` at call time — the MAP default source remains KBS.

## Risks / Trade-offs

**[Risk] DNSE API is undocumented / changes silently**  
→ Mitigation: Pin tested endpoint paths in `const.py` with version comments. Add integration test smoke-checking a known stable ticker (e.g., `VCB`).

**[Risk] DNSE endpoint availability depends on market hours**  
→ Mitigation: Intraday tick endpoint only returns data for a given `date`; history endpoint works outside market hours for past data. Document limitation in docstrings.

**[Risk] Output schema drift if DNSE adds/removes response fields**  
→ Mitigation: Column renames via `_OHLC_MAP` act as a projection; unknown fields are dropped. The `get_all=True` flag can expose additional fields without breaking default output.

**[Trade-off] Third data source increases test surface**  
→ Accepted: Unit tests mock HTTP responses and do not require live access. Integration tests are `@pytest.mark.integration` and opt-in.

## Migration Plan

1. Implement `vnstock/explorer/dnse/` module (no existing code to migrate)
2. Extend `DataSource` enum and lazy-load trigger (additive, non-breaking)
3. Add MAP entries (additive, non-breaking)
4. Add tests
5. No rollback required — DNSE is purely additive; removing MAP entries and the explorer module fully reverts the change

## Open Questions

- Confirm whether DNSE `/dnse-order-api/v2/user/transaction-buy-sell-history` truly requires no auth, or if auth is needed for real-time vs delayed tick data. If auth is required, consider making it optional: unauthenticated returns delayed data, authenticated returns real-time.
- Confirm DNSE price board endpoint field names (need live API test to finalize `_PRICE_BOARD_MAP`).
