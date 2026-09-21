## ADDED Requirements

### Requirement: Monitor scalp module gains a rolling 15 min lookback without redesigning the board or Operar

Authenticated `/monitor` SHALL keep hosting the existing Scalp BTCUSDT module on the workbench. This card SHALL add the «últimos 15 min» lookback fact, hurdle, fee, default target 35 bp, default stop −28 bp, open position after fill, last-trade result and «posição presa» inside that module. The board columns and Operar market-click flow SHALL remain. This card SHALL NOT restyle opportunity cards, signal states, or the Operar confirmation modal. This card SHALL NOT add a catalog route and SHALL NOT change landing or Ajuda copy. This card SHALL NOT add a 1 / 2 / 5 minute horizon selector. This card SHALL NOT show «Jev no máximo 1 vez / 15 min». This card SHALL NOT add Monitor copy of the 1.5 s send-wait cap.

#### Scenario: Board and Operar stay

- **WHEN** the 15 min lookback delta is present on `/monitor`
- **THEN** `table.signals` SHALL still expose Status, Preço, Distância, 7d, Risco até stop, Tags, Operar and Par / Estratégia
- **AND** the Operar control SHALL still open the existing confirmed MARKET flow
- **AND** turning the scalp on SHALL NOT remove or replace that Operar control

#### Scenario: Not a new surface

- **WHEN** the user looks for the lookback
- **THEN** it SHALL be on `/monitor` inside the existing Scalp BTCUSDT module as the fact «últimos 15 min»
- **AND** SHALL NOT require a new nav destination
- **AND** SHALL NOT be a radio 1/2/5
- **AND** SHALL NOT say «1 vez / 15 min»
