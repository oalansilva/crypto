## Why

Card #105 asks to standardize the whole system layout using `DESIGN.md`. The current app still mixes the dark crypto shell with several screen-level styles, so the product reads as multiple visual systems instead of one operational workspace.

## What Changes

- Rebase the global frontend design tokens on the Binance-inspired near-black canvas, yellow primary CTA, flat card surfaces, compact radii, and trading green/red semantics from `DESIGN.md`.
- Update the app shell and navigation so every authenticated page inherits the same visual frame.
- Normalize shared cards, muted panels, forms, tables, buttons, and page wrappers to the new system-level tokens.
- Preserve the product's operational crypto workflow density; the Binance-inspired system is adapted to this trading tool, not copied as a marketing page.
- Preserve route behavior, auth behavior, admin-only menu visibility, and existing API contracts.

## Capabilities

### New Capabilities

### Modified Capabilities
- `frontend-ux`: System-level layout, visual tokens, navigation, and shared UI surfaces follow `DESIGN.md` consistently across the React app.

## Impact

- Affected frontend shell: `frontend/src/components/Layout.tsx`, `frontend/src/components/AppNav.tsx`, shared UI components, and global CSS.
- Affected validation: frontend build, relevant navigation/layout E2E checks, and visual smoke validation.
- No backend API, database, or auth contract change expected.
