# prototype-as-ui-spec Specification

## Purpose
O protótipo aprovado é a spec de UI no apply para cards com UI impact affected.

## Requirements
### Requirement: Approved prototype is the UI spec on apply
For a card with `UI impact: affected`, `/opsx:apply` MUST load `design.md` and the approved prototype at `frontend/public/prototypes/<change-or-card-slug>/` as the UI specification before any product UI code is written. The API contract MAY drive data/integration shape; it MUST NOT replace layout, components, states, or density.

#### Scenario: Apply without loading the prototype
- **WHEN** `UI impact: affected` and the apply handoff does not record that the approved prototype was loaded
- **THEN** apply is blocked and UI code is not written

#### Scenario: Apply records prototype elements followed
- **WHEN** apply proceeds for `UI impact: affected`
- **THEN** the card handoff/PR lists the prototype path and the prototype elements that were implemented

### Requirement: UI deviations from prototype are explicit
Any delivered UI that differs from the approved prototype MUST be justified in the handoff. Silent drift is forbidden.

#### Scenario: Unjustified drift
- **WHEN** the delivered route omits or changes a prototype element without a written justification
- **THEN** Code Review treats the drift as a blocking finding

### Requirement: Pre-review comparison against prototype
Before moving to `Code Review`, the implementer MUST compare the delivered route to the approved prototype (layout, components, states, a11y, responsiveness) and record the result in the handoff/PR.

#### Scenario: Code Review without comparison record
- **WHEN** the card is `UI impact: affected` and the handoff lacks the prototype comparison result
- **THEN** the card MUST NOT enter commit/QA as if review were complete

