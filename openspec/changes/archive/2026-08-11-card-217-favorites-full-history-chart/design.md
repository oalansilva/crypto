## Context

Favorites analysis combines two candle sources: saved backtest chart context from `metrics.analysis_candles` and a current `/api/market/candles` response. The current response is intentionally bounded for UI freshness, while saved favorites can hold multi-year backtest candles.

## Goals / Non-Goals

**Goals:**

- Show full recoverable chart history when saved favorite candles are longer than current market candles.
- Keep current candles when they provide an equal-or-longer, fresher series.
- Preserve existing fallback behavior when a source fails.

**Non-Goals:**

- Change backend candle limits or favorite persistence.
- Recompute historical candles during the click.
- Alter trade/metric calculations.

## Decisions

- Add a small source-selection helper in Favorites. It compares saved and current candle arrays and chooses the longer valid array.
- Keep the existing current-candle request. It still upgrades short/stale saved data when the current series is more complete.
- Test the Quant BTC long-history case with saved candles longer than the current market-candles response.

## Risks / Trade-offs

- A longer saved series may not include the newest candles. Mitigation: current candles still win when they are at least as complete as saved context; the chart prioritizes complete history for Favorites analysis.
