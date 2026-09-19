# Assessment B (detector + browser real) — card 969 · change card-969-discovery-selo-go-nogo

> Assessor B isolado, mesmo modelo, sem transcript de A nem do pai. Sem nested-spawn.
> Nada movido (Status, branch, worktree); escrita só neste ficheiro, PNGs `969-B-*`, JSON de gate e o script do gate.
> Tokens parseáveis do `design.md` (rubrica D4, não reabrir parser): `UI impact: affected` · `live_route: /combo/discovery` · `surface: existing`.

```
Assessment B 969
digest_match: yes
detector: 0 findings
P0: nenhum
P1: nenhum
P3: chip GO/NO-GO ~292px no mobile (barra outline); Promover desktop recortado + scrollbar horizontal; Montar condensado; chrome #0d7990ca / #PF-492; 7 de 8 mock
verdict: PASS
```

- UTC: 2026-09-18T13:15:41Z
- Tuple (read-only): `q=Design` · `bound_card=969` · `q_git=card-969-discovery-selo-go-nogo` (GraphQL pontual `repository.issue(number:969).projectItems` em `oalansilva/crypto` → Status `Design`; project 1 / `oalansilva`). Sem `process_event`. Sem `gh project item-list`.
- Protótipo: `frontend/public/prototypes/card-969-discovery-selo-go-nogo/index.html`
- Servido: https://dev.criptofarol.com.br/prototypes/card-969-discovery-selo-go-nogo/
- Digest esperado: `04967d7546f8d67a1d2e6a8db246faeefb5e1c3ab5283e5d61eb58c8305d47fe` · 50488 bytes
- Rota viva: https://dev.criptofarol.com.br/combo/discovery — **sem sessão**; Playwright aterrissou em `/login` (`Bem-vindo de volta` / campo senha). `/login` **não** é a rota; **não** autoriza PASS de clone. Clone avaliado pelo proto + landmarks do catálogo.
- Browser: Playwright Python + Chromium 1243 `chrome-linux-arm64` headed sob `xvfb-run -a`. HTTPS (não `file://`). Desktop 1440×900 e mobile 390×844.
- Detector: `node .agents/skills/impeccable/scripts/detect.mjs --json` no HTML versionado.
- Gate JSON: `.impeccable/critique/969-B-gate.json`

## 1. Digest servido == local

| Ponta | sha256 | bytes |
|---|---|---|
| Disco | `04967d7546f8d67a1d2e6a8db246faeefb5e1c3ab5283e5d61eb58c8305d47fe` | 50488 |
| HTTPS GET `/prototypes/card-969-discovery-selo-go-nogo/` | `04967d7546f8d67a1d2e6a8db246faeefb5e1c3ab5283e5d61eb58c8305d47fe` | 50488 HTTP/2 200 |
| HTTPS GET `…/index.html` | `04967d7546f8d67a1d2e6a8db246faeefb5e1c3ab5283e5d61eb58c8305d47fe` | 50488 HTTP/2 200 |
| Esperado (prompt / `design.md`) | `04967d7546f8d67a1d2e6a8db246faeefb5e1c3ab5283e5d61eb58c8305d47fe` | 50488 |

`cmp` disco vs HTTPS dir e vs `index.html`: **IDENTICAL**. HTTP 200 isolado **não** é o gate. Digest **não** mudou → evidência do autor válida neste item.

## 2. Detector Impeccable

- Alvo: `frontend/public/prototypes/card-969-discovery-selo-go-nogo/index.html`
- Comando: `node .agents/skills/impeccable/scripts/detect.mjs --json` → `[]`, exit 0.
- **0 findings determinísticos.** Nada crítico → sem P0 deste item.
- Overlay live-server / `detect.js` não injectado: scan estático `[]` cobre o HTML versionado; motor URL não invocado.

## 3. Clone / fidelidade (superfície existing)

- Catálogo `scripts/process-fsm/route-landmarks.yaml` `/combo/discovery`: `Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`.
- Proto: **10 pares** `COPIED:start` / `COPIED:end`; soma UTF-8 dos intervalos = **27812** (> 0). Shell AppNav, heading, modos, rascunho, Preflight, chrome Acompanhar, cascas das grelhas, nota educacional.
- Toggle Antes/Depois: **ausente**. Botões «Antes»/«Depois» = **0** nos dois viewports (prova única de não-painel). `aria-pressed` = 0. URL canónica = `index.html` clone+delta, estado visível Decidir.
- Tokens D4 presentes em linhas próprias no `design.md` e iguais ao prompt.

## 4. Browser real — matriz (desktop 1440×900 e mobile 390×844)

Console error = 0; pageerror = 0; responses ≥400 = 0. Overflow desktop `sw==cw==1425` (viewport útil headed). Mobile `sw==cw==390`.

| # | Assert | Desktop | Mobile |
|---|---|---|---|
| 1 | Digest disco == HTTPS (não basta HTTP 200) | PASS | PASS |
| 2 | Landmark h1 `Descoberta de estratégias swing` | PASS | PASS |
| 3 | Landmark `Preflight` visível após tab Montar (`aside[aria-label="Preflight da varredura"]` h2) | PASS | PASS (abaixo da dobra; scroll) |
| 4 | Landmark `Rascunho de varredura` visível após tab Montar | PASS | PASS |
| 5 | Default Decidir; BTC `RS-E0E30719CC` selo **GO** | PASS | PASS (scroll da linha) |
| 6 | AGLD **NO-GO** + motivo Holdout (Sharpe OOS −0,18 ≤ 0) | PASS | PASS |
| 7 | DOGE **NO-GO** + motivo Treino (Calmar 0,42 < 1) | PASS | PASS |
| 8 | ADA **Baixa amostra** sem chip GO/NO-GO; Promover da linha = `Baixa amostra` disabled | PASS | PASS |
| 9 | Promover enabled nos NO-GO elegíveis (AGLD e DOGE, `disabled=false`) | PASS | PASS |
| 10 | 0 botões Antes/Depois; 3 modos, não grelha ANTES/DEPOIS | PASS | PASS |
| 11 | 0 console error / 0 pageerror / 0 ≥400 | PASS | PASS |
| 12 | COPIED pares UTF-8 > 0 | PASS (27812) | PASS |

Rota viva sem sessão: `final_url=https://dev.criptofarol.com.br/login`, h1 `Bem-vindo de volta`. **Não usada como evidência de clone.**

Pixels desktop Decidir: ranks 1–4 GO (BTC `RS-E0E30719CC`, ETH, SOL 4h, LINK short); rank 5 AGLD `NO-GO` + `Holdout — Sharpe OOS −0,18 ≤ 0 (limiar > 0)`; rank 6 DOGE `NO-GO` + `Treino — Calmar 0,42 < 1`; ADA `Baixa amostra` sem selo, rank `—`.

Pixels mobile: mesmo contrato após scroll; Promover fill amarelo enabled no AGLD/DOGE; ADA só aviso de amostra.

## 5. Findings (toda finding classificada)

### P0 — nenhum

Landmarks 3/3 no proto; digest servido == local == esperado; sem painel ANTES/DEPOIS; 10 pares COPIED com bytes > 0; GO no testemunho BTC; NO-GO com motivo Holdout e Treino; Baixa amostra sem chip; Promover no NO-GO elegível permanece; detector `[]`.

### P1 — nenhum

Delta observável nos dois viewports (mobile abaixo da dobra, não ausente). Selo tem texto `GO`/`NO-GO` (não só cor). Motivo na linha, não tooltip-only.

### P3 — aceites (Apply / clone chrome; não reabrir como P0/P1)

- **P3-1 Chip GO/NO-GO largo no mobile.** Desktop: chip compacto (`inline-flex` / `width:fit-content`). Mobile 390: bbox do selo **292×26** (quase a largura do card); outline vazio com o texto à direita, efeito da célula `display:flex; justify-content:space-between` no card. Texto legível; Apply pode encolher o chip.
- **P3-2 Coluna Ação recortada no desktop 1440.** `Promover`/`Excluir` cortados; `table-wrap` mostra scrollbar horizontal. Clone chrome da grelha; CTA existe e o gate de enabled passou no DOM.
- **P3-3 Montar condensado** vs `DiscoveryPage.tsx` viva (eixos resumidos). Landmarks presentes; sem delta deste card.
- **P3-4 Chrome copiado** `#0d7990ca` / snapshot 492 / `#PF-492`. Apply liga à varredura real.
- **P3-5 Leaderboard `7 de 8 candidatos`** mock de proto.

Observações (não-findings): selos AGLD/DOGE/ADA abaixo da dobra no desktop 900 e no mobile 844 sem scroll — visíveis na linha após scroll, sem gráfico/dialog. `/login` não conta como clone. Overlay Impeccable no browser não injectado (scan estático limpo).

## 6. Veredito

**PASS** — zero P0/P1 abertos; detector `[]`; digest idêntico disco/HTTPS/esperado; clone+delta (não ANTES/DEPOIS); `/login` não usado como prova da rota; matriz visível nos dois viewports. HTTP 200 sozinho não sustentaria este veredito.

Disposition: crítico não pede rework. P3 aceites no Apply.

## 7. Referências

- Proto URL: https://dev.criptofarol.com.br/prototypes/card-969-discovery-selo-go-nogo/
- Digest: `04967d7546f8d67a1d2e6a8db246faeefb5e1c3ab5283e5d61eb58c8305d47fe`
- Snapshot: `.impeccable/critique/969-card-969-discovery-selo-go-nogo-assessment-B.md`
- Gate: `.impeccable/critique/969-B-gate.json`
- PNGs: `969-B-desktop-1440x900.png`, `969-B-desktop-montar.png`, `969-B-desktop-acompanhar.png`, `969-B-desktop-decidir-nogo.png`, `969-B-desktop-decidir-agld.png`, `969-B-desktop-decidir-doge.png`, `969-B-desktop-decidir-ada.png`, `969-B-desktop-acompanhar-nogo.png`, `969-B-desktop-live-combo-discovery.png`, `969-B-mobile-390x844.png`, `969-B-mobile-montar.png`, `969-B-mobile-montar-preflight.png`, `969-B-mobile-preflight-card.png`, `969-B-mobile-acompanhar.png`, `969-B-mobile-acompanhar-nogo.png`, `969-B-mobile-decidir-btc.png`, `969-B-mobile-decidir-agld.png`, `969-B-mobile-decidir-doge.png`, `969-B-mobile-decidir-ada.png`
