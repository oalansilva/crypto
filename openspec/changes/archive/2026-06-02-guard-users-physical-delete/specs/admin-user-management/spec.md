## MODIFIED Requirements

### Requirement: Admin can delete a selected user
The system SHALL NOT physically delete runtime user rows through admin user management; support SHALL use ban, suspension, reactivation, or editable status fields to manage access while preserving audit history.

#### Scenario: Delete is blocked
- **WHEN** an admin attempts to delete another user with a valid reason
- **THEN** the system SHALL reject the physical deletion
- **AND** the target user SHALL remain in the database for audit and history preservation

#### Scenario: Delete own account is blocked
- **WHEN** an admin attempts to delete their own logged-in user account
- **THEN** the system SHALL reject the request
- **AND** the logged-in user SHALL remain available for authentication

#### Scenario: Delete reason is required
- **WHEN** an admin attempts to delete a user without a valid reason
- **THEN** the system SHALL reject the request before deleting the user
