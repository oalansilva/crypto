## MODIFIED Requirements

### Requirement: Walk-forward GO/NO-GO seal on Acompanhar parciais and Decidir rows

When a Discovery result is ranking-eligible and has a persisted walk-forward verdict (`oos_verdict.status` of `GO` or `NO-GO`) from the Discovery criteria profile, Acompanhar locked top-5 parciais and the Decidir leaderboard row SHALL show that verdict as a visible seal on the line itself. The operator SHALL NOT need to open the chart, expand «+ detalhes», or click Promover to see it. Missing verdict SHALL omit the seal (no invented `GO`).

A row with `eligibility=low_sample` (`Baixa amostra`) or `eligibility=insufficient_sample` (`Amostra insuficiente`) SHALL show only the sample badge: it SHALL NOT show `GO` or `NO-GO`, even if holdout Sharpe is ≤ 0 or a Combo-era `oos_verdict` is present. `NO-GO` is not `Baixa amostra` and not `Amostra insuficiente`.

Promover on an eligible `NO-GO` SHALL remain available (this card does not lock the click). Seals use distinct chips: `GO` informational, `NO-GO` danger — not the amber sample badges. The same seal rule SHALL apply to every visible line (4h and 1d, long and short, any template).

When the seal is `NO-GO`, the line SHALL also show a readable reason that names the segment (`Treino` vs `Holdout`), the observed value and the threshold. A training-portrait failure SHALL point at treino, not only holdout.

#### Scenario: NO-GO visible on parciais without opening the chart

- **GIVEN** an eligible row with Discovery `oos_verdict.status = NO-GO` because holdout Sharpe ≤ 0
- **WHEN** the line appears in Acompanhar parciais
- **THEN** the seal/text `NO-GO` is visible on that row
- **AND** the reason identifies Holdout, observed Sharpe and threshold `> 0`
- **AND** the operator did not open the graph and did not promote

#### Scenario: GO and NO-GO visible on Decidir

- **GIVEN** a completed sweep with at least one Discovery `GO` (example BTC/USDT 1d long `RS-E0E30719CC`) and one `NO-GO`
- **WHEN** the administrator opens Decidir
- **THEN** each eligible row with a verdict shows its `GO` or `NO-GO` seal
- **AND** Promover remains on the eligible `NO-GO` row

#### Scenario: Weak training portrait reason points at treino

- **GIVEN** an eligible Decidir row with holdout Sharpe > 0 whose in-sample portrait fails Calmar 1, profit factor 1,5 or max drawdown 35%
- **WHEN** the operator reads the line
- **THEN** the seal is `NO-GO`
- **AND** the visible reason identifies Treino, the observed value and the threshold
- **AND** the reason is not only Holdout

#### Scenario: Sample badges stay distinct and have no GO/NO-GO

- **GIVEN** a `NO-GO` eligible row next to a `Baixa amostra` row whose holdout Sharpe is ≤ 0
- **WHEN** both are visible on Decidir
- **THEN** the first seal is `NO-GO` and the second is `Baixa amostra`
- **AND** the `Baixa amostra` row has no `GO` and no `NO-GO`
- **AND** neither reuses the other's words

#### Scenario: 4h and short use the same seal

- **GIVEN** eligible 4h and short rows in the same Decidir grid
- **WHEN** the operator reads the seals
- **THEN** each row shows `GO` or `NO-GO` by the same Discovery profile as 1d long
