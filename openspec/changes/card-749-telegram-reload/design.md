## Context

Card #749 (P0, `Monitor`, `Prioridade P0`, `Status=Design`) é bug pós-homologação do #747 em DEV: vínculo Telegram persiste no banco (`User.telegram_chat_id`, `telegram_alerts_enabled=true`, `telegram_linked_at=27/08/2026 00:50:58`, `backend/app/models.py:261`) mas reload de `/profile` mostra `Status: Não vinculado` e toggle desligado até próxima interação (salvar/Gerar vínculo). Logs backend: dois `GET /api/users/me/telegram-settings` por abertura — um 200 e outro 401.

Investigação `grill-card` + subagent explore:

- `frontend/src/components/telegram/TelegramAlertsForm.tsx:36-46` faz `authFetch(.../telegram-settings)` e `catch { setSettings(null); onSettingsChange?.(null) }` → `settings===null` renderiza `Status: Não vinculado` (`:165`) e `checked={Boolean(settings?.telegramAlertsEnabled)}` desligado (`:147`), mascarando o 200 válido.
- `frontend/src/lib/authFetch.ts:142` explica retry legítimo: primeiro `fetch` sem `Authorization` válido → 401 → `refreshAuthToken()` (`POST /api/auth/refresh`) → retry com token renovado → 200. Em DEV `StrictMode` (`main.tsx:15`) duplica `useEffect` e `AuthProvider` (`authStore.tsx:126`) verifica `/api/auth/me` em paralelo — concorrência explica 401 observado, não duplicidade de endpoint no `ProfilePage` (`ProfilePage.tsx:208` só monta `TelegramAlertsForm` sem `onSettingsChange`).
- `ProfilePage.tsx:41` `GET /api/users/me` (perfil) ≠ `telegram-settings`; não há dois fetches de `telegram-settings` no Perfil fora do retry. `MonitorStatusTab.tsx:395` busca `telegram-settings` apenas em `/monitor`, mas replica o mesmo `catch` frágil.
- Backend `backend/app/routes/user_telegram.py:43` e `user_telegram_service.py:26` definem `linked=bool(telegram_chat_id)` e `hasPendingLinkToken`; sem bug — é frontend.
- Testes existentes (`visual-critical.spec.ts:184` mock `linked:false`) não cobrem reload `linked:true` nem 401 transitório.

Stakeholder: operador vinculado que confia no opt-in; subsistema `user-telegram-alerts` compartilhado Perfil↔Monitor.

**UI impact: none.** Correção de corrida/estado em formulários e wrapper `authFetch` existentes. Nenhuma rota nova, nenhum componente visual novo, nenhum token de marca novo. Demonstração é comportamental (reload mostra `Vinculado`); prototype HTML não acrescenta superfície — validação é via testes (unit + e2e reload). Pipeline Impeccable desta coluna Design = N/A com justificativa.

## Goals / Non-Goals

**Goals:**
- Reload de `/profile` com conta vinculada exiba `Status: Vinculado`, `linkedAt`, `botUsername` e toggle `Receber alertas Telegram` ligado sem interação extra (critério 1).
- Eliminar pisca `Não vinculado` causado por `401 transitório` seguido de 200: defense in depth — Form não zera `settings` quando já houve 200 válido (só `setSettings(null)` se primeira carga falhar) + `authFetch` não expõe 401 ao caller quando refresh sucede (Q1=C).
- Mitigar race `StrictMode` double mount sem `AbortController`/`cancelled` e estabilizar deps `useCallback` (`[onSettingsChange, toast]` voláteis → `useRef`/memo) (Q4=A).
- Corrigir também `MonitorStatusTab` no mesmo card para manter sync Perfil↔Monitor do mesmo flag `telegram_alerts_enabled` (Q2=A).
- Preservar semântica de `401 real` (refresh falha → `notifyAuthSessionCleared` → logout) sem mascarar como vinculado (critério 3).
- Travar regressão com unit mockando 401→200 + e2e Playwright reload `/profile` com `linked:true` (Q3=A).

**Non-Goals:**
- Reabrir escopo #747 (matriz position-aware, Bot API, dedupe, auditoria, destino DM vs Grupo Crypto, `MONITOR_TELEGRAM_BOT_USERNAME`, webhook secret, `telegram_link_token`).
- Mudança de modelo de bot, `telegram_link_token`/`hasPendingLinkToken`, execução de ordem, filtro `Em portfólio`, alterações em `monitor-telegram-alerts` além de `telegram-settings`.
- Refactor geral de `authFetch` além do retry encapsulado e guard `isLoading` mínimo; rework de `useToast` global.
- Novo prototype visual, nova rota, ou copy nova — `UI impact: none`.

## Decisions

1. **Defense in depth no 401 transitório (Q1=C) — Form preserva stale + authFetch encapsula retry.**
   - Form: `loadSettings` mantém `settings` anterior em `catch` quando `settings !== null` ou `prevSettingsRef.current !== null`; só faz `setSettings(null)` se nunca houve sucesso; mantém `loading` até retry final; toast apenas em 401 real ou se nunca houve 200.
   - authFetch: já faz retry e retorna 200 quando refresh sucede; garantir que caller não veja 401 intermediário (hoje já retorna 200; reforçar que 401 só retorna quando `refreshToken` ausente/falha e `notifyAuthSessionCleared` disparado). Alternativa só Form (A) deixaria caller ver 401 real como erro genérico; só authFetch (B) deixaria Form ainda zerar em race de dois mounts; guard `isLoading` (D) sozinho bloquearia render mas não corrige `catch` frágil — rejeitadas.
   - Escolha C cobre ambos os vetores e mantém logout real visível.

2. **Estabilizar deps + Abort (Q4=A) — `TelegramAlertsForm` com `AbortController`/`cancelled` e deps estáveis.**
   - `loadSettings` passa `signal` para `authFetch` (se suportado) ou flag `cancelled` em `useEffect(() => { let cancelled=false; load(); return ()=>{cancelled=true} }, [loadSettings])`; checar `cancelled` antes de `setSettings/setLoading`.
   - `useCallback` deps: remover `onSettingsChange` volátil (guardar via `useRef` atualizado em `useEffect`) ou memoizar no pai; `toast` é global estável (`use-toast.ts:141`) mas objeto `useToast()` recria — usar `toast` global direto. Alternativa só Abort (B) deixaria re-fetch desnecessário por `onSettingsChange` recriado; só deps (C) deixaria race de unmount vencer; D (nada) confiaria só em Q1 — rejeitadas.

3. **Escopo inclui Monitor (Q2=A) — mesmo fix no `MonitorStatusTab`.**
   - `fetchMonitorContext` em `MonitorStatusTab.tsx:395` replica `authFetch(.../telegram-settings)` → aplicar mesma lógica de não zerar em 401 transitório (preservar `telegramAlertsEnabled` anterior) e `Abort`/guard; `toggleTelegramAlerts` já faz `PATCH` idempotente. Alternativa só Perfil (B) deixaria Monitor com mesmo pisca ao recarregar `/monitor`; C (só se reproduzir) adiaria sync exigido no critério 4 — rejeitadas.

4. **Guard opcional `AuthProvider.isLoading` em `ProfilePage`.**
   - Avaliar `const { isLoading } = useAuth()` (`authStore.tsx:31`) e só montar/chamar `loadSettings` quando `isLoading===false` ou quando `accessToken` já verificado; reduz corrida `AuthProvider` verify vs `telegram-settings` sem bloquear render. Não obrigatório se Q1+Q4 já mitigam, mas documentado como melhoria de observabilidade. Alternativa sem guard aceita (não bloqueia Design).

5. **Testes unit + e2e (Q3=A).**
   - Unit: `frontend/src/components/telegram/TelegramAlertsForm.test.tsx` mocka `authFetch` sequenciando 401→refresh→200 e valida que `linked:true` permanece após 401 transitório e que `setSettings(null)` só em 401 real.
   - e2e: `frontend/tests/e2e/visual-critical.spec.ts` (ou novo `telegram-reload.spec.ts`) mocka `GET /api/users/me/telegram-settings` com `linked:true`, `linkedAt`, `botUsername`, `telegramAlertsEnabled:true` e valida `data-testid="telegram-alerts-form"` exibe `Vinculado` e toggle ligado após `page.goto('/profile')` + `page.reload()`; estende `installStableApiMocks` para cenário `linked:true`. Alternativa só e2e (B) perderia cobertura de retry 401→200 em isolamento; só unit (C) perderia validação visual de reload — rejeitadas.

6. **401 real vs transitório — distinguir via `refreshAuthToken` outcome.**
   - `authFetch.ts:93` `refreshAuthToken` retorna `null` e chama `notifyAuthSessionCleared` (`missing-refresh-token`/`refresh-failed`/`refresh-invalid`/`refresh-error`) → caller recebe 401 original e deve tratar como logout (não preservar stale como vinculado). `TelegramAlertsForm` distingue: se `catch` coincide com `notifyAuthSessionCleared` recente ou se `loadAuthTokens()` ainda sem token, então `setSettings(null)` e não toast de retry. Alternativa preservar sempre stale rejeitada (mascara logout).

## Risks / Trade-offs

- [Preservar stale oculta logout] → Mitigação: checar `refreshFailed`/`missing-refresh-token` e só preservar quando `authFetch` indicou retry ok; critério 3 valida logout.
- [Race StrictMode dois mounts] → Mitigação: `cancelled`/`AbortSignal` + deps estáveis; e2e em DEV valida não pisca.
- [Monitor duplicar fix diverge] → Mitigação: mesmo padrão aplicado, sync validado; diff reviewers checam `MonitorStatusTab` vs `TelegramAlertsForm`.
- [StrictMode só em DEV mas e2e pode passar em PROD] → Mitigação: unit cobre 401 transitório isolado sem depender de StrictMode.
- [Deps `onSettingsChange` volátil ainda causa re-fetch] → Mitigação: `useRef` no Form; `ProfilePage` não passa `onSettingsChange` (já estável), mas documentar para futuros pais.
- [Logs backend continuam 401+200 legítimo] → Trade-off aceito: logs mostram retry legítimo; teste que falha antes do fix é evidência de regressão, não ausência de 401.

## Migration Plan

Apply (branch `card-749-telegram-reload` em `Status=Pronto para Dev` → `Em desenvolvimento`):

1. Editar `frontend/src/components/telegram/TelegramAlertsForm.tsx` (defense in depth + Abort + deps).
2. Editar `frontend/src/lib/authFetch.ts` se necessário para não expor 401 transitório (reforçar retorno 200 quando retry sucede; manter `notifyAuthSessionCleared` em falha real).
3. Editar `frontend/src/components/monitor/MonitorStatusTab.tsx` (mesmo fix para `telegram-settings`).
4. Opcional: `frontend/src/pages/ProfilePage.tsx` guard `isLoading` do Auth.
5. Criar/atualizar testes unit + e2e (mock `linked:true`, sequência 401→200, reload).
6. `openspec validate --all` + `npm test`/`pytest` focado; `Status=Em desenvolvimento` → `pedir_review` → `diff-reviewer`+`code-reviewer` no diff `HEAD` não commitado → commit SHA → `diff-reviewer` em `origin/develop...HEAD` → push → `Status=QA` → `qa-gate` + Playwright → `integrar_develop` → `Done`; `Pronto` só em release com `release-guard`.

Rollback: reverter os 3 arquivos frontend para estado pré-fix; sem migração de banco; sem tocar `backend/app/routes/user_telegram.py` ou `models.py`.

## Open Questions

Fronteira zerada após grill Round 1 (2026-08-28). Nenhuma bloqueante.

Residual não bloqueante de observabilidade: logs 401+200 permanecem (retry legítimo) — evidência de fix é teste que falha antes do fix, não ausência de 401.

## UI impact

**none** — correção de estado/race em formulários existentes (`TelegramAlertsForm`, `MonitorStatusTab`) e wrapper `authFetch`. Nenhum componente visual novo, rota nova, ou token de marca novo. `Vinculado`/`Não vinculado` e toggle já existem; fix garante que reload reflita backend sem prototipar nova tela. Prototype N/A.

## Prototype

N/A — `UI impact: none`. Não há tela nova a prototipar; aceite validado por reload que mostra `Status: Vinculado` + toggle ligado e por testes unit/e2e que travam regressão.

## Prototype Validation

N/A — sem superfície visual nova. Browser gate não aplicável; validação é via e2e Playwright reload em `/profile` com mock `linked:true` e unit de 401 transitório. Se fosse `UI impact: affected`, abriria `https://dev.criptofarol.com.br/prototypes/card-749-telegram-reload/` em desktop+mobile e asserts de `data-testid`.

## Impeccable pipeline (esta coluna Design)

N/A — `UI impact: none`. Sem shape/protótipo/crítica/audit/polish/browser de tela de produto. Harness de processo não exige pipeline Impeccable nesta coluna; `DESIGN.md` canónico permanece autoridade visual. Justificativa não reduz gates de Design nem aprovação humana T7.

## Design Critique

- P0: nenhum — `catch { setSettings(null) }` mascarando 200 válido é P0 do bug; defense in depth + Abort + distinção 401 transitório vs real cobre sem mascarar logout; `q_git` Guard continua bloqueando Agent em `develop`/`main`.
- P1: nenhum — race `StrictMode` double mount e deps `[onSettingsChange, toast]` instáveis cobertos por `cancelled`/`Abort` + `useRef`; Monitor incluído evita drift Perfil↔Monitor; testes unit+e2e travam regressão.
- P2 (accepted-residual): logs backend continuam com 401+200 retry legítimo — aceito; observabilidade via teste que falha antes do fix.
- P3 (accepted-residual): guard opcional `isLoading` em `ProfilePage` pode ficar como melhoria futura se Q1+Q4 já mitigam — não bloqueia.

Riscos não bloqueantes: nenhum P0/P1 aberto; `UI impact: none` sem prototipagem; Impeccable/Snapshot N/A justificado abaixo.

Referências: `openspec/changes/card-749-telegram-reload/proposal.md` + `specs/user-telegram-alerts/spec.md` + issue #749 (DoD completo) + `frontend/src/components/telegram/TelegramAlertsForm.tsx:36` + `frontend/src/lib/authFetch.ts:142`.

Prototype: N/A — `UI impact: none`, correção de reload/401 (ver `## Prototype`).

Snapshot (git-tracked; Gist não envia esta pasta): N/A justificado para `UI impact: none`.

Design Agent verdict: PASS

## Apply contract

- Editar só: `frontend/src/components/telegram/TelegramAlertsForm.tsx`, `frontend/src/components/monitor/MonitorStatusTab.tsx`, `frontend/src/lib/authFetch.ts` (reforço encapsular retry), `frontend/src/pages/ProfilePage.tsx` (guard opcional), testes `frontend/src/components/telegram/TelegramAlertsForm.test.tsx` / `frontend/tests/e2e/*telegram*.spec.ts`, `openspec/changes/card-749-telegram-reload/specs/**`, `openspec/specs/**` via archive.
- Zero `backend/app/routes/user_telegram.py`, zero `backend/app/models.py` (`linked=bool(chat_id)` imutável), zero `ops/bootstrap_env.py`, zero `main` direto, zero `Environment=` com secret.
- Fix MUST: defense in depth (preservar stale só se houve 200 prévio + authFetch só expõe 200 quando retry ok), Abort/cancelled + deps estáveis, Monitor junto, não mascarar 401 real (`notifyAuthSessionCleared` → logout), reload mostra `Vinculado`/`linkedAt`/`botUsername`/toggle ligado, critérios 1-6 verdes, testes unit+e2e cobrindo 401 transitório e reload `linked:true`.
