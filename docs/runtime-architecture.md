# Arquitetura runtime do Crypto stack

## Objetivo

Este documento define o runtime operacional do Cripto Farol na VPS atual. A regra central e manter boot leve por padrao e deixar cada rotina pesada com dono, flag, log e verificacao propria.

## Topologia oficial

| Componente | Responsabilidade | Default | Ativacao |
| --- | --- | --- | --- |
| PostgreSQL | Banco runtime e workflow | Obrigatorio | `DATABASE_URL` e `WORKFLOW_DATABASE_URL` PostgreSQL |
| Redis | Broker/cache operacional | Ligado pelo `start.sh` | `start.sh` |
| Backend FastAPI | API, schema leve, rotas e leitura do produto | Ligado | `./start.sh` / services systemd |
| Frontend Vite preview | UI do produto | Ligado | `./start.sh` / services systemd |
| Candle writer canonico | Buscar candles Binance e gravar em `market_ohlcv` | Timer de ambiente | DEV: `./restart` instala/enable; PROD: installer no release |
| Backfill historico | Preencher historico longo sob demanda | Desligado | admin/API ou `BACKFILL_SCHEDULER_ENABLED=1` |
| Binance realtime prices | Snapshot/precos/top pairs, nao candles | Desligado | `BINANCE_REALTIME_WORKER_ENABLED=1` ou `BINANCE_REALTIME_ENABLED=1`, mas nao ambos |
| Runtime worker generico | Signal monitor, snapshot worker e refresh de favoritos | Desligado | `CRYPTO_RUNTIME_WORKER_ENABLED=1` + rotina `RUN_*` |
| Celery batch | Batch backtests assincronos | Desligado | `CRYPTO_CELERY_WORKER_ENABLED=1` |

## Ordem de startup

1. PostgreSQL disponivel.
2. Redis local (quando aplicavel ao stack legado).
3. Migrations Alembic.
4. Backend FastAPI.
5. Frontend.
6. Candle writer dedicado via timer de ambiente (um por DEV/PROD).
7. Backfill, realtime, runtime worker e Celery somente por flags explicitas.

## Flags principais

| Flag | Default | Efeito |
| --- | --- | --- |
| `CRYPTO_CANDLES_CANONICAL_MODE` | `1` | API usa `market_ohlcv` como fonte canonica. |
| `CRYPTO_CANDLES_DIRECT_FETCH_FALLBACK` | `0` | Contingencia: permite fallback direto para Binance no request. |
| `CRYPTO_CANDLES_WRITER_ENABLED` | `0` | Identifica processo autorizado a escrever candles. So o writer dedicado liga. |
| `MARKET_OHLCV_INGESTION_ENABLED` | `0` | Liga ingestion continua dentro do backend. Manter `0` na API. |
| `MARKET_OHLCV_TIMEFRAMES` | `15m,1d` | Timeframes do writer/ingestion. |
| `MARKET_OHLCV_SYMBOLS` | vazio | Lista explicita de simbolos; vazio resolve universo Binance USDT. |
| `MARKET_OHLCV_SYMBOL_LIMIT` | `40` no writer | Limite padrao do timer para proteger a VPS; override via env. |
| `MARKET_OHLCV_MAX_LAG_SECONDS_<TF>` | derivado do timeframe | Threshold de alerta de atraso por timeframe. |
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
- resolve pares spot USDT ativos da Binance, salvo `MARKET_OHLCV_SYMBOLS` ou `MARKET_OHLCV_SYMBOL_LIMIT`;
- roda incrementalmente a partir do ultimo candle salvo, com overlap configuravel por `CRYPTO_CANDLES_INCREMENTAL_OVERLAP_CANDLES`;
- usa lock exclusivo por ambiente (`/tmp/crypto-candle-writer-dev.lock` ou `...-prod.lock`);
- grava estado (`...-state.json`) com status, runs, duracao e `lag_alerts`;
- nao sobe runtime worker, Celery nem Binance realtime;
- API em modo canonico marca payload degradado (`degraded=true`, `data_source=market_ohlcv-stale`, `lag_seconds`) quando a ultima vela passa da tolerancia.

### DEV (obrigatorio no restart)

```bash
# Canonico: ./restart no source DEV instala/enable o timer
/srv/apps/dev/criptofarol/source/restart

# Manual
./install-candle-writer-systemd.sh --env dev
systemctl status criptofarol-dev-candle-writer.timer --no-pager
systemctl list-timers criptofarol-dev-candle-writer.timer --no-pager
journalctl -u criptofarol-dev-candle-writer.service -n 100 --no-pager
```

### PROD (somente no release)

```bash
cd /srv/apps/prod/criptofarol/source
./install-candle-writer-systemd.sh --env prod
systemctl status criptofarol-prod-candle-writer.timer --no-pager
```

Para desligar:

```bash
systemctl disable --now criptofarol-dev-candle-writer.timer
# ou
systemctl disable --now criptofarol-prod-candle-writer.timer
```

O installer legado `install-candle-writer-systemd-user-timer.sh` permanece apenas como caminho opcional legado; o caminho operacional canonico e o system timer por ambiente.

## Logs e evidencias

| Item | Evidencia |
| --- | --- |
| Backend DEV | service `criptofarol-dev-backend` / porta `8004` |
| Frontend DEV | service `criptofarol-dev-frontend` / porta `5175` |
| Candle writer DEV | `/tmp/crypto-candle-writer-dev.log` + `/tmp/crypto-candle-writer-dev-state.json` |
| Candle writer PROD | `/tmp/crypto-candle-writer-prod.log` + `/tmp/crypto-candle-writer-prod-state.json` |
| Runtime status DEV | `curl -fsS http://127.0.0.1:8004/api/runtime/status` |
| Candles metrics DEV | `curl -fsS http://127.0.0.1:8004/api/market/candles/metrics` |
| Health API DEV | `curl -fsS http://127.0.0.1:8004/api/health` |
| Health UI DEV | `curl -fsS http://127.0.0.1:5175/` |

## Verificacao anti-duplicidade Binance

Com defaults da API, estes comandos nao devem listar processos pesados na API:

```bash
pgrep -af "python -m app.workers.runtime_worker|celery .*app.celery_app:celery_app worker|python -m app.binance_realtime_worker" || true
curl -fsS http://127.0.0.1:8004/api/runtime/status
```

Para verificar candle writer DEV:

```bash
cat /tmp/crypto-candle-writer-dev-state.json
systemctl status criptofarol-dev-candle-writer.timer --no-pager
systemctl status criptofarol-dev-candle-writer.service --no-pager
```

Se `lock_held=true` em `/api/runtime/status`, ja existe writer ativo. Nao iniciar outro writer manual ate o run atual terminar.
