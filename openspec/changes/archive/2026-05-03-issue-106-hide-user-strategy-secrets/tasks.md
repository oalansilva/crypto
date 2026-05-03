## 1. Backend Redaction

- [x] 1.1 Add a shared strategy secret redaction helper with admin/non-admin behavior.
- [x] 1.2 Redact non-admin responses from `GET /api/favorites/` without changing create/update inputs.
- [x] 1.3 Redact non-admin responses from `GET /api/opportunities/`, including cached payloads.
- [x] 1.4 Restrict combo/template/backtest/optimization APIs to admin users.

## 2. Frontend Protected Rendering

- [x] 2.1 Update Monitor types/cards/export/chart modal to handle protected strategy payloads.
- [x] 2.2 Update Favorites rendering helpers to avoid exposing protected parameter values.
- [x] 2.3 Add admin route guards for frontend strategy tooling pages.

## 3. Validation

- [x] 3.1 Add or update backend tests covering non-admin redaction and admin full-detail responses.
- [x] 3.2 Add or update backend tests covering combo API admin-only enforcement.
- [x] 3.3 Add or update frontend/E2E coverage for protected Monitor rendering and route guards where proportional.
- [x] 3.4 Run OpenSpec validation, backend tests, frontend build, and `./restart`.

Note: use project skills when applicable: `crypto-frontend` for UI, OpenSpec skills for this change, and reviewer/debugging skills for validation.
