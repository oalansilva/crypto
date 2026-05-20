## ADDED Requirements

### Requirement: Frontend requests recover expired access tokens
Authenticated frontend API calls SHALL attempt one refresh-token recovery after an access-token `401` before forcing logout or surfacing the failure.

#### Scenario: Access token expired and refresh token is valid
- **WHEN** an authenticated request returns `401`
- **THEN** the frontend refreshes the token, retries the original request once, and keeps the user session active

#### Scenario: Refresh token is missing or invalid
- **WHEN** token refresh cannot produce a new access token
- **THEN** the frontend preserves the existing logout/error behavior without infinite retries
