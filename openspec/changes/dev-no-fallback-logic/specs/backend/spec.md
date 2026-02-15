# Δ backend Specification - dev-no-fallback-logic

## MODIFIED Requirements

### Requirement: Dev correction precedes fallback logic
**Description:** When validation fails for `entry_logic` or `exit_logic`, the system SHALL require Dev correction to produce valid boolean expressions and MUST NOT apply simplification fallback logic.

#### Scenario: Invalid logic is rewritten to valid boolean format
- **GIVEN** `entry_logic` and/or `exit_logic` is invalid during preflight
- **WHEN** the validation failure is detected
- **THEN** the system MUST request Dev rewrite and revalidate the rewritten expressions
- **AND** the system MUST continue only if rewritten `entry_logic` and `exit_logic` are valid boolean expressions
- **AND** the system MUST NOT replace logic with EMA/RSI or any other simplified fallback

#### Scenario: Rewrite fails to produce valid boolean logic
- **GIVEN** invalid `entry_logic` or `exit_logic` cannot be rewritten into valid boolean format
- **WHEN** correction attempts are exhausted or correction fails validation
- **THEN** the system MUST stop execution with a validation error
- **AND** the system MUST NOT execute the run using fallback strategy logic

### Requirement: Corrections must be logged
**Description:** The system SHALL persist correction metadata in run trace for invalid logic handling, including original logic, rewritten logic, validation result, reason, and explicit no-fallback status.

#### Scenario: Correction log is persisted with no-fallback evidence
- **GIVEN** a correction attempt is performed for invalid `entry_logic` or `exit_logic`
- **WHEN** the run proceeds or fails after validation
- **THEN** the trace MUST record original logic, rewritten logic, validation result, and correction reason
- **AND** the trace MUST identify Dev as the correction actor
- **AND** the trace MUST explicitly indicate that no EMA/RSI simplification fallback was applied
