# favorites-trade-regeneration Specification

## Purpose
TBD - created by archiving change card-141-favorites-trades. Update Purpose after archive.
## Requirements
### Requirement: Favorite trades can be regenerated
The system SHALL regenerate missing favorite trade history from the favorite's stored strategy parameters using the same optimization pipeline that creates favorites from `/combo/select` when the current user is allowed to view the strategy details.

#### Scenario: Favorite has summary metrics but no saved trades
- **WHEN** an authorized user requests trades for a favorite that has `total_trades` greater than zero and no `metrics.trades`
- **THEN** the backend SHALL run combo optimization with the favorite's stored strategy, symbol, timeframe, direction, dates, and fixed parameter ranges derived from the saved best parameters
- **AND** the backend SHALL return the regenerated trades

#### Scenario: Favorite already has saved trades
- **WHEN** an authorized user requests trades for a favorite that already has `metrics.trades`
- **THEN** the backend SHALL return the saved trades without requiring regeneration

### Requirement: Regenerated trades are validated against favorite metrics
The system SHALL compare regenerated summary metrics with stored favorite metrics before reporting regenerated trades as valid.

#### Scenario: Regenerated metrics match stored metrics
- **WHEN** regenerated metrics match stored metrics within numeric tolerance
- **THEN** the backend SHALL return `metrics_match=true`
- **AND** the backend SHALL persist regenerated trades into the favorite metrics

#### Scenario: Regenerated metrics differ from stored metrics
- **WHEN** regenerated metrics differ from stored metrics beyond numeric tolerance
- **THEN** the backend SHALL return `metrics_match=false`
- **AND** the response SHALL include per-metric deltas for the compared values

### Requirement: Protected favorites do not expose trade regeneration
The system MUST NOT expose regenerated protected strategy details to users who cannot view strategy secrets.

#### Scenario: Common user requests protected favorite trades
- **WHEN** a non-admin user requests trades for an admin catalog favorite whose strategy is protected
- **THEN** the backend SHALL reject the request without exposing parameters, trades, or regenerated metrics

### Requirement: Optimized favorites retain source trades
The system SHALL persist the source trades returned by combo optimization into favorite metrics when favorites are created from `/combo/select` or batch optimization.

#### Scenario: Single optimized favorite is saved
- **WHEN** `/combo/select` optimizes one symbol and saves the resulting favorite
- **THEN** the favorite metrics SHALL include the optimization response `trades` array

#### Scenario: Batch optimized favorite is saved
- **WHEN** batch optimization saves a favorite for a symbol
- **THEN** the favorite metrics SHALL include the optimization result `trades` array

