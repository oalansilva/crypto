## Why

The crypto project has accumulated technical debt in OpenSpec documentation. 11 specs have validation errors and cannot pass `openspec validate --specs`. Additionally, no health monitoring exists for the production services, and two cron jobs (crypto-news-daily, monitor diario) have been failing with rate limit errors.

## What Changes

### Fix OpenSpec spec validation errors
Run `openspec validate --specs` and fix all failing specs. The 11 specs missing Purpose sections and Scenarios are:
- chart-visualization
- combo-optimizer
- combo-strategies
- database-strategy-config
- optimization
- optimization-engine
- performance
- performance-metrics
- strategy-comparison
- strategy-enablement
- ui-ux

For each: add `## Purpose` section and ensure every requirement has at least one `#### Scenario:` block with WHEN/THEN format.

### Add health monitoring cron
Create a health check that:
- Verifies `http://127.0.0.1:8003/api/health` returns 200
- Verifies `http://127.0.0.1:5173` returns 200
- Sends Telegram notification to Alan on failure

Schedule: every 15 minutes. Use OpenClaw cron.

### Fix or disable failing cron jobs
- crypto-news-daily and monitor diario have 4 consecutive rate limit errors
- Add retry backoff OR disable both (document reason)
- Create manual trigger option for both

### Clean up docs/coordination
- Review and remove archived/completed change coordination files
- Keep only README and active coordination files

## Capabilities
No new capabilities. Maintenance only.

## Impact
- OpenSpec: clean validation
- Ops: system health visibility
- Cron: reliable operation

## Acceptance Criteria
- `openspec validate --specs` shows 0 errors (or documented known issues)
- Health cron pings Alan when backend/frontend is down
- Crons run without consecutive errors
- docs/coordination/ contains only README + active files
