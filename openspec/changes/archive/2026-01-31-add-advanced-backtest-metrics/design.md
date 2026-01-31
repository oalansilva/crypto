# Design: Advanced Metrics Architecture

## Logic Flow

1.  **Indicator Pre-calculation**: 
    - Ensure ATR and ADX are calculated for the entire dataframe during the signal generation phase (or immediately after) if they are not part of the strategy.
    - Compute `Regime` classification column.
        - **Bull**: Price > SMA200 (or EMA200).
        - **Bear**: Price < SMA200.
        - **Sideways**: ADX < 20 (Strong Trend > 25).
          - *Refinement*: Maybe just Bull (Close > SMA200) vs Bear (Close < SMA200) + Low Vol (ADX<20).
          - *Proposed Definition*: 
            - Bull: Close > SMA(200)
            - Bear: Close < SMA(200)
            - Trend Strength: Strong if ADX > 25.

2.  **Metric Calculation (`app/metrics/` & `src/report/metrics.py`)**:
    - **Expectancy**: `(Win Rate * Avg Win) - (Loss Rate * Avg Loss)`.
    - **Streak**: Iterate trades, count consecutive `pnl < 0`.
    - **Average Indicators**: `df['ATR'].mean()`, `df['ADX'].mean()`.

3.  **Regime Segmentation**:
    - For each trade, identify the Regime at `entry_time`.
    - Group trades by Regime.
    - Calculate aggregate PnL/WinRate per regime.

## Data Structures

New fields in `metrics` dictionary:
```json
{
  "expectancy": 15.5,
  "avg_win": 100.0,
  "avg_loss": 50.0,
  "max_consecutive_losses": 4,
  "avg_atr": 105.5,
  "avg_adx": 35.2,
  "regime_performance": {
    "bull": {"trades": 50, "pnl": 5000, "win_rate": 60},
    "bear": {"trades": 30, "pnl": -1000, "win_rate": 40},
    "sideways": {"trades": 10, "pnl": 0, "win_rate": 50}
  }
}
```
