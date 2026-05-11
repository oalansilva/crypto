## 1. Backend — Remover bypass de senha

- [x] 1.1 Remover constante `PASSWORDLESS_LOGIN_EMAILS` e leitura do env `PASSWORDLESS_LOGIN_EMAILS` em `backend/app/routes/auth.py`
- [x] 1.2 Remover lógica condicional de bypass no endpoint `POST /api/auth/login` (linhas 208-213)
- [x] 1.3 Atualizar `_closed_beta_registration_emails()` removendo referência a `PASSWORDLESS_LOGIN_EMAILS`
- [x] 1.4 Remover import não utilizado após limpeza (se houver)

## 2. Frontend — Remover bypass de validação

- [x] 2.1 Remover constante `PASSWORDLESS_LOGIN_EMAILS` do `frontend/src/pages/LoginPage.tsx`
- [x] 2.2 Remover lógica `bypassPassword` da função `validate()` — senha sempre obrigatória
- [x] 2.3 Confirmar que `authStore.tsx` logout já limpa localStorage corretamente (verificação, sem alteração necessária)

## 3. Testes — Atualizar para refletir novo comportamento

- [x] 3.1 Atualizar `backend/tests/unit/test_database_and_auth.py`: remover/adapter testes de passwordless login, adicionar teste de login sem senha rejeitado (HTTP 401)
- [x] 3.2 Atualizar `frontend/tests/e2e/issue-68-monitor-home.spec.ts`: remover/adapter teste "login passwordless deve aceitar o2 sem senha"
- [x] 3.3 Rodar `./backend/.venv/bin/python -m pytest -q` e confirmar que todos passam

## 4. Validação e evidência

- [x] 4.1 Rodar `openspec validate --change "card-184-fix-login-bypass"` e confirmar verde
- [x] 4.2 Rodar `npm --prefix frontend run build` e confirmar sem erros
- [x] 4.3 Verificar que `PASSWORDLESS_LOGIN_EMAILS` não aparece em nenhum arquivo fonte (grep global)
