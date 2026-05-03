## MODIFIED Requirements

### Requirement: Simplified Hold Status Display
**Description:** The system SHALL display a clear indicator: HOLD (confirmed active position), WAIT (no confirmed active position), or EXIT (position closed/exit state). `HOLD` MUST require an active entry confirmation from strategy signal history; bullish trend state alone MUST NOT create `HOLD`. When holding, show distance to exit; when not holding, show distance to entry.
When the resolved state is EXIT, the monitor SHALL hide entry/stop operational lines from both card and chart views, because those values are no longer actionable.

#### Scenario: Opportunity in HOLD state
- **WHEN** the strategy has a confirmed active entry
- **AND** no later exit invalidates that entry
- **THEN** the UI displays distance to exit

#### Scenario: Opportunity in WAIT state
- **WHEN** the strategy has no confirmed active entry
- **THEN** the UI displays distance to entry

#### Scenario: Bullish trend without entry confirmation
- **WHEN** the strategy indicators are bullish
- **AND** there is no confirmed active entry in signal history
- **THEN** the UI displays WAIT instead of HOLD

#### Scenario: Opportunity in EXIT state
- **WHEN** an opportunity resolves to EXIT
- **THEN** card and chart entries for Entry/Stop are hidden and no new entry/stop price guidance is shown.
