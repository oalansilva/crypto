## Why

Usuários do Cripto Farol não querem depender de abrir o site para saber quando uma estratégia monitorada mudou de leitura relevante para **a posição Spot que cada um carrega na carteira** — saída, Stop quando comprado, ou entrada potencial quando flat. O pipeline `#174/#183/#188` envia alertas genéricos ao `Grupo Crypto`; este card substitui esse destino por **DMs individuais position-aware**, uma por usuário elegível, filtradas pelo escopo **Em portfólio** e pelo estado real da carteira Binance **daquele usuário**.

## What Changes

- Alertas Telegram **para qualquer usuário ativo do site** que tenha vinculado Telegram e optado por receber alertas — **envio individual** (cada usuário recebe só o que importa para a **própria** carteira).
- **Sem dependência do Hermes** para envio: o Cripto Farol usa **Bot API Telegram direta** (`sendMessage`) com token e webhook/cron **próprios do produto**; remover fallback de secrets em `/root/.hermes/`.
- **Desligar** envios position-aware ao `Grupo Crypto` / tópico `Crypto` (Q5).
- Fonte de “estou comprado”: **carteira Spot Binance / `in_portfolio` derivado por usuário** (não `is_holding` simulado da estratégia).
- **Escopo de símbolos (por usuário):** só estratégias cujo símbolo está no filtro **Em portfólio** do Monitor **daquele usuário** — `portfolioStatusBySymbol.inPortfolio === true`.
- **Granularidade:** todas as estratégias com `notify_telegram=true` do símbolo no escopo disparam saída/Stop quando há posição Spot do ativo-base **do usuário**.
- **Matriz de disparo position-aware** (igual por usuário, avaliada com dados da carteira dele):
  - Comprado + `HOLD` → `EXIT` → DM Venda.
  - Comprado + saída por Stop → DM Venda com **`Motivo=Stop`**.
  - Flat (no escopo) + `EXIT` → `HOLD` → DM Compra (entrada potencial).
  - Flat + `HOLD` → `EXIT` → **suprimir**.
  - Comprado + `EXIT` → `HOLD` → **suprimir**.
  - Mesmo estado repetido → dedupe **por usuário** (janela mínima herdada).
- **Binance indisponível no cron (por usuário):** DM operacional individual (“carteira indisponível, alertas pausados”), rate limited; alertas position-aware daquele usuário pausam até a sync voltar.
- **Vinculação Telegram:** Perfil — usuário informa **@username** (obrigatório), gera token e confirma no bot (`/link`); Preferências do Monitor — toggle rápido ativar/desativar (mesmo flag). **Não** Hermes.
- Reuso da infra `#174/#183/#188` (scan, dedupe, rate limit, auditoria) com destino, filtros, matriz e loop multi-usuário novos.
- Linguagem educacional (não ordem de compra/venda / não recomendação financeira).

## Capabilities

### New Capabilities

- `user-telegram-alerts`: vinculação de conta Telegram por usuário, opt-in, webhook/link do bot Cripto, armazenamento de `chat_id` por usuário.

### Modified Capabilities

- `monitor-telegram-alerts`: destino passa a ser **DM individual por usuário**; alertas position-aware filtrados por escopo Em portfólio e posição Spot **de cada usuário**; matriz HOLD/EXIT; Stop com `Motivo=Stop`; supressão flat/comprado; pausa + DM operacional quando Binance indisponível **por usuário**; desligamento de envios position-aware ao `Grupo Crypto`; envio **autônomo** via Bot API (sem Hermes).

## Impact

- Backend: `monitor_telegram_alerts.py` — loop multi-usuário, matriz position-aware, envio direto Bot API, dedupe/rate limit por usuário.
- Backend: helper de portfolio status por `user_id` (paridade `MonitorStatusTab.portfolioStatusBySymbol`).
- Backend: modelo/API de vinculação Telegram (`UserTelegramLink` ou colunas em `users`); webhook ou polling mínimo do bot Cripto para `/link`.
- Backend: `opportunity_service.py` — expor `stop_breached_now` / `raw_analysis_status` top-level.
- Frontend: **Perfil** — seção Alertas Telegram (@username, toggle, vincular bot).
- Frontend: **Monitor Preferências** — toggle global “Receber alertas Telegram” (sincronizado com Perfil).
- Ops: `run_monitor_telegram_alert_scan.py` — token só de env/secrets **do Cripto**; remover dependência de `/root/.hermes/secrets/`.
- Config: `MONITOR_TELEGRAM_BOT_TOKEN` no ambiente Cripto (systemd/env/secrets file do repo); webhook URL apontando para backend Cripto.
- Spec deltas: `monitor-telegram-alerts`, `user-telegram-alerts` (nova).
- Docs: `docs/monitor-telegram-alerts.md`.
- **UI impact: affected** — Perfil (config completa) + Monitor (toggle opt-in).
