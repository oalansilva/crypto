## ADDED Requirements

### Requirement: Chart modal renders above app chrome
Chart modal overlays SHALL render outside nested app containers with enough stacking priority to remain visible above navigation and page chrome.

#### Scenario: User opens a chart modal on Monitor
- **WHEN** the chart modal is opened
- **THEN** the overlay appears above the application chrome and remains usable

### Requirement: Chart user-facing labels are localized
Chart visualization UI SHALL use Portuguese labels for trader-facing messages introduced by this change.

#### Scenario: Chart data is unavailable
- **WHEN** a chart has no candle data to render
- **THEN** the user-facing empty state is displayed in Portuguese
