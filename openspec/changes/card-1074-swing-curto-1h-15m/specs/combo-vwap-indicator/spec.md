## ADDED Requirements

### Requirement: Templates can use daily VWAP reset at 00:00 UTC

The existing template editor SHALL expose a daily VWAP series that accumulates typical price × volume from 00:00 UTC and resets at each UTC midnight. A template MAY use that series in an entry or exit rule. Daily VWAP SHALL complete a backtest without error on 15m, 1h and 4h.

#### Scenario: Daily VWAP resets at UTC midnight

- **WHEN** a 15m series crosses 00:00 UTC
- **THEN** the daily VWAP accumulator restarts
- **AND** values after midnight do not include volume from the previous UTC day

#### Scenario: Daily VWAP rule backtests on 15m 1h 4h

- **WHEN** a template uses daily VWAP in an entry or exit rule on 15m, 1h and 4h
- **THEN** each backtest completes without error

### Requirement: Templates can use rolling VWAP of N candles

The existing template editor SHALL expose a rolling VWAP of the last N candles, with N an optimizable parameter like other template lengths. Rolling VWAP SHALL run on any Entra timeframe including 1d. A template MAY use rolling VWAP together with daily VWAP in the same ruleset.

#### Scenario: N is optimized

- **WHEN** a template declares rolling VWAP length N as an optimizable parameter
- **THEN** the optimizer searches N like the other numeric template parameters

#### Scenario: Rolling VWAP runs on 1d

- **WHEN** a template uses rolling VWAP on timeframe 1d
- **THEN** the backtest completes without error

#### Scenario: Both VWAPs in one template

- **WHEN** a template uses daily VWAP and rolling VWAP in entry or exit rules
- **THEN** a backtest on 15m, 1h and 4h completes without error
