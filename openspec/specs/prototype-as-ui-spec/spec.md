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

### Requirement: Published Design context does not dump prototype HTML
For `UI impact: affected`, Design and isolated critics SHALL treat the navigable prototype URL, screenshot, and digest as the review surface. Chat and `design.md` MUST NOT include the prototype HTML source. `/opsx:apply` MUST still load the approved prototype files from `frontend/public/prototypes/<change-or-card-slug>/` as the UI specification before any product UI code is written. This requirement does not reopen or weaken the existing apply-loads-prototype rule.

#### Scenario: Design comment links the screen, not the source
- **WHEN** a UI-affected Design handoff is published
- **THEN** the card has a **Protótipo navegável** HTTP URL plus digest/path
- **AND** neither the Gist nor `design.md` contains the prototype HTML source

#### Scenario: Apply still uses the file on disk
- **WHEN** apply proceeds for `UI impact: affected`
- **THEN** the implementer reads the prototype directory from disk
- **AND** absence of that path still blocks apply

### Requirement: Polish patches the prototype file
After critique, prototype edits SHALL be patches against the cloned file. The agent MUST NOT emit a full-file HTML rewrite as the polish/LLM step when a patch can express the delta.

#### Scenario: Polish does not rewrite the whole file in the LLM
- **WHEN** a P0/P1 prototype finding is fixed
- **THEN** the change is a patch to the existing prototype file
- **AND** the Design session MUST NOT paste a complete replacement HTML document into chat as the fix

