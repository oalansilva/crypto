# discovery-three-modes — Delta Spec

## ADDED Requirements

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

O leaderboard SHALL ter 1 controle de ordenação + 3 colunas de risco visíveis por padrão (Calmar, Max DD, Trades/cobertura), restante em expansão por linha; página SHALL ser 10–15 por página; filtros SHALL NOT re-perguntar o rascunho; evidência (janela, candles, fees) SHALL permanecer visível; rank global SHALL NOT renumerar sob filtro/paginação.

#### Scenario: Compare candidates

- **WHEN** comparo candidatos no leaderboard
- **THEN** vejo 1 ordenação + 3 colunas de risco por padrão, resto em expansão, paginando 10–15 por página, com rank global estável.

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
