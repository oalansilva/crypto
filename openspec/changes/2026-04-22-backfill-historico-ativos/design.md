# Design

## Context

Hoje já existe um fluxo de ingestão contínua de OHLCV por timeframe e símbolo, mas sem um job dedicado de backfill histórico cobrindo janela longa no onboarding.  
A nova solução cria um job de operação assíncrona que usa as mesmas fontes de candle, com estado persistido e controle de execução para backfill em larga escala.

## Goals

- Garantir backfill automático de 2 anos para qualquer ativo novo (ou selecionado manualmente).
- Controlar volume de request por paginação + throttle para não saturar provider.
- Tornar o processamento seguro para reexecução (idempotente).
- Exibir progresso explícito no admin para operador acompanhar e retomar decisões.

## Non-Goals

- Implementar múltiplos provedores apenas para backfill (o provider atual continua o mesmo por configuração).
- Alterar estratégia de consulta da UI de backtest no mesmo release.

## Decisions

1. **Modelo de job único por `(symbol, provider, timeframe)`**
- Cada job é iniciado por ativo e inclui timeframes ativos para aquela fonte.
- O progresso é agregado por símbolo e detalhado por timeframe para fácil diagnóstico.

2. **Paginação temporal ascendente com checkpoint**
- O backfill percorre a janela de `agora - 24 meses` até `agora` em lotes ordenados por tempo.
- Cada lote grava um checkpoint persistente (último candle processado), permitindo retomar sem duplicar.

3. **Throttle por step de lote + backoff por resposta**
- Antes de cada chamada externa, validar budget de chamadas.
- Em caso de erro transitório (`429/5xx/network`), aplicar retry com jitter + exponencial.

4. **Idempotência dupla**
- Escrita de candle continua usando upsert por `(symbol, timeframe, candle_time)` como proteção primária.
- Estado de job também garante `completed / skipped / duplicated` para observabilidade de reruns.

5. **Admin progress model**
- Estado em memória + persistência: `pending/running/completed/failed/cancelled`.
- Exibir `processed`, `total_estimate`, `progress_percent`, `last_error`, `attempts`, `updated_at`.

## Risks / Trade-offs

- **Risco:** janela de 2 anos pode ser maior que o disponível no provider para alguns ativos.  
  **Mitigação:** aceitar histórico parcial com status `partial_complete` + erro explícito.
- **Risco:** backfill concorrente de muitos ativos no mesmo host pode atrasar outros jobs.  
  **Mitigação:** limitar paralelismo global e por provider.
- **Risco:** progresso total exato pode variar conforme a disponibilidade do histórico.  
  **Mitigação:** usar contadores `expected_estimate` + reconciliação final por contagem real.

## Open Questions

- Qual timezone padrão considerar no corte de janela? `UTC` por padrão para consistência.
- O job agendado de backfill deve rodar em cron fixo diário ou só ao detectar novos ativos? (Default sugerido: diário + gatilho manual em onboarding).
