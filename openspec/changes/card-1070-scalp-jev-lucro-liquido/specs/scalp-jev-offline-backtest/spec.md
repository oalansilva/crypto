## ADDED Requirements

### Requirement: Offline backtest counts two hundred independent windows per regime without the live log

The Farol SHALL provide a read-only offline replay over historical Binance BTCUSDT aggTrades that uses the same `scalp_engine` decision logic as the live loop and the account's real fee terms (maker on each filled limit leg; taker plus the version's slippage cap only when the limit exit does not fill). The replay SHALL emit non-overlapping windows, compare the signal with a random rule that buys in the same proportion, compare the side with buy-and-hold, and report net return per target/stop pair and per prazo, including prazos longer than 15 minutes. One execution SHALL produce at least 200 independent windows per market regime. The live diagnostic log SHALL NOT be the source of that 200 count. Only replies with a declared model and a declared confidence origin SHALL enter the sample. The replay SHALL NOT write product, trading state, or an applied version.

#### Scenario: One run reaches two hundred windows per regime from history

- **WHEN** the offline replay executes over historical aggTrades
- **THEN** each market regime SHALL have at least 200 independent non-overlapping windows in that run
- **AND** those windows SHALL NOT be counted from the live diagnostic log

#### Scenario: Fees follow the live fill rule

- **WHEN** a replayed window exits on a filled limit order
- **THEN** that leg SHALL be charged the maker rate in use
- **AND** a market/IOC last-resort exit SHALL be charged the taker rate and SHALL respect the slippage cap
- **AND** a window whose limit exit fills SHALL NOT be charged the taker rate

#### Scenario: Signal is compared with chance and with holding

- **WHEN** the replay reports a sample
- **THEN** it SHALL show the signal against a random rule with the same buy proportion
- **AND** SHALL show the side against buy-and-hold
- **AND** SHALL show net return by target/stop and by prazo, including prazos longer than 15 minutes

#### Scenario: Unidentified replies do not enter

- **WHEN** a reconstructed call has no declared model or no declared confidence origin
- **THEN** that window SHALL NOT count toward the 200
- **AND** SHALL NOT justify a geometry
