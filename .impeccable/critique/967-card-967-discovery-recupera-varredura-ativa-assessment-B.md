# Assessment B (detector + browser real) — card 967 · change card-967-discovery-recupera-varredura-ativa

> Assessor B isolado, mesmo modelo, sem transcript de A nem do pai. Sem nested-spawn.
> Nada movido (Status, branch, worktree); nenhuma edição fora deste ficheiro, PNGs `967-B-*` e `967-B-gate.json`.
> Tokens parseáveis do `design.md` (rubrica D4, não reabrir parser): `UI impact: affected` · `live_route: /combo/discovery` · `surface: existing`.

```
Assessment B 967
digest_match: yes
detector: [] (index + retry, exit 0)
P0: nenhum
P1: nenhum
P3: overflow 390 na grelha/chip EM CURSO; banner azul pedagógico; DELTA:end em falta no 2.º bloco; retry.html irmão
verdict: PASS
```

- UTC: 2026-09-17T12:48Z
- Tuple (read-only): `bound_card=967` · `q_git=card-967-discovery-recupera-varredura-ativa` · Status GraphQL pontual `Design` (Project 1 / `oalansilva`, item `PVTI_lAHOAAHtBM4BV8b2zg7adKU`). Sem `process_event`. GraphQL remaining=4708.
- Protótipo canónico: `frontend/public/prototypes/card-967-discovery-recupera-varredura-ativa/index.html`
- Servido: https://dev.criptofarol.com.br/prototypes/card-967-discovery-recupera-varredura-ativa/
- Digest esperado: `9e0447c6f03907bc7c57c5a0045a62ed89f5cb135015c0ff7297dc3ae213e997` · 42186 bytes
- Irmão `retry.html`: residual (banner vermelho + «Tentar novamente» + «Acompanhando #—»); **nunca** URL canónica (T5 mede só `index.html`).
- Rota viva: https://dev.criptofarol.com.br/combo/discovery — GET HTTP 200, 455 bytes, título `frontend` (shell Vite), **não** `/login`. `/login` **não** conta. **Não usada como prova de clone.** Clone avaliado só no proto HTTPS + landmarks do catálogo.
- Browser: Playwright Python + Chromium 1243 (`chrome-linux-arm64`) sob `xvfb-run -a`, `--no-sandbox`. Viewports 1440×900 e 390×844. `colorScheme: dark`. URL canónica do proto (não `file://`, não `/login`).
- Detector: `node .agents/skills/impeccable/scripts/detect.mjs --json` no HTML versionado (cwd worktree). `ignore.md` ausente.

## 1. Digest servido == local

| Ponta | sha256 | bytes |
|---|---|---|
| Disco `index.html` | `9e0447c6f03907bc7c57c5a0045a62ed89f5cb135015c0ff7297dc3ae213e997` | 42186 |
| HTTPS GET `/prototypes/card-967-discovery-recupera-varredura-ativa/` | idem | 42186 HTTP 200 |
| HTTPS GET `…/index.html` | idem | 42186 |
| Esperado (prompt / `design.md`) | `9e0447c6f03907bc7c57c5a0045a62ed89f5cb135015c0ff7297dc3ae213e997` | 42186 |
| Disco `retry.html` | `3a12b0c3028bc39354f7eb660fd7984c58b4c4cb0d1617873f19ab64d57ba21d` | 41678 · cmp HTTPS **IDENTICAL** |

`cmp` disco vs HTTPS nas pontas canónicas: **IDENTICAL**. HTTP 200 isolado **não** é o gate.

## 2. Detector Impeccable

- Alvos: `index.html` e `retry.html`.
- Comando: `node .agents/skills/impeccable/scripts/detect.mjs --json` → `[]`, exit 0 nos dois.
- Sem finding crítico. Sem P0 de detector.

## 3. Clone / fidelidade (superfície existing)

- Tokens D4 no `design.md` (linhas próprias): `UI impact: affected`, `live_route: /combo/discovery` (não catálogo emprestado), `surface: existing`. Regiões clonadas marcadas.
- Catálogo `scripts/process-fsm/route-landmarks.yaml` `/combo/discovery`: `Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`.
- Proto canónico: **11/11** pares `COPIED:start` / `COPIED:end`. Soma UTF-8 do interior exclusivo = **14378 > 0**. `DELTA:start`=2 / `DELTA:end`=1 (2.º bloco sem fecho — P3). T5 mede só `index.html`.
- Toggle Antes/Depois: **ausente**. Botões «Antes»/«Depois» = **0**. Comentário «sem painel ANTES/DEPOIS» não é painel. Default = **Acompanhar** (`aria-selected=true` em `#tab-acomp`). URL canónica = `index.html` clone+delta. `retry.html` = irmão, nunca canónica.
- `lang=pt-BR`.

## 4. Browser real — matriz (desktop 1440×900 e mobile 390×844)

Console error = 0; warning = 0; pageerror = 0; responses ≥400 no proto = 0. Gate bruto: `.impeccable/critique/967-B-gate.json` (32 asserts ×2). Overflow documento: desktop `1440==1440`; mobile Acompanhar `scrollWidth=468` vs `clientWidth=390` (P3 clone da grelha/chip — **não** assert bloqueante). PNG mobile-acomp = 468×1869 (full-page expandiu à overflow).

| # | Assert | Desktop | Mobile |
|---|---|---|---|
| 1 | Digest disco == HTTPS (não basta HTTP 200) | PASS | PASS |
| 2 | Tokens `UI impact: affected` / `live_route: /combo/discovery` / `surface: existing` | PASS | — |
| 3 | Landmark h1 `Descoberta de estratégias swing` visível | PASS | PASS |
| 4 | Landmark `Preflight` visível após Montar (hidden no default Acompanhar) | PASS | PASS |
| 5 | Landmark `Rascunho de varredura` visível após Montar | PASS | PASS |
| 6 | Default Acompanhar; tab `Acompanhando #c91f3a07` (não «#—») | PASS | PASS |
| 7 | Progresso `12 de 24` visível + chip `EM CURSO` + `role=progressbar` | PASS | PASS |
| 8 | Banner «Não foi possível verificar a varredura ativa» **ausente** | PASS | PASS |
| 9 | Zero botões Antes/Depois; URL canónica ≠ retry.html | PASS | PASS |
| 10 | Iniciar outra `disabled` no Montar | PASS | PASS |
| 11 | Voltar a Acompanhar mantém número + progresso | PASS | PASS |
| 12 | 0 console error / 0 pageerror / 0 ≥400 no proto | PASS | PASS |
| 13 | COPIED 11/11, UTF-8 soma > 0 | PASS | PASS |
| 14 | Irmão retry: banner vermelho + `#—` + «Tentar novamente»; nunca canónico | PASS | PASS |

Pixels desktop Acompanhar: tab ouro `Acompanhando #c91f3a07`; heading `Sweep ativo · #c91f3a07b6e24d8a9f51c2e8470b3d16`; chip `EM CURSO`; `12 de 24`; barra; banner azul «Varredura ativa recuperada do servidor» (não o vermelho); Histórico = outra run. Montar: `Rascunho de varredura` CONGELADO 3/14 · 4/688; Preflight 24; CTA `Iniciar varredura — 24, ~48 min` desactivado. Decidir: «Histórico · outra run», tab Acompanhar ainda com `#c91f3a07`.

Pixels mobile: mesma verdade de estado; Preflight/Rascunho abaixo da dobra após Montar. Chip `EM CURSO` e thead da grelha empurram `scrollWidth` a 468 (P3).

Rota viva **não usada como prova**. Browser do clone correu no proto canónico; retry só como irmão. GET `/combo/discovery` = shell Vite (`<title>frontend</title>`), não autenticação `/login`.

## 5. Findings (toda finding classificada)

### P0 — nenhum

Landmarks 3/3 no fluxo (heading no default; Preflight + Rascunho após Montar); digest servido == local == esperado; sem painel ANTES/DEPOIS canónico; 11 pares COPIED (UTF-8 14378) + delta de Acompanhar reconstituído; número verdadeiro `#c91f3a07` + `12 de 24`; banner vermelho ausente no index; 0 console/pageerror; detector limpo; `/login` não usado. Fidelidade + contrato visível ok → não BLOCKED.

### P1 — nenhum

Contrato visível confirmado nos dois viewports. Detector vazio. `live_route` é `/combo/discovery`. Overflow mobile não impede ver número, progresso nem landmarks.

### P3 — aceites (Apply / clone chrome; não reabrir como P0/P1)

- **P3-1 Overflow horizontal no 390 no Acompanhar.** `scrollWidth=468`. Ofensores: `table.lb` thead/tr ~645px (casca da grelha clonada; `table-wrap` `overflow:visible` no breakpoint) e chip `EM CURSO` `right≈468`. Clone do chrome Acompanhar com UUID real; Apply herda o widget vivo. Montar cai a 399.
- **P3-2 Banner azul «Varredura ativa recuperada do servidor».** Não é o vermelho do contrato. Copy pedagógica do proto; Apply pode omitir se o Acompanhar hidratado já for o estado.
- **P3-3 `DELTA:end` em falta** no 2.º bloco (`DELTA:start` reconstituição). Comentário de marcação; T5 conta COPIED, não DELTA. Apply não precisa do comentário.
- **P3-4 Irmão `retry.html`.** Residual correcto (vermelho + «Tentar novamente» + «#—» + Montar vazio); extra URL da mesma rota, nunca canónico.
- **P3-5 Select de Histórico truncado no 390** (`…coi`). Chrome clonado do selector.
- **P3-6 Intervalo/backoff/teto das tentativas automáticas** e se o loading «Verificando…» permanece entre retries — já P3 no `design.md`; proto feliz não anima o retry.

Observações (não-findings): overlay `detect.js` não injectado — evidência = CLI + Playwright no proto servido. Motor URL do detector não invocado. Soma UTF-8 medida 14378 (autor citou 14367); diferença de fronteira de comentário, ambas > 0.

## 6. Veredito

**PASS** — zero P0/P1 abertos; detector limpo; digest idêntico; clone+delta (não ANTES/DEPOIS); `/login` não usado como prova da rota; matriz visível nos dois viewports; banner vermelho só no irmão residual. HTTP 200 sozinho não sustentaria este veredito.

Disposition: crítico não pede rework. P3 aceites no Apply.

## 7. Referências

- Proto URL: https://dev.criptofarol.com.br/prototypes/card-967-discovery-recupera-varredura-ativa/
- Digest: `9e0447c6f03907bc7c57c5a0045a62ed89f5cb135015c0ff7297dc3ae213e997`
- Snapshot: `.impeccable/critique/967-card-967-discovery-recupera-varredura-ativa-assessment-B.md`
- Gate bruto: `.impeccable/critique/967-B-gate.json`
- PNGs: `967-B-desktop-acomp.png`, `967-B-desktop-montar.png`, `967-B-desktop-decidir.png`, `967-B-desktop-retry-sibling.png`, `967-B-mobile-acomp.png`, `967-B-mobile-montar.png`, `967-B-mobile-decidir.png`, `967-B-mobile-retry-sibling.png`
- proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)
