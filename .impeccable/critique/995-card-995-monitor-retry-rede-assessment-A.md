# Assessment A — card 995 · change card-995-monitor-retry-rede

> Avaliador A isolado (produto / UX / a11y / fidelidade do clone). Crítico independente, onda dupla com-tela. Sem transcript do pai. Sem nested-spawn. Sem edição de `design.md`, HTML proto, `backend/`, `frontend/src/` ou OpenSpec. Sem `process_event`. Sem arraste de Status. Única escrita: este arquivo + PNGs `995-A-*` + `995-A-gate.py` / `995-A-gate.json`.

`proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`

## Metadata

- card: 995 — "PROD: Monitor pinta erro de carga em falha transitória de rede (proxy corporativo) com sessão válida"
- change: `card-995-monitor-retry-rede`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-995-monitor-retry-rede`
- branch: `card-995-monitor-retry-rede`
- tuple: `bound_card=995` · `q_git=card-995-monitor-retry-rede` (resolver local; este filho não chama `process_event`)
- data (UTC): 2026-09-20T02:26Z
- Status observado: **Design** — GraphQL pontual `repository.issue(number:995).projectItems` → Project 1 / `oalansilva` / `fieldValueByName(Status)=Design`. GraphQL remaining=4852. MUST NOT `gh project item-list`. REST `gh api repos/oalansilva/crypto/issues/995` (não `gh issue view`): open, labels `bug` / `priority:P1` / `front:monitor` / `type:produto`.
- UI impact (rubrica D4): **affected** · `live_route: /monitor` · `surface: existing` — linhas próprias 18–20 de `design.md` (parseáveis)
- Ignore list: `.impeccable/critique/ignore.md` ausente
- Tooling: Playwright Python + Chromium (`/usr/bin/chromium-browser`) via `xvfb-run`, viewports 1280×800 e 390×844, `colorScheme: dark`. Proto servido do worktree (`frontend/public`) — o autor já documentou que worktree ≠ `environments.dev.source`. Gate `995-A-gate.json`: **156/156 PASS**. 0 console error / 0 pageerror nos 4 HTML × 2 viewports.
- Entra do issue #995 confrontado (Qs grelhadas todas A; Q4=A só Monitor). **Não reabrir.** Não Caddy/Zscaler/TTL. Não desfazer #970/#975. Não extra Favoritos/Início/Carteira.

## Limitação de sessão (obrigatória)

| URL pedida | HTTP | URL final (Playwright) | h1 | Landmarks |
|---|---|---|---|---|
| `https://dev.criptofarol.com.br/monitor` | 200 (SPA shell; urllib final continua `/monitor`) | `https://dev.criptofarol.com.br/login` | `Bem-vindo de volta` | `table.signals` = 0 |

**`/login` não é a rota.** Chrome de login **não** é evidência de clone e **não** autoriza PASS. GET urllib no path `/monitor` devolve 200 sem 302 — HTTP 200 isolado **nunca** é PASS. Prova de sessão: Playwright client-nav → `/login`. Sem cookie de administrador, a avaliação de clone usa: (1) protótipo canónico no worktree, (2) fonte viva `MonitorStatusTab.tsx`, (3) catálogo `scripts/process-fsm/route-landmarks.yaml`. Sidebar 224px / tokens Binance **não** bastam.

PNG: `995-A-live-monitor.png`.

## URL pública do proto (não é o clone)

`https://dev.criptofarol.com.br/prototypes/card-995-monitor-retry-rede/` → HTTP **404** HTML do `criptofarol-dev-prototypes.service` («Protótipo não encontrado»). Listing `/prototypes/` no :5176 só conhece três worktrees (`card-994`, `card-897`, `card-720`): o processo cacheia `roots` no boot e este worktree nasceu depois. O HTML **existe** em `crypto-worktrees/card-995-monitor-retry-rede/frontend/public/prototypes/card-995-monitor-retry-rede/`. Overlay: proto só no worktree deveria responder na URL pública — aqui o servidor está stale. **Não é P0/P1 de produto**: o aceite visível foi medido no artefacto do worktree (mesmo método do autor). PNG: `995-A-https-404.png`.

Cursor-ide-browser MCP desta sessão não criou aba estável (`No browser tab available`). Evidência = Playwright + PNGs não vazios.

## Tokens parseáveis (rubrica D4)

`design.md` linhas próprias 18–20:

```
UI impact: affected
live_route: /monitor
surface: existing
```

Regiões clonadas marcadas (linha 24): shell autenticado + workbench `/monitor` (`table.signals`, Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia) no **index.html**. Irmãos de estado da mesma superfície: `carga.html` (espera), `erro.html` (falha persistente #975), `sessao.html` (login). Sem extra `/favorites` / `/home` / Carteira (Q4=A). `COPIED:start`/`COPIED:end` nas regiões clonadas. Nunca um painel das N no index. Nunca ANTES/DEPOIS como URL canónica. Sem-tela **não** declara rota de catálogo emprestada: é com-tela `/monitor`. **PASS** deste item da rubrica. Nenhuma rodada extra nasce só para o parser.

## Digest proto (disco == HTTP local; HTTPS público 404)

| ficheiro | sha256 | bytes | disco==local | COPIED pares | copied UTF-8 |
|---|---|---|---|---|---|
| `index.html` | `5c80aa4a01efa5fab1ca1a56cdc3461e0213b22d3bfd1056fa7762407c617b9a` | 31568 | IDENTICAL | 7/7 | 22008 |
| `carga.html` | `00f523eb23752b39ab27e439ccfad82b00da98097a671c5878696060209e5fd4` | 23657 | IDENTICAL | 4/4 | 20719 |
| `erro.html` | `86d863acbb9318dfe9d5439a6e91d5fc5d1d6fde9a57065e1c464b69d40f6223` | 24773 | IDENTICAL | 5/5 | 21328 |
| `sessao.html` | `7879cd2630a22d2929db07cdfc7c0da5e1ba4f37e22261782a3ac7547d09c584` | 4933 | IDENTICAL | 3/3 | 4169 |

Canónico = index. copied > 0 em todos. Pasta HTML = `{carga,erro,index,sessao}` — **ausente** `favorites.html`. T5 mede só o index. Digests batem com `## Prototype Validation` do `design.md`.

## Fidelidade (clone da página viva)

Catálogo `/monitor`: `selectors: ["table.signals"]` · texts `Status`, `Preço`, `Distância`, `7d`, `Risco até stop`, `Tags`, `Operar`, `Par / Estratégia`.

Fonte viva `MonitorStatusTab.tsx`: `table.signals` L1256 · thead Par / Estratégia, Status, Preço, Distância, 7d, Risco até stop, Tags L1260–1266 · acções na linha (Operar). Erro vivo L1168–1178: `role="alert"` + `data-testid=monitor-load-error` + copy #975 + «Tentar de novo» com `{ refresh: true }` (bug vivo). Carga viva L1162–1165: «Carregando sinais...». Toast vivo L350–354: `Não foi possível carregar preferências do monitor.` no `catch` de preferências. KPIs vivos L1088–1107 derivam da lista (0 enquanto vazia). Bug vivo (contrato Apply, não o proto): `authFetch` só retenta `AbortError`; `TypeError: Failed to fetch` pinta #975 à primeira.

Landmarks medidos no **DOM** (`th.textContent`), não em `innerText` (CSS `text-transform:uppercase` no thead).

| Landmark | Vivo | Proto + Playwright (1280 e 390) |
|---|---|---|
| `table.signals` | L1256 | index count=2 (hold + exit); erro count=1; carga count=0 (XOR loading). Desktop index visível. Mobile index: DOM presente, tabela `visible=false`, cards no lugar |
| `Par / Estratégia` | th L1260 | thead DOM no index e no erro |
| `Status` | th L1261 | thead DOM |
| `Preço` | th L1262 | thead DOM |
| `Distância` | th L1263 (admin / `showTechnicalColumns`) | thead DOM |
| `7d` | th L1264 | thead DOM |
| `Risco até stop` | th L1265 | thead DOM |
| `Tags` | th L1266 | thead DOM |
| `Operar` | botão na linha; vivo th `actions-cell` vazio L1267 | proto th «Operar» + botões na linha. P3 clone (já no #975) |
| COPIED | — | index 7/7 · 22008 > 0 · carga 4/4 · 20719 > 0 · erro 5/5 · 21328 > 0 · sessao 3/3 · 4169 > 0 |

Anti-padrões P0:

- URL canónica do artefacto (index) **é** a board `/monitor` (shell 224×800 + KPIs + filterbar + `table.signals` + SOL/USDT e ETH/USDT). **Não** é painel ANTES/DEPOIS. Texto visível ANTES/DEPOIS = 0 nos 4 HTML × 2 viewports.
- Não é grelha de N estados no lugar da listagem. Index = caminho feliz após reabsorção. Carga / erro / sessão são irmãos. Nunca um painel das N como URL canónica.
- Sem extra `/favorites`. Contrato #983 **não reabre**.
- `MonitorDashboardTab` permanece morto. Clone = `MonitorStatusTab` / `table.signals`.
- Chrome (sidebar 224px medida no desktop: 224×800, Inter/Binance, Monitor activo, amarelo `#fcd535`) = **folha**, não prova. Prova = landmarks no proto, alinhados ao TSX.

PNGs: `995-A-desktop-1280x800-index.png` (grade + duas linhas); `995-A-mobile-390x844-index.png` (cards incumbentes).

## Produto (aceite visível — confronta Entra do #995)

Não reabrir Qs=A. Entrega = o **app** reabsorve; não isentar proxy / túnel / Caddy.

| Aceite visível (Entra) | Evidência (Playwright 1280×800 e 390×844) | Disposition |
|---|---|---|
| Feliz após reabsorção: lista pares; ausente #975; ausente toast de preferências | index: SOL/USDT + ETH/USDT; `table.signals`; KPIs 1/1/2/2 (não 0); «Não foi possível carregar as estratégias.» = 0; toast = 0; «Nenhum ativo disponível no monitor» = 0 | OK |
| Espera de dezenas de segundos: «Carregando sinais...»; KPIs **não** 0 como verdade | carga.html: «Carregando sinais...» + `role=status`; `.kpi-val` = `-` com `data-kpi-pending`; `aria-busy=true` na faixa; ausente #975; ausente toast; ausente catálogo vazio. Duração exacta = P3 Apply | OK |
| Se a carga passa na mesma abertura: lista; ausente erro; ausente toast | index é esse estado. Toast ausente nos quatro HTML × dois viewports | OK |
| Caso do incidente: depois de abrir, o quadro lista os pares (sem mudar de rede) | index pinta SOL/ETH à primeira; proto estático não exige segundo clique. Subset 2 de 11 = mock do contrato visível (design.md), não o enumerado do log | OK |
| «Tentar de novo» relê; «Atualizar» recomputa | erro: retry `data-load-mode="reread"` `href=index.html`; Atualizar `data-load-mode="recompute"` no index/carga/erro. Como (authFetch vs fila) = P3 | OK |
| Sessão morta → login; não fica no quadro de erro | sessao.html: «Bem-vindo de volta» + «Entrar»; ausente #975; ausente `table.signals`. Live `/monitor` → `/login` observado e **descartado** como clone | OK |
| Falha persistente = copy #975 + «Tentar de novo»; permanece Monitor; sem catálogo vazio | erro.html: as duas frases + retry 44px focável; chrome Monitor; URL continua no proto; 0 linhas de sinal; KPIs `-` não 0 | OK |
| Sem extra Favoritos/Início/Carteira | HTML set = 4 ficheiros; nav Favoritos/`#` não é extra de superfície | OK |
| Sem redesign da board / copy #970/#975 | Labels KPI e copy de erro intactos; filtro default «Em portfólio» | OK |

Análise/gráfico com velas = Apply (não o proto estático). `MonitorDashboardTab` permanece morto.

## UX

Modo Impeccable: **Operate** / refinement. Job: abrir `/monitor` atrás de proxy corporativo (Zscaler) com sessão válida e ver sinais depois de um corte transitório — ou #975 só se persistir, ou login se a sessão morreu.

Hierarquia: AppNav → workbench Monitor → h1 sr-only «Monitor de sinais» → KPIs → filtros Em portfólio → `table.signals`. Delta óbvio sem redesign: espera = «Carregando sinais...» + KPIs pendentes; sucesso = pares; persistente = copy #975 + retry que aponta à lista.

Carga cognitiva: 2 pares no feliz = o contrato visível (não um wall das 11). Erro nomeia a falha e oferece Tentar de novo no chrome Monitor. Irmãos não competem no index.

Vale emocional do incidente (quadro #975 + KPIs 0 + toast com sessão válida e 200 no servidor) → pico (SOL/ETH na board, ou espera honesta, ou #975 só se persistir) → fim (retry relê; sessão morta já vai ao login).

## Acessibilidade

- `lang=pt-BR`; `:focus-visible` incumbente; `prefers-reduced-motion` no proto.
- Landmarks: `aside` de navegação + `h1` «Monitor de sinais» (sr-only, clone vivo) + `table.signals` no feliz. Carga: `role="status"` `aria-live="polite"` em «Carregando sinais...»; faixa KPIs `aria-busy="true"`.
- Erro: `role=alert` + `data-testid=monitor-load-error`. Retry: `.monitor-retry` focável (`activeElement`, **não** disabled), altura medida **44px** nos dois viewports, `tag=A` `href=index.html`.
- GO de estado não é só cor: texto «Carregando sinais...» / «Não foi possível…» / pills Em posição / Saída.
- Alvos 44px no retry já no proto (e no vivo). Alvos de linha densos = clone / P3.

## Responsividade

- Desktop 1280×800: sidebar 224×800; `table.signals` visível no index; overflow-x documento = 0. Acções da linha (Ver Trades / Operar) recortam à direita — incumbente da board, P3. PNG `995-A-desktop-1280x800-{index,carga,erro,sessao}.png`.
- Mobile 390×844 index: sidebar 0; cards SOL/ETH; `table.signals` no DOM, `visible=false` como o vivo <740px. Overflow-x = 0. Busca clipa «Buscar par, est» — P3. PNG `995-A-mobile-390x844-index.png`.
- Mobile carga/erro: «Carregando sinais...» / copy #975 + retry 44px; KPIs `-`; mobilebar subtítulo «SOL/USDT 1d» (shell copiado) — P3. PNG `995-A-mobile-390x844-{carga,erro}.png`.
- Mobile sessão: login «Bem-vindo de volta» + Entrar. PNG `995-A-mobile-390x844-sessao.png`.

## Estados

Mock cobre: feliz após reabsorção (index), espera (carga.html), falha persistente #975 (erro.html), sessão morta (sessao.html). Não mocka: vazio real de catálogo (sem favoritos crypto — fora do incidente), filtro sem resultado (já no #975), toast a disparar e sumir (P3: não disparar vs retirar). Cobertura de mock = P3. Vazio real reusa copy viva; mocká-lo como irmão confundiria com o incidente.

## Design specificity

A tela é o Monitor do Cripto Farol depois do incidente PROD 2026-09-19 ~22:08 BRT (corte de proxy, 200 no uvicorn, browser sem JSON). Não iria a um SaaS genérico inalterado. Folha Binance; `DESIGN.md` não reescrito. Refinement, não redesign. `sessao.html` clona `/login` — irmão de estado, **não** empresta `live_route`.

## Heurísticas Nielsen (0–4, Operate; só neste snapshot)

| # | Heurística | Score | Nota |
|---|---|---|---|
| 1 | Visibility of system status | 4 | Feliz lista pares; espera «Carregando sinais...» + KPIs `-`; erro copy #975; sessão = login |
| 2 | Match between system and real world | 4 | Copy de operador; sem fingir catálogo vazio; toast de preferências ausente no feliz |
| 3 | User control and freedom | 4 | Tentar de novo permanece no Monitor e aponta à lista; Atualizar continua a recomputar; sessão morta já é login |
| 4 | Consistency and standards | 3 | Clone da board; thead vazio no erro (XOR vivo); th Operar vs `actions-cell` vazio |
| 5 | Error prevention | 4 | Primeiro `Failed to fetch` deixa de ser a última palavra; 0 KPI deixa de mentir na espera |
| 6 | Recognition rather than recall | 4 | Estados nomeados na própria board; operador não precisa lembrar o incidente |
| 7 | Flexibility and efficiency | 3 | Retry é o acelerador se o proxy ficar minutos; duração exacta da espera = Apply |
| 8 | Aesthetic and minimalist design | 3 | Clone denso; clip de acções a 1280 e busca a 390 |
| 9 | Help users recognize/recover errors | 4 | #975 + retry; «Isto não significa que não há estratégias.» |
| 10 | Help and documentation | 3 | Screen help incumbente; Ajuda no nav |
| **Total** | | **36/40** | **Good** |

## Cognitive load

Checklist: 1 workbench canónico; 1 lista; 2 pares no feliz. Espera/erro/sessão em URLs próprias. **Pass** (0 falhas). Decisão no glance ≤4 (abrir gráfico / retry / Atualizar / ir ao login).

## Emotional journey

Vale (PROD: «Não foi possível carregar as estratégias.» / KPIs 0 / toast de preferências com sessão válida) → pico (espera honesta, depois SOL/ETH na `table.signals`) → fim (retry relê sem recomputar; persistente continua #975; sessão morta → login). Reassegurança: a lista no servidor não foi apagada.

## Personas (só neste snapshot)

1. **Alex (operador diário em Zscaler):** abre `/monitor`, espera «Carregando sinais...», vê SOL/ETH sem mudar de rede nem bater no login.
2. **Riley (stress do incidente):** #975 só depois da espera; toast de preferências não fica no feliz; «Tentar de novo» não dispara outra recomputação.
3. **Sam / Casey (mobile 390):** cards repetem os pares; retry 44px visível no erro; KPIs `-` na espera, não 0.

## Strengths

- Clone estrutural de `/monitor`, não galeria ANTES/DEPOIS nem painel das N superfícies.
- Delta mínimo e óbvio: espera = loading + KPIs pendentes; sucesso = lista; persistente = copy #975; morta = login.
- Entra do #995 visível nos quatro irmãos. Q4=A (só Monitor) intacto. Não reaberto.
- Disco == HTTP local (index `5c80aa4a01efa5fab1ca1a56cdc3461e0213b22d3bfd1056fa7762407c617b9a`, 31568 B). copied > 0.
- `/login` descartado. Clone **não** alegado só por sidebar 224px: prova = landmarks proto × `MonitorStatusTab.tsx`. HTTP 200 isolado não foi PASS.

## Playwright (esta sessão)

- Desktop 1280×800 e mobile 390×844: aceite visível do contrato nas 4 URLs locais. 0 console / 0 pageerror. Overflow-x = 0.
- Live `/monitor` → Playwright `/login` (descartado). GET 200 no path não conta.
- HTTPS público do proto = 404 stale roots (registado; não substitui o artefacto).
- PNGs: `995-A-desktop-1280x800-{index,carga,erro,sessao}.png`, `995-A-mobile-390x844-{index,carga,erro,sessao}.png`, `995-A-live-monitor.png`, `995-A-https-404.png`. Gate: `995-A-gate.json` (156/156).
- Landmarks `/monitor` no DOM (`th.textContent`) = Status / Preço / Distância / 7d / Risco até stop / Tags / Operar / Par / Estratégia. Uppercase visual do thead é CSS incumbente.

## Prototype Validation (rubrica)

`design.md` secção Prototype Validation presente: Playwright desktop+mobile, asserts do contrato, digest. Esta sessão **reexecutou** o browser nos quatro HTML (local, porque a URL pública 404) e confirma o aceite. Curl/GET 200 no `/monitor` vivo não substituiu o Playwright. Disco == local nos quatro ficheiros.

## Priority issues

Nenhum P0/P1 de produto/escopo/contrato visível. Clip incumbente, thead vazio no erro, retry `<a>`, mobilebar «SOL/USDT 1d» em carga/erro e 404 da URL pública são P3 (Apply / clone / infra).

## P0

_(nenhum)_

## P1

_(nenhum)_

## P2

_(nenhum)_

## P3 — detalhe de Apply / clone de região fora do delta

- **P3-1** Acções da linha (Ver Trades / Operar) recortam a 1280; busca do topbar clipa placeholder a 390. Incumbente da board; non-goal redesign.
- **P3-2** `erro.html` deixa thead vazio visível por baixo do card #975 (`display:block` no `table-wrap`). Vivo é XOR erro/tabela. Já aceite em `design.md` (#975).
- **P3-3** Mobilebar subtítulo «SOL/USDT 1d» em `carga.html` / `erro.html` (shell copiado) enquanto a lista ainda não chegou. Folha, não o contrato da espera.
- **P3-4** «Tentar de novo» no proto é `<a class="monitor-retry" href="index.html">`; vivo = `<button>` + `fetchOpportunities(..., { refresh: true })`. Prova de Design = aponta à lista, `data-load-mode="reread"`, focável 44px. Apply: relê sem `refresh=true`.
- **P3-5** Contagem exacta de retries / backoff / teto em ms (desde que a espera seja dezenas de segundos, não 8s). Retry em `authFetch` vs fila no `MonitorStatusTab`.
- **P3-6** Placeholder KPI `-` / skeleton / `aria-busy` — desde que 0 não pinte como verdade. Toast: não disparar vs disparar e retirar quando a carga passa.
- **P3-7** Vivo th de acções vazio (`actions-cell` L1267); proto rotula «Operar». Detector `side-tab` ×2 nos cards mobile de tier — incumbente do clone, não redesenhar.
- **P3-8** `MonitorDashboardTab` morto: não ressuscitar. Testids `monitor-retry` / `monitor-refresh` / `monitor-loading` / `data-kpi-pending`.
- **P3-9** Mock com 2 pares (SOL/ETH), não as 11 estratégias do log do incidente. Contrato visível do `design.md` é SOL/ETH. Vazio-real de catálogo sem irmão (evita confundir com o incidente).
- **P3-10** URL pública `https://dev.criptofarol.com.br/prototypes/card-995-monitor-retry-rede/` 404 porque `dev_prototype_server` cacheia roots no boot e este worktree não está na listing. Infra; o artefacto no disco está completo. Pai/T5: restart do unit se Alan precisar do link. Não é falha do clone.

## Disposition

Aceitar P3 no Apply. Não reabrir grelha. Não reabrir Qs=A nem Q4=A. Não desfazer #970/#975. Não alongar TTL. Não mexer Caddy/Zscaler/payload. Não exigir galeria de N estados nem ANTES/DEPOIS no index. Não promover clip 1280 / busca 390 / thead vazio / retry `<a>` / mobilebar SOL / 404 stale / backoff a P0/P1. Não exigir segundo rework de Design.

## Verdict

**PASS** — zero P0/P1 de produto/escopo/contrato visível. Tokens parseáveis 3/3. Landmarks `/monitor` no index (`table.signals` + 8 texts). Disco == local (index `5c80aa4a01efa5fab1ca1a56cdc3461e0213b22d3bfd1056fa7762407c617b9a`, 31568 B). Sem galeria/ANTES-DEPOIS como index. copied > 0. Delta = espera + feliz após reabsorção + #975 persistente + login se sessão morta. Entra do #995 visível. `/login` descartado. Clone **não** alegado só por sidebar 224px: prova = landmarks proto × `MonitorStatusTab.tsx`. HTTP 200 isolado não foi PASS. Snapshots Playwright **não** vazios (8 proto + live + 404).

`Design Agent verdict` final da coluna = síntese do pai após A+B. Este filho A não chama `process_event`. Sem T5.

---

```
Assessment A 995
tokens_ok: yes
clone_ok: yes
P0: nenhum
P1: nenhum
P2: nenhum
P3: clip Operar 1280/busca 390; thead vazio erro.html; mobilebar SOL/USDT 1d em carga/erro; retry <a href=index.html> vs refetch; backoff/authFetch Apply; KPI - / toast não disparar vs retirar; actions-cell vs th Operar; MonitorDashboardTab morto; mock 2 pares; HTTPS proto 404 stale roots
verdict: PASS
```
