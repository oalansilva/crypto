# Snapshot — Assessment B · card #803 `card-803-monitor-remover-alvo` — detector + browser

- Card: #803
- Change: `card-803-monitor-remover-alvo`
- Critic: Assessment B (detector + browser gate; isolado; sem transcript do pai; sem partilha com A)
- Modelo: inherit (mesmo do pai)
- UTC: 2026-09-03T23:06:07Z
- Round: 1
- Prototype URL: `https://dev.criptofarol.com.br/prototypes/card-803-monitor-remover-alvo/`
- File: `frontend/public/prototypes/card-803-monitor-remover-alvo/index.html` (103142 bytes)
- Digest disco: `24fc626805ebbb3561f4cc3fbf45c0572e00a520b306a24274ce9e49cf2bb92d`
- Digest HTTP servido (Playwright `response.body()`, não `page.content()`): **igual ao disco**
- Digest esperado no prompt: **match**
- UI impact: affected · live_route: `/monitor` · surface: existing
- Browser: Playwright Chromium real (headless) · desktop 1280×800 · mobile 390×844. Não curl-200.
- Live `/monitor`: **miss** (SPA 200 com chrome de login; `table.signals` ausente). Não usado como evidência de clone. Não é P0.

Evidência auxiliar: `803-B-gate.json`, `803-B-gate.mjs`, `803-B-desktop-depois.png`, `803-B-desktop-antes.png`, `803-B-desktop-modal-depois.png`, `803-B-mobile-depois.png`, `803-B-mobile-antes.png`, `803-B-mobile-modal-depois.png`.

---

## Detector (CLI)

`node .agents/skills/impeccable/scripts/detect.mjs --json frontend/public/prototypes/card-803-monitor-remover-alvo/index.html` → **exit 2**, 5 findings. Não crashou.

| antipattern | sev | classificação vs produto |
|---|---|---|
| `overused-font` Inter ×3 (linhas 10/61/177) | warning | **FP** — clone `/monitor` / Inter do produto |
| `em-dash-overuse` 15 em-dashes, advisory | warning | **FP** — copy do card (`indisponível — …`, residual EXIT) |
| `dark-glow` `#3dd68c` linha 344 | warning | **FP** — `.dot.green` do shell Monitor |

Nenhum finding do detector é o delta #803 (HOLD sem `alvo` / toggle markup). Não promove a P0/P1.

---

## Overlay (browser detector)

Preflight mutável: `document.title` + `<script>` inline → `window.__impeccable_mut === true`.

HTTPS DEV: sem overlay `[Human]` headed. Fallback: Playwright `addScriptTag({ path: detect-antipatterns-browser.js })` + `impeccableScan()`.

Desktop: 203 nós / 255 hits. Contagem: undersized-ui-text 144, low-contrast 46, tiny-text 34, ai-color-palette 11, skipped-heading 3, side-tab 4, dark-glow 3, cramped-padding 2, tight-leading 4, line-length 1, overused-font 1, gradient-text 1, marquee 1.

Mobile: 191 nós / 227 hits. Mesma família + `body-text-viewport-edge` 2 (review-bar / cards no 390).

Classificação: **FP de densidade do shell `/monitor`**. Inter, pills uppercase, `--text-muted #707a8a`, glow `.dot.green`, nav `border-left` amarelo. Nenhum hit novo é o recorte HOLD sem alvo. Não promove a P0/P1.

---

## Browser gate (asserts observáveis)

URL aberta: hash `24fc6268…` = disco. HTTP 200 **não** usado como evidência de PASS. 66/66 asserts PASS. Console `errorCount=0` / `pageerror=0` nos dois viewports.

Default = `body[data-prototype-variant=after]`. HOLD kv (SOL + ETH, 2 cópias cada: mobile-cards + table detail):

`distância até saída → distância até stop → stop → entrada → preço atual`

Sem `<dt>alvo</dt>` e sem texto visível `alvo`/`Alvo` no kv HOLD.

### Desktop 1280×800

| assert | resultado |
|---|---|
| digest servido = disco = esperado | PASS |
| default Depois; `aria-pressed` Depois=true | PASS |
| HOLD SOL/ETH kv sem alvo/Alvo; ordem dos labels | PASS |
| ETH stale: `indisponível — dado não confiável` (4 campos) + preço `$3,482.10` | PASS |
| EXIT ADA: `posição encerrada segundo a estratégia — sem risco residual mapeado` | PASS |
| EXIT LINK: exposição residual 4.10% até stop histórico | PASS |
| `table.signals` ×2 visíveis; thead Status / Preço / Distância / 7d / Risco até stop / Tags / Par / Estratégia | PASS |
| botão Operar visível (8 visíveis / 16 DOM) | PASS |
| Clique **Antes**: `data-prototype-variant=before`; SOL/ETH ganham `<dt>alvo</dt>` (markup, não só aria) | PASS |
| Labels Antes: `… stop → alvo → entrada → preço atual` | PASS |
| Clique **Depois** de novo: alvo some do kv HOLD | PASS |
| Modal Gráfico SOL Depois: `[data-alvo-row][hidden]`, Alvo não visível | PASS |
| Modal SOL Antes: Alvo visível `$119.48`; Depois de novo: hidden | PASS |
| Modal ETH: mesmo recorte (hidden Depois / visível Antes) | PASS |
| Modal ADA EXIT: residual vazio; sem Alvo no recorte residual | PASS |
| 0 erros de console que quebram fluxo | PASS |

### Mobile 390×844

| assert | resultado |
|---|---|
| digest servido = disco | PASS |
| default Depois; HOLD kv sem alvo; mesma ordem de labels | PASS |
| Clique Antes/Depois muda markup (`data-prototype-variant` + `<dt>alvo</dt>`) | PASS |
| Modal SOL/ETH: mesmo recorte hidden/visível | PASS |
| `table.signals` no DOM (2) mas **não visível** (`tablesVisible=0`) — breakpoint do produto; kv nos cards | PASS (clone, não regressão) |
| Landmarks de thead presentes no DOM; Operar visível nos cards (4) | PASS |
| ETH stale + EXIT ADA/LINK presentes | PASS |
| 0 console errors | PASS |

Toggle morto só-`aria-pressed`: **não observado**.

---

## Live `/monitor`

- `https://dev.criptofarol.com.br/monitor` → HTTP 200, URL permanece `/monitor`, body = chrome de login (`EMAIL`/`SENHA`/`Entrar`). `table.signals` = 0.
- `/login` também 200. **Não** usado como evidência de clone (instrução do prompt).
- Sem sessão: **miss** de comparação de landmarks live. Não é P0.

---

## Issues

### P0 / P1

- nenhum.

### P2

- nenhum (overlay/CLI = FP do shell; live unauth = miss, não defeito do proto).

### P3

- Overlay marca low-contrast em `--text-muted` / pills 10.5px — pré-existente do clone `/monitor`, fora do delta.
- Live `/monitor` sem auth devolve login chrome (SPA 200, não 401). Só documenta miss.

---

## Disposition

- Digest: match (disco + HTTP).
- Detector CLI: 5 warnings, todos FP.
- Overlay: hits de densidade do shell; FP; sem overlay `[Human]`.
- Browser asserts: 66/66 PASS (desktop 35 + mobile 31).
- Console: 0 erros.
- Live landmarks: miss (unauth). Não bloqueia.

## Verdict

**PASS**
