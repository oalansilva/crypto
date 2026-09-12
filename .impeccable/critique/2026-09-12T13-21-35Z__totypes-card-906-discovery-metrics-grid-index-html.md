---
card: 906
change: card-906-discovery-metrics-grid
verdict: autor-PASS
ui_impact: affected
timestamp: 2026-09-12T13-21-35Z
slug: totypes-card-906-discovery-metrics-grid-index-html
---
# Snapshot — card 906 · change card-906-discovery-metrics-grid

> Evidência longa do filho Design-autor. O `design.md` traz só recorte; este arquivo é o snapshot completo (Brief/Shape/Audit/Trace). Não enviar ao Gist. Assessment A/B **não** spawnados neste filho (ordem do pai).

Method: autor-only (A/B deferred to parent — explicit spawn ban). Detector CLI ran inline. Browser gate Playwright Chromium real HTTPS.

## Metadata

- card: 906 — "detalhamento das metricas na tela de descoberta"
- change: `card-906-discovery-metrics-grid`
- worktree: `/srv/apps/dev/criptofarol/crypto-worktrees/card-906-discovery-metrics-grid` · branch `card-906-discovery-metrics-grid`
- Status observado: Design
- bound_card=906 · q_git=`card-906-discovery-metrics-grid`
- autor: filho Design-autor isolado · 1 spawn
- data (UTC): 2026-09-12T13:20Z
- pipeline: context.mjs → shape → openspec new+ff → clone+delta proto → detect.mjs → Playwright desktop+mobile → polish CSS 1× → re-gate → este snapshot
- spawns: 0 nested (sem crítico / A/B)
- UI impact: affected · live_route: `/combo/discovery` · surface: existing
- proxy modelo: design-autor → Grok 4.6 (`cursor-grok-4.6-high`)

## Brief (integral — issue grelhado via `gh api repos/oalansilva/crypto/issues/906`, sem reentrevista)

**Problema:** o operador na Descoberta não consegue ler na grelha os números fáceis que já vê em Favoritos (Sharpe, Win%, retorno): no Decidir eles só aparecem depois de «+ detalhes»; no Acompanhar nem isso. Comparar candidatos vira abrir linha a linha.

**História:** como operador da Descoberta, quero ver Sharpe, Win% e CAGR na grelha — junto com Calmar, Max DD e Trades/cobertura, como já vejo números fáceis em Favoritos — para comparar candidatos no Acompanhar e no Decidir sem abrir cada linha.

**Decisões (Alan, rodada 1):** Q1=A · Q2=A.

**Entra:**

- Nas parciais do Acompanhar (top-5) e na lista do Decidir, a grelha mostra em coluna, sem expandir a linha: Calmar, Max DD, Trades/cobertura, Sharpe, Win% e CAGR.
- CAGR é o retorno anualizado da varredura (o mesmo «Retorno (CAGR)» do diálogo de promover), não o Return acumulado de Favoritos.
- Linha com amostra insuficiente no Decidir: Sharpe, Win% e CAGR também mostram N/A, como Calmar / Max DD / Trades já fazem.
- As duas grelhas usam o mesmo conjunto de colunas no mesmo sítio.

**Não entra:** Favoritos; Montar (sem grelha de candidatos); motor/ranking/selo GO/NO-GO/promoção; ordenar por Sharpe/Win%/CAGR; Return acumulado; tirar as 3 colunas antigas; só um modo.

**Vocabulário:** Grelha da Descoberta; métricas fáceis; Acompanhar (não Acompanhamento); Decidir (não Decidor); Calmar; Return (Favoritos) fora; CAGR anualizado; Trades/cobertura ≠ Win%.

**Aceite:** 7 givens do body. Fronteira vazia.

**Como (Design):** largura da grelha (6 colunas), ecrã estreito, o que fica em «+ detalhes» (B&H, Δ, PF, janela).

## Shape

- Job/audience: operador da Descoberta em Acompanhar (top-5) ou Decidir, a comparar candidatos em fluxo, sem expandir.
- Outcome: Sharpe, Win% e CAGR alinhados em coluna junto a Calmar / Max DD / Trades.
- Direction: clone+delta Operate / refinement de `/combo/discovery`. Tokens `DESIGN.md` Binance, sem reescrever.
- Scope: duas grelhas; Montar só landmarks. Favoritos intacto.
- States: métricas finitas; Calmar N/A → novas N/A; amostra insuficiente → seis N/A; Baixa amostra fora do delta.
- Interaction: desktop overflow-x; mobile cards `data-label`; «+ detalhes» não esconde as três novas.
- Assumptions (sem AskUser): ordem Calmar → Max DD → Trades → Sharpe → Win% → CAGR; hint CAGR `anualizado`; hint Win% `acerto`.

## Decisions

1. Três colunas novas depois de Trades; não substituem as antigas.
2. CAGR = `fmtPct(cagr)` anualizado, não Return `+47.916%`.
3. Desktop scroll horizontal; mobile card-stack com as seis métricas visíveis.
4. «+ detalhes» guarda B&H, Δ B&H, PF, mercado, janela. Sort continua Calmar e CAGR vs B&H.

## Fidelidade (clone)

Catálogo `/combo/discovery` (`scripts/process-fsm/route-landmarks.yaml`):

| Landmark | Proto + Playwright |
|---|---|
| `Descoberta de estratégias swing` | h1 no default (desktop e mobile) |
| `Preflight` | h2 no painel Montar (tab) |
| `Rascunho de varredura` | h2 no painel Montar (tab) |

10 pares `COPIED:start/end`. Index = página (shell 224px + heading + 3 modos + Acompanhar + Decidir). **Não** galeria ANTES/DEPOIS. Botões Antes/Depois = 0. Tabs trocam markup (`.modepanel.active` + `aria-selected`). Montar sem delta de colunas.

Base: `DiscoveryPage.tsx` HEAD (pós-#896/#897) + proto 896 chrome. Capturas do issue lidas (Acompanhar 3 colunas; Decidir + detalhes; Favoritos só referência).

## Detector / Audit

`node .agents/skills/impeccable/scripts/detect.mjs --json frontend/public/prototypes/card-906-discovery-metrics-grid/index.html` → `[]` (exit 0).

Polish 1×: `.candidate span` ganhava de `.details { display:none }`; «+ detalhes» nascia aberto. Patch: `.candidate span.details { display:none }` / `.open { display:block }`. Re-gate verde.

## Browser gate (autor)

- URL: https://dev.criptofarol.com.br/prototypes/card-906-discovery-metrics-grid/
- Digest `1e7121225d6cb339e127657c463626dbfed13d751be6bda9d1fcfe84a723c8fc` · 45186 bytes · servido == disco
- Copiados 21247 · gerados (delta colunas) 1778 · 10 pares COPIED
- Tooling: Playwright Chromium via `frontend/node_modules/playwright` (source), HTTPS, viewports 1440×900 e 390×844
- Gate v1: 2 falhas de harness/CSS (landmark Montar hidden no `innerText`; detalhes sempre visíveis). Polish + asserts via `page.content()` / display computed.
- Gate v2: desktop **22/22 PASS**; mobile **22/22 PASS**. 0 console / 0 pageerror.
- PNGs: `.impeccable/critique/906-autor-desktop-1440x900.png`, `906-autor-mobile-390x844.png`, `906-autor-desktop-decidir-1440x900.png`

### Asserts (PASS em ambos)

1. Landmarks no HTML: Descoberta / Preflight / Rascunho.
2. Default Acompanhar visível; thead com seis métricas; sem «+ detalhes».
3. Sharpe parcial `0,31`; linha N/A também N/A em Sharpe.
4. CAGR visível sem expandir.
5. Decidir: mesmas seis colunas; CAGR `17,8%` ≠ Return Favoritos.
6. Amostra insuficiente: Sharpe/Win%/CAGR = N/A.
7. Sort: Calmar e CAGR vs B&H; sem Sharpe/Win%.
8. «+ detalhes» `none→block`; B&H/PF/janela; sem duplicar Sharpe/Win%/CAGR.
9. Colunas continuam visíveis após expandir.
10. Montar: Preflight + Rascunho; sem `table.lb`.
11. Zero botões Antes/Depois.
12. Console limpo.

## Personas (arquivo, não no design.md)

- Operador em Acompanhar: lê top-5 e compara Sharpe/Win%/CAGR sem sair da parcial.
- Operador em Decidir: escolhe promover com as seis colunas alinhadas; amostra insuficiente continua N/A.
- Leitor de Favoritos: superfície intacta (fora).

## Heuristics (arquivo)

Nielsen não emitido no chat. Scanabilidade da grelha sobe (reconhecimento vs recall). Densidade 6 colunas é o trade-off aceite; mobile empilha.

## OpenSpec paths

- `openspec/changes/card-906-discovery-metrics-grid/proposal.md`
- `openspec/changes/card-906-discovery-metrics-grid/design.md` (953 palavras)
- `openspec/changes/card-906-discovery-metrics-grid/tasks.md`
- `openspec/changes/card-906-discovery-metrics-grid/specs/discovery-leaderboard/spec.md`
- `openspec/changes/card-906-discovery-metrics-grid/specs/discovery-three-modes/spec.md`
- `frontend/public/prototypes/card-906-discovery-metrics-grid/index.html`

`openspec validate card-906-discovery-metrics-grid --type change --strict` → valid.

## Proxies

- palavras `design.md`: 953
- HTML copiado: 21247 bytes · gerado (delta colunas): 1778 bytes · total 45186
- spawns: 1 (este autor)
- proxy modelo: design-autor → Grok 4.6 (`cursor-grok-4.6-high`)
