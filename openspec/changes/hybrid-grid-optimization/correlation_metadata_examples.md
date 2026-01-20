# Correlation Metadata Examples

This document shows how to define correlated parameter groups for different strategy types.

## CRUZAMENTOMEDIAS (Moving Averages)

```json
{
  "template_name": "CRUZAMENTOMEDIAS",
  "description": "Triple Moving Average Crossover",
  "correlated_groups": [
    ["media_curta", "media_inter", "media_longa"]
  ],
  "parameters": {
    "media_curta": {"min": 3, "max": 15, "step": 2},
    "media_inter": {"min": 15, "max": 35, "step": 4},
    "media_longa": {"min": 25, "max": 60, "step": 5},
    "stop_loss": {"min": 0.005, "max": 0.13, "step": 0.002}
  }
}
```

## RSI Multi-Timeframe

```json
{
  "template_name": "RSI_DUAL",
  "description": "Dual RSI Strategy",
  "correlated_groups": [
    ["rsi_fast_period", "rsi_slow_period"]
  ],
  "parameters": {
    "rsi_fast_period": {"min": 7, "max": 21, "step": 2},
    "rsi_slow_period": {"min": 21, "max": 50, "step": 5},
    "rsi_oversold": {"min": 20, "max": 40, "step": 5},
    "rsi_overbought": {"min": 60, "max": 80, "step": 5}
  }
}
```

## Bollinger Bands + ATR

```json
{
  "template_name": "BBANDS_ATR",
  "description": "Bollinger Bands with ATR Filter",
  "correlated_groups": [
    ["bb_length", "bb_std"],
    ["atr_period", "atr_multiplier"]
  ],
  "parameters": {
    "bb_length": {"min": 15, "max": 30, "step": 3},
    "bb_std": {"min": 1.5, "max": 3.0, "step": 0.3},
    "atr_period": {"min": 10, "max": 20, "step": 2},
    "atr_multiplier": {"min": 1.0, "max": 3.0, "step": 0.5}
  }
}
```

## MACD + RSI Combo

```json
{
  "template_name": "MACD_RSI_COMBO",
  "description": "MACD and RSI Combined",
  "correlated_groups": [
    ["macd_fast", "macd_slow", "macd_signal"]
  ],
  "parameters": {
    "macd_fast": {"min": 8, "max": 16, "step": 2},
    "macd_slow": {"min": 20, "max": 32, "step": 3},
    "macd_signal": {"min": 6, "max": 12, "step": 2},
    "rsi_period": {"min": 10, "max": 20, "step": 2}
  }
}
```

## Notes

- **Multiple Groups**: A strategy can have multiple correlated groups (e.g., BBands + ATR example)
- **Independent Params**: Parameters not in any group are optimized sequentially
- **Grid Size**: Each group creates a separate Grid Search stage
- **Validation**: Total grid size per group should stay under 1,000 combinations
