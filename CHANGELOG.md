# Changelog

All notable changes to the `vnstock` project will be documented in this file.

## [4.0.9] 2026-09-07

### Added
- **AI Agent Environment Setup**: Implemented dynamic AI agent environment setup with automated background initialization.
- **Internal Skill Loader**: Introduced an internal skill loader for improved modularity.
- **Integration Test Control**: Enabled integration test skips for smoother development workflows.

### Changed & Improved
- **Core Explorer Modules**: Updated core explorer modules and removed legacy assets, schemas, and proxy management infrastructure.
- **Parameter Handling**: Unified parameter handling for OHLCV methods to ensure consistency across the API.
- **Data Fetching Robustness**: Improved data fetching robustness and standardized documentation snapshots.
- **Documentation**: Updated developer guidelines, installation instructions, and repository documentation in README.md.

## [4.0.4] 2026-05-19

### Added
- **KRX format support for Derivatives**: Automatically convert derivative symbols to the new KRX standard format (applied in the VCI explorer).
- **Bars period criteria**: Added support for the `"B"` (Bars) notation in the lookback period decoder, automatically estimating about 1.5 calendar days per bar for greater flexibility in data extraction.

### Changed & Improved
- **Flexible Parameter Passing (Kwargs Filtering)**: Upgraded the `Quote` class (API) with a mechanism to automatically read `inspect.signature` from the provider. This helps automatically filter and remove unsupported `**kwargs` parameters, preventing crashes caused by passing invalid parameters.
- **Optional Charting Dependency**: Removed the charting library installation check (`vnstock_chart`, `vnstock_ezchart`) at the module level (import-level) and moved it into the initialization process of the `Chart` object. The application can now run smoothly without requiring charting packages to be installed if they are not used.
- **Unified UI Market Interface**:
  - Standardized the parameter name `interval` to replace `resolution` in the Bond domain (backward compatibility is still maintained).
  - Added clearer `Optional[str]` type hints for time parameters in the Index domain.
  - Prevented the duplicate parameter passing error for interval/resolution in equity trades.

## [4.0.3] 2026-04-29

### Added
- **Bond Trading**: Added the bond data structure to the Unified UI layer, unifying the architecture with the `vnstock_data` version, and added `ohlcv`, `trades`, and `quote` functions.
- **InstrumentType Enum**: Added specialized security identification classification to standardize the recognition of financial asset types.

### Changed & Improved
- Added lists of indices from HNX and UPCOM, and improved the ability to accurately identify symbols via the `get_asset_type` function with support for new index codes.
- **Financial Report Data**: Supported the multiplier (`unit_multiplier`) and consistently mapped the data column structure between KBS and VCI sources.
- **Data Source Handling (MSN & VCI)**: Built a dynamic `SecId` resolution mechanism for the MSN source to fix errors in fetching historical data; cleaned up VCI's Device-ID headers and added a safe URL fallback/sanitize mechanism when loading symbol lists.

## [2.5.0] - 2026-04-06

### Changed
- **KBS Module**:
  - Fully restored the core structure (`trading.py`, `quote.py`, `financial.py`, `company.py`, `listing.py`) to match the scope of the Community edition. Features such as passing the number of periods (`limit`) for deep historical financial reports, derivative price board data, odd-lot trading, and put-through matching are part of the extended edition.
  - Cleaned up identity mapping rules in `vnstock/explorer/kbs/const.py`, removing unnecessary dictionaries (`_ODD_LOT_MAP`, `_DERIVATIVE_MAP`, `_PUT_THROUGH_MAP`).
  - Fixed price board data column identifiers: renamed `total_trades` to `volume_accumulated` and added mapping for code `CV` to a new column `volume_last`. This patch aligns the API output with the data displayed on the KBS interface (e.g., "Tổng KL" -> `volume_accumulated`, "Khớp lệnh > KL" -> `volume_last`). Users utilizing pandas parsing need to update the keys for their reports.

### Added
- **Market Events Directory**: Added the `vnstock/core/utils/market_events.py` utility to distribute data based on an open dictionary format. This module accurately stores the history of major events on the stock exchange (such as State holidays, System crashes, Full/Partial trading halts) since 2000. The format is open so the community can extend it, which helps time-series analysis.
- **Environment State Auto-Detection Guardrail**: Added a startup check flow in the root file `vnstock/__init__.py`. The system now has the ability to automatically scan the operating system's default `.venv` virtual environment directory to detect whether the extended edition `vnstock_data` is present. If it is installed but the user still runs the old syntax `from vnstock import ...`, the library prints a reminder to switch imports so the extended-edition features and quota apply.
- **AI Agent Context Comments**: Added notes to the docstring at the top of the main `__init__.py` files. These English notes state which features the free `vnstock` edition does not include, so an AI assistant (e.g. GitHub Copilot) has enough context to point the user to the `vnstock_data` edition when their needs call for those features, rather than building workarounds around the free edition.
- **1:1 Migration Helper (AST Validator)**: Added `vnstock.core.utils.upgrade.migrate_to_sponsor()` so AI agents can migrate a codebase from `vnstock` to `vnstock_data`:
  - The algorithm DOES NOT replace strings (`text replace`) using risky Regex, but instead uses the **Abstract Syntax Tree (AST Engine)** analysis mechanism to comprehensively read the source code.
  - While scanning line by line (Import Nodes), the function automatically loads the `vnstock_data` package using `importlib` and **calls a cross-check attribute using `hasattr()`** to see if the API or Method required by the source code (like `Quote`, `Company`, `Trading`) actually exists in the extended-edition namespace.
  - The replacement is applied to a line only when all required components verify 1:1, which reduces the risk of breaking the code.
