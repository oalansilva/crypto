## ADDED Requirements

### Requirement: Scalp module copy shows applied fee discount, net P&L per trade and applied geometry state

Authenticated `/monitor` SHALL keep hosting the existing Scalp BTCUSDT module. The module SHALL show the fee in use; when the BNB discount is actually applied to that fee it SHALL say "desconto aplicado". It SHALL NOT describe a BNB setting as a discount already applied when the discount did not enter the rate. It SHALL show net P&L per trade in bp and in US$, with loss as visible as gain. Status copy SHALL name the applied lookback, hurdle, fee (with discount wording when it applies), target and stop. The diagnosis on the same module SHALL speak of target, stop, prazo and regime cut together with confidence. The scalp switch, T, clip, kill, board and Operar SHALL remain. This card SHALL NOT add a catalog route and SHALL NOT change landing or Ajuda copy. The canonical surface SHALL NOT be a grid of outcome cards.

#### Scenario: Discount wording matches the rate in use

- **WHEN** an authenticated user opens `/monitor` and the fee in use includes the BNB discount
- **THEN** the Taxa em uso control SHALL include the words "desconto aplicado"
- **AND** SHALL show the discounted rate that the hurdle uses

#### Scenario: No false discount claim

- **WHEN** BNB burn is enabled but the discount did not enter the rate
- **THEN** the module SHALL NOT say "desconto aplicado"
- **AND** the fee figure SHALL match the undiscounted rate in use

#### Scenario: Net P&L per trade is on the first view

- **WHEN** this scalp has closed a round trip
- **THEN** the module SHALL show that trade's net P&L in bp and in US$
- **AND** a negative figure SHALL use the same emphasis vocabulary as a positive one

#### Scenario: Board stays

- **WHEN** the user looks at `/monitor`
- **THEN** `table.signals` SHALL still expose Status, Preço, Distância, 7d, Risco até stop, Tags, Operar and Par / Estratégia
- **AND** the Operar control SHALL still open the existing confirmed MARKET flow
