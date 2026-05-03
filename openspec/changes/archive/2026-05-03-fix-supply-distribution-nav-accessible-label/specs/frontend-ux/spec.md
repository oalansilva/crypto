## ADDED Requirements

### Requirement: Navigation exposes stable ASCII accessible labels for tested routes
The primary navigation SHALL expose stable ASCII accessible names for route links covered by role-based E2E tests while preserving the visible Portuguese labels.

#### Scenario: Supply Distribution link is found by ASCII accessible name
- **WHEN** an admin user opens the primary navigation
- **THEN** the Supply Distribution link is available by role with accessible name `Distribuicao`
- **AND** the visible menu text remains `Distribuição`
