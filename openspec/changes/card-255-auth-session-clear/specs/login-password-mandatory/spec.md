## ADDED Requirements

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
