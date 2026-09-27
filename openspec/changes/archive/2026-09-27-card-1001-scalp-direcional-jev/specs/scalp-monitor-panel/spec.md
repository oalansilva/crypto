## ADDED Requirements

### Requirement: Scalp module sits on Monitor above the KPIs

The authenticated `/monitor` workbench SHALL show a persistent Scalp BTCUSDT module between the page subtitle and the KPI row. The module SHALL NOT be a new catalog route. The module SHALL NOT live inside the Operar modal. The Monitor board (Status, Preço, Distância, Tags, Operar, Par / Estratégia) SHALL stay. Ligar the scalp SHALL NOT replace Operar.

#### Scenario: Module visible on Monitor

- **WHEN** an authenticated user opens `/monitor`
- **THEN** the Scalp BTCUSDT module SHALL be visible without opening Operar
- **AND** `table.signals` and the Operar actions SHALL remain

#### Scenario: Not a new surface

- **WHEN** the user looks for the switch
- **THEN** it SHALL be on `/monitor`
- **AND** SHALL NOT require a new nav destination as the only way to turn the loop off

### Requirement: Switch states, calibration and P&L are visible

The module SHALL show an explicit per-user switch and the states desligado, ligado and parado por kill. Default SHALL be desligado. Calibration SHALL be visible. P&L SHALL equal realized + unrealized − fees − Jev cost for this bot's inventory only; negative P&L SHALL be as visible as positive. A BTC pump without a buy fill SHALL NOT count as gain. Copy SHALL NOT say «estratégia lucrativa» or «formador de mercado». Without a Spot key the switch SHALL be disabled and SHALL point to Meu Perfil. After kill, religar SHALL be that same switch.

#### Scenario: Default off

- **WHEN** the user opens `/monitor` and has never turned the scalp on
- **THEN** the switch SHALL show desligado
- **AND** the module SHALL NOT claim the loop is sending

#### Scenario: Turn on

- **WHEN** the user with a Spot key turns the switch to ligado
- **THEN** the module SHALL show ligado
- **AND** the first timely Jev cycle MAY send a post-only order without a per-order Operar confirmation

#### Scenario: Kill state

- **WHEN** kill has fired
- **THEN** the module SHALL show «parado por kill»
- **AND** the switch SHALL act as desligado for sending
- **AND** turning it on again SHALL be an explicit user action on that same switch

#### Scenario: Calibration and loss are visible

- **WHEN** the panel is showing
- **THEN** calibration SHALL be visible
- **AND** a negative P&L figure SHALL be as visible as a positive one
- **AND** the panel SHALL NOT contain «estratégia lucrativa» or «formador de mercado»

#### Scenario: No Spot key cannot enable

- **WHEN** the user has no Spot key in Meu Perfil
- **THEN** the switch SHALL be disabled
- **AND** the module SHALL tell the user to configure the Spot key in Meu Perfil
