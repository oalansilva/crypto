# Opportunity Monitor Specification (Simplified)

## ADDED Requirements

### Requirement: Simplified Hold Status Display
The system SHALL display a clear binary indicator showing whether each strategy has an active position (HOLD) or not.

#### Scenario: Position is holding
- **WHEN** a strategy has an active position (last signal was buy and no exit signal has occurred)
- **THEN** the card displays a green badge with "HOLD"
- **AND** `is_holding` is set to `true`
- **AND** the distance shown is the distance to exit signal

#### Scenario: Position is not holding
- **WHEN** a strategy has no active position (no buy signal or exit signal already occurred)
- **THEN** the card displays a gray badge with "WAIT"
- **AND** `is_holding` is set to `false`
- **AND** the distance shown is the distance to entry signal

### Requirement: Distance to Next Status
The system SHALL always display the percentage distance to the next relevant status change.

#### Scenario: Distance when holding
- **WHEN** `is_holding` is `true`
- **THEN** the system calculates and displays distance to exit signal
- **AND** distance is shown as a percentage (e.g., "2.5% to exit")
- **AND** a progress bar visualizes how close the position is to exit

#### Scenario: Distance when not holding
- **WHEN** `is_holding` is `false`
- **THEN** the system calculates and displays distance to entry signal
- **AND** distance is shown as a percentage (e.g., "0.8% to entry")
- **AND** a progress bar visualizes how close the strategy is to entry

#### Scenario: Distance formatting
- **WHEN** distance is displayed
- **THEN** it is formatted with 2 decimal places (e.g., "0.45%")
- **AND** color coding indicates urgency:
  - Green: < 0.5% (very close)
  - Yellow: 0.5% - 1.0% (approaching)
  - Gray: > 1.0% (far away)

### Requirement: Simplified Opportunity Monitor Dashboard
The system SHALL provide a dashboard that prioritizes clarity and simplicity, showing only essential information.

#### Scenario: User views monitor
- **WHEN** user navigates to `/monitor` page
- **THEN** the page displays all favorite strategies
- **AND** each card shows: symbol, strategy name, hold status (HOLD/WAIT), distance to next status, current price
- **AND** strategies are sorted by distance (closest to status change first)
- **AND** strategies in HOLD are visually distinct from those waiting

#### Scenario: Auto-refresh
- **WHEN** the monitor page is open
- **THEN** opportunities are automatically refreshed every 60 seconds
- **AND** a loading indicator is shown during refresh
- **AND** timestamp of last update is displayed

#### Scenario: Sorting by distance
- **WHEN** user views the monitor
- **THEN** strategies are sorted by `distance_to_next_status` (ascending)
- **AND** strategies closest to status change appear first
- **AND** user can optionally sort by symbol alphabetically

## MODIFIED Requirements

### Requirement: Opportunity Card Display (Simplified)
The opportunity card component SHALL display simplified information focused on hold status and distance.

#### Scenario: Simplified card layout
- **WHEN** an opportunity card is rendered
- **THEN** card shows symbol and timeframe in header
- **AND** hold status badge is prominently displayed (green "HOLD" or gray "WAIT")
- **AND** current price is shown with currency formatting
- **AND** distance to next status is displayed prominently with progress bar
- **AND** card has left border color: green for HOLD, gray for WAIT
- **AND** message shows context: "X% to exit" or "X% to entry"

#### Scenario: Progress visualization
- **WHEN** distance is less than 1%
- **THEN** a progress bar shows visual representation
- **AND** progress bar fills as distance approaches 0%
- **AND** color matches urgency (green/yellow/gray)

## REMOVED Requirements

### Requirement: Complex Status Classification
**Reason**: Too many status categories (BUY_SIGNAL, BUY_NEAR, EXIT_SIGNAL, EXIT_NEAR, NEUTRAL) create confusion. Users only need to know: holding or not, and how close to change.

**Migration**: All existing status values will be mapped to:
- `is_holding: true` for HOLDING status
- `is_holding: false` for all other statuses
- `distance_to_next_status` calculated from existing distance field

### Requirement: Status-based Filtering
**Reason**: With only two states (HOLD/WAIT), complex filtering is unnecessary. Simple sorting by distance is sufficient.

**Migration**: Remove status filter UI. Keep only distance-based sorting.
