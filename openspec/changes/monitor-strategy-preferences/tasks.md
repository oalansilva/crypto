## 1. Backend Contract

- [x] 1.1 Add safe public strategy display-name formatting to non-admin opportunity redaction.
- [x] 1.2 Add user-level Monitor strategy preference model and API endpoints.
- [x] 1.3 Add backend tests for public display-name redaction and user-scoped liked preferences.

## 2. Monitor UI

- [x] 2.1 Load Monitor strategy preferences from the backend and keep legacy localStorage as a fallback.
- [x] 2.2 Persist star toggles through the Monitor API with optimistic UI handling.
- [x] 2.3 Keep strategy labels visible in Monitor rows/cards for common users without exposing protected details.

## 3. Validation

- [x] 3.1 Run `openspec validate monitor-strategy-preferences --type change`.
- [x] 3.2 Run targeted backend tests for opportunity redaction and Monitor preferences.
- [x] 3.3 Run frontend build and affected Monitor E2E test.

Note: use project skills when applicable: OpenSpec skills for this change, `crypto-frontend` for Monitor UI edits, and subagents for independent mapping/review when useful.
