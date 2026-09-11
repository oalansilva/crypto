# Assessment B (detector + browser real) — card 896 · change card-896-discovery-calmar-nogo

> Assessor B isolado, mesmo modelo, sem transcript de A nem do pai. Sem nested-spawn.
> Nada movido (Status, branch, worktree); nenhuma edição fora deste ficheiro e PNGs `896-B-*`.
> Tokens parseáveis do `design.md` (rubrica D4): `UI impact: affected` · `live_route: /combo/discovery` · `surface: existing`.

```
Assessment B 896
digest_match: yes
detector: 0 findings
P0: nenhum
P1: nenhum
P3: chip GO/NO-GO full-width (desktop block + mobile wrap); Montar condensado; Decidir sem filtros/modais; Promover outline vs fill; mock 16/16 vs 5 linhas; #PF-896-24 chrome copiado; oos_verdict top-level vs nested
verdict: PASS
```

- UTC: 2026-09-11T17:54Z
- Tuple (read-only): `q=Design` · `bound_card=896` · `q_git=card-896-discovery-calmar-nogo` (`scripts/process-fsm/resolve.py` + board Status; `.grok/rules/process-fsm-page.md` ausente). Sem `process_event`.
- Protótipo: `frontend/public/prototypes/card-896-discovery-calmar-nogo/index.html`
- Servido: https://dev.criptofarol.com.br/prototypes/card-896-discovery-calmar-nogo/
- Digest esperado: `19c07a26d8c479ab5a56482759f58a0683a209f9aeb674cf2ced525b6f3e5a08` · 37328 bytes
- Rota viva: https://dev.criptofarol.com.br/combo/discovery — **sem sessão**; Playwright aterrissou em `/login` (`Bem-vindo de volta` / campo senha). `/login` **não** conta como a rota; clone avaliado pelo proto + landmarks do catálogo + fonte `DiscoveryPage.tsx`.
- Browser: `playwright-cli` 0.1.19 headed sob `xvfb-run -a` (`PLAYWRIGHT_MCP_SANDBOX=false`, `PLAYWRIGHT_MCP_EXECUTABLE_PATH` Chromium 1243 arm64 / Chrome for Testing 153). Wrapper `playwright-cli-headed` / `/usr/local/bin/playwright-cli-headed` **ausentes**. Um `run-code` por viewport (`goto` + asserts + `screenshot` na mesma sessão).
- Detector: `node .agents/skills/impeccable/scripts/detect.mjs --json` no HTML versionado.

## 1. Digest servido == local

| Ponta | sha256 | bytes |
|---|---|---|
| Disco | `19c07a26d8c479ab5a56482759f58a0683a209f9aeb674cf2ced525b6f3e5a08` | 37328 |
| HTTPS GET `/prototypes/card-896-discovery-calmar-nogo/` | `19c07a26d8c479ab5a56482759f58a0683a209f9aeb674cf2ced525b6f3e5a08` | 37328 HTTP 200 |
| HTTPS GET `…/index.html` | `19c07a26d8c479ab5a56482759f58a0683a209f9aeb674cf2ced525b6f3e5a08` | 37328 |
| Esperado (prompt / `design.md`) | `19c07a26d8c479ab5a56482759f58a0683a209f9aeb674cf2ced525b6f3e5a08` | 37328 |

`cmp` disco vs `/tmp/896-B-https.html`: **IDENTICAL**. HTTP 200 isolado **não** é o gate.

## 2. Detector Impeccable

- Alvo: `frontend/public/prototypes/card-896-discovery-calmar-nogo/index.html`
- Comando: `node .agents/skills/impeccable/scripts/detect.mjs --json` → `[]`, exit 0.
- **0 findings determinísticos.** Nada por classificar → sem bloqueio deste item.

## 3. Clone / fidelidade (superfície existing)

- Catálogo `scripts/process-fsm/route-landmarks.yaml` `/combo/discovery`: `Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`.
- Fonte viva `DiscoveryPage.tsx`: h1 `Descoberta de estratégias swing` (L1326); h2 `Rascunho de varredura` (L1768); aside `aria-label="Preflight da varredura"` + h2 `Preflight` (L1925/1928).
- Proto `index.html`: **8 pares** `COPIED:start` / `COPIED:end` (shell AppNav, heading, modos, rascunho, preflight, chrome Acompanhar, header leaderboard, nota rank-stable).
- Toggle Antes/Depois: **ausente**. `aria-pressed` = 0; botões «Antes»/«Depois» = 0. Comentário HTML: `No ANTES/DEPOIS panel` (não é painel). Tabs `role=tab` mudam markup (`.modepanel.active` único). URL canónica = `index.html` clone+delta.

## 4. Browser real — matriz (desktop 1440×900 e mobile 390×844)

Console error = 0; pageerror = 0; responses ≥400 = 0 (logo `/brand/cripto-farol-logo-v6-transparent.svg` = 200). Overflow desktop `scrollWidth==clientWidth==1440`. Mobile `sw==cw==375` (viewport interno; sem overflow horizontal).

| # | Assert | Desktop | Mobile |
|---|---|---|---|
| 1 | Digest disco == HTTPS (não basta HTTP 200) | PASS | PASS |
| 2 | Landmark h1 `Descoberta de estratégias swing` | PASS | PASS |
| 3 | Landmark `Preflight` visível após tab Montar | PASS | PASS |
| 4 | Landmark `Rascunho de varredura` visível após tab Montar | PASS | PASS |
| 5 | GO 1º Calmar exact `1,20` + selo `GO` | PASS | PASS |
| 6 | ALPHA NO-GO selo + Calmar `22,00` (não `1e27` / 27 dígitos) | PASS | PASS |
| 7 | Célula absurda `N/A` | PASS | PASS |
| 8 | Todo GO acima de todo NO-GO (parciais `GO,GO,GO,NO-GO,NO-GO`; Decidir `GO,GO,NO-GO,NO-GO`, vizinha `Baixa amostra` sem veredito) | PASS | PASS |
| 9 | Selo visível sem canvas/dialog/gráfico (mobile: bbox no viewport após scroll da linha) | PASS | PASS |
| 10 | `30 · 100%` + `aria-label` `negócios / cobertura` (e Calmar CAGR÷Max DD) | PASS | PASS |
| 11 | Promover enabled no NO-GO elegível (`disabled=false`) | PASS | PASS |
| 12 | Sem painel ANTES/DEPOIS; 3 modos, não grelha | PASS | PASS |
| 13 | 0 console error / 0 pageerror / 0 ≥400 | PASS | PASS |

Rota viva sem sessão: `final_url=https://dev.criptofarol.com.br/login`, h1 `Bem-vindo de volta`. **Não usada como evidência de clone.**

Pixels desktop Acompanhar: ranks 1–3 GO (`1,20` / `0,94` / `0,81`); rank 4 ALPHA `NO-GO` `22,00` `30 · 100%`; rank 5 `N/A`. Hints `CAGR ÷ Max DD` / `negócios · velas`. Decidir: Promover no ALPHA NO-GO; copy «Calmar não é retorno… não é taxa de acerto»; vizinha `Baixa amostra` intacta (âmbar, Promover disabled).

Pixels mobile: selo `NO-GO` na linha ALPHA com `22,00` e `30 · 100%`; N/A no 5º; Promover enabled no card NO-GO. Chip ocupa a largura do card (P3).

Q1 aceite — grelha não reaberta.

## 5. Findings (toda finding classificada)

### P0 — nenhum

Landmarks 3/3 no proto (e na fonte viva); digest servido == local == esperado; sem painel ANTES/DEPOIS canónico; 8 pares COPIED; GO-first + Calmar honesto/`N/A` + selo na linha; Promover no NO-GO elegível permanece.

### P1 — nenhum

Delta observável nos dois viewports. Detector `[]`. HTML sem toggle `aria-pressed` morto. Selo tem texto `GO`/`NO-GO` (não só cor).

### P3 — aceites (Apply / clone chrome; não reabrir como P0/P1)

- **P3-1 Chip GO/NO-GO full-width.** Desktop: `.candidate span{display:block}` estica o selo na coluna Candidato. Mobile ≤720px: wrap `flex: 1 0 100%` (bbox ~277×26 em 390). Selo legível; Apply pode encolher o chip.
- **P3-2 Montar condensado** vs `DiscoveryPage.tsx` viva (eixos resumidos). Landmarks presentes; sem delta deste card.
- **P3-3 Decidir sem filtros/modais** do vivo. Condensação de proto.
- **P3-4 Promover outline** vs fill `DESIGN.md`. Clone chrome; CTA funcional e enabled no NO-GO.
- **P3-5 Leaderboard `16 de 16 candidatos` com 5 `<tr>`.** Mock; Apply liga à paginação real.
- **P3-6 `#PF-896-24` / `#c896nogo`** no chrome copiado. Apply não precisa dos ids fictícios.
- **P3-7 `oos_verdict` top-level vs nested `metrics`.** Detalhe de Apply (já no design.md).

Observações (não-findings): selo abaixo da dobra no desktop 900 px sem scroll — visível na linha, sem gráfico; harness `seal_nogo_in_viewport` falhou só antes de scroll, não é falha de produto. Overflow mobile interno 375 (scrollbar/janela headed); `sw==cw`. Motor URL do detector não invocado (scan estático `[]` cobre o HTML versionado).

## 6. Veredito

**PASS** — zero P0/P1 abertos; detector `[]`; digest idêntico; clone+delta (não ANTES/DEPOIS); `/login` não usado como prova da rota; matriz visível nos dois viewports. HTTP 200 sozinho não sustentaria este veredito.

Disposition: crítico não pede rework. P3 aceites no Apply. Q1 não reaberta.

## 7. Referências

- Proto URL: https://dev.criptofarol.com.br/prototypes/card-896-discovery-calmar-nogo/
- Digest: `19c07a26d8c479ab5a56482759f58a0683a209f9aeb674cf2ced525b6f3e5a08`
- Snapshot: `.impeccable/critique/896-card-896-discovery-calmar-nogo-assessment-B.md`
- PNGs: `.impeccable/critique/896-B-desktop-1440x900.png`, `896-B-desktop-montar.png`, `896-B-desktop-decidir.png`, `896-B-desktop-login.png`, `896-B-mobile-390x844.png`, `896-B-mobile-montar.png`, `896-B-mobile-decidir.png`, `896-B-mobile-acomp-full.png`
