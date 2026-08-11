## Context

Favorites and Monitor now share the operational chart surface, but marker construction still lives in multiple callers. Each caller turns a trade into one entry marker and one exit marker. When a daily trade opens and closes on the same candle timestamp, the chart receives independent `COMPRA` and `VENDA` markers at the same time, which reads as contradictory simultaneous advice instead of one same-candle round trip.

## Goals / Non-Goals

**Goals:**

- Make trade-to-marker conversion deterministic and shared across Favorites result charts and Monitor chart modals.
- Collapse valid same-candle entry/exit pairs into one explicit combined marker.
- Preserve normal separate entry/exit markers when trades span different candles.
- Keep existing Portuguese labels and current chart test contracts.

**Non-Goals:**

- Recalibrate strategy parameters or trading logic.
- Change metric calculation.
- Add database columns.
- Solve unrelated signal divergence for other strategies unless it uses the same marker construction path.

## Decisions

- Add a shared frontend chart marker utility instead of patching only one page.
  - Rationale: the same favorite can be opened through Favorites and Monitor. One utility prevents drift.
  - Alternative considered: normalize inside `StrategyChartSurface`. Rejected because that component only sees markers, not the source trade context or direction.
- Treat same-candle entry and exit as a valid round trip by default.
  - Rationale: daily backtests can produce entry and exit timestamps that normalize to the same candle. The UI should be explicit without changing strategy math.
  - Alternative considered: delete one marker. Rejected because it hides real trade history.
- Normalize same-candle comparison by UTC candle timestamp.
  - Rationale: chart timestamps already render in UTC seconds, so comparison should use the same anchor.

## Risks / Trade-offs

- Same-day but different intraday times on a daily chart may collapse into one marker if both normalize to the same daily candle. This is intended for 1D display and keeps the UI coherent.
- Existing E2E assertions that count markers may need targeted updates where same-candle samples are introduced.
- If the root cause is backend trade extraction creating invalid same-candle trades, this change still surfaces them clearly; implementation evidence must record whether the ADA case is valid round trip or upstream data bug.
