## ADDED Requirements

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

## REMOVED Requirements

### Requirement: System MUST provide a Kanban board for active + archived changes
**Reason:** Board operacional oficial é o GitHub Project 1; a UI interna `/kanban` foi descontinuada.
**Migration:** Operar cards em `https://github.com/users/oalansilva/projects/1/views/1`. Bookmarks `/kanban` redirecionam para `/monitor`.

### Requirement: Card details MUST show tasks checklist
**Reason:** Checklist era parte da UI Kanban interna removida.
**Migration:** Tasks continuam em OpenSpec/`tasks.md` e evidência no card do Project 1; APIs de tasks podem permanecer para automação.

### Requirement: Comments MUST be supported per change
**Reason:** Thread de comentários da UI Kanban interna foi removida com a página.
**Migration:** Comentários operacionais no GitHub Issue/Project; endpoint de comments pode permanecer sem UI.

### Requirement: Minimal auth assumptions
**Reason:** Requisito amarrado à navegação `/kanban`.
**Migration:** Sem rota de board; sessão do app permanece para demais superfícies.

### Requirement: Kanban MUST include a DESIGN column (always visible)
**Reason:** Lentes/colunas eram da UI interna.
**Migration:** Colunas de Design ficam no GitHub Project 1.

### Requirement: Kanban MUST support explicit intra-column card ordering
**Reason:** Reorder visual era da UI interna.
**Migration:** Ordenação/prioridade no Project 1 conforme processo atual.

### Requirement: Reorder MUST not bypass workflow gates
**Reason:** Acoplado à UI de reorder do board interno.
**Migration:** Gates continuam no workflow/Project; sem UI interna de reorder.

### Requirement: Design approval MUST be performed by Alan through an explicit board move
**Reason:** Texto referia drag/drawer do Kanban interno.
**Migration:** Aprovação humana continua sendo o arraste `Aprovação de Design -> Pronto para Dev` no GitHub Project 1 (somente Alan).

### Requirement: Design delivery MUST be visible before approval
**Reason:** Drawer do Kanban interno removido.
**Migration:** Evidência de design/protótipo permanece nos artifacts OpenSpec e comentário do card no Project 1.

### Requirement: Kanban interaction MUST expose transition failures
**Reason:** Feedback de drag/mobile do board interno removido.
**Migration:** Transições/erros operacionais via Project/workflow tooling, sem UI `/kanban`.

## MODIFIED Requirements

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
