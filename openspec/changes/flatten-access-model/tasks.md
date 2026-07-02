## 1. Baseline Tests

- [x] 1.1 Add or update tests that import `vnstock` without `VNSTOCK_API_KEY` and assert no registration prompt, tier output, or `vnai` setup is required.
- [x] 1.2 Add or update tests for `register_user()`, `change_api_key()`, and `check_status()` to verify they are inert compatibility shims with no key persistence or tier checks.
- [x] 1.3 Add or update Unified UI dispatch tests to verify installed sponsor/private packages such as `vnstock_data` are not detected or called.
- [x] 1.4 Add or update tests that confirm third-party provider credentials remain provider-scoped for FMP, DNSE, and notification integrations where practical.

## 2. Remove vnstock-Managed User Access

- [x] 2.1 Remove import-time `vnai` setup and vnstock-managed user initialization from `vnstock/__init__.py`.
- [x] 2.2 Replace active behavior in `vnstock/core/utils/auth.py` with inert compatibility shims that do not read `VNSTOCK_API_KEY`, store keys, query status, or print tier messaging.
- [x] 2.3 Update `vnstock/core/utils/__init__.py` and package exports so legacy helper imports remain consistent with the chosen shim behavior.
- [x] 2.4 Remove the autouse `VNSTOCK_API_KEY` registration fixture behavior from `tests/conftest.py` and adjust tests that depended on it.

## 3. Remove Sponsor And Private Package Coupling

- [x] 3.1 Remove import-time sponsor detection and warning behavior from `vnstock/__init__.py` and `vnstock/core/utils/env.py`.
- [x] 3.2 Remove `vnstock_data` lookup and sponsor fallback dispatch from `vnstock/ui/_base.py`.
- [x] 3.3 Remove unused sponsor helper functions from `vnstock/ui/helper.py` or reduce the module to non-sponsor helper behavior.
- [x] 3.4 Remove active sponsor migration and private subscription update flows from `vnstock/core/utils/upgrade.py`.
- [x] 3.5 Remove private/subscription package references such as `vnii`, `vnstock_installer`, and private index upgrade requirements from runtime config paths.
- [x] 3.6 Rework chart backend selection in `vnstock/common/viz.py` so it does not promote or auto-prefer private paid packages.

## 4. Documentation And Messaging

- [x] 4.1 Update `README.md` to remove vnstock user registration, `VNSTOCK_API_KEY`, tier, sponsor, and paid upgrade setup guidance.
- [x] 4.2 Update `AGENTS.md` to describe the flat open access model and the distinction between vnstock-managed access and third-party provider credentials.
- [x] 4.3 Update provider module docstrings and current documentation that instruct agents or users to recommend `vnstock_data` or sponsor upgrade paths.
- [x] 4.4 Decide whether historical `CHANGELOG.md` sponsor/private references remain as release history or are scrubbed for current distribution branding.

## 5. Verification

- [x] 5.1 Search the repository for active references to `VNSTOCK_API_KEY`, `register_user`, `change_api_key`, `check_status`, `vnai`, `vnstock_data`, Sponsor, Community, Guest, `vnii`, `vnstock_installer`, and private index URLs; classify any remaining references as intentional or remove them.
- [x] 5.2 Run focused tests covering package import, auth helper shim behavior, Unified UI dispatch, and affected docs/test setup.
- [ ] 5.3 Run `make verify` when the focused checks pass, or document any environment blocker.

  Attempted with a temporary verification venv on `PATH`; formatter and linter passed, but the all-files pre-commit `end-of-file-fixer` hook failed by modifying unrelated `assets/data/schemas/*.json` EOF newlines. Those generated schema-only edits were reverted to keep this change scoped.
