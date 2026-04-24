## Indicator Score Rules v1

Ruleset: `technical-normalization/v1`

Location: `backend/config/indicator_score_rules.v1.json`

Override: `INDICATOR_SCORE_RULES_PATH=/path/to/rules.json`

## Contract

- Scores are floating point values clamped to `0-10`.
- Each emitted score includes `rule_version`.
- Missing, null, `NaN`, or non-finite inputs are skipped instead of converted to `0`.
- The scoring layer consumes persisted `market_indicator` rows and does not recalculate raw indicators.
- Scores are calculated on demand in this change; if scores are persisted later, storage must include `rule_version` in the key or metadata so historical meaning is not overwritten.

## Default Rules

| Score | Inputs | Rule | Direction |
| --- | --- | --- | --- |
| `ema_trend` | `ema_9`, `ema_21` | Fast/slow crossover, percent delta through `tanh` | Fast above slow increases score |
| `sma_trend` | `sma_20`, `sma_50` | Fast/slow crossover, percent delta through `tanh` | Fast above slow increases score |
| `rsi_14` | `rsi_14` | Linear 30-70, inverse | Lower RSI increases score |
| `macd_histogram` | `macd_histogram` | Centered `tanh` around zero | Positive histogram increases score |
| `bollinger_width` | `bb_upper_20_2`, `bb_middle_20_2`, `bb_lower_20_2` | Relative band width, inverse | Narrower bands increase score |
| `atr_14` | `atr_14`, `bb_middle_20_2` | ATR as percent of middle band, inverse | Lower volatility increases score |
| `stochastic` | `stoch_k_14_3_3` | Linear 20-80, inverse | Lower stochastic increases score |
| `ichimoku_trend` | `ichimoku_tenkan_9`, `ichimoku_kijun_26` | Tenkan/kijun crossover | Tenkan above kijun increases score |
| `pivot_range` | `resistance_1`, `pivot_point`, `support_1` | Relative S1/R1 width, inverse | Tighter range increases score |
