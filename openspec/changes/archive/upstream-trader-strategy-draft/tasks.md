## 1. Backend — strategy draft + aprovação

- [x] 1.1 Persistir no run: `upstream.strategy_draft`, `upstream.ready_for_user_review`, `upstream.user_approved`, `upstream.user_feedback`.
- [x] 1.2 Ajustar endpoint de upstream message para permitir que o Trader retorne `strategy_draft` e marcar `ready_for_user_review=true`.
- [x] 1.3 Criar endpoint de aprovação:
  - `POST /api/lab/runs/{run_id}/upstream/approve` (marca `user_approved=true`, inicia execução)
- [x] 1.4 Criar endpoint de feedback:
  - `POST /api/lab/runs/{run_id}/upstream/feedback` (salva feedback e chama Trader para revisar draft)
- [x] 1.5 Adicionar trace events:
  - `upstream_strategy_draft_ready`
  - `upstream_user_approved`
  - `upstream_user_feedback`

## 2. Frontend — card do draft + botões

- [x] 2.1 Em `/lab/runs/:run_id`, mostrar card “Proposta do Trader” quando `ready_for_user_review=true`.
- [x] 2.2 Adicionar botão **Aprovar e iniciar execução**.
- [x] 2.3 Adicionar input “ajustes desejados” + botão enviar feedback.
- [x] 2.4 Garantir copy: “Trader” (não validator).

## 3. Spec delta + validate

- [x] 3.1 Escrever delta spec em `specs/lab/spec.md`.
- [x] 3.2 `openspec validate upstream-trader-strategy-draft --type change`.

## Test plan

- Manual:
  - Conversar no upstream até aparecer o draft.
  - Enviar feedback → draft revisado.
  - Aprovar → execução inicia.

- Automated (mínimo):
  - Teste de endpoint approve/feedback.
