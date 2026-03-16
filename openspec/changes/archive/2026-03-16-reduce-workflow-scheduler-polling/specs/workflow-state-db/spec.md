## ADDED Requirements

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
