# monitor-active-entry-confirmation Specification

## Purpose
TBD - created by archiving change issue-124-align-ada-hold-chart-signal. Update Purpose after archive.
## Requirements
### Requirement: Monitor HOLD requires active entry confirmation
The Monitor SHALL expose `HOLD` as an active position only when the strategy has a confirmed entry signal that has not been superseded by a later exit signal. A strategy without active entry confirmation SHALL remain non-actionable for the main Monitor board and MUST NOT be exposed as a visible `WAIT` status.

#### Scenario: Trend is bullish but no entry exists
- **WHEN** strategy indicators are in a bullish trend
- **AND** strategy signal history has no confirmed entry signal
- **THEN** the opportunity is not returned as an active `HOLD`
- **AND** the main Monitor board does not expose the opportunity as a visible `WAIT` decision.

#### Scenario: Entry exists and no later exit exists
- **WHEN** strategy signal history has a confirmed entry signal
- **AND** there is no later exit signal
- **THEN** the opportunity can be returned as active `HOLD`.

#### Scenario: Exit exists after entry
- **WHEN** strategy signal history has a confirmed exit after the latest confirmed entry
- **THEN** the opportunity is not returned as active `HOLD`
- **AND** the next decision points to re-entry or entry context.

### Requirement: Chart modal preserves Monitor decision state
The Monitor chart modal SHALL keep the same primary decision label as the Monitor list for the same opportunity when the payload status is actionable, even when candle freshness or marker visibility requires contextual warning text.

#### Scenario: Holding opportunity remains Compra in chart detail
- **WHEN** the Monitor list shows an opportunity as `Compra`
- **AND** the detailed chart detects a candle or marker context mismatch
- **THEN** the chart modal SHALL keep `Compra` as the primary badge and current marker
- **AND** the chart modal SHALL explain the mismatch in signal context

#### Scenario: Exit opportunity remains Venda in chart detail
- **WHEN** the Monitor list shows an opportunity as `Venda`
- **AND** the detailed chart detects a candle or marker context mismatch
- **THEN** the chart modal SHALL keep `Venda` as the primary badge and current marker
- **AND** the chart modal SHALL explain the mismatch in signal context

