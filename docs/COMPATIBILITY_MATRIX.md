# Compatibility Matrix vs Upstream

This matrix compares this data-only fork with the upstream `vnstock` package line
where the removed surfaces historically lived. Use it to decide whether existing
code can run unchanged or needs a migration.

| Area | Upstream package line | This data-only fork | Compatibility |
| --- | --- | --- | --- |
| Project scope | Stock analysis toolkit with data extraction plus convenience surfaces. | Data extraction library only. | Intentional scope reduction. |
| Python support | Python 3 package. | `>=3.10`; classifiers include 3.10 through 3.14. | Compatible for supported Python versions. |
| Installation metadata | Runtime dependencies may include convenience integration packages. | Runtime dependencies are aligned to data extraction only; dev/build pins are frozen in `requirements.lock`. | Reinstall from this fork's metadata or lockfile. |
| Unified UI data domains | `Reference`, `Market`, `Fundamental`, and related data domains. | `Reference`, `Market`, `Fundamental`, and `Retail`. | Supported and preferred. |
| Legacy data imports | `Quote`, `Listing`, `Company`, `Finance`, `Trading`, `Vnstock`. | Same retained top-level data imports. | Supported for data use cases. |
| Provider routing | Source-specific data providers. | Provider registry plus Unified UI routing and optional cache layer. | Supported; explicit `source=` still selects a provider directly. |
| Flat access model | May include package-level user/account helper flows. | No package-level registration, tiers, entitlement gates, or private-package fallback routing. | Applications should not rely on package-managed user state. |
| FMP data connector | External data API connector. | Retained; credentials are provided directly to the FMP connector or environment. | Supported with provider-scoped credentials. |
| DNSE market data | DNSE-related market data and broker surfaces may both exist upstream. | DNSE market data is retained under `vnstock.explorer.dnse`; broker execution is removed. | Market-data calls supported; order/account calls must migrate. |
| Charting | `Chart`, pandas `.viz`, or bundled visualization convenience APIs. | Removed. | Use DataFrame output with app-level chart libraries. |
| Documentation helpers | Runtime helpers such as `show_api`, `show_doc`, and `show_docs`. | Removed. | Use README, notebooks, and `docs/` files. |
| Bot notifications | Messenger-style Slack, Telegram, Discord, or Lark notifications. | Removed. | Use notification provider SDKs directly. |
| Broker execution | Broker UI/domain and DNSE trade/login/account/order execution. | Removed. | Use broker APIs outside `vnstock`. |
| CI expectations | Project-specific. | GitHub Actions runs Ruff, deterministic non-slow pytest core/ui/unified-ui suites, and sdist/wheel build. Provider integration tests are excluded from default CI because they may call external services. | This fork enforces data-only quality gates without depending on live provider availability. |

## Migration Summary

- Data extraction code should prefer the Unified UI and generally remains
  compatible.
- Code that imports charting, notifications, broker execution, or runtime doc
  helpers must move those concerns into the application layer.
- DNSE data usage remains available; DNSE broker execution does not.
- Use `requirements.lock` when a reproducible dev/test/build environment is
  needed.
