# multi-tenant-user-profile

## Status
- PO: done
- DESIGN: done
- DEV: done
- QA: done
- Alan approval: approved
- Homologation: approved
- archived: true

> Gate order: PO must be **done** before Alan approves to implement.

## Decisions (locked)
- Goal: Implementar perfil de usuário (visualizar/editar nome), alteração de senha (senha atual + nova), e log básico de auditoria (último login)
- Surface (mobile/desktop): Web app (desktop-first)
- Escopo backend:
  - GET /api/users/me — perfil do usuário logado (id, email, name, lastLogin)
  - PUT /api/users/me — atualizar nome do usuário
  - PUT /api/users/password — alterar senha (senha atual + nova)
  - Campo lastLogin no User model, atualizado no login
- Escopo frontend:
  - Página "Meu Perfil" (/profile)
  - Página "Alterar Senha" (/change-password)
  - Links no menu do usuário
- Out of scope: alteração de email, 2FA, logs de auditoria detalhados

## Links
- OpenSpec viewer: http://72.60.150.140:5173/openspec/changes/multi-tenant-user-profile/proposal
- PT-BR review (viewer): http://72.60.150.140:5173/openspec/changes/multi-tenant-user-profile/review-ptbr

## Notes
- Card #71 (MT-3)
- Depende de card #69 (MT-1) — autenticação existente
- Email é imutável nesta versão (requer fluxo de verificação adicional)

## Next actions
- [x] PO: Criar OpenSpec artifacts (proposal, spec, design, tasks)
- [x] DESIGN: Aprovado
- [x] DEV: Implementado (backend + frontend)
- [x] QA: Testes integrados aprovados (5/5)
- [x] Alan approval: Aprovado
- [ ] Alan: Homologação

## Audit mirror

### [QA] handoff 2026-04-03 00:23 UTC
Status: ready-for-homologation
What changed: 5/5 testes de integração passaram:
- test_get_me_returns_authenticated_profile PASSED
- test_get_me_requires_authentication PASSED
- test_put_me_updates_name PASSED
- test_put_password_changes_password_when_current_matches PASSED
- test_put_password_rejects_incorrect_current_password PASSED
Evidence: pytest backend/tests/integration/test_user_profile_endpoints.py -v
Next owner: @Alan
Next step: Homologação

### [DEV] handoff 2026-04-02 23:27 UTC
Status: needs-review
What changed: implementados `GET /api/users/me`, `PUT /api/users/me`, `PUT /api/users/password`; adicionado `last_login` no model + update no login; criadas as páginas protegidas `/profile` e `/change-password` com links no menu do usuário.
Evidence: `npm --prefix frontend run build` OK; `python -m py_compile backend/app/routes/user_profile.py backend/app/routes/auth.py backend/app/main.py backend/app/database.py backend/app/models.py backend/tests/integration/test_user_profile_endpoints.py` OK
Next owner: @QA
Next step: reconciliar o runtime/Kanban e validar os fluxos de perfil/troca de senha na UI e API.
