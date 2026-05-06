## ADDED Requirements

### Requirement: Maintenance includes beta access hygiene
The system SHALL include repeatable maintenance tooling to verify closed-beta active users.

#### Scenario: Verify active user allowlist
- **WHEN** maintenance checks beta user access
- **THEN** the output SHALL identify whether only allowed beta emails remain active
- **AND** the check SHALL be runnable without mutating data
