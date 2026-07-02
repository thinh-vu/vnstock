## Why

`vnstock` currently exposes convenience surfaces that are outside the intended
data-extraction scope: chart visualization, bot/notification integrations, and
API-documentation helpers. The package should be smaller and focused on
financial, securities, and fund data retrieval so it can be embedded into other
systems with fewer optional concerns.

## What Changes

- **BREAKING**: Remove active visualization/charting APIs, including
  `vnstock.common.viz`, DataFrame `.viz` extension behavior, and any public
  `Chart`/`get_chart` exports or documentation.
- **BREAKING**: Remove bot and notification integrations, including Slack,
  Telegram, Discord, and Lark messaging helpers.
- **BREAKING**: Remove `show_api`, `show_doc`, and `show_docs` public helper
  exports and supporting documentation surfaces.
- **BREAKING**: Remove broker/account/order execution connectors that are not
  data extraction surfaces, including the public `Broker`/DNSE UI and DNSE
  trade/account/order connector APIs.
- Preserve financial, securities, and fund data extraction APIs in Unified UI
  and legacy data classes.
- Preserve provider credentials that are required for data access, such as FMP
  API keys.
- Update README, package exports, tests, and dependency expectations to reflect
  a data-only package.

## Capabilities

### New Capabilities

- `data-only-package`: The package exposes only financial, securities, fund, and
  related market-data extraction surfaces; visualization, notification, and API
  documentation helper surfaces are absent from active behavior.

### Modified Capabilities

- None. No existing OpenSpec capabilities are present in `openspec/specs/`.

## Impact

- Public exports in `vnstock/__init__.py` and `vnstock/ui/__init__.py`.
- Modules under `vnstock/common/viz.py` and `vnstock/bot/notify.py`.
- UI helper functions under `vnstock/ui/helper.py` and any callers/imports.
- Broker UI and DNSE connector modules that expose account/order operations.
- README and agent guidance describing supported package scope.
- Tests covering package imports, public exports, retained data APIs, and removed
  non-data feature imports.
