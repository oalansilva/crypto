# workflow-state-db Specification

## Purpose
TBD - created by archiving change centralize-workflow-state-db. Update Purpose after archive.
## Requirements
### Requirement: System MUST maintain workflow state in one operational source of truth
The system MUST store workflow runtime state in a centralized database.

#### Scenario: Change lifecycle stored centrally
- **WHEN** a change is created or updated
- **THEN** its workflow state MUST be persisted in the workflow DB
- **AND** agents/UI MUST read the current state from that DB

#### Scenario: Agent handoff stored centrally
- **WHEN** PO, DESIGN, DEV, or QA completes a turn
- **THEN** status, handoff, and comment data MUST be recorded in the DB

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
The runtime workflow model MUST support a **Pending** stage for backlog items that exist before PO planning starts.

#### Scenario: Create pending backlog item
- **WHEN** a user creates a new backlog card from Kanban
- **THEN** the runtime workflow record MUST be created in a pending state
- **AND** the record MUST be queryable by the Kanban board immediately

#### Scenario: Transition from pending to PO
- **WHEN** a pending card is moved into PO
- **THEN** the runtime workflow model MUST persist the new status transition
- **AND** later workflow gates MUST remain compatible with the existing approval flow

### Requirement: Runtime updates from Kanban MUST be authoritative for board moves
The runtime workflow DB MUST accept Kanban-driven status transitions as the source of truth for card movement.

#### Scenario: Kanban move updates runtime
- **WHEN** the user moves a card between columns from Kanban
- **THEN** the backend MUST persist the corresponding runtime state change
- **AND** subsequent Kanban reads MUST reflect the new column automatically
- **AND** invalid transitions MUST be rejected with a machine-readable error response

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
The workflow runtime MUST distinguish a functionally validated change from a change that is fully ready to move to Alan homologation.

#### Scenario: QA is functionally green but publish is still pending
- **WHEN** QA confirms the feature behavior is correct
- **AND** publish/reconcile requirements are still pending or blocked
- **THEN** the workflow MUST preserve that QA functional result explicitly
- **AND** MUST report the missing publish/reconcile step without implying Alan homologation readiness

### Requirement: Runtime-affecting changes MUST include live reconciliation before QA handoff completion
For changes that affect runtime, API, or UI behavior, the workflow MUST require a live reconciliation/smoke step before the DEV handoff is considered operationally complete.

#### Scenario: Runtime stale after local success
- **WHEN** local tests pass but the live runtime still serves stale behavior
- **THEN** the workflow MUST treat the DEV handoff as incomplete
- **AND** MUST direct the next step to reconcile/restart/publish the runtime before final QA advancement

### Requirement: Homologation readiness announcements MUST require full consistency
A change MUST only be announced as ready for Alan homologation after functional QA, publish/reconcile status, and runtime stage status are all aligned.

#### Scenario: Avoid premature homologation signal
- **WHEN** one of QA functional result, publish/reconcile state, or runtime stage transition is still incomplete
- **THEN** the workflow MUST NOT announce the change as ready for Alan homologation
- **AND** MUST instead state exactly which alignment step is missing

