---
score: 35/40
p0: 0
p1: 0
p3: 4
verdict: PASS
mode: Operate
card: 935
timestamp: 2026-09-14T01-27-10Z
slug: totypes-card-935-favorites-combo-return-index-html
---
⚠️ DEGRADED: single-context (Assessment A/B spawn forbidden by design-autor prompt; parent MUST NOT spawn crítico / Assessment A/B)

Method: single-context Operate clone+delta (autor). Detector CLI + Playwright headed (xvfb + /usr/bin/chromium-browser). Sem overlay injection live-server (não spawn B).

# Critique — card-935-favorites-combo-return

## Metadata

- card: 935 — Favoritos e Combo mostram retornos diferentes na mesma estratégia
- change: `card-935-favorites-combo-return`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-935-favorites-combo-return`
- mode: Operate (clone + delta; não redesign)
- UI impact: affected · live_route: /favorites · surface: existing
- Canonical URL: https://dev.criptofarol.com.br/prototypes/card-935-favorites-combo-return/
- Extra: https://dev.criptofarol.com.br/prototypes/card-935-favorites-combo-return/analise.html
- Ignore list: `.impeccable/critique/ignore.md` ausente

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 4 | RETURN e Retorno total visíveis no estado padrão |
| 2 | Match System / Real World | 4 | Percentual composto canónico (grande) nas duas pontas |
| 3 | User Control and Freedom | 4 | «Voltar aos favoritos» preserva o composto grande |
| 4 | Consistency and Standards | 3 | Lista 33 vs resumo 32 (fora; #897); truncagem do nome na grade |
| 5 | Error Prevention | 4 | Delta elimina o ~100× que levava a decisão errada no Monitor |
| 6 | Recognition Rather Than Recall | 4 | Mesmo número; não exige calcular 985,85 × 100 |
| 7 | Flexibility and Efficiency | 3 | Filtros/export clone; sem atalho novo (fora) |
| 8 | Aesthetic and Minimalist Design | 3 | Clone Binance/Favoritos; detector side-tab incumbente |
| 9 | Error Recovery | 3 | Mock estático sem estados erro/vazio (P3 Apply) |
| 10 | Help and Documentation | 3 | Sem copy nova de ajuda; briefing no issue |
| **Total** | | **35/40** | **Operate clone saudável** |

## Design Specificity Verdict

**LLM:** A composição é a grade autenticada de Favoritos + análise `/combo/results`. Não é intercambiável com um dashboard genérico: AppNav Cripto Farol, `table.fav-strategies`, chips SOL/USDT, «Voltar aos favoritos», tokens DESIGN.md. O delta é só o número canónico grande.

**Deterministic scan:** `detect.mjs` index = 2 warnings `side-tab` (border-left 3px nos cards mobile de tier) — incumbente do clone #897 / vivo. analise.html = 0 findings. Sem P0/P1 de produto.

**Visual overlays:** não injectados (sem Assessment B spawn). Screenshots Playwright: desktop 1280×800 e mobile 390×844, index + analise.

## Overall Impression

O clone carrega a tarefa. O incidente lê-se em segundos: SOL/USDT RETURN **+98.591,56%** na grade e **+98.591,56%** no resumo. ETH +35,00% não regride. Não há painel ANTES/DEPOIS. A lista com 33 negócios permanece visível e fora do aceite.

## What's Working

- Paridade do composto grande nas duas telas (contrato do card).
- Landmarks `/favorites` no index; `/combo/results` no extra.
- Interação Analisar → Voltar preserva o número.

## Priority Issues

- **[P3] What:** Detector `side-tab` nos cards mobile de tier (`border-left: 3px`).
  - **Why:** slop detector; é o clone vivo / proto #897.
  - **Fix:** não remover neste card (redesign). Aceito Apply se o vivo mudar.
  - **Suggested command:** none (fora)

- **[P3] What:** Nome «Médias Móveis: Tendência Confirmada» trunca na coluna Estratégia a 1280px.
  - **Why:** table-layout fixed incumbente.
  - **Fix:** não alargar colunas (redesign fora). Mobile mostra o nome inteiro.
  - **Suggested command:** none

- **[P3] What:** Lista do gráfico 33 negócios vs 32 no resumo/grade.
  - **Why:** incidente PROD; aceite deste card não é 32 vs 33.
  - **Fix:** deixar. #897.
  - **Suggested command:** none

- **[P3] What:** Alvos 32px nos ícones da linha; formatador (`formatMetricPercentage` vs `formatSignedPct`); copy de milhar vs toFixed.
  - **Why:** detalhe de Apply / incumbente.
  - **Fix:** Apply contract.
  - **Suggested command:** $impeccable harden só se o vivo falhar a11y depois

## Audit (técnico)

| Dimensão | Score | Notas |
|---|---|---|
| A11y | 3 | focus-visible, landmarks, tabela semântica; alvos 32px incumbentes |
| Performance | 4 | HTML estático |
| Theming | 3 | tokens DESIGN.md no clone; cores hardcoded como o vivo |
| Responsive | 3 | cards mobile; tabela some <1024 (clone) |
| Integrity | 3 | 2 side-tab warnings classificados P3; sem false-negative do número |

## Cognitive load

Uma decisão: o retorno da linha. Quatro métricas no resumo. Filtros da grade são clone, não opções novas deste card.

## Persona red flags

Nenhum no delta. O bug vivo (985,85% vs +98.591%) era o red flag; o proto já o corrige.

## Browser gate

- Comando: `xvfb-run -a python3` + Playwright Chromium `/usr/bin/chromium-browser` headed, viewports 1280×800 e 390×844.
- URLs: canónico `https://dev.criptofarol.com.br/prototypes/card-935-favorites-combo-return/` · extra `…/analise.html`.
- Asserts: landmarks `/favorites`; RETURN e Retorno total contém 98.591 / 98591; NÃO 985,85; acerto 68,75% / DD 14,15% / n 32; +35,00% sem 0,35 nem 3.500; Analisar / Voltar; 0 console errors.
- Resultado: **35/35 PASS**.

## Verdict

PASS — Operate clone + delta do composto canónico. Zero P0/P1 de produto. P3 aceitos. Snapshot persistido.
