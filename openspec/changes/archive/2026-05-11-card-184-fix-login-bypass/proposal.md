## Why

O sistema possui um DEV BYPASS (`PASSWORDLESS_LOGIN_EMAILS`) que permite que emails específicos (atualmente `o.alan.silva@gmail.com` e `o2.alan.silva@gmail.com`) façam login sem senha. Isso bloqueia o lançamento do beta fechado em produção, pois o acesso precisa exigir autenticação válida e previsível. Acesso sem senha é uma vulnerabilidade de segurança que permite entrada não autenticada no sistema.

## What Changes

- Remover a lista `PASSWORDLESS_LOGIN_EMAILS` e a lógica de bypass do endpoint `POST /api/auth/login` no backend
- Remover a validação condicional de senha no frontend (`LoginPage.tsx`) que pula a exigência de senha para os mesmos emails
- Remover/adapter testes que validam o bypass como comportamento aceito
- Adicionar testes que comprovem que NENHUM email consegue login sem senha válida
- Garantir que logout remove sessão e impede reautenticação por cache/localStorage inválido — **BREAKING** para quem dependia do bypass

## Capabilities

### New Capabilities
- `login-password-mandatory`: Garantir que toda autenticação exija senha válida, sem bypass por email

### Modified Capabilities
- `closed-beta-access-control`: Remover bypass `PASSWORDLESS_LOGIN_EMAILS` que viola o requisito "Active user logs in with valid credentials"; adicionar requisito explícito de que nenhum email está isento de verificação de senha

## Impact

- `backend/app/routes/auth.py`: remover `PASSWORDLESS_LOGIN_EMAILS`, lógica de bypass no endpoint `/login`, e referências em `_closed_beta_registration_emails`
- `frontend/src/pages/LoginPage.tsx`: remover `PASSWORDLESS_LOGIN_EMAILS` e validação condicional de senha
- `backend/tests/unit/test_database_and_auth.py`: remover/adapter testes de bypass, adicionar teste negativo de login sem senha
- `frontend/tests/e2e/issue-68-monitor-home.spec.ts`: remover/adapter teste "login passwordless"
- `.env` / configuração de ambiente: `PASSWORDLESS_LOGIN_EMAILS` deve ter default vazio ou ser completamente removida
