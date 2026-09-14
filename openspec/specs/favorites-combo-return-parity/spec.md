# favorites-combo-return-parity Specification

## Purpose
TBD - created by archiving change card-935-favorites-combo-return. Update Purpose after archive.
## Requirements
### Requirement: Grade, resumo e Ver Trades da mesma linha mostram o mesmo composto canónico

When a Favorites row already displays a RETURN value, the analysis summary opened from that row **and** the Monitor **Ver Trades** modal (`ChartModal` `viewMode='trades'` → `StrategyTradesTable` card «Retorno total») of that same filled line SHALL show the same **retorno composto canónico**. Canonical is the large compound already contracted (#193 / #897): ratio 169,51 and percentage-points 16951 read as **+16.951%** (sixteen thousand), not 169,51%. On the 2026-09-13 incident (SOL/USDT 1d, «Médias Móveis: Tendência Confirmada») all **three** surfaces SHALL read **~+98.591%**, not 985,85%. The heuristic `|value| > 1 ⇒ already a percent` SHALL NOT shrink a compound return greater than 100%. `StrategyTradesTable` SHALL NOT print `(total_return * 100)` when `total_return` is already the large compound (ratio ~985,91 or points ~98591). This SHALL apply to any origin (combo-saved or Descoberta) whenever the number is already visible and the unit breaks.

#### Scenario: Incident SOL/USDT shows the large compound on all three surfaces

- **WHEN** the administrator opens the analysis of the Favorites row whose RETURN is +98.591,56% (SOL/USDT 1d, «Médias Móveis: Tendência Confirmada», Sharpe 0,45, 32 trades, win 68,75%, Max DD 14,15%)
- **THEN** «Retorno total» of the resumo da análise is the same large compound (~+98.591%), not ~985,85%
- **AND** Sharpe, acerto, Max DD and n de negócios of the resumo continue to match the grade

#### Scenario: Monitor Ver Trades shows the same large compound

- **WHEN** the administrator opens **Ver Trades** on `/monitor` for that same SOL/USDT 1d line
- **THEN** the «Retorno total» card of `StrategyTradesTable` is the same large compound (~+98.591%), not ~985,85%
- **AND** acerto and n de operações match the grade (68,75% and 32)

#### Scenario: Contract #193 / #897 sixteen-thousand percent

- **WHEN** grade, resumo and Monitor Ver Trades of the same line show return for the contracted pair razão 169,51 / pontos 16951
- **THEN** all three read as sixteen thousand percent (+16.951%), not 169,51%

#### Scenario: Compound under 100% does not regress on any of the three surfaces

- **WHEN** a Favorites row already shows RETURN +35% (compound < 100%) and the administrator opens the analysis or Monitor Ver Trades of that line
- **THEN** the resumo and the Ver Trades «Retorno total» continue ~+35%
- **AND** it does not become 0,35% and does not become 3.500%

#### Scenario: Back to favorites keeps the large compound

- **WHEN** the administrator uses «Voltar aos favoritos» after opening the incident analysis
- **THEN** the grade still shows the same large compound RETURN as before

### Requirement: This card does not fill missing metrics or change other summary fields

A Favorites row from Descoberta **without** Sharpe/RETURN on the grade is out of scope (#897). Sharpe, acerto, Max DD and n already matching the grade SHALL NOT be changed. The 32 vs 33 gap between resumo/grade and the chart trade list SHALL remain out of scope. Monitor Status, Preço, Distância, tags and Operar SHALL NOT be redesigned.

#### Scenario: Missing discovery metrics stay #897

- **WHEN** a Descoberta row has no Sharpe/RETURN on the grade
- **THEN** this card SHALL NOT treat filling that empty as acceptance
- **AND** that hole remains #897

#### Scenario: Matching summary fields stay matching

- **WHEN** the incident analysis resumo already shows acerto, Max DD and n equal to the grade
- **THEN** those fields remain equal
- **AND** this card does not retune them to “fix” the return

#### Scenario: Monitor table chrome stays as-is

- **WHEN** the administrator uses Ver Trades on `/monitor`
- **THEN** Status, Preço, Distância, 7d, Risco até stop, Tags and Operar remain the live table
- **AND** this card does not restyle or relabel those columns

