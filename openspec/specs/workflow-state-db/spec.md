# workflow-state-db Specification

## Purpose
TBD - created by archiving change centralize-workflow-state-db. Update Purpose after archive.
## Requirements
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

### Requirement: Kanban MUST be the main workflow interface
The Kanban UI MUST be the primary place for Alan and agents to consult workflow state and coordinate work.

#### Scenario: Kanban as primary consultation surface
- **WHEN** Alan or an agent needs to check workflow status
- **THEN** the Kanban MUST expose the current state, comments, approvals, and next actions without requiring chat as the primary source

#### Scenario: Agent coordination through comments
- **WHEN** agents need to hand off work or mention another role
- **THEN** they MUST be able to use Kanban comments to cite or mention one another directly
- **AND** those comments MUST remain attached to the relevant work item

### Requirement: Kanban MUST read workflow state from the DB
The Kanban UI MUST use DB-backed workflow state as its runtime source.

#### Scenario: Kanban renders change columns
- **WHEN** the Kanban page loads
- **THEN** it MUST read statuses/tasks/comments from DB-backed APIs
- **AND** it MUST not depend on aggregating multiple markdown files as the authoritative source

### Requirement: Workflow DB MUST support typed work items, parent-child relationships, and parallel work
The system MUST support different work item types, their relationships, and parallel execution across multiple active stories.

#### Scenario: Story and bug types
- **WHEN** a work item is created
- **THEN** the DB MUST allow explicit types such as `story` and `bug`

#### Scenario: Child bug linked to story
- **WHEN** QA/Tester or Alan identifies a bug related to a story
- **THEN** the system MUST allow creating a bug as a child of that story
- **AND** the relationship MUST be preserved in Kanban/APIs

#### Scenario: Story completion blocked by open child bugs
- **WHEN** a story has one or more child bugs not yet completed
- **THEN** the story MUST NOT be allowed to move to its final completed state
- **AND** those child bugs MUST be treated as prerequisites for story completion

#### Scenario: Multiple active stories at the same time
- **WHEN** the project has capacity for more than one active story
- **THEN** the system MUST allow multiple stories to remain active in parallel

#### Scenario: Parallel agent runs
- **WHEN** different agents work on different stories or independent work items
- **THEN** the system MUST allow parallel agent runs
- **AND** it MUST track ownership/locking so two agents do not conflict on the same controlled item without an explicit rule

### Requirement: OpenSpec artifacts MUST remain linked to workflow state
The system MUST preserve the relationship between workflow DB rows and OpenSpec change artifacts.

#### Scenario: Artifact linkage preserved
- **WHEN** a change has proposal/design/spec/tasks artifacts
- **THEN** the DB MUST store references to those artifacts so users and agents can navigate between workflow state and documentation

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

### Requirement: Workflow runtime MUST persist stable pull order per stage
The runtime workflow model MUST store enough ordering information to return a stable, user-controlled card sequence within each active stage.

#### Scenario: Persist reorder in runtime
- **WHEN** the user changes the order of two cards in the same stage
- **THEN** the runtime workflow state MUST persist that new relative order
- **AND** later Kanban reads MUST reflect the same ordering automatically

### Requirement: Ordered columns MUST guide operational pull behavior
The visible order of cards in a column MUST be treated as the intended pull sequence for agents/operators working that stage.

#### Scenario: Agent reads ordered queue
- **GIVEN** multiple cards are available in the same stage
- **WHEN** an agent/operator consults the Kanban/runtime queue
- **THEN** the topmost eligible card SHOULD be interpreted as the next preferred item to pull
- **AND** lower cards SHOULD be treated as lower priority unless blocked or explicitly skipped

### Requirement: Functional QA result MUST be distinguished from publish/runtime readiness
The workflow runtime MUST distinguish a functionally validated change from a change that is fully ready to move to Homologation.

#### Scenario: QA is functionally green but publish is still pending
- **WHEN** QA confirms the feature behavior is correct
- **AND** publish/reconcile requirements are still pending or blocked
- **THEN** the workflow MUST preserve that QA functional result explicitly
- **AND** MUST report the missing publish/reconcile step without implying Homologation readiness

### Requirement: Runtime-affecting changes MUST include live reconciliation before QA handoff completion
For changes that affect runtime, API, or UI behavior, the workflow MUST require a live reconciliation/smoke step before the DEV handoff is considered operationally complete.

#### Scenario: Runtime stale after local success
- **WHEN** local tests pass but the live runtime still serves stale behavior
- **THEN** the workflow MUST treat the DEV handoff as incomplete
- **AND** MUST direct the next step to reconcile/restart/publish the runtime before final QA advancement

### Requirement: Homologation readiness announcements MUST require full consistency
A change MUST only be announced as ready for Homologation after functional QA, publish/reconcile status, and runtime stage status are all aligned.

#### Scenario: Avoid premature homologation signal
- **WHEN** one of QA functional result, publish/reconcile state, or runtime stage transition is still incomplete
- **THEN** the workflow MUST NOT announce the change as ready for Homologation
- **AND** MUST instead state exactly which alignment step is missing

### Requirement: Scheduler MUST suppress repeated no-change workflow turns
The workflow scheduler MUST avoid repeatedly running the same heavy orchestration path when no material workflow state has changed.

#### Scenario: repeated unchanged active item
- **WHEN** the active/rightmost item remains in the same state with no new blocker, approval, or milestone
- **THEN** the scheduler MUST suppress redundant heavy reconciliation work
- **AND** MUST avoid repeated status output to Alan

### Requirement: Real workflow events MUST bypass suppression
The scheduler MUST still react promptly when a meaningful workflow event occurs.

#### Scenario: milestone or blocker appears
- **WHEN** a milestone, blocker, approval, or gate transition occurs
- **THEN** the scheduler MUST break suppression and run the appropriate workflow turn
- **AND** MAY notify Alan if the event meets the existing notification policy

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
