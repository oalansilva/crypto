# favorite-backtest-refresh Specification

## Purpose

Keep favorited strategy backtests fresh through an internal scheduled backend routine.

## ADDED Requirements

### Requirement: Favorite backtests refresh automatically
The system SHALL refresh due favorited backtests through an internal backend routine without requiring user interaction.

#### Scenario: Daily refresh runs for due favorites
- **WHEN** the backend worker starts the favorite refresh routine
- **THEN** it SHALL select favorites that never completed a refresh or completed before the configured refresh interval
- **AND** it SHALL rerun each due favorite using the saved symbol, timeframe, strategy, direction, period start, and fixed parameter ranges
- **AND** it SHALL persist refreshed metrics, trades, candles, and indicator context on the favorite

#### Scenario: One favorite refresh fails
- **WHEN** one favorite refresh raises an error
- **THEN** the routine SHALL persist failure status and error for that favorite
- **AND** it SHALL continue processing other due favorites
- **AND** it SHALL preserve the favorite's previous metrics

#### Scenario: Favorite refresh returns stale market data
- **WHEN** a favorite refresh completes its calculation but the newest returned candle is older than the tolerated freshness window for the favorite timeframe
- **THEN** the routine SHALL persist failure status and error for that favorite
- **AND** it SHALL preserve the favorite's previous metrics instead of marking stale results as refreshed

### Requirement: Favorite refresh attempts are auditable
The system SHALL record refresh attempts in both the favorite row and `auto_backtest_runs`.

#### Scenario: Refresh succeeds
- **WHEN** a favorite refresh completes successfully
- **THEN** the favorite SHALL store success status, start timestamp, completion timestamp, and run id
- **AND** `auto_backtest_runs` SHALL store a successful run linked to the favorite

#### Scenario: Refresh fails
- **WHEN** a favorite refresh fails
- **THEN** the favorite SHALL store failed status, start timestamp, completion timestamp, run id, and error message
- **AND** `auto_backtest_runs` SHALL store a failed run linked to the favorite

### Requirement: Refresh routine is internal
The system SHALL run favorite refresh from the backend worker and SHALL NOT expose it as a user-facing OpenClaw workflow.

#### Scenario: Runtime worker is enabled
- **WHEN** `RUN_FAVORITE_BACKTEST_REFRESH` is enabled
- **THEN** the backend worker SHALL start the favorite refresh loop
- **AND** shutdown SHALL stop the loop cleanly
