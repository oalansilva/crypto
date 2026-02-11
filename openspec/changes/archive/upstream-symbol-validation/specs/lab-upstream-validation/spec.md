# Requirements

## ADDED Requirements

### Requirement: Upstream Symbol Validation
**Description:** The system MUST validate the symbol provided by the user (extracted by the Trader) against the available symbols on the configured exchange (Binance USDT pairs).
**Priority:** High

#### Scenario: User provides valid symbol
**Given** the upstream chat history contains a valid symbol (e.g., "BTC/USDT")
**When** the Trader extracts the symbol
**Then** the system checks if "BTC/USDT" exists in the `ExchangeService` cache
**And** if it exists, the system accepts the input and proceeds with the conversation.

#### Scenario: User provides invalid symbol (typo)
**Given** the upstream chat history contains an invalid symbol (e.g., "BTC/USTD")
**When** the Trader extracts the symbol
**Then** the system checks if "BTC/USTD" exists in the `ExchangeService` cache
**And** if it does NOT exist, the system MUST NOT update the run input
**And** the system injects a system error message into the upstream chat history: "System: Symbol 'BTC/USTD' not found in Binance USDT pairs. Please ask the user to correct it."
**And** the Trader will ask the user for clarification in the next turn.

#### Scenario: Symbol cache unavailable
**Given** the symbol cache is unavailable or fails to load
**When** the Trader extracts a symbol
**Then** the system attempts to fetch symbols from the exchange
**And** if fetch fails, the system logs a warning but allows the symbol (soft fail) to avoid blocking valid inputs during network issues.

### Requirement: Upstream Timeframe Validation
**Description:** The system SHALL validate the timeframe provided by the user against the supported timeframes.
**Priority:** Medium

#### Scenario: Invalid timeframe
**Given** the user provides an invalid timeframe (e.g., "37h")
**When** the Trader extracts the timeframe
**Then** the system checks if "37h" is in the supported timeframes list
**And** if not, the system injects a system error message: "System: Timeframe '37h' not supported. Use: 1h, 4h, 1d, etc."
