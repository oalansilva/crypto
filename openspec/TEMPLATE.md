---
spec: openspec.v1
id: <auto>
title: <short-title>
status: draft
owner: Alan
created_at: <auto>
updated_at: <auto>
---

# 0) One-liner

<One sentence describing the change>

# 1) Context

- Problem:
- Why now:
- Constraints:

# 2) Goal

## In scope
- 

## Out of scope
- 

# 3) User stories

- As a <user>, I want <thing>, so that <benefit>.

# 4) UX / UI

- Entry points:
- States:
  - Loading
  - Empty
  - Error
- Copy (PT-BR):

# 5) API / Contracts

## Backend endpoints

### <METHOD> <PATH>
- Request:
- Response (success):
- Response (error):

## Security
- Auth:
- Rate limits:

# 6) Data model changes

- DB:
- Migrations:

# 7) VALIDATE (mandatory)

## Proposal link

- Proposal URL (filled after viewer exists): <http://31.97.92.212:5173/openspec/<id>>
- Status: draft → validated → approved → implemented

Before implementation, complete this checklist:

- [ ] Scope is unambiguous (in-scope/out-of-scope are explicit)
- [ ] Acceptance criteria are testable (binary pass/fail)
- [ ] API/contracts are specified (request/response/error) when applicable
- [ ] UX states covered (loading/empty/error)
- [ ] Security considerations noted (auth/exposure) when applicable
- [ ] Test plan includes manual smoke + at least one automated check
- [ ] Open questions resolved or explicitly tracked

# 8) Acceptance criteria (Definition of Done)

- [ ] 

# 9) Test plan

## Automated
- 

## Manual smoke
1. 

# 9) Implementation plan

- Step 1:
- Step 2:

# 10) Rollout / rollback

- Rollout:
- Rollback:

# 11) USER TEST (mandatory)

After deployment/restart, Alan will validate in the UI.

- Test URL(s):
- What to test (smoke steps):
- Result:
  - [ ] Alan confirmed: OK

# 12) ARCHIVE / CLOSE (mandatory)

Only after Alan confirms OK:

- [ ] Update spec frontmatter `status: implemented`
- [ ] Update `updated_at`
- [ ] Add brief evidence (commit hash + URL tested) in the spec

# 13) Notes / open questions

- 
