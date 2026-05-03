## 1. Backend Source Selection

- [x] 1.1 Add curated fallback favorite selection to `OpportunityService` for users with no matching favorites.
- [x] 1.2 Keep own favorites authoritative and avoid mixing fallback rows when user rows exist.
- [x] 1.3 Keep fallback compatible with tier filters and crypto-only opportunity processing.

## 2. Validation Coverage

- [x] 2.1 Add tests proving a no-favorites common user receives fallback opportunities.
- [x] 2.2 Add tests proving user-owned favorites take precedence over fallback favorites.
- [x] 2.3 Add tests or assertions proving non-admin fallback payloads remain redacted.

## 3. Evidence

- [x] 3.1 Run `openspec validate issue-108-monitor-user-data --type change`.
- [x] 3.2 Run targeted backend tests for opportunities/fallback behavior.
- [x] 3.3 Run proportional frontend/build validation if Monitor UI code changes. No frontend code changed.
- [x] 3.4 Run `./restart` after successful validation.

Note: use project skills when applicable: OpenSpec skills for this change, `crypto-frontend` for any Monitor UI edits, and subagents for independent mapping/review.
