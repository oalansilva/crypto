## ADDED Requirements

### Requirement: The Farol no longer has the directional scalper
The Farol SHALL NOT show a Scalp BTCUSDT module, SHALL NOT expose `/api/scalp/*` as a live feature (GET `/api/scalp/status` SHALL return 404), SHALL NOT run a scalper loop in the API or the runtime-worker, SHALL NOT send orders with client id prefix `cfscalp_`, SHALL NOT call Jev/TypeSafe, and SHALL NOT keep the five scalper tables after the new drop migration: `scalp_user_states`, `scalp_fills`, `scalp_jev_diagnoses`, `scalp_confidence_versions`, `scalp_calibration_state`. Flags `RUN_SCALP_LOOP`, `SCALP_API_LOOP_ENABLED`, `SCALP_*`, `JEV_*` and `TYPESAFE_*` SHALL leave the product runtime, service units and operations docs. Scripts `scalp_*`, scalper unit/e2e tests and scalper card prototypes SHALL leave the tree. OpenSpec capabilities `scalp-*` SHALL be withdrawn. Shared specs SHALL stop citing the scalper. Active OpenSpec changes of #1045 and #1070 SHALL leave `openspec/changes/`. Archived OpenSpec changes #1001–#1043 and old Alembic revisions SHALL remain as history. Monitor, Ajuda, Perfil, Credenciais da Binance and the public landing SHALL NOT mention scalper/scalp and SHALL NOT announce that it left.

#### Scenario: Monitor has no scalper
- **WHEN** an authenticated user opens `/monitor` on desktop or mobile
- **THEN** no scalper element SHALL appear
- **AND** Em posição, Saída / cobertura, KPIs and filters SHALL still work as they do today

#### Scenario: Scalp API is gone
- **WHEN** a client calls `GET /api/scalp/status`
- **THEN** the response SHALL be 404

#### Scenario: Worker and Operar keep running
- **WHEN** the backend and the runtime-worker start after this change
- **THEN** they SHALL start without error
- **AND** Discovery queue work and favorites refresh SHALL still run
- **AND** Operar and Carteira SHALL still work as before
- **AND** the Farol SHALL NOT query Jev

#### Scenario: Copy does not mention the scalper
- **WHEN** a user reads `/help`, Meu Perfil, Credenciais da Binance, or the public landing
- **THEN** those surfaces SHALL NOT mention scalper or scalp
- **AND** they SHALL NOT announce that a scalper was removed

### Requirement: A new migration drops the five scalper tables
A new Alembic revision SHALL drop `scalp_user_states`, `scalp_fills`, `scalp_jev_diagnoses`, `scalp_confidence_versions` and `scalp_calibration_state`, including their data. Older scalper migrations SHALL remain in the history so databases that already applied them (DEV and PROD) are not rewritten.

#### Scenario: Tables gone after upgrade
- **WHEN** `alembic upgrade head` has been applied
- **THEN** the five scalper tables SHALL NOT exist
- **AND** the historical create migrations SHALL still be present in the Alembic tree
