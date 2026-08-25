## Why

`GET /api/workflow/projects` é público e o DTO `ProjectOut` devolve `database_url`, `workflow_database_url` e `root_directory`. Em DEV e PROD isso entrega connection strings; com elas lê-se usuários, hashes e chaves de exchange. P0 da varredura: o Kanban precisa escolher projeto por slug/nome sem expor o banco.

## What Changes

- **BREAKING:** `GET /api/workflow/projects` passa a exigir `get_current_admin` / `ADMIN_EMAILS`. Sem sessão → 401; autenticado e não admin → 403. O corpo de erro **não** inclui connection string.
- **BREAKING:** o JSON de projeto (`ProjectOut` no GET e no POST, e qualquer serializer do row `Project`) **omite** as chaves `database_url`, `workflow_database_url` e `root_directory` (não nulas). Permanecem `id`, `slug`, `name`, `frontend_url`, `backend_url`, `tech_stack`.
- Colunas no Postgres e o seed em runtime **permanecem**; só deixam de sair na API. `POST /api/workflow/projects` continua autenticado via `get_workflow_actor` e devolve o DTO redigido; o row guarda as URLs.
- Frontend: `ProjectSelector` envia credencial no GET (`authFetch`); não-admin vê a falha de carga já existente (“Erro ao carregar”), não lista pública.
- Testes: anônimo → 401; não-admin → 403; admin → 200 sem os três campos; atualizar asserts que exigiam `workflow_database_url` no GET; overrides de integração que listam projetos passam a autenticar admin no GET.

Não entra: redesenhar o Kanban; autenticar em massa `GET /api/workflow/kanban/*`, `GET .../changes`, scheduler ou health; rotacionar senhas/URLs já vazadas (ops à parte); apagar colunas do schema; trocar `get_workflow_actor` no restante do workflow.

## Capabilities

### New Capabilities

- `workflow-projects-lockdown`: gate admin no GET de projetos; DTO HTTP sem secrets nem path interno; seletor do Kanban com credencial; testes de 401/403/redação.

### Modified Capabilities

- (nenhuma) — `workflow-state-db` continua sendo a fonte de estado; este card não muda o contrato de persistência, só o envelope HTTP da lista/criação de projeto.

## Impact

- Backend: `app.routes.workflow` (`ProjectOut`, `_project_out`, `list_projects`, `create_project`).
- Frontend: `frontend/src/components/ProjectSelector.tsx` (hoje `fetch` sem `authFetch`).
- Testes: `backend/tests/integration/test_workflow_projects.py` e demais clientes que `GET /api/workflow/projects` sem admin.
- Runtime Postgres/seed: sem migration. Clientes internos que liam `database_url` do GET quebram até env (aceito).
- `UI impact: none` — não há tela nova; o estado de erro do seletor já existe.
