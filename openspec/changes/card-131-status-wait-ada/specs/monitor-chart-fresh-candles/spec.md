## MODIFIED Requirements

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
