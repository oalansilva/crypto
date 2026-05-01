## ADDED Requirements

### Requirement: Candles endpoint supports Monitor frame `4h` and `1d`
The system SHALL support `/api/market/candles` for `timeframe=4h` and `timeframe=1d` for both crypto and stock symbols.

#### Scenario: Crypto candles on 4h
- **WHEN** a client requests `/api/market/candles?symbol=BTC/USDT&timeframe=4h`
- **THEN** the request returns `200`.
- **AND** the payload includes `timeframe: 4h`.
- **AND** payload `candles` are ordered ascending by timestamp.

#### Scenario: Stock candles on 1d
- **WHEN** a client requests `/api/market/candles?symbol=AAPL&timeframe=1d`
- **THEN** the request returns `200`.
- **AND** the response comes from US-stocks source path.

#### Scenario: Invalid stock intraday timeframe
- **WHEN** a client requests `/api/market/candles?symbol=AAPL&timeframe=1h`
- **THEN** the request returns `400`.
- **AND** the response detail indicates the unsupported timeframe for stock.

### Requirement: Stock 4h candles are returned from supported 1h aggregation source
The system SHALL return `4h` stock candles using a supported intraday source and aggregation path rather than rejecting `4h` requests.

#### Scenario: Stock 4h via Yahoo path
- **WHEN** a client requests `/api/market/candles?symbol=AAPL&timeframe=4h`
- **THEN** the request returns `200`.
- **AND** the result is aggregated from a supported source that supports 1h bars.
