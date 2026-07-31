## MODIFIED Requirements

### Requirement: System MUST maintain workflow state in one operational source of truth
The system MUST store canonical workflow status, design delivery metadata, human approval evidence, comments, and ordering in the centralized workflow database.

#### Scenario: Change lifecycle stored centrally
- **WHEN** a change is created or updated
- **THEN** its canonical workflow state MUST be persisted in the workflow DB
- **AND** agents and UI MUST read the current state from that DB

#### Scenario: Agent handoff stored centrally
- **WHEN** Design, development, Code Review, or QA completes a handoff
- **THEN** status, evidence, handoff, and comment data MUST be recorded in the DB

#### Scenario: Human design approval stored centrally
- **WHEN** Alan approves a design
- **THEN** the DB MUST persist the authenticated approver, timestamp, design digest, and prototype version or digest

### Requirement: Workflow state MUST support a pre-PO pending stage
The runtime workflow model MUST create new backlog items in `Todo` and support the canonical pre-development sequence `Todo -> Design -> Aprovação de Design -> Pronto para Dev`.

#### Scenario: Create backlog item
- **WHEN** a user creates a new backlog card from Kanban
- **THEN** the runtime workflow record MUST be created in `Todo`
- **AND** the record MUST be queryable by the Kanban immediately

#### Scenario: UI work enters design
- **WHEN** a `Todo` card with UI impact starts product/design work
- **THEN** the runtime MUST persist `Design`
- **AND** it MUST not permit `Em desenvolvimento` before design approval

#### Scenario: Development is pulled
- **WHEN** a developer pulls an approved `Pronto para Dev` card
- **THEN** the runtime MUST persist `Em desenvolvimento`

### Requirement: Runtime updates from Kanban MUST be authoritative for board moves
The runtime workflow DB MUST accept authenticated Kanban-driven status transitions through one canonical transition service.

#### Scenario: Kanban move updates runtime
- **WHEN** an authorized user moves a card through a valid transition
- **THEN** the backend MUST persist the corresponding runtime state change
- **AND** subsequent Kanban reads MUST reflect the new column automatically

#### Scenario: Invalid transition is rejected
- **WHEN** a move skips a required gate, regresses a non-regressing state, or uses an unknown status
- **THEN** the backend MUST reject it with a machine-readable error response
- **AND** no duplicated route-level matrix MUST override the canonical transition service

#### Scenario: Design approval identity is server-derived
- **WHEN** a client requests `Aprovação de Design -> Pronto para Dev`
- **THEN** the backend MUST derive the approver from the authenticated session
- **AND** a client-provided actor MUST NOT authorize the transition

## ADDED Requirements

### Requirement: Workflow MUST enforce the canonical lifecycle
The workflow MUST use `Todo -> Design -> Aprovação de Design -> Pronto para Dev -> Em desenvolvimento -> Code Review -> QA -> Done -> Homologado -> Pronto`, with `Cancelado` as a terminal alternative.

#### Scenario: Happy-path lifecycle
- **WHEN** every gate succeeds in order
- **THEN** the card MUST advance one canonical stage at a time until `Pronto`

#### Scenario: Controlled rework before Done
- **WHEN** design approval, Code Review, or QA requests material rework
- **THEN** the system MUST allow the explicitly supported return transition
- **AND** it MUST retain evidence of the reason

#### Scenario: No regression after Done
- **WHEN** a card is `Done`, `Homologado`, or `Pronto`
- **THEN** the workflow MUST NOT regress it to an earlier status

#### Scenario: Publication is independent from OpenSpec archival
- **WHEN** an OpenSpec change is archived without verified publication in `main`
- **THEN** the workflow MUST NOT infer `Pronto`

### Requirement: Human design approval MUST be bound to immutable evidence
The human design approval MUST identify the exact design and prototype evidence reviewed.

#### Scenario: Evidence remains unchanged
- **WHEN** the current design and prototype digests match the approved digests
- **THEN** the approval MUST remain valid for development handoff

#### Scenario: Evidence changes after approval
- **WHEN** the design or prototype evidence changes after approval
- **THEN** the prior approval MUST be marked obsolete
- **AND** entry into `Em desenvolvimento` MUST be blocked until Alan approves the new version

### Requirement: Legacy workflow data MUST migrate without silent reinterpretation
The system MUST migrate known legacy states idempotently and MUST preserve existing work-item identity, ordering, and evidence.

#### Scenario: Legacy active state is migrated
- **WHEN** a known legacy state such as `Pending`, `DESIGN`, `DEV`, `In Progress`, `QA`, `Homologation`, or `Archived` is loaded during migration
- **THEN** it MUST be converted using the documented status mapping exactly once

#### Scenario: Unknown legacy state exists
- **WHEN** migration encounters a status outside the documented canonical and legacy sets
- **THEN** it MUST fail visibly or quarantine the record for reconciliation
- **AND** it MUST NOT default the record to `Em desenvolvimento`

### Requirement: Codex and Cursor MUST consume one workflow contract
Repository instructions MUST define the same OpenSpec stages, design gate, status names, and evidence requirements for Codex and Cursor.

#### Scenario: Codex starts a UI change
- **WHEN** Codex follows `/opsx:*` intentions for a UI-impact card
- **THEN** it MUST prepare and publish design evidence before implementation
- **AND** it MUST wait for `Pronto para Dev` before applying code tasks

#### Scenario: Cursor starts a UI change
- **WHEN** Cursor follows the corresponding `/opsx-*` command adapters
- **THEN** it MUST execute the same ordered OpenSpec and design-gate contract
- **AND** it MUST not maintain a divergent workflow definition
