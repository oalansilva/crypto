## ADDED Requirements

### Requirement: Barriers resolve on the real price path

The read-only Jev ruler SHALL resolve target, stop and prazo on the real price path: historical or stored aggTrades, or complete 1-second candles covering the window. It SHALL NOT treat gappy or ambiguous OHLCV (1 m / 5 m / 15 m) as the barrier verdict. The sample SHALL include only replies with a declared model and a declared confidence origin. On the same windows as the 29/09 report, fewer than 5% of geometry alternatives SHALL remain indeterminate.

#### Scenario: AggTrades decide which barrier was hit first

- **WHEN** a window has a complete aggTrade path
- **THEN** the ruler SHALL mark target, stop or time-exit from that path
- **AND** SHALL NOT leave the window indeterminate because a 15-minute candle contained both barriers

#### Scenario: Complete 1-second candles are the fallback path

- **WHEN** aggTrades for a window are missing and 1-second candles cover that window without gaps
- **THEN** the ruler SHALL resolve the barrier on those candles
- **AND** SHALL NOT fall back to gappy 1 m / 5 m / 15 m OHLCV for that verdict

#### Scenario: The 29/09 windows stay almost fully determined

- **WHEN** the ruler remeasures the 29/09 window set
- **THEN** fewer than 5% of the target/stop/prazo alternatives SHALL be indeterminate
- **AND** unidentified model or confidence-origin replies SHALL NOT enter that sample
