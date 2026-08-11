## MODIFIED Requirements

### Requirement: Support Multi-Instance Indicators with Aliases
The combo strategy system SHALL support multiple instances of the same indicator type with unique aliases. The system MUST resolve aliases and supported dotted indicator fields to actual column names during signal generation.

#### Scenario: Multiple instances of same indicator type
- **GIVEN** a combo strategy requires two SMA indicators with different periods
- **WHEN** the strategy is configured with aliases "sma_fast" and "sma_slow"
- **THEN** the system resolves aliases to actual column names during signal generation
- **AND** both indicators can be used in entry/exit logic

#### Scenario: Dotted indicator field alias
- **GIVEN** a combo strategy defines a MACD indicator with alias "macd"
- **WHEN** the strategy logic references "macd.macd" and "macd.signal"
- **THEN** the system resolves those fields to the generated MACD columns during signal generation
