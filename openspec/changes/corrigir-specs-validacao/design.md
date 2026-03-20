## Design: Corrigir Specs de Validação

### Overview
This is a maintenance/cleanup change. No new UI or UX design work is required.

### Changes

1. **OpenSpec Specs**: Add `## Purpose` sections and `#### Scenario:` blocks to 11 failing specs. No visual changes.

2. **Health Monitoring**: Simple shell script (`scripts/health_check.sh`) + OpenClaw cron running every 15 minutes. Telegram notification via existing OpenClaw delivery mechanism.

3. **Cron Jobs**: Fix or disable `crypto-news-daily` and `monitor diario`. Preferred approach: add retry backoff (exponential), max 3 retries.

4. **docs/coordination/**: Remove archived files. Keep only README.md and files from active/in-progress changes.

### Files to Change
- `openspec/specs/chart-visualization/spec.md`
- `openspec/specs/combo-optimizer/spec.md`
- `openspec/specs/combo-strategies/spec.md`
- `openspec/specs/database-strategy-config/spec.md`
- `openspec/specs/optimization/spec.md`
- `openspec/specs/optimization-engine/spec.md`
- `openspec/specs/performance/spec.md`
- `openspec/specs/performance-metrics/spec.md`
- `openspec/specs/strategy-comparison/spec.md`
- `openspec/specs/strategy-enablement/spec.md`
- `openspec/specs/ui-ux/spec.md`
- `scripts/health_check.sh` (new)
- `docs/coordination/` (cleanup)
