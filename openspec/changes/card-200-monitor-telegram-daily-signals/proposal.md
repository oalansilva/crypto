## Why

Alan ainda nao recebeu sinais do Monitor no topico `Crypto` do `Grupo Crypto`. O fluxo diario existe, mas precisa provar destino, token, auditoria de silencio e falha visivel quando o cron ou envio quebrar.

## What Changes

- Corrigir o scanner diario para carregar token Telegram de forma confiavel no ambiente isolado do cron.
- Garantir uso do destino configurado `chat_id=-1003891182144` e `threadId=5` quando houver evento elegivel.
- Tornar `ANNOUNCE_SKIP` auditavel, separando ausencia real de evento, duplicidade, rate limit, status nao enviavel e configuracao incompleta.
- Garantir que falhas de envio/job retornem erro visivel para o operador sem expor token.
- Manter frequencia diaria, sem mudar cadencia para intradiaria.

## Capabilities

### New Capabilities

### Modified Capabilities
- `monitor-telegram-alerts`: scanner diario deve ser confiavel, auditavel e apontar para o topico interno correto.
- `monitor-telegram-general-alerts`: o scan deve continuar usando catalogo curado e controles de escopo existentes.

## Impact

- Backend/ops: `backend/app/services/monitor_telegram_alerts.py`, `ops/run_monitor_telegram_alert_scan.py`.
- Testes: `backend/tests/unit/test_monitor_telegram_alerts.py` e possivelmente testes unitarios do script operacional.
- Operacao: comandos de validacao do cron/OpenClaw e consultas seguras de auditoria.
