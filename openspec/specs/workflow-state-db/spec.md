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

