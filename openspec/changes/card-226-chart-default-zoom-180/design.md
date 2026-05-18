## Context

`StrategyChartSurface` now powers both Favorites and Monitor charts. Changing the initial range in this component applies the same default zoom everywhere without duplicating per-screen logic.

## Decisions

- Use a shared `DEFAULT_VISIBLE_BARS = 180`.
- On first render and reset, show the latest 180 candles when there are more than 180 candles.
- If there are 180 candles or fewer, keep `fitContent()` so the whole available history remains visible.
- Keep manual zoom and wheel zoom unchanged after the initial/default range is applied.
- Add a reusable `StrategyTradesTable` for the Favorites-style metrics and trade list.
- Replace the duplicated Favorites result trade table with `StrategyTradesTable`, keeping export behavior through the existing export handler.
- In Monitor, fetch `/favorites/{opportunity.id}/trades` when the graph modal opens; if the favorite trade payload is unavailable, fall back to closed trades derived from `signal_history`.
- Render the trade section below the chart inside the Monitor modal so the clean Monitor graph remains first, with the complete analysis details still available in the same flow.

## Risks / Trade-offs

- The visible bar counter may include small logical range rounding from `lightweight-charts`; tests should assert a bounded initial range rather than an exact string when necessary.
- Some Monitor opportunities may not map to a saved favorite ID; those cases fall back to signal history instead of blocking the modal.
