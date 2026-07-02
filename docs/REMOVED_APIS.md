# Removed APIs

This fork keeps `vnstock` focused on data extraction. Charting, bot notifications,
broker execution, and API documentation helper surfaces are intentionally outside
the package boundary.

## Removed Public Exports

| API | Previous purpose | Replacement |
| --- | --- | --- |
| `vnstock.Broker` | Broker execution entrypoint | Use the broker's official SDK or API directly. |
| `vnstock.ui.Broker` | Unified UI broker execution domain | Use broker integrations in application code. |
| `vnstock.show_api` | Runtime API listing helper | Use the README, notebooks, and `docs/` reference files. |
| `vnstock.show_doc` | Runtime documentation helper | Use the README, notebooks, and `docs/` reference files. |
| `vnstock.show_docs` | Runtime documentation helper alias | Use the README, notebooks, and `docs/` reference files. |

## Removed Modules And Classes

| Module or class | Status | Migration note |
| --- | --- | --- |
| `vnstock.common.viz.Chart` | Removed | Build charts from returned DataFrames with Plotly, Matplotlib, Seaborn, or `vnstock_ezchart` installed directly in your application. |
| Pandas `.viz` extension | Removed | Keep visualization code in the application layer. |
| `vnstock.bot.notify.Messenger` | Removed | Integrate Slack, Telegram, Discord, Lark, or other notification SDKs directly. |
| `vnstock.connector.dnse.trade.Trade` | Removed | Use DNSE or another broker execution API directly. |
| `vnstock.connector.dnse` broker login/account/order execution | Removed | Broker credentials and order routing are no longer package features. |
| `vnstock.ui.broker` and `vnstock.ui.domains.broker` | Removed | Unified UI exposes data domains only. |

Some removed modules remain as small tombstone modules with explanatory docstrings
so imports fail clearly when code reaches removed classes. They do not provide the
old runtime behavior.

## Still Supported

- Unified UI data domains: `Reference`, `Market`, `Fundamental`, and `Retail`.
- Legacy data adapters: `Quote`, `Listing`, `Company`, `Finance`, `Trading`,
  `Fund`, and `Vnstock`.
- Data providers under `vnstock.explorer.*` and `vnstock.connector.fmp`.
- DNSE market data under `vnstock.explorer.dnse` and data routing with
  `source="DNSE"` where supported.
- Provider-scoped credentials for external data connectors such as FMP.

## Dependency Boundary

Removed charting, notification, and broker execution integrations are not runtime
dependencies of this fork. If your application needs those capabilities, install
and configure those libraries directly in the application environment.
