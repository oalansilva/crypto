## ADDED Requirements

### Requirement: Favorites Preserve Strategy Direction

Favorites SHALL preserve strategy direction across save, list, regeneration and trade-analysis flows.

#### Scenario: Short favorite regeneration uses short direction

- **GIVEN** a saved favorite has `parameters.direction == "short"`
- **WHEN** `/api/favorites/{id}/trades` regenerates analysis
- **THEN** regeneration SHALL call the modern combo optimizer with `direction == "short"`
- **AND** returned trades SHALL use short-side profit and stop semantics

#### Scenario: Missing direction remains long compatible

- **GIVEN** an existing favorite does not include direction
- **WHEN** it is listed or regenerated
- **THEN** the system SHALL treat it as `long`
