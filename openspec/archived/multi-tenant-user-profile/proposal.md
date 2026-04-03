# Proposal — Card #71: [MT-3] Perfil de Usuário — Perfil, Alteração de Senha e Auditoria

## Problema

O sistema possui autenticação (card #69 - MT-1) mas não oferece ao usuário a capacidade de:
1. Visualizar e editar seu próprio perfil (nome, email)
2. Alterar sua senha (senha atual + nova senha)
3. Consultar dados básicos de auditoria (último login, etc.)

## Solução

Implementar endpoints de perfil do usuário e alteração de senha, com UI correspondente no frontend.

## User Stories

1. **Ver Perfil** — Como usuário logado, quero ver meu nome e email para confirmar meus dados cadastrais.
2. **Editar Perfil** — Como usuário logado, quero poder atualizar meu nome para corrigir erros ou mudanças.
3. **Alterar Senha** — Como usuário logado, quero alterar minha senha fornecendo a senha atual e a nova senha.
4. **Consultar Auditoria** — Como usuário, quero saber quando foi meu último login para fins de segurança.

## Critérios de Aceitação

- [ ] GET /api/users/me retorna id, email, name, lastLogin (ou createdAt como proxy)
- [ ] PUT /api/users/me permite atualizar name (email é imutável sem verificação)
- [ ] PUT /api/users/password verifica senha atual antes de permitir alteração
- [ ] Validação: nova senha ≥ 8 caracteres
- [ ] Frontend exibe página de perfil com nome, email e data de último login
- [ ] Frontend exibe página de alteração de senha com campos: senha atual, nova senha, confirmar nova senha
- [ ] Log de auditoria: lastLogin atualizado a cada login bem-sucedido

## Escopo

**Inclui:**
- GET /api/users/me (perfil)
- PUT /api/users/me (atualizar nome)
- PUT /api/users/password (alterar senha com validação de senha atual)
- Tela de perfil no frontend
- Tela de alteração de senha no frontend
- Campo lastLogin no User model (atualizado no login)

**Não inclui:**
- Alteração de email (requer fluxo de verificação adicional)
- Recuperação de senha (já coberto pelo card #69 MT-1)
- Autenticação de dois fatores
- Logs de auditoria detalhados (acesso a dados, ações, etc.)
