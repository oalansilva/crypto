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
| Celery batch | Lotes de backtest (Combo e Otimização), fila `batch_backtest` | Ligado no DEV e no PROD por unit dedicada (#1120); o `start.sh` legado segue desligado | `CRYPTO_CELERY_WORKER_ENABLED=1` no worker dedicado `criptofarol-<env>-batch-worker.service` |
| Discovery dispatcher | Republicar intents duráveis da outbox | Ligado no DEV; PROD via unit dedicado | `RUN_DISCOVERY_OUTBOX_DISPATCHER=1` em worker dedicado |
| Celery discovery | Consumir sweeps da fila `discovery` | Ligado no DEV; PROD via unit dedicado | `CRYPTO_DISCOVERY_CELERY_WORKER_ENABLED=1` em worker dedicado |

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
| `ASSET_CATALOG_REFRESH_ENABLED` | `1` | Liga a atualizacao periodica do catalogo de ativos (Binance e acoes/ETFs). Desligada sob pytest. |
| `ASSET_CATALOG_REFRESH_INTERVAL_SECONDS` | `21600` | Intervalo entre atualizacoes do catalogo por classe de ativo (6 h). |
| `ASSET_CATALOG_MIN_RESULT_RATIO` | `0.5` | Descarta a atualizacao se a nova lista tiver menos que essa fracao dos ativos anteriores. |
| `BACKFILL_SCHEDULER_ENABLED` | `0` | Liga scheduler de backfill historico. |
| `BINANCE_REALTIME_WORKER_ENABLED` | `0` | Liga worker externo de precos/top pairs. |
| `BINANCE_REALTIME_ENABLED` | `0` | Liga connector realtime dentro do backend. Nao usar junto com o worker externo. |
| `CRYPTO_RUNTIME_WORKER_ENABLED` | `0` | Habilita familia runtime worker, mas ainda exige rotina `RUN_*`. |
| `CRYPTO_CELERY_WORKER_ENABLED` | `0` | Identifica o worker Celery da fila `batch_backtest` (a unit dedicada `criptofarol-<env>-batch-worker.service` o liga). |
| `RUN_DISCOVERY_OUTBOX_DISPATCHER` | `0` | Liga a republicação periódica da outbox de discovery. |
| `CRYPTO_DISCOVERY_CELERY_WORKER_ENABLED` | `0` | Identifica o worker Celery da fila `discovery`. |

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
- le os cripto negociaveis do catalogo de ativos (salvo `MARKET_OHLCV_SYMBOLS` ou `MARKET_OHLCV_SYMBOL_LIMIT`); sem catalogo e sem exchangeInfo a rodada nao roda;
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

O mesmo `./restart` instala e valida os workers dedicados da descoberta:

```bash
systemctl status criptofarol-dev-runtime-worker.service --no-pager
systemctl status criptofarol-dev-discovery-worker.service --no-pager
journalctl -u criptofarol-dev-discovery-worker.service -n 100 --no-pager
systemctl status criptofarol-dev-batch-worker.service --no-pager
journalctl -u criptofarol-dev-batch-worker.service -n 100 --no-pager
```

### Worker dos lotes (`batch_backtest`, #1120)

Toda fila publicada em `celery_app.task_routes` precisa de um worker próprio que a consuma com `-Q`; a fila `batch_backtest` ficou parada em DEV e PROD até o #1120 ganhar o seu (o teste `backend/tests/unit/test_celery_queue_consumers.py` falha se faltar). O worker dos lotes é separado do da Descoberta e os dois rodam ao mesmo tempo:

| Unit (template em `ops/systemd/`) | Fila | Pool | Teto de memória | Parada |
| --- | --- | --- | --- | --- |
| `criptofarol-dev-batch-worker.service` | `batch_backtest` | `solo`, `--concurrency=1 --prefetch-multiplier=1`, hostname `batch-dev@%h` | 3 GiB aviso, 4 GiB corte | `KillMode=mixed`, `TimeoutStopSec=300s` |
| `criptofarol-prod-batch-worker.service` | `batch_backtest` | idem, `batch-prod@%h` | 4 GiB aviso, 5 GiB corte | idem |

- Ambiente: `backend/.env`, `DISCOVERY_RESOURCE_PROFILE=<env>` e `DISCOVERY_INTERNAL_WORKERS=1` (o otimizador do lote dimensiona o pool de processos e o spool pelo mesmo perfil da Descoberta: 1 worker, pico medido de 1,70 GiB), spool próprio em `/var/tmp/criptofarol-<env>-batch` (nunca o da Descoberta) e `CRYPTO_CELERY_WORKER_ENABLED=1`. Mesmos `Restart=on-failure`, `RestartSec=60`, `StartLimitBurst=3/900 s`, `OOMPolicy=kill` e `MemorySwapMax=512M` da Descoberta.
- Parada: o SIGTERM vai só ao processo principal do Celery (`KillMode=mixed`), que no pool `solo` termina o lote em curso antes de sair, sem sinalizar os processos filhos do otimizador (com `control-group` eles morreriam e o item falharia). Passados 300 s o systemd mata o grupo. O lote cortado não se perde: a tarefa é `acks_late`, a reentrega mantém o mesmo `task_id` (o `claim` do lote o aceita) e os itens em `collecting`/`optimizing` voltam à fila. Se a unit for morta por SIGKILL, a mensagem não confirmada só volta ao broker depois do `visibility_timeout` do Redis (padrão de 1 h); até lá o lote aparece como em execução sem worker.
- DEV: o `./restart` instala e liga o worker dos lotes junto com os demais (o instalador o para antes, se estiver ativo, e o liga uma vez com `enable --now`). O restart pode esperar até 300 s por um lote em curso.
- PROD: `./install-discovery-workers-systemd.sh --root /srv/apps/prod/criptofarol/source --batch-only` instala/atualiza só essa unit, sem tocar na Descoberta (ver `docs/prod-migration-runbook.md`). O overlay lista as duas units em `environments.*.services`, então o `release-guard post` exige `criptofarol-prod-batch-worker` em `services=` do `PROD_DEPLOY_EVIDENCE`.

### PROD discovery workers

Templates: `ops/systemd/criptofarol-prod-runtime-worker.service` (favorite refresh **e** `RUN_DISCOVERY_OUTBOX_DISPATCHER=1`), `ops/systemd/criptofarol-prod-discovery-worker.service` (Celery fila `discovery`) e `ops/systemd/criptofarol-prod-batch-worker.service` (Celery fila `batch_backtest`, #1120).

O installer `./install-discovery-workers-systemd.sh` aceita só os roots canônicos:

- `/srv/apps/dev/criptofarol/source`
- `/srv/apps/prod/criptofarol/source`

Qualquer outro path é recusado (exit 2). Em PROD **não** copia o drop-in do backend DEV.

```bash
cd /srv/apps/prod/criptofarol/source
./install-discovery-workers-systemd.sh
systemctl status criptofarol-prod-runtime-worker.service --no-pager
systemctl status criptofarol-prod-discovery-worker.service --no-pager
journalctl -u criptofarol-prod-discovery-worker.service -n 100 --no-pager
```

Desde o #1110 a unit da Descoberta PROD tem teto de memória (4 GiB aviso, 5 GiB corte). O installer completo recusa reescrevê-la com a Descoberta ativa; para aplicar o teto numa unit já instalada use `./install-discovery-workers-systemd.sh --root /srv/apps/prod/criptofarol/source --discovery-only`, que espera por ausência de busca ativa (ver `docs/discovery-memory-operations.md`, seção "Discovery PROD"). Migração de banco em PROD: `docs/prod-migration-runbook.md`.

Logs: `journalctl -u criptofarol-prod-runtime-worker.service` (dispatcher + refresh), `journalctl -u criptofarol-prod-discovery-worker.service` (Celery, fila `discovery`) e `journalctl -u criptofarol-prod-batch-worker.service` (Celery, fila `batch_backtest`). Smoke: um sweep em `https://criptofarol.com.br/discovery` sai de pending/queued e `/api/health` 200. Não reiniciar backend/frontend/leads por este installer.

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
