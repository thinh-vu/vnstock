# Changelog

All notable changes to this project will be documented in this file.

## [2025-02-01]

### Fixed
- Fixed `Listing` tests to correctly handle `pd.Series` return types from `all_future_indices` and related methods
- Fixed `Quote` integration tests to handle missing data and expired derivatives gracefully without failing the entire suite
- Fixed `KBS Quote` to correctly interpret bar-based lookback lengths (e.g., '500b') using `interpret_lookback_length` logic
- Enabled full integration test suite for `vnstock.explorer` module

### Changed
- Consolidated test documentation into `tests/docs/` directory
- Updated `.gitignore` to include debug scripts
- Standardized KBS Quote price data to use decimal values (thousands unit) instead of VND in `history` and `intraday` methods

### Removed
- Removed `price_depth` method from `vnstock.explorer.vci.quote`


## [3.4.2] - 2026-01-27

### Added

- **Derivatives Support**: Implemented `convert_derivative_symbol` and `get_derivative_maturity_date` to support the new KRX derivative symbol format (effective May 2025), automatically converting old symbols (e.g., VN30F2506) to the new standard.
- **KBS Index Support**: Added `_INDEX_MAPPING` and validation logic to fully support market indices in KBS Quote module, ensuring correct API endpoint routing.
- **VCI Listing**: Added `all_indices()` and `indices_by_group()` wrapper methods in `Listing` class to provide standardized access to market indices.

### Changed

- **KBS Financial**: Optimized `get_financial_report` to use `page_size=8` (fetching 2 years of quarterly data) and improved field normalization with `preserve_hierarchy=True`.
- **Quote Validation**: Added strict validation to prevent `intraday` data requests for Index symbols in both KBS and VCI sources (`ValueError` raised).
- **Refactoring**: Simplified `FieldHandler` initialization and removed file-based referencing in favor of built-in mappings for better performance.

## [2026-01-22]

### Added

- Overhauled Vietnamese text normalization with new character map and advanced options for robust snake_case conversion
- Advanced field handling system for financial reports with flexible standardization options
- Field display modes: standardized_only, all_fields, and auto_convert for flexible field handling
- Comprehensive field mapping and validation system for KBS financial data
- Language filtering support for financial reports (Vietnamese/English/Both)
- Field collision detection and handling with automatic ID generation
- Professional pandas extension for chart visualization with vnstock_chart integration
- Dual backend charting system: vnstock_chart (professional) and vnstock_ezchart (fallback)
- Enhanced field utilities package with specialized financial data field handlers
- Comprehensive GitHub Actions CI/CD pipeline for automated testing and quality assurance
- Multi-platform test matrix: Ubuntu, macOS, Windows across Python 3.10-3.13
- Automated coverage reporting with Codecov integration
- Performance benchmarking and regression detection
- Code quality checks: flake8, black, isort, mypy
- Security scanning with Bandit and Safety
- Enhanced pytest fixtures and utilities for comprehensive testing
- Performance monitoring and quality metrics tracking
- Direct API key registration support with non-interactive mode for programmatic setup
- Masked API key display and tier information after successful registration
- AI-powered vibe coding section in README

### Changed

- Updated API key registration URL from `/account` to `/login` endpoint
- Enhanced KBS trading module with code optimizations
- Improved README formatting and added user authentication section
- Refactored KBS financial module with advanced field processing capabilities
- Updated all financial report methods (income_statement, balance_sheet, cash_flow, ratio) with language filtering support
- Enhanced field ID generation with collision detection and automatic resolution
- Integrated professional charting capabilities with pandas DataFrame extension
- Restructured test suite with comprehensive GitHub Actions CI/CD integration
- Enhanced pytest configuration with advanced fixtures and performance monitoring
- Implemented multi-platform and multi-version testing matrix for better compatibility assurance

### Fixed

- Optimized code performance in KBS trading module

## [2026-01-16]

### Added

- New KBS data source support as default source, replacing VCI as primary source
- Authentication utilities for public uses with the Vnstock API key
- Lazy loading mechanism to prevent circular import deadlocks across multiple modules
- Show tier and limits information for registered users before prompting for key change

### Changed

- Updated version from 3.3.2 to 3.4.0
- Updated Listing class to use KBS as default data source instead of VCI
- Modified StockComponents to initialize listing with KBS source
- Updated error message to include KBS in valid source options

### Removed

- Removed outdated Vietnam stock notebook (1_vietnam_stock_vnstock3.ipynb) containing 6497 lines of legacy content
- Cleaned up comprehensive examples covering Listing, Quote, Company, Finance, and Trading modules

## [2026-01-06]

### Fixed

- Fixed issue where VN100 derivative symbols (e.g., `VN100F1M`) were incorrectly identified as Covered Warrants due to length conflict.
- Refined `auto_count_back` logic in `Quote.history` to accurately reflect Vietnam market trading hours (5 hours/day, 255 mins/day).

### Added

- Feature "Smart Lookback" for `Quote.history` in `vnstock/explorer/vci/quote.py` and `vnstock/explorer/tcbs/quote.py`. Users can now use `length` parameter (e.g., `'3M'`, `'10W'`, `'100b'`, `150`) instead of specifying start/end dates.
- New utility `vnstock/core/utils/lookback.py` for parsing flexible time periods and calculating start dates.
- Documentation for Smart Lookback feature at `docs/feature_lookback.md`.
- Enhanced header management mechanism in `vnstock/core/utils/user_agent.py` supporting `Authorization`, `custom_headers`, and `override_headers` for dynamic and flexible request configuration.
- Enhanced `ProxyManager` with `get_fresh_proxies`, custom proxy support, and singleton instance.
- Updated `client.py` to support `AUTO` proxy mode and integrated with `ProxyManager`.
- Refactored `TCBS Quote` to use central `client.py` request wrapper, enabling proxy support.
- Refactored all VCI modules (`Quote`, `Company`, `Financial`, `Listing`, `Trading`) to support proxy configuration via `__init__` parameters (`proxy_mode`, `proxy_list`), addressing IP blocking issues on cloud platforms like Google Colab/Kaggle.
- Documentation for the new header and authentication system at `docs/header_management.md`.

### Changed

- `Quote.history`: `start` parameter is now optional if `length` or `count_back` is provided.
- Updated `get_asset_type` in `vnstock/core/utils/parser.py` to dynamically recognize all indices from `vnstock.constants.INDICES_INFO`, ensuring better support for sector and investment indices (e.g., `VNSI`, `VNFINLEAD`, `VNIND`).