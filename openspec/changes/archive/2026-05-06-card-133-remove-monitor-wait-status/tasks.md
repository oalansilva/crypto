## 1. Monitor Decision Surface

- [x] 1.1 Remove `WAIT` from the visible Monitor board sections and KPI counters.
- [x] 1.2 Filter non-actionable resolved opportunities out of the main visible list without promoting them to `HOLD` or `EXIT`.
- [x] 1.3 Keep actionable `HOLD` and `EXIT` rows visible with existing sort/filter behavior.

## 2. Frontend Coverage

- [x] 2.1 Add or update focused Monitor tests proving `WAIT`/neutral rows are not rendered as visible opportunities.
- [x] 2.2 Ensure existing `HOLD` and `EXIT` coverage still matches the new visible-section contract.

## 3. Validation

- [x] 3.1 Run OpenSpec validation for `card-133-remove-monitor-wait-status`.
- [x] 3.2 Run focused frontend build/test validation for affected Monitor behavior.
- [x] 3.3 Register implementation evidence before moving card #133 to `Done`.

Note: use project skills when applicable: OpenSpec skills for this change and `crypto-frontend` for Monitor UI edits and validation.
