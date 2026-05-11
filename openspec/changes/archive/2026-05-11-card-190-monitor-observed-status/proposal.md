## Why

Monitor Telegram alerts currently compare against the last alert that was sent or dry-run. That misses the full status history when a status was observed but did not generate an alert, making change detection less auditable.

## What Changes

- Persist the latest observed Monitor status for each `symbol + timeframe` during every Telegram scan.
- Use the observed previous status as the alert candidate `previous_status`.
- Suppress alerts when the current status is unchanged from the last observed status.
- Update observed status even when the current status is not sendable or no Telegram message is emitted.

## Capabilities

### New Capabilities

### Modified Capabilities
- `opportunity-monitor`: Monitor alert scans track the latest observed status per symbol/timeframe and alert only on relevant status changes.

## Impact

- Backend model/database startup migration for `monitor_observed_statuses`.
- Monitor Telegram alert service status comparison and audit behavior.
- Unit tests for first observation, unchanged status suppression, silent-to-sendable transitions, and observed-status updates.
