## ADDED Requirements

### Requirement: Monitor E2E validates expanded detail cards
The Monitor E2E suite SHALL validate card-only controls only after the corresponding table row has been expanded.

#### Scenario: Collapsed Monitor row has no detail card in DOM
- **WHEN** the Monitor renders a collapsed opportunity row
- **THEN** the corresponding `monitor-card-*` detail element is not present

#### Scenario: Expanded Monitor row exposes detail card controls
- **WHEN** the E2E test expands a Monitor table row
- **THEN** the corresponding `monitor-card-*` detail element is visible and its controls can be asserted
