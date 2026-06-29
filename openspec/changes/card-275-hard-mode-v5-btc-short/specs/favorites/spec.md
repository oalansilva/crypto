## MODIFIED Requirements

### Requirement: BTC/USDT 1D Short Favorites saved by governed search

New favorites saved by card #275 MUST be BTC/USDT 1D strategies with `direction=short`, deep backtest evidence, public display name and description that do not fall back to generic copy, and final readback from the Favorites API.

#### Scenario: accepted Short winner is visible without fallback

- **GIVEN** a candidate passes novelty, robustness, dominance, and sequential superiority gates
- **WHEN** it is saved as a Favorite
- **THEN** `/api/favorites/` and the individual favorite endpoint show a new `favorite.id`, `created_at` after T0, `direction=short`, specific `strategy_display_name`, and specific `strategy_description`
- **AND** the new favorite does not appear as `Estratégia Cripto Farol`

#### Scenario: Long or generic candidate is rejected

- **GIVEN** a candidate has `direction=long`, missing direction, generic public copy, or fallback display
- **WHEN** the governed search evaluates it
- **THEN** it MUST NOT be saved or counted as a WINNER for card #275
