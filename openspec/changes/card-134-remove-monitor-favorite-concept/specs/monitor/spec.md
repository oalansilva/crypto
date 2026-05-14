## MODIFIED Requirements

### Requirement: Common-user Monitor follows Favorites star tiers
The Monitor page MUST show only strategies marked with 1, 2, or 3 stars by default, regardless of whether the opportunity resolves to HOLD, WAIT, or EXIT. The Monitor MUST treat stars/tier as read-only classification from Favorites and MUST NOT provide its own favorite management, favorite filter, favorite counter, favorite toggle, local favorite storage, or Monitor-local favorite preferences.

#### Scenario: Common user opens Monitor
- **WHEN** a non-admin user opens `/monitor`
- **THEN** the Monitor request MUST ask the backend for `tier=1,2,3`
- **AND** visible opportunities MUST exclude unstarred strategies (`tier=null`)
- **AND** opportunities with `tier=1`, `tier=2`, or `tier=3` MUST remain visible in their resolved HOLD, WAIT, or EXIT section
- **AND** the UI MUST NOT require the strategy to be in portfolio or in local Monitor favorites to appear
- **AND** the UI MUST NOT expose a Monitor-local favorite action, filter, or count

#### Scenario: Backend returns unstarred opportunity defensively
- **WHEN** the backend response contains an unstarred opportunity
- **THEN** the Monitor UI MUST not render that opportunity by default

#### Scenario: Admin opens Monitor
- **WHEN** an admin user opens `/monitor`
- **THEN** the existing operator filters and Monitor preference controls MAY remain available except for favorite management controls
- **AND** the Monitor MUST NOT expose a favorite filter or favorite toggle

## ADDED Requirements

### Requirement: Monitor delegates favorite curation to Favorites
The Monitor MUST NOT provide controls for adding, removing, filtering, or locally storing favorite strategies. Favorites curation and star/tier ranking SHALL be managed on the Favorites screen.

#### Scenario: User views Monitor toolbar
- **WHEN** the user opens `/monitor`
- **THEN** the toolbar MUST NOT include a `Favoritos` filter
- **AND** the visible result summary MUST NOT include a favorites count

#### Scenario: User views Monitor row actions
- **WHEN** the user views a Monitor opportunity row
- **THEN** the row actions MUST NOT include `Favoritar` or `Remover favorito`
- **AND** the row MAY still show read-only star/tier classification

#### Scenario: Monitor loads
- **WHEN** the Monitor loads opportunities
- **THEN** it MUST NOT read or write Monitor-local favorite localStorage
- **AND** it MUST NOT call Monitor strategy preference endpoints for local favorite state
