# Snapshot — card 896 · change card-896-discovery-calmar-nogo

> Evidência longa do filho Design-autor. O `design.md` traz só recorte (P0–P3 + disposition + verdict); este arquivo é o snapshot completo. Não enviar ao Gist. Assessment A/B **não** spawnados neste filho (ordem do pai); a dupla é do pai após este PASS.

Method: autor-only (A/B deferred to parent — explicit spawn ban). Detector CLI ran inline. Browser gate headed real (não file://).

## Metadata

- card: 896 — "Descoberta: ranking por Calmar dispara número enorme e esconde NO-GO"
- change: `card-896-discovery-calmar-nogo`
- worktree: `/srv/apps/dev/criptofarol/crypto-worktrees/card-896-discovery-calmar-nogo` · branch `card-896-discovery-calmar-nogo`
- Status observado: Design (T3 pelo pai; este filho não chama `process_event`)
- bound_card=896 · q_git=`card-896-discovery-calmar-nogo`
- autor: filho Design-autor isolado · continuação (spawn anterior cancelado a meio) · sem recriar change
- data (UTC): 2026-09-11T17:45Z
- pipeline: (change+proto já apply-ready) → browser gate → polish CSS mobile (1×) → re-gate → Prototype Validation → este snapshot → Gist
- spawns: 0 nested (sem crítico / A/B)
- UI impact: affected · live_route: `/combo/discovery` · surface: existing

## Brief (integral — issue grelhado via `gh api repos/oalansilva/crypto/issues/896`, sem reentrevista)

**Problema:** administrador da Descoberta vê Calmar `1.195.206.471.012.770.100.000.000.000,00` em ALPHA/USDT 1d Long (`RS-B109ED2C80`, varredura `#862f31de`) e promove como «melhor agora». Walk-forward já era **NO-GO** (Sharpe IS 0,31). Causa: curva de equity sem `DatetimeIndex`; `calculate_cagr` trata cada ponto como 1 dia (`len(equity)/365`); 30 negócios + capital ≈ 31/365 ano; CAGR `1.97e26`, Calmar `1.195e27`. `fmtNum` formata qualquer finito como `pt-BR` 2 casas — 27 dígitos. `oos_verdict` já gravado; Acompanhar e Decidir não pintam.

**História:** como administrador da Descoberta, quero Calmar com tempo de calendário e veredito NO-GO na linha, para não promover um candidato só porque a coluna parece um jackpot.

**Entra:** anos = calendário da janela; Calmar = CAGR ÷ Max DD (fração 0–1); absurdo/não finito = `N/A` (não disputa 1º); selo GO/NO-GO nas parciais e no Decidir, sem gráfico nem promover; todo GO acima de todo NO-GO; NO-GO permanece na lista; copy Calmar ≠ retorno; `30 · 100%` = negócios/cobertura, não win rate; ALPHA deixa de ser top-1 por `1e27`.

**Não entra:** amostra insuficiente (#876); achatar métricas no favorito (#897); redesign 3 modos (#852); universo/split 70/30; backfill `#862f31de`; ensinar Calmar na landing/Ajuda; travar Promover.

**Vocabulário:** Calmar (não lucro); CAGR calendário; Max DD fração; NO-GO ≠ Baixa amostra / Amostra insuficiente; `30 · 100%` ≠ taxa de acerto. Típico 1–3; honesto do incidente ~22.

**Aceite:** 7 givens do body. Q1 aceite. Fronteira vazia.

**Como (Design):** calendário da janela; teto antes de gravar e de `fmtNum`; selo na linha; entre NO-GOs Calmar → negócios → id.

## Shape

- Audience: administrador da Descoberta, varredura em curso ou recém-terminada.
- Outcome: não promover NO-GO só porque Calmar parece jackpot.
- Direction: clone+delta Operate / refinement da rota viva `/combo/discovery`. Tokens `DESIGN.md` Binance, sem reescrever.
- Scope: Acompanhar parciais + Decidir linhas (selo, ordem, célula, copy). Montar intacto (landmarks só).
- Untouched: 3 modos, CTA Promover, #876, #897, favoritos.
- Assumptions (sem AskUser): teto `|Calmar|>1000`; GO azul informativo / NO-GO danger; veredito ausente ≠ GO.

## Decisions (espelho do design.md — não reabrir)

1. Anos = `(end_at − start_at).days / 365` da janela in-sample. Não `n_trades/365`.
2. Não finito ou `|Calmar|>1000` → `N/A`. Honesto ~22 permanece `22,00`. `1,20` nunca `N/A`. UI sanitiza legado `1e27`.
3. `rank_eligible`: classe GO acima de não-GO; dentro da classe Calmar → negócios → id. Elegibilidade 30/90% intacta.
4. Selo na linha (chip, não tooltip-only). Promover no NO-GO elegível permanece.
5. Copy mínima: `Calmar (CAGR anual do calendário ÷ Max DD)`; `negócios / cobertura`; nota «não é taxa de acerto».

## Fidelidade (clone)

Catálogo `/combo/discovery` (`scripts/process-fsm/route-landmarks.yaml`):

| Landmark | Proto + Playwright |
|---|---|
| `Descoberta de estratégias swing` | h1 visível no default (desktop e mobile) |
| `Preflight` | `aria-label="Preflight da varredura"` + h2 visível após tab Montar |
| `Rascunho de varredura` | article `aria-label` + h2 visível após tab Montar |

8 pares `COPIED:start/end`. Index = página (shell 224px + heading + 3 modos + Acompanhar + Decidir). **Não** galeria ANTES/DEPOIS. Botões Antes/Depois = 0. Tabs trocam markup (`.modepanel.active` + `aria-selected`).

## Browser gate (autor)

- URL: https://dev.criptofarol.com.br/prototypes/card-896-discovery-calmar-nogo/
- Digest `19c07a26d8c479ab5a56482759f58a0683a209f9aeb674cf2ced525b6f3e5a08` · 37328 bytes · servido == local (`cmp` clean)
- Copiados 7180 · gerados 30148 · 8 pares COPIED
- Tooling: `@playwright/cli` 0.1.19 headed sob `xvfb-run -a`, `PLAYWRIGHT_MCP_SANDBOX=false`, executable Chromium 1243 arm64. `playwright-cli-headed` / `/usr/local/bin/playwright-cli-headed` **ausentes**. Um `run-code` por viewport: `goto` + asserts + `screenshot`.
- Gate v1 desktop: 19/20 — falha de harness (`#panel-montar h2` lia Rascunho, Preflight já visível). Harness corrigido; proto intacto nessa rodada.
- Pixels v1 mobile: selo GO/NO-GO fora do crop (td.candidate flex-row ≤720px). **Delta CSS** (wrap + `flex: 1 0 100%` no `.verdict`). Re-gate 1×.
- Gate v2: desktop **20/20 PASS**; mobile **18/18 PASS** (selo no viewport). 0 console / 0 pageerror / 0 ≥400.
- PNGs git-tracked: `.impeccable/critique/896-autor-desktop-1440x900.png` (116634 B), `.impeccable/critique/896-autor-mobile-390x844.png` (50252 B).

### Asserts (PASS em ambos os viewports)

1. Landmark h1 `Descoberta de estratégias swing` visível.
2. Landmark Preflight visível após Montar.
3. Landmark Rascunho de varredura visível após Montar.
4. Acompanhar: 1º = GO, Calmar exact `1,20`, selo `GO`.
5. ALPHA/USDT rank 4: selo `NO-GO`, Calmar `22,00`, sem `1e27` / dinheiro de 27 dígitos.
6. Célula absurda = `N/A`.
7. Ordem parciais: GO, GO, GO, NO-GO, NO-GO.
8. Selo visível sem canvas/chart/dialog (mobile: bounding box no viewport).
9. `30 · 100%` na linha ALPHA.
10. `aria-label` contém `negócios / cobertura`.
11. Decidir: GO acima de NO-GO.
12. Promover no NO-GO elegível `disabled=false`.
13. Decidir N/A + `30 · 100%` + copy «negócios»/«cobertura», sem «win rate».
14. Sem painel ANTES/DEPOIS.
15. Sem page/console errors bloqueantes.

Pixels desktop: ranks 1–3 GO (Calmar 1,20 / 0,94 / 0,81); rank 4 ALPHA NO-GO 22,00 e `30 · 100%`; rank 5 N/A. Hint `CAGR ÷ Max DD` / `negócios · velas`. Copy «Todo GO acima de todo NO-GO».

Pixels mobile: card rank 3 selo GO; rank 4 ALPHA `NO-GO` + `22,00` + `30 · 100%`; rank 5 `N/A` + `NO-GO`.

## Detector

`node .agents/skills/impeccable/scripts/detect.mjs --json frontend/public/prototypes/card-896-discovery-calmar-nogo/index.html` → `[]`.

## Critique própria (autor, não A/B)

- C1 (harness, não proto): assert Preflight lia o primeiro h2 do Montar. Corrigido no script.
- C2 (P1 visual → corrigido no re-gate): chip de veredito esmagado na flex-row mobile. CSS wrap. Re-gate verde. Residual P3: chip ocupa a largura do card; Apply pode encolher.
- Detector: nenhum achado.

## Audit (só com achado)

- A1 (harden): proto estático; tabs só setam classes; sem innerHTML de input.
- A2 (adapt): tabela → cards ≤720px (`data-label`); wrap do selo no re-gate.
- A3 (clarify): nota Decidir «Calmar não é retorno… não é taxa de acerto»; `Baixa amostra` vizinha intacta (não misturar com NO-GO).

## Nielsen (Operate / admin Descoberta)

| # | Heuristic | Score | Key issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 4 | Selo GO/NO-GO na linha; progresso 18/24; chip EM CURSO |
| 2 | Match System / Real World | 4 | Calmar honesto `22,00`; copy negócios/cobertura; vocabulário do issue |
| 3 | User Control and Freedom | 3 | Tabs + Pausar/Cancelar/Novo rascunho; Promover no NO-GO permanece (Q1) |
| 4 | Consistency and Standards | 3 | Tokens Binance; GO azul ≠ Long verde; NO-GO danger ≠ âmbar amostra |
| 5 | Error Prevention | 4 | GO-first + N/A + selo visível previnem o jackpot `1e27` |
| 6 | Recognition Rather Than Recall | 4 | Veredito na linha; hints no `<th>`; sem tooltip-only |
| 7 | Flexibility and Efficiency | 3 | Tabs teclado ArrowLeft/Right; sem atalhos extra (fora de escopo) |
| 8 | Aesthetic and Minimalist Design | 3 | Clone Operate; chip mobile full-width (P3) |
| 9 | Error Recovery | 3 | N/A sanitiza legado; sem backfill (non-goal) |
| 10 | Help and Documentation | 3 | Copy mínima da coluna; Ajuda/landing fora de escopo |
| **Total** | | **34/40** | **Good** |

Cognitive load: 1 falha (chunking — 5 linhas + 5 colunas no desktop; aceitável em Operate). Single focus no ranking. Working memory: selo + Calmar co-localizados.

## Personas

**Alex (admin Descoberta / power user):** vê GO `1,20` no 1º em <5 s; ALPHA 22,00 abaixo com NO-GO; Promover continua no elegível. Sem red flag de tarefa.

**Sam (teclado / leitor):** landmarks 3/3; `aria-label` Calmar e negócios/cobertura; `:focus-visible` global; tabs roving. Chip não é só cor (texto GO/NO-GO).

**Riley (stress):** `1e27` ausente; N/A no 5º; Baixa amostra ADA intacta e distinta; Promover disabled só nela.

## Priority issues

- **P0** — nenhum.
- **P1** — nenhum (pós re-gate).
- **P3** — Montar condensado; Decidir sem filtros/modais; Promover outline vs fill; mock 16/16 vs 5 linhas; `#PF-896-24`; `oos_verdict` top-level vs nested; chip mobile full-width.

## Disposition

P3 no Apply. Não reabrir grelha. Pai spawna Assessment A/B. Sem `process_event`, sem commit/push, sem editar `source/`.

## Trace

1. Tuple `q=Design bound_card=896 q_git=card-896-discovery-calmar-nogo` via `scripts/process-fsm`.
2. Change já apply-ready; proposal/specs/tasks intocados.
3. Clone gate prévio: HTTP 200, 8 COPIED, landmarks 3/3.
4. Browser gate canónico; harness Preflight; CSS mobile wrap; re-gate 20/20 + 18/18.
5. `openspec validate card-896-discovery-calmar-nogo` (não `--all`).
6. Gist + comentário no issue 896 (helper covenant-flow). HTML **não** no Gist.

## Veredito próprio

**PASS** — browser gate verde nos dois viewports; digest servido == local; P0/P1 nenhum. Verdict da coluna no `design.md` só depois deste gate (validação já não está Pendente).
