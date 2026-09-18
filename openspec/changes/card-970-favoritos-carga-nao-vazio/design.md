## Context

Card **#970**, Status=Design. Incidente PROD 2026-09-17 ~21:16 BRT em `https://criptofarol.com.br/favorites`: **Carregando estratégias...** e em seguida **Nenhuma estratégia favorita encontrada** / **0 estratégias carregadas**, filtros Todos. Banco intacto (169 estratégias, 63 pares crypto). `GET /api/favorites/` 200; PATCH 119/194/195/196 no intervalo. A grade puxava velas (~48 MB). No mesmo segundo 200 e 401. Favoritos não foram apagados.

**Vivo hoje:** `FavoritesDashboard` só ramifica `isLoading` vs `filteredFavorites.length === 0`. Erro de rede, 401 após refresh, corpo inválido e `[]` caem no mesmo texto de vazio. `useQuery` não lê `isError`. Par crypto = símbolo com `/`. Velas/trades da análise só deveriam ir ao abrir o gráfico; o peso vai embutido na lista. Sessão morta já manda a `/login` (`ProtectedRoute` / `authFetch` + `notifyAuthSessionCleared`). Início (`HomePage`) já separa erro («Não foi possível carregar `/api/favorites`.») de «Nenhuma estratégia favoritada». O `/monitor` vivo monta `MonitorStatusTab` (`GET /opportunities/`); no primeiro load falho, `opportunities=[]` pinta «Nenhum ativo disponível no monitor» (toast de erro não basta). `MonitorDashboardTab` existe no repo e **não** é montado.

**Impeccable (Operate):** audience = administrador que abre Favoritos no dia a dia para escolher o que entra no Monitor; outcome = ver os pares crypto gravados, ou um erro de carga com tentar de novo, sem achar que o catálogo sumiu; direction = clone da página viva `/favorites` + delta dos estados da lista, sem redesign da grade; `DESIGN.md` permanece autoridade visual.

Briefing = issue grelhado #970 (Problema, História, Entra, Não entra). Decisões Q1=A, Q2=A, Q3=B gravadas; não reabrir.

UI impact: affected
live_route: /favorites
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

Regiões clonadas: shell autenticado + workbench `/favorites` (`table.fav-strategies`, «Estratégias favoritas», «Symbol», «Estratégia», «Ações») no **index.html**. Extra 1: `/monitor` em `monitor.html` (`table.signals`, Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia) + delta falha da lista. Irmãos de Favoritos: `erro.html`, `filtro.html` — nunca no index. Início `/home` está fora do catálogo de clone; a copy de falha do KPI **não muda** — sem irmão extra. `COPIED:start`/`COPIED:end` nas regiões clonadas. Nunca um painel das N no index. Nunca ANTES/DEPOIS como URL canónica.

## Goals / Non-Goals

**Goals:**

- Caminho feliz: sessão válida, favoritos crypto gravados, filtros Todos, busca vazia → a grade lista esses pares.
- Erro de carga: «Carregando estratégias...» termina em erro explícito + «Tentar de novo»; permanece em Favoritos; não usa texto de catálogo vazio; não vai ao login se a sessão ainda é válida.
- Filtro sem resultado: há pares crypto mas busca/filtro esconde todos → «Não há resultado com estes filtros.»
- Vazio real: «Nenhuma estratégia favorita encontrada» só quando não há par crypto (Todos, busca vazia).
- Sessão morta → login.
- Abrir gráfico/análise de um favorito continua a mostrar velas e trades.
- Início e Monitor: falha da lista não aparece como «não há estratégias».

**Non-Goals:**

- Redesign da grade (colunas, mobile, Excel, tiers).
- Apagar ou migrar favoritos antigos de ação.
- Novo modelo de login / duração de sessão.
- Discovery / promoção / métricas (#897, #948, #935).
- Redesign de Início ou Monitor (layout, KPIs, fluxo).
- Ressuscitar `MonitorDashboardTab`.

## Decisions

1. **Quatro estados visíveis na grade, não um vazio só.**
   Loading enquanto `GET /favorites/` corre. Sucesso com pares → linhas. `isError` / corpo não-array / parse falho → erro + retry. Sucesso, catálogo crypto vazio, Todos + busca vazia → texto de catálogo vazio. Sucesso, catálogo com pares, filtro esconde todos → texto de filtro (Q1=A). Alternativa «um único empty» rejeitada: é o incidente.

2. **Retry na tela se a sessão ainda é válida (Q2=A).**
   `refetch()` da query; o operador permanece em `/favorites`. 401 que **esvazia** a sessão continua a ir ao login pelo shell já existente. Alternativa «qualquer 401 → login» rejeitada: o incidente tinha 200 e 401 no mesmo segundo com sessão ainda útil.

3. **A lista é resumo; a análise continua pesada.**
   `GET /api/favorites/` deixa de embutir `metrics.analysis_candles` (e séries históricas equivalentes) em cada linha. Velas/trades continuam em `GET /api/favorites/{id}/trades` + market candles ao abrir o gráfico. Alternativa «paginar a lista com velas» rejeitada: redesign da grade. Alternativa «não mexer no payload» rejeitada: ~48 MB na grade é o peso morto do incidente.

4. **Q3=B nas três superfícies, clone só onde a copy muda.**
   Favoritos: copy nova (erro + filtro). Monitor: primeiro load falho deixa de usar «Nenhum ativo disponível no monitor» — extra `monitor.html`. Início: copy de falha já está certa; Apply só verifica regressão — sem extra `/home`, sem `live_route` emprestada.

5. **Copy de filtro e de erro é operador, não path de API.**
   Erro Favoritos: «Não foi possível carregar as estratégias favoritas.» + «Tentar de novo». Filtro: «Não há resultado com estes filtros.» Início mantém «Não foi possível carregar `/api/favorites`.» Monitor: «Não foi possível carregar as estratégias.» (já no toast; passa a ser o estado da board). Alternativa «reusar a copy do Início na grade» rejeitada: a grade não é um KPI.

## Risks / Trade-offs

- [Risco] Tirar velas da lista quebra o open rápido da análise → Mitigação: o fluxo de análise já pede `/favorites/{id}/trades` e market candles; o spec existente já pede lista-resumo sem séries históricas por linha.
- [Risco] `[]` 200 genuíno vs parse falho → Mitigação: só `isSuccess` + `Array.isArray` + length 0 (após filtro crypto) é vazio; corpo inválido é erro.
- [Risco] Retry com sessão morta a meio do refresh → Mitigação: se `notifyAuthSessionCleared` disparar, o shell manda a `/login`; se a sessão continuar, retry fica.
- [Risco] Apply redesenha Monitor ao tratar o vazio → Mitigação: só o ramo `opportunities.length === 0 && !loading` após falha; Status/Preço/Distância/tags/Operar intocados.
- [Risco] Extra `/home` nasce por analogia → Mitigação: proibido; copy do Início não muda.

## Migration Plan

Sem migração de schema e sem backfill. Rollback = reverter o ramo de estados no frontend e o strip de `analysis_candles` no `GET /`. Favoritos gravados não se apagam nem se convertem.

## Apply contract

Apply lê este `design.md` e o HTML em `frontend/public/prototypes/card-970-favoritos-carga-nao-vazio/` como spec de layout. Sem HTML neste arquivo. Sem editar produto neste filho de Design.

**Contrato visível (não P3):**

- `/favorites` feliz: filtros Todos, busca vazia, pares `SOL/USDT` e `ETH/USDT` na grade; footer «2 estratégias carregadas»; **ausente** «Nenhuma estratégia favorita encontrada»; **ausente** «0 estratégias carregadas» como único resultado.
- `/favorites` erro (`erro.html`): «Não foi possível carregar as estratégias favoritas.» + «Tentar de novo»; chrome Favoritos; **ausente** texto de catálogo vazio; **ausente** login.
- `/favorites` filtro (`filtro.html`): busca `ZZZ`, «Não há resultado com estes filtros.»; **ausente** «Nenhuma estratégia favorita encontrada».
- `/monitor` (`monitor.html`): «Não foi possível carregar as estratégias.»; **ausente** «Nenhum ativo disponível no monitor».
- Análise/gráfico de um favorito continua a ter velas e trades (Apply, não o proto estático).

**Bug vivo (contrato no Design; correção no Apply, não neste filho):**

- `FavoritesDashboard` não lê `isError`; `filteredFavorites.length === 0` cobre falha e vazio.
- `GET /api/favorites/` devolve `metrics.analysis_candles` na lista (~48 MB no incidente).
- `MonitorStatusTab`: catch do fetch não impede o empty «Nenhum ativo disponível no monitor» no primeiro load.

**P3 — detalhe de Apply (aceito aqui, não reabrir como P0/P1):**

- Nome do helper / flag `isError` vs `status === 'error'` vs `Array.isArray`.
- Strip só `analysis_candles` vs também `trades[]` / séries de transparência na lista, desde que a grade fique resumo e a análise continue.
- `MonitorDashboardTab` morto: não ressuscitar; o vivo é `MonitorStatusTab`.
- Contadores do header (Todas N) no estado de erro.
- Detector `side-tab` ×2 nos cards mobile de tier — incumbente do clone.
- Truncagem desktop do nome longo na coluna Estratégia.
- Alvos 44px no «Tentar de novo».
- Testids `favorites-load-error` / `favorites-filter-empty` / `monitor-load-error`.

## Prototype

- Canónico: `https://dev.criptofarol.com.br/prototypes/card-970-favoritos-carga-nao-vazio/` → `frontend/public/prototypes/card-970-favoritos-carga-nao-vazio/index.html`. Clone da página viva `/favorites` + delta do caminho feliz (grade com pares crypto). Landmarks: `table.fav-strategies`, «Estratégias favoritas», «Symbol», «Estratégia», «Ações». `COPIED:start`/`COPIED:end` no clone.
- Irmão erro: `https://dev.criptofarol.com.br/prototypes/card-970-favoritos-carga-nao-vazio/erro.html` — mesmo clone + delta erro de carga + Tentar de novo.
- Irmão filtro: `https://dev.criptofarol.com.br/prototypes/card-970-favoritos-carga-nao-vazio/filtro.html` — mesmo clone + delta «Não há resultado com estes filtros.»
- Extra monitor: `https://dev.criptofarol.com.br/prototypes/card-970-favoritos-carga-nao-vazio/monitor.html` — clone `/monitor` + delta falha da lista. Sem extra `/home`.
- `cp`/clone = copied; delta dos estados = generated.
- Sem painel ANTES/DEPOIS como URL canónica.
- Digest, desktop/mobile e bytes copied vs generated: ver `## Prototype Validation`.

## Prototype Validation

- **Comando:** `xvfb-run -a python3 .impeccable/critique/970-autor-gate.py` — Playwright Chromium headed (`executable_path=/usr/bin/chromium-browser`, `--no-sandbox`). Não `curl` (curl só para digest HTTPS==disco). Evidência: `.impeccable/critique/970-autor-gate.json`.
- **URLs:** canónico `https://dev.criptofarol.com.br/prototypes/card-970-favoritos-carga-nao-vazio/` (`index.html`); irmãos `…/erro.html`, `…/filtro.html`; extra `…/monitor.html`. Disco == HTTPS (sha256 abaixo).
- **Viewports:** desktop 1280×800 + mobile 390×844, `colorScheme: dark`. Screenshots: `970-index-desktop-1280x800.png`, `970-index-mobile-390x844.png`, `970-erro-desktop-1280x800.png`, `970-erro-mobile-390x844.png`, `970-filtro-desktop-1280x800.png`, `970-filtro-mobile-390x844.png`, `970-monitor-desktop-1280x800.png`, `970-monitor-mobile-390x844.png`.
- **Ações / asserts (index, os dois viewports):** landmarks `table.fav-strategies`, «Estratégias favoritas», «Symbol», «Estratégia», «Ações»; linhas SOL/USDT e ETH/USDT; **ausente** «Nenhuma estratégia favorita encontrada»; **ausente** «0 estratégias carregadas»; footer «2 estratégias carregadas».
- **Ações / asserts (erro):** «Não foi possível carregar as estratégias favoritas.» + «Tentar de novo»; chrome Favoritos; ausente catálogo vazio; URL continua no proto (não login).
- **Ações / asserts (filtro):** busca `ZZZ`; «Não há resultado com estes filtros.»; ausente catálogo vazio.
- **Ações / asserts (monitor):** landmarks `table.signals` + Status/Preço/Distância/7d/Risco até stop/Tags/Operar/Par / Estratégia; «Não foi possível carregar as estratégias.»; ausente «Nenhum ativo disponível no monitor».
- **Console:** 0 errors / 0 pageerror nos dois viewports.
- **Resultado do autor:** **100/100 PASS** · FAIL 0. Isto **não** é PASS oficial de T5 (pai após A/B). Detector Impeccable: `side-tab` ×2 no clone dos cards de tier — P3 incumbente, não redesenhar.
- **Digest (UTF-8 sha256, gate deste autor):**
  - `index.html` `4f35d29ef0ae8180ddccd3279343508da6800846837303231cb1c9e7a1d076a0` · 43492 B = 7769 copied + 35723 generated. Pares `COPIED:start`/`COPIED:end`: 4/4; soma UTF-8 copiada 7769 (> 0). T5 mede só este index.html.
  - `erro.html` `0372478935f5b4a6777893657886b4eda330ef735b92f7a72eee08f31e9763f5` · 33545 B = 7717 copied + 25828 generated.
  - `filtro.html` `b7e21be008c44e254c204f4d9796b801ac3fbdb740b9107cc04c9078c9dcfbaf` · 32991 B = 7767 copied + 25224 generated.
  - `monitor.html` `f231f93e3c0493bffc305c1bf757cd1d7d6eecc25bbaec2e257a398396c96ee3` · 15953 B = 2963 copied + 12990 generated.

## Open Questions

Nenhuma. Fronteira veio grelhada do issue #970 (Q1=A, Q2=A, Q3=B).

## Design Critique

Com-tela. Teto 1+1+1: autor + dupla + 1 rework. Sem P0/P1 novos de produto. Sem segundo rework. P3 aceitos no Apply.

**Design Agent verdict: PASS**

- **P0:** nenhum
- **P1:** nenhum
- **P2 (residual):** extra `/monitor` a 390px clipa copy de erro + «Tentar de novo» dentro de `table.signals` (workaround = scroll; sem redesenhar colunas). Não bloqueia T5.
- **P3 (aceites Apply):** `side-tab` ×2 nos cards de tier; alvos 32/28px; truncagem Estratégia; header «Todas N» no erro; helper `isError`; strip de velas na lista; `MonitorDashboardTab` morto; thead clip 390; testids.

Q1=A, Q2=A, Q3=B não reabertas. Contrato visível intacto: grade lista pares no caminho feliz; erro de carga com «Tentar de novo» sem fingir catálogo vazio; filtro ≠ vazio; Início sem extra (copy já certa); Monitor extra não usa «Nenhum ativo disponível no monitor».

Snapshots: `.impeccable/critique/970-card-970-favoritos-carga-nao-vazio-assessment-A.md` · `.impeccable/critique/970-card-970-favoritos-carga-nao-vazio-assessment-B.md` · T7 `.impeccable/critique/970-card-970-favoritos-carga-nao-vazio.md`

`proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)`
`proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`
`proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)`

