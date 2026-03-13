# kanban-backlog-intake Specification

## Purpose
TBD - created by archiving change kanban-manual-backlog-and-drag-drop. Update Purpose after archive.
## Requirements
### Requirement: Kanban MUST support direct backlog intake in a Pending column
The system MUST allow a user to create a new work card directly from `/kanban` without requiring PO artifacts first. Newly created cards MUST start in the **Pending** column until PO begins planning.

#### Scenario: Create backlog card from Kanban
- **WHEN** the user opens `/kanban` and submits a new card title from the board UI
- **THEN** the system MUST create a new runtime change/work item for the `crypto` project
- **AND** the new card MUST appear in the **Pending** column without requiring a page reload
- **AND** the card MUST be visible to PO for later pull-based planning

#### Scenario: Optional description is stored
- **WHEN** the user provides an optional short description during card creation
- **THEN** the system MUST persist that description in the runtime record used by Kanban
- **AND** the description MUST be available in the card details view

### Requirement: Pending backlog cards MUST be movable into PO planning
The system MUST treat **Pending** as a pre-PO stage that PO can pull from when ready.

#### Scenario: PO pulls a backlog card into planning
- **WHEN** a Pending card is moved to **PO**
- **THEN** the runtime workflow state MUST update so the card is no longer pending
- **AND** the Kanban board MUST immediately show the card in the **PO** column
- **AND** later workflow gates MUST continue from the normal flow after PO

