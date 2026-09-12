# analysis-complete-trade-history Specification

## Purpose
TBD - created by archiving change card-917-historico-completo-analise. Update Purpose after archive.
## Requirements
### Requirement: Analysis chart markers match the full trade list

On `/combo/results` (análise aberta pelos Favoritos ou após Combo), the chart SHALL mark every operation in the analysis trade list on the corresponding candle: entry, and exit when the operation is closed. The marker source SHALL be that list, not the Monitor's recent `signal_history` recorte. Lista and gráfico SHALL tell the same story: no list operation without a marker, and no operation marker without a list operation.

#### Scenario: Closed trades get entry and exit markers

- **WHEN** an analysis has N operations in the list and candles that cover those dates
- **THEN** each operation has an entry marker on the entry candle
- **AND** each closed operation also has an exit marker on the exit candle

#### Scenario: No orphan markers

- **WHEN** the same analysis is open
- **THEN** there is no operation marker that does not correspond to a list row

#### Scenario: Any asset and timeframe

- **WHEN** the operator opens analysis for another asset or timeframe on the same screen
- **THEN** the same 1:1 list↔chart contract holds
- **AND** the gap is not BTC-only

#### Scenario: Summary operations count matches closed list rows

- **WHEN** the analysis summary shows Operações
- **THEN** that number matches the closed rows of the list

### Requirement: Initial zoom stays recent while full history stays on the series

The default chart viewport MAY stay on the recent recorte (~180 velas) for candle readability. Older operations SHALL remain on the series and SHALL become visible when the operator zooms out, pans, or uses Menos. Resetar SHALL restore the recent recorte without dropping old markers from the series. The screen SHALL NOT force all candles visible on open.

#### Scenario: Older BTC 1d operations appear after zoom out

- **WHEN** BTC 1d (or equivalent) has list operations before 05/01/26
- **AND** the operator uses Menos, pans, or otherwise reveals those candles
- **THEN** the old Compra/Venda arrows appear on those candles

#### Scenario: Reset keeps history on the series

- **WHEN** the operator clicks Resetar after zooming out
- **THEN** the recent recorte returns
- **AND** the old arrows remain on the series (they do not disappear)

#### Scenario: Opening does not fit all candles

- **WHEN** the analysis has thousands of candles
- **THEN** the initial view stays on the recent recorte
- **AND** the page SHALL NOT force every candle into the first viewport

