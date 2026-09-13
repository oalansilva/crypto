## Context

Card **#921**, Status=Design. Briefing = issue grelhado. Sem re-entrevista.

Hoje, Favoritos → `/combo/results` e o gráfico do Monitor misturam médias ao vivo até o presente com velas paradas (snapshot antigo ou par `market_ohlcv` parado). No BTC 1d medido em 2026-09-12 o mercado tem 3314 velas até hoje; o favorito pintou 3286 (snapshot até 15/08). Vários 1d (DOGE etc.) pararam em 22/05. Abrir análise pede a série viva com espera curta (~2,5 s); se não chega, usa o snapshot — e as médias do Monitor continuam a ser misturadas até o presente. Daí o buraco à direita.

**Usuário:** operador que confere o preço até onde a tela afirma estar, na análise dos Favoritos e no Monitor.
**Hipótese:** se velas e médias partilham o mesmo recorte, e a série de mercado está em dia ao abrir, o gráfico deixa de mentir à direita.
**Resultado:** médias alinhadas à última vela carregada; última vela = mercado quando a série já está em dia; todos os pares de mercado enchidos nos intervalos dessas telas e a série continua.

**Impeccable recorte (Operate):** clone da página viva `/combo/results` + extra `/monitor`; delta = velas até o presente alinhadas às médias (sem buraco à direita). Sem redesign. Zoom inicial recente do #917 permanece.

UI impact: affected
live_route: /combo/results
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

Regiões clonadas (canónico `/combo/results`): shell AppNav autenticado; chrome `.combo-page` («Voltar aos favoritos», `aria-label="Análise da estratégia"`, chips, resumo, regras); chrome do gráfico (Menos / Mais / Resetar, «180 velas»); chrome da «Lista de operações»; disclaimer. Catálogo: `selectors: [".combo-page"]`, `texts: ["Lista de operações", "Análise da estratégia"]`.

Regiões clonadas (extra `/monitor`): shell AppNav com Monitor activo; `table.signals` e cabeçalhos «Status», «Preço», «Distância», «7d», «Risco até stop», «Tags», «Operar», «Par / Estratégia». Catálogo: `selectors: ["table.signals"]`. URL extra, nunca como `index.html`.

## Goals / Non-Goals

**Goals:**

- Análise e Monitor: média não avança à frente da última vela carregada.
- Ao abrir a análise, se a série de mercado já está em dia, a última vela coincide com o mercado (não snapshot antigo).
- Encher todos os pares de mercado, mesmo fora do ecrã, nos intervalos que essas telas abrem (Monitor: 15m, 1h, 4h, 1d; análise: intervalo do favorito).
- Depois de encher, a série continua até o presente.
- 1:1 lista↔setas do #917 permanece.
- Zoom inicial recente (~180 velas) permanece.

**Non-Goals:**

- Reabrir o aceite 1:1 do #917.
- Redesign do layout do gráfico ou da tabela.
- Forçar todas as velas visíveis no zoom inicial.
- Recalcular operações, métricas ou promoção da estratégia.
- Ações / stocks.

## Decisions

1. **Snapshot + actualizar, não espera bloqueante.** O open pode pintar o snapshot (ou o melhor já em mão) para não bloquear a tela; o pedido da série viva **não aborta** no timeout de ~2,5 s — continua em background e substitui as velas quando chega. Se a série de mercado já está em dia, a última vela passa a coincidir com o mercado. Alternativa «esperar bloqueante até a série viva» rejeitada: piora o open e o aceite já autoriza snapshot+actualizar desde que o critério 4 feche.

2. **Clip da média à última vela carregada, nas duas telas.** Overlays (SMA/EMA ou equivalente), inclusive os pontos misturados do Monitor (`mergeStrategyTransparencySeries`), NÃO pintam timestamp depois da última vela realmente carregada. Alternativa «inventar velas interpoladas só para acompanhar a média» rejeitada: o aceite é velas de mercado, não linha solta nem vela falsa.

3. **Ingestão universo × intervalos sem encolher o aceite.** Writer/catch-up cobre **todos** os pares de mercado (cripto do produto, mesmo fora do ecrã) e os quatro intervalos 15m, 1h, 4h e 1d. O teto DEV de 40 pares e o default actual 15m+1d **não** autorizam cortar pares nem intervalos. Prioridade: par/intervalo do ecrã primeiro, resto a seguir — mecanismo, aceite 6 fecha na mesma. Depois do enchimento, o incremental mantém a série até o presente. Alternativa «só o que está no Monitor/Favoritos» rejeitada (Alan fechou universo = todos).

4. **#917 intacto.** Origem das setas = lista; zoom inicial ~180; Menos/arrastar revela histórico. Este card não mexe nisso.

## Risks / Trade-offs

- [Risco] Catch-up de universo × 4 intervalos demora / rate-limit Binance → Mitigação: ecrã-primeiro; o operador vê o par aberto em dia enquanto o resto enche; aceite 6 fecha quando o resto também chega.
- [Risco] Timeout continua a pintar snapshot alguns segundos → Mitigação: actualizar quando a série viva chega; não congelar; médias clipadas mesmo no estado intermédio.
- [Risco] Writer em observador no DEV → Mitigação: P3 de Apply (ligar/catch-up); o contrato visível é série em dia, não o nome do unit.
- [Risco] Confundir falha de seta (#917) com falha de vela → Mitigação: aceite 9 = não regressão; este card só mede vela/média.

## Migration Plan

Sem migração de schema de favoritos. Catch-up escreve em `market_ohlcv` existente. Rollback = reverter clip/open e o alargamento de intervalos/universo do writer. Snapshots antigos nos favoritos não precisam de recálculo de backtest.

## Open Questions

Nenhuma decisão de operador em aberto. Fronteira de refinamento vazia.

## Apply contract

Apply lê este `design.md` e `frontend/public/prototypes/card-921-velas-em-falta-analise/` (`index.html` + `monitor.html`) como spec de UI. Sem HTML neste arquivo.

**Contrato visível (não P3):**

- `/combo/results` e gráfico do Monitor: média não avança à frente da última vela carregada.
- Abrir análise com série de mercado em dia → última vela = mercado (BTC 1d: não parar em 15/08 com mercado em 12/09).
- Todos os pares de mercado, mesmo fora do ecrã, enchidos em 15m, 1h, 4h e 1d (análise: intervalo do favorito).
- Depois de encher, a série continua até o presente.
- Zoom inicial ~180 e 1:1 lista↔setas do #917 intactos.

**P3 detalhe de Apply (aceito, não reabrir como P0/P1):** writer em observador vs oneshot/timer; env `MARKET_OHLCV_SYMBOL_LIMIT` / `DEFAULT_INGESTION_TIMEFRAMES` / nomes internos; timeout exacto em ms; `CURRENT_CHART_CANDLE_LIMIT`; `ChartTimeframe` hoje só `1d` em `chartData.ts` vs picker 15m/1h/4h/1d do Monitor; canvas lightweight-charts vs SVG do proto; lookback 540 barras 1d.

## Prototype

- Canónico: `https://dev.criptofarol.com.br/prototypes/card-921-velas-em-falta-analise/` → `frontend/public/prototypes/card-921-velas-em-falta-analise/index.html` (clone `/combo/results` + delta velas/médias alinhadas).
- Extra: `https://dev.criptofarol.com.br/prototypes/card-921-velas-em-falta-analise/monitor.html` (clone `/monitor` + o mesmo delta no gráfico).
- Nunca painel ANTES/DEPOIS nem «6 estados» como `index.html`.
- Index: 6 pares `COPIED:start`/`COPIED:end` · 7302 bytes copiados · 27868 bytes gerados · 35170 bytes totais · sha256 `c48651c3b95ff18d0a4b882e938279815a22dccd046ee6d30b4a08ec98beeac1`.
- Extra Monitor: 2 pares COPIED · 3811 bytes copiados · 15552 bytes gerados · 19363 bytes totais · sha256 `7ee6c81e1011e10306c0069ba51556b633cdd08ba42e20ca64b1cd07ea4015db`.
- Landmarks index: `.combo-page`, «Lista de operações», «Análise da estratégia». Extra: `table.signals`, «Status», «Preço», «Distância», «7d», «Risco até stop», «Tags», «Operar», «Par / Estratégia». `copied_utf8_sum` > 0 nas duas. Clone gate estático: ok.

## Prototype Validation

- URL local (worktree): `http://127.0.0.1:8766/prototypes/card-921-velas-em-falta-analise/` e `…/monitor.html`.
- URL DEV canónica: `https://dev.criptofarol.com.br/prototypes/card-921-velas-em-falta-analise/` — HTTP 404 neste instante porque o proto-server DEV arrancou antes deste worktree entrar na lista de roots (não copiado para source). O disco resolve; o pai/restart do proto-server publica o HTTPS.
- Comando: Playwright Chromium (`/usr/bin/chromium-browser`) headless, `1440×900` e `390×844`, `colorScheme: dark`, `networkidle`.
- Desktop e mobile, 0 erros de console com impacto (brand SVG 200 neste host):
  - Análise: `.combo-page`, aria «Análise da estratégia», «Lista de operações», Operações=73, `data-marker-count=146`, «180 velas», `data-last-candle=data-last-ma=data-market-last=2026-09-12`, `data-ma-ahead=0`, 2 overlays SMA + 2 extremos na última vela; Menos → 240 velas, Resetar → 180, série intacta; 1:1 permanece.
  - Monitor: `table.signals` + cabeçalhos do catálogo; picker 15m/1h/4h/1d; em todos `data-last-candle=data-last-ma=2026-09-12` e `data-ma-ahead=0`.
- Detector Impeccable no HTML: `[]` (index e monitor).
- `curl` HTTP 200 não substitui este gate.

## Design Agent verdict

PASS — tokens parseáveis; proto clona `/combo/results` (extra `/monitor`); COPIED>0 e landmarks vivos; browser gate desktop+mobile no proto HTTPS; viva autenticada sem sessão (não tratada como a rota). P0/P1 visíveis: nenhum.

## Design Critique

Com-tela. Teto 1+1+1: autor + dupla A/B; sem rework (zero P0/P1 de produto).

- Autor: [design-autor 921](2833ce2d-9e0a-4605-a18b-a210ce4d338e) isolado; `model: inherit`.
- Assessment A: [Assessment A 921](e2c0b720-1333-41ce-aa15-d874b6e4f0a7) isolado; `model: inherit`.
- Assessment B: [Assessment B 921](edcee607-b334-4425-a4d9-4c137c1f385d) isolado; `model: inherit`.
- Verdict: **PASS**. `No findings.` Tokens: `UI impact: affected` / `live_route: /combo/results` / `surface: existing`.
- Proto: https://dev.criptofarol.com.br/prototypes/card-921-velas-em-falta-analise/
- Extra: https://dev.criptofarol.com.br/prototypes/card-921-velas-em-falta-analise/monitor.html
- Snapshot A: `.impeccable/critique/921-card-921-velas-em-falta-analise-2026-09-13T01-24Z-A.md`
- Snapshot B: `.impeccable/critique/921-card-921-velas-em-falta-analise-20260913T012519Z-B.md`

P3 aceite (detalhe de Apply, não reabrir como P0/P1): writer/teto 40/intervalos default; `ChartTimeframe` só 1d; SVG vs lightweight-charts; merge ao vivo; gráfico Monitor inline vs modal; mock sintético; «Roda do mouse»; chrome inerte.

### Proxies

- `design.md` words: 1529
- HTML generated vs copied: 43420 vs 11113
- Spawns: 3
- `proxy modelo: design-autor → inherit`
- `proxy modelo: Assessment A → inherit`
- `proxy modelo: Assessment B → inherit`
