## Context

Card [#686](https://github.com/oalansilva/crypto/issues/686). `GET /api/logs/tail` em `logs.py` só tem allowlist de nomes; sem `Depends`. JSON inclui `path` absoluto. `BackendLogViewer` faz `fetch` cru. Forgot-password em `auth.py` loga e-mail e reset link em INFO. HTTP 200 anônimo em DEV e PROD.

**Problema:** qualquer cliente lê o execution log (e-mails, links de reset) e o path do host.

**Usuário:** admin no Combo que abre **Ver logs** para acompanhar a otimização.

**Hipótese:** exigir admin + Bearer, omitir path e parar o INFO de reset fecha o vazamento sem mudar o layout do modal.

**Resultado:** 401/403 no banner já existente; sessão autenticada continua “Aguardando eventos…” / linhas; JSON sem filesystem path.

**UI impact: affected** — só o contrato do viewer (Bearer + estados 401/403). Sem redesenho.

### Recorte (shape)

- **Audience:** admin autenticado no Combo; modo Operate.
- **Outcome:** poll com Bearer; 401 = não logado; 403 = não admin; path nunca na UI nem no JSON.
- **Direction:** clone shell autenticado (sidebar 224px, tokens `--bg-*`) + modal atual do `BackendLogViewer`; delta só credencial e copy de erro.
- **Scope:** `logs.py`, `auth.py` forgot-password, `BackendLogViewer` fetch. Fora: redesenhar viewer, rotação de log, outros endpoints.

## Goals / Non-Goals

**Goals:**

- `Depends(get_current_admin)` no tail.
- JSON sem chave `path`.
- Forgot-password sem e-mail/token/link em INFO.
- Viewer com Bearer; 401/403 observáveis.

**Non-Goals:**

- Redesenhar o viewer ou o Combo.
- Rotação / retenção de arquivo de log.
- Auth em massa de outras rotas.

## Decisions

1. **`get_current_admin`, não `get_current_user`.** Alternativa rejeitada: qualquer logado leria o mesmo arquivo. O briefing pede admin; 401 vs 403 já existem no middleware.

2. **Omitir `path` em todos os ramos do tail (arquivo ausente incluso).** Alternativa: string vazia. Rejeitada: chave ainda vaza forma; aceite é não devolver path.

3. **`file_id` permanece** (dev:inode opaco). Não é path de filesystem.

4. **Cliente: `authFetch`.** Alternativa: header manual. Rejeitada: o app já persiste JWT em `localStorage` via `authFetch`.

5. **401/403 no banner amber existente** (`HTTP 401` / `HTTP 403` + frase curta). Sem layout novo, sem toast paralelo.

6. **Forgot-password: log genérico em INFO** (ex. “reset requested”) sem e-mail/token/URL. Alternativa: DEBUG com e-mail. Rejeitada: o briefing veta INFO com esses campos; DEBUG ainda pode vazar em collectors — Apply não loga os três.

7. **Requisito legado “campos atuais incluem path” é MODIFIED.** Consumidores que liam `path` quebram; aceito.

## Apply contract

- `tail_log`: `Depends(get_current_admin)`; remover `path` do dict de resposta.
- `BackendLogViewer`: `authFetch` (ou Bearer equivalente) em sessão e poll; mapear 401/403 no `error` existente; não mudar chrome do modal.
- Forgot-password: não interpolar e-mail, token ou link em log INFO.
- Testes: 401 sem token, 403 user, 200 admin sem `path`; viewer envia Authorization; reset log sem os três campos.
- Não redesenhar UI; não rotação de log; não editar DESIGN.md.

## Risks / Trade-offs

- [Clientes anônimos do tail] → 401; esperado.
- [Admin no Combo sem Bearer] → 401 no banner até Apply no viewer.
- [Logs INFO antigos já no disco] → fora; não rotacionar neste card.
- [Contrato legado com `path`] → breaking; documentado.

## Migration Plan

1. Código após T7; sem Alembic.
2. Deploy: anônimo deixa de ler o arquivo; admin autenticado no Combo continua o modal.
3. Rollback = revert (reabre vazamento).

## Open Questions

Nenhuma. Fronteira no briefing.

## UI impact

**affected** — o viewer passa a autenticar e a mostrar 401/403 no banner já existente. Layout, densidade, título, rolagem e Fechar permanecem.

## Prototype

- URL: https://dev.criptofarol.com.br/prototypes/card-686-logs-tail-auth/
- Path: `frontend/public/prototypes/card-686-logs-tail-auth/index.html`
- Digest: `c86f9c9c2c9d9524d59cdb1268314825a8393d74ff8c3facb750700fb69eaee4`
- Viewports: desktop 1440×900; mobile 390×844
- Base: clone do shell autenticado (`card-664-discovery-restore-reload`) + chrome do `BackendLogViewer`
- Estados: default (admin + Bearer + Aguardando eventos…); 401; 403
- Delta: header Authorization; copy 401/403; JSON simulado sem `path`

## Prototype Validation

URL: https://dev.criptofarol.com.br/prototypes/card-686-logs-tail-auth/  
Digest validado: `c86f9c9c2c9d9524d59cdb1268314825a8393d74ff8c3facb750700fb69eaee4`

Viewports: desktop 1440×900; mobile 390×844. Em cada um: default, 401, 403 (abrir **Ver logs**).

Asserts (todos ok):

- Título **Logs do Backend**, botão **Fechar**, sidebar 224px no desktop
- Default: `Authorization: Bearer proto-admin-token`, `Aguardando eventos…`, sem banner
- 401: banner `HTTP 401 — faça login`, Authorization ausente
- 403: banner `HTTP 403 — apenas admin`, Bearer presente
- UI do modal sem path `/srv/` e sem `full_execution_log.txt`
- Viewer não redesenhado (mesmo chrome)

Navegador: Chromium Playwright real. Sem erros de página. 404 de consola residual sem recurso HTTP correspondente (sem impacto no fluxo).

## Design Critique

- **P0:** (nenhum)
- **P1:** (nenhum)
- **P2:** Host Combo stub; botão **Ver logs** não replica zinc claro do `ComboConfigurePage` — **aberto**, aceito (delta só no modal)
- **P2:** Protótipo não modela “Rolagem pausada” / **Ir para o fim** — **aberto**, fora do delta auth
- **P2:** Modal sem focus trap / foco inicial (Tab escapa para sidebar) — **aberto**, polish opcional no Apply; produção já trava foco
- **P3:** Copy 401/403 ligeiramente mais longa que asserts mínimos — **fechado**
- **P3:** Scaffolding `.prototype-toolbar` / `#auth-probe` — **fechado**, não vai para Apply
- **P3:** Contraste `--text-muted` marginal AA — **fechado**, aceito
- **P3:** Botão **Ver logs** dark vs zinc em produção — **fechado**, aceito

**Referências:** protótipo https://dev.criptofarol.com.br/prototypes/card-686-logs-tail-auth/ (digest `c86f9c9c2c9d9524d59cdb1268314825a8393d74ff8c3facb750700fb69eaee4`); change `openspec/changes/card-686-logs-tail-auth/`.

**Snapshots Impeccable:** `.impeccable/critique/686-card-686-logs-tail-auth-A.md`, `.impeccable/critique/686-card-686-logs-tail-auth-B.md`.

**Design Agent verdict: PASS**
