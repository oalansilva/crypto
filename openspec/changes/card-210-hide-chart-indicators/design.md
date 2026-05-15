## Context

The Monitor chart modal currently creates candlestick, volume, EMA, and SMA series. For non-protected strategies it also shows indicator toggle buttons and footer legend entries. Card #210 changes the chart goal: charts should be decision-focused and show only Buy/Sell signal context rather than technical indicator overlays.

## Goals / Non-Goals

**Goals:**
- Remove visible EMA/SMA indicator overlays from the Monitor chart modal.
- Remove user controls and legends for those indicators.
- Keep Compra/Venda signal markers and chart interaction controls.

**Non-Goals:**
- Change backend signal generation or opportunity classification.
- Remove risk, candle, or signal-history panels outside the chart canvas.
- Change admin-only strategy configuration screens.

## Decisions

- Stop creating moving-average line series in the chart modal instead of only hiding them with default state. This removes the visual indicators and avoids carrying inactive chart state.
- Keep calculation helpers and sidebar values where still used by non-chart context, unless cleanup becomes safely obvious during implementation.
- Do not alter API payloads because this is a display change.

## Risks / Trade-offs

- Removing indicator toggles may break tests expecting those controls. Mitigation: update or add focused tests to assert the new absence.
- Users lose quick visual moving-average context on the chart. Mitigation: this matches the requested MVP focus on Compra/Venda signals.
