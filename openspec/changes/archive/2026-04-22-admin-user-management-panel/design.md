## Context

The app already has user authentication and an admin gate based on `ADMIN_EMAILS`, but no dedicated operational surface for account support actions. Current needs are: search and filter users, perform support CRUD updates, enforce ban/suspension workflows, and retain an auditable action log for sensitive operations under privacy constraints.

The stack is FastAPI for backend APIs and React for frontend pages, with single-tenant SQLite/PostgreSQL via SQLAlchemy models and lightweight migration logic in `backend/app/database.py`. This change should be additive and preserve existing user flows.

## Goals / Non-Goals

**Goals:**
Deliver an admin-only management capability to list, filter, edit, deactivate/reactivate, and ban/suspend users; persist status transitions and reasons; provide a privacy-aware admin action log that records who did what and why.

**Non-Goals:**
Full role-based access control with multiple admin roles, enterprise-grade identity providers, and complete legal/legal-process evidence exports. Password reset by admin is out of scope unless explicitly requested in a follow-up change.

## Decisions

- Decision: Add a dedicated admin API namespace `/api/admin/users` and `/api/admin/user-actions` protected by `AdminUser`.
  - Rationale: Keeps support operations explicit and avoids overloading existing profile/auth endpoints.
  - Alternative: extend existing user routes with admin flags in query params.
  - Why rejected: would dilute authorization boundaries and complicate auditability.

- Decision: Add a new `users` operational status model via fields (`status`, `suspended_until`, `suspension_reason`, `is_banned`), with `active` as the default status.
  - Rationale: Enables ban and suspension semantics without deleting users and supports automatic expiry for timed suspensions.
  - Alternative: model ban/suspension in a separate table only.
  - Why rejected: adds extra joins for every lookup and makes account filters slower to implement for support workflows.

- Decision: Introduce a new `admin_action_logs` table with `actor_user_id`, `target_user_id`, `action`, `target_subject`, `reason`, `created_at`, and metadata JSON.
  - Rationale: mandatory auditability for support actions while keeping mutable payloads in `metadata` for schema evolution.
  - Alternative: reuse existing logs with generic names.
  - Why rejected: existing logging is operational, not accountability-focused and lacks actor/target action-level semantics.

- Decision: Create service-level helper methods for user state transitions and centralized action logging.
  - Rationale: avoids duplicated validation and ensures every transition writes consistent audit records.
  - Alternative: perform side effects directly in each route handler.
  - Why rejected: higher risk of missing audit entries and inconsistent permission checks.

- Decision: Build a UI under an admin route (e.g. `/admin/users`) with three zones: query/filter controls, user table/card list, and action drawers/modals.
  - Rationale: keeps high-risk actions grouped and discoverable while minimizing accidental changes.
  - Alternative: expose actions only inside profile pages.
  - Why rejected: increases support latency and causes inconsistent navigation patterns.

- Decision: LGPD-oriented logging policy stores only minimal personal data in logs.
  - Rationale: audit should prove action, actor, target, timestamp, and reason without exposing sensitive credentials or extra PII.
  - Alternative: keep full user snapshots in logs.
  - Why rejected: unnecessary retention of sensitive data and higher compliance risk.

## Risks / Trade-offs

- [Risk] Ban/suspension actions can be abused by compromised admin accounts.
  - Mitigation: enforce strict admin allowlist, require explicit reason for every state change, and log every operation.
- [Risk] Existing clients may rely on current user data shape when reading user objects.
  - Mitigation: keep existing fields unchanged and add new optional fields.
- [Risk] Suspensions may persist beyond business intent if `suspended_until` is missed or timezone-handled incorrectly.
  - Mitigation: store UTC timestamps and validate transitions before action execution.
- [Risk] UI actions may be slow on large user bases if search/filter is not indexed.
  - Mitigation: add index on common filter columns and paginate every user list response.

## Migration Plan

1. Add migration-safe model changes for user status fields and `admin_action_logs`.
2. Extend `backend/app/database.py` schema bootstrap/alter checks to create the new columns and table when missing.
3. Backfill existing users: `status=active`, `is_banned=false`, clear suspension fields.
4. Deploy admin routes and DTO schemas with no functional changes to public endpoints.
5. Add frontend admin page and bind API calls.
6. Rollback: keep reads backward-compatible; if needed, disable admin routes and keep existing user table intact, preserving original account records.

## Open Questions

- O painel deve permitir reativação de usuário já banido no mesmo fluxo de suspensão, ou exigir ação separada?
- Banimento deve incluir bloqueio imediato de login via autenticação (token rejection) ou apenas bloquear ações no app no primeiro release?
