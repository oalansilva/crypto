## ADDED Requirements

### Requirement: Every database connection URL in CI and tests declares the driver explicitly

Every URL used as a real database connection in the backend CI workflows and in the test suite SHALL declare the PostgreSQL driver explicitly as `postgresql+psycopg2://`, so that no connection depends on the default driver that SQLAlchemy may change. A URL is a "connection" when it is passed to `create_engine`, to a `sessionmaker`/`bind`, or set as a `DATABASE_URL` / `WORKFLOW_DATABASE_URL` environment variable. Strings that are only assertions, expected values, guard inputs or fixture content SHALL NOT be changed by routine.

#### Scenario: CI job environment URLs are explicit

- **WHEN** the `backend-unit-tests` and `backend-tests` jobs in `.github/workflows/ci.yml` define `DATABASE_URL` and `WORKFLOW_DATABASE_URL`
- **THEN** both values SHALL use the `postgresql+psycopg2://` driver form
- **AND** no `postgresql://` URL without an explicit driver SHALL remain in those job environments

#### Scenario: Test files with real connections are explicit

- **WHEN** the test files that build a real connection (`backend/tests/conftest.py` and the integration/unit/contract files listed in the change design) declare a hardcoded database URL
- **THEN** each such URL SHALL use the `postgresql+psycopg2://` driver form

#### Scenario: Indirect connections are covered by their source

- **WHEN** a test builds a connection from `os.environ["DATABASE_URL"]` or from a `unit_database_url` / `unit_workflow_database_url` fixture
- **THEN** the underlying value SHALL already be explicit because the `conftest.py` default and the CI job environment are explicit

#### Scenario: Assertion and expected strings stay untouched

- **WHEN** a `postgresql://` string is only an assertion, an expected value, a guard input or fixture text (for example `assert _is_postgres_url("postgresql://db")` or a `Project.workflow_database_url` metadata value)
- **THEN** it SHALL NOT be rewritten by this change

#### Scenario: URL guard helpers keep accepting both forms

- **WHEN** `_is_postgres_url` (`backend/app/database.py`) or its workflow counterpart accepts a URL
- **THEN** it SHALL keep accepting both `postgresql://` and `postgresql+psycopg2://`
- **AND** the existing assertions that rely on this SHALL remain valid without modification

### Requirement: A clean install resolves SQLAlchemy 2.1.x with no pin

`backend/requirements.txt` SHALL keep `sqlalchemy>=2.0.0` without an upper bound, so that a clean install resolves the dependency to the **2.1.x** line, proving that the explicit driver removes the need for a pin. No other backend dependency SHALL change, and no `psycopg` v3 dependency SHALL be added.

#### Scenario: The requirements file keeps no upper bound

- **WHEN** the `sqlalchemy` line in `backend/requirements.txt` is read
- **THEN** it SHALL remain `sqlalchemy>=2.0.0` with no `<2.1` or equivalent upper bound

#### Scenario: A clean install resolves the 2.1 line

- **WHEN** a clean install runs from `backend/requirements.txt`
- **THEN** the resolved `sqlalchemy` version SHALL be `2.1.x`

#### Scenario: No driver migration and no other dependency change

- **WHEN** the change is applied
- **THEN** no `psycopg` v3 dependency SHALL be added
- **AND** no other backend dependency version or constraint SHALL change

### Requirement: Backend jobs and the QA gate run green under SQLAlchemy 2.1

On the pull request that carries this change, `backend-unit-tests` and `backend-tests` SHALL run to completion without failures, and `qa-gate` SHALL report `success`. The jobs SHALL NOT fail with `ModuleNotFoundError: No module named 'psycopg'`, and the integration suite SHALL NOT fail with `UndefinedTable: combo_templates`, because the explicit driver lets the first integration file create the shared schema again.

#### Scenario: Backend unit tests complete

- **WHEN** `backend-unit-tests` runs on the change's pull request
- **THEN** it SHALL install `sqlalchemy` `2.1.x`
- **AND** pytest SHALL NOT raise `ModuleNotFoundError: No module named 'psycopg'`

#### Scenario: Backend tests complete

- **WHEN** `backend-tests` runs on the change's pull request
- **THEN** it SHALL install `sqlalchemy` `2.1.x`
- **AND** it SHALL NOT raise `ModuleNotFoundError: No module named 'psycopg'`
- **AND** it SHALL NOT fail with `UndefinedTable` for `combo_templates`

#### Scenario: The schema bootstrap is restored

- **WHEN** the first integration file (`backend/tests/integration/test_ai_dashboard_dynamic.py`) runs `Base.metadata.create_all` on the shared database
- **THEN** it SHALL succeed and create the tables, including `combo_templates`
- **AND** the combo test that mounts a local app without `lifespan` SHALL find the table

#### Scenario: QA gate is green

- **WHEN** a bundle runs on the pull request whose base is `develop`
- **AND** `backend-unit-tests` and `backend-tests` finish `success`
- **THEN** `qa-gate` SHALL report `success`

### Requirement: DEV and PROD remain unchanged

This change SHALL NOT alter the DEV or PROD configuration. Both environments already use the explicit `postgresql+psycopg2://` driver, and the restart procedure SHALL NOT reinstall dependencies.

#### Scenario: Environment files already explicit

- **WHEN** the DEV `backend/.env` database variables are read
- **THEN** all four values SHALL already use `postgresql+psycopg2://`

#### Scenario: Restart does not reinstall dependencies

- **WHEN** the DEV restart procedure runs
- **THEN** it SHALL NOT run `pip install`
- **AND** the running DEV environment SHALL keep its existing installed SQLAlchemy

#### Scenario: No product code touched

- **WHEN** the change is applied
- **THEN** `backend/app/**`, `backend/alembic/**`, `backend/requirements.txt`, the Dockerfile and `frontend/**` SHALL remain unchanged
