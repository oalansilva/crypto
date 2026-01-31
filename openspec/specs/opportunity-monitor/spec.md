# opportunity-monitor Specification

## Purpose
TBD - created by syncing delta from change improve-opportunity-monitor. Dashboard for favorite strategies with hold status and distance to next signal.

## Requirements

### Requirement: Simplified Hold Status Display
The system SHALL display a clear binary indicator: HOLD (active position) or WAIT (no position). When holding, show distance to exit; when not holding, show distance to entry.

### Requirement: Distance to Next Status
The system SHALL always display percentage distance to the next relevant status change, with progress bar and color coding (Green &lt; 0.5%, Yellow 0.5–1%, Gray &gt; 1%).

### Requirement: Simplified Opportunity Monitor Dashboard
The system SHALL provide a dashboard at /monitor showing all favorite strategies. Each card shows: symbol, strategy name, hold status (HOLD/WAIT), distance to next status, current price. Strategies sorted by distance (closest first). Auto-refresh every 60 seconds.
