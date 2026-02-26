# monitor-asset-type-filter

## Status
- PO: done
- DEV: done
- QA: done
- Alan (Stakeholder): approved

> Gate order: PO must be **done** before Alan approves to implement.

## Decisions (locked)
- Goal: Add an Asset Type filter (All/Crypto/Stocks) to /monitor to reduce noise.
- Surface (mobile/desktop): Monitor only.
- Defaults: Default filter = All.
- Persistence: No persistence required.
- Data sources: Heuristic by symbol shape (crypto contains '/', stocks do not).
- Performance limits: Frontend-only filtering, no API changes.
- Non-goals: Persisting filter selection in backend.

## Links
- OpenSpec viewer: http://72.60.150.140:5173/openspec/changes/monitor-asset-type-filter/proposal
- PT-BR review (viewer): http://72.60.150.140:5173/openspec/changes/monitor-asset-type-filter/review-ptbr
- PR: (none)
- CI run: (none)

## Next actions
- [x] PO: Create OpenSpec artifacts and validation.
- [x] DEV: Implement Asset Type filter UI + filtering logic.
- [x] QA: Add Playwright E2E coverage (mocked API) and ensure CI green.
- [x] Alan: Approved implementation.
