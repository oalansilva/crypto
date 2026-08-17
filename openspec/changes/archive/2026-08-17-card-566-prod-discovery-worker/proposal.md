## Why

A tela `/discovery` já está em PROD, mas o worker que despacha e consome a varredura não. Em DEV existem `criptofarol-dev-runtime-worker` (`RUN_DISCOVERY_OUTBOX_DISPATCHER=1`) e `criptofarol-dev-discovery-worker` (Celery fila `discovery`). Em PROD o runtime-worker não exporta o dispatcher e não há unit Celery de discovery. Disparar varredura em `https://criptofarol.com.br/discovery` pode gravar sweep e ficar sem processamento.

## What Changes

- Templates systemd PROD espelhando o DEV (dispatcher + Celery discovery).
- Installer que aceita `/srv/apps/prod/criptofarol/source` (hoje `install-discovery-workers-systemd.sh` recusa qualquer root que não seja o DEV).
- Ligar `RUN_DISCOVERY_OUTBOX_DISPATCHER=1` no runtime-worker PROD sem desligar o refresh de favoritos já ativo.
- Unit `criptofarol-prod-discovery-worker` na fila `discovery`, enabled e active.
- Documentar a topologia PROD em `docs/runtime-architecture.md`.
- Validação em PROD (após Pronto para Dev e autorização do card): services active, consume da fila ou sweep de smoke, `/api/health` 200.
- Fora de escopo: WIP de idempotência (#567), redesign da tela, worker de candle-writer, restart de backend/frontend/leads.

## Capabilities

### New Capabilities

- `prod-discovery-workers`: units PROD de dispatcher e Celery discovery, installer e evidência operacional.

### Modified Capabilities

- `crypto-runtime-architecture`: Discovery dispatcher/Celery passam a ter caminho PROD documentado e instalável, não só DEV.

## Impact

- `ops/systemd/` (novos templates PROD), `install-discovery-workers-systemd.sh` (ou installer PROD irmão).
- Drop-in/env do `criptofarol-prod-runtime-worker.service`.
- `docs/runtime-architecture.md`.
- Operação PROD: somente workers de discovery; backend/frontend/leads não são redesenhados.
- UI impact: none.
