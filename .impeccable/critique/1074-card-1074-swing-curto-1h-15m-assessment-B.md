# Assessment B (detector + browser real) — card 1074 · change card-1074-swing-curto-1h-15m

> Assessor B isolado, mesmo modelo, sem transcript de A nem do pai. Sem nested-spawn.
> Nada movido (Status, branch, worktree); escrita só neste ficheiro, PNGs `1074-B-*`, JSON/py de gate e detect.
> Tokens parseáveis do `design.md` (rubrica D4, não reabrir parser): `UI impact: affected` · `live_route: /combo/discovery` · `surface: existing`.

```
Assessment B 1074
digest_match: yes (disco == HTTP local == browser; HTTPS DEV ainda não serve este proto)
detector: 0 findings
P0: nenhum
P1: nenhum
P3: Promover recortado no desktop; chip GO outline vazio no mobile; chips de template wrap; copy proto «sem campo para alterar»; rascunho Acompanhar 4h+1d; chrome #0d7990ca / #PF-492; 7 de 8 mock
verdict: PASS
```

- UTC: 2026-10-02T02:27:01Z
- Tuple (read-only): `q=Design` · `bound_card=1074` · `q_git=card-1074-swing-curto-1h-15m` (GraphQL pontual `repository.issue(number:1074).projectItems` em `oalansilva/crypto` → Status `Design`; project 1 / `oalansilva`; item `PVTI_lAHOAAHtBM4BV8b2zg9-yeA`). Sem `process_event`. Sem `gh project item-list`. Sem `gh issue view`. Título REST: «Swing curto 4h/1h: testar 4 estratégias rápidas com filtro do 1D (BTC/ETH)» — o pacote segue o body (filtro 1D **não entra**); a tela não o mostra.
- Protótipo: `frontend/public/prototypes/card-1074-swing-curto-1h-15m/index.html`
- Servido DEV: https://dev.criptofarol.com.br/prototypes/card-1074-swing-curto-1h-15m/ → HTTP **404** título `Protótipo não encontrado` (source DEV / worktrees publicados ainda sem este `index.html`). **Registado.** Evidência do browser = HTTP local do disco, não `file://`.
- HTTP local: `http://127.0.0.1:18741/prototypes/card-1074-swing-curto-1h-15m/` (cwd `frontend/public`).
- Digest esperado (`design.md`): `10523181ee5398e5a67f767b74fe954f7a1f1841e27cd60fb2fe036f6410c1c9` · 53208 bytes
- Rota viva: https://dev.criptofarol.com.br/combo/discovery — **sem sessão**; Chromium aterrissou em `/login` (`Bem-vindo de volta` / campo senha). `/login` **não** é a rota; **não** autoriza PASS de clone. Clone avaliado pelo proto local + landmarks do catálogo.
- Browser: Playwright Python + Chromium (`/usr/bin/chromium-browser`) headless, `color_scheme=dark`. Viewports **1440×900** e **390×844**. Cursor IDE browser MCP: `browser_tabs` vazio / `browser_navigate` «No browser tab available» — fallback Playwright, não `file://`.
- Detector: `node .agents/skills/impeccable/scripts/detect.mjs --json` no HTML versionado → `[]`. Overlay `detect.js` não injectado (scan estático cobre o HTML).
- Gate: `.impeccable/critique/1074-B-gate.py` · `.impeccable/critique/1074-B-gate.json`

## 1. Digest servido == local

| Ponta | sha256 | bytes | HTTP |
|---|---|---|---|
| Disco `index.html` | `10523181ee5398e5a67f767b74fe954f7a1f1841e27cd60fb2fe036f6410c1c9` | 53208 | — |
| HTTP local GET `…/index.html` | `10523181ee5398e5a67f767b74fe954f7a1f1841e27cd60fb2fe036f6410c1c9` | 53208 | 200 IDENTICAL |
| Browser (Playwright carregou o HTTP local) | o mesmo documento | 53208 | 200 |
| `design.md` / esperado | `10523181ee5398e5a67f767b74fe954f7a1f1841e27cd60fb2fe036f6410c1c9` | 53208 | — |
| HTTPS GET `/prototypes/card-1074-swing-curto-1h-15m/` | *não é o proto* | 608 | **404** «Protótipo não encontrado» |
| HTTPS GET `…/index.html` | *não é o proto* | 618 | **404** |

`cmp` disco vs HTTP local: **IDENTICAL**. Disco vs HTTPS: **DIFFER** (DEV ainda não publica este worktree). HTTP 200 isolado **não** é o gate. Digest que o browser viu **bate com o disco**.

## 2. Detector Impeccable

- Alvo: `frontend/public/prototypes/card-1074-swing-curto-1h-15m/index.html`
- Comando: `node .agents/skills/impeccable/scripts/detect.mjs --json` → `[]`, exit 0.
- **0 findings determinísticos.** Nada crítico → sem P0 deste item.
- Overlay live-server / `detect.js` não injectado.

## 3. Clone / fidelidade (superfície existing)

- Catálogo `scripts/process-fsm/route-landmarks.yaml` `/combo/discovery`: `Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`.
- Proto: **14/14** pares `COPIED:start` / `COPIED:end`; soma UTF-8 dos intervalos = **26304** (> 0). Bate com `design.md` (26304 copied + 26904 generated). Shell AppNav, heading, modos, rascunho, Preflight, chrome Acompanhar, cascas das grelhas, nota educacional.
- Toggle Antes/Depois: **ausente**. Botões «Antes»/«Depois» = **0** nos dois viewports. Index = clone+delta, default `data-state="montar"`. Não é painel de 6 estados nem ANTES/DEPOIS.
- Tokens D4 em linhas próprias no `design.md` (após Context): `UI impact: affected` / `live_route: /combo/discovery` / `surface: existing`. Regiões clonadas marcadas. **PASS** deste item da rubrica — não reabrir parser.

## 4. Browser real — matriz (desktop 1440×900 e mobile 390×844, colorScheme dark)

Console error = 0; pageerror = 0; responses ≥400 no proto local = 0. `color-scheme` meta = `dark`.

| # | Assert | Desktop | Mobile |
|---|---|---|---|
| 1 | Digest disco == HTTP local (não basta HTTP 200) | PASS | PASS |
| 2 | Landmark h1 `Descoberta de estratégias swing` | PASS | PASS |
| 3 | Landmark `Preflight` visível no Montar | PASS | PASS (scroll) |
| 4 | Landmark `Rascunho de varredura` visível no Montar | PASS | PASS |
| 5 | Heading `4h, 1h, 15m e 1d`; sem filtro de tendência 1D | PASS | PASS |
| 6 | TFs visíveis exactamente 15m / 1h / 4h / 1d; default 1d; sem 1m/5m/30m | PASS | PASS |
| 7 | 3 templates novos visíveis, sem `lab_` | PASS | PASS |
| 8 | Rótulo só leitura `taxa 0,075%` + slippage do TF; 0 inputs | PASS | PASS |
| 9 | Linha 1h `slippage 0,03%`; linha 15m `slippage 0,05%` | PASS | PASS (scroll) |
| 10 | Promover à mão enabled (não automático; Baixa amostra disabled) | PASS | PASS |
| 11 | 0 botões Antes/Depois; 3 modos, não grelha ANTES/DEPOIS | PASS | PASS |
| 12 | 0 console error / 0 pageerror / proto local sem ≥400 | PASS | PASS |
| 13 | COPIED pares UTF-8 > 0 | PASS (26304) | PASS |

Rota viva sem sessão: `final_url=https://dev.criptofarol.com.br/login`, h1 `Bem-vindo de volta`. **Não usada como evidência de clone.**

HTTPS DEV do proto: título `Protótipo não encontrado`. **Não** é evidência do HTML deste card.

Pixels desktop Montar: 4 chips (Cruzamento + Donchian + Squeeze + Pullback); grelha 2×2 de TF com **1 dia** premido; Preflight `taxa 0,075% · slippage do timeframe (0,02% em 4h e 1d · 0,03% em 1h · 0,05% em 15m)`.

Pixels desktop Decidir: Donchian `BTC/USDT · 1h` + `taxa 0,075% · slippage 0,03%`; Squeeze `BTC/USDT · 15m` + `slippage 0,05%`; GO/NO-GO; Promover fill amarelo recortado à direita (clone chrome).

Pixels mobile: mesmos TFs e custo após scroll; cards 1h/15m com Promover à mão; chip GO com outline largo (clone incumbente).

## 5. Findings (toda finding classificada)

### P0 — nenhum

Landmarks 3/3 no proto; digest disco == HTTP local == browser; HTTPS 404 registado e **não** usado como prova; sem painel ANTES/DEPOIS; 14 pares COPIED com bytes > 0; TFs 4h/1h/15m/1d sem 1m/5m/30m; sem filtro 1D no heading; 3 templates sem `lab_`; custo só leitura; Promover à mão; detector `[]`. `/login` não conta como clone.

### P1 — nenhum

Delta observável nos dois viewports (TF/Preflight/linhas 1h·15m abaixo da dobra no 390, visíveis após scroll). Selo tem texto `GO`/`NO-GO` (não só cor). Slippage não é campo.

### P3 — aceites (Apply / clone chrome; não reabrir como P0/P1)

- **P3-1 Coluna Ação recortada no desktop 1440.** `Promover`/`Excluir` cortados; `table.lb` `min-width:1240px` + scrollbar. Nit do clone incumbente da grelha; CTA existe e o gate de enabled passou no DOM.
- **P3-2 Chip GO/NO-GO com outline vazio no mobile.** Célula `display:flex; justify-content:space-between` estica o selo. Texto legível; mesmo nit do incumbente #969.
- **P3-3 Chips de template no Montar.** `axis-chips` `overflow:hidden` + `max-width:160px`; Pullback parte em duas linhas (`longa + RSI` / `+ ADX`). Os 3 nomes estão visíveis.
- **P3-4 Copy proto no Preflight** «sem campo para alterar» — meta do mock; Apply usa o rótulo operacional (`taxa 0,075%` + slip do TF) sem essa frase.
- **P3-5 Rascunho congelado do Acompanhar** ainda diz `4h + 1d` (chrome copiado). Delta deste card está no Montar/Decidir.
- **P3-6 Chrome copiado** `#0d7990ca` / snapshot 492 / `#PF-492`; leaderboard `7 de 8 candidatos` mock.
- **P3-7 Montar condensado** vs `DiscoveryPage.tsx` viva (eixos em chips, não o picker completo). Landmarks presentes; sem furo do contrato deste card.
- **P3-8 Sticky Promover do card anterior no chrome mobile** ao scroll da grelha Decidir. Nit de clone; cada linha tem o próprio Promover.

Observações (não-findings): `/login` não conta como clone. HTTPS 404 não invalida o proto do disco. Overlay Impeccable no browser não injectado (scan estático limpo). Cursor IDE browser MCP indisponível nesta sessão. Pullback aparece nos chips do Montar (contrato «3 templates visíveis»); não precisa de linha própria no Decidir.

## 6. Veredito

**PASS** — zero P0/P1 abertos; detector `[]`; digest disco == HTTP local == o que o browser carregou; clone+delta (não ANTES/DEPOIS); `/login` não usado como prova da rota; matriz visível nos dois viewports; HTTPS DEV ainda sem este proto (registado). HTTP 200 sozinho não sustentaria este veredito.

Disposition: crítico não pede rework. P3 aceites no Apply.

## 7. Referências

- Proto disco: `frontend/public/prototypes/card-1074-swing-curto-1h-15m/index.html`
- HTTP local (evidência): `http://127.0.0.1:18741/prototypes/card-1074-swing-curto-1h-15m/`
- HTTPS DEV: 404 `Protótipo não encontrado`
- Digest: `10523181ee5398e5a67f767b74fe954f7a1f1841e27cd60fb2fe036f6410c1c9`
- Snapshot: `.impeccable/critique/1074-card-1074-swing-curto-1h-15m-assessment-B.md`
- Gate: `.impeccable/critique/1074-B-gate.json` · `.impeccable/critique/1074-B-gate.py`
- Detector: `.impeccable/critique/1074-B-detect.json`
- PNGs: `1074-B-desktop-1440x900-montar.png`, `1074-B-desktop-1440x900-acompanhar.png`, `1074-B-desktop-1440x900-decidir.png`, `1074-B-desktop-1440x900-decidir-15m.png`, `1074-B-mobile-390x844-montar.png`, `1074-B-mobile-390x844-montar-tf.png`, `1074-B-mobile-390x844-montar-preflight.png`, `1074-B-mobile-390x844-acompanhar.png`, `1074-B-mobile-390x844-decidir.png`, `1074-B-mobile-390x844-decidir-1h.png`, `1074-B-mobile-390x844-decidir-15m.png`, `1074-B-live-combo-discovery.png`, `1074-B-https-404.png`
