## Context

Card #131 reports ADA/USDT shown as `WAIT` while charts show a clear active entry and daily candles stop at `2026-05-03`. Current behavior has two separate causes:

- `/api/market/candles` treats persisted `1d` candles as fresh for up to three days, so a daily crypto chart can stay behind the live provider.
- The Monitor list resolves sections with the card price timeframe preference, so a strategy with timeframe `1d` can be downgraded to `WAIT` when the card preference is `4h` or another display timeframe.

## Goals / Non-Goals

**Goals:**

- Make chart candle freshness bucket-aware for crypto timeframes.
- Keep Monitor list section resolution tied to the backend strategy decision state.
- Preserve chart-modal timeframe mismatch warnings when the trader manually views a different timeframe.
- Cover the ADA-like regression with focused backend and frontend tests.

**Non-Goals:**

- Redesign the Monitor UI.
- Change strategy entry/exit rules.
- Change Timescale ingestion cadence or add a migration.

## Decisions

- Use a timeframe bucket freshness check for persisted chart candles. A persisted row is fresh only when its timestamp reaches the current expected candle bucket for that timeframe, instead of relying only on broad age thresholds.
- Keep fallback behavior: if live provider fetch fails, stale persisted candles can still be returned as `timescaledb-stale` rather than breaking the chart.
- Resolve Monitor list grouping without `selectedTimeframe`, so list state follows `status` + `is_holding` from the opportunity payload. The chart modal continues to pass actual chart context to `resolveOpportunitySignal`.

## Risks / Trade-offs

- More frequent live fetches for current crypto candles -> mitigated by existing short-lived endpoint cache and provider cache.
- Provider outage can still show stale candles -> mitigated by existing `timescaledb-stale` source, making stale fallback explicit.
- List and chart may differ after a manual chart timeframe switch -> intentional; mismatch review belongs to chart context, not list grouping.
