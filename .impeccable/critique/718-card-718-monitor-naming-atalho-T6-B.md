# Snapshot — Assessment B · card #718 `card-718-monitor-naming-atalho` — T6 · detector + browser

- Card: #718
- Change: `card-718-monitor-naming-atalho`
- Critic: Assessment B (detector + fidelidade de clone + browser gate; isolado; sem transcript do pai; sem partilha com A)
- Modelo: inherit (mesmo do pai)
- UTC: 2026-09-08T21:30:33Z
- Round: T6 (Alan devolveu Design: residual r1 só chrome+⌘K era insuficiente)
- UI impact: affected · live_route: `/monitor` · surface: existing
- Canonical proto: `frontend/public/prototypes/card-718-monitor-naming-atalho/index.html` (24121 bytes)
- Extra Ajuda: `frontend/public/prototypes/card-718-monitor-naming-atalho/ajuda.html` (11167 bytes)
- URL canónica (HTTPS): `https://dev.criptofarol.com.br/prototypes/card-718-monitor-naming-atalho/` → **HTTP 404** (até restart; não usado como PASS)
- URL extra (HTTPS): `https://dev.criptofarol.com.br/prototypes/card-718-monitor-naming-atalho/ajuda.html` → **HTTP 404**
- Browser: Playwright Chromium 1243 real (`--no-sandbox`, fresh contexts) · desktop 1280×800 · mobile 390×844. Não curl-200. Gate HTTP local no worktree + screenshots `file://` limpos.
- Live `/monitor` sem sessão → `/login`. `/login` **não** é a live_route.

Evidência auxiliar (mesma pasta): `718-T6-B-gate.json`, `718-T6-B-desktop-index.png`, `718-T6-B-mobile-index.png`, `718-T6-B-desktop-ajuda.png`, `718-T6-B-mobile-ajuda.png`, `718-T6-B-live-monitor.png`.

---

## Verdict: APROVAR-COM-P3

Index é clone+delta T6 da topologia `/monitor` (landmarks do catálogo HEAD presentes; extra `/help` é irmão, não painel no index). Nome canónico único `Em posição` / `Saída / cobertura` observável em KPI, h3, Status da tabela, pill mobile, ScreenHelpPanel e parágrafo Ajuda. Sem ⌘K, sem badge Estado Compra, sem terceiro estado, sem Compra/Venda como estado da board. Uppercase CSS da pill/h3 é token incumbente (não muda o vocabulário). Tasks/spec cobrem T6. D2 está no contrato Apply. 0 P0/P1. P3 = clone-thinning / overlay FP / Apply já aceite / HTTPS 404 de ambiente.

---

## Digests (medi eu)

| ficheiro | bytes | sha256 disco (B) | sha256 autor | match |
|---|---|---|---|---|
| `index.html` | 24121 | `9fb0e14144333144c1b80249099e388579a187de27715eefd457cf612f199660` | `9fb0e14144333144c1b80249099e388579a187de27715eefd457cf612f199660` | **igual** |
| `ajuda.html` | 11167 | `c42327c826f5d8b68614181a779f6d3745866c6af95f7138cda7ab80af1c5972` | `c42327c826f5d8b68614181a779f6d3745866c6af95f7138cda7ab80af1c5972` | **igual** |

HTTP local (Python `SimpleHTTPRequestHandler` na pasta do proto; `response.body()`, não `page.content()`):

- `GET /` → 200, 24121 bytes, sha256 `9fb0e141…9660` = disco
- `GET /ajuda.html` → 200, 11167 bytes, sha256 `c42327c8…5972` = disco

HTTPS DEV canónico e extra: **404**. `127.0.0.1:5176` também 404. Prompt previa 404 até restart. Browser gate **não** usa HTTP 200 isolado como PASS; usa digest disco+local + asserts observáveis.

`copied` (UTF-8 entre `COPIED:start`/`COPIED:end`):

- index: 2 pares, soma **12533** bytes (> 0)
- ajuda: 1 par, soma **4682** bytes (T5 mede só o index)

---

## Tokens parseáveis (rubrica D4 / gate no autor)

Lidos de `openspec/changes/card-718-monitor-naming-atalho/design.md`, cada um em linha própria:

```
UI impact: affected
live_route: /monitor
surface: existing
surface_detail: topbar-search, kpis, filterbar, sections-hold-exit, table-signals-status, mobile-card-status, screen-help-panel
```

- `UI impact` / `live_route` / `surface` parseáveis. Com-tela marca regiões clonadas em `surface_detail` (não empresta rota de catálogo).
- HTML do proto **não** duplica essas três linhas (861 as meteu no markup). Rubrica D4: tokens vivem no autor/`design.md`; **nenhuma rodada extra nasce só para o parser**. Item da rubrica: **PASS**.
- `live_route: /monitor` é chave do catálogo HEAD `scripts/process-fsm/route-landmarks.yaml`.

---

## Detector CLI

`node .agents/skills/impeccable/scripts/detect.mjs --json <file>` — não crashou.

### index.html → exit 2, 3 findings (warnings)

| antipattern | sev | linha | classificação vs produto |
|---|---|---|---|
| `overused-font` Inter ×2 | warning | 17, 32 | **FP** — Inter do shell `/monitor` / `index.css` |
| `dark-glow` `#3dd68c` | warning | 136 | **FP** — `.status-row .pip.hold` `box-shadow: 0 0 8px rgba(61, 214, 140, 0.6)` copiado de `frontend/src/index.css` ~3503 |

Nenhum finding é o delta T6 (nomes canónicos / sem ⌘K / sem Estado Compra). Não promove a P0/P1.

### ajuda.html → exit 2, 1 finding

| antipattern | sev | classificação |
|---|---|---|
| `overused-font` Inter | warning | **FP** — clone `/help` |

---

## Overlay (browser detector)

Preflight: `addScriptTag({ path: detect-antipatterns-browser.js })` + `impeccableDetect()`. Sem overlay `[Human]` headed. HTTPS DEV 404 ⇒ scan em `file://` / HTTP local.

| superfície | nós | hits | contagem |
|---|---|---|---|
| index desktop 1280×800 | 22 | 26 | undersized-ui-text 16, dark-glow 3, cramped-padding 2, line-length 1, overused-font 1, skipped-heading 1, gradient-text 1, marquee 1 |
| index mobile 390×844 | 19 | 23 | undersized-ui-text 16, dark-glow 3, overused-font 1, skipped-heading 1, gradient-text 1, marquee 1 |
| ajuda desktop | 2 | 4 | line-length 1, overused-font 1, gradient-text 1, marquee 1 |
| ajuda mobile | 1 | 4 | overused-font 1, flat-type-hierarchy 1, gradient-text 1, marquee 1 |

Classificação: **FP de densidade do shell** (Inter, pills 10.5px, glow do pip hold/exit, line-length do ScreenHelpPanel). Nenhum hit novo é o recorte T6. Não promove a P0/P1.

`line-length` no parágrafo do ScreenHelpPanel (~149 chars) é copy incumbente (`MonitorPage.tsx:9`) com troca estrita de Compra/Venda → nomes canónicos. Não é redesign. P3 no máximo.

---

## Browser gate (asserts observáveis)

Motor: Python Playwright + Chromium 1243 `chrome-linux-arm64/chrome`. 73/73 PASS. Console errorCount=0 / pageerror=0 nos dois viewports. `document.documentElement` overflow-x = **0 px** desktop e mobile.

Default = clone+delta (sem toggle Antes/Depois — correcto: toggle morto só seria P0 se fosse a única prova de clone).

### Contrato T6 medido (DOM text)

| superfície | HOLD | EXIT | viewport |
|---|---|---|---|
| KPI `.kpi-label` | `Em posição` (`text-transform: none`) | `Saída / cobertura` (`none`) | ambos |
| h3 `.status-row h3` | `Em posição (3)` | `Saída / cobertura (2)` | ambos |
| pill tabela `table.signals td .status-pill` | `Em posição` | `Saída / cobertura` | desktop visível |
| pill mobile `.mobile-card .status-pill` | `Em posição` | `Saída / cobertura` | mobile visível |
| ScreenHelpPanel `p` | cita os dois nomes; **não** cita Compra/Venda | — | ambos |
| Ajuda `[data-testid=help-monitor-copy]` | cita os dois nomes; **não** cita Compra/Venda como estado | Spot `comprar / stop / vender` permanece | ambos |

KPI tags: 0 `.tag`. Hint: 0 `.kbd` / 0 `⌘K` / 0 `Cmd+K`. Badge: 0 `Estado Compra/Venda` / 0 `Estado hold/exit`. Terceiro estado: 0 `[data-testid=monitor-section-wait]`. Palavra visível `Compra`/`Venda` no index: **0**. `Em saída`: **0**.

⌘K/Ctrl+K no proto: `document.activeElement` permanece `BODY` (sem listener). Placeholder intacto `Buscar par, estratégia, tag...`.

Link ScreenHelpPanel `href=ajuda.html` → navega para a página extra (não embute `/help` no index). Ajuda **não** contém `table.signals`.

### Uppercase CSS da pill — muda o contrato visível?

**Não.** Medição Playwright + screenshot:

Incumbente `frontend/src/index.css`:

- `.monitor-theme .status-pill { text-transform: uppercase; font-size: 10.5px; … }` (~3685)
- `.monitor-theme .status-row h3 { text-transform: uppercase; }` (~3477)
- `.monitor-theme .kpi-label` **sem** uppercase (~3332)

Proto copia esses tokens. Resultado:

| região | DOM `textContent` | `getComputedStyle().textTransform` | `innerText` visível (Chromium, nós visíveis) | clip? |
|---|---|---|---|---|
| KPI | `Em posição` / `Saída / cobertura` | `none` | sentence case | não |
| h3 | `Em posição (3)` / `Saída / cobertura (2)` | `uppercase` | **EM POSIÇÃO (3)** / **SAÍDA / COBERTURA (2)** | não |
| pill hold visível | `Em posição` | `uppercase` | **EM POSIÇÃO** · 86×20 · scrollW=clientW=84 | não |
| pill exit visível | `Saída / cobertura` | `uppercase` | **SAÍDA / COBERTURA** · 134×20 · scrollW=clientW=132 | não |

Hoje o vivo já mostra h3 `Em posição` em uppercase e pill `Compra`→`COMPRA`. T6 troca o **vocabulário** (Compra/Venda → nomes da seção) e **herda** o token CSS. KPI (sem uppercase) vs h3 (uppercase) já divergiam em casing no incumbente; o delta não inventa um terceiro casing.

Contrato T6 = nome único lexical `Em posição` / `Saída / cobertura` nas superfícies da board + Ajuda. Casing CSS de chrome não é nome terceiro nem fura o escopo. Sem clip da string mais longa (`Saída / cobertura`) na pill mobile. **Não é P0/P1.** P3: Apply herda `.status-pill` uppercase; não desligar o token só porque o nome cresceu.

### Desktop 1280×800

| assert | resultado |
|---|---|
| digest local = disco = autor | PASS |
| `table.signals` ×2 visíveis; `.mobile-cards` display none | PASS |
| thead Status / Preço / Distância / 7d / Risco até stop / Tags / Par / Estratégia | PASS |
| botão Operar visível (≥1; 5 no DOM das tabelas) | PASS |
| 4 KPIs exactos, sem `.tag` | PASS |
| h3 HOLD/EXIT = nomes canónicos, sem `status-section-label` | PASS |
| Status linha HOLD = `Em posição`; EXIT = `Saída / cobertura` | PASS |
| ScreenHelpPanel cita nomes; não ensina Compra/Venda | PASS |
| busca sem ⌘K; Meta+K/Ctrl+K não foca | PASS |
| 0 Estado Compra; 0 terceiro estado; 0 Antes/Depois/6 estados | PASS |
| Ajuda extra via link; clone `/help` com nomes; Spot comprar/vender fica | PASS |
| overflow-x 0 px | PASS |
| 0 console / 0 pageerror | PASS |

### Mobile 390×844

| assert | resultado |
|---|---|
| digest local = disco | PASS |
| `.table-wrap` display none; `.mobile-cards` visíveis (3 HOLD + 2 EXIT) | PASS (breakpoint incumbente `@media (max-width: 740px)`) |
| pills visíveis: 3× EM POSIÇÃO + 2× SAÍDA / COBERTURA; sem clip | PASS |
| KPIs 2×2; mesmos nomes; ScreenHelpPanel canónico | PASS |
| clique Ajuda → `ajuda.html` (página, não painel) | PASS |
| 0 console / 0 pageerror; overflow-x 0 | PASS |

Landmarks de thead presentes no DOM (escondidos no breakpoint). Catálogo `/monitor` satisfeito no HTML canónico.

---

## Fidelidade de clone vs incumbente

Incumbentes lidos (não editados): `MonitorStatusTab.tsx` (⌘K `:1011`, KPIs `:1062-1076` `Em posição`+tag Compra / `Em saída`+tag Venda, badge `Estado {cfg.title}` `:1168`, h3 já canónico `:1171`, Status `badgeText` `:1294`), `OpportunityCard.tsx` pill `:256-259` + `Sinal · {badgeText}` `:312`, `signalResolution.ts` `badgeText: Compra/Venda` **e** `markerLabel: Compra/Venda`, `HelpPage.tsx:42` «Compra, Venda, contexto», `MonitorPage.tsx:9` ScreenHelpPanel.

Catálogo HEAD `/monitor`: selector `table.signals`; texts Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia. **Todos no index.** Chrome-only sem listing seria P0; aqui o listing está. Sidebar 224px **ausente** — o inverso do P0 «sidebar+tokens sem tabela». Skill: com-tela marca só as regiões clonadas (`surface_detail`). Não é galeria 2×2 nem painel ANTES/DEPOIS.

Delta visível vs incumbente (SÓ T6):

- removido `<span class="kbd">⌘K</span>`
- KPI saída `Em saída`+tag Venda → `Saída / cobertura` sem tag; KPI posição sem tag Compra
- removido `Estado Compra/Venda`
- Status/pill `Compra`/`Venda` → nomes da seção
- ScreenHelpPanel e Ajuda: troca estrita

Não-delta (clone): tokens `--bg-*` / `--hold` / `--exit` / Inter / JetBrains Mono; topbar Telegram/Tema/Atualizar; filterbar; seções hold/exit; `table.signals`; mobile-cards no ≤740px; copy page-sub / desc de seção.

Thinning (não bloqueia T5; P3):

- sem `.app-sidebar` 224px / app-header
- sem `MonitorDisclaimer`
- mobile-card simplificado (sem toggles portfólio/timeframe, sem `Sinal · {badgeText}` interno do `OpportunityCard`)
- filterbar sem seg admin `Em portfólio`/`Todos` (já P3 aceite em `design.md`)
- sample data ilustrativo (já P3 aceite)

`OpportunityCard` linha 312 `Sinal · {badgeText}` não está no proto. Tasks 3.2 amarram o rótulo visível do card (`monitor-card-signal-*`). D2/P3 do `design.md` já distingue remap de board vs `badgeText` global (ChartModal `:721`/`:916` também lê `badgeText`). Crítico **não** reabre isso como P0/P1.

---

## Tasks / spec cobrem T6?

**Sim.**

`tasks.md`:

- §3 Status da linha + rótulo mobile (3.1 coluna `table.signals` `:1294`; 3.2 pill `OpportunityCard` / `monitor-card-signal-*`; 3.3 **não** alterar `markerLabel` / Spot)
- §4 Ajuda troca estrita (4.1 `HelpPage.tsx:42`; 4.2 `MonitorPage.tsx:9` ScreenHelpPanel)
- §5 aceite 5.4 Status+pill; 5.5 Ajuda+painel

`specs/monitor/spec.md`:

- Requirement «Coluna Status e card mobile com o nome canónico» + 3 scenarios (linha HOLD, linha EXIT, card mobile)
- Requirement «Ajuda ensina os nomes canónicos» + scenarios parágrafo `/help` e ScreenHelpPanel
- Requirement HOLD/EXIT inalterada + scenario Gráfico e Spot (`markerLabel` Compra/Venda)

Residual r1 (só KPI+hint) **não** é o contrato desta rodada. T6 está escrito em proposal/design/tasks/spec e **observável** no proto.

---

## D2 (board vs markerLabel) no contrato Apply?

**Sim**, em quatro sítios — não só wording:

1. `design.md` **D2**: estado da board ≠ lado de transação; Apply não pode «renomear Compra em todo o frontend»; remap do rótulo visível da board **sem** alterar `markerLabel` nem legenda do gráfico.
2. `design.md` **Apply contract**: ficheiros da board + Ajuda; opcional `badgeText` só para board em `signalResolution.ts` **sem** tocar `markerLabel`. Proibido: rename global de Compra.
3. `tasks.md` 3.3.
4. `spec.md` Requirement «Regra HOLD/EXIT inalterada e lado de ordem intocado» / scenario Gráfico e Spot.

P3 já aceite no design: «se o remap da board é novo campo vs `badgeText` só na renderização da board». ChartModal usa `badgeText` **e** `markerLabel` — Apply tem de não vazar o rename da board para o gráfico. Detalhe de Apply; **não** reabrir como P0/P1.

Proto: 0 `markerLabel` visível; 0 painel Spot; 0 rename de Compra no gráfico. Extra Ajuda mantém `comprar / stop / vender` (lado de ordem, D4).

---

## Extra `/help` não é painel no index

Regra N superfícies: URL canónica = clone primário `/monitor` (`index.html`); extra = clone irmão `/help` (`ajuda.html`). Index **não** é galeria das N nem ANTES/DEPOIS.

Medido:

- index = MonitorStatusTab + ScreenHelpPanel; link `Ajuda` → `ajuda.html`
- ajuda = clone `HelpPage` (header, onboarding, usage grid, actions) + delta só no artigo Monitor
- clique real no browser: URL passa a `…/ajuda.html`; 0 `table.signals` na Ajuda
- T5 (não executado aqui) mede só o index — correcto

---

## Live `/monitor`

`https://dev.criptofarol.com.br/monitor` → Playwright `networkidle` → URL final `https://dev.criptofarol.com.br/login`. Chrome de login: «Bem-vindo de volta» / EMAIL / SENHA / Entrar. `table.signals` = 0.

`/login` também 200 com o mesmo chrome. **Não** usado como evidência de clone (instrução do prompt + spec impeccable-design-gate: login não é live_route). Sem sessão: **miss** de comparação de landmarks live. Não é P0.

Screenshot: `718-T6-B-live-monitor.png`.

---

## Issue #718 (REST `gh api`, não `gh issue view`)

Title: «Monitor: nomes de estado inconsistentes e atalho Cmd+K que não existe». Labels: bug, priority:P2, front:monitor, type:produto. State open.

Body original = residual r1 (KPI+seção+hint; Ajuda «aguarda #788»). Comentário PO 2026-08-29: Compra/Venda espera #788. T6 (Alan devolveu Design) alarga o residual visível a Status/pill + Ajuda porque #788 = Cancelado. Design/proposal/tasks/spec desta worktree reflectem T6. Crítico avalia o contrato T6 do prompt + `design.md`, não o body pré-T6 isolado.

---

## Issues

### P0

- nenhum.

### P1

- nenhum.

### P2

- nenhum. HTTPS 404 = ambiente (restart); live unauth = miss, não defeito do proto. Overlay/CLI = FP do shell.

### P3 (aceites / detalhe de Apply — não reabrir como P0/P1)

- P3-1 Clone thinning: sem sidebar 224px / `MonitorDisclaimer` / controlos internos do `OpportunityCard`. Landmarks do catálogo presentes; `surface_detail` declara as regiões. Sample data + filterbar sem `Em portfólio` já estão em `design.md` P3.
- P3-2 Uppercase CSS da pill/h3 é token incumbente; DOM = nomes canónicos; visual EM POSIÇÃO / SAÍDA / COBERTURA; sem clip. Apply herda `.status-pill` / `.status-row h3`.
- P3-3 Overlay: undersized-ui-text 10.5px, dark-glow dos pips, Inter, line-length do ScreenHelpPanel — densidade pré-existente.
- P3-4 CSS órfão no proto (`.status-section-label`, `.kbd` no produto) — já P3 `.kbd` / `.kpi-label .tag` no design.
- P3-5 Remap `badgeText` vs campo novo vs só render da board (ChartModal também lê `badgeText`) — já P3/D2 no `design.md`.
- P3-6 HTTPS canónico 404 até restart; evidência B = disco + HTTP local + browser no worktree.

---

## Disposition

- Digest index/ajuda: match autor = disco = HTTP local.
- HTTPS DEV: 404 (ambiente). Não bloqueia.
- Tokens parseáveis: PASS em `design.md`.
- Detector CLI: warnings FP.
- Overlay: FP de densidade; sem hit no delta T6.
- Browser asserts: **73/73 PASS** (desktop + mobile, index + ajuda + ⌘K + overflow).
- Console: 0 erros.
- Catálogo `/monitor`: landmarks presentes; `copied` 12533.
- Extra `/help`: irmão, não painel.
- D2 + tasks/spec T6: cobertos.
- Uppercase CSS: não muda contrato visível.
- Live landmarks: miss (unauth → `/login`). Não bloqueia.
- P0/P1: 0.

## Verdict

**APROVAR-COM-P3**
