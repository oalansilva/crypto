# 2026-04-22-backfill-historico-ativos / job-manager Specification

## Purpose

Provide explicit job lifecycle management for historical OHLCV backfill and expose observable execution state.

## ADDED Requirements

### Requirement: O sistema SHALL support manual and scheduled backfill jobs

The system SHALL support starting backfill jobs both manually and via scheduler.

#### Scenario: Manual initiation
- **WHEN** admin starts a backfill job for a symbol
- **THEN** the system SHALL create a job in `pending`, then `running`.

#### Scenario: Scheduled initiation
- **WHEN** scheduler detects eligible new symbol or stale-history symbol
- **THEN** the system SHALL enqueue backfill job automatically.

### Requirement: O sistema SHALL track job state machine and progress

Each backfill job SHALL move through explicit states and persist progress counters.

#### Scenario: State transitions
- **GIVEN** a running job
- **WHEN** lifecycle changes
- **THEN** state SHALL be one of: `pending`, `running`, `paused`, `completed`, `partial_complete`, `failed`, `cancelled`.

#### Scenario: Progress visibility
- **WHEN** a job is running
- **THEN** the system SHALL expose `processed`, `total_estimate`, `percent`, `timeframes`, `symbols`, `attempts`, and `last_error`.

### Requirement: O sistema SHALL support cancellation/retry semantics

Operators SHALL be able to stop and retry safely.

#### Scenario: Cancel in progress
- **GIVEN** job in `running`
- **WHEN** cancel is requested
- **THEN** worker SHALL stop after safely flushing checkpoints
- **AND** mark job as `cancelled`.

#### Scenario: Retry partial/failed job
- **GIVEN** job in `failed`/`partial_complete`
- **WHEN** retry is requested
- **THEN** job SHALL resume from last checkpoint where possible and preserve previously completed chunks.

### Requirement: O sistema SHALL record structured job logs/events

Execution trace SHALL include per-step outcomes for operator diagnosis.

#### Scenario: Error recording
- **WHEN** an execution error occurs
- **THEN** the system SHALL append an event with timestamp, provider, timeframe, error type, and retry count.
