UI impact: affected
live_route: /combo/discovery
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

# Design — card 944: nomes e ordem iguais a Favoritos na Descoberta

## Context

Card [#944](https://github.com/oalansilva/crypto/issues/944). Briefing = issue grelhado. Q1 = só nomes e ordem; Q2 = parciais E leaderboard; Q3 = CAGR anualizado no final com nome próprio. Sem reentrevista.

Hoje `/combo/discovery` (pós-#906/#916) mostra Calmar · Max DD · Trades/cobertura · Sharpe · Win% · CAGR. Favoritos mostra Sharpe · Trades · Win% · Return · Max DD. O Return de Favoritos não existe na Descoberta; CAGR 3,7% no recorte não é o Return +16.951%.

**Audience:** administrador que vai de Favoritos para a Descoberta (e volta) olhando o mesmo setup.
**Outcome:** os mesmos nomes e a mesma ordem dos indicadores partilhados, sem achar que é outra estratégia.
**Direction:** clone+delta Operate; refinement. Tokens `DESIGN.md` Binance, sem reescrever.
**Scope:** grelha Acompanhar (parciais) + grelha Decidir (leaderboard). Montar só landmarks.

Regiões clonadas (só estas): shell AppNav + heading + 3 modos + grelha Acompanhar (parciais) + grelha Decidir (leaderboard). Montar (Preflight / Rascunho / «Descoberta de estratégias swing») entra no clone para landmarks; sem delta de colunas no Montar.

## Goals / Non-Goals

**Goals:**

- Bloco partilhado na ordem de Favoritos: Sharpe → Trades → Win% → Return → Max DD.
- Extras depois: Calmar (subtexto CAGR ÷ Max DD) e CAGR anualizado (nome próprio, no final).
- Return existe como coluna; CAGR não usa esse nome nem esse sítio.
- Trades = nome Trades; cobertura de velas só como subtexto.
- As duas grelhas iguais. Identidade (rank, candidato, ação) permanece.

**Non-Goals:**

- Igualar o número do Return (nem de qualquer outro indicador) ao de Favoritos.
- Copiar a grade inteira de Favoritos (Sel, Tier, Telegram, Symbol, Stop, PF, SQN).
- Mudar Favoritos.
- Mudar cálculo do Calmar, ranking, filtros, seletor de ordenar, GO/NO-GO.
- Card irmão #897 (preencher métricas depois de promover).
- Monitor, Telegram, mobile de Favoritos, Excel.

## Decisions

### 1. Ordem visível: Favoritos primeiro, extras no fim

Cabeçalhos, da esquerda: Rank / Candidato · Sharpe · Trades · Win% · Return · Max DD · Calmar · CAGR anualizado · Ação. As duas grelhas usam esta ordem. Visível sem expandir «+ detalhes». Montar sem nova ordem.

Rejeitado: manter Calmar à esquerda. Rejeitado: só uma das grelhas (Q2).

### 2. Return = composto da janela da varredura, não CAGR

O número sob Return é o retorno composto da janela de evidência (`metrics.total_return` / `total_return_pct` já persistidos no JSON do resultado pelo optimizer; N/A se amostra insuficiente ou chave ausente). Não é `cagr`. Não é o Return armazenado em Favoritos. Formato com sinal `+`/`−` e `%`, para o rótulo ser reconhecível. Recorte do proto: ALPHA CAGR 3,7% vs Return +12,8% — números diferentes de propósito.

Rejeitado: etiquetar CAGR como Return. Rejeitado: copiar +16.951% de Favoritos.

### 3. Trades = nome; cobertura = subtexto

Cabeçalho **Trades**, hint `cobertura`. Célula: contagem de negócios; cobertura em subtexto (`100% velas`). Não `Trades/cobertura`.

### 4. Max DD mantém o sinal desta tela

Favoritos mostra 16,51% sem sinal; a Descoberta já mostra −16,5%. Este card não muda o formato do número. Sinal negativo permanece.

### 5. Payload: JSON já tem o composto; Apply só expõe

`DiscoveryResult` não tem coluna `total_return`. `_persist_metrics_snapshot` copia `best_metrics`, e o optimizer grava `total_return` / `total_return_pct`. `_result_row` hoje não promove esses campos ao top-level. Apply lê o JSON (ou promove no payload) — P3 de wiring. Sem schema novo. Sem recálculo.

## Risks / Trade-offs

- [Risco] Operador achar que Return da Descoberta tem de igualar Favoritos → Mitigação: CAGR anualizado visível no final; proto e nota separam os números; critério de aceite já diz que números diferentes não são falha.
- [Risco] Sete colunas apertam o candidato → Mitigação: overflow-x desktop (`min-width` P3); cards no estreito com `data-label`.
- [Risco] Linhas antigas sem `total_return` no JSON → Mitigação: N/A, nunca etiquetar CAGR.

## Migration Plan

Sem schema. Rollback = reverter thead/células e o campo top-level se Apply o tiver adicionado. Ranking e Favoritos intactos.

## Open Questions

Nenhuma. Q1–Q3 fechadas. Return, cobertura e sinal do Max DD decididos acima.

## Apply contract

Apply lê este `design.md` e `frontend/public/prototypes/card-944-discovery-favorites-nomenclature/index.html` como spec de layout. Sem HTML neste arquivo.

**Contrato visível (não P3):**

- Parciais e Decidir: Sharpe → Trades → Win% → Return → Max DD → Calmar (CAGR ÷ Max DD) → CAGR anualizado, visíveis sem expandir.
- Return ≠ CAGR ≠ Return de Favoritos.
- Trades não se chama Trades/cobertura.
- Ordenar: só Calmar e CAGR vs B&H.
- Montar e Favoritos sem delta.

**P3 aceito (Apply):** expor `total_return`/`total_return_pct` no payload da grelha se o frontend ainda lê só top-level; `min-width` da `.discovery-table` para 7 métricas; formatar Return com sinal (reuso de `formatCompoundReturn` ou `fmtPct` assinado); `data-label` mobile da nova ordem; testes que ainda afirmam Calmar-primeiro / `Trades/cobertura`; N/A quando o JSON não tem o composto.

## Recorte

- **Audience:** administrador a comparar o mesmo setup em Favoritos e na Descoberta.
- **Outcome:** mesmos nomes, mesma ordem; Return existe; CAGR no final.
- **Direction:** clone da rota viva + delta de ordem/nomes; Operate; sem new-work.
- **Scope:** duas grelhas; Montar só landmark.

## Prototype

- URL: https://dev.criptofarol.com.br/prototypes/card-944-discovery-favorites-nomenclature/
- Path: `frontend/public/prototypes/card-944-discovery-favorites-nomenclature/index.html`
- Digest: `e8e632a2d44c34ac` (sha256 completo `e8e632a2d44c34ac7e93674adad5599f3a2b159ac6a0a57ae6a38640c8f44ed3`).
- Base: clone de `/combo/discovery` via proto `card-916-discovery-acompanhar-acoes` (já com Sharpe/Win%/CAGR e acções) + delta de ordem/nomes. Sem painel ANTES/DEPOIS.
- Landmarks: «Descoberta de estratégias swing», «Preflight», «Rascunho de varredura».
- Estado default: Acompanhar com top-5 e a nova ordem visível.

## Prototype Validation

- URL: https://dev.criptofarol.com.br/prototypes/card-944-discovery-favorites-nomenclature/
- Viewports: 1440×900 e 390×844 (Playwright Chromium, HTTPS, não file://).
- Disco == HTTPS: sha256 `e8e632a2d44c34ac7e93674adad5599f3a2b159ac6a0a57ae6a38640c8f44ed3`.
- Ações: default Acompanhar → Decidir → expandir «+ detalhes» → Montar.
- Asserts (29/29 PASS nos dois viewports, headers via `span:not(.th-hint)`): landmarks; default Acompanhar; ordem Sharpe → Trades → Win% → Return → Max DD → Calmar → CAGR anualizado nas duas grelhas sem expandir; ALPHA Return `+12,8%` ≠ CAGR `3,7%`; sem `Trades/cobertura`; insuficiente N/A em Return e CAGR anualizado; sort só Calmar e CAGR vs B&H; «+ detalhes» guarda B&H/PF; Montar sem grelha; 0 console/pageerror.
- Detector `detect.mjs`: `[]`.
- Resultado: **PASS** (autor). Dupla A/B e `## Design Critique` abaixo.

## Design Critique

- **P0:** nenhum
- **P1:** nenhum
- **P2:** nenhum
- **P3 (aceito, Apply):** expor `total_return`/`total_return_pct` no payload; `min-width` da `.discovery-table` (Ação clipa a 1440); formatar Return com sinal; `data-label` mobile (`Win rate` / `Maximum Drawdown`); testes que ainda afirmam Calmar-primeiro / `Trades/cobertura`; Montar condensado vs vivo; chrome Acompanhar abaixo da dobra em 390×844; chip NO-GO full-width; leaderboard mock 309/4; modal promover ainda diz «Retorno (CAGR)».
- **Disposition:** P3 no Apply. Sem rework. Q1 = nomes e ordem · Q2 = parciais e leaderboard · Q3 = CAGR extra no final — intactas.
- **Pendências não bloqueantes:** sete colunas em ecrã estreito (scroll horizontal); Return da Descoberta ≠ Return de Favoritos (contrato).
- Proto: https://dev.criptofarol.com.br/prototypes/card-944-discovery-favorites-nomenclature/ · digest `e8e632a2d44c34ac`
- Snapshot T7: `.impeccable/critique/944-card-944-discovery-favorites-nomenclature.md` (A: `…-assessment-A.md` · B: `…-assessment-B.md`)
- `proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)`
- `proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`
- `proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)`
- Proxies: `design.md` words + HTML generated 37331 vs copied 27915 · spawns 3

Design Agent verdict: PASS
