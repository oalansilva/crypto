## Why

An affected common user opens Monitor with no visible data because the Monitor currently depends on per-user favorite strategies, and that user has no Monitor-ready favorites. Since strategy tooling and Favorites are admin-only for common users, Monitor needs a safe curated fallback instead of rendering an empty operational screen.

## What Changes

- Add a backend fallback for `/api/opportunities/`: when an authenticated user has no favorite strategies, compute Monitor opportunities from an admin-curated favorite set.
- Keep user-owned favorites as the primary source when they exist.
- Keep non-admin strategy redaction active for fallback opportunities.
- Add tests for the no-favorites common-user path and the own-favorites precedence path.
- Adjust Monitor empty-state/filter behavior only if needed by the backend fallback.

## Capabilities

### New Capabilities

- `monitor-curated-fallback`: Common users without own favorites can still receive safe curated Monitor data.

### Modified Capabilities

- `opportunity-monitor`: Monitor opportunity source falls back to curated favorites when a user has no own favorite strategies.

## Impact

- Backend: `backend/app/services/opportunity_service.py`, `backend/app/routes/opportunity_routes.py` if needed.
- Security: non-admin fallback payloads must remain redacted by existing strategy-secret visibility rules.
- Tests: backend integration/unit coverage for fallback source selection and redaction.
- Runtime data: no schema migration and no direct production data mutation required.
