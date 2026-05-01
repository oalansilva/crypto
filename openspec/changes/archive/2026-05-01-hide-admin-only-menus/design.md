## Context

The issue requests hiding several menus from common users while leaving them available to admins. The safest implementation is to use the role/admin state already present in the frontend instead of adding another permission system.

## Goals / Non-Goals

**Goals:**
- Gate the requested navigation entries by admin role.
- Keep admin navigation unchanged.
- Avoid changing backend authorization or route behavior in this card.

**Non-Goals:**
- Do not remove the routes or page components.
- Do not redesign the navigation shell.
- Do not introduce a new permission model.

## Decisions

- Reuse existing authenticated user role/admin flags. This keeps the menu rule aligned with current access control semantics and avoids duplicated role sources.
- Apply the restriction at navigation item definition/render time. This keeps the page components untouched and limits the blast radius to menu visibility.
- Treat this as UI visibility, not security enforcement. Direct route protection remains a separate concern unless existing guards already cover it.

## Risks / Trade-offs

- Non-admin users may still access a direct URL if route guards do not block it. Mitigation: keep this card scoped to menu visibility and document that route authorization is not changed.
- If role state loads asynchronously, menus could flicker. Mitigation: default admin-only items to hidden unless admin status is positively known.
