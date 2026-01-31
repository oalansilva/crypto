# Proposal: Add Advanced Backtest Metrics

## Goal
Enhance the backtesting engine to calculate and return a comprehensive set of advanced financial metrics, enabling deeper analysis of strategy performance across different market conditions.

## Context
Currently, the backtest results include basic metrics (ROI, CAGR, Drawdown) but lack deeper risk adjustments and contextual performance data requested by the user.

## Capabilities
1.  **Strict Performance Metrics**: Calculate Expectancy, Avg Win/Loss, Max Consecutive Losses.
2.  **Market Context**: Calculate quantitative measure of "Regime" (Bull/Bear/Sideways) and average volatility (ATR) and trend strength (ADX).
3.  **Regime Analysis**: Breakdown performance metrics by market regime.

## Risks
- **Performance**: Calculating per-regime metrics requires iterating through all trades and correlating with market state, which might add overhead on large datasets.
- **Complexity**: "Regime" definitions are subjective. We will stick to a standard definition (e.g. SMA200 + ADX) but make it clear.
