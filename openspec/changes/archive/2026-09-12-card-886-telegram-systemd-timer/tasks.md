# Tasks — card-886-telegram-systemd-timer

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.

## 1. Units oneshot+timer

- [x] 1.1 Templates `ops/systemd/criptofarol-{dev,prod}-telegram-alert-scan.service` (Type=oneshot, source do `backend/.env` do `__ROOT_DIR__`, ExecStart do `ops/run_monitor_telegram_alert_scan.py` via venv, timeout folgado, lock por ambiente).
- [x] 1.2 Templates `ops/systemd/criptofarol-{dev,prod}-telegram-alert-scan.timer` com `OnCalendar=*-*-* 11:05:00 UTC`, `Persistent=true`, **sem** `OnBootSec` / `OnUnitInactiveSec` do candle-writer.

## 2. Installer

- [x] 2.1 `install-telegram-alert-scan-systemd.sh --env <dev|prod>` no contrato candle-writer (root canónico DEV/PROD, recusa root errado, `daemon-reload`, `enable --now` do timer).
- [x] 2.2 O installer **arranca o oneshot já** (`systemctl start …telegram-alert-scan.service`) após habilitar o timer.
- [x] 2.3 Lock exclusivo por ambiente para o start imediato não empilhar com um calendar `Persistent`.

## 3. Overlay e docs

- [x] 3.1 Acrescentar os novos `.service` em `.covenant-flow/overlay.yaml` `environments.dev.services` e `environments.prod.services`. Não listar o cron Hermes como runtime.
- [x] 3.2 `docs/monitor-telegram-alerts.md`: o agendamento diário é timer systemd do Cripto Farol (08:05 BRT / 11:05 UTC), não o cron Hermes.

## 4. Scanner (mínimo)

- [x] 4.1 Reusar `ops/run_monitor_telegram_alert_scan.py`. Só alterar env/timeout/lock se o disparo exigir. MUST NOT mudar matriz, webhook `/link`, `sendMessage`, opt-in ou teto anti-ruído.
- [x] 4.2 Falha (timeout, exit ≠ 0, env incompleto) visível só no journal do unit; nenhum `sendMessage` de “o relógio quebrou”.

## 5. Evidência operacional

- [x] 5.1 Instalar e disparar no DEV (`--env dev`): journal DEV com enviou / nada a enviar / falhou; **não** usar bot/token/webhook de PROD.
- [x] 5.2 Instalar e disparar no PROD (`--env prod`): start imediato; journal PROD observável; DMs das transições enviáveis desde 06/09/2026 (teto #747 intacto).
- [x] 5.3 Só depois de 1 run PROD verde (`SENT` ou `ANNOUNCE_SKIP`, exit 0): desligar ou remover o cron Hermes `Monitor Telegram sinais diario`. Até lá não tratar esse job como serviço do produto.

Pointer Code Review: 5.1/5.2 no comentário https://github.com/oalansilva/crypto/issues/886#issuecomment-5619021122 (journal DEV pós-isolamento = `CONFIG_INCOMPLETE` / `DEV_ISOLATION`, sem Bot API; **não** `ANNOUNCE_SKIP`/`SENT` enquanto `BLOCK_PROD_BOT=1`. PROD não re-disparado; 5.2 permanece o `ANNOUNCE_SKIP` exit 0 `2026-09-10T12:35:46+00:00`). 5.3 no comentário https://github.com/oalansilva/crypto/issues/886#issuecomment-5619199316 — job `d02fa5ac-0f49-4226-b34b-3627e66a9ad0` `Monitor Telegram sinais diario` store `/root/.hermes/cron/jobs.json`: pós-estado `enabled=false` / `state=paused` (`paused_at=2026-09-10T10:08:45.589202-03:00`); ticker Hermes não dispara `enabled=false` (não acorda 11/09 08:05 BRT). Não inventar `SENT`.

## 6. Verify

- [x] 6.1 Teste do installer (dry-run / recusa de root, OnCalendar 11:05 UTC nos templates) no estilo dos workers.
- [x] 6.2 `openspec verify` desta change. Sem código de produto em `backend/` / `frontend/src/`.
