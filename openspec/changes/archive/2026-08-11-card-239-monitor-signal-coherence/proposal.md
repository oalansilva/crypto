## Why

The Monitor can show `Venda` on the chart while the summary/current state shows `Compra` for the same ADA/USDT daily moving-average strategy. This creates contradictory product guidance in a signal surface that must stay coherent and auditable.

## What Changes

- Investigate the Monitor state resolution path for ADA/USDT, `Medias Moveis: Tendencia Confirmada`, timeframe `1D`.
- Align the Monitor summary/current signal with the latest valid visible chart signal for the same favorite/strategy/timeframe.
- Preserve existing chart marker behavior from card #238 while preventing a stale or mismatched current-state fallback from overriding the visible signal.
- Add focused validation that compares chart marker direction, payload state and Monitor summary for the reported case or a deterministic fixture.
- Follow-up from Alan's 2026-05-21 retest: extend the same resolution to the Monitor list/section/card state, not only to the chart modal, and avoid adding a duplicate fallback `Venda` marker when the favorite-backed latest marker already resolves to `Venda`.
- Second follow-up from Alan's 2026-05-21 retest: move the parity rule into the backend opportunity payload when favorite cached trades already prove the latest action is `Venda`, and make restart/build flow prevent stale frontend bundles from being served after a fix.

## Capabilities

### New Capabilities
- `monitor-signal-coherence`: Covers agreement between Monitor current state, chart markers, payload/trade history and visible signal labels.

### Modified Capabilities
- `monitor`: Monitor current-state labels must resolve from the same operational signal source used by the chart for the selected strategy/favorite.
- `chart-visualization`: Chart marker direction must remain the source of truth for the visible current signal when Monitor opens a favorite-backed chart.

## Impact

- Affected Monitor frontend state/signal resolver and chart modal context.
- Possible affected backend/API payload interpretation if the inconsistency originates before the UI.
- Runtime restart/build scripts must not keep serving an old `frontend/dist` after code changes.
- No database migration expected.
- UI must keep the existing `DESIGN.md` dark operational surface and Portuguese signal language.
