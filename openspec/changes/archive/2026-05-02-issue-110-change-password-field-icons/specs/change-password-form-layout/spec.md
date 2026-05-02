## ADDED Requirements

### Requirement: Password fields preserve icon spacing
The change password form SHALL render password field icons without overlapping the field text or placeholder.

#### Scenario: User views change password form
- **WHEN** an authenticated user opens `/change-password`
- **THEN** each password input with a leading icon has enough left padding for the icon and text to remain visually separated

#### Scenario: User enters password text
- **WHEN** the user types into any change password field with a leading icon
- **THEN** the typed text remains readable and does not collide with the icon
