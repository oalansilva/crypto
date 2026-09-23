## ADDED Requirements

### Requirement: Every record carries the model version that answered

Every diagnostic record of a model call and of a cycle with a model reply SHALL carry the model version that answered (the `model` field of the reply). This SHALL happen unconditionally, not only when the optional raw-payload record is enabled. When the reply carries no model identifier, the record SHALL show `unknown` instead of omitting the field.

#### Scenario: Reply with a model version

- **WHEN** a model reply carries a model version identifier
- **THEN** the call return record and the cycle record for that reply SHALL both show that version
- **AND** the version SHALL be present with the raw-payload record disabled

#### Scenario: Reply without a model version

- **WHEN** a model reply carries no model identifier
- **THEN** the record SHALL show the model version as `unknown`

### Requirement: The call requests a fixed model version, never the moving alias

The request sent to the model SHALL carry a fixed model version identifier instead of the moving alias that changes when the provider publishes (`jev-latest`). The fixed identifier SHALL be the configured/pinned version, and the request SHALL never send the alias again.

#### Scenario: Request body carries the pinned version

- **WHEN** the scalp requests the model
- **THEN** the request body's `model` SHALL be the fixed version identifier
- **AND** it SHALL NOT be `jev-latest`

#### Scenario: The alias does not come back through configuration

- **WHEN** the pinned version is not overridden by configuration
- **THEN** the request SHALL still use the fixed version identifier
- **AND** SHALL NOT fall back to the moving alias

### Requirement: Pinning the version does not change the question

Pinning the model version SHALL NOT change the question asked to the model: the questions (`side` choice, `expected_move_bp` score and its levels, `book_toxic` noul) and the state payload SHALL stay exactly as they are.

#### Scenario: The questions are untouched

- **WHEN** the request is built with the pinned version
- **THEN** the questions (`side`, `expected_move_bp`, `book_toxic`) and their types and criteria SHALL be the same as today
- **AND** the state payload sent to the model SHALL be unchanged
