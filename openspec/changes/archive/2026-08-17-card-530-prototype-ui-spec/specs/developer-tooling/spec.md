## ADDED Requirements

### Requirement: OpenSpec apply skill loads the approved prototype for UI cards
The `/opsx:apply` skill SHALL include a mandatory step for `UI impact: affected`: read `design.md` and the approved HTML prototype before editing product UI files. API specs remain integration contracts only.

#### Scenario: Apply skill lists the prototype step
- **WHEN** an agent runs `/opsx:apply` on a UI-affected change
- **THEN** the skill instructs loading `frontend/public/prototypes/<slug>/` before coding UI
