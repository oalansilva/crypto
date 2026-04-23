# 2026-04-22-backfill-historico-ativos / ui Specification

## Purpose

Expose backfill job control and progress in Admin with an operator-friendly timeline.

## ADDED Requirements

### Requirement: O sistema SHALL show active and historical backfill jobs in Admin

The admin interface SHALL include a page/table for backfill jobs with real-time status.

#### Scenario: Visualizar jobs
- **GIVEN** at least one backfill job exists
- **WHEN** admin opens the dedicated backfill section
- **THEN** the page SHALL list `symbol`, `timeframes`, `status`, `progress%`, `ETA`, `updated_at`.

### Requirement: O sistema SHALL allow manual job actions from Admin

Administrators SHALL start and control jobs without backend console access.

#### Scenario: Start / retry / cancel
- **WHEN** admin clicks start, retry, or cancel
- **THEN** the backend job state SHALL reflect the action within 1 minute.

### Requirement: The system SHALL show failure context

The system SHALL show failure context for failed jobs.

#### Scenario: Inspecionar erro
- **GIVEN** job status is `failed`
- **WHEN** admin opens job details
- **THEN** the system SHALL show last_error, attempts, and recent event list with timestamps.

### Requirement: O sistema SHALL present loading and empty/error states

The page SHALL be explicit and stable under all states.

#### Scenario: Lista vazia
- **WHEN** no job exists
- **THEN** the page SHALL show empty-state messaging and CTA para iniciar backfill.

#### Scenario: Erro de consulta
- **WHEN** API admin for jobs fails
- **THEN** a clear error state SHALL be shown and retry action made available.
