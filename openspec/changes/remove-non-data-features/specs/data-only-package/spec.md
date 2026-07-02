## ADDED Requirements

### Requirement: Data extraction APIs remain available
The package SHALL retain public APIs for financial, securities, market, and fund
data extraction.

#### Scenario: Unified UI data domains import successfully
- **WHEN** an application imports `Reference`, `Market`, `Fundamental`, and `Retail` from `vnstock`
- **THEN** the imports succeed without requiring visualization, notification, broker, or API documentation helper modules

#### Scenario: Legacy data classes import successfully
- **WHEN** an application imports `Quote`, `Listing`, `Company`, `Finance`, `Trading`, `Fund`, and `Vnstock` from `vnstock`
- **THEN** the imports succeed and remain part of the public data extraction surface

### Requirement: Visualization surfaces are absent
The package SHALL NOT expose active visualization or charting APIs as part of the
public package surface.

#### Scenario: Top-level charting helpers are unavailable
- **WHEN** an application imports the public `vnstock` package
- **THEN** charting helpers such as `Chart`, `get_chart`, or DataFrame `.viz` extension behavior are not exported by `vnstock`

#### Scenario: Visualization module is not part of supported runtime
- **WHEN** an application attempts to use `vnstock.common.viz` for charting
- **THEN** the package does not provide active charting behavior and directs users to external charting libraries if a migration message is retained

### Requirement: Notification and bot surfaces are absent
The package SHALL NOT expose notification bot integrations or messaging helper
APIs.

#### Scenario: Messaging integrations are unavailable
- **WHEN** an application imports `vnstock`
- **THEN** Slack, Telegram, Discord, and Lark notification helpers are not exported as supported package APIs

#### Scenario: Bot module does not handle third-party messaging credentials
- **WHEN** an application tries to use the old bot notification path
- **THEN** the package does not send messages or manage messaging tokens/webhooks

### Requirement: Runtime API documentation helpers are absent
The package SHALL NOT expose runtime helper functions for showing the API tree or
rendering API documentation.

#### Scenario: API helper exports are removed
- **WHEN** an application imports `vnstock`
- **THEN** `show_api`, `show_doc`, and `show_docs` are not available from the top-level package

#### Scenario: UI helper exports are removed
- **WHEN** an application imports `vnstock.ui`
- **THEN** `show_api` and `show_doc` are not available from the UI package

### Requirement: Broker execution surfaces are absent
The package SHALL NOT expose broker account, order execution, or trading-token
connectors as supported public APIs.

#### Scenario: Broker UI is unavailable
- **WHEN** an application imports `vnstock`
- **THEN** `Broker` is not available from the top-level package

#### Scenario: DNSE account and order actions are unavailable
- **WHEN** an application tries to use DNSE account, OTP, trading-token, place-order, cancel-order, or conditional-order APIs through `vnstock`
- **THEN** those broker execution surfaces are not provided by the package

### Requirement: Data provider credentials remain provider-scoped
The package SHALL keep credentials only where an external data provider requires
them for retained data extraction.

#### Scenario: FMP data credentials remain supported
- **WHEN** an application uses retained FMP data extraction with an FMP API key
- **THEN** the credential is accepted by the FMP provider/connector without creating package-level user, tier, or entitlement state

#### Scenario: Messaging and broker credentials are not managed
- **WHEN** visualization, notification, or broker execution features are removed
- **THEN** the package no longer accepts or stores credentials solely for those removed feature areas

### Requirement: Documentation describes a data-only package
The repository documentation SHALL describe `vnstock` as a data extraction
library and SHALL NOT advertise removed visualization, bot/notification,
runtime API-doc helper, or broker execution features as supported runtime APIs.

#### Scenario: README focuses on retained data capabilities
- **WHEN** a user reads the README
- **THEN** the documented feature set centers on financial, securities, market, and fund data extraction

#### Scenario: Removed features are not documented as supported APIs
- **WHEN** a user searches repository docs for visualization, notification, runtime API-doc helpers, or broker execution usage
- **THEN** any remaining references are migration notes, historical changelog entries, or development artifacts rather than current usage instructions
