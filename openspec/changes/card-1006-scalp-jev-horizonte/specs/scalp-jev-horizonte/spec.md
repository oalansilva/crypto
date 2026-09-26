## ADDED Requirements

### Requirement: Lookback, cadence and hold are three detached 15-minute roles

The directional scalp SHALL use a rolling lookback of the last 15 minutes of `aggTrade` plus the current touch (`horizon_s = 900` on the window). The lookback SHALL NOT be a 15-minute OHLCV candle and SHALL NOT be a per-user choice. The panel SHALL show «últimos 15 min» as a fact in the same vocabulary as T and clip. The module SHALL NOT present a 1 / 2 / 5 minute radio or selector.

Jev cadence SHALL be a fresh-touch consult: while the scalp is on and there is **no** open position and **no** exit resting order, the loop SHALL ask Jev on the fresh stream touch. The ask clock SHALL remain the fresh-touch / ~1 s cadence; this card SHALL NOT ask Jev to answer faster and SHALL NOT change that clock. One Jev request SHALL be in flight at a time. The Farol SHALL wait for the Jev reply up to 1.5 s. HTTP wait and the late-reply send cap SHALL be aligned at 1.5 s (there SHALL still be a cap; this SHALL NOT be unlimited wait). A Jev reply within 1.5 s plus the other send gates (hold default, confidence, non-toxic book, hurdle, T cap, fresh book from #1008) SHALL allow that cycle to send. A Jev reply slower than 1.5 s, or a timeout, SHALL skip sending that cycle. After the reply arrives and before sending, the loop SHALL revalidate book freshness (`age_ms` ≤ 500 from #1008; fail-closed «livro indisponível»). That `age_ms` bound SHALL NOT be relaxed. `horizon_s` SHALL NOT be used as a sleep between asks. There SHALL NOT be a cap of 1 Jev consult per 15 minutes. While an open position or an exit resting order exists, the loop SHALL NOT call Jev for a new entry.

Hold SHALL be 15 minutes **after fill**. Interruptor, T, clip, kill, GTX and the Meu Perfil Spot key SHALL stay as in #1001.

#### Scenario: Lookback is the last fifteen minutes with the switch off

- **WHEN** an authenticated user opens `/monitor`
- **THEN** the stored and displayed lookback SHALL be the last 15 minutes
- **AND** the switch default SHALL remain desligado
- **AND** the module SHALL NOT offer 1 min, 2 min or 5 min as a choice

#### Scenario: Fresh-touch cadence is not a 15-minute sleep

- **WHEN** the user's scalp is ligado and there is no open position and no exit resting order
- **THEN** the loop SHALL consult Jev on the fresh stream touch
- **AND** SHALL allow more than one Jev consult inside any 15 minute interval
- **AND** SHALL keep one request in flight at a time
- **AND** SHALL NOT treat `horizon_s = 900` as a sleep

#### Scenario: Reply within 1.5 s can send

- **WHEN** Jev replies within 1.5 s and the other send gates pass (hold default, confidence, non-toxic book, hurdle, T cap, fresh book)
- **THEN** that cycle SHALL be allowed to send

#### Scenario: Late Jev still skips the send

- **WHEN** Jev takes more than 1.5 s or the wait times out
- **THEN** that cycle SHALL NOT send an order

#### Scenario: Fresh book is rechecked after the reply

- **WHEN** a Jev reply arrives within 1.5 s
- **THEN** the loop SHALL revalidate `age_ms` ≤ 500 on the book before sending
- **AND** SHALL NOT send if that freshness check fails (fail-closed «livro indisponível»)

#### Scenario: No Jev while a position is open

- **WHEN** the bot has an open position or an exit order on the book
- **THEN** the loop SHALL NOT open a Jev request for a new entry
- **AND** SHALL NOT stack a second buy

### Requirement: Enriched Jev payload and hurdle in code

The Farol SHALL compute and send the Jev `state` (it SHALL NOT ask the model to infer microstructure). `state.horizon_s` SHALL be `900` (lookback and expected-move window, never ask cadence). `state.touch` SHALL include `bid`, `ask`, `bid_qty`, `ask_qty`, `mid`, `spread_bp`, `microprice`, `imbalance` and `age_ms`. `state.window` SHALL include `horizon_s`, `trade_count`, `ret_bp`, `vol_bp`, `aggressor_flow`, `volume` and `spread_bp_mean` from the #1008 in-memory stream (rolling window size ≥ 900 s of `aggTrade` plus 1 Hz `bookTicker` snapshots). `state.account` SHALL include `inventory_btc`, `t`, `remaining_to_t`, `fee_bp` and `bnb_fee_active`. `state.resting` SHALL be `null` or `{ side, price, age_ms, role }` with `role` `entry` or `exit`. Questions SHALL be `side` (BUY/SELL/HOLD), `expected_move_bp` and `book_toxic`. The `edge_after_fees` question SHALL NOT be sent. An empty 15 minute rolling window (zero `aggTrade`) SHALL skip the cycle (no Jev, no order). This card SHALL NOT REST book or trades. TypeSafe SHALL NOT appear in the payload. `bnb_fee_active` SHALL be true only when Binance `spotBNBBurn` is on and free Spot BNB is greater than zero; otherwise `fee_bp` SHALL be 10. The loop SHALL send an entry only when `expected_move_bp` is greater than `2 × fee_bp + spread_bp`. That entry hurdle SHALL NOT set the exit target or stop. Hold remains the default. Confidence < 0.7, toxic book, full T and inventory 0 + SELL SHALL still refuse.

#### Scenario: Payload carries touch size and window aggregates

- **WHEN** the loop calls Jev
- **THEN** the body SHALL contain `touch.bid_qty`, `touch.ask_qty`, `touch.microprice`, `touch.imbalance`, `window.horizon_s` = 900, `window.ret_bp`, `window.vol_bp`, `window.aggressor_flow`, `window.volume`, `window.spread_bp_mean` and `account.fee_bp`
- **AND** SHALL NOT contain `edge_after_fees`
- **AND** SHALL NOT contain the TypeSafe secret

#### Scenario: Expected move below hurdle sends nothing

- **WHEN** Jev answers BUY with `expected_move_bp` = 10 and `fee_bp` = 10
- **THEN** the loop SHALL NOT send an order

#### Scenario: Empty window skips the cycle

- **WHEN** the rolling 15 minute lookback has zero `aggTrade` in the #1008 memory
- **THEN** the loop SHALL NOT call Jev
- **AND** SHALL NOT send an order

#### Scenario: Resting is visible but code still cancels

- **WHEN** this scalp has a resting order on the book
- **THEN** the Jev `state.resting` SHALL include `side`, `price`, `age_ms` and `role`
- **AND** a stale price off the touch SHALL still be cancelled by the Farol code without waiting for Jev

### Requirement: Mandatory post-only exit and stuck position warning

Entry SHALL remain post-only at the touch (buy at bid, sell at ask). An entry that does not fill within 10 seconds (configurable) SHALL cancel; it SHALL NOT chase price and SHALL NOT become market. Each open position SHALL have a mandatory exit, whichever comes first: target (default 35 bp), stop (default −28 bp), or max time of 15 minutes **after fill**. Exit SHALL also be post-only at the touch. If that exit does not fill by 15 minutes 30 seconds after fill, the panel SHALL show «posição presa» and the user SHALL decide; Operar SHALL remain available. There SHALL be no market order in this card. One position at a time per user. Inventory 0 + SELL SHALL still not sell the floor. Kill at −2 % of T SHALL still cancel this bot's orders and stop sending.

#### Scenario: Filled buy without fill of exit

- **WHEN** a buy fills and neither target nor stop fills within 15 minutes after fill
- **THEN** an exit post-only order SHALL be on the book
- **AND** if it still has not filled at 15 minutes 30 seconds the panel SHALL show «posição presa»

#### Scenario: Never two open buys

- **WHEN** the bot already has a position or an exit resting order
- **THEN** the loop SHALL NOT post a second buy

#### Scenario: Kill still stops this bot

- **WHEN** day loss of this loop is ≤ −2 % of T
- **THEN** the loop SHALL cancel this bot's orders
- **AND** SHALL stop sending
- **AND** SHALL NOT self-enable
