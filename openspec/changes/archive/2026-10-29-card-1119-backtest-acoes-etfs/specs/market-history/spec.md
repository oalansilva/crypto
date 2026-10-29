## ADDED Requirements

### Requirement: Equity 1h and 4h are built from 5m inside the session

The history service SHALL serve 1h and 4h of ação and ETF built on read from the 5m of the same series, by the same rule as the 15m of #1118: blocks anchored at 09:30 New York time (1h: 12 blocks of 5m; 4h: 48 blocks), cut at the session close (16:00, or 13:00 on a half session), never crossing closed market. A block missing an expected 5m SHALL NOT become a candle and SHALL be reported as a gap inherited from the 5m. The version of 1h and 4h SHALL be (version of the 5m, version of the rule). They SHALL NOT be stored as native series. Coverage SHALL list them as "montado do 5m".

#### Scenario: Full session on 4h

- **WHEN** NVDA 4h is read for a full session
- **THEN** there are two candles: 09:30–13:30 and 13:30–16:00 New York time

#### Scenario: Missing 5m inside an hour

- **WHEN** the 5m of 10:05 is missing on a session
- **THEN** the 1h block 09:30–10:30 is not returned as a candle and appears as a gap inherited from the 5m

#### Scenario: Coverage lists derived 1h and 4h

- **WHEN** the coverage of NVDA is read after a backtest on 1h
- **THEN** 1h and 4h appear with origin "montado do 5m" and the same covered period as the 5m
