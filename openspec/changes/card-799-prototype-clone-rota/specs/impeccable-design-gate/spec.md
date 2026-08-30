## ADDED Requirements

### Requirement: Existing-route prototype MUST clone live-route landmarks
For `UI impact: affected` when the surface already exists, the prototype MUST clone the authenticated live route page (listing, headers, actions, expand) and apply only the card delta inside that topology. Shell width 224px, `--bg-*` tokens, and the token sheet MUST NOT be treated as sufficient fidelity. Blocking fidelity is the versioned landmark catalog for that route.

#### Scenario: Monitor proto without listing landmarks is P0
- **WHEN** Assessment A or B reviews a `/monitor` prototype that has sidebar 224px and correct tokens but lacks `table.signals` or headers `Status` / `Preço` / `Risco até stop` / `Operar`
- **THEN** the verdict MUST be `BLOCKED` with a P0 fidelity finding
- **AND** chrome-only PASS is forbidden

#### Scenario: Delta stays inside the live topology
- **WHEN** a card changes a detail on an existing route
- **THEN** the prototype URL shows the same listing/actions landmarks as the live route
- **AND** the card delta is inside that topology, not a parallel layout

### Requirement: Gallery of states is P0 on list-plus-detail routes
When the live product is list-plus-detail, a prototype that renders N states as N cards in a grid MUST be a P0. Named anti-pattern: “N estados ⇒ N cards numa grelha”. This SHALL NOT treat a live template grid (Combo `/combo/select`) as that anti-pattern when the catalog landmarks for that route are present.

#### Scenario: Four-card gallery for Monitor is P0
- **WHEN** a `/monitor` prototype is a 2×2 gallery of state cards instead of `table.signals` plus row expand
- **THEN** Assessment MUST record P0
- **AND** T5 clone gate MUST classify that HTML as BLOCKED against `/monitor`

### Requirement: Dual critic opens the live route URL
When a session exists, Assessment A/B SHALL open the live DEV URL of the declared route and the prototype URL. A missing listing landmark on the prototype versus the live route is P0. Without a session, the critic MUST NOT treat `/login` as the live route. Authenticated Playwright MUST NOT run inside `submeter_design`.

#### Scenario: Login page is not the live route
- **WHEN** the critic has no session and the live URL redirects to `/login`
- **THEN** it MUST NOT treat login chrome as clone evidence
- **AND** it MUST NOT emit PASS on shell-only comparison to `/login`

#### Scenario: Session compares live listing to proto
- **WHEN** a session exists and `live_route` is `/monitor`
- **THEN** the critic opens the live `/monitor` URL and the prototype URL
- **AND** absence of a catalog listing landmark on the prototype is P0

### Requirement: Antes/Depois toggle MUST change the view
If the prototype exposes an Antes/Depois control, Antes MUST be the clone without the card delta and Depois MUST be clone+delta. A control that only flips `aria-pressed` without changing the view MUST be P0 when it is the only offered proof of clone. T5 SHALL NOT verify the toggle (offline static check).

#### Scenario: Dead toggle is P0
- **WHEN** the only clone evidence is an Antes/Depois button whose `aria-pressed` changes and the listing markup does not
- **THEN** Assessment MUST record P0
- **AND** T5 still uses landmarks and `copied`, not the toggle

## MODIFIED Requirements

### Requirement: Prototype clone+delta without HTML dump
For an existing product surface, the prototype MUST clone the live route page — listing, headers, actions, and expand, plus shell/nav/tokens/density — and apply only the card delta. Cloning only the current shell/nav/tokens/density is not sufficient. Design, critics, and operator chat MUST use the navigable URL, screenshot, and digest — they MUST NOT dump prototype HTML into chat or `design.md`. `/opsx:apply` MUST still read the prototype file on disk as the layout spec. Polish MUST patch the prototype file; it MUST NOT rewrite the whole HTML in the LLM. New surfaces still compose from the token sheet plus the authenticated app shell, not a generic landing; new surfaces are exempt from catalog/`copied` when `surface: new` or `live_route: N/A` is declared.

#### Scenario: Critics review URL and digest
- **WHEN** Assessment A or B reviews a UI-affected prototype
- **THEN** the spawn context includes the HTTP URL, screenshot, and digest
- **AND** it does not include the prototype HTML source as chat payload

#### Scenario: Apply still reads the prototype file
- **WHEN** `/opsx:apply` implements a UI-affected card
- **THEN** it reads `frontend/public/prototypes/<change-or-card-slug>/` from disk as the layout spec
- **AND** it does not treat `design.md` bullets as a replacement for that file

#### Scenario: Polish is a patch
- **WHEN** targeted Impeccable fixes land on the prototype
- **THEN** the edit is a patch to the existing file
- **AND** the LLM MUST NOT emit a full-file HTML rewrite as the polish step

#### Scenario: Existing route clone includes listing landmarks
- **WHEN** Design clones an existing product surface such as `/monitor`
- **THEN** the prototype HTML contains the catalog landmarks for that route
- **AND** sidebar 224px plus `--bg-*` tokens alone MUST NOT pass fidelity
