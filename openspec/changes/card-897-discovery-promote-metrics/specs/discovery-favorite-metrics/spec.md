## ADDED Requirements

### Requirement: Grade de Favoritos lê o snapshot da promoção

The Favorites grid SHALL render Sharpe, Trades, Win%, Return and Max DD of a discovery-promoted favorite from the **snapshot da promoção**, using the same keys the grid already reads today. Those values SHALL be the numbers of the discovery train window the administrator just saw, not of a terceiro backtest on current candles. Profit Factor SHALL appear in the advanced column when the discovery result already had it. Empty placeholders (`-` / `0` from a missing key) SHALL NOT be shown when the snapshot has those numbers.

#### Scenario: Newly promoted discovery favorite fills the grid

- **WHEN** an administrator promotes an eligible discovery candidate whose snapshot has Sharpe, negócios, win rate, retorno and Max DD
- **THEN** the GET payload that `/favorites` already reads contains those values
- **AND** the grid row shows them filled (not `-` / `0` from absence)
- **AND** the numbers match the snapshot, not a terceiro backtest

#### Scenario: Incident #193 numbers are visible without promoting again

- **WHEN** the grade loads an already-promoted discovery favorite whose snapshot already has the numbers (including `#193`: Sharpe 0,31, 30 negócios, win 46,7%, retorno +16.951%, Max DD 16,5%)
- **THEN** Sharpe, Trades, Win%, Return and Max DD appear filled from that snapshot
- **AND** the administrator does not need to promote again

#### Scenario: Opening the chart does not wipe the grid

- **WHEN** the administrator opens the gráfico of that discovery-promoted favorite
- **THEN** the same row on `/favorites` keeps the snapshot numbers
- **AND** the grid does not replace them with another silent backtest

### Requirement: Resumo da análise vem do snapshot

The analysis summary on `/combo/results` (retorno, acerto, Max DD, negócios) for a discovery-promoted favorite SHALL come from the snapshot da promoção. Max DD SHALL NOT render as «Indisponível» when the snapshot has Max DD.

#### Scenario: Analysis summary matches the promotion snapshot

- **WHEN** the administrator opens the gráfico of a discovery-promoted favorite whose snapshot has retorno, acerto, Max DD and negócios
- **THEN** the resumo da análise shows those snapshot values
- **AND** Max DD is not «Indisponível»

### Requirement: Janela rotulada when the trades list is not the summary window

If the list of operações on the chart remains on current candles (a different window from the snapshot), the UI SHALL label both windows so the operator cannot confuse current-candle trades with discovery-train trades.

#### Scenario: Current-candle trades list is labeled apart from the summary

- **WHEN** the analysis summary shows the snapshot window (ex.: 30 negócios da Descoberta) and the trades list shows current candles (ex.: 12 negócios)
- **THEN** the summary window is labeled as the discovery train / snapshot window
- **AND** the trades list window is labeled as velas atuais
- **AND** the two labels are distinct and visible without opening a tooltip

### Requirement: Combo-saved favorites keep today's contract

A favorite saved from Combo (not Descoberta) SHALL keep the current grid and analysis contract. This card SHALL NOT change those keys, persistence, or summary derivation for combo-saved rows.

#### Scenario: Combo-saved row is unchanged

- **WHEN** the grade renders a favorite that was saved from Combo, not from Descoberta
- **THEN** Sharpe, Trades, Win%, Return and Max DD follow the existing combo-saved contract
- **AND** opening its gráfico does not apply the discovery snapshot or janela-rotulada rules of this card
