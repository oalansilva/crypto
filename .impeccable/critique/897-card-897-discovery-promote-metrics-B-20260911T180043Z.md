# Assessment B (detector + browser real) — card 897 · change card-897-discovery-promote-metrics

> Assessor B isolado, mesmo modelo, sem transcript de A nem do pai.
> Nada movido (Status, branch, worktree); edições só nesta pasta `.impeccable/critique/`.
> Tokens parseáveis do `design.md`: `UI impact: affected` · `live_route: /favorites` · `surface: existing`.

- UTC: 2026-09-11T180043Z
- Binding dado: Status=Design, change `card-897-discovery-promote-metrics`
- `scripts/process-fsm/resolve.py`: `{q: None, bound_card: 897, q_git: card-897-discovery-promote-metrics}` (Moore page `.grok/rules/process-fsm-page.md` ausente; `q` não veio do board — não chamei `process_event`)
- Protótipo canónico: `frontend/public/prototypes/card-897-discovery-promote-metrics/index.html`
- Servido: https://dev.criptofarol.com.br/prototypes/card-897-discovery-promote-metrics/
- Extra: https://dev.criptofarol.com.br/prototypes/card-897-discovery-promote-metrics/analise.html
- Digest esperado (prompt / design.md):
  - index `f35495bc6d0d24b3ae78a258accc17257dd6126b4a4325c01070c11bac8309bc`
  - analise `5ea6e082ddeae17d8d5c6d6b89deefe78d167a7e62772157f492fd5d93ccb7b7`
- Rota viva: https://dev.criptofarol.com.br/favorites — **sem sessão**; Playwright aterrissou em `/login` (`Bem-vindo de volta` / EMAIL / SENHA / Entrar). `/login` **não** conta como a rota; clone avaliado pelo proto + landmarks do catálogo.
- Browser: `playwright-cli-headed` / `/usr/local/bin/playwright-cli-headed` **ausentes**. Equivalente: `xvfb-run -a` + `/tmp/pwcli/node_modules/.bin/playwright-cli --headed` + Chromium 1243 (`chrome-linux-arm64`), `PLAYWRIGHT_MCP_SANDBOX=false`, config `897-B-playwright.config.json` (executablePath bundled). Um `run-code --filename` por URL (index, analise, live).
- Detector: `node .agents/skills/impeccable/scripts/detect.mjs --json` nos HTML versionados. (`detector/cli/main.mjs` sem `detectCli()` no entrypoint; `detect.mjs` é o invocador.)

## 1. Digest servido == local

| Ponta | sha256 | bytes |
|---|---|---|
| Disco index | `f35495bc6d0d24b3ae78a258accc17257dd6126b4a4325c01070c11bac8309bc` | 42058 |
| HTTPS GET proto index | `f35495bc6d0d24b3ae78a258accc17257dd6126b4a4325c01070c11bac8309bc` | 42058 HTTP 200 |
| Disco analise | `5ea6e082ddeae17d8d5c6d6b89deefe78d167a7e62772157f492fd5d93ccb7b7` | 21405 |
| HTTPS GET proto analise | `5ea6e082ddeae17d8d5c6d6b89deefe78d167a7e62772157f492fd5d93ccb7b7` | 21405 HTTP 200 |
| Esperado (prompt / design.md) | idênticos | — |

HTTP 200 isolado **não** é o gate; o gate é a matriz abaixo.

## 2. Detector Impeccable

Alvos: HTML versionado (bytes = servido).

### index.html — 2 findings determinísticos (warning)

| # | antipattern | severity | line | snippet | classificação |
|---|---|---|---|---|---|
| 1 | `side-tab` | warning | 143 | `border-left:3px solid var(--fav-up)` | P3 — clone chrome mobile `.fav-mobile-card.tier-top` (acento de tier da grade viva); não é painel/galeria |
| 2 | `side-tab` | warning | 144 | `border-left:3px solid var(--turquoise)` | P3 — clone chrome mobile `.fav-mobile-card.tier-watch` (linha #193); desktop usa `box-shadow: inset 3px 0` (não flagged) |

Exit 2 (warnings contam como primary). Advisory: 0. Error: 0.

### analise.html — 0 findings

`[]`, exit 0.

**Nada determinístico ficou sem classificação.**

Cópias: `.impeccable/critique/897-B-detect-index.json`, `897-B-detect-analise.json`.

## 3. Clone / fidelidade (superfície existing)

- Catálogo `scripts/process-fsm/route-landmarks.yaml` `/favorites`: selector `table.fav-strategies`; texts `Estratégias favoritas`, `Symbol`, `Estratégia`, `Ações`.
- URL canónico = `index.html` clone+delta da grade, **não** painel ANTES/DEPOIS. Comentário do HTML: `No ANTES/DEPOIS panel`. Browser: 0 botões «Antes»/«Depois»; innerText sem painel.
- `analise.html` é extra (copy visível de `/combo/results`), não o index.
- Pares `COPIED:start`/`COPIED:end`: 4 no index (shell, heading, thead, footer); 5 no analise (shell, resumo chrome, gráfico, thead da lista, disclaimer).
- Toggle Antes/Depois: ausente. `aria-pressed` só em chips de filtro / estrelas / Telegram (clone da grade), não prova de clone falsa.
- Tokens no `design.md` (linhas próprias): `UI impact: affected` / `live_route: /favorites` / `surface: existing`.

## 4. Browser real — matriz

Chromium headed via xvfb. Viewports 1280×800 e 390×844. Console error = 0; pageerror = 0. Overflow: `scrollWidth == clientWidth` (1265 desktop / 375 mobile — viewport efetivo, sem overflow horizontal).

### index — PASS 53/53

| Assert | Desktop | Mobile |
|---|---|---|
| `table.fav-strategies` presente | PASS | PASS (DOM; tabela escondida ≤1023px) |
| textos Estratégias favoritas / Symbol / Estratégia / Ações | PASS | PASS |
| h1 visível «Estratégias favoritas» | PASS | PASS |
| **não** é painel ANTES/DEPOIS | PASS | PASS |
| #193 Sharpe 0,31 · Trades 30 · Win 46,7% · Return +16.951% · Max DD 16,5% (≠ `-`/vazio/0) | PASS | PASS (card `favorite-193-mobile`) |
| tabela visível + th Symbol/Estratégia/Ações | PASS | n/a (cards) |
| clique gráfico → `analise.html`; voltar não zera #193 | PASS | — |
| 0 console / 0 pageerror | PASS | PASS |

PNGs B: `897-B-index-desktop-1280x800.png`, `897-B-index-mobile-390x844.png`. Conferem com os screenshots do autor.

### analise — PASS 28/28

| Assert | Desktop | Mobile |
|---|---|---|
| label visível `Resumo · janela de treino da Descoberta` (completa · 10/10/2020 → 01/02/2024) | PASS | PASS |
| label visível `Lista de operações · velas atuais` (completa · 12 negócios — não é a janela da Descoberta) | PASS | PASS |
| resumo snapshot +16.951% · 46,7% · 16,5% · 30 | PASS | PASS |
| Max DD ≠ «Indisponível»; página sem «Indisponível» | PASS | PASS |
| 12 negócios; lista inclui −13,92% | PASS | PASS |
| 0 console / 0 pageerror | PASS | PASS |

PNGs B: `897-B-analise-desktop-1280x800.png`, `897-B-analise-mobile-390x844.png`.

### live `/favorites`

`final_url=https://dev.criptofarol.com.br/login`, `table.fav-strategies=0`, snippet `Bem-vindo de volta… EMAIL SENHA Entrar`. **session-unavailable.** Não usado como evidência de clone nem de PASS. PNG: `897-B-live-favorites-1280x800.png` (chrome de login).

JSON bruto: `897-B-index-gate.json`, `897-B-analise-gate.json`, `897-B-live-favorites-gate.json`.

## 5. Findings (toda finding classificada)

### P0 — nenhum

Landmarks 4/4 no index; digest servido == local == esperado; index não é ANTES/DEPOIS; extra analise com etiquetas distintas e Max DD preenchido; `#193` com os cinco números do snapshot; `/login` não usado como prova.

### P1 — nenhum

Delta observável nos dois viewports. HTML bem formado o suficiente para o gate. Detector sem error.

### P3 — aceites (Apply / clone chrome; não reabrir como P0/P1)

- **P3-1 Detector `side-tab` ×2 (warning)** em `.fav-mobile-card.tier-top` / `.tier-watch` (`border-left:3px`). Acento de tier do clone da grade viva (desktop: `box-shadow` inset). Nit de detector / detalhe de Apply se o produto vivo já usa o mesmo acento.
- **P3-2 Truncagem desktop** da meta `Descoberta · RS-B109ED2C80 · #193` para `… · #1…` (`table-layout:fixed` + overflow). Métricas do contrato continuam visíveis; mobile mostra `#193` inteiro. Densidade da tabela clonada.
- **P3-3** Nomes de chaves JSON / flatten GET vs write, testids, escala de Max DD — já listados como P3 no `design.md` Apply contract. Não reabrir.

Observações (não-findings): wrapper `playwright-cli-headed` ausente neste host — gap de tooling, não finding de UI. Combo-saved BTC/USDT (Sharpe 0,50 / 72 / 58,3%) visível e sem origem Descoberta.

## 6. Veredito

**PASS** — zero P0/P1 abertos; 2 findings do detector classificados (P3); browser gate index 53/53 e analise 28/28; digest idêntico; clone+delta (não ANTES/DEPOIS); `/login` não usado como prova.

Disposition: crítico não pede rework. P3 aceites no Apply.

## 7. Referências

- Proto URL: https://dev.criptofarol.com.br/prototypes/card-897-discovery-promote-metrics/
- Extra: https://dev.criptofarol.com.br/prototypes/card-897-discovery-promote-metrics/analise.html
- Digest index: `f35495bc6d0d24b3ae78a258accc17257dd6126b4a4325c01070c11bac8309bc`
- Digest analise: `5ea6e082ddeae17d8d5c6d6b89deefe78d167a7e62772157f492fd5d93ccb7b7`
- Snapshot: `.impeccable/critique/897-card-897-discovery-promote-metrics-B-20260911T180043Z.md`
- Tokens: `UI impact: affected` · `live_route: /favorites` · `surface: existing`
