## Why

Alan (única conta PROD com Telegram vinculado e alertas ligados) não recebe DM de venda/saída do Monitor: o disparo diário ainda passa por um cron Hermes com LLM, que falha desde 07/09/2026 (inclusive 10/09) com modelo inexistente — o scanner Python não parte. O envio já está em Pronto (#747, Bot API); falta o produto acordar o scan.

## What Changes

- Disparo diário no host do produto, **1×/dia às 08:05 BRT** (OnCalendar 11:05 UTC, herdado do #200), **sem LLM**.
- O envio continua o caminho #747 (DM via Bot API, matriz position-aware, opt-in, `/link`). Este card só muda **quem acorda** o scan.
- **Na instalação em PROD:** um disparo imediato que envia as DMs do que mudou desde a linha de base de 06/09/2026 (lote possível; vale o teto anti-ruído já existente).
- **DEV neste card:** o mesmo disparo no host DEV, **sem** o bot/token/webhook de PROD.
- **Corte do Hermes:** desligar o cron `Monitor Telegram sinais diario` **só depois** de 1 run PROD verde (enviou ou nada a enviar). Depois do corte, um único disparo por dia. Este card **não** liga o job Hermes como runtime do produto.
- Falha do disparo fica **só no journal** do unit (padrão candle-writer); não há aviso no Telegram de “o relógio quebrou”.
- Overlay `environments.*.services` e `docs/monitor-telegram-alerts.md`: o agendamento passa a ser do Cripto Farol, não do Hermes.
- `UI impact: none`.

Fora (grelha): matriz position-aware, webhook `/link`, `sendMessage`, opt-in, teto anti-ruído; aumentar cadência (30/60 min); consertar o modelo LLM no Hermes; reescrever o scanner além do necessário para o disparo (env, timeout, lock); enviar para grupo/tópico; DM operacional de falha do disparo.

## Capabilities

### New Capabilities

- (nenhuma) — o comportamento entra na capacidade já existente de alertas Telegram do Monitor.

### Modified Capabilities

- `monitor-telegram-alerts`: o scan diário passa a ser acordado por timer systemd do produto (oneshot+timer), não pelo cron Hermes; instalação PROD dispara já e envia transições desde 06/09/2026; DEV usa env DEV sem bot PROD; falha do disparo não gera DM extra; overlay e doc de operação deixam de apontar o Hermes como agendador.

## Impact

- Ops: units `criptofarol-{dev,prod}-*-` oneshot+timer no padrão candle-writer; installer por `--env`; `ops/run_monitor_telegram_alert_scan.py` já existente (só env/timeout/lock se o disparo exigir).
- Overlay: `.covenant-flow/overlay.yaml` `environments.dev.services` e `environments.prod.services`.
- Docs: `docs/monitor-telegram-alerts.md` (agendamento do produto).
- Operação pós-verde: desligar o cron Hermes `Monitor Telegram sinais diario` (não é unit do produto; não entra em overlay como runtime).
- Sem mudança de `backend/` / `frontend/src/` de produto (matriz, webhook, Bot API, opt-in). Sem cadência nova. Sem DM de relógio quebrado.
