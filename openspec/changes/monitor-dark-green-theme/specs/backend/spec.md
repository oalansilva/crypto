## ADDED Requirements

### Requirement: Backend stores Monitor theme preference
The backend MUST store a Monitor theme preference.

#### Scenario: Preference field exists
- **WHEN** the client reads monitor preferences
- **THEN** the response includes a `theme` field (e.g., `dark-green`)

#### Scenario: Client updates theme
- **WHEN** the client updates the theme
- **THEN** the backend persists it and returns the updated value
