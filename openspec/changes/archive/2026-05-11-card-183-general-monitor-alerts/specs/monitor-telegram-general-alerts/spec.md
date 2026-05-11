## ADDED Requirements

### Requirement: General alert scans use curated Monitor catalog
Monitor Telegram alert scans SHALL evaluate the general curated Monitor strategy catalog instead of a user-specific favorite or liked-strategy subset.

#### Scenario: Admin caller does not limit alert coverage
- **WHEN** an admin triggers a Monitor Telegram alert scan
- **THEN** the scan SHALL use the curated Monitor catalog as the opportunity source
- **AND** the scan SHALL NOT limit candidates to strategies owned or liked by the admin caller

#### Scenario: User liked state does not limit group alerts
- **WHEN** a strategy exists in the curated Monitor catalog
- **AND** no MVP group user has marked that strategy as liked/favorite in `monitor_strategy_preferences`
- **THEN** the strategy SHALL still be eligible for a Monitor Telegram alert

### Requirement: General alert scans remain intentionally scoped
Monitor Telegram alert scans SHALL preserve configured scoping controls so Alan can exclude strategies from group alerts intentionally.

#### Scenario: Tier filter excludes a strategy
- **WHEN** the Monitor Telegram tier filter excludes a catalog strategy tier
- **THEN** the excluded strategy SHALL NOT be evaluated as an alert candidate

#### Scenario: Default scope targets curated tiers
- **WHEN** no custom Monitor Telegram tier filter is configured
- **THEN** the scan SHALL evaluate curated tiers `1`, `2`, and `3`
