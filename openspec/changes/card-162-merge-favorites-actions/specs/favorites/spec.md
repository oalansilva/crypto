## ADDED Requirements

### Requirement: Favorites uses one analysis action for results and trades
The Favorites page SHALL expose a single analysis action per favorite for users allowed to inspect strategy details, and that flow SHALL show consolidated results and the trade list together.

#### Scenario: Admin reviews a favorite
- **WHEN** an admin user opens the Favorites page
- **THEN** each visible favorite SHALL expose one primary analysis action
- **AND** the row SHALL NOT expose separate `View Trades` and `View Results` actions

#### Scenario: Admin opens combined analysis
- **WHEN** an admin user activates the favorite analysis action
- **THEN** the system SHALL navigate to the result view for that favorite
- **AND** the result view SHALL include consolidated metrics
- **AND** the result view SHALL include the list of trades
- **AND** the result view SHALL provide a visible action to return to Favorites

#### Scenario: Admin reopens saved combined analysis
- **WHEN** an admin user activates the favorite analysis action for a favorite that already has `metrics.trades` and saved chart context
- **THEN** the UI SHALL open the result view using the saved favorite history
- **AND** the UI SHALL NOT request a new combo backtest
- **AND** the UI SHALL NOT regenerate favorite trades

#### Scenario: Admin opens legacy saved trades without chart context
- **WHEN** an admin user activates the favorite analysis action for a favorite with `metrics.trades` but without saved chart context
- **THEN** the UI SHALL request the Favorites API to backfill the analysis cache
- **AND** the result view SHALL include candles for the chart when regeneration returns candles
- **AND** the Favorites API SHALL persist the backfilled chart context so later opens use saved history

#### Scenario: Admin reads combined analysis trades
- **WHEN** the result view renders the favorite trade list
- **THEN** trade table headers and cells SHALL use readable contrast aligned to `DESIGN.md`
- **AND** labels such as `Type`, `Date and time`, and `Signal` SHALL remain legible

#### Scenario: Protected favorite remains protected
- **WHEN** a protected favorite is rendered
- **THEN** the unified analysis action SHALL NOT expose protected strategy parameters or trade regeneration to unauthorized users

## MODIFIED Requirements

### Requirement: Favorites View Trades recovers missing history
The Favorites page SHALL recover missing trade history through the unified favorite analysis action instead of treating a missing `metrics.trades` array as no trades when summary metrics indicate trades exist.

#### Scenario: User opens analysis for favorite without saved trades
- **WHEN** an admin user opens the unified analysis action for a favorite with `total_trades` greater than zero and no saved `metrics.trades`
- **THEN** the UI SHALL request regenerated trades from the Favorites API
- **AND** the result view SHALL render the returned trades
- **AND** the Favorites API SHALL persist the regenerated trades on the favorite so a later open can use saved history

#### Scenario: Regenerated trades have metric mismatch
- **WHEN** the Favorites API reports `metrics_match=false`
- **THEN** the Favorites API SHALL accept the regenerated metrics as the new saved summary for that favorite
- **AND** the Favorites API SHALL persist the previous summary and metric deltas as investigation metadata
- **AND** the UI SHALL open the result view without showing the reconstructed-history mismatch warning
- **AND** the same favorite SHALL NOT regenerate on every open

#### Scenario: Protected favorite remains redacted
- **WHEN** a protected favorite is shown to a non-admin user
- **THEN** the UI SHALL NOT request regenerated protected trades
