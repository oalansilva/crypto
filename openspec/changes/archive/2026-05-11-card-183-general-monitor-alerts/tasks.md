## 1. Opportunity Source

- [x] 1.1 Add an explicit catalog-level favorites/opportunities path in `OpportunityService`.
- [x] 1.2 Make the catalog path use admin-curated Monitor rows, independent from caller `user_id` and user liked preferences.

## 2. Alert Service

- [x] 2.1 Update Monitor Telegram scans to call the catalog-level opportunity path.
- [x] 2.2 Preserve existing tier filter, dedupe, rate limit, allowlist and dry-run behavior.

## 3. Validation

- [x] 3.1 Add/update backend tests proving group alerts use the general catalog even when user preferences do not mark a strategy as liked.
- [x] 3.2 Run focused tests and OpenSpec validation for this change.

Note: Use project skills when applicable for OpenSpec, tests and debugging.
