## ADDED Requirements

### Requirement: Admin can list and search users
The system SHALL expose a paginated admin endpoint that returns users for operational support use.

#### Scenario: Search by email or name
- **WHEN** an admin calls `GET /api/admin/users` with query `q`
- **THEN** the system SHALL return only users whose `email` or `name` contains the query (case-insensitive)
- **AND** the response SHALL include total count and pagination metadata

#### Scenario: Filter by user status and date
- **WHEN** an admin calls `GET /api/admin/users` with filters `status`, `createdFrom`, `createdTo`, `lastLoginFrom`, `lastLoginTo`
- **THEN** the system SHALL return users matching all active filters

### Requirement: Admin can create support-managed users
The system SHALL allow admins to create a new user record when requested by support.

#### Scenario: Admin creates a valid user
- **WHEN** an admin posts valid user data to `POST /api/admin/users`
- **THEN** the system SHALL create the user and return the created user record
- **AND THEN** the system SHALL record an audit entry with action `user_created`

#### Scenario: Email conflict
- **WHEN** an admin tries to create a user using an existing email
- **THEN** the system SHALL reject the request with a validation error and not create or update any user

### Requirement: Admin can view and edit user details
The system SHALL provide read and update operations for user details including operational flags.

#### Scenario: Admin views a user
- **WHEN** an admin calls `GET /api/admin/users/{userId}`
- **THEN** the system SHALL return the full user profile used for support, excluding credential hashes

#### Scenario: Admin updates user details
- **WHEN** an admin sends editable fields to `PUT /api/admin/users/{userId}`
- **THEN** the system SHALL update allowed fields only (e.g., `name`, `status`, `is_banned`, `suspended_until`, `suspension_reason`, `notes`)
- **AND** the system SHALL create an audit entry for action `user_updated`

### Requirement: Admin can perform activation, deactivation, suspension and reactivation
The system SHALL support lifecycle controls for support interventions.

#### Scenario: Admin suspends user with reason and expiry
- **WHEN** an admin calls `POST /api/admin/users/{userId}/suspend` with reason and `suspendedUntil`
- **THEN** the system SHALL mark user status as `suspended`
- **AND** the system SHALL store the reason and suspension expiry timestamp

#### Scenario: Suspended user reaches expiry
- **WHEN** the current UTC time is greater than `suspended_until`
- **THEN** the system SHALL treat the user as active again unless another active suspension exists

#### Scenario: Admin bans user
- **WHEN** an admin calls `POST /api/admin/users/{userId}/ban` with reason
- **THEN** the system SHALL mark user status as `banned`
- **AND** the system SHALL block non-admin login and admin-supported actions for that account

#### Scenario: Admin reactivates suspended user
- **WHEN** an admin calls `POST /api/admin/users/{userId}/reactivate`
- **THEN** the system SHALL clear suspension fields and set status to `active` when no ban is active

### Requirement: Admin-only authorization is enforced
The system SHALL deny non-admin access to all admin user-management operations.

#### Scenario: Non-admin reads user list
- **WHEN** a non-admin token calls `GET /api/admin/users`
- **THEN** the system SHALL return HTTP 403

#### Scenario: Admin request without reason
- **WHEN** an admin action endpoint is called without a `reason` for destructive or risk-sensitive changes
- **THEN** the system SHALL reject the request with a validation error
