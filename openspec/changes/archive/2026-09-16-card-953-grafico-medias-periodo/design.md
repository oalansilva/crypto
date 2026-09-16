## Context

Card **#953**, Status=Design. Briefing = issue grelhado (DoD completo; ritual `grill-card fronteira vazia`; Q2 aceite = B). Não reentrevista.

Hoje, análise pelos Favoritos e gráfico do Monitor pintam as velas do período já carregado, mas as linhas da estratégia — médias de preço e as outras que aquele gráfico já desenha — não cobrem esse mesmo histórico: some, para no meio, ou só existe no pedaço recente. #921 fechou o inverso (linha à frente da última vela). #917 fechou zoom recente e 1:1 lista↔setas. #949 (não reabrir) fechou o período operacional do favorito.

**Impeccable recorte (Operate):** audience = operador que lê preço e indicadores juntos; outcome = velas e linhas no mesmo recorte nas duas telas; direction = clone da página viva + delta das linhas no histórico carregado, sem redesign; scope = `/combo/results` canónico, extra `/monitor`.

UI impact: affected
live_route: /combo/results
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

Regiões clonadas (canónico `/combo/results`): shell AppNav autenticado; chrome `.combo-page` («Voltar aos favoritos», `aria-label="Análise da estratégia"`, chips, resumo, regras); chrome do gráfico (Menos / Mais / Resetar, «180 velas»); chrome da «Lista de operações»; disclaimer. Catálogo HEAD: `selectors: [".combo-page"]`, `texts: ["Lista de operações", "Análise da estratégia"]`. `COPIED:start` / `COPIED:end` nessas regiões.

Regiões clonadas (extra `/monitor`): shell AppNav com Monitor activo; `table.signals` e cabeçalhos «Status», «Preço», «Distância», «7d», «Risco até stop», «Tags», «Operar», «Par / Estratégia». Catálogo HEAD: `selectors: ["table.signals"]`. URL extra `monitor.html`, nunca como `index.html`. Sem chave nova no catálogo.

## Goals / Non-Goals

**Goals:**

- Análise e Monitor: velas e linhas da estratégia no mesmo recorte carregado — médias no preço **e** as outras linhas que aquele gráfico já desenha (painel de baixo incluído).
- Recorte = velas já carregadas. Favorito 6 meses / 2 anos **não** alarga para todo o mercado.
- Zoom inicial ~180 permanece. Ao abrir, o recorte visível já tem linha (depois do aquecimento). Ao afastar / Menos / arrastar, as velas antigas da série também têm linha. Resetar volta ao recorte recente sem apagar as linhas da série.
- #917 1:1 intacto. #921 sem linha à frente da última vela. #949 período do favorito intacto.
- Vale noutro ativo / intervalo dessas telas.

**Non-Goals:**

- Reabrir o aceite de #921, #917 ou #949.
- Alargar 6 meses / 2 anos para todo o mercado só para «completar» indicadores.
- Abrir já enquadrado em todas as velas.
- Redesign do layout do gráfico ou da tabela.
- Recalcular operações, métricas ou promoção da estratégia.
- Inventar média ou outra linha que a estratégia não usa.
- Esconder de novo as linhas no Monitor.
- Ações / stocks.

## Decisions

1. **Recorte das linhas = velas já carregadas, não o mercado inteiro.**
   6 meses / 2 anos ficam 6 meses / 2 anos. Alternativa «alargar o favorito para todo o mercado para aquecer as médias» recusada na grelha (rodada 1).

2. **Linhas = médias de preço e as outras que o gráfico daquela estratégia já desenha (Q2 = B).**
   Painel de baixo incluído quando o manifesto da estratégia o declara (RSI/MACD/ADX/ATR/volume de indicador). Não se inventa linha. Alternativa «só médias» recusada (não foi a recomendada).

3. **Leitura ao abrir = zoom recente; linhas já na série.**
   Enquadrado inicial ~180. Afastar / Menos / arrastar revela velas antigas **com** linha. Recorte visível ao abrir já tem linha após aquecimento. Alternativa «abrir enquadrado no período inteiro» recusada.

4. **Estado final visível, open não bloqueia (P3 de Apply).**
   Velas podem aparecer primeiro; o estado que o operador aceita é velas e linhas no mesmo recorte. Aquecimento (primeiras N−1 velas de uma linha de período N sem valor) **não** é o furo. Clip #921 permanece: nenhum ponto de linha depois da última vela carregada.

## Risks / Trade-offs

- [Risco] Apply só estende SMA/EMA de preço para a frente (código actual `extendMovingAverageSeriesToCandles`) e deixa o histórico antigo e o painel de baixo furados → Mitigação: aceite = todas as linhas que o gráfico daquela estratégia já desenha, no recorte das velas carregadas; Q2 = B.
- [Risco] Completar linhas alargando 6 meses / 2 anos para 2017 → Mitigação: proto da análise é favorito **2 anos** (16/09/2024 → 16/09/2026), não 17/08/2017; spec #949 intacto.
- [Risco] Abrir já em todas as velas «para ver as linhas» → Mitigação: chip «180 velas» ao abrir; Resetar volta a esse recorte.
- [Risco] Inventar RSI/MACD numa estratégia só de médias → Mitigação: análise canónica = Virada (SMA 9 e SMA 21, o que ela já usa) + volume do gráfico vivo; extra Monitor demonstra o painel de baixo duma estratégia que o gráfico já desenha (MACD).
- [Risco] Reabrir buraco à direita (#921) ao preencher o histórico → Mitigação: clip à última vela continua; `data-ma-ahead="0"`.

## Migration Plan

Sem migração de schema de favoritos. Rollback = voltar a pintar linhas só no extremo recente. Sem recálculo de backtest/métricas. Sem backfill do período do favorito.

## Apply contract

Apply lê este `design.md` e o HTML em `frontend/public/prototypes/card-953-grafico-medias-periodo/` (`index.html` + `monitor.html`) como spec de layout. Sem HTML neste arquivo. Sem editar produto neste filho de Design.

**Contrato visível (não P3):**

- `/combo/results` (favorito 2 anos): série de velas 16/09/2024 → 16/09/2026; **não** 17/08/2017. SMA 9 e SMA 21 calculadas nesse histórico. Zoom ao abrir ~180 velas, com linha no recorte visível (após aquecimento). Menos / afastar / arrastar: velas de 2024 também têm linha. Resetar: volta a ~180, linhas da série permanecem. Último ponto de linha = última vela (`data-ma-ahead="0"`). 1:1 lista↔setas. Chip «Favorito 2 anos · não todo o mercado».
- Gráfico `/monitor`: o mesmo recorte velas↔linhas na série já carregada; zoom ~180; ao afastar, velas antigas têm linha; linha não avança à frente da última vela. Timeframe 15m/1h/4h/1d não alarga para «todo o mercado». Painel de baixo da estratégia seleccionada (MACD na linha SOL) cobre o mesmo recorte. Linhas **não** são escondidas.
- 6 meses / 2 anos não viram «todo». Outro ativo (SOL) e outro intervalo (1h) nas duas telas.
- Aquecimento visível nas primeiras velas da SMA 21: ausência ali **não** conta como linha em falta.

**P3 — detalhe de Apply (aceito aqui, não reabrir como P0/P1):**

- Cálculo sobre velas carregadas: recompute integral da série vs estender/preencher buracos do manifesto; `extendMovingAverageSeriesToCandles` hoje só SMA/EMA de `panel=price` e só para a frente.
- Warmup: primeiras N−1 velas sem valor.
- Clip #921 (`clipStrategyTransparencyToLoadedCandles` / `maPointsAheadOfLastCandle`) permanece.
- Indicadores que não são SMA/EMA de preço (RSI/MACD/ADX/ATR/volume de manifesto / bandas).
- Velas primeiro, linhas a seguir, sem bloquear o open.
- Canvas lightweight-charts vs SVG do proto; nomes `analysis_indicator_data`, `strategy_transparency`, `CURRENT_CHART_CANDLE_LIMIT`.
- Detector Impeccable `side-tab` / alvos 32px nos ícones da linha — incumbente do clone.
- Mock sem loading/vazio/erro de rede.

## Prototype

- Canónico: `https://dev.criptofarol.com.br/prototypes/card-953-grafico-medias-periodo/` → `frontend/public/prototypes/card-953-grafico-medias-periodo/index.html`. Clone da página viva `/combo/results` (incumbente proto #921) + delta: linhas no histórico das velas carregadas (favorito 2 anos, não todo o mercado; zoom 180; Menos revela 2024 com linha; clip #921).
- Extra: `https://dev.criptofarol.com.br/prototypes/card-953-grafico-medias-periodo/monitor.html` — clone `/monitor` + o mesmo delta; painel de baixo MACD na estratégia que o gráfico já o desenha.
- `cp`/clone = copied; delta de recorte/linhas/painel = generated.
- Sem painel ANTES/DEPOIS como URL canónica. Nunca um painel das N no index.

## Prototype Validation

Playwright Chromium (headless) 2026-09-16 contra HTTPS canónico `https://dev.criptofarol.com.br/prototypes/card-953-grafico-medias-periodo/` + extra `monitor.html`. Desktop 1440×900 e mobile 390×844. curl 200 não substitui. Browser MCP do host não manteve tab; verificação = Playwright no mesmo HTML.

- **index (estado padrão + delta):** landmarks `/combo/results` (`.combo-page`, «Lista de operações», `aria-label="Análise da estratégia"`). Chip **2 anos · 16/09/2024 → 16/09/2026**. 731 velas carregadas; ao abrir **180 velas** com SMA 9/21; `data-ma-ahead="0"`; `data-whole-market="0"`; sem 17/08/2017. Menos ×2 → 320 velas; Menos até ao fundo → **731 velas**, `viewportFrom=2024-09-16`, `linesOnOld=1`, path SMA presente. Resetar → 180. Lista 16 · setas 32 (1:1). Desktop = mobile no recorte 180 e no chip de período.
- **monitor.html:** `table.signals` com «Par / Estratégia», «Status», «Preço», «Distância», «7d», «Risco até stop», «Tags», «Operar». 731 velas carregadas (1d), zoom 180; Menos → 320; clip `data-ma-ahead="0"`. Clique SOL: painel de baixo **Painel macd: MACD** visível, 2 paths no mesmo recorte. Linhas não escondidas.

Impeccable Operate: clone #921 + delta. Tokens Binance (`--accent #fcd535`, `--bg-primary #0b0e11`). Sem P0/P1 de produto no autor.

Verdict autor: **PASS**.

## Open Questions

Nenhuma. Fronteira veio grelhada; Q2 = B. *Como* calcular (P3) não é option de operador.

## Design Critique

Com-tela. Teto 1+1+1: autor + dupla A/B. Sem rework (zero P0 novo de produto). P3 aceitos; pai submete.

- Autor: [design-autor 953](5c5164ec-6288-4ce9-9a25-8452e5ea2ee6) isolado; `model: cursor-grok-4.6-high`.
- Assessment A: [Assessment A 953](b698bf60-4000-41b0-9168-b9af0cfb9981) isolado; `model: cursor-grok-4.6-high`. **PASS**.
- Assessment B: [Assessment B 953](f9440586-03b9-435e-9084-f9ead4160cc5) isolado; `model: cursor-grok-4.6-high`. **PASS**.
- Verdict: **PASS**. Tokens: `UI impact: affected` / `live_route: /combo/results` / `surface: existing`.
- Proto: https://dev.criptofarol.com.br/prototypes/card-953-grafico-medias-periodo/
- Extra Monitor: https://dev.criptofarol.com.br/prototypes/card-953-grafico-medias-periodo/monitor.html
- Snapshot A: `.impeccable/critique/953-card-953-grafico-medias-periodo-assessment-A.md`
- Snapshot B: `.impeccable/critique/953-card-953-grafico-medias-periodo-assessment-B.md`

- **P0:** nenhum
- **P1:** nenhum
- **P2:** nenhum
- **P3** aceito (Apply, não reabrir): detector `flat-type-hierarchy` no extra Monitor
- **P3** aceito: warmup SMA N−1; clip #921; canvas vs SVG
- **P3** aceito: nav 42px / Operar 36px; alvos 32px; gráfico baixo no mobile; thead clip a 390px
- **P3** aceito: labels Compra/Venda sobrepostas no recorte 180; mobilebar BTC estático ao mudar para SOL
- **P3** aceito: `TRADES` 2017 no JS (lista filtra); `DELTA:start=0`; datas EN na lista
- **P3** aceito: mock senóide no Monitor; mock sem loading/vazio/6m
- **P3** aceito: recompute vs extend; indicadores não-SMA; open sem bloquear
- **Disposition:** P3 aceites no Apply. Sem rework.

### Proxies

- `design.md` words: 1737
- HTML generated vs copied: 13599 vs 10369
- Spawns: 3
- `proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)`
- `proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`
- `proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)`

Design Agent verdict: PASS
