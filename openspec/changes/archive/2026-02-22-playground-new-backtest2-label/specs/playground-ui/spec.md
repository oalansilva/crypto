## ADDED Requirements

### Requirement: Playground primary action label is "New Backtest2"
The system MUST display the primary Playground action label as "New Backtest2".

#### Scenario: Playground page renders primary action label
- **WHEN** the user opens the Playground page
- **THEN** the primary action label is exactly "New Backtest2"

#### Scenario: No functional behavior change from label rename
- **WHEN** the user clicks the primary action
- **THEN** the same backtest creation flow is triggered as before the rename
