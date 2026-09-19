## Why

Em DEV (2026-09-18 ~18:07 BRT) o operador abriu `/monitor` com 18 favoritos crypto visíveis na mesma sessão e o quadro mostrou **Nenhum ativo disponível no monitor**. `GET /api/favorites/` 200 com as 18 linhas; `GET /api/opportunities/?tier=1,2,3` (primeira carga, sem recomputar) 200 com lista vazia. O #970 cobriu Favoritos; este card corrige a causa no Monitor.

## Problema

O operador abre o Monitor com favoritos crypto já salvos e o quadro não carrega os sinais (vazio falso), mesmo com a lista de Favoritos visível na mesma sessão.

## História

Como operador que usa Favoritos e Monitor no dia a dia, quero ver no Monitor os sinais das estratégias crypto que já estão nos Favoritos (e um erro claro se a análise falhar), para escolher o que acompanhar sem achar que o Monitor está vazio ou partido.

## Entra

- Com sessão válida e favoritos crypto visíveis em `/favorites`, `/monitor` **não** mostra «Nenhum ativo disponível no monitor» só porque a análise ainda não chegou ou falhou.
- «Nenhum ativo disponível no monitor» só quando, de facto, esta sessão não tem par crypto nos Favoritos.
- Se a análise do Monitor falhar (rede, sessão, resposta inválida ou análise que não devolveu sinais havendo favoritos), o operador vê **erro de carga** explícito e uma acção para **tentar de novo**, e permanece em `/monitor`.
- A primeira visita a `/monitor` com favoritos crypto visíveis nesta sessão já mostra os sinais ou um erro de carga. O operador não precisa de um segundo clique só para o quadro deixar de estar vazio.
- Recarregar a tela, na mesma sessão com os mesmos favoritos, não deixa o Monitor preso num vazio falso.
- Se a análise chegou mas um filtro (Na carteira, busca, estrela, estratégia, tempo) esconde todos os sinais, a tela diz que **não há resultado com estes filtros** — não usa o texto de catálogo vazio.
- Abrir um sinal no gráfico / análise **continua** a mostrar velas e trades. Este card não tira a análise; tira o Monitor a fingir catálogo vazio.
- Favoritos em `/favorites` permanece a listar as estratégias crypto já salvas (sem regressão do #970).
- O texto actual do erro de carga do Monitor permanece («Não foi possível carregar as estratégias.» com «A lista de favoritos não chegou. Isto não significa que não há estratégias.»). Este card corrige a causa (o quadro não carregar / fingir vazio), não o wording do erro.

## Não entra

- Reabrir ou alterar o contrato da lista magra de Favoritos (#970).
- Mudar o filtro default do Monitor (Na carteira vs Todos) como decisão de produto à parte.
- Conta sem favoritos: o vazio verdadeiro de catálogo continua vazio.
- Alterar o texto do erro de carga do Monitor.

## What Changes

Decisões gravadas (não reabrir): Q2=A — a primeira visita a `/monitor` com favoritos crypto visíveis já mostra sinais **ou** erro de carga; sem segundo clique só para o quadro deixar de estar vazio. Texto de erro actual do Monitor **fica**. Cobertura parcial 11/18 é *como* técnico (design.md / spec), não Q nova de produto.

- `/monitor` distingue **sinais carregados**, **erro de carga**, **filtro sem resultado** e **catálogo vazio real** (sessão sem par crypto nos Favoritos).
- Primeira visita (e recarregar) com favoritos crypto visíveis: o quadro mostra sinais ou o erro de carga actual — nunca «Nenhum ativo disponível no monitor» por cache vazio, timeout silencioso ou análise que devolveu `[]` havendo favoritos.
- `GET /api/opportunities/?tier=1,2,3` na primeira carga **computa** (ou falha de forma visível). Não serve 200 com lista vazia como catálogo vazio quando a sessão tem favoritos crypto.
- Análise parcial (subset analisável, incidente: 11 de 18) **mostra os sinais que chegaram**. Não exige 18/18 no quadro e não inventa superfície «7 de fora».
- Filtro que esconde todos os sinais já carregados usa «Não há resultado com estes filtros.» — não o texto de catálogo vazio.
- Copy de erro do Monitor não muda. Layout Status / Preço / Distância / 7d / Tags / Operar / Par / Estratégia não muda. Filtro default Na carteira vs Todos não muda. `#970` não reabre.

## Capabilities

### New Capabilities

- `monitor-first-load`: contrato visível da primeira visita a `/monitor` com favoritos crypto — sinais ou erro de carga, nunca vazio falso; recarregar não prende o quadro; filtro ≠ catálogo vazio; subset analisável aparece.

### Modified Capabilities

- `monitor`: sucesso 200 com lista vazia **não** MAY pintar «Nenhum ativo disponível no monitor» quando a sessão tem par crypto nos Favoritos; esse caso é erro de carga (copy actual). Catálogo vazio só sem favoritos crypto. Sem redesign da board.
- `opportunity-monitor`: a primeira `GET /api/opportunities/` da visita (sem `refresh` do operador) não devolve catálogo vazio cacheado/timeout quando o utilizador tem favoritos crypto; computa ou falha. Payload vazio com favoritos crypto não é sucesso de catálogo.

## Impact

- Frontend: `MonitorStatusTab.tsx` — o ramo `length===0 && !loading` deixa de tratar 200 vazio como catálogo sem ativos quando há favoritos crypto; erro de carga (copy actual + Tentar de novo) cobre análise que não devolveu sinais havendo favoritos. Filtro sem linhas usa copy de filtro, não catálogo vazio. Sem redesign. `MonitorDashboardTab` permanece morto.
- Backend: `GET /api/opportunities/` (`opportunity_routes.py` cache in-memory 30s/600s stale + `OpportunityService._calculate_opportunities` timeout de fetch 8s). Não gravar nem servir `[]` como catálogo fresco/stale quando o utilizador tem favoritos crypto. Primeira carga sem `refresh=true` do operador já computa ou falha. Skips (delist / sem velas / timeout) do subset não-analisável ficam fora do quadro sem UI nova.
- Favoritos `/favorites` e lista magra do #970: sem mudança de copy nem de contrato.
- Protótipo: clone `/monitor` (canónico, caminho feliz com sinais) + irmão `erro.html` (copy actual). Sem extra `/favorites`. Sem painel ANTES/DEPOIS no index.
