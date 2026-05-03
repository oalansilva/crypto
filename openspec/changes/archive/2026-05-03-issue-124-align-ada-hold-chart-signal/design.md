## Context

The backend currently derives Monitor `HOLD` mostly from moving-average trend state. The chart modal, however, proves entries using `signal_history`, entry/stop fields, and resolved signal context. When trend state says active but signal history has no open entry, the trader sees a `HOLD` row without an entry marker in the chart.

## Goals / Non-Goals

**Goals:**
- Use confirmed strategy signal history as the active-position gate for Monitor `HOLD`.
- Keep distance-to-entry behavior available when trend is bullish but no active entry exists.
- Avoid frontend contract churn; the existing `is_holding`, `status`, `next_status_label`, `entry_price`, and `signal_history` payload fields remain the API surface.
- Add focused tests for the bug class.

**Non-Goals:**
- Rebuild strategy signal generation.
- Add new chart drawing libraries or UI controls.
- Change release/commit flow.

## Decisions

- Backend is the source of truth for active `HOLD`. The API already calculates `last_buy_pos`, `last_sell_pos`, `signal_history`, and entry/stop prices, so resolving the contradiction there keeps cards, tables, and chart modal aligned.
- A confirmed active entry means the latest confirmed BUY exists and is newer than the latest confirmed SELL. Trend alone can keep entry distance near zero, but it must not create an active position by itself.
- Stop-loss exit remains terminal for `HOLD`; if a stop is breached or the last exit reason is `stop_loss`, the result stays stopped/waiting for re-entry.
- Frontend remains a consumer of corrected payload. Existing modal tests already prove signal history rendering; new backend coverage prevents the inconsistent payload from being emitted.
- The candles endpoint must not treat TimescaleDB as authoritative when the latest persisted candle is stale for the requested timeframe. Fresh persisted rows still avoid provider calls; stale persisted rows trigger CCXT refresh and are written back to storage.
- Opening a Monitor chart should prefer the opportunity strategy timeframe over the saved price timeframe preference. Saved preferences remain useful for manual chart exploration after the modal opens, but initial validation must use the same timeframe that produced the signal.

## Risks / Trade-offs

- Some strategies that were previously labeled `HOLD` from trend alone will move to `WAIT`. This is intended; it prevents active-position guidance without entry evidence.
- Strategies whose signal generator fails to emit entries will no longer show false `HOLD`. The mitigation is to fix those strategies separately if their entry generation is wrong.
- Existing fixture-only frontend tests may still create artificial `HOLD` payloads. They validate rendering only and do not override the backend contract.
- If CCXT fails while stale persisted candles exist, the endpoint can still return stale candles instead of failing the chart entirely. The UI context guard prevents stale candles from proving `HOLD`.

## Migration Plan

- Update the backend position-state helper and its call site.
- Add stale-persisted-candle detection to the market candles endpoint.
- Add unit tests for no-entry, active-entry, normal-exit, and stop-loss behavior.
- Run focused backend tests, OpenSpec validation, frontend build, and restart runtime for QA.

## Open Questions

- None for this card.
