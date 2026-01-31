# Proposal: Add Indicator Combinations

## Overview
Enable users to create flexible trading strategies by combining multiple indicators with custom logic, moving beyond single-indicator strategies to support professional trading patterns like "Trend + Momentum", "Pullback in Trend", and "Breakout Confirmation".

## Problem Statement
Currently, the backtester only supports single-indicator strategies (RSI, MACD, Bollinger Bands, etc.). Professional traders typically combine multiple indicators to:
- **Filter signals**: Use trend indicators (EMA) to filter momentum signals (RSI)
- **Confirm entries**: Use volume or ADX to confirm breakouts
- **Reduce false signals**: Combine multiple conditions before entering trades

Users cannot implement common trading patterns like:
1. **Multi-MA Crossover**: EMA 3 + SMA 37 + SMA 32 - crossover strategy with 3 moving averages (like CRUZAMENTOMEDIAS)
2. **Trend + Momentum**: EMA 9/21 + RSI (14) - only trade when price is above EMAs and RSI confirms
3. **Trend + Momentum + Volume**: EMA 20/50 + MACD + Volume - confirm moves with volume
4. **Pullback in Trend**: EMA 50 + RSI + Fibonacci - enter on pullbacks in strong trends
5. **Breakout**: Support/Resistance + Volume + ATR - confirm breakouts with volume
6. **Statistical Combo**: Bollinger Bands + RSI + ADX - trade reversions in ranging markets

## Proposed Solution
Create a new **ComboStrategy** system that allows users to:
1. Select multiple indicators (2-4 indicators per strategy)
2. Use multiple instances of the same indicator with different parameters (e.g., 3 EMAs)
3. Assign aliases to each indicator instance for clear logic (e.g., "fast", "slow", "intermediate")
4. Define custom entry/exit logic combining indicator signals with crossover/crossunder support
5. Optimize parameters for each indicator independently
6. Visualize all indicators on the results chart

### Key Features
- **Pre-built Combo Templates**: 6 common combinations (listed below) ready to use
- **Visual Combo Builder**: Create custom combos via drag-and-drop interface (no coding required)
- **Save Custom Templates**: Save your custom combos for reuse
- **Multi-Instance Support**: Use multiple instances of the same indicator (e.g., 3 moving averages with different periods)
- **Indicator Aliases**: Name each indicator instance (e.g., "fast", "slow", "intermediate") for clear logic
- **Flexible Logic**: Support AND/OR conditions between indicators with crossover/crossunder detection
- **Sequential Optimization**: Optimize parameters one at a time (much faster than grid search)
- **Chart Visualization**: Display all indicators used in the combination

## User Impact
- **Beginner traders**: Use pre-built templates for proven strategies
- **Intermediate traders**: Customize templates with different parameters
- **Advanced traders**: Create custom combinations with complex logic
- **All users**: Better backtest results through multi-indicator confirmation

## Implementation Approach

**Zero Impact on Existing Functionality**: All combo strategy features will be implemented in **new, isolated routes and components**.

### New Frontend Routes (No Changes to Existing Pages)
- `/combo/select` - Combo template selection page
- `/combo/configure` - Combo parameter configuration page
- `/combo/optimize` - Combo sequential optimization page
- `/combo/results` - Combo backtest results with multiple indicators

**Existing routes remain unchanged**: `/optimize/parameters`, `/backtest`, etc.

### New Backend Endpoints (No Changes to Existing APIs)
- `GET /api/combos/templates` - List available combo templates
- `GET /api/combos/meta/:template` - Get template schema
- `POST /api/combos/backtest` - Execute combo backtest
- `POST /api/combos/optimize` - Run sequential optimization for combos

**Existing endpoints remain unchanged**: `/api/backtest`, `/api/optimize/sequential`, etc.

### New Backend Classes (No Changes to Existing Strategies)
- `backend/app/strategies/combos/` - New directory for combo strategies
- `ComboStrategy` base class - Isolated from `DynamicStrategy`
- Individual combo templates - Separate files for each template

**Existing strategies remain unchanged**: `DynamicStrategy`, `CruzamentoMedias`, etc.

## Scope
This change introduces one new capability:
- **combo-strategies**: Core combo strategy system with templates and custom builder

## Dependencies
- Builds on existing `strategy-enablement` spec
- Uses existing indicator implementations from `DynamicStrategy`
- Extends `backtest-config` for combo strategy configuration

## Out of Scope
- Machine learning-based indicator selection
- Real-time strategy optimization
- Indicator correlation analysis
- Custom indicator creation (only combines existing indicators)

## Success Criteria
1. Users can select and run pre-built combo strategies
2. Users can customize parameters for each indicator in a combo
3. Users can configure custom optimization ranges (Min, Max, Step) for each parameter
4. Sequential optimization works for combo strategies and is significantly faster than grid search
5. Results chart displays all indicators in the combo
6. Performance is comparable to single-indicator strategies (no significant slowdown)
