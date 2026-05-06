## MODIFIED Requirements

### Requirement: Admin can create support-managed users
The system SHALL allow admins to create a new user record when requested by support, and this SHALL be the primary invite/access path during closed beta.

#### Scenario: Admin creates a valid user
- **WHEN** an admin posts valid user data to `POST /api/admin/users`
- **THEN** the system SHALL create the user and return the created user record
- **AND THEN** the system SHALL record an audit entry with action `user_created`
- **AND** the created active user SHALL be eligible to log in during closed beta

#### Scenario: Email conflict
- **WHEN** an admin tries to create a user using an existing email
- **THEN** the system SHALL reject the request with a validation error and not create or update any user
