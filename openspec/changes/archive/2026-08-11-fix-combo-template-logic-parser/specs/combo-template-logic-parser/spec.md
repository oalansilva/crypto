## ADDED Requirements

### Requirement: Safe Series Method Syntax
The combo template logic parser SHALL allow supported pandas Series methods needed by stored strategy templates while continuing to reject unknown identifiers and unsupported calls.

#### Scenario: Shift and abs syntax executes
- **WHEN** a combo template expression references `close.shift(1)` or `(close - ema).abs()`
- **THEN** signal generation evaluates the expression against the candle dataframe without treating `shift` or `abs` as unknown columns

#### Scenario: Unsupported method stays rejected
- **WHEN** a combo template expression references an unsupported method or identifier
- **THEN** signal generation fails clearly instead of silently accepting arbitrary Python behavior

### Requirement: Dotted Indicator Field Syntax
The combo template logic parser SHALL normalize supported dotted indicator field references to the engine's internal column names.

#### Scenario: MACD dotted fields execute
- **WHEN** a combo template expression references `macd.macd`, `macd.signal`, or `macd.histogram`
- **THEN** the parser evaluates those references as `macd_macd`, `macd_signal`, and `macd_histogram`

#### Scenario: Bollinger dotted fields remain supported
- **WHEN** a combo template expression references `bb.upper`, `bb.middle`, or `bb.lower`
- **THEN** the parser evaluates those references as `bb_upper`, `bb_middle`, and `bb_lower`
