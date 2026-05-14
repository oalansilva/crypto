## Context

O scanner diario `ops/run_monitor_telegram_alert_scan.py` chama `run_monitor_telegram_alert_scan` e imprime apenas `SENT`, `FAILED` ou `ANNOUNCE_SKIP`. O servico ja tem allowlist, deduplicacao, rate limit e auditoria para envios/dry-runs, mas o skip sem candidato nem sempre deixa motivo suficiente para diagnostico operacional. O script tambem depende de token carregado em processo isolado.

## Goals / Non-Goals

**Goals:**
- Provar configuracao efetiva sem expor token.
- Tornar o motivo de silencio auditavel no resumo do scanner.
- Garantir que destino e thread configurados via env/preferencia aparecam no resumo seguro.
- Manter falha de envio como retorno nao-zero no script operacional.

**Non-Goals:**
- Nao alterar frequencia do cron diario.
- Nao enviar alerta para grupo externo do beta.
- Nao enviar mensagem real em teste automatizado.

## Decisions

- Adicionar resumo seguro de configuracao ao retorno do scanner.
  - Racional: permite auditar `enabled`, token presente, destino permitido, chat e thread sem vazar segredo.
- Registrar skip reason para status nao enviavel e ausencia de oportunidades.
  - Racional: `ANNOUNCE_SKIP` continua limpo para cron saudavel, mas o JSON/rota/admin consegue explicar silencio.
- Reaproveitar `MONITOR_TELEGRAM_BOT_TOKEN` como env canonico e aceitar `TELEGRAM_BOT_TOKEN` apenas no script operacional.
  - Racional: evita mudar contrato do servico e preserva compatibilidade com runtime secrets.

## Risks / Trade-offs

- [Risk] Expor dados operacionais demais no resumo.
  - Mitigation: nunca retornar token, apenas booleano `token_configured`.
- [Risk] Mudanca de summary quebrar consumidor existente.
  - Mitigation: manter chaves existentes e apenas adicionar campos/resultados.
