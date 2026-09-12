## MODIFIED Requirements

### Requirement: Admin can create support-managed users
The system SHALL allow admins to create a new user record when requested by support. This endpoint SHALL NOT be a public or unauthenticated access door: during closed beta the entrance door for a new account SHALL be a single-use invite, consumed on the invite link's own password-definition surface, and an admin-created user SHALL be a non-administrator account.

#### Scenario: Admin creates a valid user
- **WHEN** an admin posts valid user data to `POST /api/admin/users`
- **THEN** the system SHALL create the user and return the created user record
- **AND THEN** the system SHALL record an audit entry with action `user_created`
- **AND** the created active user SHALL be eligible to log in during closed beta

#### Scenario: Email conflict
- **WHEN** an admin tries to create a user using an existing email
- **THEN** the system SHALL reject the request with a validation error and not create or update any user

#### Scenario: Admin-created user is not an administrator
- **WHEN** an admin creates a user through `POST /api/admin/users`
- **THEN** the created user SHALL have a non-administrator role
- **AND** administrator role SHALL NOT be granted as a side effect of user creation

#### Scenario: Unauthenticated caller cannot create users
- **WHEN** a caller without a valid admin session calls `POST /api/admin/users`
- **THEN** the system SHALL reject the request with HTTP 401 or HTTP 403
- **AND** no user SHALL be created

### Requirement: Admin can list and search users
The system SHALL expose a paginated admin endpoint that returns users for operational support use. The returned records SHALL expose the persisted administrator role so support can tell an administrator account from a regular account without consulting environment configuration.

#### Scenario: Search by email or name
- **WHEN** an admin calls `GET /api/admin/users` with query `q`
- **THEN** the system SHALL return only users whose `email` or `name` contains the query (case-insensitive)
- **AND** the response SHALL include total count and pagination metadata

#### Scenario: Filter by user status and date
- **WHEN** an admin calls `GET /api/admin/users` with filters `status`, `createdFrom`, `createdTo`, `lastLoginFrom`, `lastLoginTo`
- **THEN** the system SHALL return users matching all active filters

#### Scenario: Persisted role is visible to support
- **WHEN** an admin reads a user profile through the admin user-management surface
- **THEN** the response SHALL include that user's persisted role
- **AND** the role SHALL NOT be derived from the `ADMIN_EMAILS` environment list at request time

## ADDED Requirements

### Requirement: Administrator role is persisted state, not an environment comparison
The system SHALL store administrator status on the user record. A user SHALL be treated as an administrator only because that persisted role says so, and never because the user's e-mail appears in the `ADMIN_EMAILS` environment list. The `ADMIN_EMAILS` environment list MAY remain as input for deployment bootstrap and for the migration backfill of the already-configured admin, but SHALL NOT be the runtime source of authorization. No public surface SHALL grant the administrator role.

#### Scenario: Already configured admin keeps the role after backfill
- **WHEN** the persistence migration runs on an installation whose configured `ADMIN_EMAILS` address already owns an account
- **THEN** that account SHALL keep administrator access
- **AND** no other account SHALL gain the administrator role as a side effect

#### Scenario: Privileged address without an account gains nothing from the migration
- **WHEN** the persistence migration runs and a configured `ADMIN_EMAILS` address has no account yet
- **THEN** the migration SHALL NOT create an account for that address
- **AND** the migration SHALL NOT grant administrator role to any existing account
- **AND** only the explicit deployment bootstrap command SHALL be able to make that address an administrator

#### Scenario: Runtime authorization reads the persisted role
- **WHEN** an authenticated user reaches an admin-only operation
- **THEN** the system SHALL authorize the request from the persisted role on that user's record
- **AND** the system SHALL NOT authorize the request from an `ADMIN_EMAILS` e-mail comparison

#### Scenario: Registration cannot grant the role
- **WHEN** any visitor creates an account through a public surface
- **THEN** the created account SHALL NOT carry the administrator role

### Requirement: Admin issues single-use invites
The system SHALL let an existing administrator issue a single-use invite for a target address through an authenticated admin-only endpoint, returning a copyable invite link that the operator delivers outside the product.

#### Scenario: Admin issues an invite
- **WHEN** an existing administrator posts a valid target address to the admin invite endpoint
- **THEN** the system SHALL issue a single-use invite bound to that address
- **AND** the response SHALL include the copyable invite link carrying the invite token
- **AND** the invite token in clear SHALL be returned only in that response and SHALL NOT be stored in clear, logged, or written to the audit record
- **AND** the system SHALL record the issuance in audit

#### Scenario: Non-admin cannot issue invites
- **WHEN** an authenticated user without the administrator role calls the admin invite endpoint
- **THEN** the system SHALL reject the operation with HTTP 403
- **AND** no invite SHALL be issued

#### Scenario: Invite issuance is not a public surface
- **WHEN** the admin invite endpoint is called without a valid administrator session
- **THEN** the system SHALL reject the request with HTTP 401 or HTTP 403
- **AND** the issuance SHALL NOT be reachable from `POST /api/auth/register` or from the public landing lead endpoint

### Requirement: Deployment bootstrap grants the first administrator idempotently
The system SHALL provide a deployment command that makes the address already configured in the environment exist and hold administrator role, without any public surface. On an installation where that account already exists the command SHALL only grant the role. On an installation where that account does not exist yet the command SHALL create it as an administrator using a credential supplied explicitly by the operator running the command; the command SHALL NOT generate a credential and SHALL NOT print or log one. The command SHALL be idempotent.

#### Scenario: First administrator is bootstrapped on a fresh deployment
- **WHEN** an operator runs the deployment bootstrap command on an installation with no administrator account
- **THEN** the account owning the address already configured in the environment SHALL exist and hold administrator role
- **AND** neither the public registration endpoint nor the public landing endpoint SHALL accept that privileged address without a valid invite
- **AND** the command SHALL NOT generate a password and SHALL NOT print one
- **AND** the credential SHALL be supplied explicitly by the operator running the command

#### Scenario: Existing configured account is only promoted
- **WHEN** the deployment bootstrap command runs and the configured address already owns an account
- **THEN** the command SHALL grant administrator role to that account without changing its password
- **AND** it SHALL NOT create any additional account

#### Scenario: Bootstrap is idempotent
- **WHEN** the deployment bootstrap command runs again after a successful run
- **THEN** the result SHALL be the same
- **AND** no additional account SHALL gain the administrator role

#### Scenario: Bootstrap creates no second administrator and promotes nothing outside the configured list
- **WHEN** the deployment bootstrap command runs
- **THEN** it SHALL NOT create a second administrator account
- **AND** it SHALL NOT promote any address outside the configured list

#### Scenario: Bootstrap surface is not reachable from the product
- **WHEN** the deployment bootstrap command is needed
- **THEN** it SHALL run as a deployment command on the host
- **AND** it SHALL NOT be exposed as an HTTP endpoint reachable from the product
- **AND** it SHALL NOT be reachable through `POST /api/auth/register` or the public landing lead endpoint
