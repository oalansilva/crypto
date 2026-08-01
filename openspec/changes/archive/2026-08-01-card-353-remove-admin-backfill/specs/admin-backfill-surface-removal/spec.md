## ADDED Requirements

### Requirement: Admin Backfill surface is removed from the product UI
The application SHALL NOT expose `/admin/backfill` as a navigable product route and SHALL NOT show a navigation link labeled Backfill.

#### Scenario: Admin navigation no longer lists Backfill
- **WHEN** an authenticated admin opens the principal navigation
- **THEN** the navigation SHALL NOT include a link to `/admin/backfill`
- **AND** remaining admin entries such as Combo, Preferências do sistema, and Usuários remain available when applicable

#### Scenario: Backfill route is not registered
- **WHEN** a client requests `/admin/backfill` in the SPA router
- **THEN** the path SHALL NOT render the former Admin Backfill page

### Requirement: Exclusive admin backfill APIs are no longer exposed
The backend SHALL NOT expose the discontinued admin backfill API under `/api/admin/backfill`.

#### Scenario: Admin backfill jobs API is unavailable
- **WHEN** a client calls a former `/api/admin/backfill/jobs` endpoint
- **THEN** the request SHALL NOT be served by the removed admin-backfill router as a supported capability

#### Scenario: Admin backfill scheduler trigger is unavailable
- **WHEN** a client calls `POST /api/admin/backfill/scheduler/run-now`
- **THEN** the backend SHALL NOT expose the former admin scheduler handler as a supported capability

### Requirement: Programmatic OHLCV backfill remains intact
Removing the admin Backfill surface MUST NOT remove `ohlcv_backfill_service`, its store, optional scheduler boot, or full-history scheduling used by market candles.

#### Scenario: Full-history candle request can still schedule backfill
- **WHEN** `/market/candles` is called with `full_history=true` for a supported crypto pair
- **THEN** the backend SHALL still be able to schedule history via `ensure_history_job` without depending on the removed admin UI/API

#### Scenario: Optional backfill scheduler boot path remains
- **WHEN** runtime flags enable the backfill scheduler
- **THEN** application startup SHALL still be able to start/stop the backfill scheduler through the service layer
