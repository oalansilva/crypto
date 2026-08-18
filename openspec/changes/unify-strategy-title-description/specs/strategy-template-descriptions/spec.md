## ADDED Requirements

### Requirement: Visible strategy identity uses one title-description hierarchy
Combo (resultado), Descoberta, Favoritos e Monitor SHALL present a visible strategy identity as the canonical public display name followed immediately by the canonical public description. The identity block SHALL preserve the current product shell, actions, metrics and operational states, and SHALL wrap long PT-BR copy without clipping or horizontal page overflow.

#### Scenario: Combo result renders strategy identity
- **WHEN** an authorized user opens a Combo backtest result
- **THEN** the summary block SHALL render the resolved public display name as title and the resolved public description directly below
- **AND** symbol, timeframe, direction and performance metrics SHALL remain separate from the identity block.

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
- **THEN** `_result_row` SHALL return the resolved `display_name` and `description`
- **AND** the values SHALL match the Combo identity for the same template key when no database override exists.

#### Scenario: Existing leaderboard consumer reads a row
- **WHEN** `display_name` and `description` are added to a leaderboard row
- **THEN** all existing rank, metric, eligibility, deduplication, evidence and market fields SHALL remain present and unchanged
- **AND** sorting, filtering, pagination and promotion SHALL retain their current behavior.

#### Scenario: Template has no explicit public-name mapping
- **WHEN** a leaderboard result uses an unmapped custom template key
- **THEN** `display_name` SHALL use the catalog resolver's non-empty raw-name fallback
- **AND** `description` SHALL use the public description resolver's safe non-empty fallback
- **AND** the UI SHALL NOT substitute an empty heading or expose parameters as the public description.

### Requirement: Admin can edit global public identity from Combo result
An authenticated admin SHALL edit the public display name and description of a strategy template from the Combo result summary. The edit SHALL persist globally and SHALL be reflected on the next read in Combo, Descoberta, Favoritos and Monitor for the same template key.

#### Scenario: Admin saves identity from Combo result
- **WHEN** an admin edits the title and description inline on `/combo/results` and saves
- **THEN** the system SHALL persist `display_name` and `description` on `combo_templates` for that `template_name`
- **AND** the Combo result summary SHALL show the saved values immediately after success.

#### Scenario: Read-only template accepts identity edit only
- **WHEN** an admin saves identity for a template with `is_readonly=true`
- **THEN** the identity endpoint SHALL succeed
- **AND** the technical template PUT endpoint SHALL continue to reject schema/logic edits for that template.

#### Scenario: Non-admin cannot edit identity
- **WHEN** a non-admin user opens `/combo/results`
- **THEN** the edit affordance SHALL NOT be visible
- **AND** a direct call to the identity endpoint SHALL return forbidden.

#### Scenario: Same template key stays consistent after save
- **WHEN** an admin saves a new public title and description for `multi_ma_crossover`
- **THEN** Descoberta, Favoritos and Monitor SHALL resolve the same title and description for that key on the next fetch
- **AND** the technical template key SHALL remain unchanged.

#### Scenario: Seed mapping applies without override
- **WHEN** no database override exists for `multi_ma_crossover`
- **THEN** all surfaces SHALL resolve to the seeded public title `Médias Móveis: Tendência em Virada` and its mapped description
- **UNTIL** an admin saves a different override through the Combo result editor.
