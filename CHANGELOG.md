# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

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
