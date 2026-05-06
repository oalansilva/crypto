## ADDED Requirements

### Requirement: Favorites View Trades recovers missing history
The Favorites page SHALL recover missing trade history for visible admin favorites instead of treating a missing `metrics.trades` array as no trades when summary metrics indicate trades exist.

#### Scenario: User clicks View Trades for favorite without saved trades
- **WHEN** an admin user clicks `View Trades` for a favorite with `total_trades` greater than zero and no saved `metrics.trades`
- **THEN** the UI SHALL request regenerated trades from the Favorites API
- **AND** the trade modal SHALL render the returned trades

#### Scenario: Regenerated trades have metric mismatch
- **WHEN** the Favorites API reports `metrics_match=false`
- **THEN** the UI SHALL warn the user that regenerated trades do not fully match the saved summary metrics

#### Scenario: Protected favorite remains redacted
- **WHEN** a protected favorite is shown to a non-admin user
- **THEN** the UI SHALL NOT request regenerated protected trades
