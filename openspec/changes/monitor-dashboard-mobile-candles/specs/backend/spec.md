## ADDED Requirements

### Requirement: Backend provides OHLC candles for Favorites symbols
The backend MUST provide OHLC candlestick data for a given symbol and timeframe using existing market data providers.

#### Scenario: Request candles for a crypto pair
- **WHEN** the client requests candles for a symbol containing `/` and a supported timeframe
- **THEN** the backend returns OHLC candles sourced via the existing CCXT provider (or equivalent)

#### Scenario: Request daily candles for a stock ticker
- **WHEN** the client requests candles for a stock symbol without `/` and timeframe 1d
- **THEN** the backend returns OHLC candles sourced via Stooq or Yahoo (or equivalent)

#### Scenario: Request intraday candles for a stock ticker
- **WHEN** the client requests candles for a stock symbol without `/` and timeframe in {15m, 1h, 4h}
- **THEN** the backend returns OHLC candles sourced via Yahoo (or equivalent)

### Requirement: Timeframe validation
The backend MUST validate requested timeframes per data source.

#### Scenario: Unsupported timeframe for stocks
- **WHEN** the client requests a stock timeframe outside {15m, 1h, 4h, 1d}
- **THEN** the backend returns a clear validation error

#### Scenario: Supported timeframe for crypto
- **WHEN** the client requests a supported crypto timeframe (e.g., 1h, 4h, 1d)
- **THEN** the backend returns candle data successfully

### Requirement: Candles response is ordered and bounded
The backend MUST return candle data in chronological order and limit the number of returned candles.

#### Scenario: Candles ordered
- **WHEN** the backend returns candles
- **THEN** the candles are ordered by timestamp ascending

#### Scenario: Candles limited
- **WHEN** the client does not specify a limit
- **THEN** the backend uses a safe default limit
