## MODIFIED Requirements

### Requirement: Backtest Configuration Parameters
The system SHALL accept the following backtest configuration parameters:
- `symbol`: Trading pair (e.g., "BTC/USDT")
- `timeframe`: Signal generation timeframe (e.g., "1d", "4h")
- `since`: Start date (ISO 8601)
- `until`: End date (ISO 8601)
- `strategy`: Strategy template name
- `parameters`: Strategy-specific parameters (e.g., MA lengths, stop loss)
- **NEW**: `precision_mode`: Execution validation mode (`"fast"` | `"precise"`)
- **NEW**: `intraday_timeframe`: Timeframe for intraday validation (e.g., `"1h"`, `"15m"`) - required when `precision_mode="precise"`

#### Scenario: Precise backtest configuration
- **WHEN** user configures backtest with `{ "precision_mode": "precise", "intraday_timeframe": "1h" }`
- **THEN** the system validates that 1h data is available for the requested period
- **AND** proceeds with deep backtesting using 1h candles

#### Scenario: Invalid precision configuration
- **WHEN** user sets `precision_mode="precise"` without specifying `intraday_timeframe`
- **THEN** return validation error: "intraday_timeframe required when precision_mode is precise"

#### Scenario: Fast mode (backward compatible)
- **WHEN** user omits `precision_mode` or sets it to `"fast"`
- **THEN** use daily-only execution (existing behavior)
- **AND** ignore `intraday_timeframe` if provided
