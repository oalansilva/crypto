# strategy-template-descriptions Specification

## Purpose
Expose short, trader-friendly descriptions for visible strategy templates without exposing protected parameters or making performance promises.
## Requirements
### Requirement: Public Strategy Descriptions
The system SHALL expose one unique, trader-friendly and non-promissory PT-BR identity for each visible strategy/template. The name and description MUST be faithful to the executed configuration and SHALL explain entry context, exit context, consulted indicators, each indicator's function and risk control without source code or performance promises.

#### Scenario: Combo template list includes description
- **WHEN** an authorized user opens the Combo template selection flow
- **THEN** each listed template SHALL include the same public display name and description used by Favorites and Monitor.

#### Scenario: Favorites shows strategy and description
- **WHEN** a user opens Favorites
- **THEN** each favorite row/card SHALL show the canonical public strategy display name and description
- **AND** SHALL NOT show a generic fallback or internal research name.

#### Scenario: Monitor shows strategy description
- **WHEN** a user opens Monitor opportunities
- **THEN** the visible strategy identity SHALL match Favorites for the same strategy
- **AND** SHALL describe only indicators and behavior actually executed.

#### Scenario: Identity does not promise performance
- **WHEN** a public strategy description is rendered
- **THEN** it SHALL frame the strategy as decision support
- **AND** SHALL NOT promise return or make a personalized financial recommendation.

### Requirement: New hard-mode strategy has explicit public copy
Any new `strategy_name` saved by a hard-mode BTC discovery run SHALL have an explicit `strategy_display_name` and `strategy_description` mapping before the card is reported as technically complete.

#### Scenario: New strategy avoids fallback copy
- **WHEN** `/api/favorites/` returns the saved Favorite
- **THEN** `strategy_display_name` and `strategy_description` are non-empty, strategy-specific, and do not use the generic "Estrategia Cripto Farol" fallback

### Requirement: Public copy mapping is validated
Any new public display or description mapping added by a hard-mode BTC discovery run SHALL include focused validation that exercises the exact final `strategy_name`.

#### Scenario: Focused mapping test runs
- **WHEN** a new `strategy_name` mapping is added for the saved Favorite
- **THEN** a focused unit test or equivalent validation confirms the expected display name and description

### Requirement: No Fallback Public Identity For New Winners
Every new strategy key introduced for sequential BTC winner discovery SHALL resolve to a specific public display name and strategy description before saving and after served API readback.

#### Scenario: Public identity is validated before save
- **WHEN** the execution prepares a candidate for saving as a sequential Long winner
- **THEN** the execution SHALL define `name`, `strategy_name`, `strategy_display_name`, `strategy_description`, `direction`, and the public mapping source
- **AND** the public resolver or save payload SHALL return specific non-generic display and description values before the save request is made.

#### Scenario: Generic fallback blocks save
- **WHEN** a candidate public identity resolves to `Estratégia Cripto Farol`, `Strategy`, `Nova estratégia`, an empty value, or another generic fallback
- **THEN** the candidate SHALL NOT be saved as a winner
- **AND** if the fallback is caused by product behavior, the execution SHALL fix and validate the public mapping path before retrying.

#### Scenario: Served readback remains fallback-free
- **WHEN** a winner Favorite is read back from the served Favorites API after save
- **THEN** the Favorite SHALL show the expected `strategy_display_name` and `strategy_description`
- **AND** the new Favorite id SHALL NOT appear with `Estratégia Cripto Farol` in API, database-backed serialization, or UI evidence.

### Requirement: Visible strategy identity uses one title-description hierarchy
Combo (resultado e `/combo/select`), Descoberta, Favoritos e Monitor SHALL present a visible strategy identity as the canonical public display name followed immediately by the canonical public description. The identity block SHALL preserve the current product shell, actions, metrics and operational states, and SHALL wrap long PT-BR copy without clipping or horizontal page overflow.

#### Scenario: Combo result renders strategy identity
- **WHEN** an authorized user opens a Combo backtest result
- **THEN** the summary block SHALL render the resolved public display name as title and the resolved public description directly below
- **AND** symbol, timeframe, direction and performance metrics SHALL remain separate from the identity block.

#### Scenario: Combo select renders catalog identity
- **WHEN** an admin opens `/combo/select`
- **THEN** each template card SHALL render the resolved public `display_name` as title and the resolved public description below
- **AND** the visible title SHALL NOT be a Title-Case rewrite of the technical `name` (`multi_ma_crossover` SHALL NOT appear as `Multi Ma Crossover`)
- **AND** the technical template key SHALL remain the selection/clone identifier, not the heading.

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

### Requirement: Admin can edit global public identity from Combo template editor
An authenticated admin SHALL edit the public display name and description of a strategy template from `/combo/edit/{template_name}`. The edit SHALL persist globally and SHALL be reflected on the next read in Combo resultado, Combo select, Descoberta, Favoritos e Monitor for the same template key. Combo results SHALL present identity as read-only.

#### Scenario: Admin saves identity from Combo template editor
- **WHEN** an admin edits the title and description on `/combo/edit/{template_name}` and saves
- **THEN** the system SHALL persist `display_name` and `description` on `combo_templates` for that template
- **AND** the editor SHALL show the saved public title as heading.

#### Scenario: Read-only template accepts identity edit only
- **WHEN** an admin opens `/combo/edit/multi_ma_crossover` (`is_readonly=true`)
- **THEN** the identity fields SHALL be editable
- **AND** schema/JSON/optimization editors SHALL remain hidden or blocked
- **AND** the technical template PUT endpoint SHALL continue to reject schema/logic edits for that template.

#### Scenario: Non-admin cannot edit identity
- **WHEN** a non-admin user calls the identity endpoint
- **THEN** the identity endpoint SHALL return forbidden.

#### Scenario: Same template key stays consistent after save
- **WHEN** an admin saves a new public title and description for `multi_ma_crossover` from the template editor
- **THEN** Combo select, Combo resultado, Descoberta, Favoritos and Monitor SHALL resolve the same title and description for that key on the next fetch
- **AND** the technical template key SHALL remain unchanged.

#### Scenario: Seed mapping applies without override
- **WHEN** no database override exists for `multi_ma_crossover`
- **THEN** all surfaces SHALL resolve to the seeded public title `Médias Móveis: Tendência em Virada` and its mapped description
- **UNTIL** an admin saves a different override through the Combo template editor.
