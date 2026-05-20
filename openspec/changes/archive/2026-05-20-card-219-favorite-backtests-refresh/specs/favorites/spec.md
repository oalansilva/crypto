# favorites Specification Delta

## ADDED Requirements

### Requirement: Favorites expose automatic backtest refresh state
The Favorites API and UI SHALL expose the last automatic refresh state for each favorite strategy.

#### Scenario: User lists favorites after an automatic refresh
- **WHEN** a user opens Favorites
- **THEN** each favorite response SHALL include refresh status, refresh run id, start timestamp, completion timestamp, and error when available
- **AND** the Favorites UI SHALL show a compact last update/status line for each favorite

#### Scenario: Protected favorite is listed
- **WHEN** a protected favorite is listed for a common user
- **THEN** refresh metadata MAY be shown
- **AND** protected strategy parameters and implementation details SHALL remain redacted
