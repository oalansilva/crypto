# Proposal: Display Advanced Backtest Metrics in UI

## Goal
Update the `OptimizationResultsNew` component to display the newly calculated advanced metrics (Expectancy, Streak, ATR, ADX, Regime) for the Best Result.

## Context
The backend now returns these metrics. The UI needs to show them to the user to provide better insight into strategy performance.

## Capabilities
1.  **Extended Metrics Interface**: Update `OptimizationItem` type definition.
2.  **Advanced Metrics Card**: Add a new dashboard card showing Expectancy, Max Consecutive Losses, and Avg Volatility (ATR/ADX).
3.  **Regime Visualization**: Display a concise summary of performance by market regime (Bull vs Bear) if available.
