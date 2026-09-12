UI impact: none
live_route: N/A sem tela; timer/journal systemd, não rota autenticada.

# Design — card 886: disparar scan Telegram por timer systemd

## Context

Card [#886](https://github.com/oalansilva/crypto/issues/886). Briefing = issue grelhado (Problema, História, Entra/não entra, Vocabulário, critérios, Q1–Q4). Este Design não reabre a grelha.

O envio já está em Pronto (#747): Bot API, matriz position-aware, opt-in, `/link`. O *disparo* ficou no cron Hermes `Monitor Telegram sinais diario`, que desde 07/09/2026 (inclusive 10/09) falha com modelo `gpt-5.5` inexistente — o Python não parte. Linha de base PROD parou em 06/09 (9 pares). Alan é o único elegível em PROD. Script operacional já existe: `ops/run_monitor_telegram_alert_scan.py`.

Sem-tela: nenhuma rota autenticada, nenhum HTML, nenhum clone de catálogo. Evidência = journal do unit + (em PROD) DM já contratada pelo #747.

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Goals / Non-Goals

**Goals:**

- Disparo 1×/dia às 08:05 BRT no host do produto, sem LLM.
- Instalação PROD dispara já e envia DMs do que mudou desde 06/09/2026 (lote possível; teto anti-ruído #747 intacto).
- DEV neste card: o mesmo disparo no host DEV, sem bot/token/webhook de PROD.
- Cortar o Hermes `Monitor Telegram sinais diario` só depois de 1 run PROD verde (enviou ou nada a enviar). Depois, um único disparo por dia.
- Falha do disparo só no journal do unit; sem DM “o relógio quebrou”.
- Overlay e `docs/monitor-telegram-alerts.md` documentam o agendamento do Cripto Farol, não do Hermes.

**Non-Goals:**

- Mudar matriz position-aware, webhook `/link`, `sendMessage`, opt-in ou teto anti-ruído (#747).
- Aumentar cadência (30/60 min); o #200 mandou 1×/dia.
- Consertar o modelo LLM no Hermes.
- Reescrever o scanner além do necessário para o disparo (env, timeout, lock).
- Enviar para grupo/tópico.
- DM operacional de falha do disparo.
- Ligar o job Hermes como runtime do produto (overlay/services).

## Decisions

### 1. Oneshot+timer no padrão candle-writer (Q3 + cadência #200)

Units `criptofarol-{dev,prod}-telegram-alert-scan.service` + `.timer`, templates em `ops/systemd/`, installer `install-telegram-alert-scan-systemd.sh --env <dev|prod>` no mesmo contrato do candle-writer (root canónico, `__ROOT_DIR__`, `source` do `backend/.env` do ambiente, venv Python).

Timer: `Type=oneshot` no service; timer `OnCalendar=*-*-* 11:05:00 UTC` (08:05 BRT, BRT=UTC−3 o ano todo); `Persistent=true`; **sem** `OnBootSec` (não herdar o intervalo 15 min do candle-writer). `ExecStart` chama o script já existente `ops/run_monitor_telegram_alert_scan.py`.

Rejeitado: cron do host / timer de utilizador. Rejeitado: OnUnitInactiveSec do candle-writer. Rejeitado: novo bot PROD no DEV.

### 2. Instalação dispara já (Q1)

O installer, depois de `daemon-reload` e `enable --now` do timer, **arranca o oneshot já** (`systemctl start …telegram-alert-scan.service`). PROD não espera o próximo 08:05. Esse run envia transições enviáveis desde a linha de base de 06/09/2026; o teto anti-ruído #747 não é alargado — o que exceder fica para o próximo scan.

DEV: o mesmo start imediato prova o unit; a linha de base DEV está vazia, portanto o ensaio **não** replica o lote de atraso de PROD.

Rejeitado: só calendar. Rejeitado: `OnBootSec` como substituto do start imediato.

### 3. Lock + timeout para não empilhar; falha só no journal (Q4)

Lock exclusivo por ambiente (flock no estilo candle-writer) para o start imediato e um calendar atrasado (`Persistent`) não empilharem. Timeout folgado no oneshot (valor exacto = P3 Apply). Stdout/stderr do unit vão para o **journal** (`journalctl -u`); o script já imprime `SENT` / `ANNOUNCE_SKIP` / `FAILED` / `CONFIG_INCOMPLETE` sem segredos. Exit ≠ 0 = falhou. **Não** há `sendMessage` extra de relógio quebrado.

Rejeitado: DM operacional de falha. Rejeitado: depender do LLM para diagnosticar silêncio.

### 4. Isolamento DEV/PROD e overlay (Q3)

DEV source = overlay `environments.dev.source`; PROD = `environments.prod.source`. Cada unit só faz `source` do dotenv daquele root. Overlay acrescenta os novos `.service` em `environments.dev.services` e `environments.prod.services` (convenção candle-writer). O job Hermes **não** entra na lista.

Rejeitado: partilhar token/webhook PROD no ensaio DEV (#752: um bot = um webhook).

### 5. Corte Hermes depois de 1 run PROD verde (Q2)

Run verde = journal PROD com enviou (`SENT`) ou nada a enviar (`ANNOUNCE_SKIP`) e exit 0 — não `FAILED` / `CONFIG_INCOMPLETE`. Só então desligar (ou remover) o cron Hermes pelo nome `Monitor Telegram sinais diario`. Até lá o job MAY permanecer; o produto **não** o trata como serviço. Depois do corte, um único disparo por dia (o timer).

Rejeitado: cortar Hermes no mesmo instante do `enable` sem evidência. Rejeitado: deixar os dois acordarem no dia seguinte ao corte.

## Prototype

N/A — sem tela; timer/journal systemd, não rota autenticada. Sem HTML, sem `frontend/public/prototypes/`, sem clonar catálogo. Impeccable / Playwright visual de UI / `DESIGN.md` de produto = N/A justificado.

## Impeccable

N/A — sem superfície visual; não há pipeline context → shape → prototype → critique → browser-gate. Gates de Design e aprovação humana (Aprovação de Design → Pronto para Dev) permanecem.

## Apply contract

- Só após `Status=Pronto para Dev`. Sem código de produto em `backend/` / `frontend/src/` (matriz, webhook, Bot API, opt-in).
- Templates `ops/systemd/criptofarol-{dev,prod}-telegram-alert-scan.{service,timer}`; installer `--env`; `OnCalendar=*-*-* 11:05:00 UTC`; start imediato do oneshot; lock por env; timeout folgado; journal do unit.
- Reusar `ops/run_monitor_telegram_alert_scan.py`; só env/timeout/lock se o disparo exigir.
- Overlay: acrescentar os units DEV e PROD em `environments.*.services`. Docs: `docs/monitor-telegram-alerts.md` — agendamento do produto, não Hermes.
- Operação: após 1 journal PROD verde, desligar Hermes `Monitor Telegram sinais diario`. Não ligar esse job como runtime.
- Evidência: 1 run PROD observável no journal (enviou / nada a enviar / falhou). Ensaio DEV no unit DEV, sem bot PROD.
- MUST NOT: `process_event`; commit/push neste filho; spawn critic/apply; cadência 30/60 min; DM “o relógio quebrou”.

## Risks / Trade-offs

- [Lote PROD 07–10/09 vs teto anti-ruído] → aceite na grelha: o teto #747 manda; overflow no próximo scan; não alargar este card.
- [Persistent + start imediato empilham] → lock exclusivo; segundo run recusa/espera (P3 Apply: flock vs skip).
- [DEV com token incompleto] → `CONFIG_INCOMPLETE` / nada a enviar no journal DEV prova o unit; não usa bot PROD.
- [Dois disparos no mesmo dia se Hermes ainda ligado] → Q2: cortar só após 1 verde; até lá o risco é aceite vs silêncio total.
- [BRT vs UTC] → 08:05 BRT = 11:05 UTC fixo (sem DST); OnCalendar em UTC no unit.

## Migration / Rollout

1. Apply na branch do card (OpenSpec → units + installer + overlay + doc). Integração em `develop`, depois PROD no fechamento/release habitual.
2. Instalar DEV (`--env dev`): start imediato; conferir journal DEV; **não** `setWebhook` / token PROD.
3. Instalar PROD (`--env prod`): start imediato; conferir journal (enviou / nada a enviar / falhou) e auditoria `sent`/`failed` se houver DM.
4. Só com 1 run PROD verde: desligar Hermes `Monitor Telegram sinais diario`.
5. Rollback: `systemctl disable --now` dos timers novos; units ficam no git. Religar Hermes só se o produto timer for desligado — não é o caminho feliz.

## Open Questions

Nenhuma — Q1–Q4 fechadas na grelha. Timeout exacto, nome do ficheiro de lock, e se o installer espelha o drop-in do candle-writer = P3 Apply.

Design Agent verdict: PASS

## Design Critique

Crítico sem-tela (1+1+0; teto 1+1+1). Spawn: autor `aeb89482` + crítico `339194a9`. HTML generated/copied: N/A.

- P0: nenhum
- P1: nenhum
- P2: nenhum
- P3 timeout/lock/flock/drop-in do installer — aceito residual; detalhe de Apply (Open Questions)
- P3 falta `surface:` parseável — aceito residual; sem-tela já declara ausência em `live_route: N/A` + Prototype N/A; não reabrir como P0/P1

Token check: `UI impact: none` e `live_route: N/A` OK; sem rota de catálogo. Prototype N/A. Impeccable N/A.

Verdict: PASS. Sem rework (zero P0 de produto).
