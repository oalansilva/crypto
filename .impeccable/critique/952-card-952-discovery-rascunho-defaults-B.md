# Assessment B (detector + browser real) — card 952 · change card-952-discovery-rascunho-defaults

> Assessor B isolado, mesmo modelo, sem transcript de A nem do pai. Sem nested-spawn.
> Nada movido (Status, branch, worktree); nenhuma edição fora deste ficheiro, PNGs `952-B-*` e `952-B-gate.json`.
> Tokens parseáveis do `design.md` (rubrica D4): `UI impact: affected` · `live_route: /combo/discovery` · `surface: existing`.

```
Assessment B 952
digest_match: yes
detector: 1 advisory (em-dash-overuse) → P3
P0: nenhum
P1: nenhum
P3: em-dash copy viva; Novo rascunho no header do gate; tabs Acompanhar/Decidir disabled no mock; Preflight abaixo da dobra 390; pf-meta Período estático; seg 4h/1d input 0×0
verdict: PASS
```

- UTC: 2026-09-16T18:23Z
- Tuple (read-only): `bound_card=952` · `q_git=card-952-discovery-rascunho-defaults` · Status GraphQL pontual `Design` (Project 1 / `oalansilva`). Sem `process_event`.
- Protótipo: `frontend/public/prototypes/card-952-discovery-rascunho-defaults/index.html`
- Servido: https://dev.criptofarol.com.br/prototypes/card-952-discovery-rascunho-defaults/
- Digest esperado: `eab36595d3bc5548703d2bd826849f8579d86ede884d39df418580510c0e52c5` · 32337 bytes
- Rota viva: https://dev.criptofarol.com.br/combo/discovery — **não usada como prova**. GET devolve o shell Vite (`<title>frontend</title>`), 455 bytes, HTTP 200, **não** `/login`. `/login` **não** conta. Clone avaliado só no proto HTTPS + landmarks do catálogo.
- Irmão `restore.html`: evidência de restore sem overlay; **nunca** URL canónica (T5 mede só `index.html`).
- Browser: Playwright Python + Chromium 1243 (`chrome-linux-arm64`) sob `xvfb-run -a`, `--no-sandbox`. Viewports 1440×900 e 390×844. `colorScheme: dark`. URL canónica do proto (não `file://`, não `/login`).
- Detector: `node .agents/skills/impeccable/scripts/detect.mjs --json` no HTML versionado (cwd worktree).
- Q1/Q2 aceites: **não reabertos** (defaults só rascunho novo; restore traz gravado; Direção/período/ranking fora).

## 1. Digest servido == local

| Ponta | sha256 | bytes |
|---|---|---|
| Disco | `eab36595d3bc5548703d2bd826849f8579d86ede884d39df418580510c0e52c5` | 32337 |
| HTTPS GET `/prototypes/card-952-discovery-rascunho-defaults/` | `eab36595d3bc5548703d2bd826849f8579d86ede884d39df418580510c0e52c5` | 32337 HTTP 200 |
| HTTPS GET `…/index.html` | `eab36595d3bc5548703d2bd826849f8579d86ede884d39df418580510c0e52c5` | 32337 |
| Esperado (prompt / `design.md`) | `eab36595d3bc5548703d2bd826849f8579d86ede884d39df418580510c0e52c5` | 32337 |

`cmp` disco vs `/tmp/952-B-https-dir.html` e vs `…/index.html`: **IDENTICAL**. HTTP 200 isolado **não** é o gate.

## 2. Detector Impeccable

- Alvo: `frontend/public/prototypes/card-952-discovery-rascunho-defaults/index.html`
- Comando: `node .agents/skills/impeccable/scripts/detect.mjs --json` → 1 finding, exit 0.
- `em-dash-overuse` (advisory, category slop): 8 em-dashes no body (`Iniciar varredura —`, `Bloqueado — veja o que falta`, placeholders `—`). Copy do chrome vivo, não delta deste card → **P3**, não P0/P1.

## 3. Clone / fidelidade (superfície existing)

- Tokens D4 no `design.md`: `UI impact: affected`, `live_route: /combo/discovery` (não catálogo emprestado), `surface: existing`. Regiões clonadas marcadas.
- Catálogo `scripts/process-fsm/route-landmarks.yaml` `/combo/discovery`: `Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`.
- Proto canónico: **6/6** pares `COPIED:start` / `COPIED:end` (shell AppNav, modo Montar heading+tabs, cartão Templates, cartão Símbolos, cartão Time Frames, painel Preflight «Falta fazer»). Soma UTF-8 do interior exclusivo = **9498 > 0** (bloco com linha de abertura do comentário ≈ 9869). **0** `DELTA:start` — o delta é estado (0 templates, 0 símbolos, só 1 dia, 4 horas desmarcado, aviso visível, início bloqueado), não markup novo.
- Toggle Antes/Depois: **ausente**. Botões «Antes»/«Depois» = **0**. Comentário «sem painel ANTES/DEPOIS» não é painel. Default = **Montar** (`aria-selected=true`). URL canónica = `index.html` clone+delta de defaults. `restore.html` = irmão, nunca canónica.
- Layout das três opções (Templates / Símbolos / Timeframes swing) intacto; Direção Long, período Todo o histórico, ranking Calmar no estado default — iguais ao chrome vivo, fora do card.

## 4. Browser real — matriz (desktop 1440×900 e mobile 390×844)

Console error = 0; warning = 0; pageerror = 0; responses ≥400 = 0. Overflow documento `scrollWidth==clientWidth` (1425/1425 e 375/375). Gate bruto: `.impeccable/critique/952-B-gate.json` (49/49 ×2).

| # | Assert | Desktop | Mobile |
|---|---|---|---|
| 1 | Digest disco == HTTPS (não basta HTTP 200) | PASS | PASS |
| 2 | Landmark h1 `Descoberta de estratégias swing` visível | PASS | PASS |
| 3 | Landmark `Preflight` visível | PASS | PASS (abaixo da dobra; full-page) |
| 4 | Landmark `Rascunho de varredura` visível | PASS | PASS |
| 5 | Default Montar; 0 templates / 0 símbolos / 0 chips | PASS | PASS |
| 6 | Só **1 dia** marcado; **4 horas** desmarcado | PASS | PASS |
| 7 | «Falta fazer» visível; início `disabled` | PASS | PASS |
| 8 | 4 horas marcável (1 dia permanece) | PASS | PASS |
| 9 | 1 template + 1 símbolo: aviso some, início habilita | PASS | PASS |
| 10 | «Novo rascunho» volta a 0/0 / só 1 dia / aviso / início bloqueado | PASS | PASS |
| 11 | Novo rascunho **não** reseta Direção/período/ranking (período 2y mantido no ensaio) | PASS | PASS |
| 12 | Irmão restore: 3 tpl / 4 sym / 4h+1d; sem overlay dos defaults novos | PASS | PASS |
| 13 | Zero botões Antes/Depois; URL canónica ≠ restore.html | PASS | PASS |
| 14 | 0 console de impacto / 0 pageerror / 0 ≥400 | PASS | PASS |
| 15 | COPIED 6/6, UTF-8 soma > 0 | PASS | PASS |

Pixels desktop default: 1 dia ouro `rgb(252, 213, 53)`; 4 horas mudo `rgb(146, 154, 165)`; Templates/Símbolos `0 de 8`; Preflight «Falta fazer» y≈505 (dentro de 900); CTA desactivado. Após marcar 4 horas: ambos os segmentos ouro. Ready: 1+1 seleccionado, 2 combinações, CTA amarelo. Novo rascunho: eixos vazios, só 1 dia, aviso de volta; select período ficou «Últimos 2 anos» (fora do card). Restore irmão: 3 de 8 / 4 de 8, chips, 4h+1d, 24 combinações, CTA «Iniciar varredura — 24, —», aviso escondido.

Pixels mobile: mesma verdade de estado; Preflight y≈2052 (abaixo da dobra — clone do Montar com listas inline). 4 horas e 1 dia cabem no par de segmentos. Overflow horizontal 0.

Rota viva **não usada** como prova. Browser correu no proto canónico; restore só como irmão.

## 5. Findings (toda finding classificada)

### P0 — nenhum

Landmarks 3/3 no proto; digest servido == local == esperado; sem painel ANTES/DEPOIS canónico; 6 pares COPIED (UTF-8 9498) + delta de estado; rascunho novo 0/0 / só 1 dia; «Falta fazer» + início bloqueado; 4 horas marcável; «Novo rascunho» restaura defaults dos eixos; restore irmão traz 3+4+4h+1d sem overlay; Direção/período/ranking fora (não reabrir Q1/Q2); `/login` não usado. Fidelidade ok → não BLOCKED.

### P1 — nenhum

Contrato visível confirmado nos dois viewports. Detector advisory classificado P3. Layout das três opções não redesenhado. `live_route` é `/combo/discovery`.

### P3 — aceites (Apply / clone chrome; não reabrir como P0/P1)

- **P3-1 Detector `em-dash-overuse` (advisory).** 8 travessões no chrome (`Iniciar varredura —`, `Bloqueado — veja o que falta`, placeholders). Copy viva; Apply não precisa reescrever neste card.
- **P3-2 «Novo rascunho» no header do rascunho.** O proto expõe o controlo no Montar para o gate; Apply mantém o sítio vivo (Acompanhar / rascunho colapsado) — já aceite no `design.md`.
- **P3-3 Tabs Acompanhar / Decidir `disabled`.** Mock de rascunho novo sem varredura a correr; chrome de modos, sem delta deste card.
- **P3-4 Preflight abaixo da dobra em 390×844.** «Falta fazer» y≈2052; no desktop sticky y≈505. Clone do layout Montar (listas inline). Contrato («visível», não escondido) cumpre-se; Apply não redesenha as três opções.
- **P3-5 Linha estática Preflight «Período: Todo o histórico».** Não segue o select (mock). Período está fora do card; a linha de 3 combinações *sim* actualiza.
- **P3-6 Segmentos 4h/1d com input `opacity:0` 0×0.** Padrão visual clonado; o `label` envolve o controlo; clique no span marca. Apply herda o widget vivo.
- **P3-7 Chips truncados** (`Médias Móveis: Tendênc…`) no restore — `ellipsis` do chrome, não delta.

Observações (não-findings): heading «Compare templates em 4h e 1d» é chrome clonado, não contradiz o default só-1-dia. Overlay `detect.js` não injectado — evidência = CLI + Playwright no proto servido. Motor URL do detector não invocado.

## 6. Veredito

**PASS** — zero P0/P1 abertos; detector advisory classificado P3; digest idêntico; clone+delta de defaults (não ANTES/DEPOIS); `/login` não usado como prova da rota; matriz visível nos dois viewports; restore irmão sem overlay. HTTP 200 sozinho não sustentaria este veredito.

Disposition: crítico não pede rework. P3 aceites no Apply.

## 7. Referências

- Proto URL: https://dev.criptofarol.com.br/prototypes/card-952-discovery-rascunho-defaults/
- Digest: `eab36595d3bc5548703d2bd826849f8579d86ede884d39df418580510c0e52c5`
- Snapshot: `.impeccable/critique/952-card-952-discovery-rascunho-defaults-B.md`
- Gate bruto: `.impeccable/critique/952-B-gate.json`
- PNGs: `.impeccable/critique/952-B-desktop-default.png`, `952-B-desktop-4h.png`, `952-B-desktop-ready.png`, `952-B-desktop-novo-rascunho.png`, `952-B-desktop-restore-sibling.png`, `952-B-mobile-default.png`, `952-B-mobile-4h.png`, `952-B-mobile-ready.png`, `952-B-mobile-novo-rascunho.png`, `952-B-mobile-restore-sibling.png`
- proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)
