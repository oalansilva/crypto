## Context

Card **#1070**, Status=Design. Briefing = issue grelhado (Problema, História, Entra, Não entra). Sem reentrevista. As decisões fechadas no body não se reabrem.

O #1045 diagnostica, bloqueia e não promove geometria. Em DEV o scalp está ligado, o Jev responde ~30 s, `Calibração 0/25989`, zero `scalp cycle sent`. `SCALP_REGIME_BOUNDARY_BP` não está preenchida: todo ciclo sai `market_regime=unknown` → `regime_closed`. `_fee_terms` lê maker e o interruptor BNB mas **não aplica** o desconto: a tela diz «BNB habilitado; desconto não aplicado». `last_trade_quote` é o P&L de preço `(saída − entrada) × qty` sem descontar as taxas das duas pernas (`fees_quote` vai só ao P&L do dia). No fim do prazo a saída é MARKET sem teto (`scalp-aggressive-exit`). A régua mede barreiras em OHLCV com buracos: 23/23 alternativas indeterminadas no relatório de 29/09. Os 200 do #1045 são janelas ao vivo; ao vivo há 1 elegível.

A superfície do operador já é `/monitor`, módulo Scalp BTCUSDT (`ScalpModule`). Board e Operar ficam. Só mudam os textos de estado, taxa e P&L.

UI impact: affected
live_route: /monitor
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

Regiões clonadas: shell autenticado + workbench `/monitor` (`table.signals`, Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia) no **index.html**. `COPIED:start`/`COPIED:end` nessas regiões. Delta fora desses blocos: textos de estado, taxa («desconto aplicado») e P&L líquido por trade no módulo Scalp BTCUSDT já existente, e o diagnóstico a falar de alvo, stop, prazo e recorte juntos com a confiança. Sem extras. O index não é um painel de estados.

## Goals / Non-Goals

**Goals:**

- Resolver alvo, stop e prazo pelo caminho real de preço (aggTrades ou candles de 1 s completos). Amostra só com modelo e origem da confiança identificados. Nas janelas de 29/09, <5% das alternativas indeterminadas.
- Replay offline com aggTrades históricos, a mesma decisão do `scalp_engine`, taxas reais da conta. ≥200 janelas independentes por regime numa execução, sem o log ao vivo.
- Aplicar o desconto de BNB no hurdle e na tela quando o saldo de BNB cobre a taxa; a tela diz «desconto aplicado». Taxa na tela e no hurdle = taxa cobrada no fill.
- No fim do prazo: limitadora primeiro; mercado só como último recurso, com teto de derrapagem.
- Promover só geometria com retorno líquido por trade positivo e intervalo de confiança acima de zero no backtest. Prazo pode alongar além de 15 min. Geometria em uso fica até achar uma que pague. Diagnóstico diário promove e reverte alvo, stop, prazo, recorte de regime e confiança juntos.
- Não desligar o filtro de confiança para operar às cegas. Quando o conjunto pagar, calibrar a confiança reportada à escala real.
- Fronteira de regime calculada da volatilidade do backtest, mesma escala da decisão, gravada na versão.
- Os 200 contam-se no backtest. Lucro líquido exigido = backtest. Com a versão promovida, DEV envia post-only de 10 dólares e fecha compra→venda. A primeira volta pode perder; o P&L líquido por trade aparece na tela.
- Copy no `/monitor`: estado, taxa, P&L. Sem redesenhar a board.

**Non-Goals:**

- Operar com fronteira ou confiança abertas antes do backtest provar lucro líquido.
- Aumentar T ou clip; saque.
- PROD (T16). Trocar exchange ou par.
- Refazer o Monitor além dos textos de estado, taxa e P&L.
- Desligar o filtro de confiança.
- Encerrar o card com recusa visível enquanto neste par não houver geometria com lucro líquido.
- Rota nova, landing, Ajuda.

## Decisions

1. **A superfície é o `/monitor` que já tem o scalp.** Delta só de copy no `ScalpModule` (estado, taxa, P&L líquido por trade e frases do diagnóstico). Board e Operar ficam. Alternativa rejeitada — página nova ou painel de estados: a rota não está no catálogo e o index canónico não pode ser um painel.

2. **Os 200 e o lucro líquido exigido vivem no backtest offline.** Novo corredor `scripts/scalp_jev_backtest.py` (nome de Apply): baixa/cacheia aggTrades históricos BTCUSDT da Binance, reconstrói `state` no mesmo schema do `scalp_jev_payload`, corre a mesma `decide_cycle` / gates do `scalp_engine`, e chama o Jev com o modelo da versão identificada (respostas em cache por hash do estado). Só entram respostas com `model` e origem da confiança declarados. Janelas sem sobreposição. ≥200 independentes **por regime** numa execução. A régua `scalp_jev_eval.py` continua somente leitura e não escreve produto. Alternativa rejeitada — contar os 200 no log ao vivo: o body diz que ao vivo leva anos. Alternativa rejeitada — só repricar o log de 5 dias: não produz 200 elegíveis.

3. **Caminho de preço das barreiras.** Para cada janela, o primeiro toque de alvo vs stop vs fim de prazo lê-se na série de aggTrades (preço e tempo do trade). Se a série de aggTrades tiver lacuna, candles de **1 s completos** no mesmo intervalo. OHLCV de 1 m / 5 m / 15 m **não** decide barreira. Indeterminado só se o caminho real também não distinguir. Critério: nas janelas de 29/09, <5% das alternativas indeterminadas. Alternativa rejeitada — interpolar OHLCV: é o furo do relatório.

4. **Taxa: desconto uma vez, quando o BNB cobre.** `_fee_terms` já lê maker conservador (BUY/SELL × standard/tax/special) e `spotBNBBurn`, sem subtrair BNB — para não aplicar duas vezes. Este card aplica o desconto **uma vez** quando: desconto BNB habilitado na conta e no símbolo, `spotBNBBurn` ligado, e `BNB.free` × preço BNB ≥ taxa estimada do clip (10 dólares). `fee_bp` passa a ser a taxa com desconto (25% sobre o maker considerado, ou `discountRate` da comissão se vier no payload). Hurdle = `2 × fee_bp + spread_bp`. Tela: «N bp · desconto aplicado». Se o saldo não cobre, `fee_bp` sem desconto e a tela **não** diz desconto aplicado. Depois do fill, a taxa cobrada (asset da commission do fill) tem de bater com a taxa em uso; desvio visível no diagnóstico, não silêncio. Alternativa rejeitada — mostrar «BNB habilitado; desconto não aplicado» com o interruptor ligado: o body pede «desconto aplicado» quando o saldo cobre.

5. **P&L líquido por trade.** `last_trade_quote` = P&L de preço da volta **menos** a taxa da perna de compra **menos** a taxa da perna de venda, ambas em quote. `last_trade_bp` na mesma base. A tela rotula esses dois números «P&L líquido» / «P&L líquido US$». Perda tão visível quanto ganho. O KPI P&L do dia continua a incluir taxas (já inclui `fees_quote`). Alternativa rejeitada — deixar o último trade em bruto e o líquido só no dia: o critério observável pede o líquido **por trade** na tela.

6. **Fim do prazo: limitadora, depois teto.** No primeiro ciclo em que o prazo aplicado (hold após fill) termina com posição aberta, o bot **não** manda MARKET. Cancela a saída passiva de alvo/stop se ainda estiver no livro e posta uma **limitadora post-only** no lado realizável (venda no bid / compra no ask). Se essa limitadora não fechar, o último recurso é LIMIT IOC com preço limitado pelo **teto de derrapagem** gravado na versão (10 bp sobre o mid do toque fresco — *como*, não decisão de operador). Não há MARKET sem preço. Se o livro já está além do teto, não envia nesse ciclo e tenta de novo a limitadora no seguinte; «posição presa» aparece no analogado de prazo+30 s. Alternativa rejeitada — MARKET sem teto no fim da janela: o body pede limitadora primeiro e teto.

7. **Um prazo aplicado, cadência intacta.** O prazo promovido é um só número: janela rolante de aggTrades (`horizon_s`), janela de barreira e hold após fill. O facto no ecrã é «últimos N min» desse prazo. A cadência Jev continua `JEV_TARGET_MS` (30 s). Sem rádio 1/2/5. Enquanto não houver versão com prazo, vale 15 min (geometria em uso). Alternativa rejeitada — alongar só o hold e deixar lookback em 15 min: a fronteira de regime e o `vol_bp` deixariam de estar na mesma escala.

8. **Promoção do conjunto, nunca filtro desligado para encher.** Uma impressão digital de versão inclui: política de confiança por regime (numérica, na escala calibrada), fronteira de `vol_bp`, alvo, stop, prazo, taxa considerada. Promove só se o retorno líquido médio por janela independente da geometria, no backtest, tiver o limite inferior do intervalo de confiança 95% (bootstrap BCa da média) **acima de zero**. Não se grava `off` na confiança para obter fills. Se o conjunto não pagar, a geometria em uso fica e o card continua a varrer a grelha (`GEOMETRY_TARGET_CANDIDATES_BP` × `GEOMETRY_STOP_CANDIDATES_BP` × prazos 15 min, 1 h, 4 h, 24 h e, se nenhum pagar, prazos seguintes na mesma progressão). A calibração da confiança, quando o conjunto paga, é um mapa monótono gravado na versão (confiança bruta do modelo → [0, 1] da política), para deixar de comparar 0,0–0,3 com 0,7. Alternativa rejeitada — desligar o filtro: o body proíbe operar às cegas.

9. **Fronteira calculada, fail-closed até existir.** Sobre as janelas independentes do backtest com `vol_bp`, a fronteira é o corte único na mesma unidade que `window.vol_bp` que parte calmo/activo (mediana da amostra elegível; se um regime ficar abaixo de 200, o corte desloca-se o mínimo para os dois lados terem 200, ou o regime sem 200 fica fechado). Grava-se na versão. Enquanto a versão não tiver fronteira, os dois regimes continuam fechados (`regime_closed`). Não se preenche `SCALP_REGIME_BOUNDARY_BP` à mão. Alternativa rejeitada — abrir a fronteira vazia para o scalp comprar: o body diz que isso perde dinheiro.

10. **DEV confirma; o lucro exigido não muda.** Depois da promoção, com interruptor ligado, a primeira ordem é post-only de **10 dólares** (o clip já é ≤ US$ 10; T e clip não sobem). Fecha compra→venda pela geometria aplicada. `last_trade_*` líquidos aparecem mesmo negativos. O diagnóstico do dia seguinte pode promover ou reverter o conjunto conforme a prova do dia (mesmo corredor de preço e a mesma regra de lucro líquido). Alternativa rejeitada — exigir lucro na primeira volta DEV: o body diz que pode perder e ainda conta.

11. **O card não acaba sem geometria que pague neste par.** Apply não marca as tasks de promoção/ciclo como encerradas com recusa visível. Se a grelha dessa corrida não tiver CI > 0, alarga prazo e volta a medir. Geometria em uso permanece. Alternativa rejeitada — Done técnico com «não operável»: o body proíbe encerrar assim.

## Risks / Trade-offs

- [Chamadas Jev no backtest são caras] → Cache por hash do estado + modelo. Sem cache, a execução única ainda tem de produzir os 200 por regime; o Apply mede tempo e persiste o cache no disco do worktree, não no produto.
- [A primeira volta DEV perde] → Esperado. O líquido exigido continua o do backtest. A tela mostra a perda.
- [Teto de derrapagem deixa a posição aberta] → Limitadora de novo no ciclo seguinte; «posição presa» no prazo+30 s; Operar continua. Não há MARKET sem preço.
- [Mapa de confiança mal calibrado] → Só se grava quando o conjunto já tem CI > 0; o filtro numérico não se desliga.
- [Dois workers aplicam a mesma versão] → A impressão digital única do #1045 alarga-se ao conjunto; a mesma digital não aplica duas vezes.

## Migration Plan

- Alembic na mesma base das versões do #1045: a linha de versão ganha alvo, stop, prazo, fronteira, mapa de confiança e teto de derrapagem. Sem backfill que invente fronteira: sem versão, fail-closed.
- Calibração continua a nascer como o #1045 a deixou; ligá-la não liga o interruptor.
- Rollback de produto: reverter a versão anterior (conjunto inteiro). Posição aberta sai como estava.
- PROD só por T16. Este change não publica PROD.

## Open Questions

Nenhuma. As decisões de operador estão fechadas na grelha de 29/09. O *como* acima (BCa 95%, teto 10 bp, mediana de `vol_bp`, mapa monótono, LIMIT IOC com preço) não reabre essas decisões.

## Prototype

- Canónico: `https://dev.criptofarol.com.br/prototypes/card-1070-scalp-jev-lucro-liquido/` → `frontend/public/prototypes/card-1070-scalp-jev-lucro-liquido/index.html`. Clone da página viva `/monitor` (base proto #1045 = `MonitorStatusTab` + `ScalpModule` vigentes) + delta só nos textos de estado, taxa e P&L do módulo scalp. Landmarks: `table.signals`, Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia. `COPIED:start`/`COPIED:end` nas regiões clonadas.
- Vista canónica (index.html vivo, `data-state="on"`): interruptor **Ligado**; lookback **últimos 60 min**; taxa **7,5 bp · desconto aplicado**; hurdle **15,1 bp**; alvo **+20 bp** / stop **−14 bp** (versão aplicada, não escolhida no chat); P&L líquido por trade **−12,4 bp** / **−US$ 0,18** (perda visível; o P&L do dia mostra o mesmo −US$ 0,18); clip ≤ US$ 10; primeira volta DEV de US$ 10 fechada. Diagnóstico 29 set 2026: **Apliquei** alvo, stop, prazo e recorte juntos com a confiança; amostra >200 janelas por recorte no backtest; lucro líquido exigido continua o do backtest (intervalo acima de zero); versão 14. Ajuste automático Ligada 1/1. Sem rota nova. Sem landing/Ajuda.

## Prototype Validation

- **URL canónica:** `frontend/public/prototypes/card-1070-scalp-jev-lucro-liquido/index.html`. Sem HTML irmão. T5 mede só este index.
- **Digest (UTF-8 sha256):** `index.html` `c2d0fee40fa6bd2c8b3c4028addf6033307c67d4c80fcf678f41436bc1ca2b9f` · 58181 B = 21077 copied + 37104 generated. Pares `COPIED:start`/`COPIED:end`: 10/10; soma UTF-8 copiada 21077 (> 0). `design_clone_gate.classify` = PASS; landmarks `/monitor` ok. `clone_gate_ok` local True.
- **browser_gate:** a dupla A/B abre a URL pública depois do pai publicar. O autor não spawna crítico.

## Impeccable

Operate, refinamento do incumbente `/monitor`. Sem mundo visual novo. Delta só de copy no módulo scalp (estado, taxa, P&L). Tokens e board clonados. A secção de crítica no `design.md` fica para o pai depois da dupla; este autor não a escreve.

## Design Critique

Passagem depois da invalidação do protótipo. Dupla A/B de novo. Zero P0/P1. Sem rework.

- P2: 12 células e o diagnóstico aberto empurram a board; o P&L do dia repete o −US$ 0,18 do P&L líquido por trade; dois switches Ligado/Ligada; kill e posição presa sem aria-live. Não bloqueiam.
- P3: fixtures do proto, contraste do P&L, 7d visível como Gráfico, modal Operar ausente, tabela mobile em cards, testids de hurdle/P&L ausentes. Aceito para o Apply.

Disposition: P0/P1 nenhum. P2 não bloqueia. P3 aceito no Apply.

Design Agent verdict: PASS

Snapshot: `.impeccable/critique/1070-card-1070-scalp-jev-lucro-liquido-A.md` e `.impeccable/critique/1070-card-1070-scalp-jev-lucro-liquido-B.md`

proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)
proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)
proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)
