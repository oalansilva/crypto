## ADDED Requirements

### Requirement: Dashboard must exclude ineligible stable pairs from the primary view
The system SHALL remove structurally non-actionable pairs from the default `AI Dashboard` opportunities list before ranking or rendering the primary view.

#### Scenario: Stablecoin versus stablecoin pairs are excluded from the primary list
- **WHEN** the unified signal payload contains pairs classified as ineligible for the primary trading view, including stablecoin versus stablecoin assets
- **THEN** the primary dashboard view MUST hide those assets from the main opportunities list

#### Scenario: Exclusion reasons are inspectable for ineligible pairs
- **WHEN** an asset is excluded from the primary list due to an eligibility rule
- **THEN** the payload MUST expose a machine-readable exclusion reason so the UI and audits can explain the decision

### Requirement: Dashboard must separate primary opportunities from additional coverage
The system SHALL classify eligible assets into `primary`, `secondary` or `excluded` so the default view highlights the main opportunities without losing access to broader coverage.

#### Scenario: Primary and secondary tiers are explicit in the payload
- **WHEN** the dashboard classifies an asset for display
- **THEN** the unified signal MUST include its `tier` and a `tier_reason` or equivalent explanation

#### Scenario: Additional coverage remains accessible without mixing with the primary list
- **WHEN** assets are classified as secondary coverage
- **THEN** the interface MUST show that additional assets exist and allow the user to reveal them in a secondary section separate from the default opportunities list

### Requirement: Dashboard must rank primary opportunities deterministically
The system SHALL order `primary` assets using a stable relevance rule so repeated loads with the same inputs produce the same result.

#### Scenario: Primary opportunities are ordered by deterministic relevance
- **WHEN** multiple eligible `primary` assets are available in the unified signal payload
- **THEN** the system MUST order the primary list using a deterministic relevance rule that considers convergence, freshness and market quality metadata

#### Scenario: Deterministic ranking has a stable tiebreaker
- **WHEN** two or more `primary` assets have equivalent relevance inputs
- **THEN** the ordering MUST still remain stable across identical payloads by applying a deterministic tiebreaker
