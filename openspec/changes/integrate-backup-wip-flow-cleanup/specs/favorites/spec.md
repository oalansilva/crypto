## ADDED Requirements

### Requirement: Common users can inspect safe catalog favorites
The favorites API SHALL allow a common user to read favorite details from the admin catalog when that favorite is part of the safe catalog path.

#### Scenario: Common user opens admin catalog favorite detail
- **WHEN** the requested favorite belongs to the admin catalog
- **THEN** the API returns the favorite detail without exposing another common user's private favorite data

#### Scenario: Common user opens private favorite from another user
- **WHEN** the requested favorite is not owned by the current user and is not an admin catalog favorite
- **THEN** the API returns not found
