## REMOVED Requirements

### Requirement: Promote an eligible candidate only to tier 3
**Reason**: Card #1122, decisão 4 de Alan (27/10/2026): a Descoberta salva o favorito sem estrela, fora do Monitor e sem alerta, até a pessoa dar a estrela.
**Migration**: "Promote an eligible candidate as a favorite without star", abaixo. O pedido deixa de levar `tier: 3`; um pedido com qualquer tier é recusado.

### Requirement: Promote from Acompanhar parciais with the same tier-3 dialog
**Reason**: O destino fixo deixa de ser tier 3 (card #1122, 27/10/2026).
**Migration**: "Promote from Acompanhar parciais with the same dialog", abaixo.

## ADDED Requirements

### Requirement: Promote an eligible candidate as a favorite without star

The system SHALL require explicit administrator confirmation to promote an eligible `unique` discovery result. In any class (crypto, ação or ETF), this capability SHALL create **exactly one favorite without star** (`tier` null), with `notify_telegram=true` (the alert only has effect after the owner gives a star, `favorite-telegram-alerts`). The request, UI and server contract SHALL expose no tier selector or tier override; any payload that supplies a tier SHALL be rejected (422) and change nothing. Confirmation SHALL show candidate identity, `sweep_id`, `result_id`, the class, the currency, the configuration (source, session, adjustment) and the fixed destination `Favoritos · sem estrela`. The dialog title SHALL be "Promover a favorito". The destination note SHALL say "Onde ver depois: Favoritos, sem estrela e fora do Monitor" (with the configuration for ação and ETF), that giving at least 1 star there puts it in the Monitor with the Telegram alert, and that it is reversible. The duplicate check SHALL include the configuration (`favorite-configuration-identity`). After promotion the row SHALL show "Em Favoritos" and the success notice SHALL say the asset entered Favoritos without star.

#### Scenario: Promote a unique candidate

- **WHEN** the administrator confirms promotion of an eligible unique crypto result
- **THEN** exactly one favorite without star is created
- **AND** the result becomes `already_promoted`
- **AND** the leaderboard confirms success without removing the result and the row shows "Em Favoritos"

#### Scenario: Promote a unique ação or ETF candidate

- **WHEN** the administrator confirms promotion of an eligible unique NVDA result
- **THEN** exactly one favorite without star is created, with the class, source, session, adjustment, currency, conventions, effective window, `snapshot_id` and direction of the result
- **AND** the favorite does not appear in the Monitor and sends no alert until it gets a star
- **AND** the modal MUST NOT mention "Alertar" nor "No portfólio"

#### Scenario: Reject a tier

- **WHEN** a client sends `tier: 3`, any other tier, or omits the fixed contract version
- **THEN** promotion is rejected and no favorite/result state changes

#### Scenario: Attempt to promote a duplicate or low-sample candidate

- **WHEN** a candidate is equivalent to a template/favorite with the same configuration or fails ranking eligibility
- **THEN** promotion is unavailable
- **AND** the UI explains the matched reference or eligibility reason

### Requirement: Promote from Acompanhar parciais with the same dialog

The system SHALL allow an authenticated administrator to promote an eligible `unique` discovery result from Acompanhar locked top-5 parciais using the **same** confirmation dialog as Decidir (title **Promover a favorito**, fixed destination **Favoritos · sem estrela**; no tier selector). The dialog SHALL open from the parciais Promover control. Cancel, Voltar, or overlay dismiss SHALL leave the candidate and the sweep unchanged. A `NO-GO` seal with sufficient sample SHALL NOT disable Promover (the seal is an alert only, same as Decidir). After confirmed promotion the parciais row SHALL show **Em Favoritos**, SHALL keep its place in the top-5, and the active sweep SHALL continue (pause/cancel of the sweep are not implied). The same `result_id` on Decidir SHALL show the promoted state.

#### Scenario: Promote a NO-GO eligible partial while the sweep runs

- **GIVEN** a NO-GO eligible unique row in Acompanhar parciais and a non-terminal sweep
- **WHEN** the operator confirms Promover
- **THEN** exactly one favorite without star is created
- **AND** the row shows Em Favoritos and keeps its top-5 slot
- **AND** the sweep does not stop
- **AND** the NO-GO seal remains visible and did not block the click

#### Scenario: Cancel leaves the partial and the sweep untouched

- **GIVEN** the promotion dialog opened from a parciais Promover
- **WHEN** the operator cancels, goes Voltar, or dismisses the overlay
- **THEN** no favorite is created
- **AND** the candidate and the sweep stay as they were

## MODIFIED Requirements

### Requirement: Promotion follows the live favorite list

Promotion SHALL refuse a duplicate only when the equivalent favorite still exists. If the stored state is `duplicate_favorite` or `already_promoted` but that favorite has been deleted, the administrator MAY confirm **Promover a favorito**; the system SHALL accept and create a new favorite without star. The UI and the server SHALL tell the same truth: no ghost refusal «já duplica favorito ativo» for a missing N. Other real blocks (baixa amostra, amostra insuficiente, discarded, live duplicate) SHALL remain. Discarding a grid row SHALL NOT delete a favorite.

#### Scenario: Promote after the duplicate favorite is gone

- **GIVEN** an eligible row whose stored duplicate reference N no longer exists
- **WHEN** the administrator confirms Promover
- **THEN** a new favorite without star is created
- **AND** the response is not a duplicate refusal for N

#### Scenario: Promote after the origin favorite is gone

- **GIVEN** an eligible row stored as `already_promoted` for favorite N
- **AND** favorite N has been deleted
- **WHEN** the administrator confirms Promover
- **THEN** a new favorite without star is created
- **AND** the row is not treated as already that favorite

#### Scenario: Live duplicate still refused

- **GIVEN** an equivalent favorite that still exists
- **WHEN** the administrator tries to promote
- **THEN** promotion remains blocked as a live duplicate

### Requirement: Promote after 70/30 writes the complete chosen period onto the favorite

When creating a favorite from a Discovery result that was validated with walk-forward 70/30, the system SHALL set the favorite's operational `period_type` and start/end to the **complete period chosen for that sweep**, not the training slice stored on the result. For sweep period «todo» that operational window SHALL be first available candle → now. The persisted result, leaderboard Calmar, coverage and GO/NO-GO SHALL keep the training window. Provenance (`origin_type`, `sweep_id`, `result_id`, `strategy_identity_key`, `evidence_fingerprint`, `metrics_snapshot`) SHALL remain stored as the Discovery portrait and SHALL NOT be labeled on Favorites as the live full-period performance. The promotion modal SHALL NOT preview the complete period in this card.

#### Scenario: Promote todo after 70/30 does not inherit training end

- **GIVEN** a unique eligible result whose training evidence window is 17/08/2017 → 24/12/2023 and whose sweep period is «todo»
- **WHEN** the administrator confirms Promover
- **THEN** the created favorite operational period is first candle → now
- **AND** the result row on Decide still shows the training window and 70/30 metrics
- **AND** the modal does not add a complete-period preview

#### Scenario: Discovery portrait stays on Discovery

- **WHEN** the operator returns to the sweep after promotion
- **THEN** Calmar, coverage and verdict of the grid remain the training values
- **AND** that portrait is not shown on `/favorites` as the new favorite's performance
