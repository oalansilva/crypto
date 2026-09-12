## 0. Nota do projecto (ler antes das fatias)

- [x] 0.1 Usar as skills do projecto em `.cursor/skills/` quando aplicável neste Apply: `openspec-apply-change` (loop das tasks), `covenant-flow` (runbook do cliente) e `impeccable` / `design-critic` **não** se aplicam (`UI impact: none`, protótipo N/A justificado no `design.md`)
- [x] 0.2 **UI impact do card = `none`** (fluxo do tester comum; a emissão do convite é superfície nova de admin entregue como API e a entrada do convidado é rota do próprio fluxo do convite, `surface: new`, sem clone). O gate do card continua a ser **Design → Aprovação de Design → Pronto para Dev**: este Apply só existe depois de `Status=Pronto para Dev` (T8, `iniciar_apply`), e a mudança de status é do Alan/pai — o filho Apply **não** chama `process_event`, **não** commita, **não** faz push, **não** muda de branch
- [x] 0.3 Ordem do deploy é contrato do `design.md` (D9): **bootstrap → migração/backfill → enforcement**. Não inverter a ordem das fatias 2, 3 e 4

## 1. Modelos e migração (role + convite)

- [x] 1.1 `backend/app/models.py`: coluna de role persistida em `User` (`"user"`/`"admin"`, default `"user"`, `NOT NULL`) — forma final é detalhe de Apply
- [x] 1.2 `backend/app/models.py`: tabela do convite (`beta_invites` ou nome equivalente) com `id`, `email` normalizado e indexado, `token_hash` único, `created_at`, `expires_at`, `created_by_user_id`, `consumed_at`, `consumed_user_id`, `revoked_at`, `revoked_reason`, `superseded_by_id`
- [x] 1.3 `backend/alembic/versions/`: uma migração com a coluna de role + a tabela do convite; `down_revision` apontando para o(s) head(s) vigentes no Apply (hoje há ramo duplo `20260818_0001` / `20260909_0001`)
- [x] 1.4 Mesma migração: backfill do admin atual — promove a role de admin **apenas** endereço de `ADMIN_EMAILS` que **já tenha conta**; nenhuma conta é criada e nenhuma outra conta ganha o papel por efeito colateral (D7, critério 10)
- [x] 1.5 `downgrade()` da migração reversível (dropar tabela/coluna) sem desfazer o backfill de role às cegas

## 2. Bootstrap de deploy (idempotente, sem superfície pública)

- [x] 2.1 Novo comando de deploy em `ops/` (`bootstrap_admin.py` ou equivalente): garante que o endereço já configurado no ambiente existe **e** tem role de admin
- [x] 2.2 Conta existente → apenas promove a role (sem alterar senha, sem criar conta extra); conta inexistente em deploy fresco → **cria** a conta como admin com credencial fornecida explicitamente pelo operador (env/stdin), **nunca** gerada, impressa ou logada (critério 11)
- [x] 2.3 Idempotente: segunda execução devolve o mesmo resultado, não cria segundo admin e não promove endereço fora da lista configurada (critérios 12, 13)
- [x] 2.4 Comando de host, **não** endpoint HTTP: nenhuma superfície pública ou autenticada nova; não passa por register/landing (D9)

## 3. Serviço de convite + auditoria

- [x] 3.1 Criar o serviço do convite: emissão (token opaco ~256 bits, persistido só como hash, TTL default 72 h sobreponível por `BETA_INVITE_TTL_HOURS`/`ttlHours`), link `${BETA_INVITE_BASE_URL}/beta-invite/<token>` (D3)
- [x] 3.2 Consumo atómico e vinculado ao endereço: `consumed_at IS NULL AND revoked_at IS NULL AND expires_at > now()` na mesma transação que **cria o `User`** (endereço sem conta) ou que **aplica a redefinição de senha pelo dono** (endereço com conta, D8); endereço diferente → recusa explícita (critérios 3, 4)
- [x] 3.3 Falhas explícitas, não erro genérico: reuso do mesmo token e convite expirado devolvem recusa dedicada e acionável (critérios 4, 5)
- [x] 3.4 Reemissão: permitida para o mesmo endereço; revoga os convites **abertos** do endereço (`revoked_reason="superseded"` + `superseded_by_id`) e não toca consumidos/expirados (D6)
- [x] 3.5 Auditoria em `beta_access_audit_logs` (`record_beta_access_audit`) para emissão, consumo feliz, reuso, endereço diferente, expirado e reemissão — **sem** token em `metadata_json` (critério 8)
- [x] 3.6 Endereço que **já tem conta**: o convite **só** autoriza a **redefinição de senha pelo dono** no fluxo do próprio convite (D3), com o token válido para aquele endereço; **sem** segunda conta, **sem** tocar role/admin, **sem** sobrescrever senha por efeito colateral anónimo; conta banida/suspensa **não** é reabilitada (D8, critério 7)
- [x] 3.7 Rota pública de entrada do convidado `${BETA_INVITE_BASE_URL}/beta-invite/<token>` (D3): `GET` com token válido → formulário de definição de senha (endereço pré-preenchido e travado pelo convite); token expirado/consumido/revogado/de outro endereço → recusa acionável; `POST` → consome o convite e define a senha (é aqui, e **só** aqui, que a conta nasce ou a senha do dono é redefinida — nunca em `leads`). Rota nova **do fluxo do convite** — não é `/monitor`, `/favorites`, `/combo/*` nem `landing`; se o frontend a servir, é página mínima nova com `surface: new` (isenta do clone gate), **nunca** clone de página viva

## 4. Enforcement — register e leads

- [x] 4.1 `backend/app/routes/auth.py`: `POST /api/auth/register` valida o convite de uso único para aquele endereço **primeiro**; sem convite válido **nenhuma** conta é criada e a resposta não revela **privilégio/allowlist** (`ADMIN_EMAILS`/allowlist) — e não há consulta de duplicidade antes disso (critérios 1, 6)
- [x] 4.2 `backend/app/routes/auth.py`: `_closed_beta_registration_emails()` deixa de ser porta de entrada e `BETA_PUBLIC_REGISTRATION_ENABLED` **não** repõe a porta (D5)
- [x] 4.3 `backend/app/routes/auth.py`: nenhum caminho do register grava role de admin; **depois** de o convite ser válido para aquele endereço, a duplicidade preserva o 400 "Email already registered" (C2), **sem** consumir o convite nem tocar a conta — a recuperação do endereço queimado com conta existente segue pela rota do convite (3.7/D8)
- [x] 4.4 `backend/app/middleware/authMiddleware.py`: `is_admin_email()` / `get_current_admin()` respondem pela role persistida; `ADMIN_EMAILS` sai do caminho de autorização de runtime (D7)
- [x] 4.5 `backend/app/routes/leads.py` + `backend/app/services/beta_access.py`: `POST /api/leads` **sem** convite válido → 202 neutro, nenhum `User`, nenhuma senha temporária, endereço **não** queimado (critério 6); `POST /api/leads` **aceita** `inviteToken` (D10)
- [x] 4.6 Com convite válido para aquele endereço → `leads` **não** consome o convite e **não** cria nem modifica conta: 202 neutro, convite **aberto** (ainda consumível no `POST` do link) e endereço **não** queimado. A conta nasce, ou a senha do dono é redefinida, **só** no `POST` da rota do link (3.7), com **sem** senha temporária, **sem** `must_change_password` e **sem** TTL. Senha temporária/`must_change_password`/TTL ficam **só** no caminho legado sem convite de `beta_access.py`, até o enforcement (D10, decisão de operador 2)
- [x] 4.7 Endereço queimado antes desta mudança: convite novo para o mesmo endereço devolve o acesso ao dono legítimo; **havendo conta antiga**, o convite autoriza a redefinição de senha no fluxo do convite — sem segunda conta, sem role, sem reabilitar banido/suspenso (critério 7, D8)

## 5. Superfície nova de admin (emissão do convite)

- [x] 5.1 `backend/app/routes/admin_users.py` (ou router de admin equivalente): `POST /api/admin/beta-invites` atrás de `Depends(get_current_admin)` (critério 9)
- [x] 5.2 Corpo `{ email, ttlHours? }`; 201 com `id`, `email`, `expiresAt`, `invitePath` e o **link copiável** (`inviteUrl`) devolvido **uma única vez**; token nunca persistido em claro, nunca em log nem em auditoria (D2, D3)
- [x] 5.3 Validação de entrada (e-mail malformado, `ttlHours` fora do intervalo) sem revelar se o endereço é privilegiado
- [x] 5.4 Não-admin → 401/403 reusando `get_current_admin`; nenhuma autorização nova inventada (critério 9)

## 6. Fixture e verificação (critério 14)

- [x] 6.1 Fixture do caminho feliz: emissão → consumo → conta criada com a senha escolhida pelo usuário, role de usuário comum (nunca admin) — sem senha temporária/`must_change_password`/TTL no caminho do convite
- [x] 6.2 Bloqueadores cobertos: consumo repetido (falha explícita), expirado (recusa acionável + auditoria), endereço diferente (recusa + auditoria), reemissão (link anterior revogado), **consumo para endereço que já tem conta** (redefine a senha no fluxo do convite, não cria segunda conta, não toca role, não reabilita banido/suspenso)
- [x] 6.3 Bloqueadores das portas: register sem convite para endereço em `ADMIN_EMAILS` (nenhuma conta, resposta neutra quanto a privilégio/allowlist), register com `BETA_PUBLIC_REGISTRATION_ENABLED` ligado (continua exigindo convite), register **com** convite válido para endereço já existente (400 C2, convite **não** consumido, conta intacta), leads sem convite (202 neutro, nenhuma conta, endereço não queimado), leads **com** convite válido (202 neutro, nenhuma conta, convite **não** consumido e ainda consumível no `POST` do link, endereço não queimado; a conta só nasce/redefine a senha no `POST` do link — 3.7)
- [x] 6.4 Bootstrap: duas execuções idempotentes, sem segundo admin, sem promoção fora da lista; endereço sem conta falha de forma explícita
- [x] 6.5 Não-admin não emite convite (403); auditoria presente em emissão/consumo/reuso/expirado/mismatch/reemissão

## 7. Verify

- [x] 7.1 `openspec validate card-689-convite-uso-unico --strict`
- [x] 7.2 Zero superfície de catálogo frontend: nenhuma rota `/monitor`, `/favorites`, `/combo/*` ou `landing` é tocada ou emprestada; nenhum HTML de protótipo (protótipo N/A justificado). A rota do convite (`/beta-invite/<token>`) é do **fluxo do convite**, `surface: new`, sem clone; tokens do gate mantidos (`UI impact: none` / `live_route: N/A` / `surface: new`) e `evaluate_clone_gate` continua a passar
- [x] 7.3 Ordem do deploy conferida no Apply: bootstrap → migração/backfill → enforcement (D9)
- [x] 7.4 Fora do recorte, intacto: verificação de e-mail/SMTP, IdP/OAuth, sessão/JWT/cookie HttpOnly, rate limit de login/register/leads, re-entrada de usuário existente **além** da redefinição de senha pelo convite (papel, fusão/posse de conta, sessão — D8), FSM/pin/`AGENTS.md` always-on/dual-write noutros clientes
