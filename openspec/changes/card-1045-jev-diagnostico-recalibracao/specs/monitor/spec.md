## ADDED Requirements

### Requirement: Monitor scalp module shows the Jev diagnosis without a new route

Authenticated `/monitor` SHALL keep hosting the existing Scalp BTCUSDT module. That module SHALL show the last closed-day diagnosis on the first view in beginner-trader phrases: the date, that the data serves this reading, the period, the confidence in force (including its version), the last decision, and the reason. A history of those decisions SHALL be on the same module, in those phrases. The module SHALL offer pause of the automatic adjustment and a way back to the previous version. The first view SHALL NOT require the on-screen labels break-even, homogeneidade or bp. The scalp switch, T, clip, kill, board and Operar SHALL remain. Enabling the automatic adjustment SHALL NOT turn the scalp switch on and SHALL NOT send an order. This card SHALL NOT add a catalog route and SHALL NOT change landing or Ajuda copy. The canonical surface SHALL NOT be a grid of outcome cards.

#### Scenario: The diagnosis sits on the existing scalp module

- **WHEN** an authenticated user opens `/monitor` after a closed-day diagnosis exists
- **THEN** the Scalp BTCUSDT module SHALL show, in beginner-trader phrases, the date, that the data serves this reading, the period, the confidence in force, the last decision, the reason, pause, revert and the history
- **AND** the first view SHALL NOT require the labels break-even, homogeneidade or bp
- **AND** `table.signals` SHALL still expose Status, Preço, Distância, 7d, Risco até stop, Tags, Operar and Par / Estratégia
- **AND** the Operar control SHALL still open the existing confirmed MARKET flow

#### Scenario: Calibration does not press the scalp switch

- **WHEN** automatic calibration is enabled or a confidence version is applied
- **THEN** the per-user scalp switch SHALL stay as the user left it
- **AND** no order SHALL be sent solely because calibration was enabled

#### Scenario: Not a new surface

- **WHEN** the user looks for the diagnosis
- **THEN** it SHALL be on `/monitor` inside the existing Scalp BTCUSDT module
- **AND** SHALL NOT require a new nav destination
