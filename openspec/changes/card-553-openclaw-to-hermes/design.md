## Context

Agent chat, Monitor Telegram scan and the leads unit still assume OpenClaw (`ws://127.0.0.1:18789`, `/root/.openclaw`). The gateway is disabled; Hermes answers on `127.0.0.1:8642`. Product UI of chat/Favorites does not change.

## Goals / Non-Goals

**Goals:**
- Hermes client for `/v1/responses` with timeout, idempotency, sanitization, optional auth.
- Agent chat, Telegram scan and leads template off OpenClaw.
- Tests cover success, timeout, empty reply, missing auth.

**Non-Goals:**
- Redesign of Favorites/chat UI.
- Multi-tenant hardening.
- Recreating OpenClaw as fallback.
- Changing Clara or other Hermes apps.

## Decisions

1. **HTTP Hermes, not WS OpenClaw.** Card specifies `/v1/responses`. Keep `POST /api/agent/chat` stable, including `thinking` (off|minimal|low|medium|high) mapped into the Hermes request. Do not remove the modal control or make it a silent no-op.
2. **Fail closed, no OpenClaw fallback.** Timeout remains 180s (current gateway budget). Empty/timeout/unsafe = same JSON error shape the modal already reads (`detail`), without leaking secrets.
3. **Secrets:** env/files already used by Cripto/Hermes; never `/root/.openclaw`.
4. **Leads HOME:** repo-local or Hermes home, not OpenClaw CODEX_HOME.
5. **UI impact: none.** Transport-only.

## UI impact

`none` — mesmo modal/endpoint; só o transporte muda.

## Prototype

N/A. Sem tela nova. Justificativa: migração de runtime/ops; Alan valida chat não vazio e ausência de `OPENCLAW_GATEWAY_*`, não um mock.

## Impeccable Brief

N/A — `UI impact: none`.

## Impeccable Critique

N/A — `UI impact: none`.

## Impeccable Audit

N/A — `UI impact: none`.

## Impeccable Trace

N/A — `UI impact: none`.

## Risks / Trade-offs

- [Hermes `/v1/responses` payload diferente do Gateway WS] → Mitigação: adaptar parser no cliente; testes de contrato; smoke autenticado depois de Pronto para Dev.
- [Chat some se Hermes estiver down] → Aceito: OpenClaw já está down; fail-closed é o estado verdadeiro.
- [Leads unit precisa de HOME válido para gog] → Usar path canônico já usado pelo funil, não inventar `/root/.openclaw`.

## Migration Plan

1. Publicar OpenSpec no #553 e aguardar Alan em Aprovação de Design → Pronto para Dev.
2. Implementar cliente + rotas + testes na branch da change.
3. Atualizar scan Telegram e template de leads.
4. Remover cliente WS OpenClaw do runtime ativo.
5. QA visual obrigatória (sem mudança de UI: baseline existente).

## Open Questions

Nenhuma. Auth opcional Hermes via env (`HERMES_API_TOKEN` ou equivalente já usado no host).

## Design Critique

- Escopo: transporte Hermes; modal/endpoint de chat inalterados.
- Crítica isolada (Task inherit, read-only): P1 de `thinking`/timeout/`detail` corrigidos no design e na spec.
- Regressão de produto: `thinking` permanece mapeado; timeout 180s; erro no campo `detail`.
- Superfície visual nova: nenhuma (`UI impact: none`).
- Prototype: N/A justificado.

## Prototype Validation

N/A — sem protótipo navegável.

Design Agent verdict: PASS
