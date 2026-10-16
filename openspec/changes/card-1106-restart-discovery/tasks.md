## 1. Testes primeiro (sem systemd real)

- [ ] 1.1 Em `backend/tests/unit/test_dev_restart_contract.py`, montar o harness: cópia de `restart` e `install-discovery-workers-systemd.sh` em diretório temporário com raiz canônica, checagem de root, `/etc/systemd/system` e `/sys/fs/cgroup` reescritos; stubs no `PATH` para `systemctl` (estado em arquivo + log), `curl`, `npm`, `alembic`, `sudo` e o instalador do candle writer
- [ ] 1.2 Caso Descoberta ativa: exit 0; ordem `stop` → gravação do unit → `daemon-reload` → `enable --now`; um único start da Descoberta; nenhum `restart` dela
- [ ] 1.3 Casos Descoberta já parada (exit 0) e unit igual ao template (`stop` acontece mesmo assim)
- [ ] 1.4 Caso sobra: `cgroup.procs` falso com o PID de um `sleep` do teste → exit ≠ 0, stderr com cgroup, PID, comando e limites não aplicados; unit falso intacto; sem `daemon-reload`/`enable`
- [ ] 1.5 Caso `stop` falha → exit ≠ 0, nada instalado
- [ ] 1.6 Em `scripts/test_install_discovery_workers.sh`, caso isolado da trava com sobra listando PID e comando

## 2. Implementação

- [ ] 2.1 `restart` (bloco DEV): antes do instalador, `systemctl stop` da Descoberta quando a unit existe; falha do `stop` sai ≠ 0 dizendo que os limites não foram aplicados
- [ ] 2.2 `restart`: tirar a Descoberta do `systemctl restart` de backend/frontend; manter o laço final exigindo os quatro ativos
- [ ] 2.3 `install-discovery-workers-systemd.sh`: mesma condição da trava; mensagens dizem que os limites não foram aplicados e, na sobra, listam cgroup, PID e comando
- [ ] 2.4 `docs/discovery-memory-operations.md`: nota do ciclo da Descoberta no restart normal e do risco de restarts seguidos com busca ativa (circuito)

## 3. Validação

- [ ] 3.1 Rodar os testes de 1.x, `scripts/test_install_discovery_workers.sh` e a regressão `backend/tests/integration/test_discovery_memory_recovery.py` / `test_discovery_celery_loss.py`
- [ ] 3.2 Registrar o roteiro de verificação no DEV do `design.md` (T14 deste card, `is-active` dos quatro units, `systemctl show` dos limites, `ActiveEnterTimestamp`, busca interrompida retomando com `attempts` +1) para o QA
