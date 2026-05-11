## Context

O endpoint `POST /api/auth/login` em `backend/app/routes/auth.py` possui um DEV BYPASS ativo: a variável de módulo `PASSWORDLESS_LOGIN_EMAILS` (default: `o.alan.silva@gmail.com,o2.alan.silva@gmail.com`) permite que esses emails façam login com qualquer senha ou senha vazia. O frontend (`LoginPage.tsx`) replica a mesma lista para pular validação de senha no formulário. Isso viola o spec `closed-beta-access-control`, que exige credenciais válidas.

O card #184 é P0 e bloqueia o lançamento do beta fechado em produção.

## Goals / Non-Goals

**Goals:**
- Remover completamente o bypass `PASSWORDLESS_LOGIN_EMAILS` do backend e frontend
- Garantir que `POST /api/auth/login` sempre verifique senha com bcrypt para todos os usuários
- Garantir que o formulário de login no frontend sempre exija senha
- Atualizar testes para validar que login sem senha é rejeitado
- Manter logout funcional (já está correto — `persistAuthState(null, null, null)` limpa localStorage)

**Non-Goals:**
- Não alterar o fluxo de registro (`POST /api/auth/register`)
- Não adicionar 2FA ou CAPTCHA
- Não alterar refresh token ou `/api/auth/me`
- Não mudar regras de bloqueio (banned/suspended)
- Não alterar o beta access control além da remoção do bypass

## Decisions

### D1: Remover `PASSWORDLESS_LOGIN_EMAILS` completamente (não apenas mudar default)

**Alternativa considerada**: Manter a variável de ambiente mas com default vazio (`""`).

**Decisão**: Remover a constante de módulo e toda lógica de bypass.

**Rationale**: A existência do mecanismo de bypass, mesmo desabilitado por padrão, é uma superfície de ataque. Se um operador definir `PASSWORDLESS_LOGIN_EMAILS=*` por engano, todos entram sem senha. Remover o código elimina o risco. O único uso legítimo era desenvolvimento local, que pode ser resolvido com senhas conhecidas ou seed scripts.

### D2: Remover a lista do frontend também

**Alternativa considerada**: Manter validação client-side (já que o backend seria o gate real).

**Decisão**: Remover `PASSWORDLESS_LOGIN_EMAILS` do `LoginPage.tsx`.

**Rationale**: Consistência — se o backend exige senha, o frontend não deve sugerir que senha é opcional. Além disso, manter a lista no frontend criaria divergência e confusão.

### D3: Usar `PASSWORDLESS_LOGIN_EMAILS` existente como fallback para registro, migrando para `BETA_INVITED_EMAILS`

`_closed_beta_registration_emails()` atualmente inclui `PASSWORDLESS_LOGIN_EMAILS` no conjunto de emails permitidos para registro. Após remover `PASSWORDLESS_LOGIN_EMAILS`, os emails que estavam lá (`o.alan.silva@gmail.com`, `o2.alan.silva@gmail.com`) precisam ser adicionados a `BETA_INVITED_EMAILS` ou `ADMIN_EMAILS` para não perder acesso ao registro.

**Decisão**: Os emails já estão cobertos por `ADMIN_EMAILS` (importado de `authMiddleware`). Nenhuma migração adicional necessária.

## Risks / Trade-offs

- **[Risco] Contas do Alan sem senha conhecida**: Se `o.alan.silva@gmail.com` não tiver senha definida (hash nulo ou placeholder), Alan não conseguirá logar após a correção. → **Mitigação**: Verificar se as contas têm `password_hash` válido; se não tiverem, gerar senha temporária segura e comunicar offline.
- **[Risco] Testes quebrados**: Testes existentes validam o bypass como sucesso. → **Mitigação**: Atualizar testes para esperar HTTP 401 em login sem senha.
- **[Trade-off] Dev local sem bypass**: Desenvolvedores precisarão usar senha real. → **Mitigação**: Documentar uso de seed script com senha conhecida (`dev123456`).

## Migration Plan

1. Deploy do código (remover bypass)
2. Verificar `password_hash` das contas `o.alan.silva@gmail.com` e `o2.alan.silva@gmail.com` no banco
3. Se hash ausente/inválido, definir senha temporária e comunicar ao Alan
4. Rollback: reverter commit (o bypass é removido em um único commit atômico)
