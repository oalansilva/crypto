# Snapshot — Assessment B · card #792 `card-792-monitor-risco-explicito` — detector + browser · r2

- Card: #792
- Change: `card-792-monitor-risco-explicito`
- Critic: Assessment B (detector + browser gate; isolado; sem transcript do pai; sem partilha com A)
- Modelo: inherit
- UTC: 2026-08-29T20:28:15Z
- Round: 2
- Prototype URL: `https://dev.criptofarol.com.br/prototypes/card-792-monitor-risco-explicito/`
- File: `frontend/public/prototypes/card-792-monitor-risco-explicito/index.html` (95314 bytes)
- Digest disco: `1a1ff265162784ca5708a76de22e6565ae85fb2832b90daec73cc40ac12f90c3`
- Digest HTTP servido (Playwright `response.body()`, não `page.content()`): **igual ao disco**
- Digest esperado no prompt: **match**
- UI impact: affected
- Browser: Playwright Chromium real · desktop 1280×800 · mobile 390×844 (touch). Não curl-200.

Evidência auxiliar (mesma pasta): `792-r2-B-desktop-1280x800.png`, `792-r2-B-desktop-after-antes.png`, `792-r2-B-mobile-390x844.png`, `792-r2-B-gate.json`, `792-r2-B-overlay.json`.

---

## Detector (CLI + tokens/shell vs produto)

CLI: `node .agents/skills/impeccable/scripts/detect.mjs --json <prototype>` → exit 2, 5 findings.

| antipattern | sev | classificação vs produto |
|---|---|---|
| `overused-font` Inter ×3 (linhas 10/61/177) | warning | **FP** — `frontend/src/index.css` e `DESIGN.md` usam Inter. Clone correto. |
| `em-dash-overuse` 16 em-dashes, advisory | warning | **FP** — copy do card (`indisponível — …`, `posição encerrada — …`). Densidade vem do fixture duplicado (mobile-cards + table detail). |
| `dark-glow` `#3dd68c` linha 344 | warning | **FP** — copiado de `.monitor-theme .dot.green` em `index.css` (`box-shadow: 0 0 8px rgba(61, 214, 140, 0.6)`). |

Tokens no `:root` do protótipo batem com o produto: `--bg-primary #0b0e11`, `--bg-secondary #181a20`, `--accent-primary #fcd535`, `--text-primary/#secondary/#tertiary/#muted`, `--border-default #2b3139`, `--app-sidebar-width: 224px`, `--app-header-desktop: 80px`.

Shell medido no desktop (Playwright):

- `.app-sidebar` **224×748**, visível, nav Monitor `aria-current="page"`
- `.app-header` **80px** de altura, left 224
- `table.signals` ×2 (HOLD + EXIT), thead sticky copiado de `.monitor-theme .signals thead th`
- `.mobile-cards { display:none }` no desktop; `@media (max-width: 740px)` esconde `.table-wrap` — mesmo breakpoint do produto (`index.css` ~4186)

Landmarks da rota `/monitor` (`MonitorStatusTab.tsx` thead + `table.signals`): **presentes**. Não é galeria 2×2. `monitor-card` count = 0. Falta de listagem **não** se aplica.

---

## Overlay (browser detector)

Preflight mutável: `document.title` + `<script>` inline → `window.__impeccable_mut === true`.

HTTPS DEV não recebe `http://localhost/detect.js` (mixed content). Fallback: Playwright `addScriptTag({ path: detect-antipatterns-browser.js })` + `impeccableScan()`. Sem overlay visível numa tab `[Human]` headed.

Scan: 203 nós / ~254 hits. Contagem: undersized-ui-text 142, low-contrast 46, tiny-text 36, ai-color-palette 11, skipped-heading 3, side-tab 4, dark-glow 3, cramped-padding 2, tight-leading 4, line-length 1, overused-font 1, gradient-text 1, marquee 1.

Classificação: **FP de densidade do shell `/monitor`**. Produto já usa Inter, pills 10.5px `text-transform: uppercase`, `--text-muted #707a8a`, tags `.tag.strategy`, glow do `.dot.green`, border-left amarelo do nav ativo. Nenhum hit novo é o delta #792 (kv de risco / copy indisponível / residual EXIT). Não promove a P0/P1.

---

## Browser gate (asserts observáveis)

URL aberta: hash `1a1ff265…` = disco. HTTP 200 **não** usado como evidência de PASS.

### Desktop 1280×800

| assert | resultado |
|---|---|
| `table.signals` visível (2 tabelas, 1002×1226 a primeira) | PASS |
| thead visível (34px, display `table-header-group`) | PASS |
| cabeçalhos Status / Preço / Distância / 7d / Risco até stop / Tags | PASS (também `Par / Estratégia`; última col. `ações`) |
| botão Operar visível | PASS (12 no DOM; 8 visíveis — 4 hidden nos mobile-cards) |
| SOL HOLD: Compra + `$105.39` + `35.21%` + Médias Móveis | PASS — pill DOM `Compra`, `innerText` `COMPRA` via `text-transform: uppercase` do produto |
| ETH: `indisponível — dado não confiável` literal (travessão) | PASS (5 campos × 2 cópias DOM) |
| EXIT vazio ADA: `posição encerrada segundo a estratégia — sem risco residual mapeado` | PASS |
| HOLD SOL frase cruzar: `Se o preço cruzar $68.28, a leitura de posição deixa de valer segundo a estratégia (stop).` | PASS |
| Clique **Antes** muda o kv (não no-op) | PASS — `data-prototype-variant=before`; SOL kv de `distância até saída / 13.38% / …` → `<dt>compra</dt><dd>$91.40</dd>…` |
| `.table-wrap` visível; `.mobile-cards` `display:none` | PASS |
| 0 erros de console / pageerror com impacto | PASS (`console.errorCount=0`) |

### Mobile 390×844

| assert | resultado |
|---|---|
| tabela escondida (`table-wrap` display none; thead 0×0) | PASS |
| cards visíveis (`.mobile-cards` grid, 4 `mobile-card`) | PASS |
| risco legível | PASS — SOL kv 332×114, `35.21%` / `$105.39` / frase cruzar 332×52; ETH copy indisponível 332×184; ADA residual 332×77 |
| mesmos literais de copy | PASS |

---

## Issues

### P0
- nenhum. Landmarks da listagem `/monitor` presentes (não galeria 2×2). Digest servido = disco.

### P1
- nenhum.

### P2
- nenhum bloqueante. Overlay/CLI hits de densidade e Inter/glow são o shell copiado, não regressão do delta.

### P3
- Última coluna do thead diz `ações`; no produto o `<th className="actions-cell">` é vazio. Apply deve clonar o th vazio.
- Coluna `7d` é `-` (sem sparkline). Fixture; produto desenha path quando há pontos.
- `data-testid` duplicados (mobile-cards + detail-row) — espelho do produto, ruidoso no DOM do protótipo.

---

## Disposition

- Determinísticos CLI: 5, todos classificados (3 FP Inter, 1 FP advisory em-dash, 1 FP glow produto).
- Overlay scan: classificado FP de densidade do `/monitor`.
- Browser asserts críticos: verdes (incluindo Antes ≠ no-op).
- Console: 0 erros com impacto.
- Servido ≠ disco: **não**. Sem BLOCKED por digest.

## Verdict

**PASS**
