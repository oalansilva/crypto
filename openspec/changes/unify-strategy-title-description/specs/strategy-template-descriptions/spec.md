## ADDED Requirements

### Requirement: Visible strategy identity uses one title-description hierarchy
Descoberta, Favoritos e Monitor SHALL present a visible strategy identity as the canonical public display name followed immediately by the canonical public description. The identity block SHALL preserve the current product shell, actions, metrics and operational states, and SHALL wrap long PT-BR copy without clipping or horizontal page overflow.

#### Scenario: Discovery renders a leaderboard candidate
- **WHEN** a leaderboard row contains `display_name` and `description`
- **THEN** the candidate title SHALL render `display_name` instead of the raw `template_id`
- **AND** the description SHALL render directly below that title
- **AND** result id, coverage, parameters and direction-specific benchmark context SHALL remain secondary metadata rather than part of the title or description.

#### Scenario: Favorites renders desktop and mobile identities
- **WHEN** a favorite row or mobile card has a canonical public display name and description
- **THEN** it SHALL render exactly one strategy title followed by the public description
- **AND** it SHALL NOT render the redundant intermediate strategy-detail line
- **AND** refresh, revalidation, tier, direction, metrics and actions SHALL remain available.

#### Scenario: Monitor renders list and opportunity detail identities
- **WHEN** a Monitor opportunity has a public display name and description
- **THEN** the list and expanded opportunity detail SHALL render the display name as a title followed by the description
- **AND** the expanded detail SHALL NOT prefix those values with the visual labels `estratégia` or `descrição`
- **AND** timeframe, candle, alert and other operational metadata SHALL remain visually separate.

#### Scenario: Public description is long
- **WHEN** the public strategy description wraps across multiple lines on desktop or mobile
- **THEN** the complete copy SHALL remain readable without clipping, ellipsis or horizontal page scrolling
- **AND** the title SHALL remain visually dominant over the description and technical metadata.

### Requirement: Discovery leaderboard exposes canonical public strategy copy
Each Discovery leaderboard row SHALL include additive `display_name` and `description` fields resolved from the same public strategy catalog used by Combo. Existing leaderboard fields and ranking behavior SHALL remain compatible.

#### Scenario: Known template is serialized in the leaderboard
- **WHEN** a Discovery result uses a template key mapped by the public strategy catalog
- **THEN** `_result_row` SHALL return the mapped `display_name` from `public_strategy_catalog_name`
- **AND** SHALL return the mapped `description` from `public_strategy_description`
- **AND** the values SHALL match the Combo identity for the same template key.

#### Scenario: Existing leaderboard consumer reads a row
- **WHEN** `display_name` and `description` are added to a leaderboard row
- **THEN** all existing rank, metric, eligibility, deduplication, evidence and market fields SHALL remain present and unchanged
- **AND** sorting, filtering, pagination and promotion SHALL retain their current behavior.

#### Scenario: Template has no explicit public-name mapping
- **WHEN** a leaderboard result uses an unmapped custom template key
- **THEN** `display_name` SHALL use the catalog resolver's non-empty raw-name fallback
- **AND** `description` SHALL use the public description resolver's safe non-empty fallback
- **AND** the UI SHALL NOT substitute an empty heading or expose parameters as the public description.

### Requirement: Strategy copy source remains a separate product decision
This change SHALL consume the canonical product copy without renaming strategy mappings. For `multi_ma_crossover`, the current canonical title SHALL remain `Médias Móveis: Tendência em Virada` even when an informal or mock label uses `Multi MA Crossover`, unless a separately approved copy change updates the public catalog.

#### Scenario: Same strategy appears across product surfaces
- **WHEN** `multi_ma_crossover` appears in Combo, Descoberta, Favoritos or Monitor
- **THEN** every surface SHALL consume the canonical product title and description from its public-identity contract
- **AND** mock data using `Multi MA Crossover` MAY remain a fixture value only when the test intentionally verifies supplied mock copy rather than the production mapping.
