## ADDED Requirements

### Requirement: Runtime shall not require vnstock-managed users
The package SHALL import and expose its public data-access APIs without registering a vnstock user, reading `VNSTOCK_API_KEY`, checking tier status, or initializing vnstock-managed access-control state.

#### Scenario: Import without user configuration
- **WHEN** an application imports `vnstock` without `VNSTOCK_API_KEY` or vnstock user configuration
- **THEN** the import succeeds without prompting for registration, initializing a user session, or printing tier information

#### Scenario: Public data API without registration gate
- **WHEN** an application constructs a public `vnstock` API object or Unified UI object
- **THEN** construction does not require `register_user()`, API-key registration, or tier validation

### Requirement: Legacy registration helpers shall be inert
Legacy helper names for vnstock-managed registration SHALL NOT register users, store keys, initialize `vnai`, alter access permissions, or perform tier checks.

#### Scenario: Legacy register helper is called
- **WHEN** downstream code calls `register_user()` or `register_user(api_key=...)`
- **THEN** the helper performs no registration side effects and communicates that vnstock-managed registration is no longer used

#### Scenario: Legacy status helper is called
- **WHEN** downstream code calls `check_status()`
- **THEN** the helper does not query tier status and returns or reports a flat open access state

#### Scenario: Legacy key change helper is called
- **WHEN** downstream code calls `change_api_key(...)`
- **THEN** the helper does not persist the key and does not alter package access behavior

### Requirement: Tier concepts shall be absent from active behavior
The package SHALL NOT expose active Guest, Community, Sponsor, subscription, entitlement, quota-tier, or vnstock user-tier behavior.

#### Scenario: Runtime messages are emitted
- **WHEN** the package emits runtime logs, warnings, errors, or helper output
- **THEN** those messages do not instruct the user to register for vnstock tiers or upgrade package access tiers

#### Scenario: Documentation describes access model
- **WHEN** users read current setup, auth, or integration documentation
- **THEN** the documentation describes a flat open package model rather than vnstock-managed users or tiers

### Requirement: Unified UI shall not dispatch to sponsor packages
Unified UI dispatch SHALL resolve only implementations provided by this repository and SHALL NOT detect, import, or call `vnstock_data` or other sponsor/private packages as a fallback.

#### Scenario: Sponsor package is installed in the environment
- **WHEN** `vnstock_data` is installed alongside `vnstock`
- **THEN** calls through `vnstock` Unified UI use only this package's providers/connectors or fail according to this package's own registry behavior

### Requirement: Private-package migration and update flows shall be removed
The package SHALL NOT provide active runtime flows that migrate code to sponsor/private packages or prompt users to install private subscription packages.

#### Scenario: Package update notice runs
- **WHEN** version or update notice code executes
- **THEN** it does not query private package indexes or recommend sponsor/private package upgrades

#### Scenario: Migration helper is requested
- **WHEN** callers look for active migration behavior to `vnstock_data`
- **THEN** the package provides no code-rewriting migration path to sponsor/private packages

### Requirement: Third-party provider credentials shall remain provider-scoped
Credentials required by external services SHALL remain supported only as provider-specific configuration and SHALL NOT be treated as vnstock user registration, tier, or entitlement state.

#### Scenario: External API provider requires a key
- **WHEN** a provider such as FMP requires its own API key
- **THEN** the provider can accept that key through provider-specific configuration without involving `VNSTOCK_API_KEY` or vnstock registration helpers

#### Scenario: Broker connector requires login state
- **WHEN** a broker connector such as DNSE requires username/password, JWT, trading token, or OTP state
- **THEN** that state remains scoped to the broker connector and does not create vnstock-managed user or tier state
