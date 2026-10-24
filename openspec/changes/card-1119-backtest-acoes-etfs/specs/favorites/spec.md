## ADDED Requirements

### Requirement: Favoritar ação ou ETF é recusado até o #1122

`POST /api/favorites/` SHALL refuse a favorite whose asset is an ação or ETF with HTTP 422, code `asset_class_not_favoritable` and the message "Ações e ETFs ainda não podem ser favoritados: atualização diária e alertas dessas classes ainda não existem." Nothing SHALL be saved. On the result page, the "Salvar nos Favoritos" action of an ação or ETF result SHALL stay visible but unavailable (`aria-disabled`), with that reason visible as text next to it and announced when activated. Crypto favorites SHALL keep working as today, including the daily refresh.

#### Scenario: Save NVDA result

- **WHEN** Alan activates "Salvar nos Favoritos" on the NVDA result
- **THEN** no modal opens and nothing is saved
- **AND** the reason is visible next to the action and announced

#### Scenario: API refusal

- **WHEN** a client posts a favorite with symbol SPY
- **THEN** the API answers 422 with `asset_class_not_favoritable` and nothing is stored

#### Scenario: Crypto favorite unchanged

- **WHEN** Alan saves a BTC/USDT result
- **THEN** the favorite is saved as today

#### Scenario: No new notice in Favoritos about the gap rule

- **WHEN** Alan opens `/favorites` after the daily refresh recalculated a crypto favorite with the gap rule
- **THEN** no new notice about the change is shown there; the result page explains the gap rule (decision of Alan in Design, 23/10/2026)
