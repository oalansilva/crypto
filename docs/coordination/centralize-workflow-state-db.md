# centralize-workflow-state-db

## Status
- PO: done
- DESIGN: skipped
- Alan approval: approved
- DEV: done
- QA: in progress (3.1 + 3.2 validated; 3.3 pending)
- Alan homologation: approved

## Decisions (draft)
- Goal: centralize workflow runtime state in a DB inside the VPS.
- Database direction: self-hosted Postgres on the VPS.
- Multi-project support from day one.
- `docs/coordination/*.md` leaves the runtime path after cutover; until then it stays as a transitional artifact.
- Transition policy locked for MVP:
  - Phase 0 (current): `docs/coordination/*.md` still drives the board/runtime.
  - Phase 1 (migration): DB becomes the operational source of truth, while `docs/coordination/*.md` is kept only as mirrored audit/handoff artifact for active changes.
  - Phase 2 (post-cutover): no runtime decisions depend on `docs/coordination/*.md`; keep files as readable history until archive, then stop requiring them in the live flow.
- OpenSpec remains as documentation/artifact layer.
- Kanban should eventually read from DB-backed APIs.
- Historical migration scope locked for MVP:
  - Migrate into the DB only the workflow history needed for currently active changes at cutover (current status, task state, approvals/handoffs, and existing card comment thread / coordination context needed to keep work moving).
  - Do not backfill every archived/closed change or every legacy daily note/comment into normalized DB records in MVP.
  - Keep older closed changes/comments in their existing file-based artifacts as readable history, linked from the DB/UI when relevant.
  - Preserve navigation to historical artifacts/links, but treat bulk historical import as a post-MVP enhancement if it proves necessary.
- Taxonomy/parent-child locked for MVP:
  - `change` is the container/root that groups artifacts, approvals, comments, and work items for one OpenSpec change; it is not a child of another work item.
  - `story` is the default deliverable work item under a change and represents an independently plannable/trackable slice of work.
  - `bug` is a defect work item. It may exist directly under the change or as a child of a `story` when the defect belongs to that slice.
  - Parent-child rule: only `story -> bug` is a mandatory blocking parent-child relationship in MVP. Do not require deeper generic trees for the first version.
  - Closure rule: a `story` cannot reach its final completed state while any child `bug` remains open.
  - Standalone change-level bugs are allowed and must be completed before the enclosing change can be fully done, but they do not need an intermediate parent story.
  - Multiple sibling `story` items and multiple sibling `bug` items may coexist under the same `change`.
- Parallelism/WIP/locks/dependencies locked for MVP:
  - Multiple sibling `story` items may be active in parallel under the same `change`, provided each active story has a distinct owner/agent run and a separate lock scope.
  - WIP limit per `change`: at most 2 active `story` items at the same time in MVP; extra approved stories stay queued until a slot is freed.
  - WIP limit per agent run: one active `story` at a time; the same run must not hold delivery ownership of multiple stories concurrently.
  - Lock granularity for MVP is the `story`. Only one owner/run may hold the delivery lock for a story at a time. Child `bug` work under that story inherits the same lock and must not be worked by a second run concurrently.
  - Change-level approvals/handoffs (`Alan approval`, `QA`, `Alan homologation`) remain change-scoped gates, not per-story gates. So parallel story execution is allowed only inside the DEV implementation window after change approval and before the change enters QA/homologation.
  - Dependency rule: a story marked blocked by another story must not move into active implementation until all declared predecessor stories are done. Ready-without-dependency stories may proceed, respecting WIP.
  - Completion rule for parallel work: the enclosing `change` cannot advance to QA until every in-scope story/bug required for that release slice is done and no dependency-blocked work remains open.
  - Conflict fallback: if two candidate stories touch the same delivery surface and safe isolation is unclear, they must be serialized under one story lock instead of run in parallel.

## Links
- Proposal: http://72.60.150.140:5173/openspec/changes/centralize-workflow-state-db/proposal
- Review PT-BR: http://72.60.150.140:5173/openspec/changes/centralize-workflow-state-db/review-ptbr

## Notes
- Change criada a partir da preocupação do Alan com o estado descentralizado do fluxo.
- Escopo atual: discutir arquitetura e definir o workflow core em Postgres como fonte operacional multi-projeto.
- Direção desejada: o Kanban deve virar o lugar principal para consultar o fluxo, e os agentes devem se coordenar pelos comentários dos cards com menções entre si.
- A migração das changes ativas para o novo modelo faz parte do escopo de DEV depois da aprovação.
- Pré-requisitos explícitos desta change: instalar/configurar Postgres na VPS, definir persistência/segredos e validar conectividade antes da camada de workflow.
- Taxonomia MVP fechada em PO: `change` como container raiz; `story` como unidade padrão de entrega; `bug` como defeito ligado à change ou filho de uma `story`.
- Regra pai-filho MVP fechada: suportar explicitamente `story -> bug` como vínculo bloqueante; não exigir árvore genérica profunda na primeira versão.
- Regra de fechamento fechada: `story` com bug filho aberto não pode ir para estado final concluído; bug de nível da change também precisa estar fechado para a change encerrar.
- O sistema também deve suportar múltiplas stories ativas ao mesmo tempo e múltiplos agentes trabalhando em paralelo, com locks/dependências para evitar conflito.
- Regra de paralelismo MVP fechada: até 2 stories ativas por change, 1 por agent run, lock exclusivo por story, dependências entre stories bloqueiam ativação, e gates de approval/QA/homologation continuam no nível da change.
- Tracking reconciliado: 1.3, 1.4, 1.5 e 1.6 agora estão refletidos como fechados; PO concluído.
- Alan aprovou a direção arquitetural e o trabalho já foi passado para DEV.
- DEV 2.1.2 concluído no workflow core: schema agora inclui `AgentRun.status`, vínculo opcional `AgentRun.change_pk`, `WorkItem.owner_run_id` e índices relacionados para ownership/concorrência.
- DEV 2.1.2 também ganhou regras explícitas no serviço `backend/app/services/workflow_core_service.py`: dependências só entre stories da mesma change, no máximo 2 stories ativas por change, no máximo 1 story ativa por agent run, lock exclusivo por story, e bloqueio de fechamento da story enquanto houver bug filho aberto.
- DEV 2.3 (cutover Kanban) concluído: backend expõe `/api/workflow/kanban/*` (shapes compatíveis com o Kanban legado) incluindo `changes`, `comments` e agora `tasks` (adapter checklist DB-backed). Frontend Kanban foi migrado para usar **somente** `/api/workflow/*` (sem fallback para `/api/coordination/*`).
- Ajuste final de compatibilidade em 2.3: o adapter `/api/workflow/kanban/changes/{id}/tasks` agora devolve `path` com sufixo `tasks.md` e preserva a árvore `story -> bug`/bug órfão no mesmo shape de checklist esperado pelo drawer do Kanban.
- Cobertura mínima de regressão adicionada para 2.3: `backend/tests/integration/test_workflow_kanban_adapter_api.py` valida o adapter DB-backed de tasks; `frontend/tests/e2e/kanban-loads.spec.ts` valida a renderização da árvore de work-items (`Story`/`Bug`) no painel de detalhes.
- Não foi encontrado outro mecanismo local de tracking/kanban além de `openspec/changes/.../tasks.md`, `docs/coordination/*.md` e o store local de comentários em `data/coordination_comments/<change>.jsonl`.
- Reconciliação QA 2026-03-10: coordination estava incoerente ao marcar `QA: done` enquanto `tasks.md` ainda tinha 3.2/3.3 abertos; o status consolidado voltou para `QA: in progress` antes de registrar novo avanço.
- Testes adicionados em `backend/tests/integration/test_workflow_core_service.py` cobrindo WIP limit, ownership por run, dependências bloqueando ativação, exclusividade de lock e bloqueio `story -> bug` no fechamento.
- Fix de runtime config: `app.workflow_database` antes usava apenas `os.getenv()`, mas o backend carrega `backend/.env` via `pydantic-settings` (não exporta para `os.environ`). Agora a flag/URL são lidas via `get_settings()` (campos `workflow_db_enabled` e `workflow_database_url`). Também foi garantido `psycopg2-binary` no venv para Postgres.
- DEV 2.2 concluído no backend: `backend/app/routes/workflow.py` agora expõe APIs DB-backed para mudanças e tasks (`GET/POST/PATCH`), além de comments, approvals e handoffs com escopo por change ou work item.
- O schema do workflow foi ampliado em `backend/app/workflow_models.py` com tabelas `wf_approvals` e `wf_handoffs`, mantendo comments/tasks no mesmo banco operacional do workflow.
- Teste de API adicionado em `backend/tests/integration/test_workflow_api.py` cobrindo o fluxo principal de create/list/update para change + tasks + comments + approvals + handoffs em SQLite isolado.
- QA 2026-03-10 (item 3.1): suíte de workflow passou (`pytest -q backend/tests/integration/test_workflow_audit_coordination.py backend/tests/integration/test_workflow_api.py backend/tests/integration/test_workflow_core_service.py backend/tests/integration/test_workflow_kanban_adapter_api.py` => `8 passed, 4 warnings`).
- QA 2026-03-10 (Postgres/VPS): validação no Postgres foi concluída após ajustar compatibilidade de IDs de comentários legados.
  - Fix: `wf_comments.id` passou de `varchar(36)` para `varchar(64)` (IDs legados não são UUID e podem ter ~45 chars).
  - Seed OK: `PYTHONPATH=backend .venv/bin/python backend/scripts/seed_workflow_from_coordination.py --project crypto` => `inserted_changes=1`, `inserted_gate_approvals=6`, `inserted_comments=10`.
  - Audit OK: `/api/workflow/audit/coordination?project_slug=crypto` sem drift.
  - Kanban adapters OK: `/api/workflow/kanban/changes`, `/comments`, `/tasks` (com `path` apontando para `openspec/changes/.../tasks.md`).
- QA 2026-03-10 (item 3.2): validação de consistência dos updates de agente concluída. Rodei `.venv/bin/pytest -q backend/tests/integration/test_workflow_api.py backend/tests/integration/test_workflow_core_service.py backend/tests/integration/test_workflow_audit_coordination.py` => `7 passed, 4 warnings`.
  - `test_workflow_api.py`: change/task/comment/approval/handoff continuam consistentes após create/update/list pelos endpoints DB-backed.
  - `test_workflow_core_service.py`: regras de WIP, ownership por run, dependências, lock exclusivo e bloqueio `story -> bug` impedem updates incoerentes de agente.
  - `test_workflow_audit_coordination.py`: endpoint de auditoria detecta drift entre DB e coordination quando os rastros divergem.

## Infra / Config prerequisites (DEV)

### Target: self-hosted Postgres on the VPS

**Proposed DB:** `workflow`

**Proposed role/user:** `workflow_app`

**Required env/config (backend):**
- `WORKFLOW_DB_ENABLED=1`
- `WORKFLOW_DATABASE_URL=postgresql+psycopg2://workflow_app:<PASSWORD>@127.0.0.1:5432/workflow`

**Secret handling:**
- Keep the password out of git.
- Preferred: load via a server-side `.env` (or systemd EnvironmentFile) on the VPS.

**Persistence:**
- Postgres data dir must be on persistent disk (default distro install does this).

**Backups (MVP):**
- Nightly `pg_dump` of `workflow` (compressed), retain at least 7 days.

### Install/validate checklist (VPS)

1) Install Postgres packages. ✅
2) Create DB + role, grant privileges. ✅ (DB `workflow`, role `workflow_app`)
3) `psql` local connectivity smoke test. ✅
4) App connectivity test via `WORKFLOW_DATABASE_URL`. ✅ (backend reading backend/.env at runtime; `/api/workflow/health` reports `postgres`)
5) Create/verify workflow schema tables. ✅

#### Schema bootstrap (how it was done)

Until the backend service is wired with secrets on the VPS, we can still create the exact schema defined in `backend/app/workflow_models.py` by generating SQL from SQLAlchemy and applying it with `psql`:

```bash
cd /root/.openclaw/workspace/crypto
.venv/bin/python backend/scripts/generate_workflow_schema_sql.py > /tmp/workflow_schema.sql
sudo -u postgres psql -d workflow -v ON_ERROR_STOP=1 -c "SET ROLE workflow_app;" -f /tmp/workflow_schema.sql
sudo -u postgres psql -d workflow -c "\\dt"
```

This creates the tables owned by `workflow_app`.

## Closed

- Homologated by Alan and ready to archive.

## Next actions
- [x] PO: Formalizar a proposta da centralização do workflow em banco.
- [x] PO: Decidir a política de transição para `docs/coordination/*.md` (fonte temporária, espelhamento ou descontinuação por fase).
- [x] PO: Definir o escopo de migração histórica para changes/comments legados no MVP.
- [x] PO: Travar taxonomia de work items e regra pai-filho (MVP: `change` container raiz; `story` unidade de entrega; `bug` defeito; vínculo bloqueante explícito `story -> bug`; bug também pode existir direto na change).
- [x] PO: Definir regras de paralelismo (múltiplas stories ativas, locks, dependências, WIP).
- [x] Alan: Aprovar a direção arquitetural.
- [x] Alan: Revisar e aprovar a direção arquitetural (PO já concluiu escopo/taxonomia/paralelismo).
- [x] DEV: Implementar o workflow core em Postgres conforme a proposta aprovada (MVP).
  - Backend: configurar `WORKFLOW_DB_ENABLED=1` + `WORKFLOW_DATABASE_URL` (ver `backend/.env.example`).
  - Backend: APIs DB-backed de 2.2 já cobrem changes/tasks/comments/approvals/handoffs.
  - Cutover Kanban (2.3) concluído: backend agora tem `/api/workflow/kanban/*` incluindo adapter de tasks; e o frontend Kanban lê **somente** do workflow DB (sem fallback para `/api/coordination/*`).
  - Migração/seeding Phase 1 (2.4/2.5/2.6): script `backend/scripts/seed_workflow_from_coordination.py` migra changes ativas + gate status + comentários legacy (JSONL) para o workflow DB; endpoint `/api/workflow/audit/coordination` detecta drift entre DB e `docs/coordination/*.md`.
- [x] QA: Validar depois de DEV.
  - Status 2026-03-10: `3.1` (Kanban+Postgres seed), `3.2` (updates/locks/rules) e `3.3` (links/artefatos) concluídos.
  - ✅ Rodado `.venv/bin/pytest -q backend/tests/integration/test_workflow_api.py backend/tests/integration/test_workflow_core_service.py backend/tests/integration/test_workflow_audit_coordination.py`; resultado: `7 passed, 4 warnings`.
  - ✅ Item 3.3 validado: OpenSpec artifacts existem em `openspec/changes/centralize-workflow-state-db/*` e o Kanban adapter referencia `.../tasks.md`.
  - Próximo passo: Alan homologation (revisar no Kanban/UI e aprovar gate).
