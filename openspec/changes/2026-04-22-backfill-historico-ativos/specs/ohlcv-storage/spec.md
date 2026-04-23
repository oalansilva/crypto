# 2026-04-22-backfill-historico-ativos / ohlcv-storage Specification

## Purpose

Enable deterministic 2-year historical backfill for new/selected assets using existing OHLCV providers while preserving current incremental ingestion behavior.

## ADDED Requirements

### Requirement: O sistema SHALL run a dedicated historical backfill for onboarding assets

The system SHALL ingest up to 2 years of OHLCV candles for a given symbol when a backfill job is started manually or by schedule.

#### Scenario: Backfill onboarding fills minimum 2-year history
- **GIVEN** a backfill job is started for `symbol`
- **WHEN** the provider returns candles for the requested time window
- **THEN** the service SHALL attempt to fetch from `now - 24 months` to `now`
- **AND** persist all successfully retrieved candles
- **AND** mark job scope as `partial_complete` if provider history is shorter than requested.

### ADDED Requirement: O sistema SHALL paginate historical fetches by bounded page window

The service SHALL fetch candles in discrete pages/chunks, ordered by time, so calls remain bounded and resumable.

#### Scenario: Paginação e checkpoint
- **GIVEN** a symbol with a large date range
- **WHEN** backfill starts
- **THEN** the system SHALL request candles in pages of fixed limit (or provider max page limit)
- **AND** store a checkpoint after each successful page
- **AND** resume from the checkpoint after restart/failure.

### ADDED Requirement: O sistema SHALL persist with candle-level dedupe to guarantee idempotence

OHLCV writes SHALL continue using upsert by `(symbol, timeframe, candle_time)` and SHOULD log duplicate-skip metrics.

#### Scenario: Safe rerun
- **GIVEN** a job is retried after partial failure
- **WHEN** it reaches an already ingested candle
- **THEN** the write SHALL no-op for that candle
- **AND** progress SHALL continue with the next required candle without corruption.

### ADDED Requirement: O sistema SHALL enforce request pacing and retries during historical fetch

The service SHALL not exceed configured rate budgets and SHALL recover transient provider failures.

#### Scenario: Rate-limit-safe fetch
- **GIVEN** provider responses with 429 or high failure rates
- **WHEN** fetch loop runs
- **THEN** the system SHALL apply delay/budget checks
- **AND** retry with exponential backoff + jitter
- **AND** continue until success or job failure threshold.

### ADDED Requirement: O sistema SHALL expose a completion summary

Each job SHALL report completion metrics for operator review.

#### Scenario: Job summary
- **GIVEN** backfill completes
- **WHEN** admin reads job result
- **THEN** the system SHALL provide `requested_window`, `fetched_count`, `written_count`, `deduped_count`, `duration_seconds`, and `status`.
