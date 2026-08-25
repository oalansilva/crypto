## ADDED Requirements

### Requirement: Runtime JWT_SECRET is fail-closed
The runtime process that signs or validates JWT SHALL resolve `JWT_SECRET` through a single criterion and SHALL refuse to start when the value is invalid. Invalid means: unset, empty or whitespace-only, equal to the known default `dev-secret-change-in-production`, or shorter than 32 characters. The process SHALL NOT fall back to a repository-versioned default. Pytest is the only exception and MUST supply an explicit test secret that is not the known default.

#### Scenario: Missing or empty secret refuses boot
- **WHEN** a DEV or PROD runtime process that signs or validates JWT starts without `JWT_SECRET`, or with a value that is empty or whitespace-only
- **THEN** the process SHALL fail before accepting authenticated requests
- **AND** the error SHALL name `JWT_SECRET` as invalid
- **AND** the error SHALL NOT include the candidate value (empty, whitespace, known default, or short dummy)

#### Scenario: Known default refuses boot
- **WHEN** a DEV or PROD runtime process that signs or validates JWT starts with `JWT_SECRET` equal to `dev-secret-change-in-production`
- **THEN** the process SHALL fail before accepting authenticated requests
- **AND** it SHALL fail even if that value was set explicitly in the environment

#### Scenario: Short secret refuses boot
- **WHEN** a DEV or PROD runtime process that signs or validates JWT starts with `JWT_SECRET` whose length is less than 32 characters and that is not otherwise empty
- **THEN** the process SHALL fail before accepting authenticated requests

#### Scenario: Valid secret allows boot and login
- **WHEN** `JWT_SECRET` has length at least 32 and is not the known default
- **THEN** the process SHALL start
- **AND** `POST /api/auth/login` with valid credentials SHALL issue HS256 `access` and `refresh` tokens
- **AND** `get_current_user` and `get_current_admin` SHALL accept a valid access token signed with that secret

#### Scenario: Auth, middleware and OOS proof share the same criterion
- **WHEN** `app.routes.auth`, `app.middleware.authMiddleware` or `app.services.oos_promotion_proof` signs or validates a JWT
- **THEN** each path SHALL use the same resolved `JWT_SECRET`
- **AND** none of those paths SHALL call `os.getenv("JWT_SECRET", "<known default>")`

### Requirement: Tokens signed with the known default are rejected
After the fail-closed loader is in place, the runtime SHALL reject HS256 tokens signed with the known default.

#### Scenario: Forged access token with known default is 401
- **WHEN** a caller presents an HS256 access token whose `sub` is a user UUID and that was signed with `dev-secret-change-in-production`
- **THEN** `get_current_user` and `get_current_admin` SHALL respond 401
- **AND** SHALL NOT treat the caller as authenticated

### Requirement: Tests never use the known default
Automated tests SHALL set an explicit `JWT_SECRET` that is not the known default and SHALL cover the invalid cases of the fail-closed loader.

#### Scenario: Pytest supplies a test secret
- **WHEN** the backend pytest suite starts
- **THEN** tests SHALL assign `os.environ["JWT_SECRET"]` to an explicit value of length at least 32 that is not the known default **before** importing `app.config`
- **AND** that assignment SHALL NOT use `setdefault` (so `load_dotenv(..., override=False)` cannot inherit a live or default secret)
- **AND** tests SHALL NOT depend on `os.getenv("JWT_SECRET", "<known default>")` including helpers in `test_oos_promotion_proof_digest`

#### Scenario: Invalid secrets are unit-tested
- **WHEN** the unit tests for JWT secret resolution run
- **THEN** they SHALL assert failure for unset, empty/whitespace, known default, and length less than 32
- **AND** they SHALL assert that each failure `RuntimeError` names `JWT_SECRET` and does not contain the candidate value
- **AND** they SHALL assert success for a valid secret

### Requirement: Example env documents JWT_SECRET without a real value
The backend env example SHALL document `JWT_SECRET` with a placeholder and SHALL NOT contain a usable secret.

#### Scenario: Placeholder only
- **WHEN** a contributor opens the backend env example
- **THEN** `JWT_SECRET` SHALL be present
- **AND** its value SHALL be a placeholder (not the known default and not a production secret)

### Requirement: One-off snapshot scripts drop the known-default fallback
The one-off scripts `scripts/card_262_*` and `scripts/card_277_*` SHALL NOT load `JWT_SECRET` with the known-default fallback. They are not runtime.

#### Scenario: Scripts have no repository default
- **WHEN** those scripts resolve `JWT_SECRET`
- **THEN** they SHALL NOT use `os.getenv("JWT_SECRET", "dev-secret-change-in-production")`
- **AND** they SHALL fail or require an explicit environment secret instead of signing with the known default
