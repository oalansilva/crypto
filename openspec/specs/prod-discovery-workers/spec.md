# prod-discovery-workers Specification

## Purpose
PROD hospeda dispatcher e worker Celery de Discovery nos sources canônicos.
## Requirements
### Requirement: PROD hosts discovery dispatcher and Celery worker
Production SHALL run a discovery outbox dispatcher (`RUN_DISCOVERY_OUTBOX_DISPATCHER=1`) and a Celery worker on queue `discovery` (`criptofarol-prod-discovery-worker`). Both units SHALL be installed, enabled, and active after the authorized PROD rollout of this card. Favorite-refresh already active on the PROD runtime worker SHALL remain enabled.

#### Scenario: PROD units are active
- **WHEN** an operator inspects systemd on the PROD host after install
- **THEN** the discovery dispatcher path and `criptofarol-prod-discovery-worker` are enabled and active
- **AND** favorite backtest refresh on the PROD runtime worker is still enabled

#### Scenario: Sweep is consumed in PROD
- **WHEN** an admin starts a discovery sweep on `https://criptofarol.com.br/discovery`
- **THEN** the sweep leaves `pending`/`queued` and is processed (progress/counters move on the live page)
- **AND** `/api/health` returns 200
- Queue consume without that visible lifecycle MUST NOT close the card.

### Requirement: Installer accepts the canonical DEV and PROD sources
The discovery-worker installer SHALL accept `/srv/apps/dev/criptofarol/source` (DEV units) and `/srv/apps/prod/criptofarol/source` (PROD units) and SHALL refuse any other path. Backend, frontend, and leads PROD services SHALL NOT be redesigned, dropped-in, or restarted by this change; only affected discovery workers restart.

#### Scenario: Install from PROD source
- **WHEN** the installer runs from `/srv/apps/prod/criptofarol/source`
- **THEN** it installs PROD discovery units instead of exiting because the path is not DEV

#### Scenario: Install from DEV source still works
- **WHEN** the installer runs from `/srv/apps/dev/criptofarol/source`
- **THEN** it continues to install the existing DEV discovery units

#### Scenario: Non-canonical path is refused
- **WHEN** the installer runs from any other directory
- **THEN** it exits non-zero and installs nothing

#### Scenario: PROD API/UI units stay untouched
- **WHEN** discovery workers are installed in PROD
- **THEN** `criptofarol-prod-backend` and `criptofarol-prod-frontend` are not rewritten or restarted by the installer

### Requirement: PROD overlay lists the discovery worker for release closeout
Production overlay `environments.prod.services` SHALL include `criptofarol-prod-discovery-worker.service` so the authorized production publish window restarts the long-running Celery discovery worker together with the other in-memory product processes. The installer path and unit templates remain the existing PROD discovery worker; this requirement MUST NOT create a new production restart command outside release closeout and MUST NOT change DEV `./restart`.

#### Scenario: Overlay inventory includes the PROD discovery worker
- **WHEN** an operator reads `.covenant-flow/overlay.yaml` `environments.prod`
- **THEN** `services` contains `criptofarol-prod-discovery-worker.service`

#### Scenario: Publish window restarts the discovery worker with the other long-running units
- **WHEN** production release closeout restarts the overlay publish window
- **THEN** `criptofarol-prod-discovery-worker` is restarted in the same window as backend, frontend, leads, and runtime-worker
- **AND** the installer MUST NOT be the only way that worker returns to the published code

#### Scenario: DEV restart path stays unchanged
- **WHEN** this change is applied
- **THEN** canonical DEV `./restart` continues to restart DEV discovery workers as today
- **AND** no new production restart entrypoint is added outside release closeout

### Requirement: Teto da Descoberta de PROD aplicado só sem busca ativa
A aplicação dos limites na unit `criptofarol-prod-discovery-worker.service` SHALL usar o instalador a partir de `/srv/apps/prod/criptofarol/source` restrito à unit da Descoberta. Antes de parar qualquer coisa, o instalador SHALL consultar o ledger do #1093 e considerar busca ativa quando houver sweep `running` ou `cancelling`, lease com validade futura pelo relógio do PostgreSQL ou tentativa `running` sem fim; erro de consulta SHALL contar como ativa. Sweeps `pending` (na fila, sem execução) e `paused` SHALL ser listados e MUST NOT bloquear. Com busca ativa, o instalador SHALL reconsultar a cada 60 segundos até o prazo de espera (padrão 30 minutos, ajustável) e, esgotado, adiar: sair com código diferente de zero, informar "adiado: busca ativa" com os sweeps encontrados e não parar, gravar nem reiniciar nada; o operador repete depois. Sem busca ativa, SHALL parar só a Descoberta PROD, recusar se a unit seguir ativa ou o cgroup tiver processo, gravar só essa unit, recarregar e ligá-la uma vez. Runtime-worker, backend, frontend e leads de PROD MUST NOT ser reescritos nem reiniciados por esse passo.

#### Scenario: Busca de cliente em andamento
- **WHEN** há busca ativa em PROD e o operador aplica o teto
- **THEN** o instalador espera; se o prazo acabar, informa "adiado: busca ativa" e a Descoberta PROD segue rodando com a unit anterior até o operador repetir

#### Scenario: Busca só na fila
- **WHEN** há sweep `pending` em PROD, sem lease válida nem tentativa em execução, e o operador aplica o teto
- **THEN** o sweep aparece na listagem, não bloqueia a aplicação e é consumido quando a Descoberta PROD volta

#### Scenario: Sem busca ativa
- **WHEN** não há busca ativa em PROD e o operador aplica o teto
- **THEN** só a Descoberta PROD é parada, regravada e ligada uma vez, e as demais units PROD mantêm o mesmo arranque

#### Scenario: Sobra de processo após a parada
- **WHEN** depois da parada ainda há processo no cgroup da Descoberta PROD
- **THEN** o instalador recusa sem matar nada, lista os PIDs e informa que os limites não foram aplicados

### Requirement: Limites efetivos da Descoberta de PROD verificáveis
Depois da aplicação, `systemctl show criptofarol-prod-discovery-worker.service` SHALL informar MemoryHigh=4294967296, MemoryMax=5368709120, MemorySwapMax=536870912, OOMPolicy=kill, KillMode=control-group, Restart=on-failure, RestartUSec=1min, StartLimitBurst=3, StartLimitIntervalUSec=15min, TimeoutStopUSec=30s e ActiveState=active, e uma sonda de admissão com o perfil `prod` contra o cgroup da unit SHALL passar. O card que aplica o teto MUST NOT ir a Pronto sem essa verificação registrada.

#### Scenario: Verificação após aplicar
- **WHEN** o instalador termina a aplicação do teto em PROD
- **THEN** o `systemctl show` mostra os valores acima e a sonda de admissão do perfil `prod` passa

#### Scenario: Restart da janela do publish com o teto aplicado
- **WHEN** um deploy normal de PROD reinicia a janela do publish depois do teto aplicado
- **THEN** a Descoberta PROD gasta uma das três partidas permitidas em 15 minutos e volta com os mesmos limites

