## 1. Cliente Hermes

- [x] 1.1 Criar cliente HTTP para `POST /v1/responses` com timeout, idempotência, sanitização e auth opcional
- [x] 1.2 Ligar `POST /api/agent/chat` ao cliente Hermes e remover uso runtime de `OPENCLAW_GATEWAY_*` / porta 18789
- [x] 1.3 Aposentar `openclaw_gateway_client.py` do caminho ativo (delete ou wrapper morto classificado)

## 2. Ops

- [x] 2.1 Migrar `ops/run_monitor_telegram_alert_scan.py` para secrets/config canônicos (sem `/root/.openclaw`)
- [x] 2.2 Atualizar `ops/systemd/cripto-farol-leads.service` para não usar HOME/CODEX_HOME OpenClaw

## 3. Testes e docs

- [x] 3.1 Atualizar testes de agent chat (sucesso, timeout, vazio, sem fallback OpenClaw)
- [x] 3.2 Atualizar spec `02-agent-chat-favorites` notes se ainda citarem Gateway WS no main spec no apply
- [x] 3.3 QA visual obrigatória (baseline existente; sem mudança de UI)
