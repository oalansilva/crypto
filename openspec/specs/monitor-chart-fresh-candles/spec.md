# monitor-chart-fresh-candles Specification

## Purpose
TBD - created by archiving change issue-124-align-ada-hold-chart-signal. Update Purpose after archive.
## Requirements
### Requirement: Monitor chart candles refresh stale persisted data
The Monitor chart candles endpoint SHALL refresh from the live market provider when persisted OHLCV candles exist but are stale for the requested timeframe. For crypto chart requests, persisted candle freshness MUST be evaluated against the current expected market bucket for the requested timeframe, not only by a broad age threshold.

#### Scenario: Persisted daily candles are stale
- **WHEN** the chart requests `1d` candles for a crypto pair
- **AND** the latest persisted candle is older than the current expected daily market bucket
- **THEN** the endpoint fetches fresh candles from the crypto market provider
- **AND** the response returns the fresh provider candles.

#### Scenario: Persisted candles are fresh
- **WHEN** the chart requests candles for a crypto pair
- **AND** persisted candles include the current expected market bucket for the requested timeframe
- **THEN** the endpoint returns the persisted candles without calling the market provider.

### Requirement: Monitor chart opens on strategy timeframe
The Monitor chart modal SHALL use the opportunity strategy timeframe as the initial chart timeframe so signal validation starts with matching candles.

#### Scenario: Strategy timeframe differs from saved price timeframe
- **WHEN** a trader opens a Monitor chart for an opportunity
- **AND** the opportunity strategy timeframe differs from the saved price timeframe preference
- **THEN** the modal initially requests candles for the strategy timeframe
- **AND** the trader can still switch timeframe manually after the modal opens.

