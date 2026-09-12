## Context

Card **#917**, Status=Design. Briefing = issue grelhado. Sem re-entrevista.

Hoje, Favoritos → `/combo/results`: a lista mostra o histórico da análise (BTC/USDT 1d: 73 operações, 2017-10-05 → 2026-07-29) e o gráfico abre em ~180 velas. As setas, porém, vêm do recorte recente de `signal_history` do Monitor quando esse array não está vazio — ao vivo, SOL/USDT 1d tinha 32 operações na lista e só 9 marcadores. No BTC 1d o recorte inicial começa ~05/01/26; operações anteriores somem do viewport **e** da série se a origem for só o Monitor.

**Usuário:** operador que confere cada entrada e saída no mesmo período das velas, em qualquer ativo.
**Hipótese:** se as setas nascem da lista, o gráfico conta a mesma história ao afastar o zoom.
**Resultado:** 1:1 lista↔setas; zoom inicial recente; histórico antigo na série.

**Impeccable recorte (Operate):** clone da página viva `/combo/results` + delta das setas alinhadas à lista completa. Sem redesign de layout. Densidade: setas sempre na série; rótulo Compra/Venda só com viewport apertado (≤260 velas).

UI impact: affected
live_route: /combo/results
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

Regiões clonadas: shell AppNav autenticado; chrome `/combo/results` (`.combo-page`, «Voltar aos favoritos», `aria-label="Análise da estratégia"`, chips, resumo, regras); chrome do gráfico (Menos / Mais / Resetar, «180 velas»); chrome da «Lista de operações»; disclaimer. Catálogo (worktree): `selectors: [".combo-page"]`, `texts: ["Lista de operações", "Análise da estratégia"]` — confirmados no HTML vivo autenticado 2026-09-12.

## Goals / Non-Goals

**Goals:**

- Lista = todas as operações da janela da análise (abertas e fechadas).
- Gráfico marca cada operação da lista na vela certa (entrada; saída se fechada).
- 1:1 lista↔setas; qualquer ativo/timeframe nessa tela.
- Zoom inicial pode continuar no recorte recente; histórico antigo permanece na série e aparece com Menos / arrastar / afastar.
- Resetar volta o recorte sem apagar as setas da série.
- Operações do resumo bate com as linhas fechadas da lista.
- Catálogo T5 ganha `/combo/results`.

**Non-Goals:**

- Cards ao vivo do Monitor.
- Métricas de promoção da Descoberta.
- Redesenhar layout do gráfico ou da tabela.
- Excel extra.
- Forçar todas as velas visíveis ao abrir.

## Decisions

1. **Origem das setas = lista da análise.** `ComboResultsPage` deixa de preferir `signal_history` quando esse array tem itens. Marcadores = `buildTradeMarkers(result.trades, …)`. `signal_history` do Monitor MAY acrescentar só operação corrente não duplicada; NUNCA substitui a lista. Alternativa «unir e deixar o recorte ganhar» rejeitada: é o furo ao vivo (9 setas vs 32 linhas).

2. **Viewport inicial = últimas ~180 velas; série completa.** Já é o contrato de `StrategyChartSurface`. Apply não chama `fitContent()` no open. Setas antigas ficam em `setMarkers` da série inteira — o viewport é que as esconde. Alternativa «abrir em todas as velas» rejeitada (milhares de barras ilegíveis).

3. **Densidade sem cortar história.** Com muitas setas no zoom afastado: triângulos pequenos sempre; rótulo Compra/Venda só no recorte apertado. Mesma vela entrada+saída continua no collapse já existente. Alternativa «agrupar e esconder operações» rejeitada.

4. **Landmarks `/combo/results` neste Design.** HEAD hoje não tem a chave; T5 lê HEAD, então a chave no worktree só passa o gate depois de estar no HEAD desta branch. Autor não empresta `/favorites` nem `/combo/select`.

## Risks / Trade-offs

- [Risco] Timeframe baixo com centenas de setas cobre o preço → Mitigação: densidade (rótulo só no zoom apertado); série intacta.
- [Risco] T5 `load_head_catalog` ignora chave só no working tree → Mitigação: yaml neste change; commit da branch (pai) antes de `submeter_design`.
- [Risco] Spec antiga «inclui signal_history» lida como fonte exclusiva → Mitigação: delta `chart-visualization` + `favorites` + spec nova `analysis-complete-trade-history`.

## Migration Plan

Sem migração de schema. Rollback = reverter a origem dos marcadores. Favoritos já gravados não precisam de backfill.

## Apply contract

Apply lê este `design.md` e `frontend/public/prototypes/card-917-historico-completo-analise/index.html` como spec de UI. Sem HTML neste arquivo.

**Contrato visível (não P3):**

- `/combo/results`: lista completa; gráfico 1:1 com a lista; recorte inicial ~180 velas; Menos/arrastar revela setas antigas; Resetar não apaga a série.
- Resumo Operações = linhas fechadas da lista.
- Qualquer ativo/timeframe nessa tela.

**P3 detalhe de Apply (aceito, não reabrir como P0/P1):** nomes internos `buildTradeMarkers` / `signal_history`; MAE/MFE da tabela; canvas lightweight-charts vs SVG do proto.

## Prototype

- Canónico: `https://dev.criptofarol.com.br/prototypes/card-917-historico-completo-analise/` → `frontend/public/prototypes/card-917-historico-completo-analise/index.html`.
- Clone da página viva `/combo/results` (Favoritos «Ver análise completa») + delta das setas da lista completa (BTC/USDT 1d, 73 operações / 146 setas).
- 6 pares `COPIED:start`/`COPIED:end` · 7175 bytes copiados · 25579 bytes gerados · 32754 bytes totais.
- Landmarks: `.combo-page`, «Lista de operações», «Análise da estratégia».

## Prototype Validation

- URL: `https://dev.criptofarol.com.br/prototypes/card-917-historico-completo-analise/`
- Comando: Playwright Chromium headless, `1440×900` e `390×844`, `colorScheme: dark`, `networkidle`.
- Desktop e mobile (0 erros de console):
  - Estado padrão: `.combo-page`=1, «Lista de operações», `aria-label="Análise da estratégia"`, Operações=73, `data-marker-count=146`, `data-list-count=73`, «180 velas», `viewport-from=2026-01-05`, seta `2017-10-05` ausente, seta `2026-07-10` presente (12 marcadores visíveis).
  - Menos até a série toda: «2367 velas», `viewport-from=2017-08-17`, 73 Compra + 73 Venda, `data-time="2017-10-05"`=1, `data-marker-count` continua 146.
  - Resetar: «180 velas», seta 2017 oculta de novo, `data-marker-count` ainda 146.
- `curl` HTTP 200 não substitui este gate.
- Detector Impeccable no HTML: `[]`.

## Design Agent verdict

PASS — tokens parseáveis; proto clona `/combo/results` com COPIED>0 e landmarks vivos; browser gate desktop+mobile no estado padrão e no zoom que revela setas antigas. P0/P1 visíveis: nenhum.

## Design Critique

Com-tela. Teto 1+1+1: autor + dupla A/B; sem rework (zero P0/P1 de produto).

- Autor: [design-autor 917](ce6b5b46-e379-4b7d-b7a1-59e5bdd6c055) isolado; `model: cursor-grok-4.6-high`.
- Assessment A: [Assessment A 917](917f0295-facf-4c19-8d3c-46f7f8000d75) isolado; `model: cursor-grok-4.6-high`.
- Assessment B: [Assessment B 917](03ce2bb0-f410-466c-b194-78a3dfc2b16c) isolado; `model: cursor-grok-4.6-high`.
- Verdict: **PASS**. `No findings.` Tokens: `UI impact: affected` / `live_route: /combo/results` / `surface: existing`.
- Proto: https://dev.criptofarol.com.br/prototypes/card-917-historico-completo-analise/

P3 aceite (detalhe de Apply, não reabrir como P0/P1): SVG do proto vs lightweight-charts; MAE/MFE; nomes `buildTradeMarkers` / `signal_history`; mock BTC 1d no proto; rótulos no mobile em 180 velas; chrome «Roda do mouse» no touch.

### Proxies

- `design.md` words: 1130
- HTML generated vs copied: 25579 vs 7175
- Spawns: 3
- `proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)`
- `proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`
- `proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)`
