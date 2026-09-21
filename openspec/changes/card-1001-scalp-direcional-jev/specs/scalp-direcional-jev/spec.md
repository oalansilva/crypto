## ADDED Requirements

### Requirement: Per-user switch persists and defaults off

The directional scalp SHALL be a production Farol feature with an explicit per-user switch (ligado or desligado). The default SHALL be desligado. Turning user A's switch on SHALL NOT turn on user B's. Restarting the Farol SHALL leave a desligado user desligado. Disabling SHALL stop sending, stop TypeSafe/Jev spend for this loop, and cancel this bot's resting orders. Kill at −2% of T SHALL have the same sending/cancel effect as desligado; religar SHALL require that user's switch again.

#### Scenario: Boot with switch off

- **WHEN** the Farol starts and the authenticated user's scalp switch is desligado
- **THEN** this scalp SHALL send no order for that user
- **AND** Monitor, Operar and candles SHALL keep working

#### Scenario: User turns the switch off while live

- **WHEN** a user turns the switch to desligado while the loop is running
- **THEN** the loop SHALL stop sending
- **AND** SHALL cancel this bot's open orders
- **AND** SHALL stop calling Jev for that user
- **AND** the Farol process SHALL NOT crash

#### Scenario: Restart does not self-enable

- **WHEN** the Farol restarts and that user's switch was desligado
- **THEN** the switch SHALL remain desligado
- **AND** the loop SHALL NOT start sending on its own

#### Scenario: Only the user who enabled can send

- **WHEN** user A has the switch ligado and user B has it desligado
- **THEN** only A's Binance account MAY receive orders from this scalp
- **AND** B SHALL send none

### Requirement: Orders use the user's Spot key, never a house account

Orders from this scalp SHALL use the same Binance Spot key stored in Meu Perfil that Operar already uses for that authenticated user. The loop SHALL NOT withdraw. The loop SHALL NOT use a house account, a Farol-global key, or a third key type. Missing Spot key SHALL block sending. The TypeSafe/Jev key SHALL exist only in the server environment; it SHALL NEVER appear in the panel, chat, card, git, or cleartext logs. Without the Jev key, live SHALL NOT send (stand-in MAY run).

#### Scenario: Same Spot key as Operar

- **WHEN** a user with a Spot key in Meu Perfil turns the scalp on
- **THEN** orders from this scalp SHALL be signed with that same Spot key
- **AND** SHALL NOT be signed with a house or global Farol key

#### Scenario: No Spot key

- **WHEN** the user has no Spot key in Meu Perfil
- **THEN** the scalp SHALL send no order for that user

#### Scenario: TypeSafe stays on the server

- **WHEN** the panel or logs render
- **THEN** they SHALL NOT show the TypeSafe/Jev secret in cleartext

### Requirement: BTCUSDT post-only loop with T, clip and kill

The live market SHALL be BTCUSDT spot. Every order from this loop SHALL be a post-only limit that does not cross (buy at best bid, sell at best ask). A cross reject SHALL wait for the next cycle; it SHALL NOT become market or IOC. T SHALL be min(US$ 100, that user's free Spot USDT, with fee headroom). Each order SHALL be ≤ US$ 10. Day kill for this loop SHALL fire when loss ≤ −2% of T: cancel this bot's orders, stop sending, show «parado por kill», do not self-enable, do not flatten the whole wallet. The loop SHALL be directional (one side at a time), not a market maker.

#### Scenario: Post-only buy when rules pass

- **WHEN** the switch is ligado, Jev says buy with side confidence ≥ 0.7, edge after fees, book not toxic, and T still fits
- **THEN** the loop MAY post a post-only buy ≤ US$ 10 at the best bid

#### Scenario: Cross reject does not go market

- **WHEN** Binance rejects an order because it would cross
- **THEN** the loop SHALL wait for the next cycle
- **AND** SHALL NOT send a market or IOC order

#### Scenario: Kill at minus two percent of T

- **WHEN** this loop's day loss is ≤ −2% of T
- **THEN** the module SHALL match desligado for sending (no new orders, bot orders cancelled)
- **AND** the panel SHALL show «parado por kill»
- **AND** it SHALL NOT turn itself back on
- **AND** it SHALL NOT zero the user's wallet

#### Scenario: T never spends more than free USDT

- **WHEN** free USDT is 99.63
- **THEN** T SHALL be about 99 (fee headroom)
- **AND** the bot SHALL NOT try to spend 100

### Requirement: Jev clock, book protection and inventory floor

Jev requests SHALL be one at a time, target ~1 s apart (floor 400 ms). A reply slower than 800 ms SHALL skip sending that cycle. Stale resting orders SHALL cancel immediately when the touch moves, without waiting 1 s. Hold is the default. The loop SHALL only sell BTC this run bought. Inventory SHALL start at zero. Floor SHALL be free BTC at start (dust). A sell request with bot inventory zero SHALL hold; floor BTC SHALL stay untouched. Near T, only the reducing side SHALL send.

#### Scenario: No second Jev call in flight

- **WHEN** a Jev request is still outstanding
- **THEN** the loop SHALL NOT open a second Jev request

#### Scenario: Late Jev skips the send

- **WHEN** Jev takes more than 800 ms
- **THEN** that cycle SHALL NOT send an order

#### Scenario: Book moves cancel immediately

- **WHEN** best bid/ask moves and this bot's resting order is off the touch
- **THEN** the loop SHALL cancel that order immediately
- **AND** SHALL NOT wait for the next Jev reply

#### Scenario: Zero inventory does not sell floor BTC

- **WHEN** bot inventory is 0 and Jev asks to sell
- **THEN** the loop SHALL NOT sell
- **AND** BTC that was free at start SHALL remain untouched

### Requirement: Operar and this scalp share the account without a mutex

Operar (confirmed MARKET click) SHALL remain available on the same Binance Spot account while the scalp is on or off. This card SHALL NOT redesign Operar. The scalp SHALL NOT replace Operar. Shared free USDT SHALL shrink T when Operar spends quote. Scalp P&L and inventory SHALL count only this loop's fills. If Operar or an outside order reduces free BTC below scalp inventory, the loop SHALL clip inventory to remaining free BTC above the start-of-run floor and SHALL NOT treat Operar fills as this scalp's P&L.

#### Scenario: Operar still works with scalp on

- **WHEN** the user's scalp switch is ligado
- **THEN** the Monitor Operar action SHALL remain available
- **AND** a confirmed Operar MARKET order SHALL still use the same Spot key

#### Scenario: Operar spend lowers T

- **WHEN** Operar spends free USDT while the scalp is tracking T
- **THEN** T SHALL become min(US$ 100, remaining free USDT with fee headroom)

#### Scenario: Outside sell clips bot inventory

- **WHEN** free BTC falls below this loop's inventory because of Operar or another non-loop order
- **THEN** the loop SHALL clip inventory to free BTC above the floor
- **AND** SHALL NOT sell the floor
- **AND** SHALL NOT book that outside fill as this scalp's P&L
