## ADDED Requirements

### Requirement: Monitor public signal language uses Compra and Venda
The Monitor SHALL present public decision labels as `Compra` and `Venda` instead of exposing `HOLD` and `EXIT` to end users. Internal raw statuses MAY remain unchanged for classification, API compatibility, logs, and tests.

#### Scenario: User views Monitor summary and sections
- **WHEN** the user opens `/monitor`
- **THEN** the visible summary tags and actionable section headers SHALL use `Compra` for active buy/position state
- **AND** the visible summary tags and actionable section headers SHALL use `Venda` for exit/sell state
- **AND** the user SHALL NOT see `HOLD` or `EXIT` as primary Monitor decision labels.

#### Scenario: Technical state remains internal
- **WHEN** Monitor receives raw status values such as `HOLDING`, `HOLD`, `EXIT_SIGNAL`, or `EXITED`
- **THEN** the resolver MAY continue using those values internally
- **AND** the user-facing badge text SHALL still render as `Compra` or `Venda`.
