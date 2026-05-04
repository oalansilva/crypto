## MODIFIED Requirements

### Requirement: Favorites screen is available to authenticated users
The Favorites page MUST be directly accessible to any authenticated user while preserving protected strategy redaction for non-admin users.

#### Scenario: Non-admin opens favorites route
- **WHEN** a non-admin user opens `/favorites`
- **THEN** the frontend MUST render the Favorites page
- **AND** the page MUST avoid exposing original strategy names, parameter values, or admin-only strategy actions for protected favorites
- **AND** the page MUST provide a star control to choose monitoring priority

#### Scenario: Admin opens favorites route
- **WHEN** an admin user opens `/favorites`
- **THEN** the frontend MUST render the existing admin favorites workflow
- **AND** the admin user MAY still see strategy internals and admin actions allowed by existing permissions

### Requirement: Favorites tier selection uses stars
The Favorites page MUST allow users to set the existing favorite tier through a star-based control.

#### Scenario: User marks three stars
- **WHEN** the user chooses three stars for a favorite
- **THEN** the frontend MUST PATCH that favorite with `tier=1`

#### Scenario: User marks two stars
- **WHEN** the user chooses two stars for a favorite
- **THEN** the frontend MUST PATCH that favorite with `tier=2`

#### Scenario: User marks one star
- **WHEN** the user chooses one star for a favorite
- **THEN** the frontend MUST PATCH that favorite with `tier=3`

#### Scenario: User clears stars
- **WHEN** the user clears the star selection for a favorite
- **THEN** the frontend MUST PATCH that favorite with `tier=null`
