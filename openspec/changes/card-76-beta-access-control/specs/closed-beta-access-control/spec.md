## ADDED Requirements

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
The system SHALL allow existing active users to log in and continue to authenticated beta routes.

#### Scenario: Active user logs in
- **WHEN** an existing active user submits valid credentials to `POST /api/auth/login`
- **THEN** the system SHALL return access and refresh tokens
- **AND** `/api/auth/me` SHALL return that user's profile for the access token

#### Scenario: Missing user cannot log in
- **WHEN** an email with no user record submits login credentials
- **THEN** the system SHALL reject the request with HTTP 401
- **AND** no token SHALL be issued

#### Scenario: Blocked user cannot authenticate
- **WHEN** a banned or actively suspended user submits valid credentials
- **THEN** the system SHALL reject the request with HTTP 403
- **AND** no token SHALL be issued
