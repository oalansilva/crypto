## Context

Status: Design. Briefing copiado do issue #1106 (REST, 2026-10-16) em `proposal.md`; decisões do grill: parar sempre a Descoberta antes de instalar os limites, conferir que nada sobrou e religar; busca em andamento é interrompida.

UI impact: none
live_route: N/A — restart do DEV e scripts de operação, sem tela
surface: none

Impeccable: N/A — card de operação (restart, instalador, systemd), sem tela, componente ou copy visível. Prototype: N/A.

Estado atual (verificado no código e no host DEV em 2026-10-16):

- `restart`, bloco `CANONICAL DEV RESTART`: linhas 58-64 chamam `install-discovery-workers-systemd.sh` em todo restart; linhas 69-73 param o worker de runtime e fazem `systemctl restart` de backend, frontend e Descoberta; o laço final (94-108) só sai 0 com backend/frontend respondendo e runtime + Descoberta ativos.
- `install-discovery-workers-systemd.sh:125-137` (#1093), só DEV: recusa se a unit está ativa e recusa se `cgroup.procs` do `ControlGroup` não está vazio ("Legacy Discovery descendants remain; refusing coexistence.", sem dizer quais). Depois grava os units, `daemon-reload` e `systemctl enable --now` (runtime + Descoberta).
- Unit `ops/systemd/criptofarol-dev-discovery-worker.service`: MemoryHigh=5G, MemoryMax=6G, MemorySwapMax=512M, KillMode=control-group, TimeoutStopSec=30s, SendSIGKILL=yes, Restart=on-failure, StartLimitBurst=3 em 900 s. No host: unit ativa, limites já efetivos, sem drop-in.
- T14 roda o restart em `scripts/process-fsm/t14.py:357-363` com timeout de 600 s; código ≠ 0 vira `I8` com o stderr.
- Recuperação do #1093 (`docs/discovery-memory-operations.md:29-31`, `discovery_recovery.py`): 3 tentativas por combinação, contadas no claim; lease interrompida expira (TTL 300 s), o reconciler do worker de runtime marca `lease_interrupted` e reagenda com backoff 60/300 s.

## Goals / Non-Goals

**Goals:** restart do DEV com a Descoberta ligada sai 0 sem passo manual; a Descoberta é sempre parada antes de instalar, conferida vazia e ligada uma vez com os limites do #1093; sobra de processo vira falha clara sem aplicar limites; Descoberta já parada segue como hoje.

**Non-Goals:** mudar os limites de memória do #1093, StartLimit, tentativas, backoff ou circuito; PROD; restart fora do source canônico; esperar a busca terminar.

## Decisions

### D1. O restart para a Descoberta; o instalador continua sendo a trava

No bloco DEV do `restart`, antes de chamar o instalador: se a unit existe (`systemctl cat`), `systemctl stop criptofarol-dev-discovery-worker.service`. O `stop` é síncrono: SIGTERM para todo o cgroup, SIGKILL após 30 s, e só retorna com a parada concluída; também cancela um auto-restart pendente. Se o `stop` falhar, o restart sai ≠ 0 dizendo que a Descoberta não parou e que os limites não foram aplicados. Unit inexistente (primeira instalação) pula o `stop`; Descoberta já parada faz `stop` sem efeito, que é o "como hoje".

Em seguida o instalador roda **com a mesma condição** de hoje (unit ativa → recusa; `cgroup.procs` não vazio → recusa). É ele que "confere que nada sobrou", tanto no restart quanto no cutover manual de `docs/discovery-memory-operations.md`.

Alternativas: (i) `--stop-discovery` no instalador — mistura orquestração com a trava, e o instalador chamado à mão passaria a parar o serviço; (ii) a ideia (b) do issue (trava só quando o envelope muda) — descartada no grill; (iii) `systemctl restart` depois de instalar — é exatamente aplicar units novos sobre árvore viva.

### D2. Mensagem da sobra diz o que restou

Mudança só no texto da trava: ao recusar por cgroup não vazio, o instalador lista cada PID com seu comando (`/proc/<pid>/cmdline`, truncado; "?" se o processo sumiu entre a leitura) e o caminho do cgroup, e diz que os limites não foram aplicados. Nada é morto nem forçado. A recusa por unit ativa também passa a dizer que os limites não foram aplicados. Esse stderr é o que o T14 grava no `I8`.

### D3. Descoberta ligada uma vez, já limitada

O `enable --now` do instalador liga a Descoberta com os units recém-gravados. O `systemctl restart` das linhas 70-73 deixa de incluir a Descoberta (fica backend e frontend); o laço final segue exigindo os quatro ativos. Assim cada restart faz **um** start da Descoberta, como antes do #1093, e não dois — com StartLimitBurst=3/900 s, dois starts por restart esgotariam o limite já no segundo restart em 15 min.

Os limites efetivos são os do template; a própria Descoberta já verifica os limites na admissão (#1093). O restart não duplica essa conferência; a prova fica em `systemctl show` no DEV (abaixo).

### D4. Busca em andamento: sem código novo

A parada interrompe a tentativa (no máximo uma, `--pool=solo --concurrency=1`). A lease expira em até 300 s, o reconciler registra `lease_interrupted` e reagenda com backoff; a busca retoma com uma tentativa a menos. Este card não toca nesse caminho.

## Como provar os critérios

Automatizado, sem systemd real (padrão de `test_dev_restart_contract.py`: cópia do script com caminhos reescritos):

- Copiar `restart` e o instalador para um diretório temporário, reescrevendo raiz canônica, checagem de root, `/etc/systemd/system` e `/sys/fs/cgroup` para caminhos do teste; stubs no `PATH` para `systemctl` (estado em arquivo + log de chamadas), `curl`, `npm`, `alembic`, `sudo` e o instalador do candle writer.
- Casos: (a) Descoberta ativa → exit 0; ordem no log `stop` → gravação do unit → `daemon-reload` → `enable --now`; um único start da Descoberta; nenhum `restart` dela. (b) já parada → exit 0, mesma ordem. (c) unit instalado igual ao template → `stop` acontece mesmo assim. (d) sobra: o stub do `stop` deixa no `cgroup.procs` falso o PID de um `sleep` do teste → exit ≠ 0, stderr com o PID, o comando e "não aplicados"; unit falso intacto, sem `daemon-reload`/`enable`. (e) `stop` falha → exit ≠ 0, nada instalado.
- `scripts/test_install_discovery_workers.sh` ganha o caso (d) isolado do instalador.
- Busca interrompida: regressão dos testes do #1093 (`test_discovery_memory_recovery.py`, `test_discovery_celery_loss.py`) que já cobrem lease expirada → `lease_interrupted` → nova tentativa.

Verificação no DEV (QA):

- O T14 **deste** card é a prova principal: com a Descoberta `active` antes, o passo `restart` passa e o card sai de QA.
- Depois: `systemctl is-active` dos quatro units; `systemctl show -p MemoryHigh,MemoryMax,MemorySwapMax` = 5368709120 / 6442450944 / 536870912; `ActiveEnterTimestamp` da Descoberta posterior ao início do restart (parou e religou com config igual).
- Busca em andamento: com uma busca pequena rodando, `./restart` direto; sai 0 sem esperar a busca; em até ~10 min `attempts` da combinação sobe 1, a tentativa anterior tem `failure_code=lease_interrupted` e a combinação volta a rodar ou conclui.
- Sobra de processo não é provocada no DEV (exigiria processo imortal); fica no teste automatizado.

## Risks / Trade-offs

- [Restarts seguidos com busca ativa] cada interrupção é falha operacional do #1093: 3 em 15 min abrem o circuito do ambiente (Descoberta bloqueada até `acknowledge_circuit.py`) e a 3ª na mesma combinação fecha a busca com `resource_recovery_exhausted`. → Aceito pelo grill (tentativa gasta); registrado em `docs/discovery-memory-operations.md`; sem mudança no circuito.
- [StartLimit] o 4º restart em 15 min recusa o start (`start-limit-hit`) e o restart falha. → Um start por restart (D3); sem `reset-failed` automático, para não furar o limite do #1093; a mensagem do systemd chega ao stderr.
- [Tempo] a parada soma até ~60 s (SIGTERM 30 s + SIGKILL) ao restart. → Cabe nos 600 s do T14.
- [Ordem] a Descoberta passa a subir antes do restart do backend. → Ela não depende do HTTP do backend; migrações já rodaram antes.
- [Bootstrap] até este card entrar no develop, outros T14 seguem caindo em `I8`. → Contorno manual do issue.

## Migration Plan

Entra pelo T14 normal; sem migração de banco nem mudança de unit. Rollback = reverter o commit; o contorno manual volta a valer.

## Open Questions

Nenhuma de produto. Texto exato e idioma da mensagem são detalhe de Apply.
