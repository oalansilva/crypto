## Context

Cards #241/#242 criaram armazenamento canônico (`market_ohlcv`), modo canônico na API, script one-shot com lock/state e templates systemd user. Em operação, o timer nunca ficou ativo; a API com canonical mode + fallback off passou a servir velas antigas como se fossem atuais. DEV mitigou com `CRYPTO_CANDLES_DIRECT_FETCH_FALLBACK=1` no drop-in do backend.

## Goals / Non-Goals

**Goals:**
- Um writer periódico por ambiente, observável (lock, state, logs, runtime status).
- DEV: installer + `./restart` garantem timer ativo após reboot.
- PROD: units/instalador versionados prontos; ativação no release (não nesta implementação).
- API informa `degraded`/`stale` + `lag_seconds` quando a última vela ultrapassa tolerância.
- Métricas/alerta de lag por símbolo/timeframe.
- Escopo configurável para não sobrecarregar a VPS.

**Non-Goals:**
- Reescrever o pipeline CCXT/`market_ohlcv`.
- Ligar writer dentro do processo uvicorn.
- Ativar writer em PROD nesta entrega.
- Remover o fallback direto (permanece contingência explícita).

## Decisions

1. **Systemd system units por ambiente (não só user timer)**  
   DEV/PROD já rodam como system services root. User timers do card 242 dependem de linger/sessão e hoje não existem.  
   → Adicionar `criptofarol-dev-candle-writer.service/.timer` e templates PROD equivalentes + instaladores. Manter o script one-shot existente.

2. **API sem writer embutido**  
   `CRYPTO_CANDLES_WRITER_ENABLED=0` e `MARKET_OHLCV_INGESTION_ENABLED=0` na API. Só o unit do writer seta `CRYPTO_CANDLES_WRITER_ENABLED=1`. Lock file evita duplicidade se algo errado iniciar dois writers.

3. **Restart DEV garante o timer**  
   `./restart` no path canônico DEV chama o instalador/enable do timer DEV (idempotente) além de backend/frontend. Assim reboot + restart preservam atualização.

4. **Sinalização de degradação na API**  
   Corrigir o caminho canônico que hoje devolve stale com `data_source=market_ohlcv` sem flags. Quando não fresco: `data_source=market_ohlcv-stale`, `degraded=true`, `lag_seconds`, `fresh=false`. Fallback direto só se `CRYPTO_CANDLES_DIRECT_FETCH_FALLBACK=1`.

5. **Lag alert**  
   Reusar thresholds `MARKET_OHLCV_MAX_LAG_SECONDS_*` / defaults do ingestion. Writer state e `/api/market/candles/metrics` + runtime status expõem freshness/lag agregado. Log warning com `event=ohlcv_ingestion_lag_alert` (já existe; garantir cobertura no one-shot e métricas).

6. **Limites de carga**  
   Defaults seguros: `MARKET_OHLCV_TIMEFRAMES=15m,1d`; `MARKET_OHLCV_SYMBOLS` / `MARKET_OHLCV_SYMBOL_LIMIT` já existentes; timer `OnUnitInactiveSec=15min`.

## Risks / Trade-offs

- [Carga Binance/VPS] → limites de símbolos/timeframes + intervalo do timer; não habilitar ingestion na API.  
- [Duplicidade writer] → lock exclusivo + API com writer disabled.  
- [PROD sem writer ainda] → units prontos; ativação só no release; DEV valida o contrato.  
- [Fallback ligado em DEV] → após writer estável, fallback pode voltar a 0; nesta change documentar, não forçar remoção do drop-in sem validação.

## Migration Plan

1. Merge em `develop` + `./restart` (instala/enable timer DEV).  
2. Rodar um ciclo do writer; validar BTC/USDT e outro símbolo no Monitor.  
3. Confirmar runtime status / metrics / state file.  
4. No release: instalar timer PROD no path `/srv/apps/prod/criptofarol/source`.

Rollback: `systemctl disable --now criptofarol-dev-candle-writer.timer` e, se necessário, manter fallback direto.

## Open Questions

- Nenhum bloqueante: ativação PROD fica para o lote/release.
