---
spec: openspec.v1
id: multi-tenant-user-profile
title: Perfil de Usuário — MT-3
status: draft
owner: Alan
created_at: 2026-04-02
updated_at: 2026-04-02
---

# 0) One-liner

Endpoints e UI para usuário visualizar/editar perfil (nome) e alterar senha, com log básico de auditoria (último login).

# 1) Context

- Problem: O sistema tem autenticação (card #69) mas não permite ao usuário gerenciar seus próprios dados.
- Why now: Funcionalidade básica esperada por qualquer sistema autenticado.
- Constraints: Email é imutável sem fluxo de verificação adicional.

# 2) Goal

## In scope
- GET/PUT /api/users/me — perfil (nome, email)
- PUT /api/users/password — alteração de senha (senha atual + nova senha)
- lastLogin no User model (atualizado no login)
- Tela de perfil no frontend
- Tela de alteração de senha no frontend

## Out of scope
- Alteração de email
- Autenticação de dois fatores
- Logs de auditoria detalhados
- Recuperação de senha (já existe)

# 3) User stories

- Como usuário logado, quero ver meu perfil (nome, email, último login) para verificar meus dados.
- Como usuário logado, quero alterar minha senha fornecendo a senha atual e a nova senha para manter minha conta segura.
- Como usuário logado, quero editar meu nome para corrigir erros.

# 4) UX / UI

- Entry points: Menu do usuário (avatar/nome no header) → "Meu Perfil" / "Alterar Senha"
- Estados: Loading, Empty (impossível vazio para usuário logado), Error
- Copy (PT-BR):
  - Título: "Meu Perfil"
  - Campos: Nome, Email (somente leitura), Último Login
  - Botão: "Salvar"
  - Título senha: "Alterar Senha"
  - Campos: Senha Atual, Nova Senha, Confirmar Nova Senha
  - Botão: "Alterar Senha"

# 5) API / Contracts

## Backend endpoints

### GET /api/users/me
- Request: Header Authorization: Bearer <token>
- Response (200):
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "Nome do Usuário",
  "lastLogin": "2026-04-02T10:00:00Z",
  "createdAt": "2026-01-01T00:00:00Z"
}
```
- Response (401): `{ "detail": "Missing authentication" }`

### PUT /api/users/me
- Request: Header Authorization: Bearer <token>
```json
{
  "name": "Novo Nome"
}
```
- Response (200):
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "Novo Nome",
  "lastLogin": "2026-04-02T10:00:00Z",
  "createdAt": "2026-01-01T00:00:00Z"
}
```
- Response (400): `{ "detail": "Name cannot be empty" }`
- Response (401): `{ "detail": "Missing authentication" }`

### PUT /api/users/password
- Request: Header Authorization: Bearer <token>
```json
{
  "currentPassword": "senha atual",
  "newPassword": "nova senha"
}
```
- Response (200):
```json
{
  "message": "Password changed successfully"
}
```
- Response (400): `{ "detail": "Password must be at least 8 characters" }` ou `{ "detail": "Current password is incorrect" }`
- Response (401): `{ "detail": "Missing authentication" }`

## Security
- Auth: JWT Bearer token (mesmo sistema do card #69)
- Rate limits: mesmo que outras rotas autenticadas

# 6) Data model changes

- User model: adicionar campo `last_login` (DateTime, nullable, default=null)
- Migration: adicionar coluna last_login à tabela users

# 7) VALIDATE (mandatory)

- Proposal URL: http://31.97.92.212:5173/openspec/multi-tenant-user-profile
- Status: draft → validated → approved → implemented

Checklist:
- [x] Scope is unambiguous (in-scope/out-of-scope are explicit)
- [x] Acceptance criteria are testable (binary pass/fail)
- [x] API/contracts are specified (request/response/error)
- [x] UX states covered (loading/empty/error)
- [x] Security considerations noted (auth/exposure)
- [ ] Test plan includes manual smoke + at least one automated check
- [x] Open questions resolved or explicitly tracked

# 8) Acceptance criteria (Definition of Done)

- [ ] GET /api/users/me retorna dados do usuário logado com lastLogin
- [ ] PUT /api/users/me atualiza nome do usuário
- [ ] PUT /api/users/password valida senha atual e altera senha
- [ ] lastLogin é atualizado no login (middleware ou endpoint de login)
- [ ] Tela de perfil exibe nome, email, último login
- [ ] Tela de alteração de senha tem validação de senha atual incorreta
- [ ] Testes automatizados cobrem os endpoints

# 9) Test plan

## Automated
- Test GET /api/users/me com token válido → 200 + dados
- Test GET /api/users/me sem token → 401
- Test PUT /api/users/me com name válido → 200 + name atualizado
- Test PUT /api/users/password com senha correta → 200
- Test PUT /api/users/password com senha errada → 400

## Manual smoke
1. Login → Menu → Meu Perfil → verificar dados
2. Alterar nome → Salvar → verificar atualização
3. Menu → Alterar Senha → preencher dados → Alterar → verificar sucesso

# 9) Implementation plan

- Step 1: Adicionar campo lastLogin ao User model e migration
- Step 2: Criar rotas /api/users/me e /api/users/password
- Step 3: Atualizar middleware de login para gravar lastLogin
- Step 4: Criar páginas ProfilePage e ChangePasswordPage no frontend
- Step 5: Adicionar rotas no App.tsx e links no menu
- Step 6: Testes automatizados

# 10) Rollout / rollback

- Rollout: Deploy backend + frontend juntos
- Rollback: Reverter migration e endpoints

# 11) USER TEST (mandatory)

After deployment/restart, Alan will validate in the UI.

- Test URL(s): http://31.97.92.212:5173/profile, http://31.97.92.212:5173/change-password
- What to test (smoke steps):
  1. Login → clicar no avatar/nome → "Meu Perfil" → ver dados
  2. Alterar nome → Salvar
  3. Menu → "Alterar Senha" → preencher → Alterar
- Result:
  - [ ] Alan confirmed: OK

# 12) ARCHIVE / CLOSE (mandatory)

Only after Alan confirms OK:

- [ ] Update spec frontmatter `status: implemented`
- [ ] Update `updated_at`
- [ ] Add brief evidence (commit hash + URL tested) in the spec

# 13) Notes / open questions

- Email é imutável sem verificação adicional — decisão: não permite alteração de email nesta versão.
- lastLogin usa created_at do login como proxy inicial se não houver campo dedicado.
- Sugestão: unificar update de lastLogin no middleware de autenticação (auth.py).
