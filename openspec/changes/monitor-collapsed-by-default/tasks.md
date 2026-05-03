## 1. Monitor UI

- [x] 1.1 Change Monitor detail row default from expanded to collapsed.
- [x] 1.2 Preserve row click and chevron expansion behavior.

## 2. Tests

- [x] 2.1 Update Monitor E2E tests to assert collapsed default.
- [x] 2.2 Update existing detail-card assertions to expand rows first.

## 3. Validation

- [x] 3.1 Run `openspec validate monitor-collapsed-by-default --type change`.
- [x] 3.2 Run frontend build.
- [x] 3.3 Run affected Monitor E2E test.

Note: use project skills when applicable: OpenSpec skills for this change, `crypto-frontend` for Monitor UI edits, and subagents for independent mapping/review when useful.
