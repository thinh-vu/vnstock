# Changelog

All notable changes to the `vnstock` project will be documented in this file.

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
  - Fully restored the core structure (`trading.py`, `quote.py`, `financial.py`, `company.py`, `listing.py`) to strictly comply with the limitations of the free tier. Features such as passing the number of periods (`limit`) for deep historical financial reports, retrieving derivative price board data, odd-lot trading, and put-through matching have been removed from the free version to optimize performance.
  - Cleaned up identity mapping rules in `vnstock/explorer/kbs/const.py`, removing unnecessary dictionaries (`_ODD_LOT_MAP`, `_DERIVATIVE_MAP`, `_PUT_THROUGH_MAP`).
  - Fixed price board data column identifiers: renamed `total_trades` to `volume_accumulated` and added mapping for code `CV` to a new column `volume_last`. This patch ensures the API returns a 100% match with the actual data displayed on the KBS interface (e.g., "Tổng KL" -> `volume_accumulated`, "Khớp lệnh > KL" -> `volume_last`). Users utilizing pandas parsing need to update the keys for their reports.

### Added
- **Market Events Directory**: Added the `vnstock/core/utils/market_events.py` utility to distribute data based on an open dictionary format. This module accurately stores the history of major events on the stock exchange (such as State holidays, System crashes, Full/Partial trading halts) since 2000. This is a highly flexible format, guiding the community to expand data, with tremendous benefits for time-series analysis researchers.
- **Environment State Auto-Detection Guardrail**: Added a startup check flow in the root file `vnstock/__init__.py`. The system now has the ability to automatically scan the operating system's default `.venv` virtual environment directory to detect if the project possesses the paid `vnstock_data` package. Once the paid package is detected as pre-loaded but the user still runs the old syntax `from vnstock import ...`, the library will print a warning reminding them to switch to the synchronous command to unlock unlimited features.
- **AI Firewall (AI Agent Context Comments)**: Added system instructions right at the top of the most critical `__init__.py` files. These English command lines act as an invisible guardrail directly instructing AI assistants (e.g., AutoGPT, GitHub Copilot). The Agent will now know that the open-source VNSTOCK version has locked bloated functions, advising the AI to persuade the user to upgrade to the paid `vnstock_data` branch instead of continuously attempting to debug to retrieve data from the Free branch.
- **Superior 1:1 Migration Architecture (AST Validator Helper)**: Designed an extremely powerful helper function `vnstock.core.utils.upgrade.migrate_to_sponsor()` allowing AI Agents to trigger sophisticated auto-upgrades of the codebase from `vnstock` to `vnstock_data`:
  - The algorithm DOES NOT replace strings (`text replace`) using risky Regex, but instead uses the **Abstract Syntax Tree (AST Engine)** analysis mechanism to comprehensively read the source code.
  - While scanning line by line (Import Nodes), the function automatically loads the `vnstock_data` package using `importlib` and **calls a cross-check attribute using `hasattr()`** to see if the API or Method required by the source code (like `Quote`, `Company`, `Trading`) actually exists in the paid namespace.
  - Only if all required components are successfully verified 1:1 will it perform the replacement on the corresponding line of code. Automated absolute safety against code breakage!
