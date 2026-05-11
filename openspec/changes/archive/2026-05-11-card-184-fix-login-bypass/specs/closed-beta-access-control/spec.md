## MODIFIED Requirements

### Requirement: Active beta users can authenticate
The system SHALL allow existing active users to log in and continue to authenticated beta routes. Password verification is mandatory for all users.

#### Scenario: Active user logs in
- **WHEN** an existing active user submits valid credentials (email AND correct password) to `POST /api/auth/login`
- **THEN** the system SHALL verify the password against the stored hash using bcrypt
- **AND** return access and refresh tokens
- **AND** `/api/auth/me` SHALL return that user's profile for the access token

#### Scenario: Active user submits wrong password
- **WHEN** an existing active user submits valid email but incorrect password to `POST /api/auth/login`
- **THEN** the system SHALL reject the request with HTTP 401
- **AND** no token SHALL be issued

#### Scenario: Missing user cannot log in
- **WHEN** an email with no user record submits login credentials
- **THEN** the system SHALL reject the request with HTTP 401
- **AND** no token SHALL be issued

#### Scenario: Blocked user cannot authenticate
- **WHEN** a banned or actively suspended user submits valid credentials
- **THEN** the system SHALL reject the request with HTTP 403
- **AND** no token SHALL be issued

## REMOVED Requirements

### Requirement: Passwordless login bypass for specific emails
**Reason**: Security vulnerability — allowed specific email addresses to authenticate without password verification, violating the principle that all users must provide valid credentials. Blocked production release of closed beta.
**Migration**: All users must now provide their password. Accounts relying on the bypass must have valid password hashes set in the database before deploying this change. Use the admin user management interface or a database migration to ensure password hashes exist for affected accounts.
