# Assessment B (detector + browser real) — card 948 · change card-948-discovery-deleted-favorite

> Assessor B isolado, mesmo modelo, sem transcript de A nem do pai. Sem nested-spawn.
> Nada movido (Status, branch, worktree); nenhuma edição fora deste ficheiro, PNGs `948-B-*` e `948-B-gate.json`.
> Tokens parseáveis do `design.md` (rubrica D4): `UI impact: affected` · `live_route: /combo/discovery` · `surface: existing`.

```
Assessment B 948
digest_match: yes
detector: 0 findings
P0: nenhum
P1: nenhum
P3: chrome Decidir dobra 1440; Ação clip Prom/Já e; mobile testemunhas abaixo da dobra; leaderboard 680/680 mock; Montar condensado; data-label Win rate/Maximum Drawdown
verdict: PASS
```

- UTC: 2026-09-16T01:04Z
- Tuple (read-only): `bound_card=948` · `q_git=card-948-discovery-deleted-favorite` · Status GraphQL pontual `Design` (Project 1 / `oalansilva`). Sem `process_event`.
- Protótipo: `frontend/public/prototypes/card-948-discovery-deleted-favorite/index.html`
- Servido: https://dev.criptofarol.com.br/prototypes/card-948-discovery-deleted-favorite/
- Digest esperado: `1f8b13c879526506637fe6cce691b87db9d38fd5d4c7047e4be9d839bba13d74` · 69158 bytes
- Rota viva: https://dev.criptofarol.com.br/combo/discovery — **não usada como prova**. GET devolve o shell Vite (`<title>frontend</title>`), 455 bytes, HTTP 200, **não** `/login`. `/login` **não** conta. Clone avaliado só no proto HTTPS + landmarks do catálogo.
- Browser: Playwright Python + Chromium 1243 (`chrome-linux-arm64`) sob `xvfb-run -a`, `--no-sandbox`. Viewports 1440×900 e 390×844. URL canónica do proto (não `file://`, não `/login`).
- Detector: `node .agents/skills/impeccable/scripts/detect.mjs --json` no HTML versionado (cwd worktree).

## 1. Digest servido == local

| Ponta | sha256 | bytes |
|---|---|---|
| Disco | `1f8b13c879526506637fe6cce691b87db9d38fd5d4c7047e4be9d839bba13d74` | 69158 |
| HTTPS GET `/prototypes/card-948-discovery-deleted-favorite/` | `1f8b13c879526506637fe6cce691b87db9d38fd5d4c7047e4be9d839bba13d74` | 69158 HTTP 200 |
| HTTPS GET `…/index.html` | `1f8b13c879526506637fe6cce691b87db9d38fd5d4c7047e4be9d839bba13d74` | 69158 |
| Esperado (prompt / `design.md`) | `1f8b13c879526506637fe6cce691b87db9d38fd5d4c7047e4be9d839bba13d74` | 69158 |

`cmp` disco vs `/tmp/948-B-https-dir.html` e vs `…/index.html`: **IDENTICAL**. HTTP 200 isolado **não** é o gate.

## 2. Detector Impeccable

- Alvo: `frontend/public/prototypes/card-948-discovery-deleted-favorite/index.html`
- Comando: `node .agents/skills/impeccable/scripts/detect.mjs --json` → `[]`, exit 0.
- **0 findings determinísticos.** Nada por classificar → sem bloqueio deste item.

## 3. Clone / fidelidade (superfície existing)

- Catálogo `scripts/process-fsm/route-landmarks.yaml` `/combo/discovery`: `Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`.
- Proto: **11 pares** `COPIED:start` / `COPIED:end` (shell AppNav, heading, modos, run selector, rascunho, preflight, chrome Acompanhar, grelha parciais, header leaderboard, grelha Decidir, nota rank-stable). Soma UTF-8 dos pares = **31631 > 0**. **10** `DELTA:start` (ordem parciais, coluna Ação parciais, órfão Já existe→Promover Acompanhar, órfão tier 3 Acompanhar, vivo Acompanhar, ordem Decidir, órfão Já existe→Promover Decidir, órfão tier 3 Decidir, vivo Decidir, diálogos).
- Toggle Antes/Depois: **ausente**. Botões «Antes»/«Depois» = **0**. Comentário «Sem painel ANTES/DEPOIS» não é painel. Tabs `role=tab` mudam markup (`.modepanel.active` único). Default = **Decidir** (`aria-selected=true`). URL canónica = `index.html` clone+delta.
- Montar entra no clone só para landmarks; Preflight + Rascunho visíveis após o tab.
- Chrome-only **não** sustentaria fidelidade: a evidência é a verdade das três linhas (órfão `RS-E2FF8F9FEB` Promover sem nota; órfão `RS-EA2A508DBD` Promover sem Favorito tier 3; vivo Já existe + Equivale ao favorito ativo 12) em Decidir **e** Acompanhar.

## 4. Browser real — matriz (desktop 1440×900 e mobile 390×844)

Console error = 0; warning = 0; pageerror = 0; responses ≥400 = 0. Overflow documento `scrollWidth==clientWidth` (1440/1440 e 390/390). Gate bruto: `.impeccable/critique/948-B-gate.json` (38/38 ×2).

| # | Assert | Desktop | Mobile |
|---|---|---|---|
| 1 | Digest disco == HTTPS (não basta HTTP 200) | PASS | PASS |
| 2 | Landmark h1 `Descoberta de estratégias swing` visível | PASS | PASS |
| 3 | Landmark `Preflight` visível após tab Montar | PASS | PASS |
| 4 | Landmark `Rascunho de varredura` visível após tab Montar | PASS | PASS |
| 5 | Default Decidir (`aria-selected=true`, painel active) | PASS | PASS |
| 6 | `RS-E2FF8F9FEB` presente; Promover; sem Já existe; sem Equivale ao favorito ativo N | PASS | PASS |
| 7 | `RS-EA2A508DBD` presente; Promover; sem Favorito tier 3 | PASS | PASS |
| 8 | Linha viva: Já existe + Equivale ao favorito ativo 12 | PASS | PASS |
| 9 | Acompanhar: mesma verdade nas três linhas | PASS | PASS |
| 10 | Zero botões Antes/Depois | PASS | PASS |
| 11 | 0 console de impacto / 0 pageerror / 0 ≥400 | PASS | PASS |
| 12 | COPIED pares UTF-8 soma > 0 (31631) | PASS | PASS |

Pixels desktop Decidir: rank 1 `RS-E2FF8F9FEB` BTC/USDT, botão Promover, sem nota de favorito; rank 2 `RS-EA2A508DBD` ETH/USDT Promover, sem Favorito tier 3; rank 3 `Já existe` + `Equivale ao favorito ativo 12`. Acompanhar: mesmas três verdades (BTC Promover · ETH Promover · SOL Já existe + Equivale 12). Montar: Rascunho + Preflight visíveis.

Pixels mobile (cards): `RS-E2FF8F9FEB` AÇÃO Promover; `RS-EA2A508DBD` Promover; vivo `Já existe` + `Equivale ao favorito ativo 12`. Acompanhar idêntico. Montar: Rascunho no fluxo; Preflight após scroll (y=1119).

Rota viva **não usada**. Browser correu só no proto.

## 5. Findings (toda finding classificada)

### P0 — nenhum

Landmarks 3/3 no proto (heading no default; Preflight/Rascunho após Montar); digest servido == local == esperado; sem painel ANTES/DEPOIS canónico; 11 pares COPIED (UTF-8 31631) + 10 DELTA; default Decidir; órfão `RS-E2FF8F9FEB` Promover sem Já existe / sem Equivale; órfão `RS-EA2A508DBD` Promover sem Favorito tier 3; vivo Já existe + Equivale ao favorito ativo 12; Acompanhar igual; 0 console/pageerror. Fidelidade ok → não BLOCKED.

### P1 — nenhum

Delta observável nos dois viewports (innerText + pixels após scrollIntoView). Detector `[]`. HTML sem toggle Antes/Depois. Contrato visível das três linhas cumpre-se em Decidir e Acompanhar.

### P3 — aceites (Apply / clone chrome; não reabrir como P0/P1)

- **P3-1 Chrome Decidir na dobra em 1440×900.** Rank 1 começa ~y=775; o botão Ação corta para `Prom` / `Já e` por `min-width` da grelha (clone do Decidir vivo). innerText = `Promover` / `Já existe`. Contrato das três verdades cumpre-se; clip é chrome, não o delta.
- **P3-2 Testemunhas abaixo da dobra em 390×844.** Primeiro ecrã Decidir = heading + tabs + run + leaderboard chrome; rank 1 y=1181. Scroll revela Promover / Já existe. Clone do chrome vivo; não esconde o delta atrás de + detalhes.
- **P3-3 Leaderboard `680 de 680 candidatos · página 1 de 26` com 4 linhas Decidir.** Mock; Apply liga à paginação real.
- **P3-4 Ação clip também no Acompanhar desktop** (`Prom` / `Já e`). Mesmo chrome da tabela.
- **P3-5 Montar condensado** vs `DiscoveryPage.tsx` viva (eixos resumidos; Preflight mobile y=1119). Landmarks presentes; sem delta deste card.
- **P3-6 `data-label` mobile `Win rate` / `Maximum Drawdown` vs thead `Win%` / `Max DD`.** Residual do clone das grelhas (#944). Fora do delta órfão/vivo.

Observações (não-findings): thead mobile está em card-stack; métricas via `data-label`. Motor URL do detector não invocado (scan estático `[]` cobre o HTML versionado). Overlay `detect.js` não injectado — evidência = CLI + Playwright no proto servido. GET `/combo/discovery` = shell Vite; não é clone. Handler JS pós-Promover que pinta `Favorito tier 3` é simulação do sucesso de promoção, não o default das linhas órfãs.

## 6. Veredito

**PASS** — zero P0/P1 abertos; detector `[]` classificado; digest idêntico; clone+delta (não ANTES/DEPOIS); `/login` não usado como prova da rota; matriz visível nos dois viewports. HTTP 200 sozinho não sustentaria este veredito.

Disposition: crítico não pede rework. P3 aceites no Apply.

## 7. Referências

- Proto URL: https://dev.criptofarol.com.br/prototypes/card-948-discovery-deleted-favorite/
- Digest: `1f8b13c879526506637fe6cce691b87db9d38fd5d4c7047e4be9d839bba13d74`
- Snapshot: `.impeccable/critique/948-card-948-discovery-deleted-favorite-assessment-B.md`
- Gate bruto: `.impeccable/critique/948-B-gate.json`
- PNGs: `.impeccable/critique/948-B-desktop-1440x900.png`, `948-B-desktop.png`, `948-B-desktop-decidir.png`, `948-B-desktop-decidir-orphan-ja.png`, `948-B-desktop-decidir-orphan-t3.png`, `948-B-desktop-decidir-live.png`, `948-B-desktop-acomp.png`, `948-B-desktop-acomp-orphan-ja.png`, `948-B-desktop-acomp-live.png`, `948-B-desktop-montar.png`, `948-B-desktop-montar-preflight.png`, `948-B-mobile-390x844.png`, `948-B-mobile.png`, `948-B-mobile-decidir.png`, `948-B-mobile-decidir-orphan-ja.png`, `948-B-mobile-decidir-orphan-t3.png`, `948-B-mobile-decidir-live.png`, `948-B-mobile-acomp.png`, `948-B-mobile-acomp-orphan-ja.png`, `948-B-mobile-acomp-live.png`, `948-B-mobile-montar.png`, `948-B-mobile-montar-preflight.png`
- `proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)`
