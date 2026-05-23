# Arquitetura runtime do Crypto stack

## Objetivo

Este documento define o runtime operacional do Cripto Farol na VPS atual. A regra central e manter boot leve por padrao e deixar cada rotina pesada com dono, flag, log e verificacao propria.

## Topologia oficial

| Componente | Responsabilidade | Default | Ativacao |
| --- | --- | --- | --- |
| PostgreSQL | Banco runtime e workflow | Obrigatorio | `DATABASE_URL` e `WORKFLOW_DATABASE_URL` PostgreSQL |
| Redis | Broker/cache operacional | Ligado pelo `start.sh` | `start.sh` |
| Backend FastAPI | API, schema leve, rotas e leitura do produto | Ligado | `./start.sh` |
| Frontend Vite preview | UI do produto | Ligado | `./start.sh` |
| Candle writer canonico | Buscar candles Binance e gravar em `market_ohlcv` | Desligado | comando manual ou timer opt-in |
| Backfill historico | Preencher historico longo sob demanda | Desligado | admin/API ou `BACKFILL_SCHEDULER_ENABLED=1` |
| Binance realtime prices | Snapshot/precos/top pairs, nao candles | Desligado | `BINANCE_REALTIME_WORKER_ENABLED=1` ou `BINANCE_REALTIME_ENABLED=1`, mas nao ambos |
| Runtime worker generico | Signal monitor, snapshot worker e refresh de favoritos | Desligado | `CRYPTO_RUNTIME_WORKER_ENABLED=1` + rotina `RUN_*` |
| Celery batch | Batch backtests assincronos | Desligado | `CRYPTO_CELERY_WORKER_ENABLED=1` |

## Ordem de startup

1. PostgreSQL disponivel.
2. Redis local.
3. Migrations Alembic.
4. Backend FastAPI.
5. Frontend.
6. Candle writer somente por timer/comando opt-in.
7. Backfill, realtime, runtime worker e Celery somente por flags explicitas.

## Flags principais

| Flag | Default | Efeito |
| --- | --- | --- |
| `CRYPTO_CANDLES_CANONICAL_MODE` | `1` | API usa `market_ohlcv` como fonte canonica. |
| `CRYPTO_CANDLES_DIRECT_FETCH_FALLBACK` | `0` | Permite fallback direto para Binance no caminho de request quando ligado. |
| `CRYPTO_CANDLES_WRITER_ENABLED` | `0` | Identifica processo autorizado a escrever candles. Usado pelo writer dedicado. |
| `MARKET_OHLCV_INGESTION_ENABLED` | `0` | Liga ingestion continua dentro do backend. Evitar na VPS pequena. |
| `MARKET_OHLCV_TIMEFRAMES` | `15m,1d` | Timeframes do writer/ingestion. |
| `BACKFILL_SCHEDULER_ENABLED` | `0` | Liga scheduler de backfill historico. |
| `BINANCE_REALTIME_WORKER_ENABLED` | `0` | Liga worker externo de precos/top pairs. |
| `BINANCE_REALTIME_ENABLED` | `0` | Liga connector realtime dentro do backend. Nao usar junto com o worker externo. |
| `CRYPTO_RUNTIME_WORKER_ENABLED` | `0` | Habilita familia runtime worker, mas ainda exige rotina `RUN_*`. |
| `CRYPTO_CELERY_WORKER_ENABLED` | `0` | Liga Celery para fila `batch_backtest`. |

## Candle writer canonico

O candle writer oficial usa:

```bash
cd backend
CRYPTO_CANDLES_WRITER_ENABLED=1 \
CRYPTO_CANDLES_CANONICAL_MODE=1 \
CRYPTO_CANDLES_DIRECT_FETCH_FALLBACK=0 \
MARKET_OHLCV_TIMEFRAMES=15m,1d \
./.venv/bin/python scripts/run_canonical_candle_writer_once.py
```

Comportamento esperado:

- usa `market_ohlcv`;
- resolve todos os pares spot USDT ativos da Binance, salvo `MARKET_OHLCV_SYMBOLS` ou `MARKET_OHLCV_SYMBOL_LIMIT`;
- roda incrementalmente a partir do ultimo candle salvo, com overlap configuravel por `CRYPTO_CANDLES_INCREMENTAL_OVERLAP_CANDLES`;
- usa lock em `CRYPTO_CANDLES_WRITER_LOCK_FILE` ou `/tmp/crypto-candle-writer.lock`;
- grava estado em `CRYPTO_CANDLES_WRITER_STATE_FILE` ou `/tmp/crypto-candle-writer-state.json`;
- nao sobe runtime worker, Celery nem Binance realtime.

Para instalar timer systemd user opt-in:

```bash
./install-candle-writer-systemd-user-timer.sh
systemctl --user status crypto-candle-writer.timer --no-pager
systemctl --user list-timers crypto-candle-writer.timer --no-pager
journalctl --user -u crypto-candle-writer.service -n 100 --no-pager
```

Para desligar o timer:

```bash
systemctl --user disable --now crypto-candle-writer.timer
systemctl --user stop crypto-candle-writer.service
```

## Logs e evidencias

| Item | Evidencia |
| --- | --- |
| Backend | `/tmp/crypto-uvicorn-8003.log` |
| Frontend | `/tmp/crypto-vite-5173.log` |
| Candle writer | `/tmp/crypto-candle-writer.log` |
| Runtime worker | `/tmp/crypto-runtime-worker.log` |
| Celery | `/tmp/crypto-celery-worker.log` |
| Binance realtime worker | `/tmp/crypto-binance-realtime-worker.log` |
| Runtime status | `curl -fsS http://127.0.0.1:8003/api/runtime/status` |
| Candles metrics | `curl -fsS http://127.0.0.1:8003/api/market/candles/metrics` |
| Health API | `curl -fsS http://127.0.0.1:8003/api/health` |
| Health UI | `curl -fsS http://127.0.0.1:5173/` |

## Verificacao anti-duplicidade Binance

Com defaults, estes comandos nao devem listar processos pesados:

```bash
pgrep -af "python -m app.workers.runtime_worker|celery .*app.celery_app:celery_app worker|python -m app.binance_realtime_worker" || true
curl -fsS http://127.0.0.1:8003/api/runtime/status
```

Para verificar candle writer:

```bash
cat /tmp/crypto-candle-writer-state.json
systemctl --user status crypto-candle-writer.timer --no-pager
systemctl --user status crypto-candle-writer.service --no-pager
```

Se `lock_held=true` em `/api/runtime/status`, ja existe writer ativo. Nao iniciar outro writer manual ate o run atual terminar.
