## Why

The crypto project has accumulated technical debt in documentation and monitoring: (1) 14 OpenSpec specs have validation errors, (2) no health monitoring means system downtime goes unnoticed, (3) daily cron jobs have 4 consecutive errors, and (4) legacy docs/coordination/ files clutter the repo. Resolving these improves project hygiene and operational visibility.

## What Changes

- **Fix OpenSpec spec validation errors**: Fix or suppress validation errors in 14 specs: `chart-visualization`, `combo-optimizer`, `combo-strategies`, `database-strategy-config`, `design`, `external-balances`, `favorites`, `optimization`, `optimization-engine`, `performance`, `performance-metrics`, `strategy-comparison`, `strategy-enablement`, `ui-ux`. Run `openspec validate --specs` and add missing SHALL/MUST keywords and scenarios.
- **Add health monitoring**: Create a health check cron that verifies backend (GET http://127.0.0.1:8003/api/health) and frontend (http://127.0.0.1:5173) return 200, and notifies Alan via Telegram on failure.
- **Fix or disable failing cron jobs**: `crypto-news-daily` and `monitor diario` have 4 consecutive errors (likely rate limits). Fix with backoff or disable and create a manual trigger option.
- **Clean up legacy coordination docs**: Review `docs/coordination/` and remove archived/completed change files. Keep only README and active coordination files.

## Capabilities

### New Capabilities
- `health-monitoring`: Health check cron that monitors backend and frontend availability and notifies Alan via Telegram on failure.

### Modified Capabilities
<!-- No spec-level requirement changes — maintenance only -->

## Impact

- OpenSpec: Clean validation with 0 errors
- Ops: Visibility into system health with Telegram alerts
- Cron: Reliable operation without consecutive errors
- Docs: Cleaned-up coordination directory
