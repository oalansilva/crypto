## Why

O card #174 definiu que alertas do Monitor devem ir primeiro para o grupo interno `Grupo Crypto`, para Alan revisar antes de qualquer comunicacao externa com beta testers. Hoje o produto depende de leitura manual do Monitor e nao tem servico tecnico com allowlist, anti-ruido, auditoria e desligamento.

## What Changes

- Adicionar servico backend de alertas internos do Monitor por Telegram.
- Derivar eventos a partir das oportunidades do Monitor, mantendo o mesmo contrato de status visivel no produto.
- Enviar mensagens padronizadas apenas para destino Telegram interno allowlistado.
- Deduplicar por ativo, timeframe e status, com janela minima antes de repetir alerta igual.
- Aplicar limite de mensagens por janela e registrar auditoria de cada tentativa/envio.
- Adicionar configuracao para desligar alertas e permitir dry-run quando token/destino nao estiverem configurados.
- Expor ponto operacional admin para executar uma varredura manual e validar o fluxo sem depender de cron externo.

## Capabilities

### New Capabilities

- `monitor-telegram-alerts`: alertas internos do Monitor com allowlist, deduplicacao, rate limit, auditoria, mensagem padronizada e controle de desligamento.

### Modified Capabilities

Nenhuma. As preferencias administrativas usadas pela implementacao fazem parte do novo capability `monitor-telegram-alerts`.

## Impact

- Backend: novos modelos/tabelas de auditoria, servico de alertas, rota admin operacional e migracao runtime.
- Configuracao: novas preferencias/envs para habilitar alertas, token Telegram, destino allowlistado e limites.
- Testes: cobertura unitario/rota para dedupe, rate limit, dry-run, allowlist e auditoria.
- Documentacao: `docs/monitor-telegram-alerts.md` continua sendo o contrato produto/operacao do #174.
