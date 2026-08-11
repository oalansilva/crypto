# favorite-backtest-refresh Specification

## Purpose
TBD - created by archiving change card-219-favorite-backtests-refresh. Update Purpose after archive.
## Requirements
### Requirement: Favorite backtests refresh automatically
The system SHALL refresh due favorited backtests through an internal backend routine without requiring user interaction.

#### Scenario: Daily refresh runs for due favorites
- **WHEN** the backend worker starts the favorite refresh routine
- **THEN** it SHALL select favorites that never completed a refresh or completed before the configured refresh interval
- **AND** it SHALL fetch and refresh the market data required by the favorite timeframe before recalculating the backtest
- **AND** for crypto deep backtests it SHALL prepare the required intraday candles before recalculating the backtest
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

### Requirement: Favorite refresh respects CPU guardrails
The system SHALL throttle the automatic favorite refresh routine so it does not continue starting refresh work while host CPU usage is above the configured ceiling, defaulting to 60 percent.

#### Scenario: CPU is above ceiling before next favorite
- **WHEN** the favorite refresh routine is about to start another due favorite
- **AND** measured CPU usage is above the configured ceiling
- **THEN** it SHALL pause or skip starting that favorite during the current cycle
- **AND** it SHALL record the CPU guard as the reason work was paused or skipped
- **AND** it SHALL keep already refreshed favorites committed

#### Scenario: CPU stays below ceiling
- **WHEN** measured CPU usage is at or below the configured ceiling
- **THEN** the routine SHALL continue processing due favorites up to the configured batch limit

### Requirement: Favorite refresh runs as a daily bounded cycle
The system SHALL run automatic favorite refresh as a bounded background cycle configured to attempt due favorites at least once per day while respecting batch limits and pauses.

#### Scenario: Runtime stack starts
- **WHEN** the standard crypto stack start script runs without explicit overrides
- **THEN** it SHALL enable the runtime worker and favorite refresh routine by default
- **AND** it SHALL keep a daily refresh interval by default
- **AND** it SHALL run the refresh loop more frequently than once per day so bounded batches can cover the due queue
- **AND** it SHALL use a bounded per-cycle favorite limit by default

#### Scenario: More favorites are due than the batch limit
- **WHEN** due favorites exceed the configured per-cycle limit
- **THEN** the routine SHALL process at most the configured number in that cycle
- **AND** it SHALL leave the remaining favorites due for later cycles

### Requirement: Favorite refresh runtime state is observable
The system SHALL expose safe operational state for the automatic favorite refresh routine through backend runtime status.

#### Scenario: Runtime status is requested
- **WHEN** `/api/runtime/status` is requested
- **THEN** the response SHALL include whether favorite refresh is enabled
- **AND** it SHALL include sanitized latest-cycle state including due, success, failed, skipped, CPU threshold, and reason when available

#### Scenario: Refresh cycle completes or pauses
- **WHEN** a favorite refresh cycle completes or stops because of CPU guardrails
- **THEN** the system SHALL update the latest-cycle state before waiting for the next cycle

