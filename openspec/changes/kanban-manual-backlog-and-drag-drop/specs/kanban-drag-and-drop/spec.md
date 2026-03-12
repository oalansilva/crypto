## ADDED Requirements

### Requirement: Kanban MUST support direct card movement between columns
The system MUST let the user move cards between Kanban columns from the board UI using drag-and-drop on desktop, while preserving a workable move interaction on mobile.

#### Scenario: Drag card to another column on desktop
- **WHEN** the user drags a card from one Kanban column to another on desktop
- **THEN** the UI MUST indicate the active drop target
- **AND** dropping the card MUST submit a runtime workflow update for the destination column
- **AND** the board MUST refresh automatically to reflect the new column placement

#### Scenario: Move card on mobile
- **WHEN** the user uses the mobile move interaction for a card
- **THEN** selecting a destination stage MUST submit the same runtime workflow update used by desktop drag-and-drop
- **AND** the board MUST refresh automatically to reflect the new column placement

### Requirement: Column moves MUST synchronize workflow status automatically
Moving a card between columns MUST update the card's underlying workflow/runtime status mapping without requiring a separate manual status edit.

#### Scenario: Move into QA
- **WHEN** the user moves a card into **QA**
- **THEN** the backend MUST apply the runtime status transition mapped to the QA column
- **AND** the move MUST respect existing workflow guard rails or validations
- **AND** a rejected move MUST show an actionable error in the UI

#### Scenario: Move back to Pending
- **WHEN** the user moves a card back into **Pending**
- **THEN** the runtime workflow state MUST reflect that the card is back in backlog/not yet in PO planning
- **AND** the board MUST immediately show the card in Pending after the update succeeds
