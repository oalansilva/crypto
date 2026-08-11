## ADDED Requirements

### Requirement: Monitor filters opportunities by star classification
The Monitor SHALL allow a common user to filter visible opportunities by star classification using the existing tier-to-stars mapping where Tier 1 equals three stars, Tier 2 equals two stars, and Tier 3 equals one star.

#### Scenario: User selects three stars
- **WHEN** the common user selects the three-star filter in the Monitor
- **THEN** the Monitor shows only opportunities classified as Tier 1

#### Scenario: User selects two stars
- **WHEN** the common user selects the two-star filter in the Monitor
- **THEN** the Monitor shows only opportunities classified as Tier 2

#### Scenario: User clears star filtering
- **WHEN** the common user selects the all-stars option in the Monitor
- **THEN** the Monitor applies no star-specific restriction beyond the existing filters
