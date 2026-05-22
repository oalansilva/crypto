## ADDED Requirements

### Requirement: Safe default runtime topology
The Crypto stack SHALL start only the lightweight default services unless an operator explicitly enables optional worker families.

#### Scenario: default stack boot keeps heavy workers disabled
- **WHEN** the operator starts the stack with default environment values
- **THEN** Redis, database migrations, backend API, and frontend UI may start
- **AND** candle writer, historical backfill scheduler, Binance realtime worker, generic runtime worker routines, and Celery batch worker remain disabled.

#### Scenario: optional worker requires explicit enablement
- **WHEN** a worker family is not explicitly enabled by its documented flag
- **THEN** startup SHALL NOT call or launch that worker family.

### Requirement: Dedicated candle writer operation
The canonical Binance candle writer SHALL have a dedicated service/timer path and SHALL prevent concurrent writer executions.

#### Scenario: writer service is opt-in
- **WHEN** the default Crypto stack service starts
- **THEN** it SHALL NOT enable or run the dedicated candle writer service or timer.

#### Scenario: writer lock prevents duplicate Binance fetch
- **WHEN** a canonical candle writer process is already holding the writer lock
- **AND** another writer command starts
- **THEN** the second command SHALL skip without fetching Binance candles
- **AND** it SHALL report that the writer lock is held.

#### Scenario: writer records latest run state
- **WHEN** the canonical candle writer command runs
- **THEN** it SHALL persist a local state record with started time, finished time, status, process id, run count, and duration or error summary.

### Requirement: Runtime status evidence
The API SHALL expose runtime status evidence that proves service defaults, candle writer state, and canonical candle storage state without exposing secrets.

#### Scenario: runtime status endpoint returns safe operational state
- **WHEN** a client requests runtime status
- **THEN** the response SHALL include canonical candle mode, direct fetch fallback state, optional worker enablement flags, candle writer lock state, latest candle writer run state, and `market_ohlcv` metrics availability.
- **AND** the response SHALL NOT include database URLs, Redis URLs, tokens, passwords, raw command lines, or raw environment values.

#### Scenario: existing health endpoint remains lightweight
- **WHEN** a client requests `/api/health`
- **THEN** the response SHALL remain a lightweight API liveness response
- **AND** it SHALL NOT require optional workers to be running.

### Requirement: Runtime architecture runbook
The project documentation SHALL describe the runtime architecture, service ownership, startup order, flags, logs, and operator verification commands.

#### Scenario: operator needs to verify no duplicate candle collection
- **WHEN** the operator follows the runtime runbook
- **THEN** the documented commands SHALL show how to inspect API/UI health, runtime status, writer lock/state, active worker processes, and candle metrics.

#### Scenario: operator wants scheduled candle catch-up
- **WHEN** the operator follows the runtime runbook for scheduled candle writing
- **THEN** the documentation SHALL point to the dedicated candle writer service/timer installer and the commands to inspect, disable, and view logs.
