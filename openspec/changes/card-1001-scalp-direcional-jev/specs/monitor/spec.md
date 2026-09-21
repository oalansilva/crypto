## ADDED Requirements

### Requirement: Monitor hosts the directional scalp module without redesigning Operar

`/monitor` SHALL host the per-user Scalp BTCUSDT module on the existing authenticated workbench. The board columns and Operar market-click flow SHALL remain. This card SHALL NOT restyle opportunity cards, signal states, or the Operar confirmation modal.

#### Scenario: Board and Operar stay

- **WHEN** the scalp module is present on `/monitor`
- **THEN** `table.signals` SHALL still expose Status, Preço, Distância, Tags, Operar and Par / Estratégia
- **AND** the Operar control SHALL still open the existing confirmed MARKET flow
- **AND** turning the scalp on SHALL NOT remove or replace that Operar control
