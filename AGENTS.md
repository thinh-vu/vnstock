# Agent Notes for vnstock

## Setup And Commands
- Python package, `requires-python >=3.10`; install local dev tooling with `pip install -e ".[dev]"` or test-only tooling with `pip install -e ".[test]"`.
- Required local verification is `make verify`; it runs `ruff check --fix .`, `ruff format .`, `ruff check .`, `pre-commit run --all-files`, then pytest.
- Faster focused checks: `make lint`, `make format`, `make pre-commit`, `PYTHONPATH=. pytest tests/unit/api/test_quote.py`, or `PYTHONPATH=. pytest tests/unified_ui/test_registry.py`.
- `make test` first runs `PYTHONPATH=. pytest tests/unified_ui/`, then `PYTHONPATH=. pytest tests/`; expect `tests/unified_ui` to run twice.
- `pytest.ini` is the active pytest config: strict markers/config, verbose output by default, 300s timeout. Use `PYTHONPATH=.` for local tests to force the working tree package.
- Tests do not auto-register package-level user keys. Integration tests may call external services; configure provider-specific credentials directly when needed.

## Architecture
- Public package entrypoint is `vnstock/__init__.py`; it exports legacy API classes (`Quote`, `Listing`, `Company`, `Finance`, `Trading`, `Vnstock`) plus v4 Unified UI (`Reference`, `Market`, `Fundamental`, `Retail`). `Broker`, `show_api`, `show_doc`, visualization (`Chart`/`.viz`), and bot/notification (`Messenger`) have been removed.
- New user-facing APIs should go through the Unified UI under `vnstock/ui`. Top-level domain objects create subdomain objects; leaf methods route through `BaseUI._dispatch()` using `vnstock/ui/_registry.py::MAP`.
- Keep `vnstock.ui` as facade/routing only. Put data extraction in providers, not UI methods. No charting, no notifications, no broker execution in this package.
- Provider split: `vnstock/explorer/{kbs,vci,msn,fmarket,misc,dnse}` for scraping/public web data; `vnstock/connector/fmp` for the FMP data API connector; `vnstock/api/*` are legacy adapters built on `vnstock/base.py::BaseAdapter`. The `vnstock/connector/dnse` broker connector has been removed; DNSE market data lives in `vnstock/explorer/dnse`.
- Provider modules self-register at import time with `vnstock.core.registry.ProviderRegistry.register(provider_type, source, Class)`. Add providers by registration and MAP entries, not UI `if/else` source branching.
- `vnstock/core/base/registry.py` is a separate decorator-style registry; do not confuse it with the active `vnstock.core.registry.ProviderRegistry` used by `vnstock/base.py`.
- `BaseUI._dispatch()` auto-selects providers via `vnstock/core/router.py::ProviderRouter` (round-robin + cooldown). Multi-provider pools are declared in `vnstock/ui/_pools.py::POOLS`. Callers that pass `source=` explicitly bypass the router. Add a new pool entry to `_pools.py` when a new provider supports an existing method.

## Repo-Specific Gotchas
- Flat access model: do not add package-level user registration, tier gates, entitlement checks, or private-package fallback routing. Keep external provider credentials scoped to their connector/provider.
- UI modules intentionally use lazy runtime imports and `TYPE_CHECKING` blocks to avoid circular imports. Preserve that pattern when adding domain accessors or type hints.
- Ruff is the local formatter/linter source of truth: line length 88, target `py310`, double quotes, lint families `E/W/F/I/B/C4` with `E501` ignored.
- Do not add third-party dependencies unless explicitly approved; there is no lockfile in this repo.
- Repo-local OpenSpec/OpenCode workflow exists under `.opencode/commands/opsx-*.md` and `openspec/`; use `/opsx-propose`, `/opsx-apply`, `/opsx-explore`, or `/opsx-archive` only when the user asks for that workflow.
