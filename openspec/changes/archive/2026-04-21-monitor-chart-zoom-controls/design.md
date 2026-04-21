## Context

The Monitor flow already exposes an expanded strategy chart through `frontend/src/components/monitor/ChartModal.tsx`. That chart is built with `lightweight-charts`, already supports scroll/scale gestures, and synchronizes a main price panel with an RSI panel. The gap is discoverability: traders who expect a TradingView-style experience do not see direct zoom buttons, so zoom depends on mouse wheel, trackpad, or touch gestures that are not obvious or consistently available.

This change stays inside the existing Monitor chart experience. It does not introduce a new chart library, new API endpoints, or a broader redesign of the Monitor cards.

## Goals / Non-Goals

**Goals:**
- Add explicit zoom-in and zoom-out controls to the expanded strategy chart opened from `/monitor`.
- Make zoom behavior predictable by adjusting the visible logical range in fixed steps instead of refetching candles.
- Preserve existing chart state: selected timeframe, loaded candles, indicator toggles, synchronized RSI panel, and crosshair behavior.
- Keep the change frontend-only and local to the current Monitor chart implementation.

**Non-Goals:**
- Rebuilding the Monitor inline mini-chart into a full TradingView clone.
- Adding pan shortcuts, drawing tools, annotations, or saved chart preferences.
- Changing backend candle endpoints, candle limits, or historical data contracts.
- Replacing `lightweight-charts` or redesigning the modal layout.

## Decisions

1) Keep the implementation in `ChartModal`
- Decision: add explicit zoom controls to `frontend/src/components/monitor/ChartModal.tsx` rather than creating a new shared chart container.
- Rationale: the user request is specifically about visualizing a strategy chart in Monitor, and `ChartModal` already owns the richer chart surface with timeframe controls, indicators, markers, and synchronized panels.
- Alternative considered: add the same controls to `MiniCandlesChart`.
  Rejected because the mini chart is a lightweight preview inside cards and would expand scope without being necessary for this request.

2) Zoom by mutating visible logical range instead of refetching candles
- Decision: use the `timeScale()` API from `lightweight-charts` to read the current visible logical range and apply a narrower or wider range around the current center.
- Rationale: zoom is a viewport concern, not a data-loading concern. This keeps the interaction instant and avoids unnecessary network traffic.
- Alternative considered: change candle `limit` and refetch on each zoom step.
  Rejected because it increases latency, complicates caching, and makes zoom feel less like a direct chart interaction.

3) Keep synchronized panels locked together
- Decision: route zoom actions through the same synchronization path already used between the main chart and the RSI chart, so both panels keep the same visible time window.
- Rationale: a zoom action that drifts the panels apart would break the usefulness of indicators and make the chart feel unreliable.
- Alternative considered: only zoom the main chart and let the RSI panel follow indirectly.
  Rejected because the current implementation already treats both panels as a synchronized pair.

4) Use compact toolbar buttons instead of a floating overlay
- Decision: place zoom controls in the existing chart toolbar near the timeframe and indicator controls.
- Rationale: the controls remain visible, discoverable, and consistent with the current Monitor modal interaction model.
- Alternative considered: add floating `+` and `-` controls inside the chart canvas.
  Rejected because overlays can interfere with pointer inspection and reduce clarity on smaller viewports.

## Risks / Trade-offs

- [Risk] Zoom step size may feel too aggressive or too weak on different candle counts → Mitigation: use a fixed proportional step based on the current visible range and verify on short and long windows.
- [Risk] Very small visible ranges can make repeated zoom-in unstable → Mitigation: clamp the minimum window size so the chart never collapses to an unusable range.
- [Risk] Explicit controls duplicate gesture-based scaling and add slight UI density → Mitigation: keep controls visually compact and scoped to the expanded modal only.
- [Risk] Panel synchronization bugs could appear if zoom is applied inconsistently → Mitigation: centralize zoom range updates and validate price panel plus RSI panel together.

## Migration Plan

1. Add zoom control requirements and task breakdown in OpenSpec.
2. Implement zoom controls in `ChartModal` only.
3. Validate that zoom changes visible range without refetching candles and without breaking timeframe switching.
4. Run relevant frontend checks and QA validation for `/monitor`.

Rollback is straightforward: remove the toolbar controls and the helper used to update visible logical range. No backend or persistence rollback is required.

## Open Questions

- Should the modal also expose a `Reset zoom` or `Fit content` action, or is explicit zoom-in/zoom-out sufficient for the first iteration?
- Should the zoom controls be icon-only (`+` / `-`) or use labeled buttons for stronger discoverability?
