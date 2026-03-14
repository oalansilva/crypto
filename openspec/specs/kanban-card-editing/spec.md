# kanban-card-editing Specification

## Purpose
TBD - created by archiving change alterar-dados-dos-cards. Update Purpose after archive.
## Requirements
### Requirement: Kanban MUST allow editing a card title and description after creation
The system MUST let the user update the title and description of an existing Kanban card/change without recreating the card.

#### Scenario: Edit card metadata from card details
- **WHEN** the user opens an existing card in Kanban details and edits the title and/or description
- **THEN** the system MUST persist the new values in the workflow runtime record for that change
- **AND** the board/detail view MUST reflect the new values after save succeeds
- **AND** the user MUST receive actionable feedback if validation fails

### Requirement: Card metadata updates MUST preserve workflow continuity
Editing a card title or description MUST NOT reset workflow gates, delete approvals, or create a new card identity.

#### Scenario: Preserve card identity after metadata edit
- **WHEN** the user saves a title/description change for an existing card
- **THEN** the change/card id MUST remain the same
- **AND** existing workflow history/comments MUST remain associated with that same card
- **AND** the card MUST remain in its current workflow stage unless the user performs a separate stage transition

