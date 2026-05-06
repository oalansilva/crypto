## Why

The closed beta cannot expose public account creation, because any visitor can currently create an account and reach authenticated product surfaces. This change makes beta access explicit and support-managed before broader launch.

## What Changes

- Disable public self-registration by default for the beta login flow.
- Keep login available for existing active users managed through the admin user workflow.
- Allow explicit self-registration only for configured invited emails when the backend environment grants it.
- Remove the visible `Criar Conta` path from the login page so visitors see login-only beta access.
- Register tests that authorized users can log in and unauthorized visitors cannot create access.

## Capabilities

### New Capabilities
- `closed-beta-access-control`: Defines login and account creation behavior for closed beta access.

### Modified Capabilities
- `admin-user-management`: Clarifies that support/admin user creation is the primary invite/access flow during closed beta.
- `frontend-ux`: Login page must not advertise public account creation during closed beta.

## Impact

- Backend auth route: `/api/auth/register`.
- Frontend login page and auth store usage.
- Environment/config docs for invited beta emails.
- Backend unit tests and focused frontend E2E for login page access posture.
