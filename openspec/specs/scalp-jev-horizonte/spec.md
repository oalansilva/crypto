# scalp-jev-horizonte Specification

## Purpose
TBD - created by syncing change card-1006-scalp-jev-horizonte. Update Purpose after archive.
## Requirements

### Requirement: Lookback, cadence and hold are three detached 15-minute roles

The directional scalp SHALL use a rolling lookback of the last 15 minutes of `aggTrade` plus the current touch (`horizon_s = 900` on the window). The lookback SHALL NOT be a 15-minute OHLCV candle and SHALL NOT be a per-user choice. The panel SHALL show «últimos 15 min» as a fact in the same vocabulary as T and clip. The module SHALL NOT present a 1 / 2 / 5 minute radio or selector.

While the scalp is on and there is **no** open position and **no** exit resting order, Jev calls SHALL follow configurable `JEV_TARGET_MS` (30 s by default), using the latest fresh stream touch; this later `scalp-jev-consult-cadence` contract supersedes the ~1 s target described by this card. One Jev request SHALL be in flight at a time. The model call SHALL time out at 3 s, while the late gate SHALL refuse sending when reply latency is above 1.5 s; the timeout and send cap stay separate under `scalp-jev-call-timeout`. A Jev reply within 1.5 s plus the other send gates (hold default, confidence, non-toxic book, hurdle, T cap, fresh book from #1008) SHALL allow that cycle to send. A Jev reply slower than 1.5 s, or a timeout, SHALL skip sending that cycle. After the reply arrives and before sending, the loop SHALL revalidate book freshness (`age_ms` ≤ 500 from #1008; fail-closed «livro indisponível»). That `age_ms` bound SHALL NOT be relaxed. `horizon_s` SHALL NOT be used as a sleep between asks. There SHALL NOT be a cap of 1 Jev consult per 15 minutes. While an open position or an exit resting order exists, the loop SHALL NOT call Jev for a new entry.

Hold SHALL be 15 minutes **after fill**. Interruptor, T, clip, kill, GTX and the Meu Perfil Spot key SHALL stay as in #1001.

#### Scenario: Lookback is the last fifteen minutes with the switch off

- **WHEN** an authenticated user opens `/monitor`
- **THEN** the stored and displayed lookback SHALL be the last 15 minutes
- **AND** the switch default SHALL remain desligado
- **AND** the module SHALL NOT offer 1 min, 2 min or 5 min as a choice

#### Scenario: Configured cadence is not a 15-minute sleep

- **WHEN** the user's scalp is ligado and there is no open position and no exit resting order
- **THEN** the loop SHALL follow configured `JEV_TARGET_MS` (30 s by default)
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

The Farol SHALL compute and send the Jev `state` (it SHALL NOT ask the model to infer microstructure). `state.horizon_s` SHALL be `900` (lookback and expected-move window, never ask cadence). `state.touch` SHALL include `bid`, `ask`, `bid_qty`, `ask_qty`, `mid`, `spread_bp`, `microprice`, `imbalance` and `age_ms`. `state.window` SHALL include `horizon_s`, `trade_count`, `ret_bp`, `vol_bp`, `aggressor_flow`, `volume` and `spread_bp_mean` from the #1008 in-memory stream (rolling window size ≥ 900 s of `aggTrade` plus 1 Hz `bookTicker` snapshots). `state.account` SHALL include `inventory_btc`, `t`, `remaining_to_t`, `fee_bp` and `bnb_fee_active`. `state.resting` SHALL be `null` or `{ side, price, age_ms, role }` with `role` `entry` or `exit`. Questions SHALL be `side` (BUY/SELL/HOLD), `expected_move_bp` and `book_toxic`. The `edge_after_fees` question SHALL NOT be sent. An empty 15 minute rolling window (zero `aggTrade`) SHALL skip the cycle (no Jev, no order). This card SHALL NOT REST book or trades. TypeSafe SHALL NOT appear in the payload. `bnb_fee_active` SHALL be true only when Binance `spotBNBBurn` is on and free Spot BNB is greater than zero; otherwise `fee_bp` SHALL be 10. The loop SHALL send an entry only when `expected_move_bp` is greater than `2 × fee_bp + spread_bp`; the later `scalp-regime-gate` also requires the forecast to cover that hurdle plus its 50% slack in the active regime. That entry hurdle SHALL NOT set the exit target or stop. Hold remains the default. Confidence SHALL follow the active regime's policy in `scalp-confidence-gate` (a justified numeric threshold, turned off, or closed); the former fixed 0.7 threshold SHALL NOT override it. Toxic book, full T and inventory 0 + SELL SHALL still refuse.

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

Entry SHALL remain post-only at the touch (buy at bid, sell at ask). An entry that does not fill within 10 seconds (configurable) SHALL cancel; it SHALL NOT chase price and SHALL NOT become market. Each open position SHALL have a passive exit, whichever comes first: target (default 35 bp) or stop (default −28 bp), posted post-only at the touch while the 15-minute window after fill remains open. If the position is still open at the end of that window, the aggressive market/IOC escape specified by `scalp-aggressive-exit` SHALL cancel any resting passive exit and fire in that cycle without a price cap; no extra passive attempt SHALL be made at or after the window end. If the position remains open at 15 minutes 30 seconds after fill, the existing panel SHALL show «posição presa» and Operar SHALL remain available; that warning SHALL NOT trigger or delay the aggressive escape. One position at a time per user. Inventory 0 + SELL SHALL still not sell the floor. Kill at −2 % of T SHALL still cancel this bot's orders and stop sending.

#### Scenario: Filled buy without fill of exit

- **WHEN** a buy fills and neither target nor stop fills by the end of the 15-minute window after fill
- **THEN** the aggressive market/IOC escape SHALL cancel any resting passive exit and be sent in that cycle
- **AND** if the position remains open at 15 minutes 30 seconds the panel SHALL show «posição presa»

#### Scenario: Never two open buys

- **WHEN** the bot already has a position or an exit resting order
- **THEN** the loop SHALL NOT post a second buy

#### Scenario: Kill still stops this bot

- **WHEN** day loss of this loop is ≤ −2 % of T
- **THEN** the loop SHALL cancel this bot's orders
- **AND** SHALL stop sending
- **AND** SHALL NOT self-enable
