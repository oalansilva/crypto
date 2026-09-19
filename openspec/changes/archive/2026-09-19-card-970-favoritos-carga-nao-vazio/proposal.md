## Why

Em PROD (2026-09-17 ~21:16 BRT) o administrador abriu `/favorites`, viu **Carregando estratégias...** e em seguida **Nenhuma estratégia favorita encontrada** / **0 estratégias carregadas**, com filtros em Todos — embora o catálogo crypto estivesse intacto (169 estratégias, 63 pares). A tela trata falha de carga como catálogo vazio.

## Problema

O administrador abre Favoritos em produção, espera o carregamento, e a tela diz que não há estratégias — mesmo com dezenas de favoritos crypto salvos. Parece que o catálogo sumiu.

## História

Como administrador que abre Favoritos no dia a dia, quero ver as estratégias crypto que já estão salvas (e um erro claro se a carga falhar), para escolher o que entra no Monitor sem achar que perdi o catálogo.

## Entra

- Com sessão válida e favoritos crypto gravados, `/favorites` mostra essas linhas — não 0 filtradas / «Nenhuma estratégia favorita encontrada».
- O caso do incidente: conta do administrador, filtros em Todos, dezenas de pares `*/USDT` no catálogo. Depois de abrir a tela, a grade lista esses pares.
- «Carregando estratégias...» termina em lista ou em **erro de carga** explícito. Falha de rede, sessão ou resposta inválida **não** usa o texto de catálogo vazio.
- No erro de carga em Favoritos, com sessão ainda válida, o operador vê uma ação para **tentar carregar de novo** e permanece na tela — não vai ao login.
- «Nenhuma estratégia favorita encontrada» só quando, de fato, não há par crypto na lista (filtros em Todos, busca vazia).
- Se há pares crypto no catálogo mas a busca ou um filtro (par, estratégia, tempo, estrela, direção) esconde todos, a tela diz que **não há resultado com estes filtros** — não usa o texto de catálogo vazio.
- Se a sessão caiu, o operador vai para login — não fica numa grade vazia fingindo que não há favoritos.
- Abrir o gráfico / análise de um favorito **continua** a mostrar velas e trades. Este card não tira a análise; tira o peso morto da **grade**.
- Favoritos que não são par crypto (ex.: ação sem `/`) continuam de fora da grade, como hoje.
- No Início e no Monitor, falha ao carregar a lista de favoritos **não** aparece como «não há estratégias» / catálogo vazio: o operador vê que a carga falhou.

## Não entra

- Redesign da grade (colunas, mobile, Excel, tiers).
- Apagar ou migrar favoritos antigos de ação.
- Novo modelo de login / duração de sessão como produto (só o caso em que Favoritos mente «vazio» com sessão morta ou a meio do refresh).
- Discovery, promoção a favorito, ou métricas da grade (cards #897, #948, #935).
- Redesign de Início ou Monitor (layout, KPIs, fluxo). Só o tratamento de falha da lista de favoritos: não fingir que não há estratégias.

## What Changes

Decisões gravadas (não reabrir): Q1=A — texto diferente quando a busca/filtro esconde todos os pares; «Nenhuma estratégia favorita encontrada» só no catálogo mesmo vazio (Todos, busca vazia). Q2=A — no erro de carga em Favoritos, com sessão ainda válida, ação para tentar carregar de novo; permanece na tela, não vai ao login. Q3=B — qualquer sítio onde o operador vê a lista de favoritos (Favoritos, Início `/home` e Monitor `/monitor`) deixa de tratar falha como «não há estratégias».

- `/favorites` distingue **lista carregada**, **erro de carga**, **filtro sem resultado** e **catálogo vazio**.
- Com sessão válida e pares crypto gravados, filtros Todos e busca vazia, a grade lista esses pares — não 0 filtradas / texto de catálogo vazio.
- Falha de rede, 401 após refresh com sessão ainda válida, corpo inválido ou parse falho **não** usam «Nenhuma estratégia favorita encontrada». Mostram erro de carga + **Tentar de novo**; o operador permanece em Favoritos.
- Sessão morta continua a ir ao login (já existente); não é modelo novo de sessão.
- A grade deixa de puxar o peso morto das velas (~48 MB no incidente); abrir gráfico/análise **continua** a mostrar velas e trades.
- Início: falha da lista **não** aparece como «Nenhuma estratégia favoritada» (já separado no vivo; este card pina o contrato).
- Monitor: falha ao carregar a lista derivada de favoritos **não** aparece como «Nenhum ativo disponível no monitor» / «não há estratégias».

## Capabilities

### New Capabilities

- `favorites-load-states`: contrato visível dos estados da lista de favoritos — caminho feliz com pares crypto, erro de carga + tentar de novo, filtro sem resultado, catálogo vazio real, sessão morta → login — em Favoritos, Início e Monitor.

### Modified Capabilities

- `favorites`: a lista `GET /favorites/` é resumo da grade (sem histórico de velas embutido); «Carregando estratégias...» só enquanto essa lista corre; `isError` / corpo inválido não colapsam no texto de catálogo vazio; análise aberta a partir da linha continua a ter velas e trades.
- `home`: o KPI da lista de favoritos já separa erro («Não foi possível carregar `/api/favorites`.») de «Nenhuma estratégia favoritada»; este card pina essa distinção (Q3=B) sem redesign do Início.
- `monitor`: falha ao carregar a lista que alimenta `/monitor` não usa o vazio «Nenhum ativo disponível no monitor»; o operador vê que a carga falhou. Sem redesign de layout, KPIs ou fluxo.

## Impact

- Frontend: `FavoritesDashboard.tsx` (estados da query + copy de vazio vs filtro vs erro + retry); `HomePage.tsx` (verificar que o KPI não regride); `MonitorStatusTab.tsx` (primeiro load de `/opportunities/` não colapsa em vazio de catálogo). `MonitorDashboardTab.tsx` está morto no vivo (`MonitorPage` só monta `MonitorStatusTab`); Apply não o ressuscita.
- Backend: `GET /api/favorites/` deixa de embutir `metrics.analysis_candles` (e séries históricas equivalentes) na lista da grade; velas/trades continuam em `GET /api/favorites/{id}/trades` e no fluxo de análise. Sem migração de linhas, sem apagar favoritos de ação.
- Protótipo: clone `/favorites` (canónico, caminho feliz) + irmãos `erro.html` / `filtro.html` + extra `/monitor` (`monitor.html`). Sem extra `/home` (copy de falha do Início não muda). Sem painel ANTES/DEPOIS no index.
