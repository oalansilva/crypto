# Design — #689 Impedir auto-registro no e-mail admin sem verificação

## Contexto

O briefing (issue grelhado #689) **é** a spec: Problema, Entra / não entra, Vocabulário, 14 Critérios de aceite, Evidência e as 4 decisões de operador de 2026-08-29. Este Design **não** reentrevista nem reabre decisões fechadas; sintetiza-as e fixa *como*.

Factos verificados no repo (base deste desenho):

- `backend/app/routes/auth.py:31-36` lê `BETA_PUBLIC_REGISTRATION_ENABLED` e `BETA_INVITED_EMAILS` do env; `:133-143` monta `_closed_beta_registration_emails() = BETA_INVITED_EMAILS ∪ ADMIN_EMAILS`; `:148-171` é o `POST /api/auth/register` com 403 "Closed beta access requires invitation" e 400 "Email already registered".
- `backend/app/middleware/authMiddleware.py:134-148` — `is_admin_email()` (comparação com env `ADMIN_EMAILS`) e `get_current_admin()`. **Admin não é papel no banco.**
- `backend/app/routes/leads.py:89-104` → `backend/app/services/beta_access.py:295-417` — `create_beta_access_for_lead` cria `User` com `status="active"`, `must_change_password=True`, `temporary_password_expires_at` e `access_invitation_source="landing"` para endereço inexistente; `record_beta_access_audit` em `beta_access.py:157`.
- `backend/app/models.py:241-267` — `User` (`id` UUID, `email` único, `password_hash`, `name`, `status`, `is_banned`, `must_change_password`, `access_invitation_source`, `access_invitation_created_at`, …). **Não há coluna de role.**
- `backend/app/models.py:270-285` — `BetaAccessAuditLog` (`email`, `user_id`, `source`, `action`, `result`, `metadata_json`, `created_at`), que é o destino de auditoria exigido pelo critério 8.
- `backend/app/routes/admin_users.py` — `GET/POST/PUT /api/admin/users*` já atrás de `Depends(get_current_admin)`; é a superfície de admin existente onde a emissão encaixa.
- Migrações: `backend/alembic/versions/`; o `head` atual é **ramo duplo** (`20260809…` → `20260818_0001` e `20260823_0001` → `20260909_0001`). `down_revision` da migração nova é detalhe de Apply (ver D9).
- Não existe nenhum mecanismo de bootstrap de admin (`scripts/card_261_save_winner.py:43`; `ops/` não toca `ADMIN_EMAILS`; sem seed nem comando de promoção). O único caminho atual para o primeiro admin **é** o register — a porta que este card fecha.

UI impact: none
live_route: N/A backend-only; superfície de admin é API, sem rota do catálogo
surface: new

Backend-only: nenhuma rota do catálogo frontend é tocada ou emprestada — nunca `/monitor`, `/favorites`, `/combo/discovery`, `/combo/select`, `landing`. A superfície nova de emissão de convite é **API** (`POST /api/admin/beta-invites`), consumida por operador/admin, e não uma tela do catálogo. A rota pública de entrada do convidado (`${BETA_INVITE_BASE_URL}/beta-invite/<token>`, D3) é superfície nova **do próprio fluxo de convite** — não é rota do catálogo: se o frontend a servir, é uma **página mínima nova do fluxo de convite**, marcada `surface: new` e isenta do clone gate (`scripts/process-fsm/design_clone_gate.py`) porque **não** existe em `scripts/process-fsm/route-landmarks.yaml`; nenhuma página viva é clonada. Protótipo HTML: N/A justificado (`UI impact: none`); o `frontend/src/stores/authStore.tsx:229-238` chama o register mas **não é chamado por nenhuma página** (não há `RegisterPage`), logo não há superfície visual de catálogo a clonar.

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Goals / Non-Goals

**Goals**

- Register **nunca** promove a admin (critério 1, 2, 11).
- Admin como estado persistido, com backfill do admin atual **sem** auto-promoção nem lockout (critério 10).
- Convite de uso único obrigatório nas **duas** portas, vinculado a um endereço certo (critérios 3, 4, 6). A porta `leads` **valida** o convite sem o consumir e sem criar conta: o **consumo** e a criação/redefinição de senha vivem só no fluxo do link (D3/D10).
- Bootstrap de deploy idempotente que substitui a porta fechada (critérios 11, 12, 13).
- Endereço queimado recuperável por convite novo para o mesmo endereço — inclusive quando a conta já existe: o convite emitido por admin para aquele endereço autoriza a **redefinição de senha pelo dono**, sem segunda conta e sem tocar role (critério 7).
- Auditoria de emissão / consumo / expiração em `beta_access_audit_logs` (critério 8).
- Emissão atrás de admin; não-admin recusado (critério 9).
- Fixture do caminho do convite com feliz + bloqueadores (critério 14).

**Non-Goals**

- Verificação de e-mail e provedor transacional (SMTP/Brevo/Resend) — decisão de PO 2026-08-29.
- IdP externo / OAuth.
- Sessão / JWT / cookie HttpOnly (card próprio).
- Rate limit de login / register / leads (card próprio).
- Re-entrada além da redefinição de senha pelo próprio convite — papel, fusão/posse de conta, sessão/JWT — fora deste card. A **redefinição de senha pelo convite** para endereço que **já é** usuário **entra** (D8, critério 7).
- Tela nova de admin (a emissão é API). A única superfície de página admitida é a do **fluxo do convite** (D3): mínima, nova e `surface: new` (isenta do clone gate), se o frontend a servir.
- Novo estado/aresta na FSM, pin, overlay `clients.*.auto`, dual-write noutros clientes.

## Decisions

### D1 — Caminho: convite de uso único, sem verificação de e-mail (decisão de operador 1)

O convite é uma **autorização de acesso** que só pode ser consumida uma vez, por um endereço certo, e expira. Substitui a allowlist de e-mail como porta de entrada.

- Rejeitado: verificação de e-mail com SMTP (não há SMTP configurado; cadastrar terceiro para fechar o furo não é aceitável).
- Rejeitado: manter a allowlist e apenas "tirar o admin do e-mail" (não fecha a segunda porta nem o endereço queimado — critérios 6 e 7).
- Rejeitado: IdP externo/OAuth (fora do recorte; decisão de operador).

### D2 — Contrato HTTP da emissão do convite (superfície nova de admin)

`POST /api/admin/beta-invites`, atrás de `Depends(get_current_admin)` (critério 9):

- Corpo: `{ "email": <EmailStr>, "ttlHours": <int, opcional> }`.
- 201 → `{ "id", "email", "expiresAt", "invitePath" }`. **O `token` em claro é devolvido uma única vez** nesta resposta, no campo `inviteUrl` (link copiável). Nunca é persistido em claro, nunca vai para auditoria, nunca para log.
- 400 → corpo inválido (e-mail malformado; `ttlHours` fora do intervalo permitido).
- 401/403 → sem token / token de não-admin (reusa `get_current_admin`; não inventa autorização nova).
- Reemissão para o mesmo endereço: **permitida** (D6), 201 nova linha; as anteriores são afectadas conforme D6.
- Rejeitado: rota pública de emissão. Rejeitado: emissão a partir de `POST /api/leads` (a landing é anónima; emitir convite ali reabriria a porta). Rejeitado: `POST /api/admin/users` como emissor (cria usuário; a semântica de convite é diferente e a auditoria tem de ser do convite).

### D3 — Formato do link copiável, TTL e armazenamento do token

- **Link:** `${BETA_INVITE_BASE_URL}/beta-invite/<token>` (default `BETA_INVITE_BASE_URL` = URL pública do ambiente; path novo, **não** é rota do catálogo `/monitor` `/favorites` `/combo/*` e não é `landing`). O operador copia e entrega por fora (ex.: WhatsApp). Não depende de envio de e-mail.
- **Token:** opaco, gerado com `secrets.token_urlsafe(32)` (~256 bits). Persistido **apenas** como hash (`token_hash`, ex.: SHA-256 do token) com índice único; comparação por hash em tempo constante. O claro existe só na resposta 201 e no link.
- **TTL:** default **72 h**, configurável por `BETA_INVITE_TTL_HOURS` (env), sobreponível por `ttlHours` no corpo dentro de um intervalo (ex.: 1 h–720 h). Expirado → recusa acionável + auditoria (D5).
- **Rota pública de entrada do convidado (contrato fechado):** `${BETA_INVITE_BASE_URL}/beta-invite/<token>` é **rota nova pública do próprio fluxo de convite** — jamais `/monitor`, `/favorites`, `/combo/*` ou `landing`.
  - `GET` da rota com token válido para o endereço → **formulário de definição de senha**. O endereço entra **pré-preenchido e travado pelo convite** (campo que tem de bater com `invite.email` normalizado, D4/C3) — o convidado não escolhe outro endereço. Token expirado, já consumido, revogado ou de outro endereço → **recusa acionável** no próprio formulário, sem erro genérico (D4/C5).
  - `POST` da mesma rota → **consome o convite uma única vez e define a senha do dono**; nenhuma senha circula por mensagem (decisão de operador 2).
  - **Superfície:** servida pelo fluxo do convite. Se o frontend a servir, é **página mínima nova do fluxo de convite**, mantendo `surface: new` — isenta do clone gate, porque **não** é rota do catálogo viva. Nada de `live_route: landing`, nada de rota do catálogo, nada de clone de página viva.
- **Tabela:** `beta_invites` (nome de trabalho) com `id`, `email` (normalizado, indexado), `token_hash` (único), `created_at`, `expires_at`, `created_by_user_id`, `consumed_at`, `consumed_user_id`, `revoked_at`, `revoked_reason`, `superseded_by_id`. A coluna/tabela exata e o nome final são detalhe de Apply (D9).
- Rejeitado: guardar o token em claro (vaza por dump/log/auditoria). Rejeitado: JWT assinado como convite (não dá consumo único nem revogação sem estado; o requisito é estado). Rejeitado: token curto "código de convite" (curto = adivinhável; o vocabulário do issue pede explicitamente evitar "código de convite").

### D4 — Tópicos fechados do comportamento do convite

- **Vinculação ao endereço:** o consumo compara o endereço normalizado do pedido com `invite.email`. Endereço diferente → recusa **explícita** e auditoria `result="email_mismatch"` (critério 3). O link reencaminhado não serve a outro endereço (decisão de operador 4).
- **Consumo único:** o consumo é uma transição de estado atómica (`consumed_at IS NULL AND revoked_at IS NULL AND expires_at > now()` → grava `consumed_at`/`consumed_user_id` e, na mesma transação, cria o `User` do endereço **sem** conta ou aplica a **redefinição de senha pelo dono** do endereço **com** conta (D8)). Essa transição corre **apenas** no `POST` da rota do link (D3), que é a superfície onde o dono define a senha; a landing (`leads`) valida o convite sem o consumir e **não** cria conta (D10). O mesmo token usado de novo → recusa **explícita** com erro dedicado (ex.: 409/410 com código próprio), **nunca** erro genérico nem 500 (critério 4). Reusar o token não devolve o usuário criado.
- **Expiração:** `expires_at <= now()` → recusa com mensagem acionável ("convite expirado; peça um novo link ao operador") + auditoria `result="expired"` (critério 5).
- **Segredo e resposta pública (alcance fechado):** as portas públicas **não** revelam **privilégio** — endereço em `ADMIN_EMAILS`, endereço na allowlist do beta, endereço inexistente e endereço já existente têm a mesma forma de resposta quando **não** há convite válido (critérios 1, 6). A promessa não cobre a **existência de conta no register**: com convite válido para aquele endereço, o C2 mantém a duplicidade explícita (400 "Email already registered", D5). Na landing (`leads`), a resposta neutra permanece também quanto à existência de conta (C6). A distinção "falha explícita" (critério 4) vive na superfície de quem tem o link/token, não numa enumeração de contas.
- **Auditoria:** emissão (`source="admin_invite"`, `action="beta_invite_issued"`, `result="issued"`), consumo feliz (`result="consumed"`), reuso (`action="beta_invite_consume_failed"`, `result="already_consumed"`), endereço diferente (`result="email_mismatch"`), expirado (`result="expired"`), reemissão/revogação (`action="beta_invite_reissued"`, `result="superseded"`) — todos em `beta_access_audit_logs` com `email`, `user_id` quando exista, e `metadata_json` **sem** token (critério 8). O `source` deixa de ser só `"landing"` e ganha a origem do convite (`landing_invite` / `admin_invite`) — detalhe de Apply.
- **Rate limit de emissão:** **fora** deste card (a emissão fica atrás de admin). Declarado aqui para não ser lido como esquecimento.

### D5 — Register: convite obrigatório, sem promoção, sem allowlist e sem flag a repor a porta

`POST /api/auth/register` passa a aceitar `inviteToken` (nome final do campo = detalhe de Apply) além de `email`/`password`/`name`. **Ordem das verificações (fechada):** (1) validar o convite para o endereço pedido; (2) só então a duplicidade; (3) só então criar a conta.

- **Sem** convite válido (ausente, expirado, consumido, revogado ou emitido para outro endereço) → **nenhum usuário** é criado, e a resposta **não** revela privilégio (`ADMIN_EMAILS`) nem pertença à allowlist do beta (critérios 1, 6). Nesse passo não há sinal de existência de conta: a validação do convite vem antes de qualquer consulta de duplicidade.
- **Com** convite válido para aquele endereço e endereço **já existente** → o comportamento atual de duplicidade permanece **explícito**: 400 "Email already registered" (critério 2). A promessa de não-revelação fica limitada a **privilégio/allowlist** — a existência de conta é o próprio C2 que a mantém explícita, e só é alcançável por quem tem convite válido para o endereço. Esse 400 **não** consome o convite nem toca a conta: a recuperação do endereço queimado com conta existente segue pelo **fluxo de definição de senha do convite** (D8 + D3), nunca pelo register.
- **Com** convite válido e endereço **inexistente** → cria a conta pelo caminho do convite (D4), com a senha definida no fluxo do convite.
- `_closed_beta_registration_emails()` (allowlist ∪ `ADMIN_EMAILS`) **deixa de ser** critério de entrada, e `BETA_PUBLIC_REGISTRATION_ENABLED` **não** repõe a porta fechada: com a flag ligada o register continua exigindo convite de uso único. A flag pode continuar a existir como configuração legada, mas não autoriza criação de conta sem convite (critérios 1 e 6 relidos como a decisão pede).
- O usuário criado por convite é criado como role de usuário comum (**detalhe de Apply**), com a senha que ele mesmo escolheu; nenhum caminho do register grava role de admin.
- Rejeitado: manter a allowlist como "porta de convidados" e exigir convite só para admin (não fecha o endereço queimado da landing). Rejeitado: honrar `BETA_PUBLIC_REGISTRATION_ENABLED` como hoje (reporia exatamente a porta que este card fecha). Rejeitado: prometer não-revelação de existência de conta no register (contradiz o C2, que preserva o 400 explícito depois de o convite ser válido para o endereço).

### D6 — Reemissão, revogação e perda do link (risco declarado no issue)

- Reemitir convite para o **mesmo** endereço é permitido e é o caminho quando o operador perde o link antes do uso.
- Efeito no token anterior (escolha fechada): a **reemissão revoga os convites abertos do mesmo endereço** que ainda estejam válidos (`revoked_at` + `revoked_reason="superseded"` + `superseded_by_id`), para que exista no máximo **um** link vivo por endereço e um link antigo perdido/reencaminhado não continue a valer. Convite já consumido ou expirado não é tocado (fica no histórico para auditoria).
- Rejeitado: coexistência de vários tokens vivos para o mesmo endereço (amplia a superfície de vazamento e dificulta a resposta "qual link vale?"). Rejeitado: só um convite por endereço "para sempre" (impediria a recuperação do link perdido e o critério 7).

### D7 — Role persistida: backfill do admin atual sem auto-promoção

- Nova coluna de role no `User` (ex.: `role` com valores `"user"`/`"admin"`, default `"user"`, `NOT NULL`). A forma final (string versus booleano `is_admin`) é **detalhe de Apply**.
- `is_admin_email()` / `get_current_admin()` passam a responder pela role persistida. `ADMIN_EMAILS` deixa de ser fonte de verdade de autorização; pode permanecer apenas como **entrada** do backfill/bootstrap.
- Backfill da migração: para cada endereço de `ADMIN_EMAILS` que **já tenha conta**, grava role de admin (preserva o admin atual — critério 10). Para endereço de `ADMIN_EMAILS` **sem** conta, a migração **não cria** conta e **não** grava role: quem faz isso é o bootstrap, explicitamente, e **nenhuma outra conta ganha o papel por efeito colateral** (critérios 10, 13; risco "migração antes de enforcement" do issue).
- Rejeitado: derivar admin da env em runtime com fallback (mantém a vulnerabilidade e o lockout ambíguo). Rejeitado: backfill que promove todo endereço de `ADMIN_EMAILS` criando conta na migração (seria auto-promoção silenciosa e misturaria migração com bootstrap).

### D8 — Convite para endereço que já tem conta: restaura o acesso do dono por redefinição de senha

O consumo de um convite **válido**, emitido por admin para **aquele mesmo endereço**, restaura o acesso do dono legítimo. É isto que fecha o critério 7 sem recusa contraditória:

- **Endereço sem conta** → cria a conta normal com a senha que o convidado define no fluxo do convite (mantém D4/D5).
- **Endereço com conta** → o convite **só** autoriza a **redefinição de senha pelo dono**, no fluxo de definição de senha do próprio convite (D3), com o token válido para aquele endereço. **Nunca** toca role/admin, **nunca** sobrescreve senha por efeito colateral anónimo (a nova senha só existe se o dono a definir no `POST` do fluxo do convite) e **não** cria segunda conta.
- **Conta banida ou suspensa** → o convite **não** reabilita a conta: a redefinição de senha não altera `status`/`is_banned` e o login continua a ser recusado como hoje. Declarado, não escondido.
- **"Não entra" intacto:** não é verificação de e-mail nem recuperação de senha anónima — exige o **token de convite emitido por admin para aquele endereço**, e nada acontece sem ele.
- **Register com esse convite** → continua a devolver o 400 de duplicidade (C2, D5) e **não** consome o convite; a recuperação acontece na rota do convite (D3), não no register.
- Fica fora deste card apenas a re-entrada que **não** seja redefinição de senha pelo próprio convite (papel, fusão/posse de conta, sessão/JWT).
- Rejeitado: recusa acionável tipo "endereço já tem conta — use login/recuperação de senha" (contradiz o critério 7 incondicional: o endereço queimado pela landing antiga é exactamente o caso com conta existente). Rejeitado: tratar o convite como promoção, role ou verificação de e-mail (muda o aceite e o modelo de sessão).

### D9 — Ordem de execução: bootstrap → migração/backfill → enforcement; bootstrap idempotente

Ordem obrigatória de deploy (risco nº 1 do issue):

1. **Bootstrap** (`ops/bootstrap_admin.py`, novo comando de deploy) — garante que o endereço já configurado no ambiente (`ADMIN_EMAILS`) **existe e é admin**, sem superfície pública e sem passar por register/landing. Se a conta **já existe**, o comando apenas promove a role (critério 10). Se **não existe** num deploy fresco/base recriada, o comando **cria** essa conta como admin com credencial fornecida explicitamente pelo operador no próprio comando (env/stdin — nunca gerada, nunca impressa, nunca em log); é isto que impede o "deploy novo sem admin nenhum" e é o que substitui a porta que este card fecha (critérios 11, 13). Idempotente: segunda execução não cria conta, não segundo admin e não promove endereço fora da lista configurada (critério 12).
2. **Migração + backfill** (D7) — coluna/tabela e promoção do admin atual que já tem conta. A migração **não** cria conta: quem cria o primeiro admin é o comando de bootstrap, explicitamente.
3. **Enforcement** (D5/D4) — register e leads passam a exigir convite; allowlist e flag deixam de abrir porta.

O comando é idempotente e a migração é reversível; `down_revision` da migração nova aponta para o(s) head(s) vigentes no momento do Apply (hoje há ramo duplo `20260818_0001` / `20260909_0001`) — **detalhe de Apply**, resolvido contra a árvore real.

- Rejeitado: enforcement antes do bootstrap (deploy novo/base recriada fica sem admin nenhum). Rejeitado: bootstrap por endpoint HTTP (superfície pública/autenticada nova para o ato mais privilegiado do sistema). Rejeitado: bootstrap só-promoção (o endereço configurado sem conta ficaria num beco sem saída: register exige convite e não haveria admin para emitir o primeiro — não satisfaz o critério 11). Rejeitado: o bootstrap gerar e imprimir senha temporária (reintroduz credencial gerada e uma superfície de senha; contradiz a decisão de operador 2 — a credencial é fornecida, não impressa).

### D10 — `POST /api/leads`: aceita `inviteToken`; sem convite válido não cria nada

**Fechado:** `POST /api/leads` **aceita** `inviteToken` no corpo — o convite é obrigatório nas **duas** portas (`register` e `leads`, como o issue manda). O caminho de **entrega** deste card, porém, é o **link copiável** gerado pelo admin e entregue pelo operador: a landing **não** emite convite, **não** entrega link e **não** é a superfície de definição de senha (D3).

- **Ordem:** validar o convite para o endereço submetido **primeiro** e usá-lo apenas para decidir a resposta e a auditoria; sem convite válido nada é criado e a resposta não revela privilégio nem existência de conta. A validação **não** consome o convite e **não** queima o endereço.
- **Sem** convite válido: a landing continua a responder o mesmo **202 neutro** — **não cria** `User`, **não** gera senha temporária, **não** marca `must_change_password` nem TTL e **não queima** o endereço (critério 6). O lead fica registado como funil (auditoria), sem conta.
- **Com** convite válido para aquele endereço: a landing **não** consome o convite e **nenhuma** conta nasce em `leads`. O convite fica **aberto** para quem o possui consumir no `POST` da rota do link (D3), que é a superfície onde o dono define a própria senha — nenhuma senha circula por mensagem (decisão de operador 2). O 202 continua neutro e a resposta não distingue convite válido de convite ausente. Se o endereço **já tem conta**, vale D8: `leads` não toca na conta, não cria segunda conta e não toca role; a recuperação é a redefinição de senha pelo fluxo do convite.
- **Senha temporária = caminho legado:** senha temporária gerada, `must_change_password` e `temporary_password_expires_at` pertencem **apenas** ao caminho legado **sem convite** de `beta_access.py`, que continua a existir até o enforcement (D9.3) — e deixam de existir no caminho do convite. O caminho do convite fica limpo: quem define a senha é o dono, no `POST` do link (D3/3.7).
- **Consumo único e senha vivem só no link:** o consumo do convite e a criação/redefinição de senha vivem **apenas** no fluxo do link (D3); `leads` valida o convite para responder e auditar, sem consumir. A transição atómica de D4 (consumir + criar/redefinir no mesmo acto) executa-se no `POST` do link, nunca no `POST /api/leads`.
- **Endereço queimado** (submetido pela landing antiga, **com** conta criada pelo fluxo antigo): quando o operador emite convite para o mesmo endereço, o dono legítimo entra — o convite autoriza a redefinição de senha no fluxo do convite (D8), o endereço **não** fica preso (critério 7) e a landing continua a não tocar a conta. Se a conta estiver banida/suspensa, o convite não a reabilita (D8).
- Rejeitado: **`leads` consumir o convite e criar a conta antes de haver senha** (a N1 deste rework) — com D4 o consumo e a criação acontecem no mesmo acto atómico, mas `leads` não é a superfície onde o dono define a senha: a conta nasceria **sem senha utilizável** (`backend/app/models.py:246` — `password_hash` é `NOT NULL`) e o link já estaria **gasto**, logo (a)+(d) de D4 tornariam (c) impossível. Efeito visível: conta activa sem senha e endereço queimado — C4 e C7 furados por essa porta.
- Rejeitado: leads continuar a criar conta e "só depois" exigir convite (o endereço já está queimado). Rejeitado: leads devolver 403 (quebraria o 202 neutro e a anti-enumeração do critério 6). Rejeitado: fazer da landing a superfície de definição de senha (o dono define a senha no link do convite, D3). Rejeitado: recusa acionável para endereço queimado com conta existente (contradiz o critério 7 — vale D8).

### D11 — Prova e fixture (critério 14)

Fixture de teste do caminho do convite com: emissão → consumo feliz (define senha, cria conta, não promove), consumo repetido (falha explícita), expirado (recusa acionável + auditoria), endereço diferente (recusa + auditoria), **consumo para endereço que já tem conta** (redefine a senha no fluxo do convite, não cria segunda conta, não toca role, não reabilita conta banida/suspensa), register sem convite para endereço privilegiado (nenhuma conta, resposta neutra), register com convite válido para endereço existente (400 C2, convite não consumido, conta intacta), leads sem convite (202 neutro, nenhuma conta), **leads com convite válido (202 neutro, nenhuma conta, convite não consumido e ainda consumível no `POST` do link)**, bootstrap idempotente (duas execuções = mesmo resultado, sem segundo admin), não-admin emitindo (403). Rejeitado: aceitar a fixture como substituto da evidência de deploy — o aceite de deploy é a ordem de D9 verificada.

## Detalhe de Apply (não reabre Design)

Nomes finais de colunas/tabela/campos Pydantic, valor exato de códigos HTTP de recusa do convite (409/410/422), formato do hash do token, `down_revision` da migração, `metadata_json` exacto da auditoria, path/nome do comando de bootstrap e o wiring do `frontend/src/stores/authStore.tsx` (que hoje não é chamado por página nenhuma) são **detalhe de Apply**: P3 aceito, resolvido no Apply, nunca reaberto como P0/P1.

## Riscos / Trade-offs

- **Fechar o register sem bootstrap deixa um deploy novo sem admin nenhum** → mitigação: D9 fixa a ordem bootstrap → migração → enforcement e o comando é entregue **neste** card; sem conta, o comando **cria** o admin configurado com credencial fornecida pelo operador (nunca gerada/impressa), e sem superfície pública nenhuma.
- **Migração antes do enforcement transforma backfill em auto-promoção ou tranca o dono fora** → D7: backfill promove só endereço que **já tem conta**; endereço sem conta não ganha role pela migração; nenhuma outra conta ganha o papel por efeito colateral.
- **Reemissão ambígua (qual link vale?)** → D6: no máximo um convite vivo por endereço; reemissão revoga os abertos e registra `superseded_by_id`.
- **Vazamento do token** → D3: hash em repouso, claro só na resposta 201, nada de token em auditoria/log; link reencaminhado não serve a outro endereço (D4).
- **Enumeração de contas nas respostas** → D4/D5/D10: nas portas públicas, sem convite válido, a resposta só promete não revelar **privilégio/allowlist**; a existência de conta no register é o C2 que a mantém explícita (400) e só depois de o convite ser válido para o endereço; na landing a resposta permanece neutra também quanto a existência de conta; a falha explícita do critério 4 vive na superfície de quem tem o token.
- **`BETA_PUBLIC_REGISTRATION_ENABLED` ligado em algum ambiente** → D5: a flag deixa de repor a porta; é preciso conferir o valor nos ambientes no Apply (a flag não é autorização de convite).
- **Emissão de convite é alvo novo** → D2: atrás de `get_current_admin`; sem limite de emissão neste card (declarado em D4), endereço de rate limit é card próprio.
- **`leads` consumir o convite e criar conta antes de haver senha (N1 deste rework)** → D10: `leads` valida o convite **sem** o consumir e **sem** criar conta; o 202 permanece neutro. O consumo único e a criação/redefinição de senha vivem **só** no `POST` da rota do link (D3/3.7), que é onde o dono define a senha. Consumir em `leads` deixaria a conta activa **sem senha utilizável** (`password_hash` é `NOT NULL`) e o link gasto — C4 e C7 furados por essa porta.
- **Endereço queimado com conta antiga criada pelo fluxo antigo** → D8/D10: o convite emitido para o mesmo endereço restaura o acesso do dono por **redefinição de senha** no fluxo do convite; sem segunda conta, sem role, sem reabilitação de conta banida/suspensa (critério 7).
- **Convite para endereço que já é usuário** → D8: entra neste card **apenas** como redefinição de senha pelo dono; o resto da re-entrada (papel, fusão/posse de conta, sessão) continua fora e é auditado.
- **Compatibilidade de login/refresh** → fora do recorte (sessão/JWT é card próprio); D5 não toca tokens de sessão.

## Migration / Rollout

1. Apply na branch `card-689-convite-uso-unico` (worktree `card-689-convite-unico-admin`) — modelos + migração; serviço de convite + auditoria; register; leads; admin; `ops/bootstrap_admin.py`; fixture.
2. Deploy do comando de bootstrap **primeiro** (D9.1), depois a migração/backfill (D9.2) e só então o enforcement das rotas (D9.3).
3. Verificação no ambiente DEV pelo overlay (`covenant-flow-environments`) quando o Apply chegar aí; sem tocar PROD neste Design.
4. Rollback: reverter rotas para o comportamento anterior e desligar o exigir-convite; a coluna/tabela permanece (migração reversível, mas o backfill de role não deve ser desfeito às cegas para não trancar o admin).
5. Sem pin novo, sem dual-write, sem HTML de protótipo, sem arquivar changes vizinhas.

## Open Questions

Nenhuma. As 4 decisões de operador de 2026-08-29 e as perguntas do issue (ordem, migração, emissor, perda do link, flag pública, e-mail já existente) estão fechadas em D1–D10; *como* fica em D2–D11 e o que sobra é detalhe de Apply.

## Design Critique

**Rodada:** teto 1+1+1 (sem-tela declarada): 1 autor + 1 crítico + 1 rework; o segundo rework foi autorizado por **P0 novo de produto introduzido pelo próprio rework** (N1), com correção localizada e fixada no prompt — não é rodada de polish.

- **Gate (parser real, `proto_dir=None`):** `evaluate_clone_gate(...)` → **PASS (`True`)**; `UI impact: none` / `live_route: N/A` / `surface: new` em linha própria. Nenhuma rota do catálogo (`/monitor`, `/favorites`, `/combo/*`, `landing`) é tocada ou emprestada; a rota do convite é do próprio fluxo.
- **`openspec validate card-689-convite-uso-unico --strict`:** **PASS** (`Change 'card-689-convite-uso-unico' is valid`).

**Cobertura dos 14 critérios:** C1 `specs/closed-beta-access-control/spec.md` + D5; C2 `specs/closed-beta-access-control/spec.md` (400 só depois do convite válido, sem consumi-lo) + D5; C3 `specs/single-use-invite-access/spec.md` (vinculação ao endereço) + D4; C4 (consumo único e falha explícita) + D4; C5 (expirado acionável + auditoria) + D4; C6 `specs/beta-lead-access-hardening/spec.md` (202 neutro, sem conta) + D10; C7 (endereço queimado recupera por redefinição de senha no fluxo do convite) + D8/D10; C8 (auditoria de emissão/consumo/expiração) + D4; C9 (emissão só por admin) + D2; C10 (backfill promove só conta existente) + D7; C11–C13 (bootstrap idempotente, sem segundo admin, sem superfície pública) + D9; C14 (fixture do caminho feliz + bloqueadores) + D11 + `tasks.md` fatia 6.

**P0/P1 da rodada 1 — fechados:**
- **F1 (P0, C7)** — fechado: convite válido emitido por admin para o mesmo endereço **restaura o acesso**; com conta existente, só **redefinição de senha pelo dono** no fluxo do convite (D8); sem 2ª conta, sem role, banido/suspenso não reabilitado.
- **F2 (P1, superfície de entrada)** — fechado: rota nova pública **do fluxo do convite** (`GET` formulário com endereço travado / `POST` consome e define a senha), `surface: new`, sem clone de página viva (D3).
- **F3 (P1, ordem × duplicidade)** — fechado: ordem **convite → duplicidade → criação**; a não-revelação fica limitada a **privilégio/allowlist**; o 400 do C2 permanece explícito depois do convite válido e **sem** o consumir (D5).
- **F4 (P1, resíduos de senha temporária)** — fechado: o caminho do convite não produz senha temporária, `must_change_password` nem TTL; essa semântica fica condicionada ao caminho **legado sem convite** (D10).
- **F5 (P1, delta do convite vs decisão de operador 4)** — fechado: requirement e scenarios próprios para endereço com conta em `specs/single-use-invite-access/spec.md`.

**P0 novo da rodada de verificação — fechado:**
- **N1 (P0, produto/contrato — caminho `leads`)** — o rework anterior mandava `leads` consumir o convite **e** criar a conta activa, com a senha definida só no link: com D4 (consumo = transição atómica) e `password_hash NOT NULL`, a conta nasceria sem senha utilizável e o link já gasto (C4/C7 furados). Fechado em D10 + `specs/beta-lead-access-hardening/spec.md`: em `POST /api/leads` um convite válido **não** é consumido e **nenhuma** conta nasce — 202 neutro, convite **aberto** para o `POST` do link, endereço não queimado; alternativa rejeitada registada nominalmente.

**P3 aceitos (Apply) — não reabrem Design:** nomes finais de coluna/tabela/campos Pydantic e o par `invitePath`/`inviteUrl`; código HTTP exacto das recusas do convite (409/410/422); formato do hash do token e índice único; `metadata_json` exacto da auditoria; `down_revision` da migração (o head real é único: `20260909_0001`); comportamento do bootstrap com `ADMIN_EMAILS` vazio e recuperação do admin configurado cuja senha é desconhecida/expirada; precisão de "only door" = superfície de produto (o bootstrap de host é a excepção declarada); forma de servir o formulário do convite (backend ou página mínima nova) e o wiring de `frontend/src/stores/authStore.tsx`; fixar que a superfície que consome é a que define a senha.

**Disposition:** sem P0/P1 de produto aberto — o gate do autor passa, `openspec validate --strict` passa, os 14 critérios mapeiam, os 5 achados da rodada 1 e o P0 novo (N1) estão fechados. Segue para **Aprovação de Design** (T5); a aprovação continua a ser do Alan (T7).
