UI impact: affected
live_route: /combo/discovery
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

# Design — card 906: métricas fáceis na grelha da Descoberta

## Context

Card [#906](https://github.com/oalansilva/crypto/issues/906). Briefing = issue grelhado. Q1=A · Q2=A. Sem reentrevista.

Hoje `/combo/discovery` mostra Calmar, Max DD e Trades/cobertura na grelha. Sharpe, Win% e CAGR da varredura já existem no payload e no promover («Retorno (CAGR)»); no Decidir só atrás de «+ detalhes»; no Acompanhar nem isso. Favoritos já tem Sharpe / Win% / Return acumulado — fora deste card.

**Audience:** operador da Descoberta a comparar candidatos no Acompanhar (top-5) ou no Decidir.
**Outcome:** as seis métricas fáceis alinhadas em coluna, sem expandir a linha.
**Direction:** clone+delta Operate; refinement. Tokens `DESIGN.md` Binance, sem reescrever.
**Scope:** grelha Acompanhar + grelha Decidir. Montar só landmarks.

Regiões clonadas (só estas): shell AppNav + heading + 3 modos + grelha Acompanhar + grelha Decidir. Montar (Preflight / Rascunho / «Descoberta de estratégias swing») entra no clone para landmarks; sem delta de colunas.

## Goals / Non-Goals

**Goals:**

- Mesmo conjunto visível nos dois modos: Calmar, Max DD, Trades/cobertura, Sharpe, Win%, CAGR.
- CAGR = retorno anualizado da varredura, não Return acumulado de Favoritos.
- Amostra insuficiente: Sharpe / Win% / CAGR também N/A.
- Comparar duas linhas vizinhas sem «+ detalhes».

**Non-Goals:**

- Favoritos, Montar (grelha), motor, ranking, selo GO/NO-GO, promoção.
- Ordenar por Sharpe, Win% ou CAGR (fica Calmar e CAGR vs B&H).
- Tirar as três colunas antigas. Só um dos modos.

## Decisions

### 1. Ordem e sítio: três novas depois de Trades

Cabeçalhos, da esquerda: Rank / Candidato · Calmar · Max DD · Trades/cobertura · Sharpe · Win% · CAGR · (Decidir: Ação). As três novas não substituem as antigas. Acompanhar não ganha «+ detalhes».

Rejeitado: meter CAGR no sítio do Calmar. Rejeitado: só Decidir (Q2=A).

### 2. CAGR anualizado, não Return

Célula CAGR = `fmtPct(cagr)` da varredura, o mesmo «Retorno (CAGR)» do promover. Hint `anualizado`. Win% hint `acerto` para não colidir com `30 · 100%`. Sharpe usa `fmtNum` (2 casas). Positivo/negativo semântico só em CAGR (e Calmar já negativo).

Rejeitado Q1-B/C: Return acumulado tipo `+47.916%`.

### 3. Largura: scroll horizontal no desktop; cards no estreito

Seis números não cabem em viewport estreita sem cortar candidato. Desktop: `overflow-x` na grelha (`min-width` sobe — P3 de Apply). Mobile (≤720px): o card-stack já existente com `data-label`; as seis métricas ficam em pares, nunca escondidas atrás de «+ detalhes».

Não colapsar colunas no desktop. Não tirar Calmar/Max DD/Trades.

### 4. O que fica em «+ detalhes»

Sharpe, Win% e CAGR saem da expansão (já estão na grelha). «+ detalhes» guarda B&H, Δ B&H, PF, mercado e janela — o que não virou coluna. Ordenar continua só Calmar e CAGR vs B&H.

## Risks / Trade-offs

- [Risco] Seis colunas apertam o candidato → Mitigação: overflow-x desktop; candidato permanece a âncora; mobile vira cards.
- [Risco] CAGR alto (Calmar ~22) parecer Return de Favoritos → Mitigação: cabeçalho CAGR + hint anualizado; sem sinal `+` de acumulado.
- [Risco] Win% confundir com Trades/cobertura → Mitigação: hint `acerto`; `30 · 100%` continua negócios · velas.

## Migration Plan

Sem schema. Rollback = reverter o thead/células. Payload já tem os campos.

## Open Questions

Nenhuma. Q1=A · Q2=A.

## Apply contract

Apply lê este `design.md` e `frontend/public/prototypes/card-906-discovery-metrics-grid/index.html` como spec de layout. Sem HTML neste arquivo.

**Contrato visível (não P3):**

- Acompanhar top-5 e Decidir: seis colunas de métrica no mesmo sítio, visíveis sem expandir.
- CAGR = anualizado da varredura (`fmtPct(cagr)`), não Return de Favoritos.
- Amostra insuficiente no Decidir: Sharpe, Win%, CAGR = N/A.
- Ordenar: só Calmar e CAGR vs B&H.
- Montar e Favoritos sem delta.

**P3 aceito (Apply):** `min-width` da `.discovery-table`; deixar de alinhar `th:last-child` à esquerda no Acompanhar (último passa a ser CAGR); `fmtPct`/`fmtNum` nas células novas; não duplicar Sharpe/Win%/CAGR na string de «+ detalhes».

## Recorte

- **Audience:** operador da Descoberta a varrer parciais ou a decidir promoção.
- **Outcome:** comparar Sharpe, Win% e CAGR entre linhas como já compara Calmar.
- **Direction:** clone da rota viva + três colunas; Operate; sem new-work.
- **Scope:** duas grelhas; Montar só landmark.

## Prototype

- URL: https://dev.criptofarol.com.br/prototypes/card-906-discovery-metrics-grid/
- Path: `frontend/public/prototypes/card-906-discovery-metrics-grid/index.html`
- Digest: `1e7121225d6cb339` (sha256 completo `1e7121225d6cb339e127657c463626dbfed13d751be6bda9d1fcfe84a723c8fc`, 45186 bytes; HTTPS == disco).
- Base: clone de `/combo/discovery` (HEAD desta branch, pós-#896/#897) + delta das três colunas. Sem painel ANTES/DEPOIS.
- Landmarks: «Descoberta de estratégias swing», «Preflight», «Rascunho de varredura».
- Estado default: Acompanhar com top-5 e as seis colunas visíveis.

## Prototype Validation

- URL: https://dev.criptofarol.com.br/prototypes/card-906-discovery-metrics-grid/
- Viewports: 1440×900 e 390×844 (Playwright Chromium, HTTPS, não file://).
- Disco == HTTPS após polish CSS (`.candidate span.details { display:none }`).
- Ações: default Acompanhar → Decidir → expandir «+ detalhes» → Montar.
- Asserts (22/22 PASS nos dois viewports): landmarks no HTML; seis colunas visíveis sem expandir; CAGR `17,8%` (não Return `+47.916%`); amostra insuficiente N/A em Sharpe/Win%/CAGR; sort só Calmar e CAGR vs B&H; «+ detalhes» `none→block` e guarda B&H/PF/janela; Montar sem grelha de métricas; 0 console/pageerror.
- Detector `detect.mjs`: `[]`.
- Resultado: **PASS** (autor). Dupla A/B e `## Design Critique` ficam no pai.

## Design Critique

- **P0:** nenhum
- **P1:** nenhum
- **P2:** nenhum
- **P3 (aceito, Apply):** Montar condensado vs vivo; `min-width` da `.discovery-table` / `th:last-child`; `data-label` mobile `Win rate`; chrome Acompanhar abaixo da dobra em 390×844; chip NO-GO full-width; leaderboard mock; ids `#c906grid` / `#PF-906-24`; `fmtPct`/`fmtNum` nas células novas.
- **Disposition:** P3 no Apply. Sem rework. Q1=A · Q2=A intactas.
- **Pendências não bloqueantes:** largura 6 colunas em ecrã estreito (scroll horizontal); «+ detalhes» guarda B&H/PF/janela.
- Proto: https://dev.criptofarol.com.br/prototypes/card-906-discovery-metrics-grid/ · digest `1e7121225d6cb339`
- Snapshot T7: `.impeccable/critique/906-card-906-discovery-metrics-grid.md` (A: `…-assessment-A.md` · B: `…-assessment-B.md`)
- `proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)`
- `proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`
- `proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)`
- Proxies: `design.md` words + HTML generated 1778 vs copied 21247 · spawns 3

Design Agent verdict: PASS
