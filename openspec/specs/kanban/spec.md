# kanban Specification

## Purpose
TBD - created by archiving change kanban-visual-coordination. Update Purpose after archive.
## Requirements
### Requirement: System MUST provide a Kanban board for active + archived changes
The system MUST provide a Kanban UI page that lists workflow work items in the canonical order:
- Todo
- Design
- Aprovação de Design
- Pronto para Dev
- Em desenvolvimento
- Code Review
- QA
- Done
- Homologado
- Pronto
- Cancelado

#### Scenario: Canonical columns appear
- **WHEN** the user opens the Kanban
- **THEN** every workflow card MUST appear in exactly one canonical status
- **AND** `In Progress` MUST be shown as `Em desenvolvimento`

#### Scenario: Terminal cards remain consultable
- **WHEN** a card is `Pronto` or `Cancelado`
- **THEN** the Kanban MUST keep it consultable without treating OpenSpec archival alone as publication evidence

### Requirement: Kanban MUST derive status from workflow runtime
The system MUST derive each card's workflow state from the workflow DB/runtime state that powers Kanban.
`docs/coordination/<change>.md` MAY mirror that state for audit/readability, but it MUST NOT be the deciding live operational source.

#### Scenario: Coordination markdown is missing
- **WHEN** `docs/coordination/<change>.md` does not exist
- **THEN** the Kanban MUST still display the card from workflow runtime state
- **AND** missing coordination markdown alone MUST NOT block the runtime card state from being shown

#### Scenario: Coordination markdown disagrees with runtime
- **WHEN** workflow runtime state and `docs/coordination/<change>.md` disagree
- **THEN** the Kanban MUST display the workflow runtime state
- **AND** the coordination markdown MUST be treated as a mirror to reconcile later

### Requirement: Card details MUST show tasks checklist
The system MUST render a checklist view of `openspec/changes/<change>/tasks.md`.

#### Scenario: Tasks displayed
- **WHEN** a user opens a Kanban card
- **THEN** the UI MUST show the tasks and their checked/unchecked state

### Requirement: Comments MUST be supported per change
The system MUST support a comments thread per change.

#### Scenario: Add comment
- **WHEN** a user posts a comment on a change
- **THEN** the comment MUST be stored and shown in the thread

### Requirement: Minimal auth assumptions
The Kanban UI MUST use the existing app session model (no new public exposure requirements).

#### Scenario: Access via existing app
- **WHEN** the user navigates to `/kanban`
- **THEN** the UI MUST load using the existing app frontend and backend routing
- **AND THEN** it MUST NOT require any new public-facing exposure beyond the existing app access

### Requirement: Kanban MUST include a DESIGN column (always visible)
The Kanban MUST provide `Design`, `Aprovação de Design`, and `Pronto para Dev` before `Em desenvolvimento`, while preserving access to the complete canonical order.

#### Scenario: Product and design lens
- **WHEN** the user selects the `Produto e Design` lens
- **THEN** the board MUST show `Todo`, `Design`, `Aprovação de Design`, and `Pronto para Dev` in that order

#### Scenario: Delivery lens
- **WHEN** the user selects the `Entrega` lens
- **THEN** the board MUST show `Pronto para Dev`, `Em desenvolvimento`, `Code Review`, `QA`, `Done`, `Homologado`, and `Pronto` in that order

#### Scenario: Complete lens
- **WHEN** the user selects the complete board lens
- **THEN** the board MUST expose the entire canonical order without changing any card status

### Requirement: Coordination MUST support DESIGN status
Workflow coordination MUST use the canonical `Status` as the operational state and MUST support design delivery metadata separately from status.

#### Scenario: UI change enters design
- **WHEN** a card declares UI impact
- **THEN** it MUST pass through `Design` and `Aprovação de Design` before `Pronto para Dev`

#### Scenario: Non-UI change bypasses design
- **WHEN** a card declares `UI impact: none` with a non-empty justification
- **THEN** it MAY move from `Todo` to `Pronto para Dev`
- **AND** the bypass reason MUST remain visible and auditable

### Requirement: Column derivation MUST include DESIGN
The backend derivation logic MUST use the canonical persisted status and MUST NOT silently map unknown values to `Em desenvolvimento` or another column.

#### Scenario: Known status is rendered
- **WHEN** the API returns a canonical workflow status
- **THEN** the card MUST be rendered in the matching canonical column

#### Scenario: Unknown status is received
- **WHEN** the API or persisted record contains an unknown status
- **THEN** the system MUST report a machine-readable validation error
- **AND** it MUST NOT present the card as being under development

### Requirement: Kanban MUST support explicit intra-column card ordering
The system MUST let the user change the relative order of cards within the same Kanban column so the visible sequence represents pull priority.

#### Scenario: Move card upward within the same column
- **GIVEN** a column contains at least two active cards
- **WHEN** the user requests moving a card upward
- **THEN** the system MUST persist the new relative order inside that same column
- **AND** the board MUST refresh automatically showing the card in the new position

#### Scenario: Order persists after reload
- **WHEN** the board is reloaded after a successful reorder
- **THEN** the cards in that column MUST appear in the same persisted order

### Requirement: Reorder MUST not bypass workflow gates
Changing the order of cards MUST NOT act as a status transition between workflow columns.

#### Scenario: Reorder stays inside the current column
- **WHEN** the user reorders a card
- **THEN** the card MUST remain in its current workflow column
- **AND** no approval/gate state may be implicitly changed

### Requirement: Design approval MUST be performed by Alan through an explicit board move
The board MUST treat `Aprovação de Design -> Pronto para Dev` as the human design approval and MUST offer drag-and-drop plus an accessible equivalent action.

#### Scenario: Alan approves by dragging
- **GIVEN** a card in `Aprovação de Design` has a valid design delivery
- **WHEN** authenticated Alan drags it to `Pronto para Dev`
- **THEN** the backend MUST persist the status and human approval atomically
- **AND** the board MUST show who approved, when, and which design version was approved

#### Scenario: Keyboard or touch approval
- **GIVEN** Alan cannot or does not use drag-and-drop
- **WHEN** he activates the equivalent `Aprovar design` action in the card drawer
- **THEN** the system MUST execute the same authenticated transition and present the same confirmation

#### Scenario: Agent or unauthorized user attempts approval
- **WHEN** an agent or unauthorized user attempts `Aprovação de Design -> Pronto para Dev`
- **THEN** the backend MUST reject it without trusting a client-supplied actor
- **AND** the card MUST remain in `Aprovação de Design`

### Requirement: Design delivery MUST be visible before approval
Cards with UI impact MUST expose `design.md`, versioned prototype evidence, agent critique, and delivery validity from the Kanban.

#### Scenario: Complete design delivery
- **WHEN** a user opens a card in `Aprovação de Design`
- **THEN** the drawer MUST show links or references for the design and prototype
- **AND** it MUST show the critique verdict and current approval validity

#### Scenario: Incomplete delivery cannot request approval
- **WHEN** a UI-impact card lacks design, prototype evidence, or critique verdict
- **THEN** moving it from `Design` to `Aprovação de Design` MUST be rejected with actionable missing-item details

### Requirement: Kanban interaction MUST expose transition failures
Every board move MUST provide equivalent success and error feedback on desktop, keyboard, touch, and mobile flows.

#### Scenario: Desktop transition rejected
- **WHEN** a desktop drag transition is rejected by the backend
- **THEN** the card MUST return to its source column
- **AND** the user MUST see an actionable error message

#### Scenario: Mobile transition succeeds
- **WHEN** a valid mobile status action succeeds
- **THEN** the board MUST refresh and announce the new status accessibly
