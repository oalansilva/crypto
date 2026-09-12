## ADDED Requirements

### Requirement: Acompanhar top-5 shows the same six metric columns

Acompanhar parciais (top-5) SHALL show the same six metric columns as Decidir, visible without expanding a row: Calmar, Max DD, Trades/cobertura, Sharpe, Win%, and CAGR. CAGR SHALL be the scan's annualized return, not Favorites accumulated Return. Acompanhar SHALL NOT add a «+ detalhes» control in this change. Montar SHALL keep Preflight and Rascunho without a candidate grid and without this card's column delta.

#### Scenario: Partials show six columns

- **GIVEN** the operator is on Acompanhar with locked partials
- **WHEN** they look at the top-5 without expanding a row
- **THEN** each row shows Calmar, Max DD, Trades/cobertura, Sharpe, Win%, and CAGR in columns
- **AND** the set of metric columns matches Decidir

#### Scenario: Montar has no candidate grid delta

- **GIVEN** the operator is on Montar
- **WHEN** they edit the draft or read Preflight
- **THEN** rascunho and preflight are unchanged
- **AND** there is no candidate metrics grid in Montar

## MODIFIED Requirements

### Requirement: Decidable leaderboard

O leaderboard SHALL ter 1 controle de ordenação + 6 colunas de métrica visíveis por padrão (Calmar, Max DD, Trades/cobertura, Sharpe, Win%, CAGR), restante (B&H, Δ B&H, PF, mercado, janela) em expansão por linha; página SHALL ser 10–15 por página; filtros SHALL NOT re-perguntar o rascunho; evidência (janela, candles, fees) SHALL permanecer visível; rank global SHALL NOT renumerar sob filtro/paginação. Ordenação SHALL continuar Calmar (default) e CAGR vs B&H; Sharpe, Win% e CAGR SHALL NOT ser chaves de ordenação neste change.

#### Scenario: Compare candidates

- **WHEN** comparo candidatos no leaderboard
- **THEN** vejo 1 ordenação + 6 colunas de métrica por padrão, resto em expansão, paginando 10–15 por página, com rank global estável
- **AND** Sharpe, Win% e CAGR estão nas colunas, não só atrás de «+ detalhes»

### Requirement: Decidir row for amostra insuficiente

The Decidir leaderboard SHALL show `insufficient_sample` rows in the list: rank displayed as `—`, visible seal `Amostra insuficiente` (same words as the progress bag; not `Baixa amostra`), Calmar / Max DD / Trades/cobertura / Sharpe / Win% / CAGR as `N/A`, and no Promover CTA. The row SHALL NOT appear in Acompanhar top-5 partials. Existing `Baixa amostra` rows SHALL keep their current promote-disabled control and MAY keep finite metric values.

#### Scenario: Operator reads which pairs lacked history

- **WHEN** the operator opens Decidir after a sweep that cut short listings
- **THEN** each cut combination has a list row with seal `Amostra insuficiente`, rank `—`, and N/A metrics including Sharpe, Win%, and CAGR
- **AND** there is no Promover button on that row
- **AND** an eligible neighbor still shows Promover
