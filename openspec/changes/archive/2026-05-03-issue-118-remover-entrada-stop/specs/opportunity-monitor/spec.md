## MODIFIED Requirements

### Requirement: Simplified Hold Status Display
**Description:** The system SHALL display a clear binary indicator: HOLD (active position) or WAIT (no position). When holding, show distance to exit; when not holding, show distance to entry.
When the resolved state is EXIT, the monitor SHALL hide entry/stop operational lines from both card and chart views, because those values are no longer actionable.

#### Scenario: Opportunity in HOLD state
- **WHEN** the strategy is in HOLD status
- **THEN** the UI displays distance to exit

#### Scenario: Opportunity in WAIT state
- **WHEN** the strategy is in WAIT status
- **THEN** the UI displays distance to entry

#### Scenario: Opportunity in EXIT state
- **WHEN** an opportunity resolves to EXIT
- **THEN** card and chart entries for Entry/Stop are hidden and no new entry/stop price guidance is shown.
