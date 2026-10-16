## 1. Pré-condição

- [x] 1.1 Aplicar a decisão de Alan (alternativa A, 2026-10-16): perfil `prod` com 1 worker interno, igual ao DEV, em D1/D4, unit e testes; sem medição com 3 workers

## 2. Perfil de recursos por ambiente (código)

- [x] 2.1 `discovery_resources.py`: tabela de perfis `dev` (3/4 GiB/512 MiB, 1 worker obrigatório) e `prod` (4/5 GiB/512 MiB, 1 worker); perfil desconhecido recusa com `resource_budget_unavailable`
- [x] 2.2 Fórmula `floor((MemoryMax − 1 GiB) / 3 GiB)`, mínimo 1, configuração inválida recusa
- [x] 2.3 Admissão: limites do cgroup iguais aos do perfil; `MemTotal ≥ Σ MemoryMax dos perfis (9 GiB) + 14 GiB`; manter MemAvailable ≥ 8 GiB, SwapFree ≥ 1 GiB, disco ≥ 4 GiB
- [x] 2.4 Chave de ambiente: provar que Descoberta e runtime-worker de PROD resolvem `prod` (presença/valor de `APP_ENV` no `.env` PROD, lido por quem tem root); se divergir, `discovery_environment()` prefere o nome do cgroup `criptofarol-{dev,prod}-*`
  - Apply: o `.env` PROD é `root:root 600` e o filho Apply não o lê. Resolvido sem ele: `discovery_environment()` agora prefere sempre o nome do cgroup `criptofarol-{dev,prod}-*` (as units PROD de Descoberta e runtime-worker não definem `APP_ENV`; `systemctl show` confirma os cgroups `criptofarol-prod-discovery-worker.service` e `criptofarol-prod-runtime-worker.service`), então as duas resolvem `prod` com ou sem `APP_ENV` no `.env`. Testes em `test_discovery_memory.py` (`test_discovery_environment_prefers_unit_name`). **Leitura do `.env` PROD (presença/valor de `APP_ENV`) fica para o operador no deploy**; se o valor existir e for ≠ `prod`, a chave do circuito antigo fica órfã (inofensivo, falhas expiram em 15 min).
- [x] 2.5 Testes unitários: perfis, fórmula (4 GiB→1, 5 GiB→1, 3 GiB→recusa), reserva de dois envelopes, divergência unit × perfil, chave de ambiente; atualizar `test_discovery_memory.py` e `test_dev_restart_contract.py` que fixam 5/6 GiB
- [x] 2.6 Teste de admissão PROD com MemAvailable < 8 GiB: recusa sem reservar combinação, sem tentativa nem falha de circuito, outbox sem ack (reentrega)

## 3. Sonda de busca ativa e circuito por ambiente

- [x] 3.1 Script de leitura em `backend/scripts/discovery/`: ativo = sweep `running|cancelling`, lease válida pelo relógio do PostgreSQL ou tentativa `running` sem fim; `pending`/`paused` listados sem bloquear; JSON com sweeps; erro conta como ativo; testes no banco privado de testes
- [x] 3.2 Sonda de admissão contra o cgroup de uma unit (`admission(group=...)`) com o perfil do ambiente
- [x] 3.3 `acknowledge_circuit.py`: unit/cgroup derivados do ambiente (DEV ou PROD), sem mudar regras do circuito; teste

## 4. Units e instalador

- [x] 4.1 `ops/systemd/criptofarol-prod-discovery-worker.service`: perfil `prod`, 1 worker, spool/StateDirectory PROD, MemoryAccounting, 4G/5G/512M, OOMPolicy=kill, KillMode=control-group, TimeoutStopSec=30s, SendSIGKILL, Restart=on-failure, RestartSec=60, StartLimitBurst=3/900
- [x] 4.2 `ops/systemd/criptofarol-dev-discovery-worker.service`: MemoryHigh=3G, MemoryMax=4G
- [x] 4.3 `install-discovery-workers-systemd.sh`: `--discovery-only` aceito em PROD; sequência sonda/espera (60 s, prazo padrão 30 min, ajustável) → stop só da Descoberta → trava (ativa/cgroup) → reconsulta → grava só a unit → daemon-reload → `enable --now` → imprime `systemctl show`; no adiamento sai ≠ 0 com "adiado: busca ativa" e nada é parado
- [x] 4.4 Testes do instalador (dry-run e contrato): PROD discovery-only lista só a unit da Descoberta; adiamento não para nada; sweep `pending` não bloqueia; DEV sem regressão

## 5. Documentação

- [x] 5.1 Criar `docs/prod-migration-runbook.md` com gatilho antes de publicar (`git fetch` + `alembic heads` de `origin/main` em checkout descartável contra `alembic current`), ordem D7 sem espera por busca ativa, lista fixa de workers afetados e o que para para os clientes, backup com `pg_restore --list`, falhas (backup ilegível e migração sem efeito → religar; revisão intermediária → parado até Alan), StartLimit, reserva contra `user.slice` e passo D6 após a janela
- [x] 5.2 `docs/crypto-overlay.md`: linha de deploy PROD e TL;DR apontam para o runbook quando há migração
- [x] 5.3 `docs/discovery-memory-operations.md`: seção "Discovery PROD" (valores, política, sonda, aplicação, link do runbook) e valores DEV 3/4 GiB no texto
- [x] 5.4 `docs/release-2026-10-16.md`: "Ordem dos passos" da migração reconstruída do journal 13:55–14:02 UTC, backup e Alembic; passo sem fonte marcado "sem registro"; sync do Google Doc da release com `~/.local/bin/gog-bws`

## 6. Validação

- [x] 6.1 Suíte backend da Descoberta e do restart verde; `openspec validate card-1110-runbook-migracao-teto-prod --strict`
- [ ] 6.2 DEV (após `./restart`/T14): `systemctl show` informa 3221225472 / 4294967296 / 536870912 e demais propriedades; uma busca normal DEV admitida e concluída com eventos high/max/oom_kill = 0 <!-- covenant-flow:after-qa -->

## 7. PROD (na release que levar o card)

- [ ] 7.1 Os passos PROD (deploy pela linha do overlay ou pelo runbook se houver migração; aplicar o teto com o instalador PROD discovery-only sem busca ativa; registrar `systemctl show`, a sonda de admissão `prod` e os arranques na nota da release) são executados no fechamento da release (T16) pelo runbook, e o plano fica registrado no card antes do T14; Pronto só com essa evidência <!-- covenant-flow:after-qa -->
