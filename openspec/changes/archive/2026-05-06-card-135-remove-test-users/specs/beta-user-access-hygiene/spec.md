## ADDED Requirements

### Requirement: Closed beta user cleanup blocks unauthorized accounts
The system SHALL provide an operation that makes all beta users except the allowed Alan accounts unable to authenticate.

#### Scenario: Unauthorized users exist
- **WHEN** the cleanup operation runs with apply mode enabled
- **THEN** every user whose email is not `o.alan.silva@gmail.com` or `o2.alan.silva@gmail.com` SHALL be marked banned/inactive
- **AND** user-owned history SHALL remain preserved

#### Scenario: Allowed users exist
- **WHEN** allowed users are present before cleanup
- **THEN** the cleanup operation SHALL leave their `status`, `is_banned`, and login eligibility unchanged

#### Scenario: Dry run
- **WHEN** the cleanup operation runs without apply mode
- **THEN** the system SHALL report what would change
- **AND** it SHALL NOT mutate any user rows

### Requirement: Cleanup records safe evidence
The cleanup operation SHALL produce safe before/after evidence for card closure.

#### Scenario: Evidence output
- **WHEN** the cleanup operation completes
- **THEN** output SHALL include total users, allowed active users, unauthorized active users, changed users, and masked email lists
- **AND** output SHALL NOT include credential hashes or secrets
