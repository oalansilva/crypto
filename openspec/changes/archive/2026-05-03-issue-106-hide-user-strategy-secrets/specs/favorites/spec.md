## ADDED Requirements

### Requirement: Favorites hide strategy secrets from non-admin users
The Favorites API and UI MUST hide clear strategy implementation details from non-admin users.

#### Scenario: Non-admin lists favorites
- **WHEN** a non-admin user lists saved favorite strategies
- **THEN** each favorite MUST avoid exposing the original strategy name
- **AND** each favorite MUST avoid exposing saved strategy parameter values
- **AND** each favorite MUST mark the strategy as protected

#### Scenario: Admin lists favorites
- **WHEN** an admin user lists saved favorite strategies
- **THEN** each favorite MUST include the original strategy name and parameter values as before
- **AND** each favorite MUST mark the strategy as not protected

### Requirement: Favorites screen is admin-only
The Favorites page MUST only be directly accessible to admin users because it exposes strategy comparison and saved configuration workflows.

#### Scenario: Non-admin opens favorites route
- **WHEN** a non-admin user opens `/favorites`
- **THEN** the frontend MUST redirect the user away from the page

#### Scenario: Admin opens favorites route
- **WHEN** an admin user opens `/favorites`
- **THEN** the frontend MUST render the existing favorites workflow
