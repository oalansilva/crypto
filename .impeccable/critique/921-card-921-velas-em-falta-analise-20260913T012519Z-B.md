# Assessment B (detector + browser real) — card 921 · change card-921-velas-em-falta-analise

> Assessor B isolado, mesmo modelo inherit, sem transcript de A nem do pai. Sem nested-spawn.
> Nada movido (Status, branch, worktree); nenhuma edição fora de `.impeccable/critique/**`.
> Tokens parseáveis do `design.md` (rubrica D4): `UI impact: affected` · `live_route: /combo/results` · `surface: existing`.

```
Assessment B 921
digest_match: yes
detector: 0 findings
P0: nenhum
P1: nenhum
P3: SVG vs lightweight-charts; mock sintético; chart 240px mobile; velas calendário vs pregão #917; tabela Monitor scroll horizontal no 390; chrome inerte; th uppercase no innerText
verdict: PASS
```

- UTC: 2026-09-13T01:25:19Z
- Tuple (read-only): `bound_card=921` · `q_git=card-921-velas-em-falta-analise`. Sem `process_event`.
- Protótipo canónico: `frontend/public/prototypes/card-921-velas-em-falta-analise/index.html`
- Extra: `…/monitor.html`
- Servido: https://dev.criptofarol.com.br/prototypes/card-921-velas-em-falta-analise/
- Digest index: `c48651c3b95ff18d0a4b882e938279815a22dccd046ee6d30b4a08ec98beeac1` · 35170 bytes
- Digest monitor: `7ee6c81e1011e10306c0069ba51556b633cdd08ba42e20ca64b1cd07ea4015db` · 19363 bytes
- Rota viva: https://dev.criptofarol.com.br/combo/results e https://dev.criptofarol.com.br/monitor — **não autenticadas**. Playwright caiu em `/login` («Bem-vindo de volta»). `/login` **não** conta como a rota. Clone avaliado no proto HTTPS + landmarks do catálogo.
- Browser: Playwright Python + Chromium 1243 (`chrome-linux-arm64`) sob `xvfb-run -a`, `--no-sandbox`. Viewports `1440×900` e `390×844`. `colorScheme: dark`, `networkidle`. URL canónica do proto (não `file://`, não `/login`).
- Detector: `node .agents/skills/impeccable/scripts/detect.mjs --json` no HTML versionado (cwd worktree).
- Gate bruto: `.impeccable/critique/921-B-gate.json` · extra zoom: `.impeccable/critique/921-B-chart-extra.json`
- MCP cursor-ide-browser: tabs vazias / navigate recusou («No browser tab available»). Evidência = Playwright.

## 1. Digest servido == local

| Ponta | sha256 | bytes |
|---|---|---|
| Disco index | `c48651c3b95ff18d0a4b882e938279815a22dccd046ee6d30b4a08ec98beeac1` | 35170 |
| HTTPS GET `/prototypes/card-921-velas-em-falta-analise/` | `c48651c3b95ff18d0a4b882e938279815a22dccd046ee6d30b4a08ec98beeac1` | 35170 HTTP 200 |
| HTTPS GET `…/index.html` | mesmo | 35170 |
| Esperado (`design.md`) | mesmo | 35170 |
| Disco monitor | `7ee6c81e1011e10306c0069ba51556b633cdd08ba42e20ca64b1cd07ea4015db` | 19363 |
| HTTPS GET `…/monitor.html` | `7ee6c81e1011e10306c0069ba51556b633cdd08ba42e20ca64b1cd07ea4015db` | 19363 HTTP 200 |
| Esperado (`design.md`) | mesmo | 19363 |

HTTP 200 isolado **não** é o gate. Igualdade de sha256 + asserts de DOM/pixels abaixo.

## 2. Detector Impeccable

- Alvos: `index.html` e `monitor.html` da pasta do proto.
- Comando: `node .agents/skills/impeccable/scripts/detect.mjs --json` → `[]` nos dois, exit 0.
- **0 findings determinísticos.** Nada por classificar → sem bloqueio deste item.
- `.impeccable/critique/ignore.md` ausente.

## 3. Tokens + clone / fidelidade (superfície existing)

- `design.md` linhas próprias: `UI impact: affected` · `live_route: /combo/results` · `surface: existing`. **Não** é rota de catálogo emprestada.
- Catálogo `/combo/results`: `selectors: [".combo-page"]`, `texts: ["Lista de operações", "Análise da estratégia"]`.
- Catálogo `/monitor`: `selectors: ["table.signals"]`, `texts: ["Status", "Preço", "Distância", "7d", "Risco até stop", "Tags", "Operar", "Par / Estratégia"]`.
- Index no browser (1440 e 390): `.combo-page`=1; texto «Lista de operações»; `aria-label="Análise da estratégia"`; «Voltar aos favoritos»; chips BTC/USDT · 1D · Long / compra; Menos / Mais / Resetar; chip «180 velas».
- Extra `monitor.html` (não é index): `table.signals` + 8 cabeçalhos do catálogo via `th.textContent`. `innerText` do `body` devolve `STATUS`/`PREÇO` por `text-transform:uppercase` nos `th` — falso negativo do assert `texts_all`; landmarks estão no markup. **Não é P0.**
- 6 pares `COPIED:start`/`COPIED:end` no index; 2 no monitor. Index **não** é painel ANTES/DEPOIS nem galeria de N estados (`antes_depois_btns=0`, `gallery_states=0`).
- Toggle Antes/Depois: **ausente**. Picker 15m/1h/4h/1d no extra **muda markup** (`data-timeframe`, `aria-pressed`, classe `.on`).
- Monitor ao vivo autenticado: **não aberto** (login wall). Não usado como prova de clone.

## 4. Browser real — matriz (desktop 1440×900 e mobile 390×844)

Console error = 0; warning = 0; pageerror = 0; responses ≥400 = 0 (exceto o que o gate filtrou: nenhum). Overflow documento `scrollWidth==clientWidth` (1440 e 390 no index e no monitor).

Fluxo index: estado padrão → Menos (240) → Resetar (180) → Menos×11 até série toda (3314, 2017-08-17).
Fluxo monitor: 1d → 15m → 1h → 4h → 1d; `data-ma-ahead=0` em todos.

| # | Assert | Desktop | Mobile |
|---|---|---|---|
| 1 | Digest disco == HTTPS (não basta HTTP 200) | PASS | PASS |
| 2 | Landmark index `.combo-page` + «Lista de operações» + `aria-label="Análise da estratégia"` | PASS | PASS |
| 3 | Index **não** é painel ANTES/DEPOIS nem galeria de estados | PASS | PASS |
| 4 | `data-last-candle=data-last-ma=data-market-last=2026-09-12` · `data-ma-ahead=0` | PASS | PASS |
| 5 | Geometria: último ponto SMA rápida/lenta e `data-ma-end` no mesmo x da última vela (`ahead_px=0`) | PASS | PASS |
| 6 | Padrão «180 velas»; `viewport-to=2026-09-12`; seta `2017-10-05` ausente; `2026-07-10` presente | PASS | PASS |
| 7 | Operações=73 · `data-marker-count=146` · `data-list-count=73` · chip 1:1 | PASS | PASS |
| 8 | Menos uma vez → 240 velas, marker 146 intacto | PASS | PASS |
| 9 | Resetar → 180 velas, marker 146 intacto | PASS | PASS |
| 10 | Menos×11 → 3314 velas, `2017-10-05` presente, 73 Compra + 73 Venda, `data-ma-ahead=0` | PASS | PASS |
| 11 | Extra monitor: `table.signals` + 8 textos do catálogo (`th.textContent`) | PASS | PASS |
| 12 | Monitor 15m/1h/4h/1d: last candle = last MA = 2026-09-12, `ma-ahead=0`; picker muda markup | PASS | PASS |
| 13 | Zero botões Antes/Depois; index tem `.combo-page`; extra **não** usa `.combo-page` como página | PASS | PASS |
| 14 | a11y básica: `lang=pt-BR`, zoom `min-height` ≥44, `aria-label` Menos/Mais/Resetar, `aria-live` no chip | PASS | PASS |
| 15 | 0 console de impacto / 0 pageerror / 0 ≥400 / `sw==cw` | PASS | PASS |

Pixels desktop padrão: recorte 2026-03 → 2026-09; SMA vermelha + SMA azul terminam na última vela (dots no extremo direito); **sem buraco à direita**. Chip «Velas e médias até 2026-09-12». Full-zoom: eixo 2017-08 → 2026-09; triângulos densos; 1:1 intacto; médias ainda no extremo direito.

Pixels mobile: toolbar usável; chip 1:1 full-width; gráfico 240px; «Lista de operações» visível; MAs no extremo direito. Monitor 390: primeiras colunas visíveis; resto no `overflow:auto` do wrap (DOM tem os 8 `th`).

Rota viva **não usada** como prova (login wall). Browser correu proto HTTPS + tentou viva.

## 5. URLs abertas (viva vs proto vs login)

| Pedido | Final | Sessão | Uso |
|---|---|---|---|
| https://dev.criptofarol.com.br/prototypes/card-921-velas-em-falta-analise/ | mesma URL, HTTP 200, digest = disco | n/a (estático) | **prova de clone+delta** |
| https://dev.criptofarol.com.br/prototypes/card-921-velas-em-falta-analise/monitor.html | mesma, digest = disco | n/a | **prova extra /monitor** |
| https://dev.criptofarol.com.br/combo/results | **https://dev.criptofarol.com.br/login** («Bem-vindo de volta») | sem sessão | **não é a rota**; não prova clone |
| https://dev.criptofarol.com.br/monitor | **https://dev.criptofarol.com.br/login** | sem sessão | **não é a rota** |

Sem sessão, a comparação proto-vs-viva de landmarks da listagem **não corre**. Isso não é P0: o skill manda não tratar `/login` como a rota. Com sessão, A/B teria de confrontar landmarks viva↔proto; aqui a viva não autenticou.

## 6. Delta #921 observável

1. Última vela = mercado mock 2026-09-12 (não 15/08). PASS.
2. Média clipada: `data-ma-ahead=0`; geometria SVG x(last MA)=x(last candle); pixels sem linha solta à direita. PASS.
3. Recorte inicial ~180 velas. PASS.
4. #917 1:1 intacto: 73 ops, 146 setas, Menos revela 2017-10-05, Resetar não apaga série. PASS.
5. Extra Monitor: mesmo alinhamento em 15m/1h/4h/1d. PASS.

## 7. Brief / Critique / Audit / Trace (snapshot only)

**Brief recorte (Operate):** clone `/combo/results` + extra `/monitor`; delta = velas e médias no mesmo recorte até o presente. Sem redesign.

**Personas:**
- Operador na análise dos Favoritos: precisa ver preço até onde a tela afirma estar. Proto mostra série até 2026-09-12 e médias no mesmo x.
- Operador no Monitor (1d → 15m): picker muda o recorte sem soltar a média à frente.
- Operador mobile: listagem+gráfico usáveis; tabela Monitor exige scroll horizontal (clone da densidade viva).

**Carga cognitiva:** uma página de análise (não galeria). Delta anunciado num chip («Velas e médias até 2026-09-12») sem novo chrome. Menos/Mais/Resetar inalterados.

**Heurísticas (snapshot; não no retorno ao pai):**

| # | Heurística | Score 0–4 | Nota |
|---|---|---|---|
| 1 | Visibilidade do estado | 4 | Chip 180 velas + série até 2026-09-12 + 1:1 |
| 2 | Match mundo real | 4 | Copy clone da análise; delta em linguagem de velas/médias |
| 3 | Controlo do utilizador | 4 | Menos/Mais/Resetar; picker TF no extra |
| 4 | Consistência | 4 | Shell AppNav + tokens da folha; extra não usurpa o index |
| 5 | Prevenção de erro | 3 | Proto não demonstra timeout→snapshot (estado intermédio é contrato Apply) |
| 6 | Reconhecimento vs recall | 4 | Landmarks da listagem presentes |
| 7 | Flexibilidade | 3 | Zoom/pan no index; extra sem Menos (fora do delta deste card) |
| 8 | Estética e minimalismo | 4 | Sem painel ANTES/DEPOIS |
| 9 | Recuperação de erro | 3 | Chrome de zoom recupera recorte; sem estado de erro de série viva |
| 10 | Ajuda | 3 | «Roda do mouse: zoom» clonado; inerte no touch |

**Audit a11y/responsive:** alvos zoom ≥44px; `lang=pt-BR`; foco visível no CSS; palco `tabindex=0`; `aria-live` no chip. Mobile esconde sidebar (clone). Detector `[]`.

**Trace:** HTTPS proto 200 + sha256 = disco → detector `[]` → Playwright 1440/390 index+monitor → zoom #917 → viva `/combo/results` e `/monitor` → `/login` (não usado).

## 8. Findings (toda finding classificada)

### P0 — nenhum

Tokens parseáveis e `live_route` é `/combo/results`. Landmarks 3/3 no index; 8/8 no extra via `th`. Digest servido == local. Clone+delta (não ANTES/DEPOIS, não galeria). Média **não** à frente da última vela (`data-ma-ahead=0`, geometria 0px, pixels sem buraco). #917 1:1 observável. `/login` não usado como prova. Fidelidade ok → não BLOCKED.

### P1 — nenhum

Aceite visível nos dois viewports. Detector `[]`. Botões de zoom com alvo ≥44px. Sem overflow horizontal de documento. Picker TF muda markup.

### P3 — aceites (Apply / clone chrome; não reabrir como P0/P1)

- **P3-1 SVG do proto vs canvas lightweight-charts.** Já aceite no `design.md`.
- **P3-2 Writer observador / teto 40 pares / intervalos default / timeout ms / `CURRENT_CHART_CANDLE_LIMIT`.** Já aceite.
- **P3-3 Mock sintético** (interpolação de trades no index; seno no monitor). Critério «última vela = mercado» no Apply na página viva.
- **P3-4 `.chart-stage` 240px no ≤1023px** vs `min-h` vivo.
- **P3-5 Velas calendário (inclui sáb/dom)** → viewport inicial 2026-03-17…09-12 em 180 barras, vs pregão do #917 que começava ~2026-01. Chip continua «180 velas».
- **P3-6 Tabela Monitor no 390:** colunas 7d/Risco/Tags/Operar no overflow horizontal do wrap; DOM tem os 8 `th`.
- **P3-7 Chrome inerte:** hamburger / Recolher / nav `href=#`; «Roda do mouse: zoom» no touch.
- **P3-8 Extra monitor sem Menos/Mais/Resetar** — fora do delta (alinhamento velas/médias); zoom ~180 fixo no extra.

Observações (não-findings): `innerText` uppercase nos `th` do Monitor não esconde landmarks (`textContent` correcto). Overlay `detect.js` não injectado — evidência = CLI + Playwright no proto servido. MCP IDE browser indisponível nesta sessão.

## 9. Veredito

**PASS** — zero P0/P1 abertos; detector `[]` classificado; digest idêntico; index clona `/combo/results` (não painel ANTES/DEPOIS); extra clona landmarks de `/monitor`; delta observável (last candle alinhada à last MA, recorte 180, #917 1:1); `/login` não usado como prova da rota; matriz desktop+mobile. HTTP 200 sozinho não sustentaria este veredito.

Disposition: crítico não pede rework. P3 aceites no Apply.

## 10. Referências

- Proto canónico: https://dev.criptofarol.com.br/prototypes/card-921-velas-em-falta-analise/
- Extra: https://dev.criptofarol.com.br/prototypes/card-921-velas-em-falta-analise/monitor.html
- Digest index: `c48651c3b95ff18d0a4b882e938279815a22dccd046ee6d30b4a08ec98beeac1`
- Digest monitor: `7ee6c81e1011e10306c0069ba51556b633cdd08ba42e20ca64b1cd07ea4015db`
- Snapshot: `.impeccable/critique/921-card-921-velas-em-falta-analise-20260913T012519Z-B.md`
- Gate bruto: `.impeccable/critique/921-B-gate.json`
- PNGs: `921-B-{desktop-1440x900,mobile-390x844}-{index-default,index-menos,monitor-1d,monitor-after-tf}.png`, `921-B-{desktop,mobile}-index-{chart,fullzoom}.png`, `921-B-desktop-monitor-chart-close.png`, `921-B-live-{combo_results,monitor}.png`
