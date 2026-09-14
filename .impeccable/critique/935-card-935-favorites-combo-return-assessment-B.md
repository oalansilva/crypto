# Assessment B (detector + browser real) — card 935 · change card-935-favorites-combo-return

> Assessor B isolado, mesmo modelo, sem transcript de A nem do pai. Sem nested-spawn.
> Nada movido (Status, branch, worktree); nenhuma edição fora deste ficheiro, PNGs `935-B-*` e `935-B-gate.json`.
> Tokens parseáveis do `design.md` (rubrica D4): `UI impact: affected` · `live_route: /favorites` · `surface: existing`.

proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)

```
Assessment B 935
digest_match: yes
detector: index 2 warning side-tab (P3 clone); analise 0
P0: nenhum
P1: nenhum
P3: side-tab cards mobile; truncagem «Médias Móveis…»; 32 vs 33 lista; alvos 32px ícones; ETH Analisar morto no extra; 16.951 só no spec
verdict: PASS
```

- UTC: 2026-09-14T01:35Z
- Tuple (read-only): `bound_card=935` · `q_git=card-935-favorites-combo-return`. Sem `process_event`.
- Protótipo canónico: `frontend/public/prototypes/card-935-favorites-combo-return/index.html`
- Extra: `…/analise.html` (`/combo/results`)
- Servido: https://dev.criptofarol.com.br/prototypes/card-935-favorites-combo-return/ · extra `…/analise.html`
- Digest esperado (`design.md`): index `2f2bb0a5a3c4ce5ee92b8ecbabf148d0732d7dcd40d87a5fef0ff217cc3cea39` · 42089 B; analise `1bc0942794179d646f9a610d7f7cef85d85e1ffdb35485f378e77635cbb08d5c` · 26812 B
- Rota viva: https://dev.criptofarol.com.br/favorites — **não usada como prova**. GET devolve o shell Vite (`<title>frontend</title>`), não a grade. `/login` **não** conta. Clone avaliado no proto HTTPS + landmarks do catálogo.
- Browser: Playwright Python + Chromium (`/usr/bin/chromium-browser`) headed sob `xvfb-run -a`, `--no-sandbox`. Viewports **1280×800** e **390×844**, `colorScheme: dark`. URL canónica do proto (não `file://`).
- Detector: `node .agents/skills/impeccable/scripts/detect.mjs --json` no HTML versionado (cwd worktree). Overlay `detect.js` **não** injectado — evidência = CLI + Playwright no proto servido.

## 1. Digest servido == local

| Ponta | sha256 | bytes |
|---|---|---|
| Disco `index.html` | `2f2bb0a5a3c4ce5ee92b8ecbabf148d0732d7dcd40d87a5fef0ff217cc3cea39` | 42089 |
| HTTPS GET `/prototypes/card-935-favorites-combo-return/` | `2f2bb0a5a3c4ce5ee92b8ecbabf148d0732d7dcd40d87a5fef0ff217cc3cea39` | 42089 HTTP/2 200 |
| HTTPS GET `…/index.html` | `2f2bb0a5a3c4ce5ee92b8ecbabf148d0732d7dcd40d87a5fef0ff217cc3cea39` | 42089 |
| Disco `analise.html` | `1bc0942794179d646f9a610d7f7cef85d85e1ffdb35485f378e77635cbb08d5c` | 26812 |
| HTTPS GET `…/analise.html` | `1bc0942794179d646f9a610d7f7cef85d85e1ffdb35485f378e77635cbb08d5c` | 26812 HTTP/2 200 |
| Esperado (`design.md`) | idêntico aos dois hashes | 42089 / 26812 |

`copied_utf8_sum(index)=7661` (4/4 pares COPIED) · `copied_utf8_sum(analise)=4981` (5/5 pares). HTTP 200 isolado **não** é o gate.

## 2. Detector Impeccable

- Alvo index: 2 findings `side-tab` (warning, slop) linhas 143–144 — `border-left:3px` nos cards mobile `.tier-top` / `.tier-watch`. Incumbente do clone #897 / vivo. **P3**, não produto deste card.
- Alvo analise: `[]`, exit 0.
- Classificado → sem bloqueio.

## 3. Tokens + clone / fidelidade (superfície existing)

Rubrica D4 — tokens em **linha própria** em `openspec/changes/card-935-favorites-combo-return/design.md`:

```
UI impact: affected
live_route: /favorites
surface: existing
```

Não é rota de catálogo emprestada. Extra `/combo/results` está em `analise.html`, **não** no `index.html` canónico.

Catálogo `scripts/process-fsm/route-landmarks.yaml`:

- `/favorites`: `selectors: ["table.fav-strategies"]`, `texts: ["Estratégias favoritas", "Symbol", "Estratégia", "Ações"]` — **presentes** no index (thead `textContent`; h1 visível). Thead com `text-transform:uppercase` (AÇÕES) é chrome vivo, não painel.
- `/combo/results` (extra): `selectors: [".combo-page"]`, `texts: ["Lista de operações", "Análise da estratégia"]` — **presentes** em analise.html (`.combo-page`; `aria-label` + topbar + h2 da lista).

Clone: 4 pares `COPIED:start`/`COPIED:end` no index (shell AppNav, heading, `table.fav-strategies` thead, footer). Delta = linhas SOL / ETH (fora dos blocos COPIED do chrome). Extra: 5 pares COPIED (shell, chrome resumo, gráfico, lista thead, disclaimer).

Toggle Antes/Depois: **ausente**. Botões «Antes»/«Depois» = 0. Comentário HTML «No ANTES/DEPOIS» não é painel. URL canónica = clone+delta.

Escopo **não** furado no proto visível: sem Holdout / Treino vs Holdout; Monitor só no AppNav clonado; lista **33 negócios** deixada visível (fora, #897); sem preencher métrica vazia da Descoberta; sem colunas novas / export como aceite.

## 4. Contrato visível (número grande)

Fonte HTML + Playwright + pixels:

| Estado | Grade `/favorites` | Resumo `/combo/results` |
|---|---|---|
| Incidente SOL 1d «Médias Móveis: Tendência Confirmada» | RETURN **+98.591,56%** · Sharpe 0,45 · 32 · 68,75% · Max DD 14,15% | «Retorno total» **+98.591,56%** · acerto 68,75% · DD 14,15% · 32 ops |
| Composto &lt; 100% ETH | RETURN **+35,00%** (não 0,35% nem 3.500%) | extra é o par SOL; +35% não regride na grade |
| Número ~100× menor | **0** ocorrências de `985,85` no HTML e no texto visível | idem |
| «Voltar aos favoritos» | RETURN grande **preservado** após Analisar → Voltar (1280 e 390) | link 44px |

Copy visível **não** ensina 985,85% como «correcto» (zero no markup servido). Igualdade = composto grande (`98.591` / `+98.591,56%`), não o glifo do milhar.

## 5. Browser real — matriz (desktop 1280×800 e mobile 390×844)

Console error = 0; pageerror = 0; respostas ≥400 no proto = 0. Overflow `scrollWidth==clientWidth`. Gate bruto: `.impeccable/critique/935-B-gate.json` (**67/67 PASS**, fail 0).

Fluxo nos dois viewports: grade → ícone/Analisar SOL → resumo → «Voltar aos favoritos».

| # | Assert | Desktop | Mobile |
|---|---|---|---|
| 1 | Digest disco == HTTPS (não basta HTTP 200) | PASS | PASS |
| 2 | Landmarks `/favorites`: `table.fav-strategies` · «Estratégias favoritas» · Symbol · Estratégia · Ações | PASS (Ações x=1140 no viewport) | PASS (tabela no DOM; cards visíveis) |
| 3 | Zero botões Antes/Depois; index é o canónico | PASS | PASS |
| 4 | SOL RETURN **+98.591,56%**; não 985,85 | PASS | PASS |
| 5 | ETH **+35,00%**; não 0,35% nem 3.500% | PASS | PASS |
| 6 | Sharpe 0,45 · 32 · 68,75% · Max DD 14,15% na linha SOL | PASS | PASS |
| 7 | Extra `.combo-page` + «Análise da estratégia» + «Lista de operações» | PASS | PASS |
| 8 | «Retorno total» **+98.591,56%** = grade; acerto/DD/32 iguais | PASS | PASS |
| 9 | a11y resumo: `section[aria-label="Análise da estratégia"]` · `dl[aria-label="Resumo de desempenho e risco"]` · 4 `dt`/`dd` · sinal `+` no número (não só cor) · Voltar ≥44px | PASS | PASS |
| 10 | «Voltar aos favoritos» mantém o composto grande | PASS | PASS |
| 11 | 32 vs 33 na lista **não** «corrigido» (fora) | PASS | PASS |
| 12 | 0 console de impacto / 0 pageerror / 0 ≥400 / `sw==cw` | PASS | PASS |

Pixels desktop grade: RETURN verde `+98.591,56%` e `+35,00%` na coluna visível; Ações (gráfico) no viewport; nome SOL truncado «Médias Móveis: Tendência …» (table-layout fixed incumbente). Pixels extra: Retorno total o mesmo composto no `dl` à direita; lista 33.

Pixels mobile: cards SOL/ETH com o mesmo par de retornos; Analisar na thumb zone; extra mostra `+98.591,56%` no resumo 2×2; lista em cards 33.

Rota viva **não usada**. Browser correu só no proto.

## 6. Findings (toda finding classificada)

### P0 — nenhum

Tokens parseáveis ok; clone `/favorites` com landmarks + COPIED; extra `/combo/results` em `analise.html`; as duas telas mostram **+98.591,56%**, não 985,85%; +35% não regride na grade; digest servido == disco; sem painel ANTES/DEPOIS canónico; a11y do resumo suficiente para ler o composto; escopo #897 / 32 vs 33 / holdout / Monitor / redesign **não** furado. Fidelidade ok → não BLOCKED.

### P1 — nenhum

Delta observável nos dois viewports. Detector index classificado P3. Copy visível não ensina o número pequeno. Resumo `dt`/`dd` + `aria-label`.

### P3 — aceites (Apply / clone chrome; não reabrir como P0/P1)

- **P3-1 Detector `side-tab`** nos cards mobile de tier (`border-left: 3px`). Clone #897 / vivo. Não remover neste card.
- **P3-2 Truncagem desktop** de «Médias Móveis: Tendência Confirmada» na coluna Estratégia (`text-overflow`). table-layout fixed incumbente; mobile mostra o nome inteiro. Redesign fora.
- **P3-3 Lista 33 vs resumo/grade 32.** Incidente PROD; aceite deste card não é 32 vs 33. Deixar (#897).
- **P3-4 Alvos 32px** nos ícones da linha desktop; helper `formatMetricPercentage` vs `formatSignedPct`; copy de milhar vs `toFixed`. Já no Apply contract de `design.md`.
- **P3-5 ETH «Analisar» é botão inerte** (extra só cobre o par SOL). O estado +35% está na grade canónica nos dois viewports; o cenário «abre a análise da linha +35%» fica para o Apply. Não é segundo ecrã canónico.
- **P3-6 Par 169,51 / +16.951%** não está mockado no HTML (só no spec). O incidente +98.591,56% demonstra a mesma unidade grande. Apply testa o par #193/#897.
- **P3-7 Mock sem loading/vazio/erro.** Fora do delta.

Observações (não-findings): overlay `detect.js` não injectado (CLI + Playwright cobrem o HTML servido). Motor URL do detector não invocado. Cursor-ide-browser sem tab estável nesta sessão — evidência visual = PNGs Playwright. `/favorites` vivo sem sessão não é prova de clone.

## 7. Veredito

**PASS** — zero P0/P1 abertos; detector classificado; digest idêntico; clone+delta (não ANTES/DEPOIS); `/login` não usado como prova da rota; composto grande nas duas telas em desktop e mobile; +35% sem regressão na grade; a11y do resumo lê o número. HTTP 200 sozinho não sustentaria este veredito.

Disposition: crítico não pede rework. P3 aceites no Apply.

## 8. Referências

- Proto URL: https://dev.criptofarol.com.br/prototypes/card-935-favorites-combo-return/
- Extra: https://dev.criptofarol.com.br/prototypes/card-935-favorites-combo-return/analise.html
- Digest index: `2f2bb0a5a3c4ce5ee92b8ecbabf148d0732d7dcd40d87a5fef0ff217cc3cea39`
- Digest analise: `1bc0942794179d646f9a610d7f7cef85d85e1ffdb35485f378e77635cbb08d5c`
- Snapshot: `.impeccable/critique/935-card-935-favorites-combo-return-assessment-B.md`
- Gate bruto: `.impeccable/critique/935-B-gate.json`
- PNGs: `.impeccable/critique/935-B-index-desktop-1280x800.png`, `935-B-index-mobile-390x844.png`, `935-B-analise-desktop-1280x800.png`, `935-B-analise-mobile-390x844.png`
