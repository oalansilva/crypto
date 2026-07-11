## Context

O estado público do Monitor combina análise atual, `is_holding`, trades armazenados na favorita e marcadores visíveis. Hoje uma saída é tratada como autoritativa apenas por ser o evento mais recente em `metrics.trades`; não há garantia de que seu timestamp esteja coberto pelos candles da análise. No frontend, um marcador de saída visível também pode substituir a resolução da posição. O caso do card #280 apresentou saída posterior ao último candle persistido.

## Goals / Non-Goals

**Goals:**

- Definir uma fronteira temporal única para validar eventos de entrada/saída.
- Impedir que evento futuro ou fora da cobertura force posição fechada.
- Fazer backend, badge, mensagem e marcadores compartilharem a mesma resolução válida.
- Cobrir o comportamento com testes determinísticos, sem I/O de mercado.
- Preservar componentes e tokens atuais do `DESIGN.md` em desktop/mobile.

**Non-Goals:**

- Alterar parâmetros, lógica de cruzamento ou stop das estratégias.
- Declarar paridade com TradingView quando template/parâmetros diferem.
- Criar novo status público além de `HOLD`/`EXIT`.
- Redesenhar o Monitor.

## Decisions

### 1. Validar trades contra a cobertura de candles antes de resolver o último evento

O backend derivará o primeiro e o último timestamp válidos de `analysis_candles`. Eventos de trade posteriores ao último candle serão ignorados. Um evento cached também será ignorado quando for anterior ao sinal calculado mais recente, evitando que uma saída stale sobrescreva uma nova entrada. Eventos fora de uma cobertura conhecida não poderão ser a única evidência autoritativa para sobrescrever a análise atual.

Alternativa rejeitada: corrigir apenas o badge no frontend. Isso deixaria API, Telegram, mensagem e posição divergentes.

### 2. Não persistir silenciosamente refresh temporalmente incoerente

O deep backtest deixará de transformar `end_of_period` em uma saída `signal_15m` no dia seguinte ao último candle. Posição ainda aberta no fim do período não será persistida como trade realizado. Stop intraday realmente observado continua fechando o trade. O refresh também validará que eventos persistidos não excedem a cobertura dos candles retornados; se a origem continuar incoerente, falhará sem substituir métricas válidas anteriores.

Alternativa rejeitada: truncar datas futuras sem conhecer a semântica da execução, pois isso inventaria um candle de venda.

### 3. Marcadores não substituem uma posição por evidência temporalmente inválida

O endpoint de oportunidades será a fonte canônica do card/linha. O endpoint de trades serve ao gráfico e histórico, sem reclassificar de forma assíncrona `Compra` para `Venda`. No modal, marcador de saída só prevalece quando estiver no intervalo de candles e for compatível com uma resolução explícita de saída. Entrada ativa sem saída válida permanece `Compra`; fallback não cria venda contraditória.

Alternativa rejeitada: remover todos os fallbacks. Eles ainda são úteis quando não existe histórico recuperável.

### 4. Preservar linguagem e tokens existentes

Compra continua usando `#0ecb81`, venda `#f6465d`, canvas `#0b0e11` e superfícies `#1e2329`, conforme `DESIGN.md`. A mudança é de coerência funcional, sem novo componente visual.

## Risks / Trade-offs

- [Histórico antigo sem candles armazenados pode perder autoridade] → manter fallback da análise atual e classificar incerteza, sem fabricar saída.
- [Timestamps de execução intraday podem não coincidir exatamente com candle 1D] → validar por cobertura temporal e normalização de candle/timeframe, não por igualdade textual.
- [Correção apenas na leitura deixa dado inválido persistido] → adicionar validação no refresh e teste de não regressão.
- [TradingView usa configuração diferente] → validar resultado DEV com configuração exata da favorita e documentar a diferença.
