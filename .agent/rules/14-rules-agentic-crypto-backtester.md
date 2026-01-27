CRYPTO_AGENT_RULES.txt
14 Rules for Agentic Systems – Crypto Backtester Edition
Trigger: always_on

This file defines the mandatory behavioral and architectural rules
for the AI in this workspace.
All rules are binding and must be applied conceptually at all times.

==================================================
METADATA
==================================================

Title: 14 Rules para IDEs Agenticas – Crypto Backtester Edition
Tools: Cursor, Antigravity, Claude Code, Windsurf, Cline
Author: Breno Vieira Silva – Lion Lab Academy (adapted for Crypto Backtester)
Version: 2.0
License: Free to use and modify

==================================================
PROJECT STRUCTURE
==================================================

crypto-backtester/
  .agent/
    rules/
      rule-01-api-boundary.md
      rule-02-async-performance.md
      rule-03-dataset-isolation.md
      rule-04-secrets-vault.md
      rule-05-execution-hardening.md
      rule-06-clean-architecture.md
      rule-07-financial-determinism.md
      rule-08-error-handling.md
      rule-09-dependency-hygiene.md
      rule-10-test-first.md
      rule-11-api-consistency.md
      rule-12-commit-discipline.md
      rule-13-env-isolation.md
      rule-14-reproducibility.md

==================================================
RULE 01 – API BOUNDARY LAW
==================================================

Name: Isolamento por Fronteira de API

Purpose:
Prevent frontend, client agents or external scripts from executing
business logic, financial calculations or accessing the database.

Trigger:
When creating or modifying files in /frontend, /pages, /components
or any code consuming backend data.

Non-negotiable rules:
- Frontend must never access the database directly.
- Frontend must never perform financial calculations.
- All execution must go through /api/backtest/*.
- Workers must not expose public endpoints.

Forbidden example:
await fetch("http://localhost:8003/db/backtests")

Correct example:
await fetch("/api/backtest/run", { method: "POST" })

==================================================
RULE 02 – ASYNC PERFORMANCE LAW
==================================================

Name: Performance e Concorrência Assíncrona

Purpose:
Ensure FastAPI never blocks the event loop.

Trigger:
When modifying /backend/app/api, /services or /workers.

Rules:
- Async first.
- Never use time.sleep().
- Never use requests.
- Heavy backtests must run in workers.

Forbidden:
def run_backtest():
    time.sleep(10)

Correct:
async def run_backtest():
    await asyncio.sleep(10)

==================================================
RULE 03 – DATASET ISOLATION LAW
==================================================

Name: Isolamento de Dataset

Purpose:
Prevent data leakage between simulations.

Trigger:
When writing queries, repositories or read services.

Rules:
- Every query must filter by run_id.
- A backtest must never read another backtest data.

Forbidden:
results = db.query(Result).all()

Correct:
results = db.query(Result).filter(Result.run_id == run_id).all()

==================================================
RULE 04 – SECRETS VAULT LAW
==================================================

Name: Cofre de Segredos

Purpose:
Protect exchange and data provider API keys.

Trigger:
When handling Binance, Coinbase, AlphaVantage, etc.

Rules:
- Never store secrets in plain text.
- Always encrypt secrets.
- Never log secrets.

Forbidden:
db.save({"binance_key": api_key})

Correct:
encrypted = encryption.encrypt(api_key)
db.save({"binance_key": encrypted})

==================================================
RULE 05 – EXECUTION HARDENING LAW
==================================================

Name: Blindagem de Execução

Purpose:
Prevent invalid or destructive simulations.

Trigger:
When starting any backtest.

Mandatory validations:
- Allowed timeframe
- Date range
- Maximum candles
- Maximum strategies

Example:
if payload.candles > 200000:
    raise ValueError("Dataset too large")

==================================================
RULE 06 – CLEAN ARCHITECTURE LAW
==================================================

Name: Arquitetura Limpa

Purpose:
Prevent mixing transport with financial domain.

Layers:
- API: transport only
- Services: financial rules
- Workers: heavy execution

Supreme rule:
API must never contain business logic.

==================================================
RULE 07 – FINANCIAL DETERMINISM LAW
==================================================

Name: Determinismo Financeiro

Purpose:
Without determinism there is no science.

Trigger:
When using random, dates, seeds or simulations.

Forbidden:
- random without seed
- datetime.now()
- live APIs

Correct:
np.random.seed(42)

==================================================
RULE 08 – ERROR HANDLING LAW
==================================================

Name: Erros com Contexto

Purpose:
Avoid blind debugging.

Every error must include:
- run_id
- strategy
- timestamp
- stacktrace

Example:
logger.error("backtest.failed", run_id=run_id, strategy=strategy, exc_info=True)

==================================================
RULE 09 – DEPENDENCY HYGIENE LAW
==================================================

Name: Higiene de Dependências

Purpose:
Avoid CVEs and useless dependencies.

Rules:
- Last release < 12 months
- No critical CVEs
- Avoid trivial libraries

==================================================
RULE 10 – TEST FIRST LAW
==================================================

Name: Testes Antes da Implementação

Purpose:
Backtest without tests is not scientific.

Workflow:
Red -> Green -> Refactor

Example:
def test_sharpe_positive():
    assert calculate_sharpe([1,2,3]) > 0

==================================================
RULE 11 – API CONSISTENCY LAW
==================================================

Name: Consistência de API

Standard:
POST /backtest/run
GET  /backtest/status/{id}
GET  /backtest/result/{id}

==================================================
RULE 12 – COMMIT DISCIPLINE LAW
==================================================

Name: Disciplina de Commits

Format:
feat(backtest): add walk-forward analysis

==================================================
RULE 13 – ENVIRONMENT ISOLATION LAW
==================================================

Name: Isolamento de Ambientes

Purpose:
Never mix dev and prod.

Rules:
- SQLite in dev
- Postgres in prod
- Never share data

==================================================
RULE 14 – REPRODUCIBILITY LAW (SUPREME)
==================================================

Name: Reprodutibilidade Científica

Purpose:
Guarantee scientific validity.

Trigger:
When finishing any backtest.

Every run must store:
- parameters
- strategy
- dataset
- seed
- code version

Example:
{
  "run_id": "123",
  "strategy": "SMA_CROSS",
  "params": {"fast":10,"slow":50},
  "dataset": "BTC_4H_2023_2025",
  "engine_version": "2.0.1",
  "seed": 42
}

==================================================
THE 3 SUPREME LAWS OF AGENTIC SYSTEMS
==================================================

Law 1:
The backend calculates. The frontend visualizes.

Law 2:
The domain thinks. The API transports.

Law 3:
Without determinism there is no science.
Without reproducibility there is no trust.

==================================================
END OF FILE
==================================================
