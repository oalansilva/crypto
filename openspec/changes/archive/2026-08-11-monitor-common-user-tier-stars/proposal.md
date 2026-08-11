## Why

Common users should see only curated Monitor strategies, not untiered/admin working rows. The tier value also needs to be understandable as a simple quality/ranking signal instead of internal labels.

## What Changes

- Restrict non-admin Monitor opportunities to strategies classified in Tier 1, 2, or 3.
- Keep admin behavior unchanged so admins can still inspect all tiers, including untiered rows.
- Display Tier as a star rating in Monitor:
  - Tier 1: 3 stars
  - Tier 2: 2 stars
  - Tier 3: 1 star

## Capabilities

### New Capabilities
- `monitor-tier-stars`: Monitor shows tier classification as user-facing star rating.

### Modified Capabilities
- `opportunity-monitor`: Common-user opportunity results are limited to Tier 1, 2, or 3.

## Impact

- Backend: opportunity route tier filter normalization for non-admin users.
- Frontend: Monitor row tags for tier star classification.
- Tests: backend route tests and affected Monitor E2E coverage.
