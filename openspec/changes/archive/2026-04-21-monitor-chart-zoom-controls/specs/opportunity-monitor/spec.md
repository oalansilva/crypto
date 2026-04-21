## ADDED Requirements

### Requirement: Monitor chart modal exposes direct zoom actions
The opportunity monitor SHALL expose direct zoom-in and zoom-out actions when a trader opens the detailed chart for a strategy.

#### Scenario: Direct zoom is available after opening chart
- **WHEN** the trader opens a strategy chart from a Monitor card
- **THEN** the modal includes direct zoom actions in the chart controls area

#### Scenario: Zoom works alongside existing chart actions
- **WHEN** the trader uses zoom controls in the Monitor chart modal
- **THEN** the existing close action, timeframe selector, and indicator toggles remain available

### Requirement: Monitor zoom controls are accessible through click and keyboard focus
The opportunity monitor MUST expose zoom controls as standard interactive UI controls that can receive focus and activation without pointer gestures.

#### Scenario: Zoom button can receive focus
- **WHEN** the trader navigates through the chart modal controls with keyboard focus
- **THEN** the zoom-in and zoom-out controls are reachable as focusable elements

#### Scenario: Zoom action can be triggered without mouse wheel
- **WHEN** the trader activates a zoom control using keyboard or click
- **THEN** the visible chart range changes in the same way as the corresponding direct zoom action
