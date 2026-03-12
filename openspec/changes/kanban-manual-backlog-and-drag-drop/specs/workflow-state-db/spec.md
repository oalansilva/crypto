## MODIFIED Requirements

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
