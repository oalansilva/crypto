## ADDED Requirements

### Requirement: An aggressive exit closes any position the passive exit did not fill

The scalp Binance client SHALL gain an aggressive exit order (`MARKET`/IOC), which does not exist today — only post-only `LIMIT`/GTX exists. The aggressive exit SHALL be fired in the **first cycle in which the end of the waiting window is reached** (`HOLD_AFTER_FILL_S`, 15 minutes after the fill) with the position still open — that is, without a passive fill — and it SHALL be sent **without any price cap** (it exits whatever the price). The `stuck` mark (`STUCK_AFTER_FILL_S`, 930 s) SHALL NOT be the trigger of the escape and SHALL NOT be required for it. The escape SHALL be **reachable while a bot passive exit is resting and unfilled**: the exit-path gates SHALL be ordered so that the end-of-window/escape condition is evaluated **before** the return that refuses the cycle because a resting exit exists — today the `if resting is not None → skip_reason="exit_resting"` branch returns before the `stuck` branch, so the escape must come before the `exit_resting` return. At the moment of the escape, any unfilled bot passive exit SHALL be cancelled before the aggressive order is sent in the same cycle. No extra passive attempt SHALL be made at or after the end of the waiting window. The aggressive exit SHALL replace the inert behaviour in which `decide_exit_cycle` returned `skip_reason="stuck"` without sending any order.

#### Scenario: Unfilled passive exit is closed by the aggressive path

- **WHEN** the first cycle in which the end of the waiting window is reached finds the position still open and a bot passive exit resting and unfilled
- **THEN** the escape SHALL be reached (the `exit_resting` refusal SHALL NOT preempt it)
- **AND** the unfilled bot passive exit SHALL be cancelled and the aggressive exit SHALL be sent in that cycle
- **AND** the position SHALL be closed by that order

#### Scenario: Escape fires at the end of the waiting window, not at the stuck mark

- **WHEN** the waiting window has ended with the position still open
- **THEN** the aggressive exit SHALL be sent in the first cycle that sees it
- **AND** the escape SHALL NOT wait for the `stuck` mark (`STUCK_AFTER_FILL_S`)

#### Scenario: No price cap on the escape

- **WHEN** the aggressive exit is sent
- **THEN** it SHALL NOT carry a price ceiling or a slippage guard that could prevent it from filling
- **AND** the exit price obtained SHALL be recorded

#### Scenario: No extra passive attempt at or after the window end

- **WHEN** the waiting window has ended without a passive fill
- **THEN** the bot SHALL NOT post a passive exit order at the end of the window nor before going aggressive
- **AND** any unfilled bot passive exit SHALL be cancelled so the aggressive order can take the position

#### Scenario: A position past the waiting window is never inert

- **WHEN** a cycle finds an open position whose waiting window has ended and no passive exit resting
- **THEN** the bot SHALL send the aggressive exit in that cycle
- **AND** SHALL NOT refuse the cycle with an inert `stuck` and no order

### Requirement: No position crosses the waiting window without an exit attempt, and the aggressive exit is visible

The invariant SHALL hold that no position crosses the waiting window without an exit attempt — the passive one within the window (target/stop), or the aggressive one at or after its end. The aggressive exit SHALL leave a visible record in the #1015 diagnostic log (at WARNING level, with its own reason token and the exit data). It SHALL NOT add any field, alert or control to the Monitor panel or to the scalp status output, whose refusal reasons stay log-only.

#### Scenario: Every position has an exit attempt by the end of the window

- **WHEN** a position reaches the end of the waiting window still open
- **THEN** an exit attempt SHALL have been made — the passive one within the window, or the aggressive one at its end
- **AND** the position SHALL NOT stay open without any exit attempt

#### Scenario: The aggressive exit leaves a visible record

- **WHEN** the aggressive exit is sent
- **THEN** the diagnostic log SHALL contain a WARNING record with its own reason token and the exit data
- **AND** the panel and the scalp status SHALL stay unchanged

#### Scenario: Panel is not borrowed for the escape

- **WHEN** the aggressive exit fires
- **THEN** no new field, alert, route or control SHALL appear in `/monitor`, `/favorites`, `/combo/discovery`, `/combo/select` or the landing
- **AND** the only visible surface SHALL be the log
