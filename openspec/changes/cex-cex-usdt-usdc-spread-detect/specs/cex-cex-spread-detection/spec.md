## ADDED Requirements

### Requirement: Detect cross-exchange USDT/USDC spreads
The system SHALL fetch top-of-book prices for USDT/USDC from each configured exchange and compute cross-exchange spreads using best-ask as the buy price and best-bid as the sell price.

#### Scenario: Spread computation across two exchanges
- **WHEN** the system receives prices for USDT/USDC from Binance and OKX
- **THEN** it computes spread = (best_bid_okx - best_ask_binance) / best_ask_binance

### Requirement: Provide spread detection API response
The system SHALL expose an API that returns detected spreads for configured exchanges, including buy exchange, sell exchange, buy price, sell price, spread percentage, and timestamp.

#### Scenario: API returns a detected opportunity
- **WHEN** a request is made for USDT/USDC with exchanges [Binance, OKX, Bybit]
- **THEN** the API responds with a list of opportunities containing buy/sell venues and spread percentage

### Requirement: Support configurable threshold filtering
The system SHALL allow a spread threshold parameter to filter opportunities and return only those at or above the threshold.

#### Scenario: Threshold filters small spreads
- **WHEN** the request specifies a 0.2% threshold
- **THEN** opportunities below 0.2% are excluded from the response

### Requirement: No trade execution in spread detection
The system SHALL NOT place orders, transfer funds, or rebalance balances as part of spread detection.

#### Scenario: Detection request does not execute trades
- **WHEN** the detection API is called
- **THEN** no order placement or balance changes are triggered
