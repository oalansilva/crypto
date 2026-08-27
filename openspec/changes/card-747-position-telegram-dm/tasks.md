## 1. User Telegram linking e parâmetros (sem Hermes)

- [x] 1.1 Migration/modelo: `telegram_chat_id`, `telegram_username`, `telegram_alerts_enabled` (default false), `telegram_link_token`, `telegram_link_expires_at`, `telegram_linked_at`
- [x] 1.2 API `GET/PATCH /users/me/telegram-settings`: username (obrigatório), opt-in; POST gerar token link
- [x] 1.3 Webhook Cripto com `TELEGRAM_WEBHOOK_SECRET`; handler `/link <token>`; validar username declarado vs `from.username`
- [x] 1.4 Remover fallback Hermes em `ops/run_monitor_telegram_alert_scan.py`
- [x] 1.5 Testes: link válido, username mismatch warn, token expirado

## 2. UI Perfil — Alertas Telegram (config completa)

- [x] 2.1 Seção no `ProfilePage`: toggle opt-in, input @username (obrigatório), status vinculado, botão gerar `/link`
- [x] 2.2 Validação frontend: username obrigatório para vincular
- [ ] 2.3 Teste E2E: salvar params, estados desvinculado/vinculado

## 3. UI Monitor Preferências — toggle opt-in

- [x] 3.1 Toggle global “Receber alertas Telegram” em `MonitorStatusTab` (prefs `__global__` ou API dedicada sincronizada)
- [x] 3.2 Mesmo flag `telegram_alerts_enabled`; alterar no Monitor reflete no Perfil e vice-versa
- [ ] 3.3 Teste: toggle Monitor desliga alertas; Perfil mostra off

## 4. Portfolio scope resolution (server-side, por user)

- [x] 4.1 Helper `resolve_portfolio_status_for_user(db, user_id, symbols)`
- [x] 4.2 Listar elegíveis: active + `telegram_alerts_enabled` + `telegram_chat_id` presente
- [x] 4.3 Testes: múltiplos users, posições diferentes; user sem Binance usa escopo manual

## 5. Catálogo — expor motivo Stop

- [x] 5.1 Campos `raw_analysis_status` e `stop_breached_now` top-level
- [x] 5.2 Teste STOPPED_OUT

## 6. Scanner position-aware multi-usuário

- [x] 6.1 Matriz position-aware conforme design
- [x] 6.2 Loop por user elegível → envio para `telegram_chat_id` do user
- [x] 6.3 Dedupe/rate limit/auditoria por user
- [x] 6.4 Sem envio ao `Grupo Crypto`; DM operacional Binance por user

## 7. Envio autônomo Bot API

- [x] 7.1 `sendMessage` direto; `chat_id` por user
- [x] 7.2 Teste dois users na mesma execução

## 8. Testes e documentação

- [ ] 8.1 Matriz multi-user; toggles Perfil↔Monitor
- [x] 8.2 Atualizar `docs/monitor-telegram-alerts.md`
- [x] 8.3 `openspec validate` + suite backend
