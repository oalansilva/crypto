## 1. Backend: Database + API

- [ ] 1.1 Add a new DB table to persist monitor preferences per symbol (`monitor_preferences`)
- [ ] 1.2 Implement `GET /api/monitor/preferences` to return preferences keyed by symbol
- [ ] 1.3 Implement `PUT /api/monitor/preferences/{symbol}` to update `in_portfolio` and/or `card_mode`
- [ ] 1.4 Add backend integration tests for reading/updating preferences (deterministic; no network)

## 2. Frontend: Preferences Integration

- [ ] 2.1 Fetch monitor preferences on Monitor load and merge with favorites-derived symbols
- [ ] 2.2 Default Monitor list filter to show only `in_portfolio=true` symbols
- [ ] 2.3 Add a filter control to switch between In Portfolio and All

## 3. Frontend: Per-card Mode Toggle

- [ ] 3.1 Add per-card toggle icon to switch between Price and Strategy views
- [ ] 3.2 Persist card mode changes via the backend preferences API
- [ ] 3.3 Render Price view using existing candle UI; render Strategy view using existing strategy/status content

## 4. E2E Tests (Playwright)

- [ ] 4.1 Add Playwright E2E test: defaults to In Portfolio list
- [ ] 4.2 Add Playwright E2E test: toggle In Portfolio flag persists across reload
- [ ] 4.3 Add Playwright E2E test: per-card mode toggling persists across reload

## 5. Validation

- [ ] 5.1 Run `openspec validate monitor-card-mode-and-portfolio --type change`

> Note: Use project skills (.codex/skills) when applicable (architecture, tests, debugging, frontend).
