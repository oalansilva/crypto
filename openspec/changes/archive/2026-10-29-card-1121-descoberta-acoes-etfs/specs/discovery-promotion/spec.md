## MODIFIED Requirements

### Requirement: Promote an eligible candidate only to tier 3

The system SHALL require explicit administrator confirmation to promote an eligible `unique` discovery result. For a crypto result, this capability SHALL create **exactly tier 3** favorites. For an ação or ETF result, it SHALL create a favorite **without a star level** (`tier` null) until #1122 brings ação and ETF to Monitor, as the lote of #1120 does. The request, UI and server contract SHALL expose no tier selector or tier override. Any payload that supplies a tier other than `3` SHALL be rejected, and the server SHALL derive the stored tier from the asset class. Confirmation SHALL show candidate identity, `sweep_id`, `result_id`, the class and currency, and the fixed destination. The destination is `Tier 3 · observação` for crypto, and `Favoritos · sem nível de estrela` for ação and ETF, with "Monitor, Telegram e Revalidar: ainda não para ações e ETFs."

#### Scenario: Promote a unique candidate

- **WHEN** the administrator confirms promotion of an eligible unique crypto result
- **THEN** exactly one tier 3 favorite is created
- **AND** the result becomes `already_promoted`
- **AND** the leaderboard confirms success without removing the result

#### Scenario: Promote a unique ação or ETF candidate

- **WHEN** the administrator confirms promotion of an eligible unique NVDA result
- **THEN** exactly one favorite without star level is created, with the class, source, session, adjustment, currency, conventions, effective window, `snapshot_id` and direction of the result
- **AND** the result becomes `already_promoted` and the row shows "Favorito · sem estrela"

#### Scenario: Reject another tier

- **WHEN** a client sends tier `2`, omits the fixed contract version, or attempts any non-3 tier
- **THEN** promotion is rejected and no favorite/result state changes

#### Scenario: Attempt to promote a duplicate or low-sample candidate

- **WHEN** a candidate is equivalent to a template/favorite or fails ranking eligibility
- **THEN** promotion is unavailable
- **AND** the UI explains the matched reference or eligibility reason
