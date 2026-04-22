# Revisão (PT-BR) — admin-user-management-panel

## O que é

Criar um painel administrativo de gestão de usuários para suporte, com consulta, busca/filtros, ações de ciclo de vida da conta (suspensão/banimento/reactivação) e trilha de auditoria.

## Mudanças principais
- Adiciona campos operacionais no modelo de usuário para estado de conta: `status`, `suspended_until`, `suspension_reason`, `is_banned`, `notes`.
- Bloqueia login e renovação de sessão para contas banidas.
- Reativa automaticamente usuários suspensos após expirar `suspended_until`.
- Cria a API administrativa em `/api/admin`:
  - `GET /api/admin/users`
  - `POST /api/admin/users`
  - `PUT /api/admin/users/{userId}`
  - `GET /api/admin/users/{userId}`
  - `POST /api/admin/users/{userId}/suspend`
  - `POST /api/admin/users/{userId}/ban`
  - `POST /api/admin/users/{userId}/reactivate`
  - `GET /api/admin/user-actions`
- Registra `AdminActionLog` para auditoria de ações administrativas.
- Adiciona interface `/admin/users` no frontend (somente admin) com filtros, criação, edição, suspensão, banimento, reativação e consulta de logs.

## Como validar
1. Entrar com usuário admin.
2. Abrir `/admin/users`.
3. Buscar e filtrar usuários por nome/e-mail, status e janelas de data.
4. Criar e editar usuário com motivo de alteração.
5. Suspender e banir usuário, confirmando razão e mensagem de sucesso/erro.
6. Reativar usuário e validar retorno a `active` com limpeza de marcações de suspensão.
7. Consultar logs em `GET /api/admin/user-actions` (e painel no frontend).

## Artefatos
- Proposal: `openspec/changes/admin-user-management-panel/proposal.md`
- Specs:
  - `openspec/changes/admin-user-management-panel/specs/admin-user-management/spec.md`
  - `openspec/changes/admin-user-management-panel/specs/admin-action-audit-log/spec.md`
- Design: `openspec/changes/admin-user-management-panel/design.md`
- Tasks: `openspec/changes/admin-user-management-panel/tasks.md`
- Review PT-BR: `openspec/changes/admin-user-management-panel/review-ptbr.md`
