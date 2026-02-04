---
spec: openspec.v1
id: crypto.openspec.viewer.simple
title: Simple OpenSpec viewer inside the app (no auth)
status: draft
owner: Alan
created_at: 2026-02-04
updated_at: 2026-02-04
---

# 0) One-liner

Add a minimal in-app OpenSpec viewer so Alan can open a link and read specs without pasting content into chat.

# 1) Context

We are using OpenSpec (SDD) and want to reduce token usage by avoiding copying full spec markdown into chat. Specs live in the repo under `crypto/openspec/specs/*.md`.

# 2) Goal

## In scope
- Add a simple page in the frontend at `/openspec` that lists available spec files.
- Clicking a spec opens a detail view that renders the markdown.
- No authentication required.

## Out of scope
- Editing specs from the UI.
- Search, tags, or advanced navigation.
- Exposing non-spec files.

# 3) UX / UI

- Route: `/openspec`
  - Shows a list of specs (filename + title parsed from frontmatter if present).
- Route: `/openspec/:id`
  - Renders markdown content.
- Basic states:
  - Loading
  - Empty (no specs)
  - Error

# 4) API / Contracts

## Backend

### GET /api/openspec/specs
Return list of spec files.

Response:
```json
{
  "items": [
    {
      "id": "04-revert-app-title-original",
      "path": "openspec/specs/04-revert-app-title-original.md",
      "title": "Revert app document title to original",
      "status": "draft",
      "updated_at": "2026-02-04"
    }
  ]
}
```

### GET /api/openspec/specs/:id
Return raw markdown of the spec.

Response:
```json
{ "id": "04-revert-app-title-original", "markdown": "..." }
```

## Security
- Single-tenant, no auth (explicitly accepted by user).
- Limit file access to `crypto/openspec/specs/` only.

# 5) VALIDATE (mandatory)

- [ ] Scope is unambiguous (in-scope/out-of-scope are explicit)
- [ ] Acceptance criteria are testable (binary pass/fail)
- [ ] API/contracts are specified (request/response/error) when applicable
- [ ] UX states covered (loading/empty/error)
- [ ] Security considerations noted (auth/exposure) when applicable
- [ ] Test plan includes manual smoke + at least one automated check
- [ ] Open questions resolved or explicitly tracked

# 6) Acceptance criteria (Definition of Done)

- [ ] Visiting `http://31.97.92.212:5173/openspec` shows a list of specs.
- [ ] Clicking a spec opens a URL like `/openspec/04-revert-app-title-original` and shows the markdown.
- [ ] Only files under `openspec/specs/` are accessible (no path traversal).
- [ ] Frontend build succeeds.

# 7) Test plan

## Manual smoke
1. Open `/openspec` and verify list loads.
2. Open a spec detail page and verify markdown renders.
3. Try invalid id → shows error.

## Automated
- Backend: small unit test for id/path validation (optional if no test harness).
- Frontend: `npm run build`.

# 8) Implementation plan

Backend:
1. Add routes:
   - `GET /api/openspec/specs`
   - `GET /api/openspec/specs/{id}`
2. Implement safe spec directory allowlist + id validation (no `../`).

Frontend:
1. Add pages + routes.
2. Use a minimal markdown renderer (or simple `<pre>` if we want zero deps).

# 9) Notes / open questions

- Do we want markdown rendering or plain text? (Default: markdown rendering if we already have a renderer; otherwise plain `<pre>` is acceptable.)
