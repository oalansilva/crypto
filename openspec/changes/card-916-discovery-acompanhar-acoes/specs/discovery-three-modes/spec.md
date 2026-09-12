## ADDED Requirements

### Requirement: Acompanhar parciais expose Promover and Excluir

Acompanhar locked top-5 parciais SHALL show an **Ação** column using the same `action-stack` pattern as Decidir: **Promover** and **Excluir** on each eligible row. The controls SHALL be available whenever the parciais table is visible (sweep **em curso**, **pausada**, or **recuperada** after F5). Acompanhar SHALL remain a top-5: it SHALL NOT become the full leaderboard, SHALL NOT add pagination, and SHALL NOT add filters. Montar SHALL keep Preflight and Rascunho without this card's action-column delta. Decidir's existing Promover/Excluir SHALL remain unchanged.

Low-sample, duplicate, and already-promoted rows SHALL use the same visible blocks as Decidir (Promover blocked/absent with the same reason; Excluir follows the same rules; already promoted SHALL NOT offer Excluir). `insufficient_sample` SHALL NOT appear in the top-5. Action on one tab SHALL update the same `result_id` on the other.

#### Scenario: Operator acts on a visible partial without changing tab

- **GIVEN** Acompanhando with locked parciais visible (sweep running, paused, or recovered)
- **WHEN** the operator looks at an eligible row
- **THEN** they see Promover and Excluir without opening Decidir
- **AND** the table still shows at most five ranked candidates

#### Scenario: Top-5 does not become the full list

- **GIVEN** the operator wants the complete leaderboard
- **WHEN** they are on Acompanhando
- **THEN** the parciais stay a top-5
- **AND** the full list, pagination, and filters remain on Decidir

#### Scenario: Montar has no action-column delta

- **GIVEN** the operator is on Montar
- **WHEN** they edit the draft or read Preflight
- **THEN** rascunho and preflight are unchanged
- **AND** there is no candidate action column in Montar
