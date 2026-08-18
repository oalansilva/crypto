## ADDED Requirements

### Requirement: New app routes require Playwright functional and visual specs
Any new product route added to the app router (`frontend/src/App.tsx` or equivalent) MUST have a corresponding Playwright spec under `frontend/tests/e2e/` covering functional behavior and versioned desktop/mobile screenshots. Absence of that spec without an authorized visual-QA dispensation MUST fail a dedicated CI check and therefore `qa-gate`.

#### Scenario: New route without spec fails CI
- **WHEN** `App.tsx` gains a new `Route` path and no matching spec exists in `frontend/tests/e2e/`
- **AND** the card does not have `qa-visual-skip` plus Alan's comment `QA visual dispensado por Alan.` with a non-empty `Motivo:`
- **THEN** the coverage check fails naming the route and the expected spec path
- **AND** `qa-gate` does not succeed

#### Scenario: New route with desktop and mobile snapshots
- **WHEN** a new route ships with functional and visual specs
- **THEN** the visual spec records versioned snapshots for desktop and mobile in `*-snapshots/`
- **AND** those files are reviewable in the PR diff

#### Scenario: Authorized dispensation
- **WHEN** the linked card has `qa-visual-skip` and Alan's required dispensation comment
- **THEN** the missing-spec check records the reason and does not fail solely for the missing visual spec

### Requirement: Existing routes are inventoried, not silently skipped
The check SHALL compare current product router paths against a committed inventory of already-covered or explicitly grandfathered routes so legacy gaps do not fail every pipeline until they are closed as follow-up work. The check MUST ignore `PrototypeRedirect`, `/prototypes/*`, and `Navigate` alias/index routes; those are not new product screens.

#### Scenario: Unchanged grandfathered route
- **WHEN** an existing route is listed in the inventory as covered or grandfathered
- **AND** the route path did not change
- **THEN** the new-route check passes for that path

#### Scenario: Prototype redirect is not a product route
- **WHEN** `App.tsx` contains `PrototypeRedirect` or a `/prototypes/*` path
- **THEN** the coverage check MUST NOT require a visual product spec for that path

#### Scenario: Alias Navigate is covered by the destination
- **WHEN** a route only `Navigate`s to an existing page (for example `/kanban` → `/monitor`)
- **THEN** the check treats it as covered by the destination inventory entry, not as a new screen
