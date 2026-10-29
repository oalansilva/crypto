## Why

A migração de PROD da release 2026-10-16 só deu certo por improviso, e a Descoberta de PROD roda sem teto de memória na mesma máquina do DEV. Alan decidiu em 2026-10-16 aplicar o teto em PROD (4/5 GiB), reduzir o do DEV (3/4 GiB) e escrever o procedimento de migração para toda migração em PROD.

O texto abaixo, de `## Problema` até `## Não entra`, é cópia integral do body do issue #1110 (lido por REST em 2026-10-16). O *como* está em `design.md`.

## Problema
Alan (operador) e os clientes da Descoberta de PROD: a migração de banco da release 2026-10-16 só deu certo porque o procedimento foi improvisado (workers parados, backup antes), sem estar escrito; e a Descoberta de PROD roda sem teto de memória na mesma máquina do DEV, então um estouro num ambiente pode derrubar o outro.

## História
Como operador do Criptofarol, quero um procedimento escrito para migrar o banco de PROD e um teto de memória na Descoberta de PROD, para que a próxima migração seja repetível e um estouro de memória não derrube DEV nem o resto de PROD.

## Entra
**Runbook de migração em PROD**
- Dado qualquer migração de banco a aplicar em PROD, quando o operador seguir o runbook, então: backup antes, workers afetados parados durante a migração, migrar, subir, verificar. Vale para **toda** migração em PROD (decisão de Alan, 2026-10-16), sem julgar compatibilidade caso a caso.
- O runbook é referenciado pelo overlay e a documentação operacional da Descoberta ganha a seção PROD (ou aponta para o runbook).
- A nota da release 2026-10-16 registra a evidência desta migração: backup, ordem dos passos, workers parados.

**Teto de memória da Descoberta de PROD** (substitui o critério de aceite 2 abaixo: é **aplicar**, não decidir; ver comentário de Alan de 2026-10-16)
- Dada a Descoberta de PROD em execução, quando passar do teto, então é contida sem derrubar DEV nem o backend de PROD. Valores decididos por Alan (2026-10-16): **PROD aviso 4 GiB / corte 5 GiB** e **DEV reduzido para aviso 3 GiB / corte 4 GiB** (hoje 5/6). PROD fica maior que DEV porque é o ambiente de clientes. Soma no pior caso = 9 GiB, cabe na máquina (23 GiB). O pico medido da carga completa de DEV (1,7 GiB) cabe no novo teto do DEV.
- Dado o DEV com o novo teto, quando a Descoberta de DEV rodar uma busca normal, então continua admitida e concluindo sem corte (Design confirma que as regras de admissão do DEV seguem válidas com o teto menor).
- Dada falha repetida da Descoberta de PROD, então o comportamento é o mesmo do DEV: reinicia só em falha, espera 1 min, no máximo 3 partidas em 15 min, depois fica parada até Alan agir.
- Dada busca de cliente em andamento em PROD, quando o teto for aplicado, então a aplicação espera a busca terminar (adia ou repete depois); não interrompe busca ativa.
- Verificação: os limites efetivos aparecem no estado do serviço PROD depois de aplicados.

## Não entra
- Mudar o circuito de bloqueio por interrupções (3 em 15 min) nem o fluxo de restart do DEV.
- Teto de memória para outros serviços de PROD (backend, runtime, frontend).
- Higiene do release-guard (#1109) e tipo Harness no board (#1111).


## What Changes

- Novo runbook versionado de migração em PROD (`docs/prod-migration-runbook.md`): decidir se há migração antes de publicar (revisão do banco PROD contra os heads de `origin/main`, depois do `git fetch`), parar os workers afetados (lista fixa), backup `pg_dump` com verificação de leitura, publicar o código, `alembic upgrade head`, subir a janela do publish e verificar. Vale para toda migração em PROD. Diz o que para para os clientes enquanto os workers estão parados e como religar quando o backup é ilegível ou a migração falha sem aplicar nada. O overlay (`docs/crypto-overlay.md`) passa a apontar para ele na linha de deploy PROD.
- Unit `criptofarol-prod-discovery-worker.service` ganha o teto: MemoryHigh=4G, MemoryMax=5G, MemorySwapMax=512M, OOMPolicy=kill, KillMode=control-group, TimeoutStopSec=30s, Restart=on-failure, RestartSec=60, StartLimitBurst=3 em 900 s, perfil `DISCOVERY_RESOURCE_PROFILE=prod` com um worker interno (decisão de Alan, 2026-10-16: 1 worker, igual ao DEV).
- Unit `criptofarol-dev-discovery-worker.service` reduzida para MemoryHigh=3G, MemoryMax=4G (swap 512M e demais propriedades iguais).
- Perfil de recursos por ambiente no código da Descoberta (`discovery_resources.py`): limites esperados por ambiente, fórmula de workers recalibrada para os envelopes novos e reserva do host calculada sobre os dois envelopes (9 GiB). Sem isso a Descoberta DEV com 4 GiB recusaria iniciar.
- Troca de contrato do #1093, confirmada junto com a aprovação do Design: reserva aos demais serviços 16 → 13 GiB; base da fórmula de workers 2 → 1 GiB; folga do host 0,41 GiB (9 + 13 + 1 = 23 GiB ≤ 23,41 GiB). Não há alternativa que preserve o #1093 com os valores de Alan: 9 + 16 + 1 = 26 GiB > 23,41 GiB. Consequência: se o MemTotal da VM cair abaixo de 23 GiB, as duas Descobertas recusam iniciar, PROD inclusive.
- Admissão do #1093 passa a valer em PROD: com 1 worker, uma busca de cliente espera (fica "em execução" sem progresso, sem gastar tentativa) quando o host compartilhado tem menos de 8 GiB livres, e retoma sozinha quando a memória volta.
- Aplicação do teto em PROD só sem busca ativa, com sonda de leitura do ledger do #1093 (busca na fila não bloqueia), espera com prazo e adiamento sem parar nada quando o prazo acaba, e verificação com `systemctl show` dos limites efetivos.
- `docs/discovery-memory-operations.md` ganha a seção PROD (apontando para o runbook) e passa a citar os valores novos do DEV; `docs/release-2026-10-16.md` registra a ordem dos passos da migração desta release.

## Capabilities

### New Capabilities

- `prod-migration-runbook`: procedimento obrigatório para toda migração de banco em PROD (backup verificado, workers afetados parados, migrar, subir, verificar) e sua referência no overlay.

### Modified Capabilities

- `discovery-resource-budget`: o envelope passa a existir por ambiente (DEV 3/4 GiB, PROD 4/5 GiB), com fórmula de workers e reserva do host recalculadas para dois envelopes na mesma VM; a política de restart e o circuito valem também para PROD.
- `dev-restart-discovery`: os limites efetivos verificados após o restart do DEV mudam para 3 GiB / 4 GiB / 512 MiB.
- `prod-discovery-workers`: o teto da Descoberta de PROD é aplicado só sem busca ativa, pelo instalador restrito à unit da Descoberta, e verificado no estado do serviço.

## Impact

- Código: `backend/app/services/discovery_resources.py` (perfis, fórmula, reserva), `install-discovery-workers-systemd.sh` (`--discovery-only` e trava também para PROD), sonda de busca ativa em `backend/scripts/discovery/`, `backend/scripts/discovery/acknowledge_circuit.py` (unit por ambiente), testes unitários correspondentes.
- Units: `ops/systemd/criptofarol-prod-discovery-worker.service`, `ops/systemd/criptofarol-dev-discovery-worker.service`.
- Docs: `docs/prod-migration-runbook.md` (novo), `docs/crypto-overlay.md`, `docs/discovery-memory-operations.md`, `docs/release-2026-10-16.md` (+ sync do Google Doc da release).
- Operação: DEV recebe o teto novo no próximo `./restart` (T14); PROD recebe o teto na release que levar este card, depois da janela do publish. Sem migração de banco, sem tela, sem mudança no circuito nem no fluxo de restart do DEV.
