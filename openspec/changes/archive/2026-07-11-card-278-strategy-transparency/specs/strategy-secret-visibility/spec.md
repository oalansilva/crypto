## MODIFIED Requirements

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
