## ADDED Requirements

### Requirement: Safe default crypto runtime startup

The crypto startup path SHALL NOT start Binance candle fetch loops, backfill schedulers, runtime worker routines, or Celery batch workers by default.

#### Scenario: normal startup uses defaults

- **GIVEN** no explicit worker enablement flags are set
- **WHEN** `start.sh` starts the crypto application
- **THEN** the backend starts with Binance realtime disabled
- **AND** OHLCV ingestion and backfill scheduling remain disabled
- **AND** runtime worker routines remain disabled
- **AND** the Binance realtime worker and Celery worker are not started.

#### Scenario: worker enablement flag is empty

- **GIVEN** a worker enablement flag is unset or empty
- **WHEN** `start.sh` evaluates whether the worker is enabled
- **THEN** the flag is treated as disabled.

#### Scenario: legacy runtime routine flags remain in env

- **GIVEN** `CRYPTO_RUNTIME_WORKER_ENABLED` is not enabled
- **AND** one or more legacy `RUN_*` runtime routine flags are enabled
- **WHEN** `start.sh` starts the crypto application
- **THEN** the runtime worker is not started.

#### Scenario: operator explicitly enables a worker

- **GIVEN** an operator sets the relevant worker enablement flag and required routine flag
- **WHEN** `start.sh` starts the crypto application
- **THEN** only that explicitly enabled worker family may start.
