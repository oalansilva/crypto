## Context

The current Favorites screen (`/favorites`) is implemented as a desktop-first layout and becomes difficult to operate on small viewports. Users experience dense information, small tap targets, and (in practice) horizontal scrolling / awkward interactions.

Constraints:
- Frontend is a Vite/React app (see `frontend/src/App.tsx` route `/favorites`).
- Backend APIs should remain unchanged for this UX-only change.
- The desktop experience should not regress.

## Goals / Non-Goals

**Goals:**
- Provide a mobile-first, responsive Favorites UI (360–430px widths) that avoids horizontal scrolling.
- Ensure key actions are touch-friendly and safe (confirmation for destructive actions).
- Preserve desktop behavior and density for larger viewports.

**Non-Goals:**
- Changing backend API shapes or adding new backend endpoints.
- Redesigning unrelated pages.
- Altering strategy logic or opportunity calculations.

## Decisions

1) Responsive layout strategy
- Decision: Implement a breakpoint-based layout in the Favorites page:
  - Mobile: card/stack layout with a summary + collapsible details.
  - Desktop: keep the existing layout.
- Rationale: Minimizes risk and scope; avoids impacting desktop while solving mobile usability.

2) Action placement
- Decision: On mobile, render a compact action row (e.g., overflow menu or clearly labeled buttons) with 44x44px targets.
- Rationale: Prevent mis-taps and improve reachability.

3) Progressive disclosure
- Decision: Keep critical fields always visible; move secondary fields into collapsible sections.
- Rationale: Reduces vertical scrolling while preserving access to all data.

4) Styling approach
- Decision: Prefer utility CSS / existing component patterns already used in the codebase; avoid introducing new styling dependencies.
- Rationale: Keeps the change lightweight and consistent.

## Risks / Trade-offs

- [Risk] Desktop regressions due to shared components/styles → Mitigation: isolate mobile styles with breakpoint guards; test desktop visually.
- [Risk] Long text overflow on mobile (template names/notes) → Mitigation: wrap/truncate with ellipsis and provide expand affordance.
- [Risk] Increased render complexity in FavoritesDashboard → Mitigation: extract MobileFavoriteCard component and keep logic shared.
