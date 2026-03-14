## ADDED Requirements

### Requirement: Kanban MUST support explicit card cancelation without physical deletion
The system MUST allow a user to cancel a card/change from the Kanban flow without physically deleting the underlying runtime record.

#### Scenario: Cancel an invalid or obsolete card
- **WHEN** the user explicitly confirms card cancelation
- **THEN** the system MUST mark the card as canceled using a runtime representation that preserves auditability
- **AND** the card MUST stop appearing as active work in the normal execution flow
- **AND** the system MUST NOT require physical deletion of the record to remove it from active work

### Requirement: Card cancelation MUST require clear intent and preserve history
Canceling a card MUST be an intentional action and MUST preserve the operational trail for later review.

#### Scenario: Confirm cancelation
- **WHEN** the user chooses the cancel action for a card
- **THEN** the UI MUST ask for explicit confirmation before applying the cancelation
- **AND** existing comments, handoffs, and identifiers MUST remain available for audit/history purposes
- **AND** subsequent board/runtime queries MUST represent the card consistently as canceled or non-active
