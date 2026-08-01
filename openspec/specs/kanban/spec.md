# kanban Specification

## Purpose
TBD - created by archiving change kanban-visual-coordination. Update Purpose after archive.
## Requirements
### Requirement: Product MUST NOT expose an internal Kanban board UI
The authenticated product MUST NOT render a Kanban board at `/kanban` or any equivalent SPA route. The operational board for delivery is the GitHub Project `https://github.com/users/oalansilva/projects/1/views/1`.

#### Scenario: Former kanban route does not show the board
- **WHEN** an authenticated user navigates to `/kanban`
- **THEN** the system MUST NOT render the former `KanbanPage` board UI
- **AND** the user MUST be redirected to an existing product surface (default `/monitor`)

#### Scenario: Navigation has no internal kanban entry
- **WHEN** the user inspects the primary app navigation
- **THEN** there MUST be no nav item that links to an internal Kanban board route

### Requirement: Workflow kanban APIs MAY remain without a board UI
The system MAY keep `/api/workflow/kanban/*` endpoints for non-board consumers (for example Home snapshots and agent automation). Presence of those APIs MUST NOT imply a product board UI.

#### Scenario: API without board UI
- **WHEN** a client calls `/api/workflow/kanban/changes`
- **THEN** the API MAY return workflow change data
- **AND** that response alone MUST NOT require a `/kanban` page to exist in the product

### Requirement: Kanban MUST derive status from workflow runtime
The system MUST derive each card's workflow state from the workflow DB/runtime state that powers operational status.
`docs/coordination/<change>.md` MAY mirror that state for audit/readability, but it MUST NOT be the deciding live operational source.
Product operators MUST treat the GitHub Project Status as the visual board; runtime remains the technical source for APIs/agents.

#### Scenario: Coordination markdown is missing
- **WHEN** `docs/coordination/<change>.md` does not exist
- **THEN** workflow APIs MUST still expose the card from workflow runtime state
- **AND** missing coordination markdown alone MUST NOT block the runtime card state from being returned

#### Scenario: Coordination markdown disagrees with runtime
- **WHEN** workflow runtime state and `docs/coordination/<change>.md` disagree
- **THEN** workflow APIs MUST expose the workflow runtime state
- **AND** the coordination markdown MUST be treated as a mirror to reconcile later

### Requirement: Coordination MUST support DESIGN status
Workflow coordination MUST use the canonical `Status` as the operational state and MUST support design delivery metadata separately from status. Every card MUST pass `Design -> Aprovação de Design -> Pronto para Dev` on the official GitHub Project board before implementation.

#### Scenario: UI change enters design
- **WHEN** a card declares UI impact
- **THEN** it MUST pass through `Design` and `Aprovação de Design` before `Pronto para Dev`

#### Scenario: Design gate is mandatory for every card
- **WHEN** a card is started for implementation
- **THEN** it MUST NOT skip `Design`, `Aprovação de Design`, or `Pronto para Dev`
- **AND** chat requests such as `implemente` MUST NOT authorize skipping those columns

### Requirement: Column derivation MUST include DESIGN
The backend derivation logic MUST use the canonical persisted status and MUST NOT silently map unknown values to `Em desenvolvimento` or another column.

#### Scenario: Known status is rendered
- **WHEN** the API returns a canonical workflow status
- **THEN** the card MUST be rendered in the matching canonical column

#### Scenario: Unknown status is received
- **WHEN** the API or persisted record contains an unknown status
- **THEN** the system MUST report a machine-readable validation error
- **AND** it MUST NOT present the card as being under development
