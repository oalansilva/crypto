# Discovery DEV: contenção, cutover e recuperação

Este procedimento corresponde à change `card-1093-discovery-memory`, com os valores revistos pelo card #1110. O perfil DEV admite uma combinação e um worker interno, com MemoryHigh=3 GiB, MemoryMax=4 GiB e MemorySwapMax=512 MiB (eram 5/6 GiB no #1093). O perfil PROD (seção "Discovery PROD" abaixo) usa 4/5 GiB/512 MiB. Os limites cobrem toda a árvore, page cache e IPC. Os limites esperados vêm de uma tabela de perfis por ambiente no código, escolhida por `DISCOVERY_RESOURCE_PROFILE` (`dev` ou `prod`); perfil desconhecido bloqueia o trabalho. A admissão exige cgroup v2 verificado com limites **iguais** aos do perfil, `memory.oom.group=1`, MemTotal ≥ soma dos tetos dos dois perfis (4 + 5 = 9 GiB) + 14 GiB (13 GiB para os demais serviços e 1 GiB de margem; eram 17 GiB fora de um único envelope), MemAvailable ≥8 GiB, swap livre ≥1 GiB e disco livre ≥4 GiB. O worker interno é `min(pedido, floor((MemoryMax − 1 GiB) / 3 GiB))`, com mínimo 1: DEV e PROD usam 1 worker. Falha de admissão conserva a fila e informa `resource_budget_unavailable`.

## Estado ao final do Apply (13/10/2026)

A carga integral original (492.480 candidatos × 3 buscas) foi concluída em 13/10/2026 às 23:39 UTC, `Result=success`, sem OOM: pico de ≈1,70 GiB (abaixo de MemoryHigh=5 GiB), swap 0, `NRestarts=0`. Detalhes e hashes em `apply-evidence.md`. O estado abaixo descreve o ambiente DEV real, que não foi alterado pelo Apply.

O worker DEV legado ilimitado está parado, MainPID=0 e cgroup vazio. Nenhuma migração foi aplicada ao banco DEV compartilhado e a nova unit ainda não foi instalada. Outros serviços e PROD continuam fora desta operação. O runtime-worker existente não deve executar código legado contra o schema novo: o cutover exige o código com fencing disponível aos consumidores antes da migração.

Uma máscara runtime foi criada para a unit Discovery, porém o arquivo local em `/etc/systemd/system` prevaleceu e `LoadState` permaneceu `loaded`. A contenção efetiva é o drop-in exclusivo `/run/systemd/system/criptofarol-dev-discovery-worker.service.d/card-1093-hold.conf`, copiado de `ops/systemd/discovery-runtime-hold.conf`. Ele exige o marcador ausente `/run/criptofarol-card-1093-discovery-release`. `ConditionResult=no` impede partidas provocadas por dependências do backend. Não criar esse marcador para liberar o worker legado.

## Cutover coordenado

1. Registrar SHA, revisão Alembic, estados de sweeps/tentativas/circuito, unit e drop-ins atuais. Fazer backup usual do banco. Identificar quem conduz qualquer job systemd pendente; aguardar a parada em curso antes de disputar a unit.
2. Bloquear admissão Discovery e parar somente `criptofarol-dev-discovery-worker.service`. Verificar `MainPID=0`, `ActiveState=inactive|failed`, `Job=` vazio e ausência de PIDs em `ControlGroup/cgroup.procs`. Não aplicar o teto à árvore ilimitada em execução. Se a parada não drenar, diagnosticar os PIDs/cgroup/journal antes da limpeza autorizada da própria árvore.
3. Disponibilizar a versão com fencing aos consumidores do schema, incluindo API/dispatcher. Não reiniciar backend/runtime implicitamente por meio do instalador. Coordenação desses consumidores é uma etapa explícita do responsável pelo cutover.
4. Aplicar `20261013_0001` com o ambiente DEV correto e Discovery ainda bloqueada. A migração é aditiva, expira leases legadas, conserva o número de tentativas e não inventa histórico de claims antigos. Pendências esgotadas são fechadas conservadoramente. `downgrade` recusa remover o ledger.
5. Inspecionar previamente `./install-discovery-workers-systemd.sh --dry-run --discovery-only --root /srv/apps/dev/criptofarol/source`. Deve listar somente a unit Discovery DEV e `backend_dropin=none`. Após o código chegar ao caminho canônico, instalar apenas essa unit limitada. O instalador recusa árvore ativa/coexistente; o hold mantém a partida bloqueada nesta etapa.
6. Verificar com `systemctl cat/show` MemoryAccounting, MemoryHigh=3221225472, MemoryMax=4294967296 (valores do #1110; no #1093 eram 5368709120 e 6442450944), MemorySwapMax=536870912, OOMPolicy=kill, KillMode=control-group, Restart=on-failure, RestartSec=60, StartLimitBurst=3/900 s e TimeoutStopSec=30. Limite de parada systemd é contenção final; cleanup interno deve terminar em ≤20 s. Confirmar spool persistente privado, nunca tmpfs, em `/var/tmp/criptofarol-dev-discovery`.
7. Somente com código/schema compatíveis e limites verificados, remover o drop-in `card-1093-hold.conf` desta operação, executar `systemctl unmask --runtime criptofarol-dev-discovery-worker.service`, `daemon-reload` e iniciar somente Discovery. Verificar os arquivos reais do cgroup antes de aceitar trabalho. Se circuito estiver aberto, diagnosticar e reconhecer administrativamente conforme abaixo.

## Discovery no restart normal do DEV (#1106)

O `./restart` do DEV (T14 e restart manual) para a Discovery antes de instalar os units: `systemctl stop criptofarol-dev-discovery-worker.service` (síncrono: SIGTERM, SIGKILL após `TimeoutStopSec=30s`), depois `install-discovery-workers-systemd.sh`, que continua sendo a trava e liga a Discovery uma única vez com `enable --now`. A Discovery não faz parte do `systemctl restart` final de backend/frontend. Isso acontece em todo restart, mesmo com a unit igual ao template e mesmo com busca em andamento; o restart soma até ~60 s de parada e não espera a busca terminar. O restart só sai com sucesso com backend, frontend, worker de runtime e Discovery ativos.

- **Falha do `stop`:** o restart sai com erro dizendo que a Discovery não parou e que os limites não foram aplicados; nada é instalado.
- **Sobra de processo no cgroup:** o instalador recusa, sem matar nada, e lista o cgroup, cada PID com o comando e "limites não aplicados". Drenar a sobra conforme o Cutover coordenado e repetir o `./restart`. A Discovery fica parada até lá.
- **Drop-in de contenção do #1093 ainda presente** (`card-1093-hold.conf`): impede a partida; o instalador diz isso quando a Discovery não fica ativa. Remover o hold só conforme o passo 7 do cutover.
- **Falha após o `stop`:** o restart aborta antes de reiniciar backend, frontend e worker de runtime e avisa que a Discovery pode ter ficado parada.

### Busca em andamento e restarts seguidos

A parada interrompe a tentativa em curso. A lease expira (TTL 300 s), o reconciler marca `lease_interrupted` e a busca é reagendada com backoff 60/300 s, retomando com uma tentativa a menos. Cada interrupção é uma falha operacional do #1093: **3 interrupções em 15 min abrem o circuito do ambiente** (Discovery bloqueada até `acknowledge_circuit.py`) e a 3ª na mesma combinação fecha a busca com `resource_recovery_exhausted`. Decisão do Alan (2026-10-16): aceito, sem mudança no circuito. Evite restarts seguidos com busca ativa.

### Teto de partidas (StartLimitBurst)

A unit tem `StartLimitBurst=3` em `StartLimitIntervalSec=900`. Cada restart faz uma partida da Discovery, então o **4º restart em 15 min é recusado** pelo systemd (`start-limit-hit`) e o restart falha com aviso claro (o instalador cita o teto). Não há `reset-failed` automático, para não furar o limite do #1093: aguarde a janela passar e repita o `./restart`.

## Discovery PROD (card #1110)

A unit `criptofarol-prod-discovery-worker.service` passa a ter o mesmo desenho da DEV, com teto maior. Em 2026-10-16 ela rodava sem limite (`MemoryHigh/Max/SwapMax=infinity`, `OOMPolicy=stop`, `Restart=always`, `RestartSec=5s`) e sem perfil, com 3 processos de cálculo por busca. DEV e PROD dividem a mesma VM, então a Descoberta de um ambiente não pode derrubar o outro.

- **Limites:** MemoryHigh=4 GiB (aviso), MemoryMax=5 GiB (corte), MemorySwapMax=512 MiB, `OOMPolicy=kill`, `KillMode=control-group`, `TimeoutStopSec=30s`, `SendSIGKILL=yes`. Perfil `prod` (`DISCOVERY_RESOURCE_PROFILE=prod`) com **1 worker interno** (`DISCOVERY_INTERNAL_WORKERS=1`, decisão de Alan, 2026-10-16), spool em `/var/tmp/criptofarol-prod-discovery`. Medição do #1093 (1 worker, DEV): pico de 1,70 GiB na árvore inteira, sem OOM.
- **Efeito para o cliente:** buscas grandes ficam até cerca de 3× mais lentas que com 3 workers (referência: ~6,6 h com 1 worker contra ~2 a 3 h estimadas com 3). Pela primeira vez a busca de um cliente pode esperar por memória: com MemAvailable < 8 GiB no host compartilhado a busca não começa, aparece em "Varredura em execução" sem progresso, `resource_budget_unavailable` fica só no journal e o outbox reentrega o pedido a cada cerca de 10 min até a admissão passar. Não gasta tentativa nem circuito.
- **Política de reinício:** igual à DEV. `Restart=on-failure`, `RestartSec=60`, no máximo 3 partidas em 900 s; a quarta é recusada e a unit fica parada até Alan agir, sem `reset-failed` automático. Falha repetida em PROD abre o circuito `prod` como no DEV (3 falhas em 15 min). Um restart da janela de deploy gasta uma das 3 partidas.
- **Chave de ambiente:** o ambiente do circuito e do spool vem primeiro do nome do cgroup `criptofarol-{dev,prod}-*`, depois de `DISCOVERY_RESOURCE_PROFILE` e `APP_ENV`. Assim o runtime-worker, o backend e a Descoberta de PROD resolvem `prod` mesmo que `APP_ENV` no `.env` tenha outro valor.

### Sonda de busca ativa

`backend/scripts/discovery/active_search_probe.py` (somente leitura, banco do ambiente, relógio do PostgreSQL). **Busca ativa** é qualquer sweep `running` ou `cancelling`, lease com validade futura ou tentativa `running` sem fim. Sweeps `pending` (na fila) e `paused` são listados e **não** bloqueiam. Imprime JSON com os sweeps; sai 0 quando ocioso e 3 quando ativo; erro de consulta conta como ativo. Para rodar: `PYTHONPATH=<source>:<source>/backend` com o `.venv` e o `.env` do ambiente (em PROD, como root).

### Aplicar o teto em PROD

`./install-discovery-workers-systemd.sh --root /srv/apps/prod/criptofarol/source --discovery-only [--wait-idle <min>]`, como root. Em ordem:

1. Consulta a sonda; com busca ativa, reconsulta a cada 60 s por até 30 min (`--wait-idle` muda o prazo; `0` não espera).
2. Esgotado o prazo: sai com código 75, diz "adiado: busca ativa" e lista os sweeps; **não para, não grava nem reinicia nada**. A Descoberta PROD segue com a unit anterior; repita depois. Com buscas de ~6,6 h, a janela ociosa pode demorar e pode exigir outro horário.
3. Sem busca ativa: para só a Descoberta PROD, recusa se a unit seguir ativa ou o cgroup tiver processo (lista os PIDs, "limites não aplicados", nada é morto), reconsulta a sonda (lease nova entra como aviso), grava só essa unit, `daemon-reload`, `enable --now` (uma partida) e imprime o `systemctl show` de verificação.

Runtime-worker, backend, frontend e leads de PROD não são reescritos nem reiniciados por esse passo. Uma instalação PROD completa (sem `--discovery-only`) recusa reescrever a unit com a Descoberta ativa.

### Verificar

`systemctl show criptofarol-prod-discovery-worker.service -p MemoryHigh -p MemoryMax -p MemorySwapMax -p OOMPolicy -p KillMode -p Restart -p RestartUSec -p StartLimitBurst -p StartLimitIntervalUSec -p TimeoutStopUSec -p ActiveState -p NRestarts` deve informar `4294967296` / `5368709120` / `536870912` / `kill` / `control-group` / `on-failure` / `1min` / `3` / `15min` / `30s` / `active`. Depois, a sonda de admissão do perfil `prod` contra o cgroup da unit: `PYTHONPATH=<source>:<source>/backend <source>/backend/.venv/bin/python backend/scripts/discovery/admission_probe.py --env prod` (sai 0 e imprime `"admitted": true`). O card #1110 só vai a `Pronto` com essa verificação registrada na nota da release.

### Reconhecer o circuito de PROD

`acknowledge_circuit.py --env prod --reason "<motivo>"`, como root, com a Descoberta PROD parada e o cgroup vazio. Sem `--env` o padrão continua sendo DEV (ou `DISCOVERY_RESOURCE_PROFILE`). As regras do circuito não mudam; só a unit e o cgroup verificados passam a ser os do ambiente.

### Migração de banco em PROD

Toda migração em PROD segue `docs/prod-migration-runbook.md`: gatilho antes de publicar, workers afetados parados (inclusive a Descoberta, sem esperar busca ativa), backup `pg_dump` verificado, migração, janela do publish e verificação. A combinação interrompida volta pela recuperação do #1093 com uma tentativa a menos.

## Rollback conservador

Bloquear admissão, parar Discovery e confirmar árvore vazia. Manter os limites e o ledger/resultados. Não executar downgrade destrutivo nem voltar ao worker sem fencing. Uma reversão de algoritmo só pode usar código compatível com posse/geração/schema e o mesmo envelope; na ausência desse adapter, manter Discovery parada até correção. Restaurar o hold exclusivo é reversível e impede restart externo do worker. Não remover drop-ins alheios. Os ensaios isolados cobrem parada/limpeza de árvore, migração aditiva/backfill, recusa de downgrade, lease revogada, escrita tardia rejeitada e reconhecimento administrativo com Discovery vazia.

## Circuito e retry

Há três tentativas duráveis por combinação, com backoffs mínimos 60/300 s e candles congelados reutilizados. Claim incrementa uma vez antes de spawn; Celery/redelivery/restart não concede slots adicionais. Heartbeat 30 s/TTL 300 s é independente do progresso; aviso 120 s e aborto 600 s sem avanço verificável. O reconciler no runtime-worker opera fora do cgroup Discovery em startup/dispatch e a cada 30 s. Cancel impede retry; pause preserva orçamento e prazo. Resultados commitados são reconhecidos após perda de ACK.

A terceira falha recuperável fecha o sweep com `operational_failure/resource_recovery_exhausted`, conserva resultados e marca não iniciados como skipped. O circuito por ambiente bloqueia novas buscas até intervenção. `backend/scripts/discovery/acknowledge_circuit.py --help` informa os argumentos: reconhecimento exige Discovery parada e cgroup vazio, nenhuma lease ativa, probe de admissão em cgroup limitado e motivo obrigatório. A auditoria usa identidade efetiva do administrador; não reseta tentativas nem reabre sweeps terminados.

## Observação e validação isolada

Journal e ledger registram contadores planned/executed/succeeded/failed/unknown/remaining, fase/progresso, pending futures/bytes, spool, RSS/PSS, alocações Python, cache em bytes, cgroup memory.current/peak/swap/events e NRestarts. Cache agregado ≤67108864 bytes, 4096 entradas e 32 snapshots; não confundir MB decimal com MiB. Inputs congelados e spool compartilham quota 2147483648 bytes; retenção máxima 134217728 bytes. Falha de cálculo, quota, I/O ou pool impede resultado/rodada seguinte; não trunca candidatos.

Recursos privados preservados: PostgreSQL16 em `/tmp/card-1093-integration-20261013/pg`, socket no diretório pai, port55493, role `card1093`, DB `crypto_card1093_test`, sem TCP; Redis `card-1093-redis` com `--network none`, teto 128 MiB e socket privado. A carga integral já terminou; ainda assim, estes testes truncam as tabelas Discovery do banco privado e nunca devem apontar para o banco compartilhado. Teardown para somente estes recursos: como dono do cluster, `pg_ctl -D /tmp/card-1093-integration-20261013/pg stop -m fast`; `docker stop card-1093-redis`. Conservar diretórios/container e manifestações para auditoria. Não limpar banco/fila compartilhados.

A carga integral (executada e concluída em 13/10/2026 às 23:39 UTC: 3 buscas, pico de 1,70 GiB, sem OOM) usou `backend/scripts/discovery/original_workload.py --runs 3` em unit transitória previamente verificada com o perfil DEV e banco privado. R1 preserva 492480 candidatos, depois executa todas as rodadas geradas. Oracle independente TA-Lib verifica cada trial e ranking global; manifests/progresso e três relatórios ficam na change. Dados recuperados têm hashes reproduzíveis e atendem janela/contagem histórica; não existe digest histórico dos bytes originais, portanto a identidade binária histórica permanece sem prova. Pilotos reduzidos não contam como busca original.
