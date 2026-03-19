## REMOVED Requirements

### Requirement: Wallet UI MUST provide search and locked-only filtering

#### Scenario: Search
- **WHEN** the user searches by asset symbol
- **THEN** the UI MUST filter rows case-insensitively by `asset`

#### Scenario: Locked only
- **WHEN** the user enables a "locked only" filter
- **THEN** the UI MUST show only rows where `locked > 0`

**Reason**: The "locked only" filter and "Locked" column are removed from the Wallet UI to simplify the interface.

**Migration**: None required — the `locked` field remains in the API response; only the UI filter and column are removed.
