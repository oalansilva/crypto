## ADDED Requirements

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
