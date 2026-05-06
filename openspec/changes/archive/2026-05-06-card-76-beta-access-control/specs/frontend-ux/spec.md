## ADDED Requirements

### Requirement: Login page hides public registration during closed beta
The frontend UI SHALL present the beta login page as a login-only surface and SHALL NOT advertise public account creation.

#### Scenario: Visitor opens login page
- **WHEN** a visitor opens `/login`
- **THEN** the page SHALL show the login form
- **AND** the page SHALL NOT show a `Criar Conta` mode switch or public account creation form

#### Scenario: Visitor has no account
- **WHEN** a visitor cannot log in because they do not have credentials
- **THEN** the visible path SHALL imply invitation/support-managed access instead of public self-service registration
