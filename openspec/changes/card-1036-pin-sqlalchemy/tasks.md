# Tasks — card-1036-pin-sqlalchemy (driver explícito no CI e nos testes)

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.
> `UI impact: none` nesta entrega: nada de painel/Monitor, rota, HTML ou base de dados de produto. Os tokens do gate estão no `design.md`.
> Sem pin: `backend/requirements.txt` **não** é tocado. Escopo: `.github/workflows/ci.yml` (4 valores) + 14 ficheiros de teste (incl. `backend/tests/conftest.py`).

## 1. Tornar o driver explícito no CI

- [x] 1.1 — Em `.github/workflows/ci.yml`, trocar `postgresql://` por `postgresql+psycopg2://` em `:262` e `:263` (`DATABASE_URL` / `WORKFLOW_DATABASE_URL` do job `backend-unit-tests`).
- [x] 1.2 — Em `.github/workflows/ci.yml`, trocar `postgresql://` por `postgresql+psycopg2://` em `:367` e `:368` (mesmas variáveis do job `backend-tests`).

## 2. Tornar o driver explícito nos testes (só sítios de ligação real)

- [x] 2.1 — Em `backend/tests/conftest.py`, trocar os defaults de `DATABASE_URL` (`:15`) e `WORKFLOW_DATABASE_URL` (`:19`) para `postgresql+psycopg2://`.
- [x] 2.2 — Em `backend/tests/integration/`, trocar a URL de ligação em: `test_ai_dashboard_dynamic.py:20`, `test_external_binance_spot_balances.py:18`, `test_workflow_audit_coordination.py:19`, `test_workflow_core_service.py:22`, `test_monitor_preferences_endpoints.py:19`, `test_system_preferences_admin.py:15`, `test_workflow_projects.py:57`, `test_user_profile_endpoints.py:20`, `test_user_binance_credentials.py:16`, `test_monitor_theme_preference.py:15`, `test_workflow_api.py:17`, `test_workflow_update_change_guards.py:37`, `test_workflow_kanban_manual_backlog.py:21`.
- [x] 2.3 — **Não** tocar nas ocorrências de asserção/esperadas/fixture (ex.: `test_database_and_auth.py`, `test_backend_unit_harness.py`, `test_workflow_projects.py:50,129,146,165,247,266`, `test_discovery_service.py:112`, `test_bootstrap_env.py`, `test_ohlcv_storage.py`, `test_runtime_status.py`, `test_runtime_worker_and_workflow_db.py`): só se muda uma string usada **como** URL de ligação.
- [x] 2.4 — Confirmar que `backend/requirements.txt` (`:9` e `:10`) permanece intocado (sem pin).

## 3. Correr a suíte

- [x] 3.1 — Correr a suíte backend localmente contra o Postgres de teste, sem `psycopg` v3 instalado, e verificar que não há `ModuleNotFoundError: No module named 'psycopg'` nem `UndefinedTable: combo_templates`.
- [x] 3.2 — Confirmar que a cascata está resolvida: `test_ai_dashboard_dynamic.py` volta a criar o esquema (`Base.metadata.create_all`) e o teste do combo encontra `combo_templates`.

## 4. Verificação de fecho no PR (pai / T11) — não é tarefa da coluna Apply

> Estas verificações exigem o PR aberto e o CI corrido; são executadas pelo pai no fecho da coluna (`aceitar_sha`), não pelo Apply.

- No PR para `develop`, confirmar `sqlalchemy-2.1.x` no log de instalação de `backend-unit-tests` e `backend-tests`.
- Confirmar que `backend-unit-tests` e `backend-tests` correm até ao fim **sem falhas** e que o `qa-gate` fica `success`.

## 5. Validar o pacote

- [x] 5.1 — `openspec validate card-1036-pin-sqlalchemy --strict` verde.
