## ADDED Requirements

### Requirement: Login always requires valid password
The system SHALL verify password for every authentication attempt, without exception by email or any other user attribute.

#### Scenario: Login with valid password succeeds
- **WHEN** an existing active user submits correct email and password to `POST /api/auth/login`
- **THEN** the system SHALL verify the password with bcrypt
- **AND** return access and refresh tokens with user profile

#### Scenario: Login with wrong password is rejected
- **WHEN** an existing active user submits correct email but incorrect password to `POST /api/auth/login`
- **THEN** the system SHALL reject the request with HTTP 401
- **AND** the response SHALL indicate invalid credentials
- **AND** no token SHALL be issued

#### Scenario: Login with empty password is rejected
- **WHEN** any user submits valid email with empty or missing password to `POST /api/auth/login`
- **THEN** the system SHALL reject the request with HTTP 401 or 422
- **AND** no token SHALL be issued

#### Scenario: No email-based password bypass exists
- **WHEN** any user, regardless of email address, submits a login request
- **THEN** the system SHALL apply the same password verification logic
- **AND** no email address SHALL be exempt from password verification

### Requirement: Login form always requires password input
The login UI SHALL require password input for all users without exception.

#### Scenario: Password field is always required
- **WHEN** any user accesses the login page
- **THEN** the password field SHALL be required
- **AND** form validation SHALL reject submission with empty password
- **AND** no email address SHALL bypass the password requirement

#### Scenario: Logout clears session and prevents re-authentication without credentials
- **WHEN** a user clicks logout
- **THEN** access token, refresh token, and user data SHALL be removed from localStorage
- **AND** React Query cache SHALL be cleared
- **AND** subsequent navigation to protected routes SHALL redirect to login
