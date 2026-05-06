## Why

The Monitor currently exposes `WAIT` as a third visible decision state, which makes the product read like "buy, sell, or maybe" instead of a clear trading workflow. Alan confirmed that uncertain or inactive strategies should not become a user-facing intermediate status; the system must fix the signal handling and show only actionable buy/entry or sell/exit decisions in the main Monitor surface.

## What Changes

- Remove `WAIT` from the main Monitor UI sections, KPI counters, and common-user visible decision states.
- Keep non-actionable or uncertain strategy results out of the main visible opportunity list instead of presenting them as opportunities.
- Preserve internal defensive handling so uncertain, stale, mismatched, or unknown states do not become buy or sell signals.
- Update chart/detail behavior for actionable rows to continue supporting active hold and exit/entry decisions without exposing `WAIT` as business state.
- Add focused frontend coverage for filtering out `WAIT`/neutral results.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `monitor`: the main Monitor screen must show only actionable decision sections and exclude non-actionable `WAIT` results from common-user visible opportunities.
- `opportunity-monitor`: opportunity resolution may keep defensive internal states, but visible dashboard decisions must no longer treat `WAIT` as an actionable section.
- `monitor-active-entry-confirmation`: bullish trend without a confirmed active entry must remain non-actionable without being exposed as `WAIT`.

## Impact

- Frontend Monitor decision grouping and KPI rendering in `frontend/src/components/monitor/MonitorStatusTab.tsx`.
- Frontend signal resolution helpers in `frontend/src/components/monitor/signalResolution.ts`.
- Monitor card/chart behavior that consumes resolved signal visuals.
- Existing Monitor Playwright coverage and focused frontend tests.
