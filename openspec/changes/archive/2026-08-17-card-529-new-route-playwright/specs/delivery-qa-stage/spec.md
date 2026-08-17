## ADDED Requirements

### Requirement: QA cannot close Done on a new route without Playwright evidence
A card that adds a product route MUST NOT move to Done while the route lacks functional+visual Playwright coverage, unless Alan recorded the auditable visual-QA dispensation.

#### Scenario: Done blocked without spec
- **WHEN** the delivery added a new `App.tsx` route and no spec or dispensation exists
- **THEN** the card MUST remain outside Done
