# Assessment B (detector + browser real) — card 949 · change card-949-favorito-historico-inteiro

> Assessor B isolado, mesmo modelo, sem transcript de A nem do pai. Sem nested-spawn.
> Nada movido (Status, branch, worktree); nenhuma edição fora deste ficheiro, PNGs `949-B-*` e `949-B-gate.json`.
> Tokens parseáveis do `design.md` (rubrica D4): `UI impact: affected` · `live_route: /favorites` · `surface: existing`.

```
Assessment B 949
digest_match: yes
detector: 3 findings (side-tab) classificados P3
P0: nenhum
P1: nenhum
P3: side-tab cards mobile de tier; truncagem Estratégia; mock 71 vs recorte da lista; copy de contraste «não o treino» na análise; Preflight 01 jan 2017 vs testemunho 17/08; leaderboard 309/26; thead clip no 390; alvos 32px
verdict: PASS
```

- UTC: 2026-09-16T01:12Z
- Tuple (read-only): `bound_card=949` · `q_git=card-949-favorito-historico-inteiro`. Sem `process_event`.
- Briefing REST: `gh api repos/oalansilva/crypto/issues/949` → #949 open, *«Ao salvar favorito após 70/30, gravar e mostrar o histórico inteiro»*. Q1/Q2/Q3 no body; testemunho 17/08/2017 → 24/12/2023; 70/30 fica na grelha; sem migrar legado; Combo 2 anos ≠ «todo».
- Protótipo canónico: `frontend/public/prototypes/card-949-favorito-historico-inteiro/index.html`
- Servido: https://dev.criptofarol.com.br/prototypes/card-949-favorito-historico-inteiro/
- Extras: `descoberta.html` · `analise.html` · `combo.html` (mesma pasta/URL). `select.html` HTTP 404.
- Digest index: `0d87ecd5992a5aa343c4d2249209bb8d1d0a3ae4f9f5b487ec925beb369b97e4` · 48155 bytes
- Rota viva `/favorites` **não usada como prova** (não autenticada neste filho). Clone avaliado no proto HTTPS + landmarks do catálogo HEAD.
- Browser: Playwright Python + Chromium 1243 (`chrome-linux-arm64`) sob `xvfb-run -a`, `--no-sandbox`. Viewports 1440×900 e 390×844. `colorScheme: dark`. URL canónica do proto (não `file://`, não `/login`).
- Detector: `node .agents/skills/impeccable/scripts/detect.mjs --json` no HTML versionado (cwd worktree).

## 1. Digest servido == local

| Ponta | sha256 | bytes |
|---|---|---|
| Disco `index.html` | `0d87ecd5992a5aa343c4d2249209bb8d1d0a3ae4f9f5b487ec925beb369b97e4` | 48155 |
| HTTPS GET `/prototypes/card-949-favorito-historico-inteiro/` | idem | 48155 HTTP 200 |
| HTTPS GET `…/index.html` | idem | 48155 |
| Disco `descoberta.html` | `03f0980e04646c001bdf25d31bc3408e1e14d39e8604ced05051877f644d08c8` | 67906 · cmp HTTPS **IDENTICAL** |
| Disco `analise.html` | `2bc183850e855a183a166023488483f578a262ef58ec00a3bf335af5572e67ce` | 27023 · cmp HTTPS **IDENTICAL** |
| Disco `combo.html` | `e4f16156b55a4a98083125e6fe718bfc778807bb2211d59d058e4cff5f4fb1ff` | 23263 · cmp HTTPS **IDENTICAL** |
| HTTPS GET `…/select.html` | 404 (626 B) | sem extra `/combo/select` |

`cmp` disco vs HTTPS nas quatro pontas canónicas: **IDENTICAL**. HTTP 200 isolado **não** é o gate.

## 2. Detector Impeccable

- Alvos: os quatro HTML do proto + scan da pasta.
- `index.html` exit 2 → 3 findings `side-tab` (L149–151: `.fav-up` / `.turquoise` / `.fav-primary-active` `border-left:3px`). `descoberta.html` / `analise.html` / `combo.html` → `[]`, exit 0.
- **Classificação:** P3 incumbente do clone `/favorites` (já aceite no `design.md`: «Detector `side-tab` nos cards mobile de tier»). Slop de CSS de tier, não contrato de período. **Não** reabre como P0/P1.

## 3. Tokens + clone / fidelidade (superfície existing)

- `design.md` linhas próprias: `UI impact: affected` · `live_route: /favorites` · `surface: existing`. **Não** é rota de catálogo emprestada (`/combo/discovery`, `/combo/results`, `/combo/select`).
- Catálogo `scripts/process-fsm/route-landmarks.yaml` `/favorites`: `selectors: ["table.fav-strategies"]`, `texts: ["Estratégias favoritas", "Symbol", "Estratégia", "Ações"]`.
- Index no browser: `table.fav-strategies`=1; h1 «Estratégias favoritas»; thead `textContent` **Symbol** / **Estratégia** / **Ações** (innerText vira SYMBOL/AÇÕES por `text-transform:uppercase` — landmark presente, não em falta). Filtro visível `Symbol`. `copied_utf8_sum`=7718 > 0 (total 48155).
- 4 pares `COPIED:start`/`COPIED:end` no index (shell AppNav, heading, thead `table.fav-strategies`, footer). Delta de período/números nas células (generated); `DELTA:start`=0 no index — não é painel das N.
- Toggle Antes/Depois: **ausente**. Botões «Antes»/«Depois» = 0. Comentário HTML «No ANTES/DEPOIS» não é painel. URL canónica = `index.html`.
- Extra Descoberta: 11 COPIED + 5 DELTA. Landmarks «Descoberta de estratégias swing» + «Preflight» visíveis no Decidir; «Rascunho de varredura» + Preflight visíveis no tab **Montar** (`aria-selected=true`, h2 visível). Grelha Decidir 70/30.
- Extra análise / Combo: 5 COPIED cada; `.combo-page` + «Lista de operações» + «Análise da estratégia». Sem «Available Templates». Sem chrome de Monitor ao vivo. Nav «Monitor» no shell = clone `/favorites`, não extra `/monitor`.
- `/combo/select`: sem ficheiro no proto; GET 404; zero copy deste card.

## 4. Browser real — matriz (desktop 1440×900 e mobile 390×844)

Console error = 0; warning = 0; pageerror = 0; responses ≥400 no proto = 0. Overflow documento `scrollWidth==clientWidth` (1440 e 390). `desktop_eq_mobile_index_dates: true`. Gate bruto: `.impeccable/critique/949-B-gate.json`.

Falsos FAIL do script inicial (`lm_symbol`, `lm_acoes`, `desc_lm_rascunho`): innerText uppercase no thead; Rascunho vive no tab Montar (`display:none` no Decidir). Reprobe: thead `textContent` Symbol/Ações; Montar mostra Rascunho + Preflight. **Não** são P0/P1.

| # | Assert | Desktop | Mobile |
|---|---|---|---|
| 1 | Digest disco == HTTPS (não basta HTTP 200) | PASS | PASS |
| 2 | Tokens `UI impact: affected` / `live_route: /favorites` / `surface: existing` | PASS | — |
| 3 | Landmarks `/favorites`: `table.fav-strategies` + «Estratégias favoritas» + Symbol + Estratégia + Ações | PASS (thead + filtro) | PASS (filtro Symbol; cards; thead clip incumbente) |
| 4 | COPIED > 0; 4 pares; zero botões Antes/Depois; sem painel das N | PASS | PASS |
| 5 | BTC novo **17/08/2017 → 15/09/2026** (não 24/12/2023); 71 · 54,9% · +210,40% · Sharpe 0,38 | PASS | PASS |
| 6 | Legado SOL **17/08/2017 → 24/12/2023** «Já na lista · não migrado»; 48 · +120% | PASS | PASS |
| 7 | Combo ETH **15/09/2024 → 15/09/2026**; 22 · +35,00%; não 2017; não «todo» | PASS | PASS |
| 8 | Desktop = mobile nas três janelas do index | PASS | PASS |
| 9 | Sem mistura 43 / Win 58,14% / 68 sob rótulo 2023 (proto usa 48 treino vs 71 completo; 68 ausente) | PASS | PASS |
| 10 | Descoberta Decidir: retrato 70/30 · 17/08/2017 → 24/12/2023; Calmar/GO-NO-GO; BTC grelha 48 · +120% · 8,1% CAGR ≠ lista 71 · +210,40% | PASS | PASS |
| 11 | Modal Promover: janela 17/08/2017 → 24/12/2023 · 48 trades · 8,1%; **sem** 15/09/2026 / 71 / preview | PASS | PASS |
| 12 | Montar: «Rascunho de varredura» + «Preflight» visíveis | PASS | PASS (screenshot extra) |
| 13 | Análise: «Resumo · histórico inteiro · 17/08/2017 → 15/09/2026»; 71; **não** «Resumo · janela de treino da Descoberta · …2023» | PASS | PASS |
| 14 | Combo: 2 anos completos 15/09/2024 → 15/09/2026; chip 70/30; «Salvar nos Favoritos»; lista arranca 15/09/2024 | PASS | PASS |
| 15 | Sem `/monitor` extra; sem `/combo/select`; 0 console / 0 pageerror / `sw==cw` | PASS | PASS |
| 16 | a11y: `lang=pt-BR`; dialog `role=dialog` `aria-modal` `aria-labelledby`; Fechar `aria-label`; Voltar | PASS | PASS |

Pixels index desktop: Período BTC `17/08/2017 → 15/09/2026` · 71 · 54,9% · +210,40%; SOL `17/08/2017 → 24/12/2023` · 48 · +120,00%; ETH `15/09/2024 → 15/09/2026` · 22 · +35,00% · stop 8,50%. AÇÕES visível. Nome da estratégia truncado (P3 aceite).

Pixels index mobile: mesmos três períodos e métricas nos cards; 71 / 48 / 22.

Pixels Descoberta: nota «Retrato 70/30 · treino 17/08/2017 → 24/12/2023»; linha BTC «Grelha no treino 70/30 — não no histórico inteiro»; GO. Modal vivo sem preview do completo. Montar: Rascunho + Preflight.

Pixels análise: h1 período completo 2017→2026; Return +210,40% / 54,9% / 71; gráfico e lista no mesmo recorte (1.ª operação 17/08/2017). Subtítulo proto «não o treino 17/08/2017 → 24/12/2023» (contraste, não ensino do treino como desempenho).

Pixels Combo: «Período 2 anos completos · 15/09/2024 → 15/09/2026»; 70/30 na busca; Salvar; 22 negócios; copy «não o treino (~até 02/2026) e não o histórico inteiro desde 2017».

Rota viva **não usada**. Browser correu só no proto.

## 5. Findings (toda finding classificada)

### P0 — nenhum

Clone `/favorites` com landmarks do catálogo; copied 7718 > 0; sem painel ANTES/DEPOIS / das N; BTC novo não herda 24/12/2023; legado não migrado; Combo 2 anos não vira «todo»; grelha continua 70/30; modal sem preview; análise não rotula treino como resumo; digest HTTPS == disco; detector classificado. Fidelidade + contrato visível ok → não BLOCKED.

### P1 — nenhum

Delta observável nos dois viewports. Números do treino (grelha 48 / +120% / Win 55,0% / CAGR 8,1%) **não** ocupam a linha nova «todo» (71 / +210,40% / 54,9%). 43 / 58,14% / 68 **ausentes** no proto — a regressão «lista até hoje sob o rótulo 2023» não se materializa (legado leva 48, não 68). Copy da grelha e da análise **nega** o treino como desempenho completo.

### P3 — aceites (Apply / clone chrome; não reabrir como P0/P1)

- **P3-1 `side-tab` nos cards mobile de tier** (detector L149–151). Incumbente; já no `design.md`.
- **P3-2 Truncagem do nome na coluna Estratégia** (`table-layout` fixed vivo). Já no Apply contract.
- **P3-3 Mock da lista de análise:** cabeçalho 71 negócios, recorte visível ~33 linhas. Vizinho do P3 «32 vs 33 negócios» / #917 setas.
- **P3-4 Copy de contraste na análise** («não o treino 17/08/2017 → 24/12/2023») e no Combo. Pedagógica do proto; Apply pode omitir se os números já forem do período certo.
- **P3-5 Preflight Montar** «todo o histórico [01 jan 2017, 12 set 2026]» ≠ testemunho BTC 17/08/2017 → 15/09/2026. Chrome da busca, não a linha de Favoritos.
- **P3-6 Leaderboard `309 de 309 · página 1 de 26` com poucas `<tr>`.** Mock da Descoberta viva.
- **P3-7 Thead clip / card-stack no 390.** Landmarks via filtro + `data-label`/cards; clone vivo.
- **P3-8 Alvos 32px nos ícones da linha; modal «Retorno (CAGR)» 8,1%** (diálogo reutilizado do Decidir vivo). Fora do delta deste card.
- **P3-9 Nomes internos / segundo backtest vs datas abertas.** Já P3 de Apply.

Observações (não-findings): `DELTA:start`=0 no index porque o delta é célula/período, não região nova. Overlay `detect.js` não injectado — evidência = CLI + Playwright no proto servido. GET `/favorites` não usado. Nav Monitor no shell = clone, não extra `/monitor`.

## 6. Veredito

**PASS** — zero P0/P1 abertos; detector `side-tab` classificado P3; digest idêntico nas 4 pontas; clone+delta (não ANTES/DEPOIS); `/login` não usado; matriz visível desktop+mobile no index e extras. HTTP 200 sozinho não sustentaria este veredito.

Disposition: crítico não pede rework. P3 aceites no Apply.

## 7. Referências

- Proto URL: https://dev.criptofarol.com.br/prototypes/card-949-favorito-historico-inteiro/
- Digest index: `0d87ecd5992a5aa343c4d2249209bb8d1d0a3ae4f9f5b487ec925beb369b97e4`
- Snapshot: `.impeccable/critique/949-card-949-favorito-historico-inteiro-assessment-B.md`
- Gate bruto: `.impeccable/critique/949-B-gate.json`
- PNGs: `949-B-desktop-1440x900-index.png`, `949-B-desktop-1440x900-descoberta.png`, `949-B-desktop-1440x900-descoberta-promover.png`, `949-B-desktop-1440x900-descoberta-montar.png`, `949-B-desktop-1440x900-analise.png`, `949-B-desktop-1440x900-combo.png`, `949-B-mobile-390x844-index.png`, `949-B-mobile-390x844-descoberta.png`, `949-B-mobile-390x844-descoberta-promover.png`, `949-B-mobile-390x844-descoberta-montar.png`, `949-B-mobile-390x844-analise.png`, `949-B-mobile-390x844-combo.png`

proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)
