# discovery-discard Specification

## Purpose

Permitir que o administrador descarte um resultado individual de Discovery que não pretende promover, com confirmação e persistência.
## Requirements
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

### Requirement: Discard from Acompanhar parciais with the same dialog

The system SHALL allow an authenticated administrator to discard a persisted discovery result that is not `already_promoted` from Acompanhar locked top-5 parciais using the **same** confirmation dialog as Decidir (**Excluir resultado**). Cancel, Voltar, or overlay dismiss SHALL leave the candidate and the sweep unchanged. After confirmed discard the result SHALL disappear from the parciais **and** from Decidir of the same sweep, SHALL stay omitted after F5, and SHALL NOT reopen the Montar draft. The vacated top-5 slot MAY be filled by the next already-processed eligible result of that sweep (no ghost row). Discard SHALL NOT cancel the sweep and SHALL NOT delete favorites.

#### Scenario: Discard a partial and the next processed occupies the slot

- **GIVEN** Acompanhando with five locked parciais and at least one further processed eligible result
- **WHEN** the operator confirms Excluir on one unpromoted row
- **THEN** that `result_id` is persisted as `discarded`
- **AND** it disappears from the parciais and from Decidir of the same sweep
- **AND** the next already-processed eligible result MAY occupy the vacated top-5 place
- **AND** the draft stays collapsed (Montar does not reopen)

#### Scenario: Cancel discard leaves ranking and sweep untouched

- **GIVEN** the discard dialog opened from a parciais Excluir
- **WHEN** the operator cancels, goes Voltar, or dismisses the overlay
- **THEN** the candidate remains in the parciais and in Decidir
- **AND** the sweep stays as it was

