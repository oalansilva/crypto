# Assessment B (detector + browser real) — card 906 · change card-906-discovery-metrics-grid

> Assessor B isolado, mesmo modelo, sem transcript de A nem do pai. Sem nested-spawn.
> Nada movido (Status, branch, worktree); nenhuma edição fora deste ficheiro, PNGs `906-B-*` e `906-B-gate.json`.
> Tokens parseáveis do `design.md` (rubrica D4): `UI impact: affected` · `live_route: /combo/discovery` · `surface: existing`.

```
Assessment B 906
digest_match: yes
detector: 0 findings
P0: nenhum
P1: nenhum
P3: chrome Acompanhar abaixo da dobra no 390; chip NO-GO full-width; leaderboard 248/248 mock 4 linhas; ids #c906grid/#PF-906-24; min-width 1080 (já aceite); Montar condensado
verdict: PASS
```

- UTC: 2026-09-12T13:27Z
- Tuple (read-only): `bound_card=906` · `q_git=card-906-discovery-metrics-grid`. Sem `process_event`.
- Protótipo: `frontend/public/prototypes/card-906-discovery-metrics-grid/index.html`
- Servido: https://dev.criptofarol.com.br/prototypes/card-906-discovery-metrics-grid/
- Digest esperado: `1e7121225d6cb339e127657c463626dbfed13d751be6bda9d1fcfe84a723c8fc` · 45186 bytes
- Rota viva: https://dev.criptofarol.com.br/combo/discovery — **não navegada**. Sem sessão; `/login` **não** conta como a rota. Clone avaliado só no proto HTTPS + landmarks do catálogo.
- Browser: Playwright Python + Chromium 1243 (`chrome-linux-arm64`) sob `xvfb-run -a`, `--no-sandbox`. Viewports 1440×900 e 390×844. URL canónica do proto (não `file://`, não `/login`).
- Detector: `node .agents/skills/impeccable/scripts/detect.mjs --json` no HTML versionado (cwd worktree).

## 1. Digest servido == local

| Ponta | sha256 | bytes |
|---|---|---|
| Disco | `1e7121225d6cb339e127657c463626dbfed13d751be6bda9d1fcfe84a723c8fc` | 45186 |
| HTTPS GET `/prototypes/card-906-discovery-metrics-grid/` | `1e7121225d6cb339e127657c463626dbfed13d751be6bda9d1fcfe84a723c8fc` | 45186 HTTP 200 |
| HTTPS GET `…/index.html` | `1e7121225d6cb339e127657c463626dbfed13d751be6bda9d1fcfe84a723c8fc` | 45186 |
| Esperado (prompt / `design.md`) | `1e7121225d6cb339e127657c463626dbfed13d751be6bda9d1fcfe84a723c8fc` | 45186 |

`cmp` disco vs `/tmp/906-B-https.html`: **IDENTICAL**. HTTP 200 isolado **não** é o gate.

## 2. Detector Impeccable

- Alvo: `frontend/public/prototypes/card-906-discovery-metrics-grid/index.html`
- Comando: `node .agents/skills/impeccable/scripts/detect.mjs --json` → `[]`, exit 0.
- **0 findings determinísticos.** Nada por classificar → sem bloqueio deste item.

## 3. Clone / fidelidade (superfície existing)

- Catálogo `scripts/process-fsm/route-landmarks.yaml` `/combo/discovery`: `Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`.
- Proto: **10 pares** `COPIED:start` / `COPIED:end` (shell AppNav, heading, modos, rascunho, preflight, chrome Acompanhar, grelha parciais, header leaderboard, grelha Decidir, nota rank-stable). **2** `DELTA:start` (colunas Sharpe/Win%/CAGR em Acompanhar e Decidir).
- Toggle Antes/Depois: **ausente**. Botões «Antes»/«Depois» = 0. Comentário «Sem painel ANTES/DEPOIS» não é painel. Tabs `role=tab` mudam markup (`.modepanel.active` único). URL canónica = `index.html` clone+delta.
- Montar entra no clone só para landmarks; sem `table.lb` no painel.

## 4. Browser real — matriz (desktop 1440×900 e mobile 390×844)

Console error = 0; warning = 0; pageerror = 0; responses ≥400 = 0. Overflow documento `scrollWidth==clientWidth` (1440 e 390). Gate bruto: `.impeccable/critique/906-B-gate.json` (55/55 ×2).

| # | Assert | Desktop | Mobile |
|---|---|---|---|
| 1 | Digest disco == HTTPS (não basta HTTP 200) | PASS | PASS |
| 2 | Landmark h1 `Descoberta de estratégias swing` visível | PASS | PASS |
| 3 | Landmark `Preflight` visível após tab Montar | PASS | PASS |
| 4 | Landmark `Rascunho de varredura` visível após tab Montar | PASS | PASS |
| 5 | Default Acompanhar; thead/células com seis métricas (Calmar, Max DD, Trades/cobertura, Sharpe, Win%, CAGR) | PASS | PASS (cards `data-label`) |
| 6 | Acompanhar: 0 botão «+ detalhes»; Sharpe `0,31`; CAGR `17,8%` | PASS | PASS |
| 7 | CAGR anualizado `17,8%` ≠ Return `+47.916%` (Acompanhar e Decidir) | PASS | PASS |
| 8 | Decidir: mesmas seis colunas visíveis com detalhes `display:none` | PASS | PASS |
| 9 | Amostra insuficiente: selo + Sharpe/Win%/CAGR = `N/A` | PASS | PASS |
| 10 | Sort: só `Calmar` e `CAGR vs B&H` (2 options; sem Sharpe/Win%/CAGR) | PASS | PASS |
| 11 | «+ detalhes» `none→block`; B&H / PF / janela; sem duplicar Sharpe/Win%/CAGR | PASS | PASS |
| 12 | Colunas continuam visíveis após expandir | PASS | PASS |
| 13 | Montar: Preflight + Rascunho; 0 `table.lb` no painel | PASS | PASS |
| 14 | Zero botões Antes/Depois | PASS | PASS |
| 15 | 0 console de impacto / 0 pageerror / 0 ≥400 | PASS | PASS |

Pixels desktop Acompanhar: thead Calmar · Max DD · Trades/cobertura · Sharpe · Win% (acerto) · CAGR (anualizado); linha 1 `22,53` / `−16,5%` / `30 · 100%` / `0,31` / `46,7%` / `17,8%`; CAGR x=1308 dentro de 1440 (sem scroll horizontal no documento). Decidir: CAGR `17,8%` na grelha com «− detalhes» aberto a mostrar B&H/PF/janela. Montar: Rascunho + Preflight, sem grelha.

Pixels mobile (após scroll à grelha): cards em pares Calmar/Max DD, Trades/Sharpe, Win rate/Retorno (CAGR) `17,8%`; sem «+ detalhes» no Acompanhar. Decidir: mesmas seis métricas com «+ detalhes» colapsado; linha `Amostra insuficiente` com N/A ×6. Montar: Rascunho + Preflight, sem tabela de métricas.

Rota viva **não usada**. Browser correu só no proto.

## 5. Findings (toda finding classificada)

### P0 — nenhum

Landmarks 3/3 no proto; digest servido == local == esperado; sem painel ANTES/DEPOIS canónico; 10 pares COPIED + 2 DELTA; seis colunas visíveis sem expandir; CAGR `17,8%` não Return; amostra insuficiente N/A; sort só Calmar / CAGR vs B&H; Montar sem grelha. Fidelidade ok → não BLOCKED.

### P1 — nenhum

Delta observável nos dois viewports. Detector `[]`. HTML sem toggle `aria-pressed` morto. Acompanhar não esconde métricas atrás de expansão.

### P3 — aceites (Apply / clone chrome; não reabrir como P0/P1)

- **P3-1 Chrome Acompanhar abaixo da dobra em 390×844.** Sweep/progress ocupam o primeiro ecrã; a grelha (y≈1292) exige scroll. Contrato («nunca atrás de + detalhes») cumpre-se; clone do chrome vivo. Apply não precisa encolher o progresso neste card.
- **P3-2 Chip NO-GO full-width** no card mobile (`flex: 1 0 100%` no wrap ≤720px) e `span{display:block}` no desktop. Selo legível; Apply pode encolher o chip.
- **P3-3 Leaderboard `248 de 248 candidatos · página 1 de 21` com 4 `<tr>`.** Mock; Apply liga à paginação real.
- **P3-4 IDs fictícios `#c906grid` / `#PF-906-24`.** Chrome copiado. Apply não precisa dos ids.
- **P3-5 `min-width:1080px` em `table.lb`.** Já aceite no `design.md` (overflow-x desktop). Documento `sw==cw` em 1440; as seis colunas cabem.
- **P3-6 Montar condensado** vs `DiscoveryPage.tsx` viva (eixos resumidos). Landmarks presentes; sem delta deste card.
- **P3-7 `th:last-child` / `fmtPct`/`fmtNum` / não duplicar Sharpe/Win%/CAGR em «+ detalhes».** Já no contrato P3 do `design.md`; browser confirmou a não-duplicação.

Observações (não-findings): thead mobile está `clip-path` (card-stack); métricas via `data-label`/`::before`. Motor URL do detector não invocado (scan estático `[]` cobre o HTML versionado). Overlay `detect.js` não injectado — evidência = CLI + Playwright no proto servido.

## 6. Veredito

**PASS** — zero P0/P1 abertos; detector `[]` classificado; digest idêntico; clone+delta (não ANTES/DEPOIS); `/login` não usado como prova da rota; matriz visível nos dois viewports. HTTP 200 sozinho não sustentaria este veredito.

Disposition: crítico não pede rework. P3 aceites no Apply.

## 7. Referências

- Proto URL: https://dev.criptofarol.com.br/prototypes/card-906-discovery-metrics-grid/
- Digest: `1e7121225d6cb339e127657c463626dbfed13d751be6bda9d1fcfe84a723c8fc`
- Snapshot: `.impeccable/critique/906-card-906-discovery-metrics-grid-assessment-B.md`
- Gate bruto: `.impeccable/critique/906-B-gate.json`
- PNGs: `.impeccable/critique/906-B-desktop-1440x900.png`, `906-B-desktop.png`, `906-B-desktop-decidir.png`, `906-B-desktop-montar.png`, `906-B-mobile-390x844.png`, `906-B-mobile.png`, `906-B-mobile-acomp-grid.png`, `906-B-mobile-decidir.png`, `906-B-mobile-decidir-cagr.png`, `906-B-mobile-montar.png`, `906-B-mobile-montar-preflight.png`
