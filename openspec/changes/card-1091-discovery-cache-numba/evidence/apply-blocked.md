# Apply #1091 — interrupção de infraestrutura

Esta evidência não constitui aceite de implementação. Tasks permanecem 0/19
marcadas; equivalência ampliada e desempenho ainda não foram executados.

Baseline Git: `64c1b97aec75b250ad4f32c0fd20692cf7a5f5b5` (HEAD inicial,
pós-945). Candidato: alterações não commitadas no worktree
`card-1091-discovery-cache-numba`; não existe SHA de candidato commitado.

## Recusa persistente

A criação de `backend/scripts/discovery_benchmark_1091.py` por `apply_patch`
com destino absoluto no worktree foi recusada duas vezes por PreToolUse:

```text
process-fsm-guard deny reason=fail_closed q=None
q_git=card-1091-discovery-cache-numba bound_card=1091.
Write produto blocked.
```

Entre recusas, a consulta de leitura `github_status_provider('1091')` mostrou
`Em desenvolvimento` e `decide(payload, status_provider=github_status_provider)`
retornou `allow` para a mesma ferramenta e destino. Nenhum Status foi injetado;
guard/FSM não foram modificados. O harness não foi escrito e a ação não foi
repetida através de outra ferramenta. O pai identificou timeout de 2 segundos
na consulta de Status como explicação possível, sem confirmação da causa.

## Instalação limpa e checks executados

Ambiente isolado de validação descartável, sem dependência de produto nesse path:

```sh
python3 -m venv /tmp/card-1091-clean-env
/tmp/card-1091-clean-env/bin/python -m pip install \
  -r /srv/apps/dev/criptofarol/crypto-worktrees/card-1091-discovery-cache-numba/backend/requirements.txt \
  -r /srv/apps/dev/criptofarol/crypto-worktrees/card-1091-discovery-cache-numba/backend/requirements.lock
/tmp/card-1091-clean-env/bin/python -m pip check
```

Instalação PASS; `No broken requirements found.` Python 3.12/aarch64;
Numba 0.68.0, llvmlite 0.50.0, NumPy 2.4.6, pandas 3.0.3, TA-Lib 0.6.8,
pyarrow 24.0.0. Nenhum upgrade de dependência alheia foi gravado no repo.
Os dois kernels compilaram com `fastmath=False`, sem paralelismo adicional.

```sh
DATABASE_URL=postgresql+psycopg2://unused:unused@127.0.0.1:1/crypto_app_test \
PYTHONPATH=backend:. /tmp/card-1091-clean-env/bin/python -m pytest \
  backend/tests/unit/test_card_945_fastpath.py \
  backend/tests/unit/test_deep_backtest_open_position.py \
  backend/tests/unit/test_backtest_execution_costs.py -q --timeout=0
```

Resultado: **11 passed**, 8.72 segundos, dois avisos: depreciação de Config
Pydantic em `app/config.py` e overflow CAGR em `app/metrics/performance.py`.
O primeiro attempt de coleta usou `postgresql://` e falhou por driver `psycopg`
ausente com SQLAlchemy 2.1.4 da resolução limpa. O URL explícito `+psycopg2`
usa a dependência já declarada e passou; não houve conexão a banco vivo.

## Implementação parcial preservada

- Kernels posição e Deep estritos, índices int64 separados de preços float64,
  import opcional de Numba e fallback Python.
- Snapshot privado com identidade de dados/índice/esquema, geração/fonte/papel,
  buffers protegidos e transporte ao worker.
- LRU compartilhado com teto 64 MiB/4.096 entradas/32 snapshots, caches
  indicador/coverage/intraday/ISO limitados e cleanup no fim da execução.
- Adaptadores comuns e flag `COMBO_OPTIMIZER_1091_DISABLED` independente de LEGACY.
- Pins Numba/llvmlite e injeção interna de fixtures/observer para o futuro harness.

Não validado: cache adversarial completo, fallback compiler/cache sem escrita,
2.800 casos/568 edges, 21.210 trials, ablação TA-Lib, cinco pares por cenário,
JIT frio e memória agregada. Nenhum ganho de desempenho é reivindicado.

Requested modelo/esforço: `gpt-6.1-sol` / `high`, captura do pai
`/tmp/card-1091-apply-model.json`. Modelo/esforço/runtime observados:
`unavailable` (sem fonte autoritativa exposta). Spawns deste Apply: 0;
HTML gerado/copied: N/A; UI impact: none.
