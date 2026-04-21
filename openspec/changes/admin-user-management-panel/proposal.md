## Why

Hoje o suporte administrativo depende de verificações manuais e não possui uma superfície dedicada para localizar usuários, corrigir cadastro ou intervir em casos de abuso. Um painel administrativo reduz tempo de atendimento, melhora a governança operacional e permite registrar ações sensíveis com trilha de auditoria compatível com exigências de LGPD.

## What Changes

- Add an admin-only user management panel for support operations over user accounts.
- Add user listing with search and operational filters such as status, creation date, and recent access.
- Add CRUD flows for admin-driven user maintenance, including create, view, edit, and controlled deactivation/reactivation.
- Add ban and suspension actions with required operator attribution and support reason.
- Add an administrative action log for user-management interventions with privacy-aware data exposure.
- Add backend authorization, persistence, and API surfaces required to support admin moderation and auditability.

## Capabilities

### New Capabilities
- `admin-user-management`: Provides an admin-only panel and APIs for user listing, filtering, CRUD maintenance, and ban/suspension lifecycle management.
- `admin-action-audit-log`: Records and exposes a privacy-aware audit trail for administrative actions on user accounts, including actor, target, action, reason, and timestamp.

### Modified Capabilities
- None.

## Impact

- Affected code: `backend/app/models.py`, auth/admin middleware and routes, new admin-facing API routes, and frontend admin/support pages and components.
- Data model impact: user records will need manageable operational status fields plus a persistent audit log for administrative actions.
- API impact: new protected admin endpoints for user search, filters, CRUD actions, suspension/ban actions, and audit-log retrieval.
- Security/privacy impact: admin authorization rules must gate all operations, and audit visibility must minimize unnecessary personal data while preserving accountability.
