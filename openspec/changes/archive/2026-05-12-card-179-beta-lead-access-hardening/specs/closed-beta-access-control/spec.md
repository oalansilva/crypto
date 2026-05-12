## MODIFIED Requirements

### Requirement: Active beta users can authenticate
The system SHALL allow existing active users to log in and continue to authenticated beta routes. Password verification is mandatory for all users. Users marked with temporary beta access SHALL be forced to change password before normal app navigation, and expired temporary passwords SHALL NOT authenticate.

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

#### Scenario: Temporary access requires password change
- **WHEN** a temporary-access user logs in before expiry
- **THEN** the auth response SHALL include `mustChangePassword=true`
- **AND** the frontend SHALL keep the user on the password-change flow before normal app navigation
- **AND** regular authenticated backend APIs SHALL reject the access token until password change succeeds
- **AND** the password-change and auth-status endpoints SHALL remain available

#### Scenario: Expired temporary access cannot authenticate
- **WHEN** a temporary-access user logs in after the temporary password expiry
- **THEN** the system SHALL reject the request with HTTP 403
- **AND** no token SHALL be issued
