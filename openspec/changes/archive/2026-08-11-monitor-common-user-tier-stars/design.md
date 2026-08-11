## Context

Monitor currently calls `/api/opportunities/?tier=all`, and `all` includes untiered rows. This is useful for admin review, but too broad for common users. Existing favorites already use `tier` values `1`, `2`, `3`, or `null`.

## Decisions

1. Enforce common-user tier scope in the backend.

   `get_opportunities` already determines admin visibility through `can_view_strategy_secrets`. Reuse that role check. If the requester is not allowed to view strategy secrets, normalize the requested tier filter to the intersection of `1,2,3`. For `all` or omitted tier, use `1,2,3`.

2. Keep admin tier behavior unchanged.

   Admins can still request `all`, `none`, or specific tier filters for operational review.

3. Render tier as stars in the Monitor table.

   Tier star mapping is display-only:
   - `1` -> `★★★`
   - `2` -> `★★`
   - `3` -> `★`
   - missing/invalid -> no star label

## Risks

- Existing common users may have liked untiered opportunities. Mitigation: the favorite preference stays stored, but the row no longer appears until it receives Tier 1, 2, or 3.
- Frontend-only filtering would still expose untiered rows through API. Mitigation: backend enforces the scope.

## Validation

- Backend tests prove common `tier=all` is normalized to `1,2,3` and admin `tier=all` remains unchanged.
- E2E proves tier stars render in Monitor.
- OpenSpec validation, frontend build, affected Monitor E2E.
