# Review — Card #71: [MT-3] Perfil de Usuário

## Resumo da Funcionalidade

Permitir ao usuário autenticado:
1. Visualizar seu perfil (nome, email, último login)
2. Editar seu nome
3. Alterar sua senha (fornecendo senha atual + nova senha)

## Endpoints

| Método | Path | Descrição | Auth |
|--------|------|-----------|------|
| GET | /api/users/me | Retorna perfil do usuário | Sim |
| PUT | /api/users/me | Atualiza nome do usuário | Sim |
| PUT | /api/users/password | Altera senha | Sim |

## Critérios de Aceitação

- [ ] GET /api/users/me retorna dados completos do usuário logado
- [ ] PUT /api/users/me atualiza nome com sucesso
- [ ] PUT /api/users/password valida senha atual antes de alterar
- [ ] lastLogin é atualizado a cada login
- [ ] Página de perfil exibe todos os campos
- [ ] Página de alteração de senha valida senhas coincidem
- [ ] Testes automatizados cobrindo os endpoints

## Pages Frontend

| Página | Route | Descrição |
|--------|-------|-----------|
| Meu Perfil | /profile | Visualização e edição do perfil |
| Alterar Senha | /change-password | Formulário de alteração de senha |

## Checkpoints

- [ ] Design approved por Alan
- [ ] Implementação completa (backend + frontend)
- [ ] Testes passando
- [ ] Homologação por Alan
