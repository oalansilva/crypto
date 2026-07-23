## Why

Com `CRYPTO_CANDLES_CANONICAL_MODE` ativo e fallback direto desligado, o Monitor ficou preso na última vela persistida (ex.: 16/07) porque o writer canônico nunca foi implantado como serviço periódico. O fallback direto em DEV mitiga o sintoma, mas não substitui um único writer observável por ambiente.

## What Changes

- Implantar exatamente um writer canônico periódico por ambiente (DEV agora; PROD via units/instalador prontos no release), fora da API.
- Integrar instalação/enable do timer ao `./restart` DEV e documentar o caminho PROD equivalente.
- Expor atraso (lag) por símbolo/timeframe em métricas/runtime status e emitir alerta quando a última vela ultrapassar a tolerância.
- Fazer a API marcar respostas degradadas (stale + lag) em vez de entregar candles antigos silenciosamente.
- Manter fallback direto apenas como contingência explícita (`CRYPTO_CANDLES_DIRECT_FETCH_FALLBACK`).
- Limitar escopo/frequência via env configurável (`MARKET_OHLCV_SYMBOLS`, `MARKET_OHLCV_TIMEFRAMES`, limites existentes).
- Cobrir com testes: writer incremental, exclusão mútua, lag/alerta e fallback/degraded.

## Capabilities

### New Capabilities
- `canonical-candle-continuity`: writer canônico contínuo por ambiente, integração com restart, sinalização de degradação/lag na API e observabilidade operacional.

### Modified Capabilities
- `ohlcv-storage`: reforçar que a ingestão contínua de `market_ohlcv` é responsabilidade do writer dedicado (não da API), com limites configuráveis.

## Impact

- `restart`, `install-candle-writer-*.sh`, `ops/systemd/*candle-writer*`
- `backend/scripts/run_canonical_candle_writer_once.py`
- `backend/app/services/ohlcv_storage.py`, `runtime_status.py`, `canonical_candle_service.py`
- `backend/app/api.py` (`/api/market/candles`, métricas)
- `docs/runtime-architecture.md`
- testes unitários/integração de writer, API e lag
