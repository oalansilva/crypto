# login-password-mandatory Specification

## Purpose
Ensure login always requires password verification and the UI never bypasses password input by email or user attribute.

## Requirements
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

### Requirement: Invalid authenticated sessions clear client state
The frontend SHALL clear stored authentication data and in-memory auth state when an authenticated request receives `401` and token refresh cannot produce a new access token.

#### Scenario: Stale monitor session cannot refresh
- **WHEN** a user opens `/monitor` with stale access and refresh tokens
- **AND** the Monitor preferences request receives `401`
- **AND** the refresh request fails or returns an invalid payload
- **THEN** the frontend SHALL remove access token, refresh token, and user data from localStorage
- **AND** the frontend SHALL clear React Query cache
- **AND** the protected route SHALL redirect the user to `/login`

#### Scenario: Refresh succeeds
- **WHEN** an authenticated request receives `401`
- **AND** the refresh request returns a valid access token and refresh token
- **THEN** the frontend SHALL persist the refreshed tokens
- **AND** retry the original request with the refreshed access token
- **AND** keep the user on the protected page
