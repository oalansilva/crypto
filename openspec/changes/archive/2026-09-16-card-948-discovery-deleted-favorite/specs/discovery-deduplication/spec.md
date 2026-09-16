## ADDED Requirements

### Requirement: Deleted favorite is not an active match

When a favorite is removed from the list by real deletion (the product today deletes the row; it does not archive or inactivate it), the system SHALL stop treating that favorite as an active duplicate or promotion target. Results previously classified `duplicate_favorite` or `already_promoted` against that favorite SHALL become current `unique` (append-only reclassification; prior evidence remains queryable for audit). The leaderboard and promotion paths SHALL also re-read whether the referenced favorite still exists, so a stale stored classification cannot keep lying. The grid SHALL NOT show a historical-favorite note. Internal audit MAY record the reclassification; that trail SHALL NOT appear on the Discovery row.

#### Scenario: Duplicate of a deleted favorite becomes unique

- **GIVEN** a persisted result classified `duplicate_favorite` with reference N
- **AND** favorite N has been deleted from the list
- **WHEN** Discovery reads that result
- **THEN** the current classification is `unique`
- **AND** no historical-favorite note is attached for the grid

#### Scenario: Already-promoted origin of a deleted favorite becomes unique

- **GIVEN** a persisted result classified `already_promoted` because it created favorite N
- **AND** favorite N has been deleted from the list
- **WHEN** Discovery reads that result
- **THEN** the current classification is `unique`
- **AND** the row is not treated as still being that favorite

#### Scenario: Live favorite still blocks

- **GIVEN** a result equivalent to a favorite that still exists
- **WHEN** Discovery classifies or re-reads it
- **THEN** it remains `duplicate_favorite` with that favorite as reference
