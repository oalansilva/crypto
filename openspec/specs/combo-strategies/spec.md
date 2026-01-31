# combo-strategies Specification

## Purpose
Enable users to create and backtest trading strategies that combine multiple indicators with flexible logic (multi-MA crossovers, trend + momentum, pullback entries, breakout validation).

## Requirements

### Requirement: Select Combo Strategy Template
The strategy selection UI SHALL display a "Combo Strategies" section with pre-built templates. The system MUST provide at least 6 combo templates (Multi-MA Crossover, EMA+RSI, EMA+MACD+Volume, EMA+RSI+Fibonacci, Volume+ATR, Bollinger+RSI+ADX). Each template MUST show description and component indicators.

### Requirement: Configure Combo Strategy Parameters
The parameter form SHALL group parameters by indicator. All parameters MUST support optimization ranges for grid search.

### Requirement: Support Multi-Instance Indicators with Aliases
The combo strategy system SHALL support multiple instances of the same indicator type with unique aliases. The system MUST resolve aliases to actual column names during signal generation.

### Requirement: Create Custom Combo via Visual Builder
The system SHALL provide a visual interface for creating custom combo strategies: select indicators, configure parameters, assign aliases, define entry/exit logic without writing code.
