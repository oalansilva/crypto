## 1. Backend: Theme Preference

- [ ] 1.1 Extend monitor preferences schema to include `theme` (default: `dark-green`)
- [ ] 1.2 Update preferences endpoints to read/write theme
- [ ] 1.3 Add SQLite migration/ensure-migration for the new column
- [ ] 1.4 Add backend integration tests for theme preference

## 2. Frontend: Dark-Green Monitor Theme

- [ ] 2.1 Apply dark-green palette to Monitor root container (scoped CSS vars or Tailwind)
- [ ] 2.2 Ensure key components (filter bar, cards, chart container, buttons) use the new palette
- [ ] 2.3 Verify readability/contrast on mobile

## 3. Tests (E2E)

- [ ] 3.1 Add/extend Playwright E2E smoke: Monitor loads with dark-green theme
- [ ] 3.2 Add E2E: theme persists after reload (via preferences)

## 4. Validation

- [ ] 4.1 Run `openspec validate monitor-dark-green-theme --type change`
