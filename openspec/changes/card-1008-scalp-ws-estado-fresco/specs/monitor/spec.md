## ADDED Requirements

### Requirement: Scalp panel shows livro indisponível when the book is not fresh

The Scalp BTCUSDT module already on authenticated `/monitor` SHALL show the exact copy «livro indisponível» when the scalp is ligado and the shared book stream is down or the touch `age_ms` is greater than 500. The per-user switch SHALL remain Ligado. The module SHALL NOT add a new catalog route. The module SHALL NOT live inside Operar. Existing visual states `off`, `on`, `kill` and `nokey` SHALL remain. This card SHALL NOT redesign the switch, T, clip, kill banner, board, or Operar.

#### Scenario: Stream down while scalp is on

- **WHEN** the authenticated user has the scalp ligado
- **AND** the BTCUSDT book stream is down or the touch is older than 500 ms
- **THEN** the scalp status line on `/monitor` SHALL show «livro indisponível»
- **AND** the switch SHALL remain Ligado
- **AND** `table.signals` SHALL still expose Status, Preço, Distância, 7d, Risco até stop, Tags, Operar and Par / Estratégia

#### Scenario: Book returns while scalp stays on

- **WHEN** the scalp is still ligado
- **AND** the in-memory touch is fresh (`age_ms` ≤ 500)
- **THEN** the status line SHALL NOT show «livro indisponível» as the live copy
- **AND** the switch SHALL remain Ligado

#### Scenario: Off kill and nokey stay as they are

- **WHEN** the module is desligado, parado por kill, or sem chave Spot
- **THEN** those states SHALL keep their existing copy and controls
- **AND** this card SHALL NOT restyle the switch, T, clip, or kill banner
