## 1. Baseline Tests (Red)

- [x] 1.1 Create `tests/unit/explorer/test_dnse_quote.py` with failing tests: instantiation of `Quote(source="DNSE", symbol="VCB")`, invalid interval raises `ValueError`, `ProviderRegistry.get("quote", "dnse")` resolves after import
- [x] 1.2 Create `tests/unit/explorer/test_dnse_trading.py` with failing tests: instantiation of `Trading(source="DNSE")`, `price_board()` returns DataFrame with required columns, unauthenticated access works
- [x] 1.3 Add `DataSource.DNSE` enum value to `vnstock/core/types.py` and add a test asserting `source="DNSE"` passes `BaseAdapter` validation

## 2. DNSE Explorer Module

- [x] 2.1 Create `vnstock/explorer/dnse/__init__.py` re-exporting `Quote` and `Trading`
- [x] 2.2 Create `vnstock/explorer/dnse/const.py` with URL constants (`_BASE_URL = "https://services.entrade.com.vn"`), `_OHLC_URL`, `_INTRADAY_URL`, `_PRICE_BOARD_URL`, `_INTERVAL_MAP`, `_OHLC_MAP`, `_INTRADAY_MAP`, `_PRICE_BOARD_MAP`
- [x] 2.3 Implement `vnstock/explorer/dnse/quote.py::Quote.__init__(symbol, random_agent, show_log, ...)` following the KBS/VCI `__init__` signature exactly
- [x] 2.4 Implement `Quote.history(start, end, interval, to_df, show_log, count_back, floating, get_all)` — convert date strings to Unix timestamps, GET `_OHLC_URL`, rename columns via `_OHLC_MAP`, return standard `[time, open, high, low, close, volume]` DataFrame
- [x] 2.5 Implement `Quote.intraday(date, to_df, show_log, get_all)` — GET `_INTRADAY_URL`, rename columns via `_INTRADAY_MAP`, return standard `[time, price, volume, match_type]` DataFrame; raise `ValueError` for future date
- [x] 2.6 Add `ProviderRegistry.register("quote", "dnse", Quote)` at the bottom of `quote.py`
- [x] 2.7 Implement `vnstock/explorer/dnse/trading.py::Trading.__init__(symbol, random_agent, show_log, ...)` and `price_board(symbols_list, show_log, get_all)` — GET `_PRICE_BOARD_URL`, rename columns via `_PRICE_BOARD_MAP`, return standard price board DataFrame
- [x] 2.8 Add `ProviderRegistry.register("trading", "dnse", Trading)` at the bottom of `trading.py`

## 3. Integration — Enum, Lazy Load, Registry MAP

- [x] 3.1 Add `DNSE = "DNSE"` to `DataSource` enum in `vnstock/core/types.py`; update `all_sources()` if it uses an explicit list
- [x] 3.2 Add `from .explorer import dnse` (or equivalent) to `vnstock/__init__.py::_ensure_explorer_modules_loaded` so DNSE self-registration fires at package load time
- [x] 3.3 Verify `vnstock/api/quote.py::Quote.__init__` source validation accepts `"DNSE"` — update allowed-source list or validator if it hard-codes KBS/VCI
- [x] 3.4 Verify `vnstock/api/trading.py::Trading.__init__` source validation accepts `"DNSE"` — update if needed
- [x] 3.5 Add DNSE MAP entries to `vnstock/ui/_registry.py` — do not change default source; add DNSE as a documented alternative source comment or secondary tuple entry following current pattern

## 4. Tests — Green and Integration

- [x] 4.1 Add `@pytest.mark.integration` tests in `tests/integration/explorer/test_dnse_quote_integration.py` that mock HTTP responses (no live calls): assert `history()` column names, dtypes, and price unit for equity and index
- [x] 4.2 Add integration test asserting `intraday()` columns match KBS/VCI intraday output schema
- [x] 4.3 Add integration test asserting `price_board()` columns match KBS price_board output schema for the standard fields
- [x] 4.4 Add test asserting that switching `source` from `"KBS"` to `"DNSE"` in `Quote.history()` returns DataFrames with identical column names

## 5. Documentation

- [x] 5.1 Add `DNSE` to the provider capability matrix in `roadmap.md`
- [x] 5.2 Update `AGENTS.md` provider split note to include `vnstock/explorer/dnse` in the explorer list
- [x] 5.3 Add a brief DNSE source note in `CHANGELOG.md` under a new patch version entry

## 6. Verification

- [x] 6.1 Run `PYTHONPATH=. pytest tests/unit/explorer/` and confirm all new tests pass
- [x] 6.2 Run `python -m ruff check vnstock/explorer/dnse tests/unit/explorer/` — zero errors
- [x] 6.3 Run `python -m ruff format --check vnstock/explorer/dnse tests/unit/explorer/` — no changes needed
- [x] 6.4 Run `python -m compileall -q vnstock/explorer/dnse` — no syntax errors
- [x] 6.5 Run `PYTHONPATH=. python -c "from vnstock.explorer.dnse.quote import Quote; from vnstock.core.registry import ProviderRegistry; print(ProviderRegistry.get('quote','dnse'))"` — prints DNSE Quote class
