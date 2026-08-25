# Snapshot — card #685 `card-685-workflow-projects-lockdown`

- Card: #685
- Change: `card-685-workflow-projects-lockdown`
- Critic: isolated Design Critic (no transcript inherit)
- UTC: 2026-08-25T02:48:00Z
- UI impact: none (justificado: seletor já tem loading/erro; Prototype N/A)
- Surfaces lidas: proposal, design, tasks, spec; `workflow.py` (`ProjectCreate`/`ProjectOut`/`list_projects`/`create_project`/`_project_out`); `ProjectSelector.tsx`; `authFetch.ts`; `test_workflow_projects.py`

---

## Brief

Lockdown HTTP de `GET /api/workflow/projects`: hoje público; `ProjectOut`/`_project_out` copiam `database_url`, `workflow_database_url`, `root_directory`. Alvo: `Depends(get_current_admin)` no GET (401 sem token, 403 autenticado fora de `ADMIN_EMAILS`); DTO sem as três chaves (não `exclude_none`); POST permanece `get_workflow_actor` com resposta redigida e row/seed intactos; `ProjectSelector` passa a `authFetch` (JWT Bearer em `localStorage`); testes 401/403/200 sem as chaves e overrides só onde a lista precisa de admin. Fora: Kanban visual, auth em massa, rotação de URLs, drop de colunas.

Audience: admin no Kanban (slug/nome). Outcome: lista autenticada sem connection strings. Direction: contrato de API + credencial no GET existente. Scope: envelope HTTP de list/create project.

---

## Critique

### GET vs POST gate

`get_current_admin` (via `get_current_user`) já mapeia missing/invalid token → 401 e e-mail fora de `ADMIN_EMAILS` → 403 (`Admin access required`). HTTPBearer `auto_error=False`; ausência de credencial ainda vira 401 em `get_current_user`, não lista. POST já está atrás de `get_workflow_actor` (`Depends(get_current_user)`). Manter POST no ator logado é Entra, não furo do GET. Qualquer logado ainda pode **gravar** URLs no POST; o risco residual é escrita, não eco GET público.

### Omissão de chaves vs `exclude_none`

`ProjectOut` hoje declara as três chaves `Optional` e `_project_out` as preenche. `exclude_none` / `response_model_exclude_none` **vaza** quando o row tem valor. Decisão 2 (remover campos do modelo e parar de copiar em `_project_out`) é a única que satisfaz “chaves ausentes, não nulas”. `ProjectCreate` deve continuar aceitando o body. `response_model=List[ProjectOut]` / `ProjectOut` no POST corta extras se Apply não devolver o ORM cru sem modelo.

### Serializers outros

Único HTTP shape do row `Project` em `workflow.py`: `_project_out` em GET e POST. Task 1.3 + spec “Other Project serializers share the cut” cobrem regressão. Kanban/changes não serializam o row completo hoje.

### 401/403 body

Falhas de `get_current_admin`/`get_current_user` usam `detail` estático (`Missing authentication`, `Admin access required`, etc.). Gate corre **antes** de `list_projects`; o handler não lê `wf_projects`. Spec 401/403 “body SHALL NOT contain a connection string” é testável. 400 de POST (`database_url must point to PostgreSQL`) nomeia a chave, não ecoa a URL — fora do GET.

### authFetch vs fetch

Contrato JWT: `authFetch` injeta `Authorization: Bearer` de `auth_access_token`; `fetch` cru não. Após GET admin-only, admin logado no seletor quebraria sem Bearer. Refresh só em **401**, não em 403: não-admin autenticado não dispara logout por este GET. UI none: `isLoading` / `error` → “Erro ao carregar” já existe; 401/403 reutilizam o mesmo estado. `ProjectSelector` não é importado noutro TSX agora; o contrato do card ainda exige a troca.

### Testes / overrides

`_build_client` só override `get_workflow_db` + `get_workflow_actor`; `finally` faz `dependency_overrides.clear()`. GET atual espera 200 e **asserta** `root_directory` / `workflow_database_url` no JSON. Sem override de `get_current_admin`, GET vira 401 (TestClient sem JWT). Decisão 6 + tasks 2.1–2.3: override **só** nos casos que listam; 401/403 **sem** override admin; não globalizar em `conftest` de produto. Task 2.2: persistência no row, não no JSON.

### UI none

Nenhuma superfície visual nova. Delta de produto: não-admin deixa de ver catálogo público e cai no erro já desenhado. Prototype N/A aceitável.

---

## Audit

- A11y/responsive/browser: N/A (`UI impact: none`).
- Segurança de envelope: GET público + DTO completo = leak atual; design fecha o envelope sem `exclude_none`.
- Dual-DB: admin em `get_db` (users); lista em `get_workflow_db` — correto.
- Risco operacional (não bloqueante): se Apply meter `get_current_admin` dentro de `_build_client` para todos os testes do arquivo, os cenários 401/403 ficam falsos-positivos.

---

## Trace

1. proposal.md — breaking GET admin + DTO cut + POST ator + authFetch + testes.
2. design.md — decisões 1–7; Apply contract; Prototype N/A.
3. spec.md — 401/403 sem connection string; chaves ausentes; POST `get_workflow_actor`; seletor com credencial.
4. tasks.md — 1.1–1.3 DTO/gate/search; 2.1–2.3 testes/overrides; 3.1 authFetch.
5. `list_projects` sem Depends de auth; `ProjectOut` inclui as três chaves.
6. `get_current_admin` 403 se não admin; 401 via `get_current_user`.
7. `authFetch` Bearer + refresh só 401.
8. `test_workflow_projects.py` asserts de leak no GET/POST JSON; só override de actor.

---

## Findings (para emissão curta)

### P0

(nenhum)

### P1

(nenhum)

### P2

- Testes 401/403 não podem reutilizar um `_build_client` que já override `get_current_admin`; o `clear()` no `finally` é necessário, mas um override “sempre-on” no helper esconde o gate.

### P3

- `ProjectSelector` hoje é componente órfão (sem import no app); `authFetch` ainda é o contrato certo se/quando o Kanban o montar.
- Não-admin vê o mesmo “Erro ao carregar” de falha de rede (aceito pelo Entra / UI none).
- `frontend_url` / `backend_url` permanecem no DTO (fora do corte das três chaves).

### Disposition

Achados P2/P3 são guard-rails de Apply e resíduos aceitos; não exigem redesenho nem alargar o Entra. Prototype N/A.

### Verdict

**PASS**
