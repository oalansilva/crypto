## ADDED Requirements

### Requirement: Admin can delete a selected user
The system SHALL allow an authenticated admin to delete a selected user from admin user management.

#### Scenario: Delete succeeds
- **WHEN** an admin deletes another user with a valid reason
- **THEN** the target user SHALL be removed from the user list
- **AND** the system SHALL record a `user_deleted` admin action containing the deletion reason and target user evidence

#### Scenario: Delete own account is blocked
- **WHEN** an admin attempts to delete their own logged-in user account
- **THEN** the system SHALL reject the request
- **AND** the logged-in user SHALL remain available for authentication

#### Scenario: Delete reason is required
- **WHEN** an admin attempts to delete a user without a valid reason
- **THEN** the system SHALL reject the request before deleting the user
