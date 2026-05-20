# closed-beta-access-control Specification

## Purpose
TBD - created by archiving change card-76-beta-access-control. Update Purpose after archive.
## Requirements
### Requirement: Closed beta blocks public self-registration
The system SHALL keep public self-registration disabled by default during closed beta.

#### Scenario: Visitor tries to register without invitation
- **WHEN** a visitor calls `POST /api/auth/register` and public registration is disabled
- **AND** the email is not present in configured beta invited emails
- **THEN** the system SHALL reject the request with HTTP 403
- **AND** the response SHALL explain that beta access requires invitation
- **AND** no user SHALL be created

#### Scenario: Invited email registers
- **WHEN** a visitor calls `POST /api/auth/register` with an email present in configured beta invited emails
- **THEN** the system SHALL create the user when the payload is otherwise valid
- **AND** the user SHALL be able to log in with the created password

#### Scenario: Public registration is explicitly enabled
- **WHEN** `BETA_PUBLIC_REGISTRATION_ENABLED` is enabled
- **THEN** the system SHALL preserve existing self-registration behavior for valid unique emails

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

### Requirement: Frontend requests recover expired access tokens
Authenticated frontend API calls SHALL attempt one refresh-token recovery after an access-token `401` before forcing logout or surfacing the failure.

#### Scenario: Access token expired and refresh token is valid
- **WHEN** an authenticated request returns `401`
- **THEN** the frontend refreshes the token, retries the original request once, and keeps the user session active

#### Scenario: Refresh token is missing or invalid
- **WHEN** token refresh cannot produce a new access token
- **THEN** the frontend preserves the existing logout/error behavior without infinite retries

