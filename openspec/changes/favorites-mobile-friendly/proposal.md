## Why

The Favorites screen is currently hard to use on mobile (small tap targets, dense table-like layout, and horizontal scrolling). This slows down daily monitoring and quick edits when away from a desktop.

## What Changes

- Make the **/favorites** screen responsive and mobile-first.
- Replace the dense desktop layout with a **card/stack layout** on small screens.
- Ensure primary actions (edit/delete/tier/notes) are **touch-friendly** and accessible.
- Improve information hierarchy (HOLD vs non-HOLD, tier visibility) to reduce scrolling and mis-taps.
- Keep desktop behavior intact; changes are additive and responsive.

## Capabilities

### New Capabilities
- `favorites-mobile-ui`: Responsive and mobile-first UX for the Favorites screen (layout, actions, filters, and readability on small viewports).

### Modified Capabilities
- `frontend-ux`: Add requirements specific to responsive behavior for the Favorites route (mobile breakpoints, touch targets, and layout rules).

## Impact

- Frontend: `FavoritesDashboard` route (`/favorites`) and related components/styles.
- No backend API changes expected.
- QA: Must verify usability on common mobile widths (e.g., 360–430px) and that desktop layout remains unaffected.
