## Context

The backup branch contains valid fixes mixed with generated Playwright evidence under `output/playwright`. The release workflow correctly preserved the state, but the repo lacked an ignore rule for that output path and the WIP was not isolated before release work started.

## Goals / Non-Goals

**Goals:**
- Integrate the useful WIP into the normal `develop -> main` path.
- Keep auth/session recovery, safe favorite detail access, and Monitor chart behavior coherent with current code.
- Block generated `output/` artifacts from becoming unclassified release work.
- Leave evidence explaining why the backup existed and what was integrated.

**Non-Goals:**
- Preserve debug screenshots or Playwright JSON artifacts in `main`.
- Rewrite the release process or introduce a new dependency.
- Change production database schema.

## Decisions

- Reapply useful changes selectively instead of cherry-picking the backup commit wholesale. This avoids conflicts and prevents generated artifacts from entering the release.
- Centralize token refresh in the authenticated fetch/store path. This keeps UI callers simple and preserves logout behavior when refresh fails.
- Treat admin-catalog favorite access as read-safe fallback behavior only. Private user favorites remain owner-scoped.
- Ignore `/output/` at repo root. This path is operational evidence, not versioned product source.

## Risks / Trade-offs

- Timeframe behavior from the backup narrows Monitor chart options to the operational `1d` path. Mitigation: cover this with the existing Monitor timeframe E2E test and document it in the spec.
- Auth refresh can mask expired access tokens. Mitigation: only retry once and only when a refresh token exists.
- Favorite fallback can expose more catalog data than before. Mitigation: allow only admin-catalog/public favorite details, not another user's private favorite.
