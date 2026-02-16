## MODIFIED Requirements

### Requirement: Distance to Next Status
The system SHALL always display percentage distance to the next relevant status change, with progress bar and color coding (Green < 0.5%, Yellow 0.5–1%, Gray > 1%). When the status is WAIT (no position), the system SHALL compute the distance to entry using the entry rule: entry is valid only when (crossover(short, long) OR crossover(short, medium)) AND trend up (short > long). If trend up is false, the system SHALL measure distance using the short-to-long pair (red → blue). If trend up is true, the system SHALL measure distance using the short-to-medium pair (red → orange).

#### Scenario: WAIT with trend up false
- **WHEN** the strategy is in WAIT status and short <= long
- **THEN** the distance to entry is computed from the short-to-long pair (red → blue)

#### Scenario: WAIT with trend up true
- **WHEN** the strategy is in WAIT status and short > long
- **THEN** the distance to entry is computed from the short-to-medium pair (red → orange)
