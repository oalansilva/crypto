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

#### Scenario: operator explicitly enables a worker

- **GIVEN** an operator sets the relevant worker enablement flag
- **WHEN** `start.sh` starts the crypto application
- **THEN** only that explicitly enabled worker family may start.
