# Assessment B (detector + browser real) — card 944 · change card-944-discovery-favorites-nomenclature

> Assessor B isolado, mesmo modelo, sem transcript de A nem do pai. Sem nested-spawn.
> Nada movido (Status, branch, worktree); nenhuma edição fora deste ficheiro, PNGs `944-B-*` e `944-B-gate.json`.
> Tokens parseáveis do `design.md` (rubrica D4): `UI impact: affected` · `live_route: /combo/discovery` · `surface: existing`.

```
Assessment B 944
digest_match: yes
detector: 0 findings
P0: nenhum
P1: nenhum
P3: chrome Acompanhar abaixo da dobra no 390; chip NO-GO full-width; leaderboard 309/309 mock 4 linhas; min-width 1240 (Ação clip 1440); modal «Retorno (CAGR)» 3,7%; Montar condensado; data-label Win rate/Maximum Drawdown
verdict: PASS
```

- UTC: 2026-09-14T20:56Z
- Tuple (read-only): `bound_card=944` · `q_git=card-944-discovery-favorites-nomenclature`. Sem `process_event`.
- Protótipo: `frontend/public/prototypes/card-944-discovery-favorites-nomenclature/index.html`
- Servido: https://dev.criptofarol.com.br/prototypes/card-944-discovery-favorites-nomenclature/
- Digest esperado: `e8e632a2d44c34ac7e93674adad5599f3a2b159ac6a0a57ae6a38640c8f44ed3` · 65246 bytes
- Rota viva: https://dev.criptofarol.com.br/combo/discovery — **não usada como prova**. GET devolve o shell Vite (`<title>frontend</title>`), não a grelha. `/login` **não** conta. Clone avaliado só no proto HTTPS + landmarks do catálogo.
- Browser: Playwright Python + Chromium 1243 (`chrome-linux-arm64`) sob `xvfb-run -a`, `--no-sandbox`. Viewports 1440×900 e 390×844. URL canónica do proto (não `file://`, não `/login`).
- Detector: `node .agents/skills/impeccable/scripts/detect.mjs --json` no HTML versionado (cwd worktree).

## 1. Digest servido == local

| Ponta | sha256 | bytes |
|---|---|---|
| Disco | `e8e632a2d44c34ac7e93674adad5599f3a2b159ac6a0a57ae6a38640c8f44ed3` | 65246 |
| HTTPS GET `/prototypes/card-944-discovery-favorites-nomenclature/` | `e8e632a2d44c34ac7e93674adad5599f3a2b159ac6a0a57ae6a38640c8f44ed3` | 65246 HTTP 200 |
| HTTPS GET `…/index.html` | `e8e632a2d44c34ac7e93674adad5599f3a2b159ac6a0a57ae6a38640c8f44ed3` | 65246 |
| Esperado (prompt / `design.md`) | `e8e632a2d44c34ac7e93674adad5599f3a2b159ac6a0a57ae6a38640c8f44ed3` | 65246 |

`cmp` disco vs `/tmp/944-B-https.html` e vs `…/index.html`: **IDENTICAL**. HTTP 200 isolado **não** é o gate.

## 2. Detector Impeccable

- Alvo: `frontend/public/prototypes/card-944-discovery-favorites-nomenclature/index.html`
- Comando: `node .agents/skills/impeccable/scripts/detect.mjs --json` → `[]`, exit 0.
- **0 findings determinísticos.** Nada por classificar → sem bloqueio deste item.

## 3. Clone / fidelidade (superfície existing)

- Catálogo `scripts/process-fsm/route-landmarks.yaml` `/combo/discovery`: `Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`.
- Proto: **11 pares** `COPIED:start` / `COPIED:end` (shell AppNav, heading, modos, run selector, rascunho, preflight, chrome Acompanhar, grelha parciais, header leaderboard, grelha Decidir, nota rank-stable). **5** `DELTA:start` (ordem parciais, coluna Ação parciais, acções linha 1, ordem Decidir, diálogos reutilizados).
- Toggle Antes/Depois: **ausente**. Botões «Antes»/«Depois» = 0. Comentário «Sem painel ANTES/DEPOIS» não é painel. Tabs `role=tab` mudam markup (`.modepanel.active` único). URL canónica = `index.html` clone+delta.
- Montar entra no clone só para landmarks; sem `table.lb` no painel.
- Chrome-only **não** sustentaria fidelidade: a evidência é a ordem/nomes nas duas grelhas (Sharpe → Trades → Win% → Return → Max DD → Calmar → CAGR anualizado), Return `+12,8%` ≠ CAGR `3,7%`, e a ausência do nome `Trades/cobertura`.

## 4. Browser real — matriz (desktop 1440×900 e mobile 390×844)

Console error = 0; warning = 0; pageerror = 0; responses ≥400 = 0. Overflow documento `scrollWidth==clientWidth` (1425/1425 e 375/375). Gate bruto: `.impeccable/critique/944-B-gate.json` (65/65 ×2). Headers via `span:not(.th-hint)`.

| # | Assert | Desktop | Mobile |
|---|---|---|---|
| 1 | Digest disco == HTTPS (não basta HTTP 200) | PASS | PASS |
| 2 | Landmark h1 `Descoberta de estratégias swing` visível | PASS | PASS |
| 3 | Landmark `Preflight` visível após tab Montar | PASS | PASS |
| 4 | Landmark `Rascunho de varredura` visível após tab Montar | PASS | PASS |
| 5 | Default Acompanhar; 0 «+ detalhes» nas parciais | PASS | PASS |
| 6 | Ordem Sharpe → Trades → Win% → Return → Max DD → Calmar → CAGR anualizado nas duas grelhas, sem expandir | PASS | PASS (cards `data-label`) |
| 7 | ALPHA Return `+12,8%` ≠ CAGR anualizado `3,7%` (Acompanhar e Decidir) | PASS | PASS |
| 8 | Sem coluna nomeada `Trades/cobertura`; cabeçalho `Trades` + hint `cobertura` | PASS | PASS |
| 9 | Amostra insuficiente: selo + Return/CAGR = `N/A` | PASS | PASS |
| 10 | Sort: só `Calmar` e `CAGR vs B&H` (2 options) | PASS | PASS |
| 11 | «+ detalhes» colapsado nas métricas; aberto mostra B&H/PF/janela sem duplicar Return/CAGR | PASS | PASS |
| 12 | Montar: Preflight + Rascunho; 0 `table.lb` no painel | PASS | PASS |
| 13 | Zero botões Antes/Depois | PASS | PASS |
| 14 | 0 console de impacto / 0 pageerror / 0 ≥400 | PASS | PASS |

Pixels desktop Acompanhar: thead Sharpe · Trades (cobertura) · Win% (acerto) · Return (janela) · Max DD · Calmar (CAGR ÷ Max DD) · CAGR anualizado; linha ALPHA `0,31` / `30 · 100% velas` / `46,7%` / `+12,8%` / `−16,5%` / `22,53` / `3,7%`. Return x=881, CAGR x=1168, ambos em `table-cell`. Decidir: mesma ordem; Return `+12,8%` x=918 ≠ CAGR `3,7%` x=1188 com «+ detalhes» `display:none`. Linha insuficiente: selo + Return/CAGR `N/A`. Montar: Rascunho + Preflight, sem grelha.

Pixels mobile (cards): pares Sharpe/Trades, Win rate/Return `+12,8%`, Maximum Drawdown/Calmar, CAGR anualizado `3,7%` sozinho; cobertura `100% velas` sob Trades. Sem «+ detalhes» no Acompanhar. Decidir: mesmas métricas com «+ detalhes» colapsado; linha `Amostra insuficiente` com N/A em Return e CAGR. Montar: Rascunho + Preflight, sem tabela de métricas.

Rota viva **não usada**. Browser correu só no proto.

## 5. Findings (toda finding classificada)

### P0 — nenhum

Landmarks 3/3 no proto; digest servido == local == esperado; sem painel ANTES/DEPOIS canónico; 11 pares COPIED + 5 DELTA; sete métricas visíveis sem expandir na ordem de Favoritos + extras; Return `+12,8%` não é CAGR `3,7%`; Trades não se chama `Trades/cobertura`; amostra insuficiente N/A; sort só Calmar / CAGR vs B&H; Montar sem grelha. Fidelidade ok → não BLOCKED.

### P1 — nenhum

Delta observável nos dois viewports. Detector `[]`. HTML sem toggle `aria-pressed` morto. Acompanhar não esconde métricas atrás de expansão. Contrato visível das duas grelhas cumpre-se.

### P3 — aceites (Apply / clone chrome; não reabrir como P0/P1)

- **P3-1 Chrome Acompanhar abaixo da dobra em 390×844.** Sweep/progress ocupam o primeiro ecrã; a grelha exige scroll. Contrato («nunca atrás de + detalhes») cumpre-se; clone do chrome vivo.
- **P3-2 Chip NO-GO full-width** no card mobile (`flex: 1 0 100%` no wrap ≤720px). Selo legível; Apply pode encolher o chip.
- **P3-3 Leaderboard `309 de 309 candidatos · página 1 de 26` com 4 `<tr>`.** Mock; Apply liga à paginação real.
- **P3-4 `min-width:1240px` em `table.lb`.** Já no Apply contract (7 métricas; overflow-x desktop). Documento `sw==cw` em 1440; Ação corta no viewport até scroll do `.table-wrap`.
- **P3-5 Modal promover ainda rotula `3,7%` como «Retorno (CAGR)».** Diálogos reutilizados do Decidir vivo (#916); fora do delta das grelhas. Contrato deste card é a ordem/nomes nas duas tabelas. Apply pode alinhar o rótulo do modal a Return vs CAGR anualizado.
- **P3-6 Montar condensado** vs `DiscoveryPage.tsx` viva (eixos resumidos). Landmarks presentes; sem delta deste card.
- **P3-7 `data-label` mobile `Win rate` / `Maximum Drawdown` vs thead `Win%` / `Max DD`; wiring `total_return` / `formatCompoundReturn`.** Já no P3 do `design.md`. Thead via `span:not(.th-hint)` cumpre os nomes do contrato.

Observações (não-findings): thead mobile está `clip-path` (card-stack); métricas via `data-label`/`::before`. Motor URL do detector não invocado (scan estático `[]` cobre o HTML versionado). Overlay `detect.js` não injectado — evidência = CLI + Playwright no proto servido. GET `/combo/discovery` = shell Vite; não é clone.

## 6. Veredito

**PASS** — zero P0/P1 abertos; detector `[]` classificado; digest idêntico; clone+delta (não ANTES/DEPOIS); `/login` não usado como prova da rota; matriz visível nos dois viewports. HTTP 200 sozinho não sustentaria este veredito.

Disposition: crítico não pede rework. P3 aceites no Apply.

## 7. Referências

- Proto URL: https://dev.criptofarol.com.br/prototypes/card-944-discovery-favorites-nomenclature/
- Digest: `e8e632a2d44c34ac7e93674adad5599f3a2b159ac6a0a57ae6a38640c8f44ed3`
- Snapshot: `.impeccable/critique/944-card-944-discovery-favorites-nomenclature-assessment-B.md`
- Gate bruto: `.impeccable/critique/944-B-gate.json`
- PNGs: `.impeccable/critique/944-B-desktop-1440x900.png`, `944-B-desktop.png`, `944-B-desktop-acomp-grid.png`, `944-B-desktop-decidir.png`, `944-B-desktop-montar.png`, `944-B-desktop-montar-preflight.png`, `944-B-mobile-390x844.png`, `944-B-mobile.png`, `944-B-mobile-acomp-grid.png`, `944-B-mobile-acomp-alpha.png`, `944-B-mobile-acomp-alpha-vp.png`, `944-B-mobile-decidir.png`, `944-B-mobile-decidir-alpha.png`, `944-B-mobile-decidir-na.png`, `944-B-mobile-montar.png`, `944-B-mobile-montar-preflight.png`
