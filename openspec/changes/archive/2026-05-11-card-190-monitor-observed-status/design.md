## Context

The MVP daily Telegram job scans the admin-curated Monitor catalog and sends concise signals to the `Crypto` Telegram topic. The alert history table records sent/dry-run/failed attempts, but not every observed Monitor state.

## Goals / Non-Goals

**Goals:**

- Track the latest observed status per `symbol + timeframe` every scan.
- Preserve alert audit history separately from observed-state tracking.
- Alert on status change into sendable states such as Compra/Venda.
- Avoid repeat alerts when the observed status is unchanged.

**Non-Goals:**

- Full time-series history of every scan.
- Per-user status tracking.
- UI for observed status inspection.

## Decisions

1. Add `MonitorObservedStatus` with a unique key on `symbol + timeframe`.

   This keeps current-state lookup cheap and avoids overloading `monitor_telegram_alerts`, which remains send/audit history.

2. Update observed status after evaluating each opportunity.

   The previous observed status is read first for comparison; then the current scan result is persisted regardless of send outcome.

3. First sendable observation can alert.

   If no previous observed status exists and current status is sendable, the MVP should notify rather than wait another day.

4. Unchanged status suppresses alert before dedupe/rate limit.

   Dedupe still protects against repeats and manual retries, but observed-state comparison is the primary change detector.

## Risks / Trade-offs

- [Risk] Existing alert history does not backfill observed status. -> First scan after deployment establishes observed state; sendable first observations may alert once.
- [Risk] Failed sends still advance observed status. -> Keep this for noise control; failure is separately auditable in `monitor_telegram_alerts` and can be retried manually if needed.
