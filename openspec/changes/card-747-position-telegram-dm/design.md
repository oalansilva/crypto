## Context

Card [#747](https://github.com/oalansilva/crypto/issues/747). Change `card-747-position-telegram-dm`.  
Pipeline base: `#174` / `#183` / `#188` (`monitor_telegram_alerts.py`, cron `ops/run_monitor_telegram_alert_scan.py`).  
Hoje o scanner envia transições `HOLD`/`EXIT` de oportunidades `notify_telegram=true` para o `Grupo Crypto`, sem filtrar posição real nem escopo Em portfólio, e o cron ainda pode ler token em `/root/.hermes/secrets/`.

**Revisão de escopo (Alan, pós-T5):** alertas para **qualquer usuário** do site com envio **individual** por carteira; **sem infra Hermes** — o Cripto Farol envia sozinho via Bot API.

## Problema

Usuários não querem refreshar o Monitor para saber quando um sinal mudou de forma relevante **para a posição Spot que cada um carrega**. Alertas genéricos ao grupo interno geram ruído, não refletem carteira individual e dependem de infra externa (Hermes) para config/allowlist.

## Decisão técnica

### 1. Envio autônomo (sem Hermes)

- **Manter e estender** `send_telegram_message` — já chama `https://api.telegram.org/bot{token}/sendMessage` diretamente.
- **Token:** `MONITOR_TELEGRAM_BOT_TOKEN` via env systemd do Cripto ou `backend/.monitor-telegram-secrets.json` — **remover** `/root/.hermes/secrets/runtime-secrets.json` de `SECRETS_CANDIDATES` no cron.
- **Allowlist Hermes:** substituída por **chat_ids persistidos no banco** (usuários que vincularam conta).
- **Vinculação:** webhook HTTP no backend Cripto (`POST /api/telegram/webhook`, secret `TELEGRAM_WEBHOOK_SECRET`) ou long-polling operacional mínimo; bot processa `/link <token>` emitido no Perfil. **Não** usar `hermes-telegram.service` nem gateway Hermes.

### 2. Multi-usuário, entrega individual

- **Elegíveis por execução do cron:** usuários `active`, com `telegram_alerts_enabled=true`, `telegram_chat_id` preenchido e (para position-aware) credencial Binance configurada ou regra manual aplicável.
- **Loop externo por usuário:** para cada elegível, resolver escopo/portfólio **daquele user**, aplicar matriz, enviar **uma DM para o chat_id dele**.
- **Sinal global, filtro individual:** `MonitorObservedStatus` permanece por `(symbol, timeframe)` — transição detectada uma vez; fan-out position-aware por usuário.
- **Dedupe:** chave `(user_id, symbol, timeframe, new_status)` ou `(destination_chat_id, symbol, timeframe, new_status)` na auditoria.
- **Rate limit:** por usuário (contagem/janela separadas ou prefixo na chave de dedupe operacional).

### 3. Posição e escopo (por usuário)

Helper `resolve_portfolio_status_for_user(db, user_id, symbols)` espelhando `MonitorStatusTab.portfolioStatusBySymbol`:

- crypto + Binance do **usuário** → `inPortfolio = hasWalletPosition(baseAsset, min_usd=1)`; preferência manual bloqueada (409).
- regra derivada inativa → `MonitorPreference.in_portfolio` **do usuário**.
- escopo = `inPortfolio=true` ∩ catálogo admin `notify_telegram=true`.

### 4. Matriz de disparo (inalterada na lógica, avaliada por usuário)

| Posição Spot (escopo do user) | Transição | Ação |
| --- | --- | --- |
| Comprado | `HOLD` → `EXIT` | DM Venda |
| Comprado | Stop → `EXIT` | DM Venda + `Motivo=Stop` |
| Flat | `EXIT` → `HOLD` | DM Compra |
| Flat | `HOLD` → `EXIT` | Suprimir |
| Comprado | `EXIT` → `HOLD` | Suprimir |
| Qualquer | mesmo status | Dedupe por user |

Stop: `raw_analysis_status` / `stop_breached_now` top-level no catálogo (D5).

### 5. Destino e Q5

- Position-aware → **somente** `telegram_chat_id` do usuário (DM individual).
- **Desligar** envios position-aware ao `Grupo Crypto`.
- Thread id omitido em DM.

### 6. Binance indisponível (por usuário)

Falha ao sync carteira do user → DM operacional **para aquele chat_id**, rate limited; pausar alertas position-aware **só desse user** na execução.

## Escopo

**Entra:** loop multi-usuário, DM individual position-aware, vinculação Telegram no produto, webhook/link bot Cripto, opt-in no Perfil, matriz, escopo Em portfólio por user, Stop, dedupe/rate limit/auditoria por user, envio Bot API autônomo, desligar Grupo Crypto para estes eventos.

**Não entra:** Hermes gateway/allowlist/secrets; grupo beta externo; ordens automáticas; chat Telegram como canal de comando além de `/link` (+ `/stop` opt-out); websocket/tempo real; proxy `is_holding`; alteração do filtro Em portfólio no Monitor.

## UI impact

**affected** — duas superfícies sincronizadas (mesmo flag backend `telegram_alerts_enabled`):

1. **Perfil** (`ProfilePage`) — seção **“Alertas Telegram”** (configuração completa):
   - Toggle ativar/desativar alertas.
   - Campo informado pelo usuário: **@username Telegram** (obrigatório para vincular) — usado para instruções e validação pós-link contra `from.username` do bot.
   - Status: desvinculado / aguardando confirmação / vinculado (`chat_id` resolvido pelo bot, não editável).
   - Ação: gerar código `/link <token>` + link deep para o bot Cripto Farol.
   - Padrão visual: mesmo card/`page-card` do bloco `BinanceCredentialsForm`.

2. **Preferências do Monitor** (`MonitorStatusTab`, chave global `__global__`) — toggle **“Receber alertas Telegram”** espelhando o mesmo opt-in (usuário liga/desliga sem ir ao Perfil).

**Entrega real:** Bot API usa `chat_id` obtido quando o usuário confirma no bot (`/link`). O @username declarado **não substitui** o `/link`; serve para instruções e validar coerência após vincular.

## Goals / Non-Goals

**Goals**

- Qualquer usuário elegível recebe DMs individuais position-aware.
- Envio 100% no stack Cripto (Bot API + cron + DB).
- Matriz HOLD/EXIT + Stop; Q5 (sem Grupo Crypto).

**Non-Goals**

- Hermes para envio, allowlist ou secrets.
- Broadcast compartilhado (grupo/tópico) para alertas position-aware.
- `is_holding` como proxy de carteira.

## Decisions

| # | Decisão | Alternativa descartada |
| --- | --- | --- |
| D1 | Helper portfolio por `user_id` compartilhado UI/cron | Lógica inline — drift |
| D2 | Colunas em `users`: `telegram_chat_id`, `telegram_username`, `telegram_alerts_enabled`, `telegram_link_token`, `telegram_linked_at` | Allowlist estática env — não escala multi-user |
| D3 | Link via token one-time no Perfil + `/link` no bot; username declarado validado contra `from.username` do Telegram | Só username sem `/link` — rejeitado (Bot API exige `chat_id` + conversa iniciada) |
| D8 | Toggle opt-in **duplicado** Perfil + Monitor global prefs; **uma** API (`PATCH /users/me/telegram-settings`) | Dois flags divergentes — rejeitado (drift) |
| D4 | Bot API direta; secrets só do Cripto | Hermes secrets/gateway — rejeitado (requisito Alan) |
| D5 | Observed status global; fan-out por user | Observed por user — rejeitado (explosão de estado) |
| D6 | Dedupe/rate limit por `(user_id, …)` | Dedupe global — rejeitado (usuário A silenciaria B) |
| D7 | Payload catálogo: `stop_breached_now` + `raw_analysis_status` | Inferir Stop na mensagem — frágil |

## Risks / Trade-offs

- **Usuário sem Binance** → só alertas flat no escopo manual ou skip position-aware. Mitigação: mensagem clara no Perfil; fail-closed por user.
- **Drift UI vs cron** na regra Em portfólio. Mitigação: helper compartilhado + testes.
- **Webhook exposto** → validar `TELEGRAM_WEBHOOK_SECRET`; rate limit no endpoint.
- **Volume cron** cresce com usuários. Mitigação: batch por user; métricas no summary; aceitável no MVP beta.
- **Bot token único** do produto — todos os users usam o mesmo bot Cripto Farol (padrão Telegram).

## Migration Plan

1. Criar bot Cripto Farol (ou reutilizar token Monitor) com webhook apontando para backend Cripto DEV/PROD.
2. Migrar cron para secrets Cripto-only; deploy modelo + API link + Perfil.
3. Usuários vinculam Telegram no Perfil; opt-in explícito.
4. Desativar destino `Grupo Crypto` para position-aware (Q5).
5. Atualizar docs. Rollback: reverter deploy; links Telegram permanecem no DB.

## Open Questions

- Confirmar se o bot Telegram Monitor existente vira bot único do produto ou bot dedicado “Cripto Farol Alertas”.
- Política para usuário **sem** credencial Binance: só escopo manual (`MonitorPreference.in_portfolio`), ou exigir Binance para opt-in? **Proposta design:** permitir opt-in sem Binance; alertas position-aware usam escopo manual; DM operacional se sync falhar quando Binance estiver configurado mas indisponível.

## Apply contract

O Apply **MUST**:

1. Modelo + migration: `telegram_chat_id`, `telegram_username`, `telegram_alerts_enabled` (default **off**), tokens link.
2. API `GET/PATCH /users/me/telegram-settings`: ler/salvar username, opt-in; POST gerar token link.
3. Webhook bot Cripto: validar secret; `/link <token>` persiste `chat_id`; validar `from.username` vs `telegram_username` declarado (warn se divergir, ainda vincula).
4. Toggle Monitor global (`MonitorStatusTab`) chama a **mesma** API de opt-in.
4. Helper portfolio por `user_id`; paridade `MonitorStatusTab`.
5. Refatorar scan: loop usuários elegíveis → matriz position-aware → `sendMessage` para `telegram_chat_id` do user.
6. Dedupe, rate limit e auditoria **por usuário**; incluir `user_id` no payload de auditoria.
7. DM operacional Binance **por usuário** quando sync falhar.
8. Expor Stop no catálogo; suprimir flat/comprado conforme matriz.
9. **Não** enviar position-aware ao `Grupo Crypto`.
10. Remover fallback Hermes em `ops/run_monitor_telegram_alert_scan.py`.
11. UI **Perfil**: seção Alertas Telegram (toggle, @username obrigatório, status link, botão vincular).
12. UI **Monitor Preferências**: toggle global “Receber alertas Telegram” sincronizado.
13. Testes: matriz multi-user, link flow, toggles Perfil↔Monitor, dedupe por user, sem Hermes.
14. Atualizar `docs/monitor-telegram-alerts.md`.

## Prototype

N/A — delta documentado: Perfil (seção config) + Monitor (toggle global). Mesmo shell/tokens existentes; Apply contract §11–12.

## Prototype Validation

N/A — validação via testes backend + revisão visual do delta Perfil em DEV.

## Design Critique

- **P0:** (nenhum)
- **P1:** (nenhum)
- **P1→fechado:** escopo revisado de “só Alan” para multi-user individual — refletido nesta revisão.
- **P1→fechado:** dependência Hermes removida do design — Bot API + secrets Cripto.
- **P2:** webhook/link precisa hardening (secret, expiração token) — documentado; apply must implementar.
- **P2:** cron O(users × strategies) — aceitável MVP beta; monitorar summary.
- **P3:** usuário sem Binance — política em Open Questions; não bloqueia design base.

**Disposition:** Revisão pós-feedback Alan incorporada; achados P2/P3 aceitos.

**Referências:** change `card-747-position-telegram-dm`; specs `monitor-telegram-alerts`, `user-telegram-alerts`; Prototype N/A (delta Perfil minimal).

**Snapshot Impeccable:** N/A — delta UI minimal documentado no Apply contract.

**Design Agent verdict: PASS** (revisão 4 — só @username obrigatório; sem celular)
