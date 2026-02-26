## Context

Monitor uses a dark palette and is heavily used on mobile. Alan requested an aesthetic refresh: replace the primary black background with a dark-green palette, while preserving readability and not impacting performance.

The theme must be persisted in the backend so it follows the user across devices.

## Goals / Non-Goals

**Goals:**
- Apply a dark-green palette to `/monitor` (cards, filter bar, chart container, buttons).
- Keep contrast/readability acceptable on mobile.
- Persist theme preference in the backend.
- Default theme is dark-green.

**Non-Goals:**
- Full site-wide theming.
- Complex theming system with multiple themes.

## Decisions

1) Scope: Monitor only
- Decision: apply theme styles only to `/monitor`.

2) Storage: backend preference
- Decision: store `theme` in the existing `monitor_preferences` record per symbol/user context.
- Note: since there is no user auth model, we treat this as a single global preference.

3) Implementation approach
- Decision: use Tailwind classes and a small set of CSS variables scoped to the Monitor root container.
- Rationale: reduces churn and keeps components consistent.

## Risks

- [Risk] Reduced contrast in some cards/components → Mitigation: test on mobile; adjust text/outline colors.
- [Risk] Preference schema changes require migration → Mitigation: add SQLite migration + tests.
