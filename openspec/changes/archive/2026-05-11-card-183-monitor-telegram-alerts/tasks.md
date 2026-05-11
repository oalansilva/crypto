## 1. OpenSpec e contrato

- [x] 1.1 Criar proposal, design, specs e tasks para `card-183-monitor-telegram-alerts`.
- [x] 1.2 Validar a change com `openspec validate card-183-monitor-telegram-alerts --type change`.

## 2. Backend - dados e configuracao

- [x] 2.1 Criar modelo `MonitorTelegramAlert` com campos de auditoria, dedupe e resultado.
- [x] 2.2 Adicionar runtime migration idempotente para tabela e indices PostgreSQL.
- [x] 2.3 Adicionar helpers de configuracao/env/preferencias para habilitar, destino, dedupe, rate limit e dry-run.

## 3. Backend - servico e envio

- [x] 3.1 Implementar servico que coleta oportunidades do Monitor e monta candidatos de alerta relevantes.
- [x] 3.2 Implementar deduplicacao por ativo/timeframe/status e rate limit por janela.
- [x] 3.3 Implementar entrega Telegram allowlistada via Bot API, com dry-run seguro quando incompleto.
- [x] 3.4 Persistir auditoria para envios, dry-runs e falhas.

## 4. API operacional

- [x] 4.1 Criar rota admin `POST /api/admin/monitor-telegram-alerts/run`.
- [x] 4.2 Registrar a rota no app FastAPI.

## 5. Testes e validacao

- [x] 5.1 Adicionar testes unitarios para formato, dry-run, dedupe, rate limit e falha de envio.
- [x] 5.2 Adicionar teste da rota admin com servico mockado.
- [x] 5.3 Rodar testes focados, `black --check backend`, `openspec validate --change`, `openspec validate --all` e build/teste proporcional se aplicavel.
