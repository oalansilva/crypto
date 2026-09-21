# Assessment B (detector + browser real) — card 994 · rework 1 · change card-994-monitor-multiplos-timeframes

> Assessor B isolado, mesmo modelo, sem transcript de A nem do pai. Sem nested-spawn.
> Nada movido (Status, branch, worktree); nenhuma edição fora deste snapshot, PNGs `994-B-*`, `994-B-gate.py`, `994-B-gate.json` e dumps do detector.
> Tokens parseáveis do `design.md` (rubrica D4, não reabrir parser): `UI impact: affected` · `live_route: /monitor` · `surface: existing`.

```
Assessment B 994 rework 1
digest_match: yes
detector CLI: [] (index, exit 0, 0 rules)
detector browser overlay: 52 overlays · 79 nits (low-contrast, undersized-ui-text, tiny-text, cramped-padding, ai-color-palette, gpt-thin-border-wide-shadow, text-occlusion, skipped-heading, gradient-text, marquee) — P3 clone chrome; nenhum fura o contrato do seletor
P0: nenhum
P1: nenhum
P2: nenhum
P3: overlay ChartModal vs dockado; clip Operar; cards 390; KPIs não seguem filtro; gráfico dockado permanece BTC no filtro 1d; nits visuais do overlay
verdict: PASS
```

- UTC: 2026-09-21T00:17Z
- Tuple (read-only): `q` ausente na Moore page (`.grok/rules/process-fsm-page.md` missing) · `bound_card=994` · `q_git=card-994-monitor-multiplos-timeframes` via `scripts/process-fsm/resolve.py`. GraphQL pontual: **Status=Design**. Sem `process_event`. Sem `move_agent_to_root`.
- Status GraphQL pontual (`repository.issue(number:994).projectItems`): **Design** · item `PVTI_lAHOAAHtBM4BV8b2zg7vsaw` · Project 1 `oalansilva`. MUST NOT `gh project item-list`.
- REST issue #994: OPEN *«Monitor: respeitar múltiplos timeframes (filtro, ficha e Abrir gráfico)»*.
- Protótipo canónico: `frontend/public/prototypes/card-994-monitor-multiplos-timeframes/index.html`
- Servido para o browser: **HTTP local** `frontend/public` (`http://127.0.0.1:<ephemeral>/prototypes/card-994-monitor-multiplos-timeframes/`). HTTPS DEV medido e **idêntico**; Chrome de `/login` **não** é evidência.
- Sem irmão HTML. `erro.html` / `favorites.html` / `filtro.html` / `grafico.html` disco ausente; HTTPS 404.
- Digest esperado: `f79ceb83f3d16a0cd03d2facf0937234170206da2996897796050c3f8e18628b` · 39552 B. Disco MUST == HTTPS: **IDENTICAL**.
- Rota viva `https://dev.criptofarol.com.br/monitor` → browser **`/login`**. Login **não** é a rota; **não** autoriza PASS de clone.
- Browser: Playwright Python + Chromium 1243 (`chrome-linux-arm64`) headless `--no-sandbox`. Viewports **1440×900** e **390×844**. `colorScheme: dark`. Não `file://`.
- Detector CLI: `node .agents/skills/impeccable/scripts/detect.mjs --json` no HTML versionado.
- Overlay: mutation preflight OK (`document.title` + `<script>`). `live-server.mjs` **não** arrancado (fence de escrita: só `.impeccable/critique/**`). Inject in-page de `detect-antipatterns-browser.js` **depois** dos screenshots de contrato.

## 1. Digest servido == local

| Ponta | sha256 | bytes |
|---|---|---|
| Disco `index.html` | `f79ceb83f3d16a0cd03d2facf0937234170206da2996897796050c3f8e18628b` | 39552 |
| HTTPS GET `/prototypes/card-994-monitor-multiplos-timeframes/` | idem | 39552 HTTP 200 · **IDENTICAL** |
| HTTPS GET `…/index.html` | idem | 39552 · **IDENTICAL** |
| Esperado (prompt) | idem | 39552 |
| Browser gate | local static de disco | 39552 |

HTTP 200 isolado **não** é o gate. Disco == HTTPS == esperado → **digest_match: yes**. Avaliação no disco servido localmente.

## 2. Detector Impeccable

- CLI alvo: `index.html`. Comando pedido → `[]`, exit 0. **0 findings. 0 rule names.**
- Dump: `.impeccable/critique/994-B-detector.json` (CLI + resumo browser) e `.impeccable/critique/994-B-detector-browser.json`.
- Overlay browser (mutation disponível): 52 overlays visíveis; `impeccableDetect()` 55 elementos / **79** nits aninhados. Regras: `undersized-ui-text` 38, `low-contrast` 28, `text-occlusion` 3, `tiny-text` 2, `cramped-padding` 2, `ai-color-palette` 2, `gpt-thin-border-wide-shadow` 1, `skipped-heading` 1, `gradient-text` 1, `marquee` 1. Severidade warning/advisory. **Nenhum** aponta seletor de TF do gráfico, `data-chart-tf`, 15m/1h/1d, ou «Estratégia (4H)».
- **Classificação D4:** nits visuais do detector = **P3**. Seletor ainda lá seria P0 — **não está**.

## 3. Tokens D4 + clone / fidelidade (`surface: existing`)

- `design.md` linhas próprias (18–20): `UI impact: affected` · `live_route: /monitor` · `surface: existing`. **PASS** rubrica D4. Não é rota de catálogo emprestada. Sem extra `/favorites`.
- Catálogo `route-landmarks.yaml` `/monitor`: `table.signals` + texts Status, Preço, Distância, 7d (COPIED comment), Risco até stop, Tags, Operar, Par / Estratégia. Th visível da coluna de spark = **Gráfico**.
- Index 1440 e 390: `table.signals`=**2**. Sidebar desktop `offsetWidth=224`. Mobile tabela `display:none` (clone); cards BTC 4h / ETH 1d.
- COPIED 9/9; utf-8 copiada 21255 incl / **21057** excl (> 0); total 39552; `DELTA:start`=0.
- Toggle Antes/Depois: **ausente**. URL canónica = `index.html`.

## 4. Contrato visível do rework (seletor do gráfico FORA)

| Contrato | Desktop 1440×900 | Mobile 390×844 |
|---|---|---|
| AUSENTE `data-chart-tf` | PASS 0 | PASS 0 |
| AUSENTE `aria-label="Selecionar timeframe do gráfico"` | PASS 0 | PASS 0 |
| AUSENTE botões 15m / 1h / 1d do gráfico | PASS 0/0/0 | PASS 0/0/0 |
| AUSENTE «Estratégia (4H)» como botão | PASS 0 botões; copy ausente no body/HTML | PASS |
| AUSENTE JS que troca TF do gráfico | PASS (script só filtra `#tf-filter`; sem `chart-timeframe` / `setChart`) | PASS |
| PRESENTE rótulo só de leitura `Estratégia · 4h` (`data-testid="chart-strategy-tf"`, tag `P`) | PASS | PASS |
| `#tf-filter` Todos / 4h / 1d | PASS | PASS |
| `pair-tf` 4h no BTC | PASS | PASS (card `BTC/USDT 4h`) |
| AUSENTE «Gráfico 1d» / «tf 1d» | PASS | PASS |
| Coluna **Gráfico** | PASS th `GRÁFICO` | PASS thead no DOM |
| Landmarks `table.signals` + Status/Preço/Distância/Tags/Operar/Par / Estratégia | PASS | PASS (cards + thead) |
| Filtro 4h esconde ETH 1d; mantém BTC | PASS `1 resultados`; ETH `hidden` | PASS card ETH ausente |
| Filtro 1d esconde BTC 4h; mantém ETH | PASS Em posição (0); só ETH | PASS |
| Todos mostra ambos | PASS | PASS |

Pixels desktop index: BTC/USDT **4h** + Médias Móveis: Tendência em Virada; ETH/USDT **1d**; Timeframe: Todos; coluna GRÁFICO; ficha badge **4h**; gráfico dockado com **Estratégia · 4h** e 42 velas 4h. Sem 15m/1h/1d.

Pixels filtro 4h: select `4h`; 1 resultado; ETH some; BTC 4h + rótulo 4h permanecem.

Pixels filtro 1d: select `1d`; Em posição (0); só ETH/USDT 1d na lista; gráfico dockado continua a cena BTC 4h (P3 proto aceite).

Pixels gráfico: toolbar só de leitura — `Estratégia · 4h` + chip `42 velas · 4h`. Sem `role="group"` de selecção.

Pixels mobile: cards BTC 4h / ETH 1d; filtro Todos/4h/1d; mobilebar `BTC/USDT 4h`; gráfico readonly 4h.

## 5. Browser real — matriz (desktop 1440×900 e mobile 390×844)

Console error = 0; pageerror = 0; responses ≥400 no proto = 0. Overflow documento sem overlay: 1440==1440; 390==390. Gate bruto: `.impeccable/critique/994-B-gate.json`. Asserts **138**, failed []. Desktop 56 PASS · mobile 59 PASS.

| # | Assert | Desktop 1440×900 | Mobile 390×844 |
|---|---|---|---|
| 1 | Digest disco == HTTPS == esperado | PASS | PASS |
| 2 | Tokens D4 `UI impact: affected` / `live_route: /monitor` / `surface: existing` | PASS | — |
| 3 | Landmarks `/monitor` + coluna Gráfico | PASS | PASS (cards + thead) |
| 4 | Sem seletor de TF do gráfico (data-chart-tf, aria, 15m/1h/1d, Estratégia (4H), JS) | PASS | PASS |
| 5 | Rótulo readonly `Estratégia · 4h` | PASS | PASS |
| 6 | Filtro lista 4h / 1d / Todos | PASS | PASS |
| 7 | Sem «Gráfico 1d» / «tf 1d»; pair-tf BTC 4h | PASS | PASS |
| 8 | Sem extra `/favorites`; 0 console / 0 pageerror | PASS | PASS |
| 9 | Detector CLI `[]` | PASS | — |
| 10 | Live `/monitor` sem sessão → `/login`; login **não** usado como PASS | PASS | — |
| 11 | Overlay detector injectado (mutation OK) | PASS 52 overlays | inject noutro viewport |

Rota viva **não usada como prova de clone**.

## 6. Findings (toda finding classificada)

### P0 — nenhum

Seletor do gráfico **ausente**. Contrato do rework visível: gráfico só exibe o TF da estratégia. Clone `/monitor` com landmarks; copied 21057 > 0; digest idêntico; detector CLI `[]`. **não BLOCKED**.

### P1 — nenhum

Uma URL canónica mostra lista + gráfico. Sem extra `/favorites`. Login vivo não foi PASS. Filtro 4h/1d/Todos altera a listing. Segundo TF «Gráfico 1d» / «tf 1d» **ausente**.

### P2 — nenhum

### P3 — aceites (Apply / clone chrome; não reabrir como P0/P1)

- **P3-1 Overlay vivo vs proto dockado.** Gráfico abaixo da lista no mesmo URL. Apply mantém `ChartModal` overlay. Aceite (prompt).
- **P3-2 Clip desktop da coluna Operar** («Ver Trades» / «Operar» empilhados). Incumbente da board.
- **P3-3 Cards mobile** (tabela `display:none`) — clone vivo.
- **P3-4 Mobilebar `BTC/USDT 4h`** — chrome; não é seletor. No filtro 1d o chrome do bar não muda (proto).
- **P3-5 `DELTA:start`=0:** delta em tbody/filtro/spark/modal.
- **P3-6 KPIs Total/Em posição do topo não seguem o filtro** (continuam 1/1/2/2); `result-count` e `(n)` da secção seguem.
- **P3-7 Gráfico dockado permanece BTC quando o filtro é 1d.** Contrato visível é TF da estratégia na cena BTC; overlay vivo fecha com o modal.
- **P3-8 Detector browser nits** (`undersized-ui-text`, `low-contrast` #707a8a/#181a20, `tiny-text`, `cramped-padding`, `ai-color-palette` nos pair-icons, `skipped-heading` h1→h3, `gradient-text`, `text-occlusion`, `gpt-thin-border-wide-shadow`, `marquee` falso-positivo de overlay). Clone `DESIGN.md`. CLI estático não dispara. **Não furam o contrato.**
- **P3-9 Stitch de header sticky nos PNG full-page.** Artefacto Playwright.

## 7. Veredito

**PASS** — zero P0/P1/P2; CLI detector `[]`; overlay browser só P3 de clone; digest disco == HTTPS == `f79ceb83…8628b`; seletor de TF do gráfico **fora**; rótulo `Estratégia · 4h`; filtro da lista intacto. HTTP 200 sozinho não sustentaria este veredito. `/login` não usado.

Disposition: crítico não pede rework. P3 aceites no Apply.

## 8. Referências

- Proto disco (browser): local `frontend/public/prototypes/card-994-monitor-multiplos-timeframes/`
- Proto HTTPS (digest only): https://dev.criptofarol.com.br/prototypes/card-994-monitor-multiplos-timeframes/
- Digest index: `f79ceb83f3d16a0cd03d2facf0937234170206da2996897796050c3f8e18628b` · 39552 B
- Snapshot: `.impeccable/critique/994-card-994-monitor-multiplos-timeframes-assessment-B.md`
- Gate bruto: `.impeccable/critique/994-B-gate.json`
- Detector dump: `.impeccable/critique/994-B-detector.json` · `.impeccable/critique/994-B-detector-browser.json`
- PNGs: `994-B-desktop-1440x900-index.png`, `994-B-desktop-1440x900-filtro-4h.png`, `994-B-desktop-1440x900-filtro-1d.png`, `994-B-desktop-1440x900-grafico-readonly.png`, `994-B-desktop-1440x900-overlay.png`, `994-B-mobile-390x844-index.png`, `994-B-mobile-390x844-filtro-4h.png`, `994-B-mobile-390x844-filtro-1d.png`, `994-B-mobile-390x844-grafico-readonly.png`

proxy modelo: Assessment B → Grok 4.6 (grok-4.6)
