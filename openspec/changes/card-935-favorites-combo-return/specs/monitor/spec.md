## ADDED Requirements

### Requirement: Ver Trades Retorno total matches the Favorites compound of the same line

When `/monitor` opens **Ver Trades** for a row whose Favorites RETURN is already visible, the ChartModal (`viewMode='trades'`) `StrategyTradesTable` card «Retorno total» SHALL show the same canonical large compound as the grade (incident SOL/USDT 1d «Médias Móveis: Tendência Confirmada»: ~+98.591%, not 985,85%). Acerto and n de operações SHALL match the grade. The formatter MUST NOT always print `(displayMetrics.total_return * 100)` when `GET /favorites/{id}/trades` already passed `payload.metrics` in mixed units. Status, Preço, Distância, tags and Operar SHALL remain untouched.

#### Scenario: Incident SOL Ver Trades shows the large compound

- **WHEN** the administrator clicks Ver Trades on the Monitor row SOL/USDT 1d «Médias Móveis: Tendência Confirmada» whose Favorites RETURN is +98.591,56%
- **THEN** the modal card «Retorno total» reads the same large compound (~+98.591%), not ~985,85%
- **AND** taxa de acerto and total de operações match the grade (68,75% and 32)

#### Scenario: Compound under 100% does not regress in Ver Trades

- **WHEN** the administrator opens Ver Trades for a Monitor row whose Favorites RETURN is +35%
- **THEN** «Retorno total» remains ~+35%
- **AND** it does not become 0,35% and does not become 3.500%
