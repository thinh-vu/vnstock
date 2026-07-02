## 1. Baseline Tests

- [x] 1.1 Add focused tests proving retained top-level data imports still work: `Reference`, `Market`, `Fundamental`, `Retail`, `Quote`, `Listing`, `Company`, `Finance`, `Trading`, `Fund`, and `Vnstock`.
- [x] 1.2 Add focused tests proving removed public exports are unavailable from `vnstock`: `Broker`, `show_api`, `show_doc`, and `show_docs`.
- [x] 1.3 Add focused tests proving `vnstock.ui` no longer exports `Broker`, `show_api`, or `show_doc`.
- [x] 1.4 Add focused tests for retained FMP data credential behavior so provider-scoped data credentials are not removed.

## 2. Remove Public Non-Data Exports

- [x] 2.1 Remove `Broker`, `show_api`, `show_doc`, and `show_docs` from `vnstock/__init__.py` imports and `__all__`.
- [x] 2.2 Remove `Broker`, `show_api`, and `show_doc` lazy exports from `vnstock/ui/__init__.py` and update its `__all__`.
- [x] 2.3 Remove or disconnect `vnstock/ui/broker.py` and the `Broker` registry/domain routes.
- [x] 2.4 Remove runtime `show_api` and `show_doc` helper behavior from `vnstock/ui/helper.py` or delete the module if no retained code imports it.

## 3. Remove Visualization And Notification Surfaces

- [x] 3.1 Remove or disconnect `vnstock/common/viz.py` charting behavior and pandas `.viz` extension registration.
- [x] 3.2 Remove charting-only exports, imports, tests, examples, and dependency references tied to `vnstock_ezchart` or `vnstock_chart` if they are no longer required by retained data APIs.
- [x] 3.3 Remove or disconnect `vnstock/bot/notify.py` and bot package exports.
- [x] 3.4 Remove notification-only tests, examples, docs, and dependency references tied to Slack, Telegram, Discord, or Lark messaging helpers.

## 4. Remove Broker Execution Surfaces

- [x] 4.1 Remove top-level and UI access to DNSE broker/account/order functionality.
- [x] 4.2 Remove or disconnect `vnstock/connector/dnse` modules if no retained data path imports them.
- [x] 4.3 Remove DNSE account, OTP, trading-token, place-order, cancel-order, and conditional-order docs/tests/examples.
- [x] 4.4 Preserve market/trading data APIs such as price board, quote history, intraday trades, foreign trade, and proprietary trade.

## 5. Documentation And Reference Cleanup

- [x] 5.1 Update README Vietnamese and English sections to describe a data-only package and remove current usage instructions for visualization, notification, runtime API-doc helpers, and broker execution.
- [x] 5.2 Update `AGENTS.md` to record the data-only boundary for future sessions.
- [x] 5.3 Update changelog or migration notes for the breaking removal, without advertising removed features as current APIs.
- [x] 5.4 Grep the repository for removed feature names and classify remaining references as historical, migration, tests, or OpenSpec artifacts.

## 6. Verification

- [x] 6.1 Run focused tests for the data-only package boundary.
- [x] 6.2 Run `ruff check` and `ruff format --check` on touched Python files.
- [x] 6.3 Run `git diff --check`.
- [x] 6.4 Run `make verify` if the local environment has the required dependencies; otherwise document the exact blocker and the strongest successful checks.
