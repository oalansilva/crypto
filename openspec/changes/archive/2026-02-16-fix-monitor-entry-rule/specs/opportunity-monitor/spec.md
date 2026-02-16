## MODIFIED Requirements

### Requirement: Simplified Hold Status Display
**Description:** The system SHALL display a clear binary indicator: HOLD (active position) or WAIT (no position). When holding, show distance to exit; when not holding, show distance to entry.

#### Scenario: HOLD distance shown
- **WHEN** the strategy is in HOLD status
- **THEN** the UI displays distance to exit

#### Scenario: WAIT distance shown
- **WHEN** the strategy is in WAIT status
- **THEN** the UI displays distance to entry

### Requirement: Distance to Next Status
**Description:** The system SHALL always display percentage distance to the next relevant status change, with progress bar and color coding (Green < 0.5%, Yellow 0.5–1%, Gray > 1%). When the status is WAIT (no position), the system SHALL compute the distance to entry using the entry rule: entry is valid only when (crossover(short, long) OR crossover(short, medium)) AND trend up (short > long). If trend up is false, the system SHALL measure distance using the short-to-long pair (red → blue). If trend up is true, the system SHALL measure distance using the short-to-medium pair (red → orange).

#### Scenario: WAIT with trend up false
- **WHEN** the strategy is in WAIT status and short <= long
- **THEN** the distance to entry is computed from the short-to-long pair (red → blue)

#### Scenario: WAIT with trend up true
- **WHEN** the strategy is in WAIT status and short > long
- **THEN** the distance to entry is computed from the short-to-medium pair (red → orange)

### Requirement: Simplified Opportunity Monitor Dashboard
**Description:** The system SHALL provide a dashboard at /monitor showing all favorite strategies. Each card shows: symbol, strategy name, hold status (HOLD/WAIT), distance to next status, current price. Strategies sorted by distance (closest first). Auto-refresh every 60 seconds.

#### Scenario: Dashboard shows favorite strategies
- **WHEN** the user opens /monitor
- **THEN** the dashboard lists all favorite strategies with symbol, strategy name, hold status, distance, and current price

#### Scenario: Sorted by distance
- **WHEN** multiple strategies are listed
- **THEN** the cards are sorted by closest distance first
