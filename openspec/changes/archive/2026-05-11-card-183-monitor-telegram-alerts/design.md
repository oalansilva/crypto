## Context

O card #174 fechou a decisao operacional: Clara nao envia alertas diretamente ao grupo externo do beta. O produto precisa gerar rascunhos/alertas internos a partir do Monitor para um destino Telegram allowlistado, com Alan como filtro humano antes de qualquer encaminhamento externo.

O backend ja possui o `OpportunityService`, que calcula as oportunidades/status exibidos no Monitor. Tambem ja possui `SystemPreference`, runtime migrations leves em `ensure_runtime_schema_migrations`, rotas admin e padrao de testes unitarios com PostgreSQL local.

## Goals / Non-Goals

**Goals:**

- Criar servico backend de alertas internos do Monitor baseado no payload de oportunidades.
- Persistir auditoria e ultimo envio por ativo/timeframe/status para deduplicacao.
- Aplicar allowlist de destino, janela minima e limite por hora.
- Enviar para Telegram via Bot API quando habilitado e configurado.
- Permitir dry-run operacional quando token/destino nao estiverem configurados.
- Expor rota admin para varredura manual, suficiente para validar o fluxo e plugar em cron depois.

**Non-Goals:**

- Enviar automaticamente ao grupo externo do beta.
- Responder mensagens de beta testers.
- Criar aconselhamento financeiro ou recomendacao personalizada.
- Implementar UI administrativa completa neste card.
- Substituir o Monitor ou alterar a regra de calculo de status.

## Decisions

### D1: Derivar eventos do `OpportunityService`

Usar o `OpportunityService` como fonte canonica evita divergencia entre o que aparece no Monitor e o que vira alerta. A varredura usa favoritos/estrategias ja monitorados e gera evento por oportunidade relevante.

Alternativa considerada: ler direto tabelas de sinais. Rejeitada porque aumentaria risco de status diferente do Monitor.

### D2: Persistir auditoria em tabela propria

Criar `monitor_telegram_alerts` para registrar tentativas/envios, com payload, destino, resultado, hash e timestamps. Isso cobre auditoria e deduplicacao sem misturar com logs textuais.

Alternativa considerada: usar somente arquivo/log. Rejeitada porque nao permite dedupe confiavel nem consulta operacional.

### D3: Preferencias por env primeiro, `SystemPreference` como override

O servico le configuracao de envs para runtime simples e consulta `SystemPreference` quando houver sessao DB. Isso permite desligar/ajustar sem expor segredo em docs ou board.

Segredos como token Telegram ficam apenas em env (`MONITOR_TELEGRAM_BOT_TOKEN`) e nunca em `SystemPreference`.

### D4: Dry-run como comportamento seguro

Se alertas estiverem habilitados mas sem token/destino valido, a varredura registra o que teria sido enviado como `dry_run`, sem tentar entrega externa. Isso permite validar dedupe, rate limit e formato sem risco de postar em grupo errado.

### D5: Rota admin operacional

Adicionar `POST /api/admin/monitor-telegram-alerts/run` para execução manual por admin. A automacao recorrente pode chamar a rota ou serviço depois, sem ampliar o escopo agora.

## Risks / Trade-offs

- [Risk] `OpportunityService` pode ser pesado para rodar com alta frequencia -> Mitigation: rota manual e limites configuraveis; cron deve usar intervalo minimo de 15 minutos.
- [Risk] destino Telegram errado pode vazar alerta -> Mitigation: allowlist obrigatoria, destino unico validado e dry-run quando configuracao esta incompleta.
- [Risk] repeticao excessiva por flapping de status -> Mitigation: dedupe por ativo/timeframe/status e janela minima de 6 horas por padrao.
- [Risk] alerta soar como call -> Mitigation: template fixo com disclaimer educacional e texto pronto para Alan revisar.

## Migration Plan

1. Criar modelo/tabela via runtime migration idempotente.
2. Subir servico e rota admin sem habilitar envio externo por padrao.
3. Configurar envs/preferencias em runtime quando Alan aprovar o destino interno.
4. Validar com dry-run antes de habilitar envio real.

Rollback: desligar `MONITOR_TELEGRAM_ALERTS_ENABLED` ou preferencia equivalente; a tabela de auditoria pode permanecer sem impacto no runtime.
