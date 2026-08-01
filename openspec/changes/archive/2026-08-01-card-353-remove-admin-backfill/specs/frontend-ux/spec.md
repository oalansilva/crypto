## MODIFIED Requirements

### Requirement: Navigation hides admin-only menus from common users
The UI SHALL hide admin-only navigation entries from users who are not admins. The discontinued Backfill admin entry SHALL NOT appear for any user.

#### Scenario: Common user opens navigation
- **WHEN** a non-admin authenticated user views the app navigation
- **THEN** the navigation SHALL NOT show Combo or Backfill entries

#### Scenario: Admin opens navigation
- **WHEN** an admin authenticated user views the app navigation
- **THEN** the navigation SHALL show Combo when applicable
- **AND** the navigation SHALL NOT show a Backfill entry

#### Scenario: Admin status is not loaded yet
- **WHEN** the app has not positively identified the authenticated user as admin
- **THEN** admin-only navigation entries SHALL remain hidden
