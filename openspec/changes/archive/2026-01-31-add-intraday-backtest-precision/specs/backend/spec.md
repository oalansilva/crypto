## ADDED Requirements

### Requirement: Intraday Execution Validation
The backtest engine SHALL validate trade execution using intraday data when precision mode is enabled.

#### Scenario: Stop loss hit before target (loss)
- **GIVEN** a long trade entered at $100,000 with stop at $98,500 and no explicit target
- **AND** the daily candle shows Low=$98,400, High=$105,000
- **WHEN** iterating through 1h candles for that day
- **AND** the 10:00 candle Low touches $98,400 (stop triggered)
- **THEN** exit the trade at $98,500 at 10:00
- **AND** ignore subsequent price action (even if it rallied to $105,000 later)

#### Scenario: Target hit before stop (win)
- **GIVEN** a long trade entered at $100,000 with target at $110,000 and stop at $98,500
- **AND** the daily candle shows Low=$98,400, High=$110,500
- **WHEN** iterating through 1h candles
- **AND** the 14:00 candle High reaches $110,000 first
- **THEN** exit the trade at $110,000 at 14:00
- **AND** ignore the later drop to $98,400

#### Scenario: Fast mode (daily only) - ambiguous case
- **GIVEN** precision mode is set to "fast"
- **AND** a trade with tight stop (1.5%)
- **WHEN** the daily candle Low touches the stop
- **THEN** assume pessimistic execution (stop hit first)
- **AND** log a warning: "Tight stop detected in fast mode - results may be optimistic"

### Requirement: Precision Mode Configuration
The system SHALL accept a `precision_mode` parameter in backtest requests.

#### Scenario: Enable precise mode
- **WHEN** backtest request includes `{ "precision_mode": "precise", "intraday_timeframe": "1h" }`
- **THEN** use 1h data to validate execution
- **AND** return results with metadata: `{ "precision": "deep", "intraday_tf": "1h" }`

#### Scenario: Default to fast mode
- **WHEN** backtest request omits `precision_mode`
- **THEN** use daily-only execution (current behavior)
- **AND** return results with metadata: `{ "precision": "fast" }`
