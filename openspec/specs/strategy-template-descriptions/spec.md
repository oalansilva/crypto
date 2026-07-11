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
