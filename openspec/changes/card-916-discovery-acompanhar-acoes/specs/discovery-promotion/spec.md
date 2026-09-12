## ADDED Requirements

### Requirement: Promote from Acompanhar parciais with the same tier-3 dialog

The system SHALL allow an authenticated administrator to promote an eligible `unique` discovery result from Acompanhar locked top-5 parciais using the **same** confirmation dialog as Decidir (fixed destination **Promover a favorito tier 3**; no tier selector). The dialog SHALL open from the parciais Promover control. Cancel, Voltar, or overlay dismiss SHALL leave the candidate and the sweep unchanged. A `NO-GO` seal with sufficient sample SHALL NOT disable Promover (the seal is an alert only, same as Decidir). After confirmed promotion the parciais row SHALL show **Favorito tier 3**, SHALL keep its place in the top-5, and the active sweep SHALL continue (pause/cancel of the sweep are not implied). The same `result_id` on Decidir SHALL show the promoted state.

#### Scenario: Promote a NO-GO eligible partial while the sweep runs

- **GIVEN** a NO-GO eligible unique row in Acompanhar parciais and a non-terminal sweep
- **WHEN** the operator confirms Promover as tier 3
- **THEN** exactly one tier 3 favorite is created
- **AND** the row shows Favorito tier 3 and keeps its top-5 slot
- **AND** the sweep does not stop
- **AND** the NO-GO seal remains visible and did not block the click

#### Scenario: Cancel leaves the partial and the sweep untouched

- **GIVEN** the promotion dialog opened from a parciais Promover
- **WHEN** the operator cancels, goes Voltar, or dismisses the overlay
- **THEN** no favorite is created
- **AND** the candidate and the sweep stay as they were
