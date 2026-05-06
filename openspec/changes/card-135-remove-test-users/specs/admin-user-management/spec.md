## ADDED Requirements

### Requirement: Closed beta unauthorized users can be audit-safely disabled
The system SHALL support disabling unauthorized beta users without physically deleting their historical records.

#### Scenario: Admin-safe user cleanup
- **WHEN** an operational cleanup disables an unauthorized user
- **THEN** the user SHALL be blocked from authentication
- **AND** existing user-owned records SHALL remain available for audit or future migration
