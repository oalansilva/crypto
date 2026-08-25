## Context

Card [#685](https://github.com/oalansilva/crypto/issues/685) (P0, Segurança). Issue grelhado: `GET /api/workflow/projects` não tem `Depends` de auth (`list_projects` só usa `get_workflow_db`). `ProjectOut` / `_project_out` copiam `database_url`, `workflow_database_url` e `root_directory` do row `wf_projects`. `POST /projects` já usa `get_workflow_actor` (qualquer logado) e ecoa o mesmo DTO. Seed em `app.main` continua gravando URLs no Postgres. `ProjectSelector` faz `fetch` cru em `${API_BASE_URL}/workflow/projects` sem `authFetch`; o tipo TS já só usa `id`/`slug`/`name`. Estado de erro do seletor já existe.

**UI impact: none.** Sem tela nova ou redesenho do Kanban. Credencial no GET e 401/403 reutilizam “Erro ao carregar”. Prototype N/A. Impeccable N/A.

## Goals / Non-Goals

**Goals:**

- GET da lista de projetos só para admin (`get_current_admin` / `ADMIN_EMAILS`).
- DTO HTTP sem `database_url`, `workflow_database_url`, `root_directory` (chaves ausentes).
- POST autenticado como hoje; resposta redigida; row no banco intacto.
- Seletor envia JWT; não-admin não vê lista pública.
- Testes 401/403/200 redigido; asserts antigos do GET atualizados.

**Non-Goals:**

- Redesenhar o Kanban.
- Auth em massa de kanban/changes/scheduler/health.
- Rotacionar URLs já vazadas.
- Drop de colunas / migration.
- Trocar `get_workflow_actor` no restante do workflow.
- Tornar POST admin-only (história fala “criar”; Entra mantém POST com ator logado — Entra vence).

## Decisions

1. **GET: `Depends(get_current_admin)`, não `get_workflow_actor`.**  
   Alternativa: qualquer usuário autenticado. Rejeitada: o issue nomeia `get_current_admin` / `ADMIN_EMAILS` e 403 para não-admin. FastAPI já mapeia sessão ausente → 401 e e-mail fora da lista → 403.

2. **Redigir no modelo `ProjectOut`, não com `exclude_none`.**  
   Alternativa: manter campos Optional e omitir quando None. Rejeitada: o aceite exige que as três chaves **não existam** mesmo se o row tiver valor. `_project_out` deixa de copiá-las. `ProjectCreate` continua aceitando URLs no body do POST para o runtime gravar.

3. **Um único `_project_out` para GET e POST.**  
   Alternativa: dois DTOs. Desnecessária: o issue pede o mesmo recorte em qualquer serializer do row `Project`. Hoje só esses dois endpoints usam `_project_out`.

4. **POST permanece `get_workflow_actor`.**  
   Alternativa: alinhar POST a admin. Fora do Entra. Apply não “completa” a história alargando o gate.

5. **Frontend: `authFetch` no `ProjectSelector`.**  
   Alternativa: `credentials: 'include'` no `fetch`. O app autentica por JWT em `localStorage` (`authFetch`), não cookie de sessão. `fetch` cru hoje não manda Bearer; após o GET virar 401 o admin logado também falharia. Usar o helper existente.

6. **Testes de integração: override `get_current_admin` no cliente que lista.**  
   O `_build_client` de `test_workflow_projects.py` só override `get_workflow_actor`. Sem override do admin, GET passa a 401. Apply: override admin nos testes que precisam listar; testes novos sem override / com user não-admin para 401 e 403. Não enfraquecer o gate com override global em `conftest` da API de produto.

7. **Kanban/changes sem mudança de auth.**  
   Endpoints que devolvem change/task **não** serializam o row `Project` completo hoje. Apply confirma que nenhum outro `response_model` ecoa as três chaves; se achar um, o mesmo recorte (Entra).

## Apply contract

- Editar `ProjectOut` / `_project_out` / `list_projects` e testes de `/api/workflow/projects`.
- Trocar o GET do `ProjectSelector` para `authFetch`.
- Não migration, não seed, não auth de kanban/changes.
- Não redesenhar UI.
- Não logar connection strings em evidência.

## Risks / Trade-offs

- [Cliente interno lia `database_url` do GET] → quebra até env; aceito no issue.
- [URLs já vazadas] → rotação ops fora do card.
- [GET admin vs POST ator qualquer] → POST ainda autenticado; não ecoa secrets. Aceito pelo Entra.
- [Testes de workflow que GET projetos sem admin] → atualizar overrides; risco de 401 em massa se Apply esquecer um cliente.
- [Admin logado no Kanban sem `authFetch`] → lista quebra; mitigado pela decisão 5.

## Migration Plan

1. Código na branch após T7; sem Alembic.
2. Deploy DEV no Done: GET anônimo deixa de vazar; admin autenticado no Kanban lista slug/nome.
3. Rollback = revert do commit (reabre o vazamento — não desejado).
4. Rotação das strings já vazadas: ops, não este Done.

## Open Questions

Nenhuma. Fronteira fechada na grelha.

## UI impact

**none** — credencial + redação de JSON. Superfície do seletor inalterada (loading/erro/dropdown já existem).

## Prototype

N/A — `UI impact: none`. Sem HTML de protótipo.

## Prototype Validation

N/A.

## Impeccable Brief

N/A — `UI impact: none`.

## Impeccable Critique

N/A — `UI impact: none`.

## Impeccable Audit

N/A — `UI impact: none`.

## Impeccable Trace

N/A — `UI impact: none`.

## Design Critique

Crítica isolada inherit (read-only, 1 spawn, sem transcript). Fontes: `proposal.md`, `design.md` (D1–D7), `tasks.md`, `specs/workflow-projects-lockdown/spec.md`, `workflow.py` ProjectOut/GET/POST, `ProjectSelector`, `authFetch`, `test_workflow_projects.py`. Card #685, change `card-685-workflow-projects-lockdown`, `Status=Design`. Prototype: N/A. Impeccable: N/A (`UI impact: none`). Snapshot: `.impeccable/critique/685-card-685-workflow-projects-lockdown-20260825T024800Z.md`.

- **P0:** nenhum
- **P1:** nenhum
- **P2 — testes 401/403 (tasks 2.1):** não usar `_build_client` com override permanente de `get_current_admin`.
- **P3 — `ProjectSelector` sem import no app (aceito):** Entra ainda pede credencial no GET; Apply patcha o componente.
- **P3 — não-admin reusa “Erro ao carregar” (aceito / UI none).**
- **P3 — `frontend_url` / `backend_url` permanecem no DTO (Entra).**

Riscos não bloqueantes: strings já vazadas até ops; clientes que liam `database_url` do GET; POST continua ator logado.

**Design Agent verdict: PASS** — crítica isolada inherit. Prototype N/A. Impeccable N/A.
