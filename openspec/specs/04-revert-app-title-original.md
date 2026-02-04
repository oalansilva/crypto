---
spec: openspec.v1
id: crypto.ui.title.revert-original
title: Revert app document title to original
status: draft
owner: Alan
created_at: 2026-02-04
updated_at: 2026-02-04
---

# 0) One-liner

Revert the web app document title back to the original value (`frontend`).

# 1) Context

We changed the Vite frontend HTML `<title>` to `teste123` to test the OpenSpec flow. Now we want to revert to the original title.

# 2) Goal

## In scope
- Update the default document `<title>` back to `frontend`.

## Out of scope
- Any other rebrand changes (icons, header text, nav labels).

# 3) VALIDATE (mandatory)

Before implementation, complete this checklist:

- [ ] Scope is unambiguous (in-scope/out-of-scope are explicit)
- [ ] Acceptance criteria are testable (binary pass/fail)
- [ ] API/contracts are specified (request/response/error) when applicable
- [ ] UX states covered (loading/empty/error)
- [ ] Security considerations noted (auth/exposure) when applicable
- [ ] Test plan includes manual smoke + at least one automated check
- [ ] Open questions resolved or explicitly tracked

# 4) Acceptance criteria (Definition of Done)

- [ ] Opening the frontend in a browser shows the tab title as `frontend`.
- [ ] `npm run build` succeeds.

# 5) Test plan

## Manual smoke
1. Open http://31.97.92.212:5173/
2. Confirm browser tab title is `frontend`.

## Automated
- `npm run build`

# 6) Implementation plan

1. Edit `crypto/frontend/index.html` and set `<title>frontend</title>`.
2. Run `npm run build`.
3. Commit with message `frontend: revert document title to frontend`.
