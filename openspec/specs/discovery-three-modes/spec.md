# discovery-three-modes Specification

## Purpose
TBD - created by archiving change card-852-descoberta-tres-modos. Update Purpose after archive.
## Requirements
### Requirement: One mode visible at a time

A tela SHALL exibir exatamente 1 dos 3 modos por vez: `Montar` (sem sweep ativo), `Acompanhando #X` (sweep não-terminal em curso), `Decidir` (sweep terminal escolhido ou histórico).

#### Scenario: Montar sem sweep ativo

- **WHEN** abro `/combo/discovery` sem varredura ativa
- **THEN** vejo só o modo `Montar` (rascunho editável + preflight 3 linhas), sem UUID/hash/token/fórmula no caminho feliz.

#### Scenario: Iniciar colapsa rascunho e trava leaderboard

- **WHEN** o início da varredura conclui
- **THEN** o rascunho colapsa, o modo vira `Acompanhando #X` e o leaderboard fica travado nesse sweep.

### Requirement: Human preflight (3 lines + impediments)

O preflight SHALL mostrar `N combinações · ~T estimado · janela/período` em até 3 linhas e, quando bloqueado, SHALL listar o que falta fazer (ex.: reduzir escopo, escolher 1 timeframe). Detalhe técnico (fórmula bruta, snapshot/hash/token/chave) SHALL ficar em bloco expansível fora do caminho feliz.

#### Scenario: Blocked names the fix

- **WHEN** o preflight está bloqueado (escopo vazio ou acima do limite)
- **THEN** a tela lista 1+ impedimentos acionáveis em linguagem de operação, sem JSON técnico.

### Requirement: Decidable leaderboard

O leaderboard SHALL ter 1 controle de ordenação + 6 colunas de métrica visíveis por padrão (Calmar, Max DD, Trades/cobertura, Sharpe, Win%, CAGR), restante (B&H, Δ B&H, PF, mercado, janela) em expansão por linha; página SHALL ser 10–15 por página; filtros SHALL NOT re-perguntar o rascunho; evidência (janela, candles, fees) SHALL permanecer visível; rank global SHALL NOT renumerar sob filtro/paginação. Ordenação SHALL continuar Calmar (default) e CAGR vs B&H; Sharpe, Win% e CAGR SHALL NOT ser chaves de ordenação neste change.

#### Scenario: Compare candidates

- **WHEN** comparo candidatos no leaderboard
- **THEN** vejo 1 ordenação + 6 colunas de métrica por padrão, resto em expansão, paginando 10–15 por página, com rank global estável
- **AND** Sharpe, Win% e CAGR estão nas colunas, não só atrás de «+ detalhes»

### Requirement: Full-history default period (ajuste Alan 2026-09-07)

O preset default do seletor de período SHALL ser `Todo o histórico` (histórico completo); as opções menores (`Últimos 2 anos`, `Últimos 6 meses`) SHALL continuar disponíveis. O preflight default SHALL refletir o histórico cheio (`N combinações · ~T estimado · todo o histórico + datas da janela`, ex.: `24 combinações · ~2h 24min estimado · todo o histórico [01 jan 2017, 01 jan 2026)`); o rótulo do CTA default SHALL ser `Iniciar varredura — N, ~T` do histórico cheio. Trocar o preset SHALL atualizar preflight, CTA e rascunho congelado. Sem mudança de motor.

#### Scenario: Default is full history

- **WHEN** abro o modo `Montar` sem tocar no seletor de período
- **THEN** vejo `Todo o histórico` selecionado, preflight com `N combinações · ~T · todo o histórico + datas da janela` e CTA `Iniciar varredura — N, ~T` do histórico cheio; opções menores seguem selecionáveis.

### Requirement: Inline selection, modal as advanced edit

Seleção de templates/símbolos comuns SHALL funcionar inline (busca + contador + marcar/desmarcar, sem modal). O modal atual SHALL existir só como "edição avançada" com exatamente **2 ações de eixo inteiro** e visíveis: `Selecionar todos` (marca todos os itens do eixo) e `Limpar seleção` (desmarca tudo). O escopo filtrado SHALL NOT ter ação própria na edição avançada (filtro + marcar/desmarcar permanecem resolvíveis inline); a edição avançada opera o eixo inteiro. O contador do modal SHALL refletir a seleção ao vivo; o contador inline SHALL refletir a seleção após Aplicar.

#### Scenario: Common selection without modal

- **WHEN** busco e marco templates/símbolos comuns
- **THEN** não preciso abrir modal; o modal só aparece como "edição avançada".

#### Scenario: Advanced edit whole-axis actions (ajuste Alan 2026-09-07)

- **WHEN** abro a edição avançada e clico `Selecionar todos`
- **THEN** todos os itens do eixo ficam marcados, o contador do modal atualiza (`X de N`), e após Aplicar o contador inline reflete o total do eixo; `Limpar seleção` desmarca tudo. `Selecionar todos`/`Limpar seleção` são as únicas ações da edição avançada — não há ação de escopo filtrado (`Selecionar filtrados`/`Limpar`).

### Requirement: Stable start CTA with named block

O botão iniciar SHALL ter rótulo estável `Iniciar varredura — N, ~T` e SHALL ser a ação dominante do modo Montar. Com sweep em curso, o bloqueio SHALL nomear a diferença: mesmo escopo ("existe varredura igual em curso — ver progresso") vs outro escopo ("há outra em curso — conclua ou cancele"), com link "ver progresso".

#### Scenario: Other sweep running names the difference

- **WHEN** há varredura em curso e tento iniciar outra
- **THEN** vejo qual é a diferença (mesmo escopo vs outro escopo) e o link "ver progresso".

### Requirement: Promotion with side-by-side risk summary

O modal de promoção SHALL mostrar lado a lado retorno, queda máxima, trades, cobertura e janela, mais destino Tier 3 e "onde ver depois" (favoritos; reversível via descarte do favorito, sem apagar histórico do sweep).

#### Scenario: Promote shows risk summary

- **WHEN** clico Promover e o modal abre
- **THEN** vejo retorno, queda máxima, trades, cobertura e janela lado a lado, com destino Tier 3 e onde ver depois.

### Requirement: Short hidden until data exists

`short` SHALL NOT aparecer no caminho feliz do rascunho nem dos filtros do leaderboard até haver dados que o justifiquem; quando aparecer, SHALL ser consistente nos dois lugares.

#### Scenario: Short stays out of the happy path

- **WHEN** abro o rascunho ou os filtros do leaderboard sem dados de short
- **THEN** não vejo `short` em nenhum dos dois lugares.

### Requirement: No regression on focus, evidence, destructive copy

Foco/armadilhas de modal/rótulos SHALL manter o padrão atual; janela, cobertura e rank estável SHALL ser preservados; copy de escopo destrutivo (cancelar/excluir) SHALL ser preservada. Descartar por linha, estados dedup (`duplicate`/`already_promoted`), bloco 409, nota de revalidação sob lock, painel 403, bloco stale e sessão expirada do vivo SHALL ser preservados fora do switch de modos (não pertencem a nenhum dos 3 modos; o protótipo os omite como mock de delta).

#### Scenario: Destructive and evidence states survive the mode switch

- **WHEN** navego entre Montar, Acompanhar e Decidir com um sweep em curso
- **THEN** Descartar por linha, dedup/409, revalidação sob lock, 403, stale e sessão expirada continuam presentes fora dos modos, e foco, janela, cobertura e rank estável não regredem.

### Requirement: Acompanhar progress shows four bags

The Acompanhar progress line SHALL render `N processadas = X sucesso + Y falha + Z ignoradas + W amostra insuficiente` using the reconciled sweep counters. The fourth term SHALL use the exact words `amostra insuficiente`. The line SHALL remain a single scannable formula (no extra legend required). Limits copy («8 global · 1 por sweep · fila justa») SHALL NOT change.

#### Scenario: Fourth term visible while running

- **WHEN** the operator is in Acompanhar with a live sweep that has insufficient-sample combinations
- **THEN** the progress line includes `amostra insuficiente` as the fourth addend
- **AND** those combinations are not counted inside `sucesso` or `ignoradas`

### Requirement: Decidir row for amostra insuficiente

The Decidir leaderboard SHALL show `insufficient_sample` rows in the list: rank displayed as `—`, visible seal `Amostra insuficiente` (same words as the progress bag; not `Baixa amostra`), Calmar / Max DD / Trades/cobertura / Sharpe / Win% / CAGR as `N/A`, and no Promover CTA. The row SHALL NOT appear in Acompanhar top-5 partials. Existing `Baixa amostra` rows SHALL keep their current promote-disabled control and MAY keep finite metric values.

#### Scenario: Operator reads which pairs lacked history

- **WHEN** the operator opens Decidir after a sweep that cut short listings
- **THEN** each cut combination has a list row with seal `Amostra insuficiente`, rank `—`, and N/A metrics including Sharpe, Win%, and CAGR
- **AND** there is no Promover button on that row
- **AND** an eligible neighbor still shows Promover

### Requirement: Walk-forward GO/NO-GO seal on Acompanhar parciais and Decidir rows

When a Discovery result has a persisted walk-forward verdict (`oos_verdict.status` of `GO` or `NO-GO`), Acompanhar locked top-5 parciais and the Decidir leaderboard row SHALL show that verdict as a visible seal on the line itself. The operator SHALL NOT need to open the chart, expand «+ detalhes», or click Promover to see it. Missing verdict SHALL omit the seal (no invented `GO`). `NO-GO` is not `Baixa amostra` and not `Amostra insuficiente`. Promover on an eligible `NO-GO` SHALL remain available (this card does not lock the click). Seals use distinct chips: `GO` informational, `NO-GO` danger — not the amber sample badges.

#### Scenario: NO-GO visible on parciais without opening the chart

- **GIVEN** ALPHA/USDT `RS-B109ED2C80` with `oos_verdict.status = NO-GO`
- **WHEN** the line appears in Acompanhar parciais
- **THEN** the seal/text `NO-GO` is visible on that row
- **AND** the operator did not open the graph and did not promote

#### Scenario: GO and NO-GO visible on Decidir

- **GIVEN** a completed sweep with at least one `GO` and one `NO-GO`
- **WHEN** the administrator opens Decidir
- **THEN** each row with a verdict shows its `GO` or `NO-GO` seal
- **AND** Promover remains on the eligible `NO-GO` row

#### Scenario: Sample badges stay distinct

- **GIVEN** a `NO-GO` eligible row next to a `Baixa amostra` row
- **WHEN** both are visible on Decidir
- **THEN** the first seal is `NO-GO` and the second is `Baixa amostra`
- **AND** neither reuses the other's words

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

