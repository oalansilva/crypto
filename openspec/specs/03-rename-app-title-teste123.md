---
spec: openspec.v1
id: crypto.ui.title.teste123
title: Rename app title to teste123
status: draft
owner: Alan
created_at: 2026-02-04
updated_at: 2026-02-04
---

# 0) One-liner

Change the web app document title to `teste123`.

# 1) Context

The Vite frontend currently sets the HTML document title via `frontend/index.html` (and possibly route-level overrides). We want a simple rename for quick OpenSpec testing.

# 2) Goal

## In scope
- Update the default document `<title>` to `teste123`.

## Out of scope
- Changing navbar/header titles inside the UI (unless they depend on document title).
- Rebranding icons/assets.

# 3) Acceptance criteria (Definition of Done)

- [ ] Opening the frontend in a browser shows the tab title as `teste123`.
- [ ] `npm run build` succeeds.

# 4) Test plan

## Manual smoke
1. Open http://31.97.92.212:5173/
2. Confirm browser tab title is `teste123`.

## Automated
- `npm run build`

# 5) Implementation plan

1. Edit `crypto/frontend/index.html` and set `<title>teste123</title>`.
2. Build the frontend.
3. Commit with message `frontend: rename document title to teste123`.

# 6) Notes

If any routes override the title at runtime, we may need to adjust the relevant React code as well.
