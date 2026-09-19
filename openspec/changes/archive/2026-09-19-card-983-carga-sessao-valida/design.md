## Context

Card **#983**, Status=Design. Incidente PROD 2026-09-18 ~22:55 BRT em `https://criptofarol.com.br/favorites`: a grade mostra «Não foi possível carregar as estratégias favoritas.» / «Carga falhou» / «Tentar de novo», com a copy «a sessão continua válida». Os favoritos **não foram apagados**. `GET /api/favorites/` 200 no backend; Caddy `aborting with incomplete response` (broken pipe / connection reset) — o browser não recebe o JSON e cai no erro do #970. No mesmo segundo, par **200+401**. «Tentar de novo» aborta o pedido anterior e gera mais corte. Mesmo padrão 2026-09-18 23:37 BRT na Carteira: rajada 401 em balances, login 200, depois par 200+401; Caddy 0 cortes em balances nessa janela.

**Vivo hoje (pós-#970 / #975, desta branch):**
- Dois caminhos de sessão no cliente: `axios` em `authStore.tsx` (arranque / `/auth/me` / refresh, AbortController 8s) e `authFetch` em `authFetch.ts` (páginas).
- `FavoritesDashboard`: `useQuery` + `authFetch` **sem** `signal`; `retry: false`; `isError` pinta o erro do #970 com «a sessão continua válida». `refetch()` em «Tentar de novo».
- `HomePage` `/home`: `fetchJson` é `fetch` cru com o token guardado — **sem** refresh em 401 — e o KPI pinta «Não foi possível carregar `/api/favorites`.».
- `MonitorStatusTab`: `resolveHasCryptoFavorites` chama `GET /favorites/`; falha marca `opportunitiesLoadError`. `MonitorDashboardTab` existe e **não** é montado.
- `ExternalBalancesPage`: segundo `load()` aos 320 ms (`minUsd`); `catch` grava erro **sem** guardar o `fetchId` — um 401 tardio sobrescreve um 200.

**Impeccable (Operate):** audience = administrador que abre Favoritos/Carteira/Monitor/Início com sessão a renovar; outcome = ver a lista/saldos, não erro falso; direction = clone das páginas vivas + delta de estados, sem redesign; `DESIGN.md` permanece autoridade visual.

Briefing = issue grelhado #983 (Problema, História, Entra, Não entra). Q1=A, Q2=A gravadas; não reabrir. Não alongar TTL. Não desfazer #970.

UI impact: affected
live_route: /favorites
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

Regiões clonadas: shell autenticado + workbench `/favorites` (`table.fav-strategies`, «Estratégias favoritas», «Symbol», «Estratégia», «Ações») no **index.html**. Irmão `erro.html` — falha real #970. Extras com copy visível: `/monitor` em `monitor.html`; Início `/home` em `inicio.html` (vivo da rota `/home`; index `/` redirecciona a `/monitor`); Carteira `/external/balances` em `carteira.html` (fora do catálogo de landmarks — clone da página viva, não emprestar `/favorites`) + `carteira-erro.html` para falha real. `COPIED:start`/`COPIED:end` nas regiões clonadas. Nunca um painel das N no index. Nunca ANTES/DEPOIS como URL canónica.

## Goals / Non-Goals

**Goals:**

- Janela de renovação + catálogo no servidor: `/favorites` lista os pares crypto; ausente o erro do #970 com «a sessão continua válida»; ausente catálogo vazio.
- «Tentar de novo» com catálogo intacto e sessão válida termina na lista. Um 200 que chegou ou vai chegar ganha de abort / 401 transitório.
- Sessão morta de verdade → login. Não fica na grade de erro fingindo que a sessão vale.
- Falha real de rede ou corpo inválido em Favoritos **continua** o erro do #970 + «Tentar de novo».
- Na mesma janela, Início mostra a estratégia no KPI; Monitor mostra `table.signals`; Carteira mostra os saldos.
- Falha real na Carteira continua «Erro ao carregar» / «Falha ao carregar saldos».
- Abrir gráfico / análise continua a ter velas e trades.

**Non-Goals:**

- Redesign da grade (colunas, mobile, Excel, tiers).
- Desfazer o #970 (vazio vs erro vs filtro; lista magra).
- Alongar a sessão / mudar quanto tempo o login dura.
- Apagar ou migrar favoritos.
- Discovery, promoção, métricas da grade.
- Falha de credenciais da exchange, Telegram ou «quem sou eu».
- Redesign de Início, Monitor ou Carteira.
- Ressuscitar `MonitorDashboardTab`.

## Decisions

1. **Renovação com catálogo no servidor é lista, não erro do #970.**
   Enquanto o refresh token ainda recupera o acesso, Favoritos pinta a grade. Alternativa «qualquer 401 → erro do #970 com “a sessão continua válida”» rejeitada: é o incidente. Alternativa «qualquer 401 → login» rejeitada: o par 200+401 no mesmo segundo ainda tem sessão útil. Alternativa «alongar TTL» rejeitada: fora do Entra.

2. **Um 200 que chegou (ou vai chegar) ganha do abort / 401 transitório.**
   «Tentar de novo» e um pedido a meio do caminho não deixam a tela no erro se a lista chegou ou está a chegar. Alternativa «o último pedido manda sempre, inclusive um 401/abort depois de um 200» rejeitada: é o furo da Carteira (`catch` sem `fetchId`) e o corte Caddy em Favoritos.

3. **Sessão morta ≠ 401 transitório.**
   Morta = refresh esgotado, sem acesso recuperável → login (já existente). Transitório = par 200+401 / abort / token a meio do refresh com catálogo no servidor → lista. Alternativa «ficar no erro do #970 a fingir que a sessão vale» rejeitada: Entra.

4. **Q1=A e Q2=A nas quatro superfícies, clone só onde a copy muda.**
   Favoritos canónico. Monitor extra: some a falha falsa da lista. Início extra `/home`: some «Não foi possível carregar `/api/favorites`.». Carteira extra: some «Erro ao carregar» / «Falha ao carregar saldos»; falha real continua esse erro (`carteira-erro.html`). Sem painel das N no index.

5. **Vocabulário (nasce aqui, não no issue).**
   - **Renovação:** janela em que o access token está a ser trocado; o refresh ainda vale.
   - **Falha falsa:** erro de carga com sessão recuperável e catálogo/saldos no servidor.
   - **Falha real:** rede cortada de verdade ou corpo inválido, sessão ainda viva.
   - **Sessão morta:** refresh esgotado; o operador vai ao login.
   - **200 que chegou (ou vai chegar):** payload de sucesso já em mão ou ainda em voo; ganha de abort/401 transitório.

## Risks / Trade-offs

- [Risco] Apply alonga TTL do login para «resolver» o 401 → Mitigação: Non-Goal explícito; o contrato é ganhar o 200, não durar mais a sessão.
- [Risco] Apply desfaz o #970 e volta a pintar vazio no erro → Mitigação: `erro.html` pina a copy do #970; spec ADDED não apaga vazio vs filtro vs erro.
- [Risco] Um 401 transitório na Carteira continua a sobrescrever o 200 (`catch` sem `fetchId`) → Mitigação: decisão 2; P3 o helper, contrato visível é «saldos visíveis».
- [Risco] `HomePage.fetchJson` sem refresh continua a pintar o KPI de erro na renovação → Mitigação: extra `inicio.html`; Apply alinha o caminho de sessão da lista ao das páginas.
- [Risco] Extra vira painel ANTES/DEPOIS no index → Mitigação: index = clone `/favorites` + lista; irmãos/extras são URLs próprias.
- [Risco] Apply ressuscita `MonitorDashboardTab` (AbortController no unmount de `/favorites/`) → Mitigação: P3; o vivo é `MonitorStatusTab`.

## Migration Plan

Sem migração de schema e sem backfill. Rollback = reverter o tratamento de 401/abort nas quatro superfícies. Favoritos gravados não se apagam. TTL do login não muda.

## Apply contract

Apply lê este `design.md` e o HTML em `frontend/public/prototypes/card-983-carga-sessao-valida/` como spec de layout. Sem HTML neste arquivo. Sem editar produto neste filho de Design.

**Contrato visível (não P3):**

- `/favorites` feliz (`index.html`): filtros Todos, pares `SOL/USDT` e `ETH/USDT`; footer «2 estratégias carregadas»; **ausente** «Não foi possível carregar as estratégias favoritas.»; **ausente** «Nenhuma estratégia favorita encontrada».
- `/favorites` falha real (`erro.html`): copy do #970 + «Tentar de novo»; chrome Favoritos; **ausente** catálogo vazio; URL continua no proto (não login). «Tentar de novo» aponta à lista.
- `/monitor` (`monitor.html`): landmarks `table.signals` + Status/Preço/Distância/7d/Risco até stop/Tags/Operar/Par / Estratégia; **ausente** «Não foi possível carregar as estratégias.»; **ausente** «Nenhum ativo disponível no monitor».
- `/home` (`inicio.html`): KPI «Melhor estratégia (7d)» com estratégia visível; **ausente** «Não foi possível carregar `/api/favorites`.».
- `/external/balances` (`carteira.html`): saldos visíveis; **ausente** «Erro ao carregar» / «Falha ao carregar saldos».
- Carteira falha real (`carteira-erro.html`): «Erro ao carregar» + «Falha ao carregar saldos».
- Análise/gráfico de um favorito continua a ter velas e trades (Apply, não o proto estático).

**Bug vivo (contrato no Design; correção no Apply, não neste filho):**

- Dois caminhos de sessão (`authStore` axios vs `authFetch`) + `HomePage.fetchJson` sem refresh.
- Abort/401 transitório pinta o erro do #970 com «a sessão continua válida» embora o backend tenha listado 200.
- «Tentar de novo» / segundo fetch pode abortar um 200 a meio do caminho (Caddy incomplete response).
- Carteira: `catch` de `load()` ignora `fetchId` e um 401 tardio tapa o 200.

**P3 — detalhe de Apply (aceito aqui, não reabrir como P0/P1):**

- Unificar `authFetch` / axios / `fetchJson` vs fila única de refresh.
- Passar `AbortSignal` do React Query e **não** tratar abort como `isError` se um 200 está em voo.
- Guardar `fetchId` no `catch` da Carteira; cancelar o debounce de `minUsd` no primeiro paint.
- `MonitorDashboardTab` morto: não ressuscitar.
- Testids `favorites-renewal-ok` / `wallet-renewal-ok` / `wallet-load-error`.
- Detector `side-tab` ×2 nos cards mobile de tier — incumbente do clone #970, não redesenhar.
- Alvos 44px no «Tentar de novo».

## Prototype

- Canónico: `https://dev.criptofarol.com.br/prototypes/card-983-carga-sessao-valida/` → `frontend/public/prototypes/card-983-carga-sessao-valida/index.html`. Clone da página viva `/favorites` + delta do caminho feliz da renovação (grade com pares crypto). Landmarks: `table.fav-strategies`, «Estratégias favoritas», «Symbol», «Estratégia», «Ações». `COPIED:start`/`COPIED:end` no clone.
- Irmão erro: `https://dev.criptofarol.com.br/prototypes/card-983-carga-sessao-valida/erro.html` — mesmo clone + delta falha real #970.
- Extra monitor: `https://dev.criptofarol.com.br/prototypes/card-983-carga-sessao-valida/monitor.html`.
- Extra início: `https://dev.criptofarol.com.br/prototypes/card-983-carga-sessao-valida/inicio.html` (vivo `/home`).
- Extra carteira: `https://dev.criptofarol.com.br/prototypes/card-983-carga-sessao-valida/carteira.html` + `carteira-erro.html`.
- `cp`/clone = copied; delta dos estados = generated.
- Sem painel ANTES/DEPOIS como URL canónica.
- Digest, desktop/mobile e bytes copied vs generated: ver `## Prototype Validation`.

## Prototype Validation

- **Comando:** `python3 .impeccable/critique/983-autor-gate.py` — Playwright Chromium (`executable_path=/usr/bin/chromium-browser`, `--no-sandbox`), preview local da pasta `frontend/public`. Não `curl` contra DEV (worktree ≠ `environments.dev.source`). Evidência: `.impeccable/critique/983-autor-gate.json`.
- **URLs locais:** canónico `…/prototypes/card-983-carga-sessao-valida/` (`index.html`); irmão `…/erro.html`; extras `…/monitor.html`, `…/inicio.html`, `…/carteira.html`, `…/carteira-erro.html`.
- **Viewports:** desktop 1280×800 + mobile 390×844, `colorScheme: dark`. Screenshots: `983-index-desktop-1280x800.png`, `983-index-mobile-390x844.png`, `983-erro-desktop-1280x800.png`, `983-erro-mobile-390x844.png`, `983-monitor-desktop-1280x800.png`, `983-monitor-mobile-390x844.png`, `983-inicio-desktop-1280x800.png`, `983-inicio-mobile-390x844.png`, `983-carteira-desktop-1280x800.png`, `983-carteira-mobile-390x844.png`, `983-carteira-erro-desktop-1280x800.png`, `983-carteira-erro-mobile-390x844.png`.
- **Ações / asserts (index):** landmarks `table.fav-strategies`, «Estratégias favoritas», «Symbol», «Estratégia», «Ações»; linhas SOL/USDT e ETH/USDT; **ausente** o erro do #970; **ausente** catálogo vazio.
- **Ações / asserts (erro):** copy #970 + «Tentar de novo»; ausente catálogo vazio; URL continua no proto.
- **Ações / asserts (monitor):** landmarks `table.signals` + Status/Preço/Distância/7d/Risco até stop/Tags/Operar/Par / Estratégia; ausente falha falsa da lista.
- **Ações / asserts (inicio):** KPI «Melhor estratégia (7d)» com estratégia; ausente o erro falso da lista.
- **Ações / asserts (carteira):** saldos BTC/ETH; ausente «Erro ao carregar».
- **Ações / asserts (carteira-erro):** «Erro ao carregar» + «Falha ao carregar saldos».
- **Resultado do autor:** **PASS** · FAIL 0. Pai após A/B: HTTPS DEV == disco IDENTICAL (`criptofarol-dev-prototypes.service` restart); Assessment A/B PASS. Detector Impeccable: `side-tab` ×2 no clone dos cards de tier — P3 incumbente, não redesenhar.
- **Digest (UTF-8 sha256, gate deste autor):**
  - `index.html` `54a581b7cbe2015d2e1b092f43ca6b2a5b98414b8eb9dad49171a7ca9cc34145` · 43556 B = 7781 copied + 35775 generated. Pares `COPIED:start`/`COPIED:end`: 4/4. T5 mede só este index.html.
  - `erro.html` `aff6abcdb57fd4267fd61945adb0d8a307e3b2c7ecdcc14a18d6c96a1fa51d19` · 33720 B = 7729 copied + 25991 generated.
  - `monitor.html` `51e5ee44f8833d254ef843bbf7893fc2657a36d7a12d476015adb0179856ee9e` · 31034 B = 21504 copied + 9530 generated.
  - `inicio.html` `48892e62a63666d741676e23e6d139fcdd89a9b3e579cc81cd773d6af0cf196a` · 14478 B = 8806 copied + 5672 generated.
  - `carteira.html` `6808e6cc9fde934f137d217b7c0fbc77b1efacadd56f8181d3c17686f6dcf6d4` · 16549 B = 10819 copied + 5730 generated.
  - `carteira-erro.html` `0b44d6a49bc09afc5250eb8de66741c4c3d28cab341391ac88a27dedf0b54f53` · 15197 B = 10819 copied + 4378 generated.

## Open Questions

Nenhuma. Fronteira veio grelhada do issue #983 (Q1=A, Q2=A).

## Design Critique

Com-tela. Teto 1+1+1: autor + dupla + 1 rework. Dupla PASS; P0/P1 nenhum; sem rework. P3 aceitos (Apply, não reabrir).

**P0:** nenhum  
**P1:** nenhum  
**P3 (aceitos):** «Todas 2» no `erro.html`; KPIs de sucesso em `carteira-erro.html`; retry `<a href=index.html>` vs `refetch`; `role=alert` ×2; clip Monitor 1280/1440 e busca 390; `side-tab` ×2 cards mobile de tier; truncagem Estratégia 1440; thead/cards 390; mobilebar SOL no monitor; `DELTA:start=0`; Apply `authFetch`/`fetchId`; `MonitorDashboardTab` morto; chrome «Crypto» no extra Início.

**Disposition:** P3 → Apply. Não reabrir Q1=A, Q2=A, #970 nem alongar TTL.

**Snapshots:** `.impeccable/critique/983-card-983-carga-sessao-valida-assessment-A.md` · `.impeccable/critique/983-card-983-carga-sessao-valida-assessment-B.md`

**Design Agent verdict:** PASS

- Autor: [design-autor 983](ba4e5ac0-0fb7-416f-9f4c-d5eb8e726366) isolado; `model: cursor-grok-4.6-high`.
- Assessment A: [Assessment A 983](6f476c41-511a-4dee-b3d6-4cc8c43ed211) isolado; `model: cursor-grok-4.6-high`. **PASS**.
- Assessment B: [Assessment B 983](a7b684ab-6d9d-4ad7-8069-5b4f54bb0588) isolado; `model: cursor-grok-4.6-high`. **PASS**. digest_match yes.

`proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)`  
`proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`  
`proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)`

