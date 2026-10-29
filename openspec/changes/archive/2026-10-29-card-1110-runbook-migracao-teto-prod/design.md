## Context

Status: Design. Briefing copiado do issue #1110 (REST, 2026-10-16) em `proposal.md`. Valores de Alan (2026-10-16): PROD aviso 4 GiB / corte 5 GiB; DEV aviso 3 GiB / corte 4 GiB; falha repetida em PROD igual ao DEV; teto em PROD só sem busca ativa; runbook para toda migração em PROD; 1 worker interno na Descoberta PROD (alternativa A).

UI impact: none
live_route: N/A
surface: none

Sem superfície: o card mexe em units systemd, perfil de recursos do worker, instalador e runbook de operação; nenhuma tela, componente ou texto de produto muda. Prototype: N/A. Impeccable: N/A (operação de serviços, sem tela).

Estado verificado no repo e no host em 2026-10-16:

- Host: MemTotal 25.137.336.320 B (23,41 GiB), swap 4 GiB, 4 CPUs, `/var/tmp` com ~51 GB livres. Inventário #1093 dos demais cgroups: 10,38 GiB (`dev_inventory.json`), dos quais 5,48 GiB são `user.slice` (sessões de agentes). Hoje: PROD backend 0,96 GiB, PROD runtime 0,44 GiB, Descoberta PROD 0,16 GiB.
- `criptofarol-prod-discovery-worker.service` instalada: MemoryHigh/Max/SwapMax=infinity, OOMPolicy=stop, Restart=always, RestartSec=5s, StartLimitBurst=5/10s, sem `DISCOVERY_RESOURCE_PROFILE`.
- `backend/app/services/discovery_resources.py`:
  - `:35-37` o perfil tem um só jogo de limites, fixo em 5/6 GiB/512 MiB; `configured()` (`:60-64`) troca só o nome, nunca os limites.
  - `:52` `capacity = (memory_max − 2 GiB) // 3 GiB`; `:53-54` capacidade < 1 recusa; `:55-56` DEV exige 1 worker.
  - `:106-113` a admissão exige limites do cgroup **iguais** aos do perfil, `MemTotal ≥ MemoryMax + 17 GiB`, `MemAvailable ≥ 8 GiB`, `SwapFree ≥ 1 GiB` e disco ≥ 4 GiB.
  - `:145` a chave de ambiente é `DISCOVERY_RESOURCE_PROFILE`, senão `APP_ENV`, senão o nome do cgroup.
- `backend/app/tasks/discovery_celery_tasks.py:70-77`: admissão só roda com `DISCOVERY_RESOURCE_PROFILE` definido. Em PROD não roda. Na recusa, o orquestrador sai antes de reservar combinações e sem `ack_outbox`: não gasta tentativa nem circuito, e o outbox reentrega o pedido depois de `DISCOVERY_OUTBOX_REDELIVERY_SECONDS` (600 s), enquanto o dispatcher do runtime-worker roda.
- `discovery_resources.py:66-73` + `combo_optimizer.py:2119`: sem perfil, o otimizador fica "unprofiled" com `cpu_count − 1` = **3 workers internos**. É o que PROD usa hoje.
- `discovery_supervisor.py:317`: `MemAvailable < 2 GiB` por 30 s aborta a tentativa (vale nos dois ambientes).
- `discovery_recovery.py:214-260`: uma combinação interrompida (lease vencida) vira `lease_interrupted`, conta 1 no circuito (3 em 15 min) e volta para a fila com backoff se ainda tiver tentativa (máximo 3); na 3ª, a busca termina `failed` (`resource_recovery_exhausted`).
- `backend/alembic/env.py:64-65`: `context.begin_transaction()` sem `transaction_per_migration`. O `upgrade head` roda **todas** as revisões numa transação só; uma falha comum desfaz tudo e o banco fica na revisão inicial. Só uma operação fora de transação (ex.: `autocommit_block`, hoje sem uso em `backend/alembic/versions`) deixaria revisão intermediária.
- `install-discovery-workers-systemd.sh`: `:68` `--discovery-only` só DEV; `:130-147` trava (ativa / cgroup com processo) só DEV; `:167` `enable --now`.
- `backend/scripts/discovery/acknowledge_circuit.py:15,32`: cgroup e unit DEV fixos.
- Units PROD que o runbook para: `criptofarol-prod-candle-writer.timer` (a cada 15 min, `Persistent=true`), `criptofarol-prod-telegram-alert-scan.timer` (diário 11:05 UTC, `Persistent=true`), `criptofarol-prod-runtime-worker.service` (dispatcher do outbox da Descoberta e refresh dos backtests de favoritos, `RUN_FAVORITE_BACKTEST_REFRESH=1`) e a Descoberta PROD.
- Medição #1093 (carga completa DEV, 1 worker, 3 buscas): pico da árvore inteira 1.825.865.728 B (1,70 GiB), swap 0, eventos high/max/oom = 0, ~6,6 h por busca.

### Conflito com as regras do #1093

Com os valores de Alan, o código atual recusa a Descoberta DEV:

1. A fórmula com DEV `MemoryMax=4 GiB` dá `floor((4−2)/3) = 0` e a admissão recusa (`resource_budget_unavailable`). PROD 5 GiB daria 1.
2. A admissão compara os limites do cgroup com os do perfil fixo 5/6 GiB. Com qualquer unit nova, a comparação falha nos dois ambientes.
3. A reserva "16 GiB aos demais + 1 GiB fora do envelope" (spec `discovery-resource-budget`) pressupõe um só envelope. Com dois (4 + 5 = 9 GiB), 9 + 16 + 1 = 26 GiB > 23,41 GiB. O teste do código (`MemoryMax + 17 GiB`) passa em cada ambiente isolado (21 e 22 GiB ≤ 23,41), mas não prova o pior caso dos dois juntos.

Resolução em D1–D3, sem mudar nenhum valor de Alan. A troca de contrato do #1093 que isso exige está em D3 e em **Decisão de Alan: workers PROD**.

## Goals / Non-Goals

**Goals:**

- Runbook versionado para toda migração em PROD, citado pelo overlay.
- Teto 4/5 GiB na Descoberta PROD e 3/4 GiB na DEV, com admissão do #1093 válida nos dois.
- Política de falha repetida em PROD igual à do DEV.
- Aplicar o teto em PROD só sem busca ativa e verificar com `systemctl show`.
- Docs da Descoberta com a seção PROD; nota da release 2026-10-16 com a ordem dos passos.

**Non-Goals:**

- Circuito (3 interrupções em 15 min), tentativas, backoff, fluxo do `./restart` do DEV.
- Teto para backend, runtime, frontend ou leads de PROD.
- Release-guard (#1109), Tipo Harness (#1111).
- Restart normal de PROD sem migração (segue a linha atual do overlay).
- Migração de banco neste card: ele não traz nenhuma.

## Decisions

### D1. Perfil de recursos por ambiente

`ResourceProfile` passa a vir de uma tabela por ambiente no código, chaveada por `DISCOVERY_RESOURCE_PROFILE`:

| Perfil | MemoryHigh | MemoryMax | MemorySwapMax | requested_workers |
| --- | --- | --- | --- | --- |
| `dev` | 3 GiB | 4 GiB | 512 MiB | 1 (obrigatório) |
| `prod` | 4 GiB | 5 GiB | 512 MiB | 1 (decisão de Alan, A) |

Nome desconhecido recusa (`resource_budget_unavailable`). A comparação exata unit × perfil continua: se o código e a unit divergirem, a busca fica na fila e não roda. Cache, spool, batch e retenção não mudam.

Alternativa rejeitada: ler os limites do próprio cgroup e confiar neles. Perde a prova de que a unit instalada é a aprovada.

### D2. Fórmula de workers recalibrada pela medição

`effective_workers = min(requested, floor((MemoryMax − 1 GiB) / 3 GiB))`. Mínimo admissível 1; configuração inválida recusa início.

- DEV 4 GiB → 1. PROD 5 GiB → 1. `MemoryMax < 4 GiB` → 0 → recusa.
- A base de 2 GiB do #1093 era proposta de Design sem medição. A medição veio depois: a árvore inteira (pai, supervisor, 1 worker, IPC, page cache) chegou a 1,70 GiB. Cabe em 1 + 3 = 4 GiB e fica abaixo do aviso DEV de 3 GiB, com 1,30 GiB de folga, sem throttling esperado.
- O envelope de 3 GiB por worker, que cobre temporários, fica igual.

Alternativa rejeitada: base 2 GiB e 2 GiB por worker. Também dá 1, mas encolhe o envelope por worker, que não foi medido sozinho.

### D3. Reserva do host com dois envelopes (troca de contrato do #1093)

A admissão passa a exigir `MemTotal ≥ Σ MemoryMax de todos os perfis do host (4 + 5 = 9 GiB) + 14 GiB` (13 GiB aos demais serviços + 1 GiB de margem). A soma vem da tabela D1, não do outro cgroup. Assim o teste fica determinístico e cobre o pior caso dos dois juntos.

Conta: 9 + 14 = 23 GiB ≤ 23,41 GiB (folga 0,41 GiB). Os demais cgroups medidos somavam 10,38 GiB, page cache incluído, abaixo de 13. `MemAvailable ≥ 8 GiB`, `SwapFree ≥ 1 GiB` (dois swaps de 512 MiB ≤ 4 GiB) e a parada por `MemAvailable < 2 GiB` ficam iguais.

A reserva estática não garante recusa da segunda busca: a admissão só recusa se, no momento, `MemAvailable < 8 GiB`. Se as duas Descobertas crescerem depois de admitidas, quem protege é o corte de cada cgroup e a parada da tentativa por `MemAvailable < 2 GiB` por 30 s, sem OOM global.

Troca de contrato, aprovada junto com este Design:

- Reserva aos demais serviços: 16 → 13 GiB.
- Base da fórmula de workers: 2 → 1 GiB (D2).
- Folga do host: 0,41 GiB.
- Sem alternativa que preserve o #1093: 9 + 16 + 1 = 26 GiB > 23,41 GiB, e os 9 GiB são valores de Alan.
- Consequência: se o MemTotal cair abaixo de 23 GiB (kernel novo, memória reservada pelo hypervisor), **as duas Descobertas recusam**, PROD inclusive. As buscas de clientes ficam em "Varredura em execução" sem progresso até alguém ajustar a reserva (fail closed, `resource_budget_unavailable` no journal).

### D4. Units

- **PROD**: igual à DEV em contenção e reinício. `DISCOVERY_RESOURCE_PROFILE=prod`, `DISCOVERY_INTERNAL_WORKERS=1`, `DISCOVERY_SPOOL_DIR=/var/tmp/criptofarol-prod-discovery`, `StateDirectory=criptofarol-prod-discovery`, `MemoryAccounting=yes`, `MemoryHigh=4G`, `MemoryMax=5G`, `MemorySwapMax=512M`, `OOMPolicy=kill`, `KillMode=control-group`, `TimeoutStopSec=30s`, `SendSIGKILL=yes`, `Restart=on-failure`, `RestartSec=60`, `StartLimitIntervalSec=900`, `StartLimitBurst=3`.
- **DEV**: só `MemoryHigh=3G` e `MemoryMax=4G` mudam.
- O estouro de PROD é contido no cgroup próprio: `oom-kill` só da árvore da Descoberta PROD, sem OOM global. Com `on-failure` + 60 s + 3/900 s, a quarta partida em 15 min é recusada e a unit fica parada até Alan agir. Sem `reset-failed` automático.
- Chave de ambiente: com o perfil `prod`, a Descoberta usa `prod`. O runtime-worker PROD (dispatcher/reconciler) usa `APP_ENV`, senão o cgroup (`prod`). O Apply prova que os dois consumidores PROD resolvem a mesma chave (o `.env` PROD é root 600; lê-se só a presença/valor de `APP_ENV`). Se `APP_ENV` existir com valor ≠ `prod`, `discovery_environment()` passa a preferir o nome do cgroup `criptofarol-{dev,prod}-*`. Assim circuito e spool não mudam de chave.

### D5. Sonda de busca ativa (ledger do #1093)

Script de leitura em `backend/scripts/discovery/` (nome é detalhe do Apply). Usa o banco do ambiente e o relógio do PostgreSQL. Considera **busca ativa** (bloqueia) se houver qualquer um destes:

- sweep em `running` ou `cancelling`;
- combinação com `lease_owner` e `lease_expires_at > clock_timestamp()`;
- `discovery_attempts` com `state='running'` e `finished_at IS NULL`.

Sweeps em `pending` (na fila, sem execução) e `paused` são **listados, mas não bloqueiam**: parar o worker não interrompe o que ainda não começou, e a mensagem é consumida na volta.

Sai 0 quando ocioso e com código próprio quando ativo. Imprime JSON com os sweeps encontrados e falha fechado: erro de banco conta como ativo. Uma combinação em backoff deixa o sweep `running`, então a espera cobre o intervalo entre tentativas.

A sonda bloqueia só a aplicação do teto (D6). No runbook de migração (D7) ela é só registro.

### D6. Aplicar o teto em PROD

`install-discovery-workers-systemd.sh --root /srv/apps/prod/criptofarol/source --discovery-only` passa a valer em PROD e faz, em ordem:

1. Roda a sonda. Com busca ativa, reconsulta a cada 60 s por até 30 min (padrão; `--wait-idle <min>` muda o prazo). Esgotado o prazo, **adia**: sai ≠ 0 dizendo "adiado: busca ativa", lista os sweeps, não para, não grava e não reinicia nada. O operador repete depois (decisão de Alan: "adia ou repete depois").
2. `systemctl stop` só da Descoberta PROD.
3. Trava igual à DEV, estendida a PROD: unit inativa e cgroup vazio, senão recusa sem matar nada.
4. Reconsulta a sonda. Lease nova entre o passo 1 e o 2 fica registrada no aviso.
5. Grava só a unit da Descoberta PROD, faz `daemon-reload` e `enable --now` (uma partida).
6. Imprime o `systemctl show` de verificação (D8).

Runtime-worker, backend, frontend e leads não são reescritos nem reiniciados.

Com 1 worker, uma busca grande leva ~6,6 h. A janela ociosa pode demorar, e o operador pode precisar repetir em outro horário. O card só vai a Pronto com D8 verificado, então fica aguardando até lá.

Alternativa rejeitada: só procedimento manual. A espera vira hábito do operador, e o issue exige não interromper.

### D7. Runbook de migração em PROD

Mora em `docs/prod-migration-runbook.md`, ao lado das outras notas operacionais versionadas. A linha de deploy PROD do overlay (`docs/crypto-overlay.md`, regra de release/lote) passa a dizer: "pacote com migração (`alembic` com revisão nova): seguir `docs/prod-migration-runbook.md`; sem migração: linha atual". O TL;DR do overlay ganha uma linha. `docs/discovery-memory-operations.md` ganha a seção "Discovery PROD" com valores, política, sonda, D6 e link para o runbook, e passa a citar os valores novos do DEV.

**Gatilho, decidido antes de publicar.** Depois de `git fetch origin` no source PROD, sem trocar o código: comparar `alembic current` do banco PROD com `alembic heads` de `origin/main`, rodado num checkout descartável (`git worktree add --detach <tmp> origin/main`, fora do source PROD e removido no fim; `heads` lê só os arquivos de revisão). Conferência cruzada: `git diff --name-only HEAD origin/main -- backend/alembic/versions`. Revisão do banco diferente do head de `origin/main` → runbook. Igual → linha atual do overlay. Sem julgar compatibilidade.

Ordem:

1. **Pré**: registrar o SHA atual do source PROD, `alembic current`, o head de `origin/main` e as revisões a aplicar (gatilho acima), o estado das units e a saída da sonda D5 (só registro).
2. **Parar os afetados (lista fixa)**: `criptofarol-prod-candle-writer.timer` e `criptofarol-prod-telegram-alert-scan.timer`, esperando os oneshots em curso terminarem; depois `criptofarol-prod-runtime-worker.service` e `criptofarol-prod-discovery-worker.service`. Verificar `ActiveState=inactive`, `MainPID=0` e cgroup vazio. Backend, frontend e leads seguem servindo com o código em memória e reiniciam na janela. Não há espera por busca ativa: o issue pede parar os workers. Uma combinação da Descoberta em execução é interrompida e reagendada pela recuperação do #1093, com uma tentativa a menos (de 3) e 1 interrupção no circuito. Se já era a 3ª tentativa, a busca termina como falha.
3. **Backup**: `pg_dump -Fc` do banco PROD (`crypto_app`) em diretório root 0700 fora de qualquer checkout Git, arquivo 0600. Verificar a leitura com `pg_restore --list`: lista legível, nº de entradas > 0 e `alembic_version` presente. Registrar tamanho, entradas e SHA-256.
4. **Publicar código**: `git reset --hard origin/main` (o fetch já foi feito).
5. **Migrar**: `alembic upgrade head` com o ambiente PROD. Depois, `alembic current` precisa ser igual ao head registrado no passo 1.
6. **Build** do frontend (linha atual do overlay).
7. **Subir**: `systemctl restart` da janela do publish do overlay e `start` dos dois timers.
8. **Verificar**: units da janela ativas, com arranque dentro da janela e `NRestarts`; timers ativos; `https://criptofarol.com.br/api/health` 200; journal sem erro desde o passo 2; Descoberta com o `systemctl show` D8.
9. **Evidência** na `docs/release-<data>.md`: horários de cada passo, backup (tamanho, entradas, SHA, sem o caminho completo), revisões, workers parados.

**O que para para os clientes entre o passo 2 e o 7** (minutos, na prática): as velas de PROD não atualizam (gravador a cada 15 min); buscas novas da Descoberta ficam em "Varredura pendente" e a em curso para; os backtests dos favoritos não são atualizados; o alerta diário do Telegram (11:05 UTC), se cair na janela, sai atrasado, ao religar o timer (`Persistent=true`). O site e a API seguem no ar com o código antigo.

**Falhas:**

- **Backup ilegível** (passo 3): nada foi publicado nem migrado. Religar os dois serviços e os dois timers, verificar e registrar. Encerrar sem migrar.
- **Migração falha e `alembic current` é a revisão do passo 1** (caso comum: a transação única desfez tudo): voltar o source ao SHA do passo 1, religar os dois serviços e os dois timers com o código antigo, verificar e registrar. Alan decide a correção numa nova janela.
- **Migração falha e o banco ficou em revisão intermediária ou desconhecida** (operação fora de transação, ou `alembic current` não responde): source volta ao SHA do passo 1, workers e timers seguem parados, e Alan decide entre restaurar o backup e corrigir para frente. Sem downgrade automático (o do ledger da Descoberta recusa).

Se o pacote também alterar a unit da Descoberta PROD (este card), o passo D6 roda **depois** do passo 8, nunca no meio.

### D8. Verificação e efeito do StartLimit no publish

Verificação: `systemctl show criptofarol-prod-discovery-worker.service -p MemoryHigh -p MemoryMax -p MemorySwapMax -p OOMPolicy -p KillMode -p Restart -p RestartUSec -p StartLimitBurst -p StartLimitIntervalUSec -p TimeoutStopUSec -p ActiveState -p NRestarts`. Esperado: `4294967296` / `5368709120` / `536870912` / `kill` / `control-group` / `on-failure` / `1min` / `3` / `15min` / `30s` / `active`. Mais os arquivos `memory.high/max/swap.max/oom.group` do cgroup e uma sonda de admissão (`admission(group=<cgroup da unit>)` com o perfil `prod`). A sonda prova que código e unit batem. DEV: `3221225472` / `4294967296` / `536870912` após o `./restart`.

StartLimit no publish de PROD:

- Deploy normal: o `systemctl restart` da janela gasta 1 das 3 partidas em 15 min.
- Deploy com migração: o `stop` do passo 2 não conta; a janela conta 1. Religar após falha (D7) também conta 1.
- Release deste card: janela (1) + D6 (1) = 2.
- O risco é repetir a janela várias vezes, ou somar uma falha real: a 4ª partida em 15 min é recusada (`start-limit-hit`), o `restart` sai ≠ 0 e a Descoberta fica parada.
- O runbook manda conferir o estado antes de repetir, esperar a janela de 15 min e nunca rodar `reset-failed` sem Alan.
- O restart normal continua interrompendo a busca em curso, como hoje (fora do escopo, aviso no runbook).

### D9. Nota da release 2026-10-16

O Apply reconstrói a ordem real a partir de fontes, sem inventar. Usa o journal das units PROD de 2026-10-16 13:55–14:02 UTC (stop/start), o `mtime` do backup e a saída do Alembic já registrada. Acrescenta "Ordem dos passos" sob "Git, CI e PROD". Passo sem fonte fica marcado "sem registro". A nota existe no Drive, então o Google Doc é sincronizado (`~/.local/bin/gog-bws`).

## Decisão de Alan: workers PROD

**Decidido por Alan em 2026-10-16: alternativa A, 1 worker interno na Descoberta PROD, igual ao DEV.** Hoje PROD roda 3 processos de cálculo por busca, porque não tem perfil. Com o perfil `prod` e a fórmula D2, passa a 1.

- Medido: 1,70 GiB de pico, bem abaixo do aviso de 4 GiB. Libera CPU para o backend de PROD e para o DEV nesta VM de 4 CPUs.
- Velocidade: buscas grandes ficam até ~3× mais lentas do que hoje. A carga de referência leva ~6,6 h com 1 worker; com 3, estimam-se ~2–3 h. Não existe SLA de velocidade.
- Admissão nova em PROD: pela primeira vez, uma busca de cliente pode esperar por memória. Se o host compartilhado tiver menos de 8 GiB livres (DEV, sessões de agentes), a busca não começa. O cliente vê a busca em "Varredura em execução", com o progresso parado; não há mensagem específica na tela, e o motivo `resource_budget_unavailable` fica só no journal do worker. A busca não gasta tentativa nem circuito e retoma sozinha quando o outbox reentrega o pedido (a cada ~10 min) e a memória voltou.
- Espera do teto: com buscas mais longas, achar PROD ociosa para o D6 demora mais (D6, adiamento).
- Specs e tasks seguem A. Sem medição com 3 workers (antiga B) e sem remover o perfil (antiga C).

Confirmado junto com a aprovação do Design: reserva aos demais serviços 16 → 13 GiB, base da fórmula 2 → 1 GiB, folga 0,41 GiB, sem alternativa (9 + 16 + 1 > 23,41); se o MemTotal cair, as duas Descobertas recusam, PROD inclusive (D3).

## Risks / Trade-offs

- [Folga de 0,41 GiB em D3] → Queda de MemTotal recusa as duas Descobertas (fail closed). O runbook cita a conta.
- [Reserva estática contra `user.slice` volátil] → A proteção real é a de runtime (`MemAvailable ≥ 8 GiB` na admissão e `< 2 GiB` por 30 s na tentativa). O runbook cita.
- [Sweep travado em `running` impede o teto para sempre] → A sonda lista o sweep e o adiamento aponta o diagnóstico do #1093. Sem forçar.
- [Corrida sonda → stop] → Janela de segundos, reconsulta no passo 4. Uma busca que comece nesse intervalo retoma pela recuperação (1 tentativa).
- [Backend serve durante a migração] → É a prática atual. O `upgrade head` roda numa transação só (`env.py:64-65`), então o backend em memória vê o esquema antigo ou o novo, nunca o meio; DDL pode esperar lock enquanto houver consulta aberta. O restart da janela traz o código novo.
- [Migração interrompe a Descoberta] → Sem espera, a combinação em curso gasta 1 tentativa e 1 interrupção no circuito; uma migração por janela não abre o circuito sozinha.
- [DEV com teto menor] → O `./restart` do DEV já para a Descoberta antes de instalar (#1106). Código e unit chegam no mesmo commit.
- P3 aceitos para o Apply: nomes de script/flag, caminho e retenção do diretório de backup, forma da tabela de perfis, ajuste dos testes que fixam 5/6 GiB (`test_discovery_memory.py`, `test_dev_restart_contract.py`). `validation_snapshot.py` é evidência histórica do #1093 e não muda.

## Migration Plan

Sem migração de banco. DEV recebe o teto no `./restart` da integração (T14): código e unit juntos. PROD recebe na release que levar o card: janela normal primeiro, depois D6 sem busca ativa e D8. O card só vai a Pronto com D8 verificado em PROD. Rollback: reinstalar a unit anterior pela mesma D6 (espera busca, uma partida). O ledger não é tocado.

## Open Questions

Nenhuma.

## Design Critique

- P2-1 — Gatilho do runbook só se resolvia depois de publicar. Disposition: resolvido no rework; gatilho decidido após `git fetch`, com `alembic heads` de `origin/main` num checkout descartável (D7 "Gatilho", spec `prod-migration-runbook`).
- P2-2 — Espera por busca ativa no runbook e `pending` como ativa. Disposition: resolvido; espera removida do runbook (interrupção reagendada pelo #1093 com uma tentativa a menos), `pending` listado sem bloquear (D5), teto com prazo de 30 min e adiamento sem parar nada (D6).
- P2-3 — Caminho de falha degradava PROD sem dizer; Alembic impreciso. Disposition: resolvido; religar quando `alembic current` é a revisão inicial ou o backup é ilegível, parar só com revisão intermediária, efeito ao cliente declarado, transação única descrita (D7, Context).
- P2-4 — Troca de contrato do #1093 escondida. Disposition: resolvido; números em `proposal.md` (What Changes), em D3 e na linha de confirmação; exagero da "segunda admissão" corrigido.
- P2-5 — Efeito da admissão nova em PROD para o cliente. Disposition: resolvido; o que o cliente vê, como retoma e a espera mais longa do teto (Decisão de Alan).
- P3 — Unit PROD sem `DISCOVERY_MARKET_CACHE_DIR`. Disposition: aceito (Apply).
- P3 — Reserva estática contra `user.slice` volátil. Disposition: aceito; citado em Risks e no runbook.
- P3 — Retenção e limpeza dos backups `pg_dump` (~165 MB cada). Disposition: aceito (Apply).
- P3 — Contador de StartLimit ao trocar Burst/Interval no `daemon-reload`, e corrida sonda → stop no D6. Disposition: aceito (Apply).
- P3 — `acknowledge_circuit.py:31` → `:32`. Disposition: aceito; corrigido no Context.

Design Agent verdict: approve
