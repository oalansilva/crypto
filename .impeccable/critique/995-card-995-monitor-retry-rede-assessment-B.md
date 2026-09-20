# Assessment B (detector + browser real) — card 995 · change card-995-monitor-retry-rede

> Assessor B isolado, mesmo modelo, sem transcript de A nem do pai. Sem nested-spawn.
> Nada movido (Status, branch, worktree); nenhuma edição fora deste ficheiro, PNGs `995-B-*`, `995-B-gate.py`, `995-B-gate.json` e `995-B-detect.json`.
> Tokens parseáveis do `design.md` (rubrica D4, não reabrir parser): `UI impact: affected` · `live_route: /monitor` · `surface: existing`.

```
Assessment B 995
digest_match: disk==expected yes; HTTPS 404 (roots congelados no arranque)
detector: [] index/carga/erro; sessao flat-type-hierarchy warning (P3 incumbente login)
P0: nenhum
P1: nenhum
P2: nenhum
P3: clip Operar/Ver Trades 1440; busca truncada 390; thead vazio+clip erro; mobilebar SOL carga/erro; flat-type-hierarchy sessao; DELTA:start=0; HTTPS 404 até restart prototypes; retries/backoff Apply
verdict: PASS
```

- UTC: 2026-09-20T02:16Z
- Tuple (read-only): `bound_card=995` · `q_git=card-995-monitor-retry-rede`. Sem `process_event`. Sem `move_agent_to_root`.
- Status GraphQL pontual (`repository.issue(number:995).projectItems`): **Design** · item `PVTI_lAHOAAHtBM4BV8b2zg7x7qg` · Project 1 `oalansilva`. GraphQL remaining=4855. MUST NOT `gh project item-list`.
- REST `gh api repos/oalansilva/crypto/issues/995` (não `gh issue view`): OPEN *«PROD: Monitor pinta erro de carga em falha transitória de rede (proxy corporativo) com sessão válida»* · labels `bug` `priority:P1` `front:monitor` `type:produto`.
- Protótipo canónico: `frontend/public/prototypes/card-995-monitor-retry-rede/index.html`
- Servido (overlay): https://dev.criptofarol.com.br/prototypes/card-995-monitor-retry-rede/ → HTTP **404** HTML «Protótipo não encontrado» (não SPA). `criptofarol-dev-prototypes.service` PID 921468 calcula `public_roots` **uma vez no arranque**; o worktree `card-995-monitor-retry-rede` é posterior. Disco do worktree **existe** (index 31568 B). Avaliação do contrato = HTTP local sobre `frontend/public` (mesmo path que o servidor deveria servir). Não `file://`.
- Irmãos (mesma superfície, não extra de catálogo): `carga.html` · `erro.html` · `sessao.html`. Sem extra `/favorites` / `/home` / Carteira (Q4=A).
- Digest index esperado (`design.md`): `5c80aa4a01efa5fab1ca1a56cdc3461e0213b22d3bfd1056fa7762407c617b9a` · 31568 B. Disco == esperado: **IDENTICAL**. HTTPS ≠ disco (404, 607 B).
- Rota viva `https://dev.criptofarol.com.br/monitor` → browser **`/login`** («Bem-vindo de volta»). Login **não** é a rota; **não** autoriza PASS de clone. GET curl `/monitor` HTTP 200 · 455 B (shell Vite) **não** é PASS. Clone avaliado no proto do worktree.
- Browser: Playwright Python + Chromium 1243 (`chrome-linux-arm64`) sob `xvfb-run -a`, `--no-sandbox`. Viewports **1440×900** e **390×844**. `colorScheme: dark`. Critério igual nos dois viewports (autor usou 1280×800; 1440 cobre o mesmo contrato). MCP `cursor-ide-browser` não abriu tab neste filho (list vazia); evidência = Playwright. Snapshots **não** vazios → **não BLOCKED**.
- Detector: `node .agents/skills/impeccable/scripts/detect.mjs --json` nos quatro HTML versionados (cwd worktree). Overlay `detect.js` não injectado.

## 1. Digest servido == local

| Ponta | sha256 | bytes |
|---|---|---|
| Disco `index.html` | `5c80aa4a01efa5fab1ca1a56cdc3461e0213b22d3bfd1056fa7762407c617b9a` | 31568 |
| Esperado (`design.md`) | idem | 31568 · **IDENTICAL** |
| HTTPS GET `/prototypes/card-995-monitor-retry-rede/` | `dda22bf3…eb51469` | 607 HTTP **404** · não idêntico |
| HTTPS GET `…/index.html` | 404 · 617 B | não idêntico |
| Disco `carga.html` | `00f523eb23752b39ab27e439ccfad82b00da98097a671c5878696060209e5fd4` | 23657 · HTTPS 404 |
| Disco `erro.html` | `86d863acbb9318dfe9d5439a6e91d5fc5d1d6fde9a57065e1c464b69d40f6223` | 24773 · HTTPS 404 |
| Disco `sessao.html` | `7879cd2630a22d2929db07cdfc7c0da5e1ba4f37e22261782a3ac7547d09c584` | 4933 · HTTPS 404 |

HTTP 200 isolado **não** é o gate. 404 HTTPS é o servidor de protótipos com roots congelados — P3 infra, não furo de produto. Contrato visível medido no HTML do worktree.

## 2. Detector Impeccable

- Alvos: `index.html`, `carga.html`, `erro.html`, `sessao.html`.
- `index.html` / `carga.html` / `erro.html` → `[]`, exit 0.
- `sessao.html` exit 2 → 1 finding `flat-type-hierarchy` (L36, sizes 12/14/20px, ratio 1.7:1). Clone `/login`.
- **Classificação:** P3 incumbente do clone de login (já no `design.md`). **Não** reabre como P0/P1. Sem finding crítico. `side-tab` antecipado no Apply contract **não disparou**.

## 3. Tokens + clone / fidelidade (superfície existing)

- `design.md` linhas próprias: `UI impact: affected` · `live_route: /monitor` · `surface: existing`. **Não** é rota de catálogo emprestada. Sem extra `/favorites`.
- Catálogo `scripts/process-fsm/route-landmarks.yaml` `/monitor`: `selectors: ["table.signals"]`, `texts: ["Status", "Preço", "Distância", "7d", "Risco até stop", "Tags", "Operar", "Par / Estratégia"]`.
- Index no browser (1440 e 390): `table.signals`=**2** (Em posição + Saída / cobertura); thead `textContent` contém os 8 texts. Sidebar 224px no desktop (`offsetWidth=224`); **chrome 224px sozinho não passa** — listing + headers visíveis no 1440.
- Mobile 390: tabela `display:none` como o vivo; cards incumbentes mostram SOL/USDT e ETH/USDT. Landmarks permanecem no HTML/`textContent` do thead.
- Pares `COPIED:start`/`COPIED:end` index = **7/7**; soma UTF-8 copiada **22008** (> 0); total 31568 = 22008 copied + 9560 generated. `carga.html` 4/4 · 20719 copied. `erro.html` 5/5 · 21328. `sessao.html` 3/3 · 4169. `DELTA:start`=0 — delta nas linhas/KPI/estados, não região nova / painel das N.
- Toggle Antes/Depois: **ausente**. Botões «Antes»/«Depois» = **0**. Substring `ANTES`/`DEPOIS` só em comentário HTML («Sem painel ANTES/DEPOIS») — innerText do body **não** as mostra. URL canónica = `index.html`. Sem grelha «N estados».
- Caminho feliz visível: linhas **SOL/USDT** (Cruzamento EMA · Em posição) e **ETH/USDT** (RSI swing · Saída / cobertura); KPIs 1 / 1 / 2 / 2; default **Em portfólio** + Todos; **ausente** «Nenhum ativo disponível no monitor»; **ausente** copy #975; **ausente** toast «Não foi possível carregar preferências do monitor.»; «Atualizar» com `data-load-mode="recompute"`.
- `lang=pt-BR` nas quatro páginas.

## 4. Browser real — matriz (desktop 1440×900 e mobile 390×844)

Console error = 0; warning relevante = 0; pageerror = 0; responses ≥400 no proto local = 0. Overflow documento `scrollWidth<=clientWidth+1` (1440==1440; 390==390). Gate bruto: `.impeccable/critique/995-B-gate.json`. «Tentar de novo» box 126.2×**44** px; `href=index.html`; `data-load-mode="reread"`.

| # | Assert | Desktop 1440×900 | Mobile 390×844 |
|---|---|---|---|
| 1 | Digest disco == esperado (HTTPS 404 documentado; não basta HTTP 200) | PASS | PASS |
| 2 | Tokens `UI impact: affected` / `live_route: /monitor` / `surface: existing` | PASS | — |
| 3 | Landmarks `/monitor`: `table.signals` + Status / Preço / Distância / 7d / Risco até stop / Tags / Operar / Par / Estratégia | PASS (2 tabelas + thead) | PASS (cards + thead no DOM; tabela `display:none` incumbente) |
| 4 | Chrome 224px **não** é a prova sozinha | PASS (sidebar 224 + listing) | PASS (sidebar hidden; listing via cards) |
| 5 | COPIED 7/7 · 22008 > 0; 0 botões Antes/Depois; sem painel das N / ANTES/DEPOIS | PASS | PASS |
| 6 | Feliz: SOL/USDT + ETH/USDT; KPIs 1/1/2/2; **ausente** empty; **ausente** #975; **ausente** toast | PASS | PASS |
| 7 | `carga.html`: «Carregando sinais...»; KPI 0-como-verdade **ausente** (`data-kpi-pending`, valor `-`); **ausente** #975; **ausente** toast; `role=status` | PASS | PASS |
| 8 | `erro.html`: copy #975 + «Tentar de novo» reread; chrome Monitor; KPI não 0; **não** catálogo vazio; URL proto (não `/login`); `role=alert` | PASS | PASS |
| 9 | `sessao.html`: «Bem-vindo de volta» + «Entrar»; **ausente** quadro #975; labels Email/Senha | PASS | PASS |
| 10 | Sem extra `/favorites`; 0 console / 0 pageerror | PASS | PASS |
| 11 | Detector sem finding crítico | PASS | — |
| 12 | Live `/monitor` sem sessão → `/login`; login **não** usado como PASS | PASS | — |

Pixels index desktop: pares SOL/USDT e ETH/USDT na `table.signals`; headers PAR / ESTRATÉGIA · STATUS · PREÇO · DISTÂNCIA · 7D · RISCO ATÉ STOP · TAGS · OPERAR; KPIs 1/1/2/2; filtro Em portfólio; sem empty; sem #975; sem toast. Sem botões Antes/Depois. Coluna Operar empilha «Ver Trades» sobre «Operar» (clip incumbente).

Pixels index mobile: cards SOL/USDT · ETH/USDT; KPIs empilhados; «2 resultados»; busca «Buscar par, est»; mobilebar «SOL/USDT 1d»; sem empty.

Pixels carga desktop: «Carregando sinais...»; KPIs `-` (não 0); labels Em posição / Saída / cobertura / Total / Em carteira intactos; sem #975; sem toast.

Pixels carga mobile: mesma espera + KPIs `-`; mobilebar «SOL/USDT 1d» (chrome clone, não linha de sinal).

Pixels erro desktop: copy #975 + «Tentar de novo» 44px amarelo; KPIs `-`; thead vazia visível; **não** «Nenhum ativo disponível no monitor». Retry aponta a `index.html`.

Pixels erro mobile: mesma copy + retry 44px; thead recorta à direita (P3); mobilebar «SOL/USDT 1d».

Pixels sessao desktop+mobile: card «Bem-vindo de volta» + «Entrar»; **ausente** #975.

Rota viva **não usada como prova de clone** (caiu em `/login`). HTTP 200 do GET `/monitor` (455 B) **não** conta.

## 5. Confronta Entra

| Entra | Proto | Disposition |
|---|---|---|
| App reabsorve falha transitória (não isentar proxy) | Quatro XOR: carga → lista; #975 só no irmão persistente | PASS |
| Primeiro corte **não** é a última palavra | Index feliz sem #975; carga sem #975 | PASS |
| Espera dezenas de segundos em «Carregando sinais...» | Estado `carga.html` visível; ms exactos = P3 Apply | PASS |
| KPIs **não** 0 como verdade durante a espera | `data-kpi-pending` + `-`; `kpi_zero_truth=false` | PASS |
| Toast de preferências ausente se a carga passa | Needle ausente no index e na carga (DOM + innerText) | PASS |
| «Tentar de novo» relê; «Atualizar» recomputa | retry `data-load-mode="reread"`; Atualizar `"recompute"` | PASS |
| Incidente: lista os pares sem mudar de rede | Clone lista SOL/USDT + ETH/USDT (não 11 linhas — clone vivo, não redesign) | PASS |
| Sessão morta → login | `sessao.html` clone `/login`; sem quadro #975 | PASS |
| Falha persistente = copy #975, sem catálogo vazio | `erro.html` copy exacta; empty ausente | PASS |
| Não entra: Caddy/Zscaler/TTL/redesign/Favoritos-Início-Carteira | Sem extra dessas rotas; copy #975 intacta | PASS |

## 6. Findings (toda finding classificada)

### P0 — nenhum

Clone `/monitor` com landmarks do catálogo; copied 22008 > 0; sem painel ANTES/DEPOIS nem grelha das N; feliz com pares crypto e KPIs reais; carga com «Carregando sinais...» e KPI pendente; irmão erro com copy #975 + Tentar de novo reread; sessão morta = login; empty e toast **ausentes**; detector sem crítico; snapshots Playwright não vazios. Fidelidade + contrato visível ok → **não BLOCKED**. Chrome 224px não foi tratado como prova suficiente. Login da rota viva não foi usado como PASS.

### P1 — nenhum

Quatro estados visíveis em URLs distintas (index / carga / erro / sessao). Empty de catálogo **não** ocupa nenhum. Retry permanece no proto e aponta à lista. Extras Favoritos/Início/Carteira **ausentes** (Q4=A). HTTPS 404 não é furo de produto/escopo (servidor de protótipos; HTML no worktree cumpre o contrato).

### P2 — nenhum

### P3 — aceites (Apply / clone chrome; não reabrir como P0/P1)

- **P3-1 Clip desktop da coluna Operar** («Ver Trades» / «Operar» empilhados). Já no `design.md`.
- **P3-2 Truncagem da busca a 390** («Buscar par, est»). Incumbente; Non-goal: não redesenhar.
- **P3-3 Thead vazio no `erro.html`** (XOR vivo erro/tabela) + clip TAGS/OPERAR no 390. Já no Apply contract.
- **P3-4 Mobilebar `SOL/USDT 1d` em carga/erro** — chrome incumbente; não é linha de sinal nem catálogo vazio.
- **P3-5 Cards mobile no index** (tabela `display:none`) — clone vivo. Landmarks via thead no DOM + cards SOL/ETH.
- **P3-6 Detector `flat-type-hierarchy`** no clone `/login` (`sessao.html`). Já no `design.md`.
- **P3-7 `DELTA:start`=0** no index: delta é tbody/KPI/estados, não região marcada. Copied 7/7 > 0.
- **P3-8 URL pública 404** — `criptofarol-dev-prototypes.service` não rescaneia worktrees novos. Disco == digest esperado. Restart do unit (pai/Alan) se o link HTTPS for preciso; este filho MUST NOT restart.
- **P3-9 Contagem exacta de retries / backoff / teto em ms; `authFetch` vs fila; toast não disparar vs retirar; `MonitorDashboardTab` morto; testids.** Já P3 de Apply no `design.md`. Proto cumpre o contrato visível (espera / lista / #975 / login).
- **P3-10 Alvos «Tentar de novo» 44px** — medido 126.2×**44** nos dois viewports. Já no vivo.

Observações (não-findings): overlay `detect.js` não injectado — evidência = CLI + Playwright no proto do worktree. GET `/monitor` autenticado não usado. Default visível «Em portfólio». Needle «Nenhum ativo disponível no monitor» **ausente** inclusive no HTML. Placeholder KPI é hífen incumbente `-` (não em-dash). «Atualização contínua a cada 30s» permanece copy do clone (grelha: não é pull real).

## 7. Veredito

**PASS** — zero P0/P1/P2 abertos; detector `flat-type-hierarchy` classificado P3; digest disco == esperado; clone+delta (não ANTES/DEPOIS); `/login` vivo não usado como prova; matriz visível desktop+mobile nos quatro estados. HTTP 200 sozinho não sustentaria este veredito. Snapshots Playwright não vazios.

Disposition: crítico não pede rework. P3 aceites no Apply.

## 8. Referências

- Proto URL (overlay): https://dev.criptofarol.com.br/prototypes/card-995-monitor-retry-rede/ (404 até restart do unit)
- Digest index (disco): `5c80aa4a01efa5fab1ca1a56cdc3461e0213b22d3bfd1056fa7762407c617b9a` · 31568 B
- Digest carga: `00f523eb23752b39ab27e439ccfad82b00da98097a671c5878696060209e5fd4` · 23657 B
- Digest erro: `86d863acbb9318dfe9d5439a6e91d5fc5d1d6fde9a57065e1c464b69d40f6223` · 24773 B
- Digest sessao: `7879cd2630a22d2929db07cdfc7c0da5e1ba4f37e22261782a3ac7547d09c584` · 4933 B
- Snapshot: `.impeccable/critique/995-card-995-monitor-retry-rede-assessment-B.md`
- Gate bruto: `.impeccable/critique/995-B-gate.json`
- Detector: `.impeccable/critique/995-B-detect.json`
- PNGs: `995-B-desktop-1440x900-{index,carga,erro,sessao}.png`, `995-B-mobile-390x844-{index,carga,erro,sessao}.png`, `995-B-https-404-canonical.png`

proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)
