## 1. Fundação de dados e autorização

- [ ] 1.1 Extend `backend/app/models.py` with admin operational fields on `User` (`status`, `suspended_until`, `suspension_reason`, `notes`)
- [ ] 1.2 Add `AdminUserAction`/`AdminActionLog` model for immutable audit records with indexes for actor, target, action, and timestamp
- [ ] 1.3 Update `backend/app/database.py` bootstrap/migrations to backfill existing users and create new columns/table safely for existing environments
- [ ] 1.4 Add or improve admin role checks in `backend/app/middleware/authMiddleware.py` to keep all new routes in `AdminUser` scope
- [ ] 1.5 Validate backend schema initialization and add migration-safe fallback for non-empty production data

## 2. API administrativa de usuários

- [ ] 2.1 Add request/response schemas in `backend/app/schemas` for user list filters, create/update payloads, and state transitions
- [ ] 2.2 Implement admin user listing endpoint `GET /api/admin/users` with pagination, search (`q`), and filters (`status`, date windows, last login windows)
- [ ] 2.3 Implement CRUD endpoints: `GET /api/admin/users/{userId}`, `POST /api/admin/users`, `PUT /api/admin/users/{userId}`
- [ ] 2.4 Implement lifecycle endpoints: `POST /api/admin/users/{userId}/suspend`, `POST /api/admin/users/{userId}/reactivate`, `POST /api/admin/users/{userId}/ban`
- [ ] 2.5 Enforce required `reason` for suspend/ban/update-sensitive transitions and validate suspension expiry behavior
- [ ] 2.6 Add endpoint `GET /api/admin/user-actions` with pagination, filters (`actorUserId`, `action`, date range, targetUserId), and newest-first ordering
- [ ] 2.7 Create and reuse centralized action logger service so every supported admin action writes one audit record (`action`, `actorUserId`, `targetUserId`, `reason`, `metadata`, `createdAt`)

## 3. Proteção de sessão e login por status

- [ ] 3.1 Enforce account status/bans in authentication/login flow (`/api/auth/login`) so banned users are denied access even with valid credentials
- [ ] 3.2 Ensure suspended users are blocked for sensitive endpoints and represented as `suspended` until `suspended_until` expires
- [ ] 3.3 Add service-level helper for status resolution and reuse in sensitive routes

## 4. Frontend do painel administrativo

- [ ] 4.1 Add admin route and page shell (e.g., `/admin/users`) with access guard consistent with existing auth patterns
- [ ] 4.2 Implement user search/filter bar and paginated table/list UI with columns for operational status, last login, created date, and ban/suspension metadata
- [ ] 4.3 Implement create, edit, and quick status controls with confirmation flows and required reason fields
- [ ] 4.4 Add dedicated ban/suspend/reactivate actions and explicit success/error feedback
- [ ] 4.5 Add per-user action log panel with details loaded from `GET /api/admin/user-actions`

## 5. Testes e qualidade

- [ ] 5.1 Add backend tests for admin access control, user listing filters, and lifecycle actions
- [ ] 5.2 Add backend tests for audit log creation on each action and privacy-safe payload assertions
- [ ] 5.3 Add frontend tests/smoke checks for panel rendering, search/filter, and admin action flows
- [ ] 5.4 Add E2E scenario for admin search + suspend/ban + audit visibility (using Playwright CLI workflow) and capture execution evidence

## 6. Finalização e handoff

- [ ] 6.1 Run `openspec validate admin-user-management-panel --type change` and close missing spec/format issues
- [ ] 6.2 Update coordination/runtime handoff comments with implementation evidence and blockers per gate
- [ ] 6.3 Sync delta specs to `openspec/specs/` only after implementation decisions are stable

Use `.codex/skills/playwright-cli-official` for UI automation and `.codex/skills/interface-design-codex` for UX validation if design touches are required.
