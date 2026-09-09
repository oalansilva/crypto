## ADDED Requirements

### Requirement: Acompanhar progress shows four bags

The Acompanhar progress line SHALL render `N processadas = X sucesso + Y falha + Z ignoradas + W amostra insuficiente` using the reconciled sweep counters. The fourth term SHALL use the exact words `amostra insuficiente`. The line SHALL remain a single scannable formula (no extra legend required). Limits copy («8 global · 1 por sweep · fila justa») SHALL NOT change.

#### Scenario: Fourth term visible while running

- **WHEN** the operator is in Acompanhar with a live sweep that has insufficient-sample combinations
- **THEN** the progress line includes `amostra insuficiente` as the fourth addend
- **AND** those combinations are not counted inside `sucesso` or `ignoradas`

### Requirement: Decidir row for amostra insuficiente

The Decidir leaderboard SHALL show `insufficient_sample` rows in the list: rank displayed as `—`, visible seal `Amostra insuficiente` (same words as the progress bag; not `Baixa amostra`), Calmar / Max DD / Trades/cobertura as `N/A`, and no Promover CTA. The row SHALL NOT appear in Acompanhar top-5 partials. Existing `Baixa amostra` rows SHALL keep their current promote-disabled control.

#### Scenario: Operator reads which pairs lacked history

- **WHEN** the operator opens Decidir after a sweep that cut short listings
- **THEN** each cut combination has a list row with seal `Amostra insuficiente`, rank `—`, and N/A metrics
- **AND** there is no Promover button on that row
- **AND** an eligible neighbor still shows Promover
