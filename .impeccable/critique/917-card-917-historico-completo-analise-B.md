# Assessment B (detector + browser real) — card 917 · change card-917-historico-completo-analise

> Assessor B isolado, mesmo modelo, sem transcript de A nem do pai. Sem nested-spawn.
> Nada movido (Status, branch, worktree); nenhuma edição fora deste ficheiro, PNGs `917-B-*` e `917-B-gate.json`.
> Tokens parseáveis do `design.md` (rubrica D4): `UI impact: affected` · `live_route: /combo/results` · `surface: existing`.

```
Assessment B 917
digest_match: yes
detector: 0 findings
P0: nenhum
P1: nenhum
P3: SVG vs lightweight-charts; mock BTC 1d; chart 240px mobile; labels Menos visíveis no 390 (vivo esconde); chip 1:1 full-width; velas skip fim-de-semana; zoom ancora à direita; chrome inerte
verdict: PASS
```

- UTC: 2026-09-12T18:34Z
- Tuple (read-only): `bound_card=917` · `q_git=card-917-historico-completo-analise`. Sem `process_event`.
- Protótipo: `frontend/public/prototypes/card-917-historico-completo-analise/index.html`
- Servido: https://dev.criptofarol.com.br/prototypes/card-917-historico-completo-analise/
- Digest: `3f4b61913528622ecb87ca57ef6ae1e7cda1a89b835d6f05bc6bdb72b141db38` · 32754 bytes
- Rota viva: https://dev.criptofarol.com.br/combo/results — **não autenticada**. Playwright caiu em `/login` («Bem-vindo de volta»). `/login` **não** conta como a rota. Clone avaliado no proto HTTPS + landmarks do catálogo + chrome de `ComboResultsPage` / `StrategyChartSurface` no worktree.
- Browser: Playwright Python + Chromium 1243 (`chrome-linux-arm64`) sob `xvfb-run -a`, `--no-sandbox`. Viewports `1440×900` e `390×844`. `colorScheme: dark`, `networkidle`. URL canónica do proto (não `file://`, não `/login`).
- Detector: `node .agents/skills/impeccable/scripts/detect.mjs --json` no HTML versionado (cwd worktree).

## 1. Digest servido == local

| Ponta | sha256 | bytes |
|---|---|---|
| Disco | `3f4b61913528622ecb87ca57ef6ae1e7cda1a89b835d6f05bc6bdb72b141db38` | 32754 |
| HTTPS GET `/prototypes/card-917-historico-completo-analise/` | `3f4b61913528622ecb87ca57ef6ae1e7cda1a89b835d6f05bc6bdb72b141db38` | 32754 HTTP 200 |
| HTTPS GET `…/index.html` | `3f4b61913528622ecb87ca57ef6ae1e7cda1a89b835d6f05bc6bdb72b141db38` | 32754 |
| Esperado (`design.md` 32754 bytes) | `3f4b61913528622ecb87ca57ef6ae1e7cda1a89b835d6f05bc6bdb72b141db38` | 32754 |

`cmp` disco vs `/tmp/917-B-https.html`: **IDENTICAL**. HTTP 200 isolado **não** é o gate.

## 2. Detector Impeccable

- Alvo: `frontend/public/prototypes/card-917-historico-completo-analise/index.html`
- Comando: `node .agents/skills/impeccable/scripts/detect.mjs --json` → `[]`, exit 0.
- **0 findings determinísticos.** Nada por classificar → sem bloqueio deste item.

## 3. Tokens + clone / fidelidade (superfície existing)

- `design.md` linhas próprias: `UI impact: affected` · `live_route: /combo/results` · `surface: existing`. **Não** é rota de catálogo emprestada (`/favorites`, `/combo/select`, `/combo/discovery`).
- Catálogo `scripts/process-fsm/route-landmarks.yaml` `/combo/results`: `selectors: [".combo-page"]`, `texts: ["Lista de operações", "Análise da estratégia"]`.
- Proto no browser: `.combo-page`=1; texto «Lista de operações»; `aria-label="Análise da estratégia"`; «Voltar aos favoritos»; chips BTC/USDT · 1D · Long / compra; Menos / Mais / Resetar; chip «180 velas»; «Roda do mouse: zoom» (chrome vivo de `StrategyChartSurface`).
- 6 pares `COPIED:start` / `COPIED:end` (shell AppNav, chrome `/combo/results`, regras, toolbar do gráfico, lista, disclaimer). Delta observável: chip `Lista 73 · Setas 146 (entrada+saída) · 1:1` + série SVG com setas da lista completa (fora dos blocos COPIED do chrome).
- Toggle Antes/Depois: **ausente**. Botões «Antes»/«Depois» = 0. Comentário do HTML («NÃO é painel ANTES/DEPOIS») não é painel.
- Monitor ao vivo / cards de posição: **ausentes** (fora do card).

## 4. Browser real — matriz (desktop 1440×900 e mobile 390×844)

Console error = 0; warning = 0; pageerror = 0; responses ≥400 = 0. Overflow documento `scrollWidth==clientWidth` (1440 e 390). Gate bruto: `.impeccable/critique/917-B-gate.json`.

Fluxo em ambos os viewports: estado padrão → Menos até a série toda → Resetar → arrastar o palco para trás (180 velas, viewport ~2021).

| # | Assert | Desktop | Mobile |
|---|---|---|---|
| 1 | Digest disco == HTTPS (não basta HTTP 200) | PASS | PASS |
| 2 | Landmark `.combo-page` + «Lista de operações» + `aria-label="Análise da estratégia"` | PASS | PASS |
| 3 | Resumo Operações = 73 = linhas fechadas únicas da lista | PASS | PASS (73 cards) |
| 4 | `data-marker-count=146` · `data-list-count=73` · chip 1:1 visível | PASS | PASS |
| 5 | Padrão: «180 velas», `viewport-from=2026-01-05`, seta `2017-10-05` ausente, `2026-07-10` presente, 12 marcadores visíveis (6 Compra + 6 Venda) | PASS | PASS |
| 6 | Não abre em fit-all: 180 ≠ 2367 velas no primeiro viewport | PASS | PASS |
| 7 | Menos até série: «2367 velas», `viewport-from=2017-08-17`, 73 Compra + 73 Venda, `data-time="2017-10-05"`=1, `data-marker-count` continua 146, rótulos 0 | PASS | PASS |
| 8 | Resetar: «180 velas», 2017 oculta de novo, `data-marker-count` ainda 146 | PASS | PASS |
| 9 | Arrastar com 180 velas revela recorte anterior a 05/01/26 (viewport `2021-09-30`, série ainda 146) | PASS | PASS |
| 10 | Zero botões Antes/Depois; zero chrome de Monitor ao vivo | PASS | PASS |
| 11 | a11y básica: `lang=pt-BR`, botões zoom `min-height` ≥44, `aria-label` Menos/Mais/Resetar, `aria-live` no chip de velas, palco `tabindex=0` | PASS | PASS |
| 12 | 0 console de impacto / 0 pageerror / 0 ≥400 / `sw==cw` | PASS | PASS |

Pixels desktop padrão: recorte 2026-01 → 2026-09; poucas setas com rótulo Compra/Venda (viewport ≤260). Zoom-out: eixo 2017-08 → 2026-09; triângulos densos sem rótulo; chip 1:1 intacto. Resetar devolve o recorte recente sem dropar a série. Pan: 2021-09 → 2022-06 ainda com setas da lista.

Pixels mobile: toolbar Menos/Mais/Resetar usáveis; chip 1:1 full-width; gráfico 240px; lista em cards 73. Zoom-out mostra o histórico 2017→2026; Resetar volta a 180 velas.

Rota viva **não usada** como prova (login wall). Browser correu só no proto.

## 5. Aceite #917 observável no proto

1. Cada operação da lista tem entrada+saída no gráfico quando a série está aberta (73+73=146). PASS.
2. Sem seta órfã: 146 marcadores = 73 trades × 2. PASS.
3. BTC 1d com ops < 05/01/26: Menos revela `2017-10-05`; arrastar revela 2021. PASS.
4. Outro ativo/timeframe: proto demonstra só BTC/USDT 1d — **P3 Apply** (contrato escrito; mock único). Não é P0: o 1:1 não está amarrado a um recorte de Monitor neste HTML.
5. Resetar não apaga a série (`data-marker-count` 146 nos três estados). PASS.
6. Operações do resumo = 73 linhas fechadas. PASS.

Fora do card (não-findings): Monitor ao vivo ausente; layout da página não redesenhado (shell + resumo + regras + gráfico + lista); Excel extra não inventado (botão clone da tabela viva); sem fit-all no open.

## 6. Findings (toda finding classificada)

### P0 — nenhum

Tokens parseáveis e `live_route` é `/combo/results`. Landmarks 3/3 no proto. Digest servido == local. Clone+delta (não ANTES/DEPOIS). 1:1 lista↔setas observável; zoom inicial 180; histórico antigo na série; Resetar preserva marcadores. Fidelidade do delta do card ok → não BLOCKED.

### P1 — nenhum

Aceite visível nos dois viewports. Detector `[]`. Botões de zoom com alvo ≥44px e rótulo acessível. Sem overflow horizontal. Densidade (rótulo some com 2367 velas; triângulos ficam) cumpre o contrato.

### P3 — aceites (Apply / clone chrome; não reabrir como P0/P1)

- **P3-1 SVG do proto vs canvas lightweight-charts.** Já aceite no `design.md`. Apply não pinta este SVG.
- **P3-2 Nomes internos `buildTradeMarkers` / `signal_history` e MAE/MFE da tabela (`—`).** Já aceite no `design.md`.
- **P3-3 Mock só BTC/USDT 1d.** Critério 4 do issue (qualquer ativo/timeframe) é do Apply na página viva; o proto escolhe o cenário grelhado (73 ops / 146 setas).
- **P3-4 `.chart-stage` 240px no ≤1023px** vs `min-h-[360px]` vivo. Palco continua usável; não é redesenho do layout da análise.
- **P3-5 Texto Menos/Mais/Resetar visível no 390** (vivo usa `hidden sm:inline`, só ícone). Proto mais explícito; a11y ok.
- **P3-6 Chip 1:1 full-width no mobile** (`width:100%`). Delta deste card, legível.
- **P3-7 Velas mock saltam sáb/dom; zoom ancora `toIdx` no fim da série.** Detalhe do SVG; Apply usa a superfície viva.
- **P3-8 Chrome inerte:** hamburger / Recolher / nav `href=#`; «Voltar» é âncora (vivo é `button`); «Roda do mouse: zoom» no touch (já no chrome vivo).

Observações (não-findings): thead desktop vs cards mobile é o recorte do clone; overlay `detect.js` não injectado — evidência = CLI + Playwright no proto servido.

## 7. Veredito

**PASS** — zero P0/P1 abertos; detector `[]` classificado; digest idêntico; clone `/combo/results` + delta só das setas completas; aceite #917 observável (1:1, 180 no open, Menos/arrastar revelam pré-05/01/26, Resetar não apaga); `/login` não usado como prova da rota; matriz desktop+mobile. HTTP 200 sozinho não sustentaria este veredito.

Disposition: crítico não pede rework. P3 aceites no Apply.

## 8. Referências

- Proto URL: https://dev.criptofarol.com.br/prototypes/card-917-historico-completo-analise/
- Digest: `3f4b61913528622ecb87ca57ef6ae1e7cda1a89b835d6f05bc6bdb72b141db38`
- Snapshot: `.impeccable/critique/917-card-917-historico-completo-analise-B.md`
- Gate bruto: `.impeccable/critique/917-B-gate.json`
- PNGs: `917-B-desktop-chart-{default,zoomout,reset,pan}.png`, `917-B-desktop-viewport-{default,zoomout,reset}.png`, `917-B-mobile-chart-{default,zoomout,reset,pan}.png`, `917-B-mobile-viewport-{default,zoomout,reset}.png`, full-page `917-B-{desktop-1440x900,mobile-390x844}-{default,zoomout,reset,pan}.png`
