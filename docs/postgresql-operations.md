# PostgreSQL Operations

This repository standardizes on PostgreSQL for runtime databases.

## Current scope

- PostgreSQL 16 for runtime and workflow databases
- Alembic for versioned runtime schema migrations
- Daily logical backups via `pg_dump`
- TimescaleDB intentionally deferred until candles/indicators are persisted as first-class tables

## Docker workflow

Copy the Docker env file and start the stack:

```bash
cp .env.docker.example .env.docker.local
make docker-up
```

The backend container applies `alembic upgrade head` before starting FastAPI.

## Run migrations manually

From the repo root:

```bash
make db-migrate
```

Or directly:

```bash
cd backend
alembic upgrade head
```

## Daily backups

The `postgres-backup` service creates one logical dump per database every 24 hours.

- Output directory: `./backups/postgres`
- Retention: controlled by `BACKUP_RETENTION_DAYS`
- Interval: controlled by `BACKUP_INTERVAL_SECONDS`

Trigger an immediate one-off backup:

```bash
make db-backup
```

## Restore example

List available dumps:

```bash
ls -lah backups/postgres
```

Restore a single database dump:

```bash
pg_restore \
  --clean \
  --if-exists \
  --no-owner \
  --dbname postgresql://postgres:postgres@127.0.0.1:5432/crypto_app \
  backups/postgres/crypto_app_YYYYMMDDTHHMMSSZ.dump
```

## TimescaleDB decision

TimescaleDB is not provisioned yet on purpose.

Enable it only after the application starts persisting:

- candles / OHLCV history
- derived indicators in time-series tables
- retention/compression-sensitive datasets

Until then, PostgreSQL keeps the runtime simpler and fits the current VM profile better.
