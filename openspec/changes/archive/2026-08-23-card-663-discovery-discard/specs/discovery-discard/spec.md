# discovery-discard Specification

## Purpose

Permitir que o administrador descarte um resultado individual de Discovery que não pretende promover, com confirmação e persistência.

## ADDED Requirements

### Requirement: Discard a discovery result with confirmation

The system SHALL allow an authenticated administrator to discard a persisted discovery result that is not `already_promoted`. The UI SHALL require explicit confirmation showing candidate identity, `sweep_id` and `result_id`. Discard SHALL persist a durable `discarded` state on that `result_id` (not only client-side hide). A discarded result SHALL NOT appear in the default leaderboard of that sweep and SHALL NOT be promotable. Reloading the page or re-fetching the sweep SHALL keep it omitted. Discard SHALL NOT delete the favorite store, templates, or other results.

#### Scenario: Discard a unique unpromoted result

- **WHEN** the administrator confirms discard of a unique eligible result
- **THEN** the result is persisted as `discarded`
- **AND** it disappears from the default leaderboard
- **AND** a later GET of that sweep does not include it in default results

#### Scenario: Discard remains available when promotion is blocked

- **WHEN** the result is `low_sample` or `duplicate`
- **THEN** promotion stays unavailable with an explicit reason
- **AND** discard remains available and, after confirm, persists `discarded`

#### Scenario: Already promoted cannot be discarded here

- **WHEN** the result is `already_promoted`
- **THEN** the leaderboard does not offer discard
- **AND** the favorite remains unchanged

#### Scenario: Reject discard without admin

- **WHEN** a non-admin or unauthenticated client requests discard
- **THEN** the server returns `403` or `401`
- **AND** no result state changes

#### Scenario: Idempotent discard

- **WHEN** discard is retried for an already `discarded` result
- **THEN** the server returns success without erroring as a missing resource
- **AND** the result remains `discarded`
