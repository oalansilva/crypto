# QA Evidence — 2026-04-23-indicadores-basicos-timeframes-scoring

## 6.1 Smoke da pipeline (BTCUSDT 1d + 1h)

Executar em backend local:

```bash
cd /root/.openclaw/workspace/crypto/backend
DATABASE_URL='postgresql+psycopg2://root@/crypto_app' \
  python3 scripts/qa_market_indicator_pipeline_smoke.py \
  --symbol BTCUSDT \
  --timeframes 1d 1h \
  --force-full \
  --strict-gaps \
  --timeout-seconds 600 \
  --output qa_artifacts/market-indicators-smoke.json
```

Observações esperadas:
- status final do job `completed`;
- `latest_rows` com no mínimo 1 linha para cada timeframe;
- sem duplicates no PK `(symbol, timeframe, ts)`;
- timestamps `ts` com timezone UTC;
- sem gaps grandes (quando `--strict-gaps`).

## 6.2 Cobertura, unicidade e alinhamento de `market_indicator`

Comando acima já verifica:
- cobertura dos timeframes executados;
- unicidade por `(symbol, timeframe, ts)`;
- timezone e monotonicidade dos timestamps.

Resultado esperado:
- `qa_artifacts/market-indicators-smoke.json` contendo `results` com seções `latest_rows` e `uniqueness_and_tz`.

## 6.3 Validação TradingView

Executar teste de fixture:

```bash
cd /root/.openclaw/workspace/crypto/backend
DATABASE_URL='postgresql+psycopg2://root@/crypto_app' \
  python3 -m pytest tests/unit/test_market_indicator_tradingview_fixtures.py -q
```

Observações:
- registrar saída do pytest em anexo neste arquivo (ou caminho paralelo `qa_artifacts/.../tradingview-parity.txt`).

## Execuções realizadas (hoje)

### 6.1 Smoke pipeline

Comando executado:

```bash
cd /root/.openclaw/workspace/crypto/backend
PYTHONPATH=/root/.openclaw/workspace/crypto/backend \
DATABASE_URL='postgresql+psycopg2://root@/crypto_app' \
./../backend/.venv/bin/python scripts/qa_market_indicator_pipeline_smoke.py \
  --symbol BTCUSDT --timeframes 1d 1h --force-full --strict-gaps --timeout-seconds 600 \
  --output qa_artifacts/market-indicators-smoke.json
```

Saída resumida:

- `pipeline_job` finalizou em `completed`
- `estimated_bars`: 480
- `processed_timeframes`: 2
- latest rows encontrados para `1d` e `1h`
- unicidade/monotonicidade de `ts` e timezone UTC aprovadas
- evidência gravada: `backend/qa_artifacts/market-indicators-smoke.json`

### 6.3 Teste TradingView

Comando executado:

```bash
cd /root/.openclaw/workspace/crypto/backend
PYTHONPATH=/root/.openclaw/workspace/crypto/backend \
DATABASE_URL='postgresql+psycopg2://root@/crypto_app' \
./../backend/.venv/bin/pytest tests/unit/test_market_indicator_tradingview_fixtures.py -q
```

Resultado: `4 passed, 1 warning in 1.38s`.
