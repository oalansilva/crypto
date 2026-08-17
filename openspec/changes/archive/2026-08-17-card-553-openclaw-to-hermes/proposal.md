## Why

O Cripto Farol ainda chama o Gateway WS OpenClaw (`OPENCLAW_GATEWAY_*`, porta 18789) no agent chat, lê secrets em `/root/.openclaw` no scan Telegram e aponta o unit de leads para HOME/CODEX_HOME do OpenClaw. O gateway OpenClaw está desabilitado; o runtime ativo do Alan é o Hermes em `127.0.0.1:8642`. Manter OpenClaw no caminho operacional deixa chat, alertas e leads quebrados ou acoplados a um runtime aposentado.

## What Changes

- Substituir o cliente OpenClaw Gateway WS por um cliente Hermes HTTP `/v1/responses` com timeout, idempotência, sanitização e autenticação opcional.
- Migrar `POST /api/agent/chat`, testes e configs para Hermes; respostas continuam não vazias e a sessão permanece estável.
- Migrar `ops/run_monitor_telegram_alert_scan.py` para secrets/config canônicos (sem `/root/.openclaw`).
- Atualizar o template systemd de leads para não usar HOME/CODEX_HOME do OpenClaw.
- **BREAKING:** remover fallback operacional OpenClaw depois da validação (nenhum código runtime ativo depende de `OPENCLAW_GATEWAY_*` ou porta 18789).
- OpenClaw permanece apenas como histórico explicitamente classificado em docs.

## Capabilities

### New Capabilities

- `hermes-agent-runtime`: transporte Hermes para agent chat (cliente `/v1/responses`, timeout, idempotência, sanitização, auth opcional).

### Modified Capabilities

- `02-agent-chat-favorites`: backend deixa de usar OpenClaw Gateway WS e passa a usar Hermes; o contrato HTTP do chat permanece.
- `monitor-telegram-alerts`: o scan operacional não lê `/root/.openclaw`.
- `maintenance`: templates/scripts runtime não apontam HOME/CODEX_HOME do OpenClaw.

## Impact

- Backend: `backend/app/routes/agent_chat.py`, novo cliente Hermes, remoção/aposentadoria de `openclaw_gateway_client.py`, testes `test_gateway_and_agent_chat.py`.
- Ops: `ops/run_monitor_telegram_alert_scan.py`, `ops/systemd/cripto-farol-leads.service`.
- Spec legado `openspec/specs/02-agent-chat-favorites.md`.
- Superfície de UI do chat: inalterada (mesmo endpoint e modal). Runtime Hermes precisa estar acessível no host.
