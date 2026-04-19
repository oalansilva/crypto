# Async Processing

The repository now uses Redis + Celery for durable background jobs that should not stay tied to the FastAPI process lifetime.

## What runs where

- `worker`: long-lived runtime loops such as `signal_monitor` and signal feed refresh
- `celery-worker`: discrete jobs pulled from Redis-backed queues
- `redis`: broker + shared job state + failed-task registry

## Current Celery workload

The first migrated workload is combo `batch backtest`.

- API creates a `queued` job record before dispatch
- Celery consumes the job from the `batch_backtest` queue
- job progress is stored in Redis and can be read back by the API
- retries use exponential backoff with jitter
- when retries are exhausted, the job is marked as failed and copied to the dead-letter registry

## Defaults tuned for this VM

- `CELERY_WORKER_CONCURRENCY=1`
- `CELERY_WORKER_PREFETCH_MULTIPLIER=1`
- `CELERY_BATCH_MAX_RETRIES=3`
- `CELERY_RETRY_BACKOFF_MAX=300`

This keeps CPU pressure low on the current `2 vCPU / 8 GiB RAM` machine.

## Dead-letter registry

Failed jobs that exhaust all retries are pushed to:

- Redis list: `batch_backtest:dead_letters`

Job progress lives under:

- Redis key pattern: `batch_backtest:job:<job_id>`

## Operational commands

```bash
make docker-up
make celery-logs
```

Scale out only when needed:

```bash
docker compose --env-file .env.docker.local up --scale celery-worker=2
```

Prefer scaling by service count before raising per-process concurrency on this VM.
