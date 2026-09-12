## ADDED Requirements

### Requirement: Walk-forward GO/NO-GO seal on Acompanhar parciais and Decidir rows

When a Discovery result has a persisted walk-forward verdict (`oos_verdict.status` of `GO` or `NO-GO`), Acompanhar locked top-5 parciais and the Decidir leaderboard row SHALL show that verdict as a visible seal on the line itself. The operator SHALL NOT need to open the chart, expand «+ detalhes», or click Promover to see it. Missing verdict SHALL omit the seal (no invented `GO`). `NO-GO` is not `Baixa amostra` and not `Amostra insuficiente`. Promover on an eligible `NO-GO` SHALL remain available (this card does not lock the click). Seals use distinct chips: `GO` informational, `NO-GO` danger — not the amber sample badges.

#### Scenario: NO-GO visible on parciais without opening the chart

- **GIVEN** ALPHA/USDT `RS-B109ED2C80` with `oos_verdict.status = NO-GO`
- **WHEN** the line appears in Acompanhar parciais
- **THEN** the seal/text `NO-GO` is visible on that row
- **AND** the operator did not open the graph and did not promote

#### Scenario: GO and NO-GO visible on Decidir

- **GIVEN** a completed sweep with at least one `GO` and one `NO-GO`
- **WHEN** the administrator opens Decidir
- **THEN** each row with a verdict shows its `GO` or `NO-GO` seal
- **AND** Promover remains on the eligible `NO-GO` row

#### Scenario: Sample badges stay distinct

- **GIVEN** a `NO-GO` eligible row next to a `Baixa amostra` row
- **WHEN** both are visible on Decidir
- **THEN** the first seal is `NO-GO` and the second is `Baixa amostra`
- **AND** neither reuses the other's words
