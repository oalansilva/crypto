# monitor-active-entry-confirmation Specification

## Purpose
TBD - created by archiving change issue-124-align-ada-hold-chart-signal. Update Purpose after archive.
## Requirements
### Requirement: Monitor HOLD requires active entry confirmation
The Monitor SHALL expose `HOLD` as an active position only when the strategy has a confirmed entry signal that has not been superseded by a later exit signal.

#### Scenario: Trend is bullish but no entry exists
- **WHEN** strategy indicators are in a bullish trend
- **AND** strategy signal history has no confirmed entry signal
- **THEN** the opportunity is not returned as an active `HOLD`
- **AND** the opportunity remains in `WAIT` with entry distance context.

#### Scenario: Entry exists and no later exit exists
- **WHEN** strategy signal history has a confirmed entry signal
- **AND** there is no later exit signal
- **THEN** the opportunity can be returned as active `HOLD`.

#### Scenario: Exit exists after entry
- **WHEN** strategy signal history has a confirmed exit after the latest confirmed entry
- **THEN** the opportunity is not returned as active `HOLD`
- **AND** the next decision points to re-entry or entry context.

