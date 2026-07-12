## ADDED Requirements

### Requirement: Functional indicator configuration is not hidden as a strategy secret
The system MUST expose indicator periods, thresholds, semantic roles, direction and risk settings required to interpret a visible strategy while continuing to protect implementation-only information.

#### Scenario: Common trader opens protected strategy chart
- **WHEN** a common authorized trader opens a protected strategy
- **THEN** the public manifest and chart MUST show the same functional indicator configuration needed to understand the signal
- **AND** MUST continue to omit source code, credentials, raw diagnostics, mutation controls and non-public logic expressions
