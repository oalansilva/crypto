# Proposal — Card #69: [MT-1] Autenticação — Login, Registro e JWT

## Problema

O sistema não possui autenticação. Qualquer usuário pode acessar任意 endpoints sem verificação de identidade. É necessário implementar login, registro e proteção de rotas com JWT.

## Solução

Implementar sistema completo de autenticação com:
- Registro de usuários com email/senha (senha com hash bcrypt)
- Login que retorna access token + refresh token JWT
- Middleware de autenticação em todas as rotas protegidas
- Logout que invalida tokens

## User Stories

1. **Registro** — Como novo usuário, quero me registrar com email/senha para criar minha conta.
2. **Login** — Como usuário, quero fazer login para acessar minha conta.
3. **Rotas protegidas** — Como usuário logado, quero que o sistema proteja minhas rotas recusando acesso sem token válido.

## Critérios de Aceitação

- [ ] Cadastro com email + senha (hash bcrypt, ≥ 10 caracteres)
- [ ] Login retorna access token JWT (validade: 15min) + refresh token (validade: 7d)
- [ ] Rotas protegidas (exceto /auth/*) recusam acesso sem token válido
- [ ] Logout invalida refresh token (blocklist ou marcação)
- [ ] Senha nunca exposta em respostas da API
- [ ] Validação de email formatado

## Escopo

**Inclui:**
- Registro POST /auth/register
- Login POST /auth/login
- Logout POST /auth/logout
- Refresh token POST /auth/refresh
- Middleware de auth para rotas protegidas
- Hash bcrypt de senhas

**Não inclui:**
- Isolamento de dados por tenant (MT-2)
- Perfil de usuário / atualização de dados (MT-3)
- Recuperação de senha
- Login social / OAuth
