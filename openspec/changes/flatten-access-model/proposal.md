## Why

`vnstock` currently mixes data-access behavior with user registration, API-key status, tier messaging, sponsor/private-package routing, and upgrade prompts. This makes the package harder to embed into another system that wants a flat, open library surface without caring about vnstock-managed users, tiers, or paid-package handoff.

## What Changes

- **BREAKING**: Remove vnstock-managed user registration and status behavior from the public runtime surface, including `VNSTOCK_API_KEY`, `register_user()`, `change_api_key()`, and `check_status()` as active access-control features.
- **BREAKING**: Remove Guest/Community/Sponsor tier concepts, rate-limit tier messages, and any behavior that depends on a vnstock user identity.
- **BREAKING**: Remove automatic sponsor/private-package detection and dispatch to `vnstock_data` from the free package runtime.
- Remove migration and upgrade prompts that route users toward sponsor/private packages such as `vnstock_data`, `vnii`, `vnstock_installer`, or private package indexes.
- Keep external provider credentials where the upstream service requires them, such as FMP API keys, DNSE broker login/session tokens, or notification webhooks.
- Document the distinction between vnstock-managed access control, which is removed, and third-party provider credentials, which remain provider-specific configuration.

## Capabilities

### New Capabilities
- `flat-access-model`: Defines the package access model as open and flat, with no vnstock-managed users, tiers, sponsor redirects, or paid-package runtime behavior.

### Modified Capabilities
- None.

## Impact

- Public API exports in `vnstock/__init__.py` and `vnstock/core/utils/__init__.py`.
- Auth/access utilities in `vnstock/core/utils/auth.py`, `vnstock/core/utils/env.py`, and `vnstock/core/utils/upgrade.py`.
- Unified UI dispatch in `vnstock/ui/_base.py` and sponsor helper functions in `vnstock/ui/helper.py`.
- Version/dependency metadata in `vnstock/config.py` where private/subscription packages are referenced.
- Documentation and agent guidance in `README.md`, `AGENTS.md`, provider module docstrings, and changelog text that mention tiers, sponsor packages, or paid upgrade paths.
- Tests that currently set up `VNSTOCK_API_KEY` or assert registration/tier behavior.
