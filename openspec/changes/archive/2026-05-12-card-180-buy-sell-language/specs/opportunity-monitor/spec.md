## ADDED Requirements

### Requirement: Opportunity Monitor chart and history use Compra and Venda labels
The opportunity monitor SHALL use `Compra` and `Venda` in card badges, chart current markers, and visible signal history labels while preserving raw signal types for computation.

#### Scenario: Opportunity card renders public label
- **WHEN** a visible Monitor opportunity resolves to an active position state
- **THEN** the card badge SHALL show `Compra`
- **AND** when the opportunity resolves to exit/sell state the card badge SHALL show `Venda`.

#### Scenario: Chart modal renders public signal labels
- **WHEN** the trader opens a Monitor chart modal for a visible opportunity
- **THEN** the current signal badge and signal history labels SHALL use `Compra` for entry/buy events
- **AND** SHALL use `Venda` for exit/sell events.

#### Scenario: Non-actionable state remains hidden
- **WHEN** an opportunity resolves to an internal wait or uncertain state
- **THEN** the main Monitor board SHALL keep excluding it from visible actionable rows
- **AND** SHALL NOT expose `WAIT` as a public third signal label.
