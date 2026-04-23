## Why

Backtests recentes precisam de histórico suficiente para gerar sinais e métricas confiáveis.  
Hoje, para símbolos recém-adicionados, o sistema frequentemente não tem janelas históricas de 2 anos no storage, comprometendo a qualidade do backtest.

## What Changes

- Incluir job de backfill histórico de OHLCV de 2 anos para novo ativo.
- Permitir execução manual e agendada do backfill.
- Implementar paginação no fetch histórico (janela por lotes) com retomada por cursor/cutoff.
- Aplicar throttle/budget de API (rate limiting + backoff + retry) durante backfill.
- Garantir idempotência por símbolo/timeframe/página/candle para evitar duplicidade e permitir rerun seguro.
- Expor progresso e estado no painel Admin com visibilidade por ativo, timeframe, etapa e erros.

## New / Modified Capabilities

### New

- `ohlcv-backfill-2y`: serviço e APIs para backfill de 2 anos por ativo recém-adicionado.
- `admin-backfill-monitor`: visualização de status/progresso/ETA de backfill no Admin.

### Modified

- `ohlcv-storage`: suporte explícito a cargas históricas em lote para onboarding de ativos.
- `job-manager`: gerenciamento de jobs no padrão assíncrono (status + progresso + pausa/cancelamento opcional).

## Impact

- Backend: criação de serviço de backfill, scheduler hooks, endpoints administrativos e persistência de progresso/checkpoint por job.
- Banco de dados: tabela/estrutura de estado de job (se necessário) e índices auxiliares para rastreio por ativo/timeframe.
- Admin UI: nova área de controle/monitoramento de jobs de backfill.

## Out of Scope

- Mudanças de estratégia de datasource em nível de pricing core (usa providers já existentes).
- Refatoração da infraestrutura completa de data pipelines fora do fluxo de novos ativos OHLCV.
- Mudança de retenção (a retenção atual de 2 anos é mantida).
