# strategy-secret-visibility Specification

## Purpose
Define which strategy implementation details are visible to common users and which remain admin-only.
## Requirements
### Requirement: Strategy secrets are only visible to admin users
The system MUST keep source code, credentials, tokens, raw diagnostics, internal mutation controls and implementation-only payloads admin-only while exposing the canonical functional transparency manifest to every authorized trader.

#### Scenario: Non-admin receives strategy payload
- **WHEN** a non-admin user requests a visible strategy
- **THEN** the response MUST include its canonical public identity, relevant effective parameters, used indicators, functions, participation and timestamped public series
- **AND** MUST omit source code, credentials, tokens, raw diagnostic aliases and internal analyzer payloads
- **AND** MUST preserve the protected flag for remaining implementation-only data without hiding the public manifest.

#### Scenario: Admin receives full strategy payload
- **WHEN** an admin user requests the same strategy
- **THEN** the response MUST include the same public manifest
- **AND** MAY additionally include original identifiers, raw configuration and technical diagnostics already authorized for audit.

#### Scenario: Operational decision context remains visible
- **WHEN** a non-admin user receives a protected strategy payload
- **THEN** the response MUST still include symbol, timeframe, decision status, distance, price context, tier, notes, signal history and the transparency manifest where available.

### Requirement: Strategy tooling is admin-only
The system MUST restrict APIs and routes that expose strategy templates, optimization schema, backtest configuration internals, or strategy mutation controls to admin users.

#### Scenario: Non-admin requests strategy tooling API
- **WHEN** a non-admin user requests a combo template, strategy metadata, backtest, optimization, or template mutation API
- **THEN** the system MUST reject the request with an authorization error

#### Scenario: Admin requests strategy tooling API
- **WHEN** an admin user requests a combo template, strategy metadata, backtest, optimization, or template mutation API
- **THEN** the system MUST preserve the existing admin behavior
