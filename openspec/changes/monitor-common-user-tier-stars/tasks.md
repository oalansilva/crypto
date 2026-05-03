## 1. Backend Tier Scope

- [x] 1.1 Normalize non-admin Monitor opportunity tier filters to Tier 1, 2, and 3 only.
- [x] 1.2 Preserve admin tier filter behavior, including `all` and `none`.
- [x] 1.3 Add backend tests for common-user and admin tier behavior.

## 2. Monitor UI

- [x] 2.1 Add Monitor tier-to-star display mapping.
- [x] 2.2 Render Tier 1/2/3 star classification in Monitor row tags.
- [x] 2.3 Add/update E2E coverage for tier star rendering.

## 3. Validation

- [x] 3.1 Run `openspec validate monitor-common-user-tier-stars --type change`.
- [x] 3.2 Run targeted backend tests for opportunities.
- [x] 3.3 Run frontend build and affected Monitor E2E test.

Note: use project skills when applicable: OpenSpec skills for this change, `crypto-frontend` for Monitor UI edits, and subagents for independent mapping/review when useful.
