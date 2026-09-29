## MODIFIED Requirements

### Requirement: An aggressive exit closes any position the passive exit did not fill

When the applied waiting window (`HOLD_AFTER_FILL_S` from the consumed version) ends with the position still open, the loop SHALL first post a post-only limit exit on the realizable side. The unfilled target/stop rest SHALL be cancelled so that limit can stand. Only if that limit does not fill SHALL the loop send a last-resort IOC limit whose price is capped by the version's slippage ceiling (basis points from the fresh mid). It SHALL NOT send an uncapped `MARKET`. The `stuck` mark SHALL NOT be the trigger of that last resort and SHALL NOT be required for it. The end-of-window path SHALL be reachable while a bot passive exit is resting and unfilled: the `exit_resting` refusal SHALL NOT preempt it.

#### Scenario: Unfilled passive exit is replaced by a limit at window end

- **WHEN** the first cycle in which the end of the waiting window is reached finds the position still open and a bot passive exit resting and unfilled
- **THEN** the unfilled bot passive exit SHALL be cancelled
- **AND** a post-only limit exit SHALL be posted in that cycle
- **AND** an uncapped MARKET SHALL NOT be sent in that cycle

#### Scenario: Escape fires at the end of the waiting window, not at the stuck mark

- **WHEN** the waiting window has ended with the position still open
- **THEN** the limit-at-window-end path SHALL run in the first cycle that sees it
- **AND** the last-resort IOC SHALL NOT wait for the `stuck` mark

#### Scenario: Last resort carries a slippage cap

- **WHEN** the window-end limit has not filled and the last-resort exit is sent
- **THEN** it SHALL be an IOC limit priced within the version's slippage cap from the fresh mid
- **AND** it SHALL NOT be an uncapped MARKET
- **AND** if the book is already beyond that cap the cycle SHALL NOT send and SHALL retry the post-only limit on the next cycle

#### Scenario: A position past the waiting window is never inert

- **WHEN** a cycle finds an open position whose waiting window has ended
- **THEN** the bot SHALL have a live limit exit or a capped last-resort attempt
- **AND** SHALL NOT refuse the cycle with an inert `stuck` and no order

### Requirement: No position crosses the waiting window without an exit attempt, and the aggressive exit is visible

The invariant SHALL hold that no position crosses the waiting window without an exit attempt — the passive target/stop within the window, the post-only limit at its end, or the capped last-resort IOC. The last-resort exit SHALL leave a visible record in the #1015 diagnostic log (at WARNING level, with its own reason token and the exit data). The Monitor status and stuck copy MAY name that limit-then-capped path; this card SHALL NOT add a catalog route or a new control.

#### Scenario: Every position has an exit attempt by the end of the window

- **WHEN** a position reaches the end of the waiting window still open
- **THEN** an exit attempt SHALL have been made — the passive one within the window, or the window-end limit
- **AND** the position SHALL NOT stay open without any exit attempt

#### Scenario: The last-resort exit leaves a visible record

- **WHEN** the capped last-resort exit is sent
- **THEN** the diagnostic log SHALL contain a WARNING record with its own reason token and the exit data
- **AND** the scalp status MAY describe that last resort in the estado / posição presa copy

#### Scenario: Panel is not rebuilt for the escape

- **WHEN** the window-end exit path runs
- **THEN** no new route or control SHALL appear in `/monitor`, `/favorites`, `/combo/discovery`, `/combo/select` or the landing
- **AND** board and Operar SHALL stay
