## Context

The app displays Portuguese labels, while several Playwright tests intentionally use ASCII accessible names to avoid accent-sensitive selector drift. The Supply Distribution menu item had a visible label that did not match the expected accessible selector.

## Goals / Non-Goals

**Goals:**

- Preserve the visible Portuguese label.
- Make the accessible name deterministic for E2E.
- Keep admin-only navigation behavior unchanged.

**Non-Goals:**

- Rename the route.
- Change menu layout.
- Expose the admin-only item to common users.

## Decisions

- Add an optional `accessibilityLabel` to nav item config and pass it to `aria-label`.
- Use `Distribuicao` only as accessible name; visible text stays `Distribuição`.

## Risks / Trade-offs

- Screen readers receive ASCII label for this item. This is acceptable for current QA stability and does not alter the visible UI.
