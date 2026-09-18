# Assessment A — card 970 · change card-970-favoritos-carga-nao-vazio

> Avaliador A isolado (produto / UX / a11y / fidelidade do clone). Crítico independente, onda dupla com-tela. Sem transcript do pai. Sem nested-spawn. Sem edição de `design.md`, HTML proto, `backend/`, `frontend/src/` ou OpenSpec. Sem `process_event`. Sem arraste de Status. Única escrita: este arquivo + PNGs `970-A-*` + `970-A-gate.py` / `970-A-gate.json`.

`proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`

## Metadata

- card: 970 — "PROD: Favoritos fica em Carregando e depois diz que não há estratégias"
- change: `card-970-favoritos-carga-nao-vazio`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-970-favoritos-carga-nao-vazio`
- branch: `card-970-favoritos-carga-nao-vazio`
- tuple: `bound_card=970` · `q_git=card-970-favoritos-carga-nao-vazio` (resolver local; este filho não chama `process_event`)
- data (UTC): 2026-09-18T13:18Z
- Status observado: **Design** — GraphQL pontual `repository.issue(number:970).projectItems` → Project 1 / `oalansilva` / `fieldValueByName(Status)=Design`. GraphQL remaining=4799. MUST NOT `gh project item-list`. REST `gh api repos/oalansilva/crypto/issues/970` (não `gh issue view`).
- UI impact (rubrica D4): **affected** · `live_route: /favorites` · `surface: existing` — linhas próprias 11–13 de `design.md` (parseáveis)
- Ignore list: `.impeccable/critique/ignore.md` ausente
- Tooling: Playwright Python + Chromium (`/usr/bin/chromium-browser`) via `xvfb-run`, HTTPS real, viewports 1280×800 e 390×844, `colorScheme: dark`. 0 console error / 0 pageerror nos 4 HTML × 2 viewports.
- Q1=A, Q2=A, Q3=B gravadas no grill / `design.md`. **Não reabrir.**

## Limitação de sessão (obrigatória)

| URL pedida | HTTP | URL final (Playwright) | h1 | Landmarks |
|---|---|---|---|---|
| `https://dev.criptofarol.com.br/favorites` | 200 (SPA shell) | `https://dev.criptofarol.com.br/login` | `Bem-vindo de volta` | `table.fav-strategies` = 0 |

**`/login` não é a rota.** Chrome de login **não** é evidência de clone e **não** autoriza PASS. GET urllib no path `/favorites` devolve 200 sem 302 — HTTP 200 isolado **nunca** é PASS. Prova de sessão: Playwright client-nav → `/login`. Sem cookie de administrador, a avaliação de clone usa: (1) protótipo canónico HTTPS, (2) fonte viva `FavoritesDashboard.tsx` + `MonitorStatusTab.tsx`, (3) catálogo `scripts/process-fsm/route-landmarks.yaml`. Sidebar 224px / tokens Binance **não** bastam.

PNG: `970-A-live-favorites.png`.

## Tokens parseáveis (rubrica D4)

`design.md` linhas próprias 11–13:

```
UI impact: affected
live_route: /favorites
surface: existing
```

Regiões clonadas marcadas: shell AppNav + workbench `/favorites` (`table.fav-strategies`, «Estratégias favoritas», «Symbol», «Estratégia», «Ações») no **index.html**. Extra 1: `/monitor` em `monitor.html`. Irmãos `erro.html` / `filtro.html` — nunca canónicos. Sem extra `/home`. Sem `live_route` emprestada. **PASS** deste item da rubrica. Nenhuma rodada extra nasce só para o parser.

## Digest proto (disco == HTTPS)

| ficheiro | sha256 | bytes | disco==HTTPS | COPIED pares | copied UTF-8 |
|---|---|---|---|---|---|
| `index.html` | `4f35d29ef0ae8180ddccd3279343508da6800846837303231cb1c9e7a1d076a0` | 43492 | IDENTICAL | 4/4 | 7769 |
| `erro.html` | `0372478935f5b4a6777893657886b4eda330ef735b92f7a72eee08f31e9763f5` | 33545 | IDENTICAL | 4/4 | 7717 |
| `filtro.html` | `b7e21be008c44e254c204f4d9796b801ac3fbdb740b9107cc04c9078c9dcfbaf` | 32991 | IDENTICAL | 4/4 | 7767 |
| `monitor.html` | `f231f93e3c0493bffc305c1bf757cd1d7d6eecc25bbaec2e257a398396c96ee3` | 15953 | IDENTICAL | 2/2 | 2963 |

Canónico = index. copied > 0 em todos. Pasta HTML = `{index,erro,filtro,monitor}` — **ausente** `home.html`.

## Fidelidade (clone da página viva)

Catálogo `/favorites`: `selectors: ["table.fav-strategies"]` · texts `Estratégias favoritas`, `Symbol`, `Estratégia`, `Ações`.

Fonte viva `FavoritesDashboard.tsx`: h1 L1261 · `table.fav-strategies` L1466 · thead Symbol / Estratégia / Ações L1472–1487. Bug vivo (contrato Apply, não o proto): `useQuery` L305 só lê `isLoading`; L1393–1396 e L1491–1494 ramificam `filteredFavorites.length === 0` → «Nenhuma estratégia favorita encontrada.»

| Landmark | Vivo | Proto + Playwright (1280 e 390) |
|---|---|---|
| `table.fav-strategies` | L1466 | count=1; desktop visível; mobile no DOM, cards no lugar (`@media`) |
| `Estratégias favoritas` | h1 L1261 | h1 visível desktop e mobile |
| `Symbol` | th L1472 | thead desktop; filtro + tile SOL/ETH no mobile |
| `Estratégia` | th L1473 | thead desktop; nome da estratégia no card mobile |
| `Ações` | th L1487 | thead desktop; Analisar/Revalidar/Delete no card mobile |
| COPIED | — | index 4/4 · copied 7769 > 0 |

Catálogo `/monitor` (só extra): `table.signals` · Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia. Extra `monitor.html` tem os 8 texts + `table.signals` count=1.

Anti-padrões P0:

- URL canónica `…/prototypes/card-970-favoritos-carga-nao-vazio/` → index **é** a listagem de Favoritos (shell 224px + workbench + duas linhas). **Não** é painel ANTES/DEPOIS. Texto visível ANTES/DEPOIS = 0 nos 4 HTML × 2 viewports.
- Não é grelha de N estados no lugar da listagem. Index = caminho feliz (SOL/USDT + ETH/USDT). Erro e filtro são irmãos; monitor é extra. Nunca um painel das N como URL canónica.
- Sem extra `/home`. Copy de falha do Início (`HomePage.tsx` «Não foi possível carregar `/api/favorites`.») **não muda**.
- `MonitorDashboardTab` existe no repo e **não** é montado (só a definição). Extra clona `MonitorStatusTab` / `table.signals`.

Chrome (sidebar 224px, Inter/Binance, Favoritos ativo, amarelo `#fcd535`) = **folha**, não prova. Prova = landmarks no proto, alinhados ao TSX.

## Produto (aceite visível — não reabrir Q1 / Q2 / Q3)

Q1=A quatro estados visíveis. Q2=A retry na tela se a sessão continua. Q3=B Favoritos + Monitor (copy nova) + Início (só regressão, sem extra).

| Aceite visível | Evidência (Playwright 1280×800 e 390×844) | Disposition |
|---|---|---|
| Feliz: SOL/USDT + ETH/USDT; footer «2 estratégias carregadas» | index desktop e mobile. Linhas da tabela = 2. | OK |
| Ausente catálogo vazio no feliz | «Nenhuma estratégia favorita encontrada» = 0 no index. | OK |
| Ausente «0 estratégias carregadas» como único resultado | index footer = «2 estratégias carregadas». | OK |
| Erro: copy + Tentar de novo; permanece Favoritos | erro.html: «Não foi possível carregar as estratégias favoritas.» + «Tentar de novo»; topbar Favoritos; URL continua no proto. | OK |
| Erro: ausente catálogo vazio; ausente login | copy de vazio = 0; «Bem-vindo de volta» = 0; URL ≠ `/login`. `role=alert`. | OK |
| Filtro: busca ZZZ + copy de filtro | input search = `ZZZ`; «Não há resultado com estes filtros.»; `role=status`. | OK |
| Filtro: ausente catálogo vazio | «Nenhuma estratégia favorita encontrada» = 0. Header «Todas 2» + «0 filtradas» = catálogo existe, filtro esconde. | OK |
| Monitor: erro ≠ vazio do board | «Não foi possível carregar as estratégias.»; «Nenhum ativo disponível no monitor» = 0. | OK |
| Sem extra `/home`; Discovery/#897/#948/#935 fora | HTML da pasta = 4 ficheiros. Nav Descoberta/Combo só chrome. | OK |

Q1/Q2/Q3 **não reabertas**. Análise/gráfico com velas = Apply (não o proto estático).

## UX

Modo Impeccable: **Operate** / refinement. Job: abrir Favoritos e ver os pares crypto, ou um erro com retry, sem achar que o catálogo sumiu.

Hierarquia: AppNav → h1 Estratégias favoritas → tiers → filtros → lista. Delta óbvio sem redesign da grade: o vazio único parte-se em feliz / erro / filtro.

Carga cognitiva: 2 linhas no feliz = o contrato, não um wall. Filtro nomeia a causa (ZZZ visível). Erro nomeia a falha e oferece Tentar de novo no chrome Favoritos.

Vale emocional do incidente (catálogo «sumiu») → pico (pares visíveis ou erro explícito) → fim (retry sem login; filtro não mente vazio).

## Acessibilidade

- `lang=pt-BR`; `:focus-visible`; `prefers-reduced-motion`.
- Landmarks: `aside[aria-label=Navegação principal]` + `main`; tabela `fav-strategies` / extra `signals`.
- Erro Favoritos: `role=alert` + `data-testid=favorites-load-error`. Filtro: `role=status`. Monitor: `role=alert` + `data-testid=monitor-load-error`.
- «Tentar de novo» Favoritos: `min-height:44px` (CSS). Desktop o primeiro `.fav-retry` está no bloco mobile (`display:none`) — o visível está no `td` da tabela (PNG). Monitor retry medido 44px.
- GO de estado não é só cor: texto «Carga falhou» / «Não foi possível…» / «Não há resultado…».
- Alvos 28px nas estrelas e 32px nos ícones da linha = clone vivo / P3 já no `design.md`.

## Responsividade

- Desktop 1280×800: sidebar 224px; tabela visível; overflow-x documento = 0. Colunas Período/Stop/PF… do thead vivo existem; 1280 recorta à direita (clone denso, non-goal). PNGs `970-A-desktop-1280x800-{index,erro,filtro,monitor}.png`.
- Mobile 390×844 Favoritos: sidebar 0; cards SOL/ETH no feliz; erro e filtro em card de estado. Overflow-x documento = 0. PNGs `970-A-mobile-390x844-{index,erro,filtro,monitor}.png`.
- Mobile 390×844 Monitor extra: `table.signals` larga; o delta de erro (copy + Tentar de novo) fica dentro de `td colspan=8` e **clipa** até haver scroll horizontal do wrap. Ver P2.

## Estados

Mock cobre: feliz (index), erro de carga (erro.html), filtro sem resultado (filtro.html), falha Monitor (monitor.html). Não mocka: loading, vazio real de catálogo, sessão morta→login (já é o shell). Cobertura de mock = P3. Vazio real reusa copy viva; mocká-lo como irmão confundiria com o incidente.

## Design specificity

A tela é Favoritos do Cripto Farol depois do incidente 2026-09-17 (carga falhou e mentiu vazio). Não iria a um SaaS genérico inalterado. Folha Binance; `DESIGN.md` não reescrito. Refinement, não redesign.

## Heurísticas Nielsen (0–4, Operate; só neste snapshot)

| # | Heurística | Score | Nota |
|---|---|---|---|
| 1 | Visibility of system status | 4 | Feliz lista pares; erro «Carga falhou»; filtro «0 filtradas» com Todas 2 |
| 2 | Match between system and real world | 4 | Copy de operador, sem path de API na grade; Início mantém o path no KPI |
| 3 | User control and freedom | 4 | Tentar de novo permanece em Favoritos (Q2=A); filtro ZZZ visível para limpar |
| 4 | Consistency and standards | 3 | Clone da grade; extra Monitor mete o erro *dentro* da tabela (vivo empty é card) |
| 5 | Error prevention | 3 | Quatro ramos evitam o falso vazio; header «Todas 2» no erro ainda mente contagem (P3 aceite) |
| 6 | Recognition rather than recall | 4 | Estados nomeados na própria lista; operador não precisa lembrar o incidente |
| 7 | Flexibility and efficiency | 3 | Filtros do vivo no mock; retry é o acelerador do incidente |
| 8 | Aesthetic and minimalist design | 3 | Clone denso; truncagem da Estratégia (table-layout fixed vivo) |
| 9 | Help users recognize/recover errors | 4 | Erro + retry; «isto não significa que o catálogo está vazio» |
| 10 | Help and documentation | 3 | Screen help incumbente; Ajuda no nav |
| **Total** | | **35/40** | **Good** |

## Cognitive load

Checklist: 1 h1; 1 lista; 2 pares no feliz. Filtro e erro não competem no index. **Pass** (0–1 falhas). Decisão no glance ≤4 (abrir análise / retry / limpar ZZZ).

## Emotional journey

Vale (PROD: «Nenhuma estratégia favorita encontrada» com 63 pares no banco) → pico (SOL/ETH na grade, ou erro com retry) → fim (filtro admite que o catálogo existe). Reassegurança: «Isto não significa que o catálogo está vazio. A sessão continua válida.»

## Personas (só neste snapshot)

1. **Alex (operador diário):** abre `/favorites`, vê SOL/ETH e «2 estratégias carregadas», não 0. Se a carga falha, Tentar de novo sem ir ao login.
2. **Riley (stress do incidente):** erro ≠ vazio; filtro ZZZ ≠ vazio; Monitor falho ≠ «Nenhum ativo disponível no monitor».
3. **Sam / Casey (mobile 390):** cards repetem os pares; retry Favoritos visível. Extra Monitor: CTA clipada no wrap da tabela (P2).

## Strengths

- Clone estrutural de `/favorites`, não galeria ANTES/DEPOIS.
- Delta mínimo e óbvio: o vazio único parte-se em três copies (lista / erro / filtro).
- Q1 visível nos irmãos; Q2 visível (retry + chrome Favoritos); Q3 visível no extra Monitor sem extra `/home`.
- Filtro «Todas 2» + «0 filtradas» ensina que o catálogo não sumiu.

## Playwright (esta sessão)

- Desktop 1280×800 e mobile 390×844: aceite visível do contrato 8/8 nas 4 URLs. 0 console / 0 pageerror.
- Live `/favorites` → Playwright `/login` (descartado). GET 200 no path não conta.
- PNGs: `970-A-desktop-1280x800-{index,erro,filtro,monitor}.png`, `970-A-mobile-390x844-{index,erro,filtro,monitor}.png`, `970-A-live-favorites.png`. Gate: `970-A-gate.json`.
- 1 check urllib (`live-is-login-not-route`) falhou porque a SPA não faz 302 — **não** é defeito de produto; Playwright prova `/login`.

## Prototype Validation (rubrica)

`design.md` secção Prototype Validation presente: Playwright desktop+mobile, asserts do contrato. Esta sessão **reexecutou** o browser nas 4 URLs públicas e confirma o aceite. Curl/GET 200 não substituiu o Playwright.

## Priority issues

Nenhum P0/P1 de produto/escopo/contrato visível. O clip do retry no extra Monitor a 390 é P2 (workaround = scroll; non-goal = sem redesign da grelha Monitor).

## P0

_(nenhum)_

## P1

_(nenhum)_

## P2

- **P2-1** Extra `/monitor` a 390×844: o delta «Não foi possível carregar as estratégias.» + «Tentar de novo» vive num `td colspan=8` de `table.signals`; o wrap horizontal clipa copy e CTA. O vazio vivo (`MonitorStatusTab`) é `monitor-empty-card` a largura do board, não uma linha da tabela. Workaround: scroll. Não redesenhar colunas Status/Preço/Distância. Apply: estado de falha a largura do board (card/alert), thead `table.signals` pode permanecer para o landmark. Residual — não bloqueia Design.

## P3 — detalhe de Apply / clone de região fora do delta

- **P3-1** Detector `side-tab` nos cards mobile de tier — incumbente do clone `/favorites`. Já aceite em `design.md`.
- **P3-2** Alvos 32px nos ícones da linha e 28px nas estrelas — clone vivo; já no contrato Apply.
- **P3-3** Truncagem desktop do nome na coluna Estratégia. Já no Apply.
- **P3-4** Contadores do header («Todas 2», tiers 1/0/1) no estado de erro — já aceite. Chip «Carga falhou» mitiga.
- **P3-5** «Tentar de novo» Favoritos é `<a href=index.html>` no proto estático; vivo = `refetch()`. Testids `favorites-load-error` / `favorites-filter-empty` / `monitor-load-error`.
- **P3-6** Nome do helper / `isError` vs `status === 'error'` vs `Array.isArray`. Strip `analysis_candles` (e séries equivalentes) na lista; análise continua pesada.
- **P3-7** `MonitorDashboardTab` morto: não ressuscitar.
- **P3-8** Mock sem loading e sem vazio-real. Sessão morta já é o shell `/login`.
- **P3-9** Colunas avançadas (Período/Stop/PF…) recortadas a 1280 — clone denso; non-goal redesign da grade.

## Disposition

Aceitar P3 no Apply. P2-1 residual: estado de falha do Monitor a largura do board, sem redesenhar a grelha. Não reabrir grelha. Não reabrir Q1 / Q2 / Q3. Não exigir segundo rework de Design. Não promover `side-tab` / 32px / header «Todas 2» no erro / clip de colunas a P0/P1.

## Verdict

**PASS** — zero P0/P1 de produto/escopo/contrato visível. Tokens parseáveis 3/3. Landmarks `/favorites` no index. Disco == HTTPS (index `4f35d29ef0ae8180ddccd3279343508da6800846837303231cb1c9e7a1d076a0`, 43492 B). Sem galeria/ANTES-DEPOIS como index. copied > 0. Delta = feliz com pares + erro + filtro + extra Monitor. `/login` descartado. Clone **não** alegado só por sidebar: prova = landmarks proto × `FavoritesDashboard.tsx`. HTTP 200 isolado não foi PASS.

`Design Agent verdict` final da coluna = síntese do pai após A+B. Este filho A não chama `process_event`.

---

```
Assessment A 970
tokens_ok: yes
clone_ok: yes
P0: nenhum
P1: nenhum
P2: extra /monitor 390 clipa erro+retry dentro de table.signals
P3: side-tab; alvos 32/28px; truncagem Estratégia; header Todas 2 no erro; <a> vs refetch; isError helper; candles; MonitorDashboardTab morto; mock sem loading/vazio-real; colunas 1280
verdict: PASS
```
