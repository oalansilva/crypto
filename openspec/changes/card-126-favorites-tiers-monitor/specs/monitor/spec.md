## MODIFIED Requirements

### Requirement: Common-user Monitor follows Favorites star tiers
The Monitor page MUST show common users only strategies that they marked with stars in Favorites.

#### Scenario: Common user opens Monitor
- **WHEN** a non-admin user opens `/monitor`
- **THEN** the Monitor request MUST use the backend common-user tier policy
- **AND** the visible list MUST be based on tiered Favorites (`tier=1`, `tier=2`, or `tier=3`)
- **AND** unstarred favorites (`tier=null`) MUST NOT be shown
- **AND** the UI MUST NOT require the strategy to be in portfolio or in local Monitor favorites to appear

#### Scenario: Admin opens Monitor
- **WHEN** an admin user opens `/monitor`
- **THEN** the existing operator filters and Monitor favorite preference controls MAY remain available
