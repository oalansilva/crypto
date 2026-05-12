## ADDED Requirements

### Requirement: Admin user deletion preserves action evidence
The system SHALL preserve safe admin action evidence when a selected beta user is deleted.

#### Scenario: Deleted beta user has audit evidence
- **WHEN** an admin deletes a selected beta user
- **THEN** the deletion action SHALL remain visible in admin action logs
- **AND** the action evidence SHALL NOT include credential hashes or secrets
