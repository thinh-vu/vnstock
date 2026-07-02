## Why

`vnstock` currently sources Vietnamese equity market data exclusively from KBS and VCI. DNSE (DragonFly Securities - Entrade) operates a publicly accessible market data API that provides OHLCV history, real-time price board, and intraday tick data for Vietnamese equities. Adding DNSE as a third provider increases data redundancy, offers an independent fallback when KBS or VCI is unavailable, and gives users source-level choice via the existing `source=` parameter.

## What Changes

- **New explorer module** `vnstock/explorer/dnse/` implementing `Quote` and `Trading` classes following the KBS/VCI pattern
- **ProviderRegistry self-registration** for `("quote", "dnse")` and `("trading", "dnse")`
- **DataSource enum** extended with `DNSE`
- **Lazy-load trigger** added to `vnstock/__init__.py::_ensure_explorer_modules_loaded`
- **UI registry MAP** extended: `Market.equity.ohlcv`, `Market.equity.quote`, `Market.equity.trades` gain `dnse` as an available source
- **Unit and integration tests** for the new explorer

## Capabilities

### New Capabilities

- `dnse-market-data`: OHLCV history, real-time price board, and intraday tick tape sourced from DNSE's public market data API, consistent in output schema with KBS/VCI equivalents

### Modified Capabilities

- `flat-access-model`: DNSE credentials (if required for higher-tier endpoints) must be provider-scoped, not registered at package level — consistent with the flat access model spec

## Impact

- **New files**: `vnstock/explorer/dnse/__init__.py`, `const.py`, `quote.py`, `trading.py`
- **Modified files**: `vnstock/core/types.py` (DataSource enum), `vnstock/__init__.py` (lazy-load), `vnstock/ui/_registry.py` (MAP entries)
- **New test files**: `tests/unit/explorer/test_dnse_quote.py`, `tests/unit/explorer/test_dnse_trading.py`
- **No breaking changes** to existing public API; DNSE is additive
- **No new third-party dependencies** required if DNSE API is REST/JSON
