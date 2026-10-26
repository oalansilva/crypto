## MODIFIED Requirements

### Requirement: Promote an eligible candidate only to tier 3

The system SHALL require explicit administrator confirmation to promote an eligible `unique` discovery result. In any class (crypto, ação or ETF), this capability SHALL create **exactly tier 3** favorites, with `notify_telegram=false`. The request, UI and server contract SHALL expose no tier selector or tier override. Any payload that supplies a tier other than `3` SHALL be rejected. Confirmation SHALL show candidate identity, `sweep_id`, `result_id`, the class, the currency, the configuration (source, session, adjustment) and the fixed destination `Tier 3 · observação`. The duplicate check SHALL include the configuration (`favorite-configuration-identity`).

#### Scenario: Promote a unique candidate

- **WHEN** the administrator confirms promotion of an eligible unique crypto result
- **THEN** exactly one tier 3 favorite is created
- **AND** the result becomes `already_promoted`
- **AND** the leaderboard confirms success without removing the result

#### Scenario: Promote a unique ação or ETF candidate

- **WHEN** the administrator confirms promotion of an eligible unique NVDA result
- **THEN** exactly one tier 3 favorite is created, with the class, source, session, adjustment, currency, conventions, effective window, `snapshot_id` and direction of the result
- **AND** the result becomes `already_promoted` and the row shows "Favorito tier 3"
- **AND** the modal MUST NOT say "Monitor, Telegram e Revalidar: ainda não para ações e ETFs"
- **AND** the destination note SHALL say to mark "Alertar" in Favoritos and mark the asset "No portfólio" in the Monitor to receive Telegram alerts

#### Scenario: Reject another tier

- **WHEN** a client sends tier `2`, omits the fixed contract version, or attempts any non-3 tier
- **THEN** promotion is rejected and no favorite/result state changes

#### Scenario: Attempt to promote a duplicate or low-sample candidate

- **WHEN** a candidate is equivalent to a template/favorite with the same configuration or fails ranking eligibility
- **THEN** promotion is unavailable
- **AND** the UI explains the matched reference or eligibility reason
