## Context

O card #1086 está em Design. O briefing copiado está em `proposal.md`. Em `combo_strategy.py`, `dc_upper` é `high.rolling(N).max()`: inclui o candle avaliado, cujo fechamento não supera a própria máxima. A expressão atual do template exige justamente `close > dc_upper`. Os testes do #1074 verificam execução/coluna de sinais, sem exigir compras.

UI impact: none
live_route: N/A — correção da decisão de entrada no backend, sem mudança de tela ou copy.
surface: none

## Goals / Non-Goals

**Goals:** reconhecer rompimento do canal anterior com volume confirmado; registrar compra real no backtest; provar ausência de entrada nos casos negativos e causalidade em 4h, 1h e 15m; preservar demais templates e indicadores.

**Non-Goals:** mudar thresholds de aprovação, taxa, slippage, promoção de favoritos, saída, stop loss, timeframes disponíveis ou Status Homologado do #1074. Não recalcular resultados históricos nem reescrever estratégias salvas de usuários.

## Decisions

### Corrigir a expressão do template

Trocar exclusivamente a referência de entrada em `backend/config/combo_templates_export.json` para `(close > dc_upper.shift(1)) & (volume > vol_avg)`. Em t, o canal passa a representar `max(high[t-N:t])`, com t excluído. O avaliador existente aceita `shift`; `test_combo_strategy_logic_parser.py` já cobre esse método. Não criar indicador, parâmetro, coluna derivada ou regra especial baseada no nome do template.

Alternativa rejeitada: deslocar globalmente as bandas Donchian em `ComboStrategy`. Isso mudaria consumidores existentes e também `dc_middle`, alterando a saída `close < dc_middle` fora do pedido. A solução escolhida preserva as três bandas, aliases, cache e saída.

### Preservar confirmação e execução

`vol_avg` permanece SMA do volume com período e multiplicador existentes, incluindo o volume do candle avaliado. No padrão: período 20 e multiplicador 1,2, comparação estrita `volume > vol_avg`. Deslocar também a média de volume seria outra estratégia.

Exigir N candles anteriores completos; referência ausente não autoriza entrada. Com índice iniciado em zero, o primeiro candle potencial é t=N. Decidir no fechamento de t; `ComboStrategy` mantém a entrada pendente e o sinal em t+1, executado na abertura de t+1. Não adicionar um segundo atraso. Sem candle seguinte disponível, não inventar execução.

### Provar compra no caminho da Descoberta

Usar o template carregado do export e OHLCV determinístico, parametrizado para 4h, 1h e 15min. Exercitar `ComboStrategy.generate_signals` e o extrator real `extract_trades_from_signals` de `combo_optimizer.py`, usado pelo caminho de backtest da Descoberta. Não mockar sinais nem extrator. Produzir uma saída posterior controlada, pois o extrator retorna operações encerradas. A operação deve conter `type=long`, `entry_signal_type=Comprar`, horário t+1 e preço de abertura correspondente.

Fixture base: N=20, máximas anteriores 100, volumes anteriores 100, fechamento de rompimento 101 e volume 200. A média confirmadora é 126 no candle de rompimento; máxima atual acima de 101 não participa da referência. Variantes isoladas: fechamento 100; abaixo de 100; máxima acima de 100 com fechamento abaixo; rompimento com volume 100; warmup insuficiente. Cada variante deve terminar sem operação comprada atribuída ao candle avaliado. Evitar outros rompimentos nas fixtures negativas.

Validar também outro N para comprovar uso do período configurado. Alterar somente a máxima atual preservando fechamento/volume deve manter a decisão. Alterar candles após t não muda a decisão em t; comparar sinais até t+1. Para comparar preço de execução, manter a abertura de t+1 fixa: o preço depende legitimamente dessa abertura. Não exigir igualdade de saídas ou lucros afetados pelo futuro.

### Distribuição pelo mecanismo existente

`startup_seed.py` já atualiza `donchian_volume_breakout` via `CARD_1074_TEMPLATE_NAMES` em tabela populada; o seed inicial lê o mesmo export. Verificar os dois caminhos sem criar migração de schema ou nova rotina de atualização. Testes de persistência usarão PostgreSQL isolado conforme overlay. Não executar seed nem escrita no banco durante Design.

## Risks / Trade-offs

- Alteração do indicador compartilhado ampliaria o impacto → limitar o delta à expressão e comparar bandas/saída e os outros templates com a baseline.
- Teste apenas de sinal mascararia falta de compra → exigir registro real do extrator com saída controlada, incluindo os caminhos fast e legacy existentes.
- A carga persistida poderia continuar antiga → verificar seed inicial e atualização idempotente do catálogo existente; nenhuma alteração dos outros registros além do comportamento atual do seed.
- Resultados Donchian mudarão em novos backtests → efeito esperado da correção; sem promessa de rentabilidade ou alteração de critérios de aprovação.

## Migration Plan

No Apply, validar export, parser, backtest e carga do catálogo. Na integração autorizada posterior, o ciclo habitual do backend carrega o export pelo seed existente. Rollback restaura a expressão anterior e repete esse mecanismo; não exige DDL. Resultados já calculados e estratégias copiadas anteriormente permanecem como estavam.

## Prototype

N/A — não há superfície visual alterada. HTML gerado: N/A. HTML copiado: N/A.

## Impeccable

N/A — correção de lógica do backend sem alteração de tela, copy ou interação. Design e aprovação humana continuam obrigatórios.

## Open Questions

Nenhuma decisão de produto pendente. Detalhes de organização das fixtures e do teste de seed são P3 aceitos para resolver no Apply.

## Design Critique

- P0–P2: nenhum.
- P3: nos negativos, verificar ausência de sinal de compra em t+1 além da ausência de trade encerrado; lista vazia pode esconder posição aberta.
- disposition: aceito como detalhe de Apply; nenhum rework necessário.
- verdict: PASS de conteúdo; comprovação de runtime recuperada dos traces locais de autor e crítico, ambos gpt-6-astra/medium e completed com payload. Proxies validados com successful=true.
