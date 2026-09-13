## ADDED Requirements

### Requirement: Persisting a terceiro backtest must not overwrite snapshot keys

When the system regenerates trades on current candles for a discovery-promoted favorite and persists that result, it SHALL NOT replace the snapshot da promoção on the keys the Favorites grid and the analysis summary already read (Sharpe, negócios, win rate, retorno, Max DD, and Profit Factor when present). Regenerated trades and candles MAY be stored for the chart list. Provenance and the complete snapshot SHALL remain.

#### Scenario: Opening analysis persists current-candle trades without wiping the grid keys

- **WHEN** an authorized user opens the gráfico of a discovery-promoted favorite that has no saved trades list and the system reruns on velas atuais
- **THEN** the persisted payload may include the regenerated trades for the list
- **AND** Sharpe, Trades, Win%, Return and Max DD on the keys the grade reads remain the snapshot values
- **AND** a subsequent GET of the favorite still fills the grade from the snapshot

#### Scenario: Regenerated metrics do not become the analysis summary

- **WHEN** the terceiro backtest returns different numbers (ex.: 12 negócios, retorno negativo, Max DD ausente)
- **THEN** the resumo da análise still uses the snapshot
- **AND** Max DD in the resumo is not «Indisponível» if the snapshot has Max DD
