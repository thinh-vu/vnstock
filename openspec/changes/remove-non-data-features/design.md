## Context

`vnstock` now uses a flat access model, but it still exposes several surfaces
that are outside the core data-extraction contract: chart visualization,
notification bots, API tree/documentation helpers, and broker account/order
connectors. These features pull the package toward application tooling and
integration actions instead of a focused financial data library.

The retained scope is financial, securities, market, and fund data retrieval via
Unified UI and legacy data classes. Existing data providers include KBS, VCI,
MSN, FMarket, and FMP. FMP keeps provider-scoped credentials because the
external data provider requires them.

## Goals / Non-Goals

**Goals:**

- Keep public APIs for stock/securities market data, company reference data,
  financial statements, fund data, forex/crypto/commodity market data, and
  provider-backed international market data.
- Remove active visualization/charting behavior and related pandas extension
  surfaces from the package.
- Remove bot/notification behavior and related third-party messaging credential
  handling from the package.
- Remove `show_api`, `show_doc`, and `show_docs` public helper exports.
- Remove broker/account/order execution surfaces, especially `Broker` and DNSE
  trade/account/order connector APIs, because they are not data extraction.
- Update docs/tests so the supported surface is clearly data-only.

**Non-Goals:**

- Do not remove market/trading data APIs such as price board, trades, foreign
  trade, proprietary trade, or quote/history data.
- Do not remove data-provider credentials such as FMP API keys when the external
  data provider requires them.
- Do not change provider scraping/extraction internals unless needed to detach
  removed public surfaces.
- Do not reintroduce user registration, tiers, entitlement checks, or private
  package fallback routing.

## Decisions

1. Remove public entrypoints rather than leaving active compatibility shims.

   Rationale: the requested package boundary is data-only. Leaving operational
   visualization, notification, documentation, or broker helpers would preserve
   the non-data surface and keep optional dependency concerns alive.

   Alternative considered: keep deprecated no-op shims. This reduces breakage but
   makes the public API misleading and keeps imports for features the package no
   longer supports.

2. Keep data extraction classes and methods even when their domain name includes
   trading language.

   Rationale: `Trading.price_board`, `Quote.intraday`, `foreign_trade`, and
   similar methods return market data, which is part of the retained financial
   data scope. DNSE broker order/account actions are different because they
   authenticate and operate on a brokerage account.

   Alternative considered: remove every `trading`-named class/module. This would
   incorrectly remove market data functionality that users still need.

3. Delete or disconnect non-data modules from package exports and docs first,
   then remove dead modules when tests confirm no retained data paths import
   them.

   Rationale: the riskiest failures are stale imports from top-level exports,
   `vnstock.ui`, package `__init__` files, and docs/tests. Removing public routing
   first establishes the contract, then dead code cleanup can follow safely.

   Alternative considered: delete files first. That can create noisy import
   failures before the intended public API boundary is updated.

4. Keep OpenSpec `show_api` documentation separate from runtime `show_api`.

   Rationale: this change removes the runtime Python helpers `show_api`,
   `show_doc`, and `show_docs`. It does not remove OpenSpec files, repository
   docs required for development, or normal README/API examples that describe the
   retained data APIs.

   Alternative considered: remove all documentation. That is broader than the
   request and would reduce maintainability.

## Risks / Trade-offs

- Public API breakage for users importing removed helpers/modules -> document the
  breaking change and provide migration guidance to use external charting,
  notification, documentation, or broker libraries directly.
- Hidden imports from retained code may reference removed modules -> add focused
  import tests for top-level package, Unified UI domains, and retained legacy data
  classes.
- Optional dependency cleanup can be incomplete -> grep for removed module names,
  extras, docs, and tests, then run focused lint/import checks.
- DNSE removal may surprise users who considered broker account data part of
  financial data -> explicitly distinguish market data from broker account/order
  operations in docs and tests.

## Migration Plan

1. Add failing tests for removed public exports/imports and retained data-only
   APIs.
2. Remove `show_api`, `show_doc`, `show_docs`, `Broker`, visualization, bot, and
   DNSE broker exports from top-level and UI modules.
3. Delete or disconnect non-data implementation modules and tests.
4. Remove optional dependencies and documentation references tied only to the
   removed features.
5. Verify retained imports and focused tests for Reference, Market, Fundamental,
   Retail, legacy Quote/Listing/Company/Finance/Trading/Fund, and FMP data
   credential behavior.
6. Run formatting/linting and the strongest available test command.

Rollback strategy: revert the change or restore removed modules/exports from the
previous commit if downstream consumers require the non-data APIs.

## Open Questions

- Should removed modules raise explicit import errors with migration messages for
  one release, or should the files be deleted immediately? The proposal favors
  deletion/disconnection because the user requested removal, but implementation
  can choose the smallest safe path.
