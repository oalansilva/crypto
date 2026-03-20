# combo-strategies Specification

## Purpose
Enable users to create and backtest trading strategies that combine multiple indicators with flexible logic (multi-MA crossovers, trend + momentum, pullback entries, breakout validation).

## Requirements

### Requirement: Select Combo Strategy Template
The strategy selection UI SHALL display a "Combo Strategies" section with pre-built templates. The system MUST provide at least 6 combo templates (Multi-MA Crossover, EMA+RSI, EMA+MACD+Volume, EMA+RSI+Fibonacci, Volume+ATR, Bollinger+RSI+ADX). Each template MUST show description and component indicators.

#### Scenario: Display combo templates section
- **GIVEN** the user is on the strategy selection page
- **WHEN** the page loads
- **THEN** a "Combo Strategies" section is displayed
- **AND** at least 6 pre-built templates are shown with descriptions and component indicators

### Requirement: Configure Combo Strategy Parameters
The parameter form SHALL group parameters by indicator. All parameters MUST support optimization ranges for grid search.

#### Scenario: Group parameters by indicator
- **GIVEN** a combo strategy with multiple indicators is selected
- **WHEN** the parameter form is displayed
- **THEN** parameters are grouped by their indicator
- **AND** each parameter supports optimization ranges for grid search

### Requirement: Support Multi-Instance Indicators with Aliases
The combo strategy system SHALL support multiple instances of the same indicator type with unique aliases. The system MUST resolve aliases to actual column names during signal generation.

#### Scenario: Multiple instances of same indicator type
- **GIVEN** a combo strategy requires two SMA indicators with different periods
- **WHEN** the strategy is configured with aliases "sma_fast" and "sma_slow"
- **THEN** the system resolves aliases to actual column names during signal generation
- **AND** both indicators can be used in entry/exit logic

### Requirement: Create Custom Combo via Visual Builder
The system SHALL provide a visual interface for creating custom combo strategies: select indicators, configure parameters, assign aliases, define entry/exit logic without writing code.

#### Scenario: Create custom combo without code
- **GIVEN** the user accesses the visual builder
- **WHEN** the user selects indicators, configures parameters, assigns aliases, and defines entry/exit logic
- **THEN** a custom combo strategy is created without writing code
