## 1. Testes primeiro (sem systemd real)

- [x] 1.1 Em `backend/tests/unit/test_dev_restart_contract.py`, montar o harness: cópia de `restart` e `install-discovery-workers-systemd.sh` em diretório temporário com raiz canônica, checagem de root, `/etc/systemd/system` e `/sys/fs/cgroup` reescritos; stubs no `PATH` para `systemctl` (estado em arquivo + log), `curl`, `npm`, `alembic`, `sudo` e o instalador do candle writer
- [x] 1.2 Caso Descoberta ativa: exit 0; ordem `stop` → gravação do unit → `daemon-reload` → `enable --now`; um único start da Descoberta; nenhum `restart` dela
- [x] 1.3 Casos Descoberta já parada (exit 0) e unit igual ao template (`stop` acontece mesmo assim)
- [x] 1.4 Caso sobra: `cgroup.procs` falso com o PID de um `sleep` do teste → exit ≠ 0, stderr com cgroup, PID, comando e limites não aplicados; unit falso intacto; sem `daemon-reload`/`enable`
- [x] 1.5 Caso `stop` falha → exit ≠ 0, nada instalado
- [x] 1.6 Em `scripts/test_install_discovery_workers.sh`, caso isolado da trava com sobra listando PID e comando

## 2. Implementação

- [x] 2.1 `restart` (bloco DEV): antes do instalador, `systemctl stop` da Descoberta quando a unit existe; falha do `stop` sai ≠ 0 dizendo que os limites não foram aplicados
- [x] 2.2 `restart`: tirar a Descoberta do `systemctl restart` de backend/frontend; manter o laço final exigindo os quatro ativos
- [x] 2.3 `install-discovery-workers-systemd.sh`: mesma condição da trava; mensagens dizem que os limites não foram aplicados e, na sobra, listam cgroup, PID e comando
- [x] 2.4 `docs/discovery-memory-operations.md`: nota do ciclo da Descoberta no restart normal e do risco de restarts seguidos com busca ativa (circuito)

## 3. Validação

- [x] 3.1 Rodar os testes de 1.x, `scripts/test_install_discovery_workers.sh` e a regressão `backend/tests/integration/test_discovery_memory_recovery.py` / `test_discovery_celery_loss.py` (integração do #1093 pulada no Apply: PostgreSQL/Redis privados parados, ver "Apply notes" abaixo; fica para o QA)
- [x] 3.2 Registrar o roteiro de verificação no DEV (seção "Roteiro de verificação no DEV (QA)" no fim deste arquivo) (T14 deste card, `is-active` dos quatro units, `systemctl show` dos limites, `ActiveEnterTimestamp`, busca interrompida retomando com `attempts` +1) para o QA

## Apply notes (resolução dos P3)

- Fail-fast: se o instalador falha depois do `stop` (sobra, start-limit, drop-in de contenção), o `restart` aborta antes de reiniciar backend, frontend e worker de runtime e diz que a Discovery pode ter ficado parada. Não segue e falha no fim.
- Mensagens em inglês (idioma atual do `restart`/instalador), todas com "limites não aplicados" quando os limites não foram instalados; a sobra lista cgroup, `PID n: comando` (cmdline truncada em 200 caracteres, `comm` ou `?` se o processo sumiu). Nada é morto.
- Start-limit: se `enable --now` falha, o instalador cita `StartLimitBurst=3/900s` ("wait and repeat"); sem `reset-failed`. Se a Discovery não fica ativa, o instalador aponta o drop-in `card-1093-hold.conf` (em `/run` ou `/etc`) quando presente.
- Limites efetivos: o `restart` só imprime `MemoryHigh/MemoryMax/MemorySwapMax` (informativo, `|| true`); a conferência é do QA abaixo.
- Regressão do #1093 (`test_discovery_memory_recovery.py`, `test_discovery_celery_loss.py`): exige PostgreSQL/Redis privados. No Apply, o cluster `/tmp/card-1093-integration-20261013/pg` e o container `card-1093-redis` existem mas estão parados e `DATABASE_URL` privado não está definido; não foram religados nem apontados para o banco compartilhado. Os testes não foram executados; este card não toca o código do #1093.
- Correção do Code Review (P3 mecânicos): `restart` checa o instalador (`-x`) antes do `stop`; stderr do cmdline de PID que sumiu fica limpo; mensagens de falha do `enable --now` com StartLimitBurst/#1093 só em DEV (genérica em PROD); teste de "um único start" também proíbe `start` avulso da Discovery.

## Roteiro de verificação no DEV (QA)

1. Com a Discovery `active` (`systemctl is-active criptofarol-dev-discovery-worker.service`), o T14 deste card executa `./restart`; o passo `restart` deve passar (exit 0) e o card segue.
2. `systemctl is-active` de backend, frontend, runtime-worker e discovery-worker: os quatro `active`.
3. `systemctl show criptofarol-dev-discovery-worker.service -p MemoryHigh -p MemoryMax -p MemorySwapMax` = 5368709120 / 6442450944 / 536870912.
4. `systemctl show criptofarol-dev-discovery-worker.service -p ActiveEnterTimestamp -p NRestarts`: `ActiveEnterTimestamp` posterior ao início do restart; um único start.
5. Busca em andamento: com uma busca pequena rodando, `./restart` direto; sai 0 sem esperar a busca; em até ~10 min `attempts` da combinação sobe 1, a tentativa anterior tem `failure_code=lease_interrupted` e a combinação volta a rodar ou conclui.
6. Evitar mais de 3 restarts em 15 min (teto de partidas) e restarts seguidos com busca ativa (circuito do #1093); ver `docs/discovery-memory-operations.md`.
