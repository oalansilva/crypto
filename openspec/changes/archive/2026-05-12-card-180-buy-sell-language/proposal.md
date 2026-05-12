## Why

Alan identified that the user-facing labels `HOLD` and `EXIT` can confuse beta users and diverge from the landing v3 language. The Monitor should use the same plain-language decision labels as marketing and onboarding: `Compra` and `Venda`.

## What Changes

- Replace user-visible Monitor decision labels for active position and exit decision from `HOLD`/`EXIT` to `Compra`/`Venda`.
- Keep internal backend status names, API payload fields, and technical resolver logic unchanged where they are implementation details.
- Update Monitor card/list/chart copy, signal history labels, related E2E expectations, and product docs that describe user-facing Monitor signals.
- Preserve the existing no-financial-advice posture: the UI labels indicate product signal state, not guaranteed profit or personalized recommendation.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `monitor`: Monitor must present visible decision labels as `Compra` and `Venda` instead of `HOLD` and `EXIT`.
- `opportunity-monitor`: Opportunity Monitor visible rows, cards, and chart modal must align signal labels with Compra/Venda language while preserving internal technical state.

## Impact

- Frontend Monitor components: `MonitorStatusTab`, `OpportunityCard`, `ChartModal`, signal resolution helper.
- Frontend E2E tests covering Monitor visible state labels and chart labels.
- Docs that describe public Monitor signal language.
- No API, database, or dependency changes expected.
