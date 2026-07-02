## Context

The package currently initializes `vnai`, exposes user registration helpers, documents `VNSTOCK_API_KEY`, prints Guest/Community/Sponsor tier messages, detects `vnstock_data`, and can dispatch Unified UI calls into sponsor/private package classes when installed. Those behaviors are orthogonal to the desired library role: an embeddable data-access package whose runtime does not manage vnstock users, tiers, or paid-package routing.

The repository also contains legitimate third-party credentials for external integrations, such as FMP API keys, DNSE broker login tokens, and notification webhooks. Those credentials must remain distinct from removed vnstock-managed access control.

## Goals / Non-Goals

**Goals:**
- Make `vnstock` import and runtime behavior independent from vnstock-managed user registration, `VNSTOCK_API_KEY`, tier status, and `vnai` setup.
- Remove automatic sponsor/private-package handoff, including `vnstock_data` detection, migration prompts, and subscription/private package update messaging.
- Preserve functional integrations that require upstream credentials controlled outside vnstock, including FMP, DNSE, and notification connectors.
- Provide a clear migration path for callers that imported legacy registration helpers.

**Non-Goals:**
- Reimplement sponsor-only `vnstock_data` functionality that is not present in this repository.
- Remove credentials required by third-party services or broker APIs.
- Add a new centralized auth, entitlement, quota, or tenant-management system.
- Introduce new external dependencies.

## Decisions

### Decision: Convert vnstock-managed auth helpers to inert compatibility shims

`register_user()`, `change_api_key()`, and `check_status()` should no longer call `vnai`, read `VNSTOCK_API_KEY`, write API keys, display tiers, or affect data access. To reduce unnecessary import breakage, keep these names importable as compatibility shims that clearly report the package no longer uses vnstock-managed registration.

Alternative considered: remove the symbols completely. That is cleaner, but it creates immediate import failures for existing notebooks and tests even though callers can safely ignore these functions in the new flat model.

### Decision: Remove import-time `vnai` initialization and user-key test setup

Package import should not initialize `vnai`, call `vnai.setup()`, check user status, or register a key from `VNSTOCK_API_KEY`. Test setup should not auto-register users. Tests that need third-party provider credentials should configure those providers directly.

Alternative considered: keep `vnai` only as an optional dormant dependency. This preserves unused code paths and leaves unclear ownership of access control, so it should be removed from runtime paths touched by `vnstock`.

### Decision: Remove sponsor/private-package dispatch from Unified UI

`BaseUI._dispatch()` should resolve only providers and connectors registered in this package. It should not inspect whether `vnstock_data` is installed and should not instantiate classes from that package.

Alternative considered: keep sponsor dispatch behind an opt-in flag. That still preserves paid-package coupling and makes runtime behavior depend on environment state, which conflicts with the flat model.

### Decision: Keep third-party provider credentials provider-scoped

FMP API keys, DNSE login/session tokens, and notification webhook tokens should remain because they authenticate with external systems, not with vnstock's own user/tier layer. Their docs and errors should describe provider requirements without using vnstock tier language.

Alternative considered: remove all key/token handling. That would break broker, notification, and external provider integrations and would not match the requested scope.

### Decision: Remove private-package upgrade and migration flows

Runtime notices, helpers, and docs that direct users to `vnstock_data`, `vnii`, `vnstock_installer`, private indexes, or Sponsor tiers should be removed or rewritten as neutral open-package documentation.

Alternative considered: leave these only in changelog/history. Historical changelog entries can remain if needed for release history, but active runtime paths and current docs should not promote or depend on private-package flows.

## Risks / Trade-offs

- Existing users who relied on `VNSTOCK_API_KEY` registration for rate-limit tier messaging will lose that workflow -> document that `vnstock` no longer manages user identity or tiers.
- Existing users who installed both `vnstock` and `vnstock_data` may lose transparent sponsor fallback -> make the behavior explicit: this package only dispatches to its own providers/connectors.
- Compatibility shims could hide obsolete calls in downstream code -> emit or return clear messages that registration is no longer used, without performing side effects.
- Removing private-package update checks may reduce visibility into related package updates -> acceptable because this package should not manage private-package lifecycle.

## Migration Plan

1. Remove `vnai` initialization, user-key registration, tier messaging, and `VNSTOCK_API_KEY` test setup.
2. Replace legacy registration helpers with inert compatibility shims or remove active exports according to implementation review.
3. Remove sponsor/private-package detection and dispatch from Unified UI.
4. Remove migration/update flows for sponsor/private packages.
5. Update docs, agent instructions, and tests to describe the flat access model and provider-scoped credentials.
6. Run focused unit tests for imports, UI dispatch, auth helpers, and docs-sensitive test setup, then run repository verification where practical.

## Open Questions

- Should compatibility shims return success-like values for old notebooks, or should they raise a deprecation error to force cleanup?
- Should historical changelog entries mentioning sponsor/private packages remain as immutable release history, or be scrubbed for distribution branding consistency?
