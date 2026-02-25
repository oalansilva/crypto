## 1. Backend: Preferences Schema + API

- [ ] 1.1 Add `price_timeframe` field to `monitor_preferences` table (default 1d)
- [ ] 1.2 Extend `GET /api/monitor/preferences` to include `price_timeframe`
- [ ] 1.3 Extend `PUT /api/monitor/preferences/{symbol}` to validate and persist `price_timeframe`
- [ ] 1.4 Add/update backend integration tests for `price_timeframe` persistence and validation

## 2. Frontend: Unify Monitor View

- [ ] 2.1 Remove Status/Dashboard tabs from Monitor (single cards view)
- [ ] 2.2 Ensure existing In Portfolio vs All filter remains
- [ ] 2.3 Ensure per-card Price vs Strategy toggle remains

## 3. Frontend: Per-card Timeframe Selector

- [ ] 3.1 Add per-card timeframe UI in Price mode
- [ ] 3.2 Persist timeframe changes via preferences API
- [ ] 3.3 Enforce timeframe constraints (stocks only 1d) in UI

## 4. E2E Tests (Playwright)

- [ ] 4.1 Update E2E to not depend on Monitor tabs
- [ ] 4.2 Add E2E: timeframe selection persists across reload

## 5. Validation

- [ ] 5.1 Run `openspec validate monitor-unified-cards-timeframe-prefs --type change`

> Note: Use project skills (.codex/skills) when applicable (architecture, tests, debugging, frontend).
