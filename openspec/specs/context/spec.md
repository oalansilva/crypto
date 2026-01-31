# context Specification

## Purpose
TBD - created by syncing delta from change add-advanced-backtest-metrics. Market context metrics for backtest results.

## Requirements

### Requirement: Calculate Average ATR
The system MUST calculate the Average True Range (ATR) over the backtest period and return the mean value.
#### Scenario:
Backtest runs for 100 candles. ATR series is computed. Mean of this series is returned as `avg_atr`.

### Requirement: Calculate Average ADX
The system MUST calculate the Average Directional Index (ADX) over the backtest period and return the mean value.
#### Scenario:
Backtest runs for 100 candles. ADX series is computed. Mean of this series is returned as `avg_adx`.
