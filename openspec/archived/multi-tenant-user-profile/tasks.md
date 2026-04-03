# Tasks — Card #71: [MT-3] Perfil de Usuário

## Implementação

### Backend

- [ ] **TASK-71-1**: Adicionar campo `last_login` ao User model
  - Local: `backend/app/models.py`
  - Tipo: `Column(DateTime, nullable=True, default=None)`
  - Executar migration se necessário

- [ ] **TASK-71-2**: Criar arquivo de rotas `user_profile.py`
  - Local: `backend/app/routes/user_profile.py`
  - Endpoints:
    - `GET /api/users/me` — retorna perfil do usuário logado
    - `PUT /api/users/me` — atualiza nome do usuário
    - `PUT /api/users/password` — altera senha com validação

- [ ] **TASK-71-3**: Registrar router no main.py
  - Local: `backend/app/main.py`
  - Importar e incluir `user_profile_router`

- [ ] **TASK-71-4**: Atualizar endpoint de login para gravar `last_login`
  - Local: `backend/app/routes/auth.py`
  - No `POST /auth/login`, após autenticação bem-sucedida, atualizar `user.last_login = datetime.utcnow()`

### Frontend

- [ ] **TASK-71-5**: Criar página ProfilePage
  - Local: `frontend/src/pages/ProfilePage.tsx`
  - Estados: loading, ready, error, success
  - Campos: nome (editável), email (readonly), último login, membro desde
  - Integração: GET/PUT /api/users/me

- [ ] **TASK-71-6**: Criar página ChangePasswordPage
  - Local: `frontend/src/pages/ChangePasswordPage.tsx`
  - Estados: loading, ready, error, success
  - Campos: senha atual, nova senha, confirmar nova senha
  - Integração: PUT /api/users/password
  - Validação client-side: senhas coincidem, min 8 chars

- [ ] **TASK-71-7**: Adicionar rotas no App.tsx
  - Local: `frontend/src/App.tsx`
  - Rotas:
    - `/profile` → ProfilePage (protected)
    - `/change-password` → ChangePasswordPage (protected)

- [ ] **TASK-71-8**: Adicionar links ao menu do usuário
  - Local: `frontend/src/components/AppNav.tsx` (ou onde estiver o dropdown do usuário)
  - Items: "Meu Perfil" → /profile, "Alterar Senha" → /change-password

### Testes

- [ ] **TASK-71-9**: Testes automatizados backend
  - Local: `backend/tests/`
  - Testar GET /api/users/me com token válido → 200
  - Testar GET /api/users/me sem token → 401
  - Testar PUT /api/users/me com name válido → 200
  - Testar PUT /api/users/password com senha correta → 200
  - Testar PUT /api/users/password com senha errada → 400

### Documentação

- [ ] **TASK-71-10**: Atualizar README ou adicionar documentação de API
  - Documentar novos endpoints

---

## Resumo das Tarefas

| # | Descrição | Responsável | Estimativa |
|---|-----------|------------|------------|
| 1 | Campo last_login no User model | DEV | 15 min |
| 2 | Rotas user_profile.py | DEV | 1h |
| 3 | Registrar router no main.py | DEV | 5 min |
| 4 | last_login no login | DEV | 10 min |
| 5 | ProfilePage | DEV | 45 min |
| 6 | ChangePasswordPage | DEV | 45 min |
| 7 | Rotas no App.tsx | DEV | 15 min |
| 8 | Links no menu | DEV | 15 min |
| 9 | Testes backend | QA | 1h |
| 10 | Documentação | DEV | 15 min |

**Total estimado: ~4h30**
