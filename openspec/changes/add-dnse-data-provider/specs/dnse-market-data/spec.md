## ADDED Requirements

### Requirement: DNSE shall be a selectable data source for OHLCV history
The package SHALL provide an `explorer/dnse/Quote` class that implements `history(symbol, start, end, interval, ...)` returning a DataFrame with standard columns `[time, open, high, low, close, volume]` in VND, compatible in schema with KBS and VCI equivalents.

#### Scenario: OHLCV history via DNSE source
- **WHEN** a caller requests `Quote(source="DNSE", symbol="VCB").history(start="2024-01-01", end="2024-06-30", interval="1D")`
- **THEN** the method returns a DataFrame with columns `time`, `open`, `high`, `low`, `close`, `volume` where prices are in VND and `time` contains timezone-aware datetime values

#### Scenario: Intraday OHLCV via DNSE source
- **WHEN** a caller requests `Quote(source="DNSE", symbol="VCB").history(interval="1m", start="2024-06-01", end="2024-06-01")`
- **THEN** the method returns a DataFrame with 1-minute OHLCV bars using the same standard column schema

#### Scenario: Unsupported interval raises error
- **WHEN** a caller passes an interval string not in the DNSE interval map
- **THEN** the method raises a `ValueError` with a message listing valid interval options

### Requirement: DNSE shall be a selectable data source for intraday tick data
The package SHALL provide `explorer/dnse/Quote` with an `intraday(date, ...)` method returning a DataFrame of matched trades with columns `time`, `price`, `volume`, `match_type` consistent with KBS/VCI intraday output.

#### Scenario: Intraday tick tape for a session date
- **WHEN** a caller requests `Quote(source="DNSE", symbol="VCB").intraday(date="2024-06-17")`
- **THEN** the method returns a DataFrame containing individual matched trades for that date with at minimum `time`, `price`, `volume`, `match_type` columns

#### Scenario: Intraday called for future date
- **WHEN** a caller passes a date in the future
- **THEN** the method raises a `ValueError` indicating the date is invalid

### Requirement: DNSE shall be a selectable data source for real-time price board
The package SHALL provide `explorer/dnse/Trading` with a `price_board(symbols_list, ...)` method returning a DataFrame with at minimum `symbol`, `time`, `reference_price`, `close_price`, `volume_accumulated`, `bid_price_1`, `bid_vol_1`, `ask_price_1`, `ask_vol_1` columns, consistent with KBS price board output.

#### Scenario: Multi-symbol price board via DNSE source
- **WHEN** a caller requests `Trading(source="DNSE").price_board(symbols_list=["VCB", "TCB", "VNM"])`
- **THEN** the method returns a DataFrame with one row per symbol containing standard price board columns

### Requirement: DNSE output schema SHALL be consistent with KBS and VCI
All DNSE provider methods SHALL produce DataFrames whose standard column names, dtypes, and value units match those produced by the KBS and VCI equivalents for the same method.

#### Scenario: Source switch does not break downstream processing
- **WHEN** a caller switches `source` from `"KBS"` to `"DNSE"` for `history()` with identical parameters
- **THEN** the resulting DataFrames have the same column names and compatible dtypes, differing only in the data values returned

#### Scenario: Default output does not include raw provider fields
- **WHEN** `get_all=False` (default)
- **THEN** the returned DataFrame contains only the standard mapped columns, no raw API field names

#### Scenario: Extended output with get_all=True
- **WHEN** `get_all=True`
- **THEN** the returned DataFrame includes additional provider-specific fields beyond the standard columns

### Requirement: DNSE provider SHALL self-register at module import time
The DNSE `Quote` and `Trading` classes SHALL register themselves with `ProviderRegistry` at the bottom of their respective module files so that `BaseAdapter` can resolve `("quote", "dnse")` and `("trading", "dnse")` after the module is imported.

#### Scenario: Registry resolves DNSE after import
- **WHEN** `vnstock.explorer.dnse.quote` has been imported
- **THEN** `ProviderRegistry.get("quote", "dnse")` returns the DNSE `Quote` class without raising `ValueError`

#### Scenario: Registry before import raises
- **WHEN** `vnstock.explorer.dnse.quote` has NOT been imported
- **THEN** `ProviderRegistry.get("quote", "dnse")` raises `ValueError`

### Requirement: DNSE credentials SHALL be provider-scoped and optional
DNSE public market data endpoints SHALL be accessible without authentication. If any endpoint requires credentials for higher-tier or real-time data, those credentials SHALL be accepted only as constructor parameters on the DNSE provider class, not as package-level registration state.

#### Scenario: Unauthenticated public data access
- **WHEN** a caller constructs `Quote(source="DNSE", symbol="VCB")` without passing any credential
- **THEN** the provider can fetch publicly available OHLCV history without raising a credential error

#### Scenario: Optional credential injection
- **WHEN** a caller passes `api_key=` or equivalent credential directly to the DNSE constructor
- **THEN** the provider uses that credential for the session without storing it in package-level state
