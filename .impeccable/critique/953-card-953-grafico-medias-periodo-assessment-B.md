# Assessment B (detector + browser real) — card 953 · change card-953-grafico-medias-periodo

> Assessor B isolado, mesmo modelo, sem transcript de A nem do pai. Sem nested-spawn.
> Nada movido (Status, branch, worktree); nenhuma edição fora deste ficheiro, PNGs `953-B-*` e `953-B-gate.json`.
> Tokens parseáveis do `design.md` (rubrica D4): `UI impact: affected` · `live_route: /combo/results` · `surface: existing`.

```
Assessment B 953
digest_match: yes
detector: 1 finding (flat-type-hierarchy em monitor.html) classificado P3
P0: nenhum
P1: nenhum
P3: warmup SMA; clip #921 / canvas vs SVG; mock senóide Monitor; thead clip 390; alvos 32px; slop flat-type-hierarchy; DELTA:start=0
verdict: PASS
```

- UTC: 2026-09-16T18:34Z
- Tuple (read-only): `bound_card=953` · `q_git=card-953-grafico-medias-periodo`. Sem `process_event`. Status GraphQL = **Design** (item `PVTI_lAHOAAHtBM4BV8b2zg7R-pc`, Project 1). Não arrastado.
- Briefing REST: `gh api repos/oalansilva/crypto/issues/953` → #953 open, *«Gráfico: velas do período inteiro sem médias calculadas»*. Contrato: velas **e** linhas da estratégia no mesmo recorte carregado (análise + Monitor); 6m/2a não alargam a 2017; zoom 180; #917/#921/#949 intactos.
- Protótipo canónico: `frontend/public/prototypes/card-953-grafico-medias-periodo/index.html`
- Servido: https://dev.criptofarol.com.br/prototypes/card-953-grafico-medias-periodo/
- Extra: `monitor.html` (mesma pasta/URL). Sem `select.html`.
- Digest index: `7f848b6cd861dff02649aebc04dbc3fb670bc9d3c05dbabfe3c9e9542e16ee4e` · 37236 bytes
- Digest monitor: `c59eec83bc3df59c0912f936b5b958eaecb6192eccb46cfcc0629043b242ac01` · 26095 bytes
- Rota viva `/combo/results` **não usada como prova** (não autenticada neste filho). Clone avaliado no proto HTTPS + landmarks do catálogo HEAD.
- Browser: Playwright Python + Chromium 1243 (`chrome-linux-arm64`) sob `xvfb-run -a`, `--no-sandbox`. Viewports 1440×900 e 390×844. `colorScheme: dark`. URL canónica do proto (não `file://`, não `/login`).
- Detector: `node .agents/skills/impeccable/scripts/detect.mjs --json` no HTML versionado (cwd worktree).

## 1. Digest servido == local

| Ponta | sha256 | bytes |
|---|---|---|
| Disco `index.html` | `7f848b6cd861dff02649aebc04dbc3fb670bc9d3c05dbabfe3c9e9542e16ee4e` | 37236 |
| HTTPS GET `/prototypes/card-953-grafico-medias-periodo/` | idem | 37236 HTTP 200 |
| HTTPS GET `…/index.html` | idem | 37236 |
| Esperado (prompt) | idem | 37236 |
| Disco `monitor.html` | `c59eec83bc3df59c0912f936b5b958eaecb6192eccb46cfcc0629043b242ac01` | 26095 |
| HTTPS GET `…/monitor.html` | idem | 26095 HTTP 200 |
| Esperado (prompt) | idem | 26095 |

`cmp` disco vs HTTPS nas duas pontas: **IDENTICAL**. HTTP 200 isolado **não** é o gate.

## 2. Detector Impeccable

- Alvos: os dois HTML do proto + scan da pasta.
- `index.html` → `[]`, exit 0.
- `monitor.html` exit 2 → 1 finding `flat-type-hierarchy` (L24: `Sizes: 12px, 13px, 20px (ratio 1.7:1)`). Pasta = o mesmo finding.
- `.impeccable/critique/ignore.md` ausente.
- **Classificação:** P3 slop de tipografia do clone `/monitor` (chrome incumbente). **Não** é contrato de recorte/linhas. **Não** reabre como P0/P1. `side-tab` (aceite no `design.md`) **não** disparou neste HTML.

## 3. Tokens + clone / fidelidade (superfície existing)

- `design.md` linhas próprias: `UI impact: affected` · `live_route: /combo/results` · `surface: existing`. **Não** é rota de catálogo emprestada (`/favorites`, `/combo/discovery`, `/combo/select`).
- Catálogo HEAD `/combo/results`: `selectors: [".combo-page"]`, `texts: ["Lista de operações", "Análise da estratégia"]`.
- Catálogo HEAD `/monitor`: `selectors: ["table.signals"]`, `texts: ["Status", "Preço", "Distância", "7d", "Risco até stop", "Tags", "Operar", "Par / Estratégia"]`.
- Index no browser (1440 e 390): `.combo-page`=1; «Lista de operações»; `aria-label="Análise da estratégia"`; «Voltar aos favoritos»; chips BTC/USDT · 1D · Long / compra; chip **2 anos · 16/09/2024 → 16/09/2026**; Menos / Mais / Resetar; chip «180 velas».
- Extra `monitor.html` (não é index): `table.signals` + 8 `th.textContent` do catálogo. `innerText` do body uppercase nos `th` (clone vivo) — landmarks no markup. Extra **não** usa `.combo-page` como página.
- 6 pares `COPIED:start`/`COPIED:end` no index; 2 no monitor. `DELTA:start`=0 — o delta é JS (SMA/MACD no recorte), não região nova. **Não** é painel das N.
- Toggle Antes/Depois: **ausente**. Botões «Antes»/«Depois» = 0. Comentário HTML «NÃO é painel ANTES/DEPOIS» não é painel. URL canónica = `index.html`.
- `/login` não usado.

## 4. Browser real — matriz (desktop 1440×900 e mobile 390×844)

Console error = 0; warning = 0; pageerror = 0; responses ≥400 no proto = 0. Overflow documento `scrollWidth==clientWidth` (1440 e 390, index e monitor). `desktop_eq_mobile_index_period: true`. Gate bruto: `.impeccable/critique/953-B-gate.json`.

Falsos FAIL do script inicial (`clip_geom`, `full_ahead`, `mon_clip_geom`): parser `Number("L1076.0")=NaN` no `d` do path. Reprobe com regex de números: open `aheadPx=0` (último ponto SMA = `cx` do `data-ma-end` = centro da última vela). Full: path e `data-ma-end` em x=1076; 1.4px vs último `<rect>` amostrado (`step>1`) — não é linha à frente. `data-ma-ahead="0"` passou nos dois viewports. **Não** são P0/P1.

| # | Assert | Desktop | Mobile |
|---|---|---|---|
| 1 | Digest disco == HTTPS (não basta HTTP 200) | PASS | PASS |
| 2 | Tokens `UI impact: affected` / `live_route: /combo/results` / `surface: existing` | PASS | — |
| 3 | Landmarks `/combo/results`: `.combo-page` + «Lista de operações» + `aria-label="Análise da estratégia"` | PASS | PASS |
| 4 | COPIED 6/6; zero botões Antes/Depois; sem painel das N; index ≠ galeria | PASS | PASS |
| 5 | Ao abrir: **180 velas**; SMA 9/21 no recorte visível; `viewportFrom=2026-03-21` → `2026-09-16` | PASS | PASS |
| 6 | Chip favorito **2 anos · 16/09/2024 → 16/09/2026**; `data-whole-market="0"`; innerText **sem** 2017 | PASS | PASS |
| 7 | `data-ma-ahead="0"`; último ponto SMA = última vela (`aheadPx=0` no reprobe) | PASS | PASS |
| 8 | 1:1 #917: lista 16 · setas 32; métrica Operações 16 | PASS | PASS |
| 9 | Menos ×2 → **320 velas**; paths SMA presentes; sem 2017 | PASS | PASS |
| 10 | Menos até ao fundo → **731 velas**, `viewportFrom=2024-09-16`, `linesOnOld=1`, SMA no histórico antigo | PASS | PASS |
| 11 | Resetar → 180; linhas da série permanecem; `linesOnOld=0` (recorte recente, não «abrir no período inteiro») | PASS | PASS |
| 12 | Extra monitor: `table.signals` + 8 textos do catálogo; 180 velas; 731 carregadas; clip 0 | PASS | PASS (thead clip incumbente) |
| 13 | Monitor Menos → 320; fundo 731 + `linesOnOld=1`; TF 1h não vira «todo» nem 2017 | PASS | PASS |
| 14 | Clique SOL: painel **Painel macd: MACD**; 2 paths no mesmo recorte; linha não escondida | PASS | PASS |
| 15 | 0 console / 0 pageerror / 0 ≥400 / `sw==cw` | PASS | PASS |
| 16 | a11y: `lang=pt-BR`; zoom `min-height` ≥44; `aria-live` no chip; palco `tabindex=0` | PASS | PASS |

Pixels index desktop: chip 2 anos 16/09/2024 → 16/09/2026; 180 velas; SMA vermelha + azul no recorte Mar–Set 2026; dots no extremo direito; lista 16 ops (sem 2017). Full: eixo 2024-09 → 2026-09-16; 731 velas; linhas atravessam o histórico antigo; clip à última vela.

Pixels index mobile: mesmo período e 16 ops em cards; 180 ao abrir; full 731 / 2024-09 → 2026-09-16 com linhas. Gráfico ~estreito (clone da densidade viva).

Pixels monitor desktop: tabela BTC+SOL; 731 velas carregadas · não todo o mercado; SMA 9/21 até 2026-09-16. SOL: EMA 12/26 + painel MACD (2 linhas) no mesmo recorte.

Pixels monitor mobile: primeiras colunas da tabela visíveis; resto no wrap; SMA/EMA + MACD visíveis; chip 180.

Rota viva **não usada**. Browser correu só no proto.

## 5. Findings (toda finding classificada)

### P0 — nenhum

Clone `/combo/results` com landmarks do catálogo; extra `/monitor` com `table.signals`; copied 6+2 pares; sem painel ANTES/DEPOIS / das N; favorito 2 anos **não** mostra 2017; zoom 180 ao abrir; Menos revela 2024 com linha; `data-ma-ahead=0` e geometria sem buraco à direita; 1:1 16↔32; digest HTTPS == disco; detector classificado. Fidelidade + contrato visível ok → não BLOCKED.

### P1 — nenhum

Delta observável nos dois viewports: linhas no recorte visível ao abrir e nas velas antigas após Menos. 6m/2a não alargam a «todo o mercado» (index `periodStart=2024-09-16`; monitor `wholeMarket=0` em 1d e 1h). Painel de baixo MACD só na estratégia que o gráfico já o desenha (SOL). Resetar não apaga a série nem abre enquadrado no período inteiro.

### P3 — aceites (Apply / clone chrome; não reabrir como P0/P1)

- **P3-1 Warmup SMA:** no full, path SMA 9 começa depois das primeiras N−1 velas (`nPts` 723 de 731). Já no `design.md` («aquecimento não é o furo»).
- **P3-2 Clip #921 / canvas vs SVG:** proto é SVG; produto vivo é lightweight-charts. `data-ma-ahead="0"` + último ponto no x da última vela. Já P3 de Apply.
- **P3-3 Mock senóide no Monitor** e série interpolada na análise. Já «Mock sem loading/vazio/erro de rede».
- **P3-4 Thead / colunas clip no 390 do extra Monitor.** Landmarks via `th.textContent`; clone da densidade viva.
- **P3-5 Alvos 32px / gráfico baixo no mobile.** Zoom ≥44px; palco estreito é incumbente (#921 P3).
- **P3-6 Detector `flat-type-hierarchy`** em `monitor.html` L24 (12px vs 13px). Slop de clone, não contrato de linhas.
- **P3-7 `DELTA:start=0`** e array `TRADES` com 2017 no `<script>` (filtrado do DOM visível). Nomes internos / recompute vs extend — já P3 de Apply.
- **P3-8 Detector `side-tab` / 32px** (aceite no `design.md`) não disparou neste HTML; fica no contrato de Apply do clone.

Observações (não-findings): overlay `detect.js` não injectado — evidência = CLI + Playwright no proto servido. GET `/combo/results` não usado. Nav Monitor no extra = clone `/monitor`, não o index. Proto 6 meses não tem ecrã próprio; o canónico é 2 anos + TF 1h no Monitor.

## 6. Veredito

**PASS** — zero P0/P1 abertos; detector `flat-type-hierarchy` classificado P3; digest idêntico nas 2 pontas; clone+delta (não ANTES/DEPOIS); `/login` não usado; matriz visível desktop+mobile no index e extra monitor (zoom 180, Menos com linhas nas velas antigas, 2a sem 2017, clip #921, MACD no mesmo recorte). HTTP 200 sozinho não sustentaria este veredito.

Disposition: crítico não pede rework. P3 aceites no Apply.

## 7. Referências

- Proto URL: https://dev.criptofarol.com.br/prototypes/card-953-grafico-medias-periodo/
- Extra: https://dev.criptofarol.com.br/prototypes/card-953-grafico-medias-periodo/monitor.html
- Digest index: `7f848b6cd861dff02649aebc04dbc3fb670bc9d3c05dbabfe3c9e9542e16ee4e`
- Digest monitor: `c59eec83bc3df59c0912f936b5b958eaecb6192eccb46cfcc0629043b242ac01`
- Snapshot: `.impeccable/critique/953-card-953-grafico-medias-periodo-assessment-B.md`
- Gate bruto: `.impeccable/critique/953-B-gate.json`
- PNGs: `953-B-desktop-1440x900-index.png`, `953-B-desktop-1440x900-index-menos.png`, `953-B-desktop-1440x900-monitor.png`, `953-B-desktop-1440x900-monitor-sol.png`, `953-B-mobile-390x844-index.png`, `953-B-mobile-390x844-index-menos.png`, `953-B-mobile-390x844-monitor.png`, `953-B-mobile-390x844-monitor-sol.png`

proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)
