## Context

The Monitor currently opens `ChartModal` from table rows and expanded `OpportunityCard` details. That modal always renders the chart, signal context, summary, and `StrategyTradesTable` together. Card #227 asks for two user-facing actions so a trader can either inspect only the graph or open the deeper trade/summary analysis.

The UI must follow `DESIGN.md`: Binance dark surface, yellow primary action, compact 8px-or-less radii, Portuguese labels, stable responsive sizing, and no text overlap.

## Goals / Non-Goals

**Goals:**

- Add `Abrir Grafico` and `Ver Trades` actions wherever the Monitor currently exposes the chart action.
- Let `Abrir Grafico` open a chart-only modal without the strategy summary side panel or trades table.
- Let `Ver Trades` open the existing analysis view with chart, strategy summary, signal context, and trades list.
- Keep existing candle fetching, signal markers, favorite trade loading, and protected-strategy behavior.

**Non-Goals:**

- Changing backend contracts.
- Redesigning Monitor filtering, signal classification, Favorites, or trade metrics.
- Archiving the OpenSpec change before release.

## Decisions

- Reuse `ChartModal` with a `viewMode` prop instead of creating a second modal.
  - Rationale: the chart data loading, markers, timeframe toolbar, and trade recovery logic already live there.
  - Alternative considered: duplicate a chart-only modal. Rejected because it would duplicate chart-state and increase regression risk.

- Track the selected modal mode in `MonitorStatusTab` alongside the active opportunity.
  - Rationale: the caller owns which action was clicked, and the modal remains stateless with respect to workflow choice.
  - Alternative considered: internal modal tabs. Rejected because the card asks for two entry actions, not an in-modal mode switch.

- Keep trades fetching disabled in chart-only mode.
  - Rationale: `Abrir Grafico` should be fast and should not load hidden trade data.

## Risks / Trade-offs

- Existing tests expect `Ver grafico` and the combined modal. Mitigation: update focused Monitor tests to assert `Abrir Grafico` is chart-only and `Ver Trades` shows summary/trades.
- Mobile action density can become crowded. Mitigation: use compact buttons with icons and full Portuguese labels where space allows, wrapping safely.
