# Runbook: migração de banco em PROD

Procedimento do operador (Alan ou quem executa o deploy) para publicar em PROD um pacote que **altera o banco**. Vale para qualquer migração Alembic, de qualquer tamanho. Nasceu do card #1110, depois da release 2026-10-16, cuja migração `20261013_0001` foi feita sem procedimento escrito (ver `docs/release-2026-10-16.md`).

Os comandos rodam como root, no host de PROD. Escreva cada comando numa linha própria (não encadeie com `cd ... &&` no meio de um bloco colado).

Constantes de PROD (do overlay `docs/crypto-overlay.md`):

- Source: `/srv/apps/prod/criptofarol/source` (dono root). Banco: `crypto_app`. URL pública: `https://criptofarol.com.br`.
- Janela do publish (units persistentes): `criptofarol-prod-backend`, `-frontend`, `-leads`, `-runtime-worker`, `-discovery-worker` e `-batch-worker` (todas `.service`; o `-batch-worker` consome só a fila `batch_backtest`, #1120).
- Oneshots fora da janela, disparados por timer: `criptofarol-prod-candle-writer.service` e `criptofarol-prod-telegram-alert-scan.service`.

## 1. Gatilho: há migração? (antes de publicar)

Decida **antes de trocar o código**. O source PROD continua no SHA anterior e nenhum worker é parado até aqui.

```
cd /srv/apps/prod/criptofarol/source
git fetch origin
git rev-parse HEAD
cd /srv/apps/prod/criptofarol/source/backend
set -a; source .env; set +a
.venv/bin/alembic current
cd /srv/apps/prod/criptofarol/source
T=$(mktemp -d /tmp/prod-heads-XXXXXX)
git worktree add --detach "$T/co" origin/main
cd "$T/co/backend"
/srv/apps/prod/criptofarol/source/backend/.venv/bin/alembic heads
cd /srv/apps/prod/criptofarol/source
git diff --name-only HEAD origin/main -- backend/alembic/versions
git worktree remove --force "$T/co"
rmdir "$T"
```

- `alembic current` lê o banco PROD e imprime a revisão (por exemplo `20261002_0001 (head)`; compare só o identificador). `alembic heads` lê só os arquivos de revisão de `origin/main` e não conecta ao banco, por isso roda no checkout descartável (fora do source PROD, removido no fim). A listagem de `git diff` é conferência cruzada.
- **Revisão do banco diferente do head de `origin/main` → siga este runbook do início ao fim.** Sem julgar compatibilidade, caso a caso.
- **Igual → não há migração.** Publique pela linha de deploy PROD do overlay (`git reset --hard origin/main`, build, `systemctl restart` da janela). Este runbook não é exigido.
- Mais de um head em `origin/main`: pare e chame Alan. Não migre.
- Registre a comparação (SHA atual, revisão do banco, head de `origin/main`, revisões a aplicar) na nota da release.

## 2. Ordem fixa dos passos

Anote o horário UTC (`date -u +%FT%TZ`) de cada passo; eles vão para a nota da release.

### Passo 1: estado inicial

Registre, sem alterar nada:

- SHA do source PROD, revisão do banco e head de `origin/main` (seção 1).
- Estado das seis units da janela e dos dois timers: `systemctl show UNIT -p ActiveState -p ActiveEnterTimestamp -p NRestarts`.
- Saída da sonda de busca ativa da Descoberta, **só como registro** (este runbook não espera por busca):

```
cd /srv/apps/prod/criptofarol/source/backend
set -a; source .env; set +a
PYTHONPATH=/srv/apps/prod/criptofarol/source:/srv/apps/prod/criptofarol/source/backend .venv/bin/python scripts/discovery/active_search_probe.py
```

Se o source PROD ainda não tem o script, rode-o a partir de um checkout de `origin/main` com o mesmo `PYTHONPATH` apontando para esse checkout e o `.venv` de PROD. Se a sonda falhar, registre "sem registro" e siga.

### Passo 2: parar os workers afetados (lista fixa)

Os workers afetados são exatamente estes (cinco unidades numa release que já tem o worker de lote; quatro na primeira release do #1120), nesta ordem:

1. `criptofarol-prod-candle-writer.timer` e `criptofarol-prod-telegram-alert-scan.timer`, e esperar os oneshots em curso terminarem.
2. `criptofarol-prod-runtime-worker.service`.
3. `criptofarol-prod-discovery-worker.service`.
4. `criptofarol-prod-batch-worker.service` (worker dos lotes, #1120; ausente na primeira release que o instala, onde a lista termina no item 3).

Release que já tem a unit do worker de lote:

```
systemctl stop criptofarol-prod-candle-writer.timer criptofarol-prod-telegram-alert-scan.timer
for u in criptofarol-prod-candle-writer.service criptofarol-prod-telegram-alert-scan.service; do while [ "$(systemctl show "$u" -p ActiveState --value)" = activating ]; do sleep 5; done; done
systemctl stop criptofarol-prod-runtime-worker.service criptofarol-prod-discovery-worker.service criptofarol-prod-batch-worker.service
```

Primeira release com o worker de lote (#1120; a unit ainda não existe em PROD, sem `criptofarol-prod-batch-worker`):

```
systemctl stop criptofarol-prod-candle-writer.timer criptofarol-prod-telegram-alert-scan.timer
for u in criptofarol-prod-candle-writer.service criptofarol-prod-telegram-alert-scan.service; do while [ "$(systemctl show "$u" -p ActiveState --value)" = activating ]; do sleep 5; done; done
systemctl stop criptofarol-prod-runtime-worker.service criptofarol-prod-discovery-worker.service
```

- O `stop` do runtime-worker pode levar até 90 s (`TimeoutStopSec` padrão) e terminar em SIGKILL com `Result=timeout`, porque o refresh de backtests dos favoritos termina o que está fazendo antes de sair. Foi o que aconteceu em 2026-10-16 (13:58:18 a 13:59:48 UTC). Não é falha do runbook: o estado `failed` não impede o `start` do passo 7.
- O `stop` do batch-worker pode levar até 300 s (`TimeoutStopSec=300s`, `KillMode=mixed`): um lote em curso recebe SIGTERM e esse prazo para terminar; passado o prazo o systemd mata o grupo. O lote interrompido volta pela reentrega com o mesmo `task_id` e retoma do próximo passo (itens `collecting`/`optimizing` voltam à fila); ver `docs/runtime-architecture.md`. Na primeira release do #1120 (unit não instalada), use o segundo bloco, sem este `stop`.
- Verifique os cinco (os quatro, na primeira release do #1120): `ActiveState=inactive` (ou `failed` só no runtime-worker por timeout), `MainPID=0` e cgroup vazio.

Release que já tem a unit do worker de lote (os cinco):

```
for u in criptofarol-prod-candle-writer.timer criptofarol-prod-telegram-alert-scan.timer criptofarol-prod-runtime-worker.service criptofarol-prod-discovery-worker.service criptofarol-prod-batch-worker.service; do systemctl show "$u" -p ActiveState -p MainPID -p ControlGroup; done
cat /sys/fs/cgroup/system.slice/criptofarol-prod-runtime-worker.service/cgroup.procs /sys/fs/cgroup/system.slice/criptofarol-prod-discovery-worker.service/cgroup.procs /sys/fs/cgroup/system.slice/criptofarol-prod-batch-worker.service/cgroup.procs
```

Primeira release com o worker de lote (#1120; os quatro, sem `criptofarol-prod-batch-worker`):

```
for u in criptofarol-prod-candle-writer.timer criptofarol-prod-telegram-alert-scan.timer criptofarol-prod-runtime-worker.service criptofarol-prod-discovery-worker.service; do systemctl show "$u" -p ActiveState -p MainPID -p ControlGroup; done
cat /sys/fs/cgroup/system.slice/criptofarol-prod-runtime-worker.service/cgroup.procs /sys/fs/cgroup/system.slice/criptofarol-prod-discovery-worker.service/cgroup.procs
```

  Se algum cgroup ainda listar processo, não prossiga: descubra o que é (`ps -o pid,cmd -p <pid>`) antes de seguir. Nada é morto às cegas.
- **Não há espera por busca ativa.** Uma combinação da Descoberta em execução é interrompida; a recuperação do #1093 a reagenda com uma tentativa a menos (de 3) e conta 1 interrupção no circuito (3 em 15 min abrem o circuito). Se já era a 3ª tentativa daquela combinação, a busca termina com falha (`resource_recovery_exhausted`). Uma migração por janela não abre o circuito sozinha.
- Backend, frontend e leads **continuam servindo** com o código em memória até a janela do passo 7.

### O que para para os clientes (do passo 2 ao passo 7)

Dura minutos. O site e a API seguem no ar com o código antigo. Enquanto os workers estão parados:

- As velas de PROD não atualizam (o gravador roda a cada 15 min).
- Buscas novas da Descoberta ficam em "Varredura pendente" e a busca em curso para.
- Os lotes de backtest (Combo e Otimização) ficam em "na fila" e o lote em curso para; retomam quando o batch-worker volta.
- Os backtests dos favoritos não são atualizados.
- O alerta diário do Telegram (11:05 UTC), se cair na janela, sai atrasado quando o timer voltar (`Persistent=true`).

### Passo 3: backup verificado

O backup fica **fora de qualquer checkout Git**, em diretório 0700 do root, arquivo 0600. Diretório usado até aqui: `/srv/apps/prod/criptofarol/runtime/backups` (não faz parte do source, então `git reset --hard` não o toca).

```
cd /srv/apps/prod/criptofarol/source/backend
set -a; source .env; set +a
D=/srv/apps/prod/criptofarol/runtime/backups
install -d -m 700 "$D"
F="$D/pre-release-AAAA-MM-DD-REVISAO_INICIAL.dump"
# A senha vai por variáveis PG* (ambiente do processo), nunca na linha de comando:
# argumentos aparecem em `ps` e no histórico; o ambiente do processo não.
python3 - "$F" <<'PY'
import os, sys
from urllib.parse import unquote, urlsplit

u = urlsplit(os.environ["DATABASE_URL"])
env = dict(os.environ, PGHOST=u.hostname or "", PGDATABASE=u.path.lstrip("/"))
for key, val in (("PGPORT", u.port), ("PGUSER", u.username), ("PGPASSWORD", u.password)):
    if val:
        env[key] = unquote(str(val))
os.umask(0o077)
os.execvpe("pg_dump", ["pg_dump", "-Fc", "-f", sys.argv[1]], env)
PY
chmod 600 "$F"
pg_restore --list "$F" > "$F.lista"
```

Verifique antes de seguir:

- `pg_restore --list` terminou sem erro.
- Entradas > 0: `grep -vc '^;' "$F.lista"` (linhas que não são cabeçalho).
- A tabela de versão está listada: `grep -c alembic_version "$F.lista"` deve ser pelo menos 1.
- Registre tamanho (`stat -c %s "$F"`), número de entradas e SHA-256 (`sha256sum "$F"`). Na nota da release, sem o caminho completo.

Retenção: guarde o dump até Alan dar a release como `Pronto`; remoção de dumps antigos só com Alan. Cada um tem cerca de 165 MB.

### Passo 4: publicar o código

```
cd /srv/apps/prod/criptofarol/source
git reset --hard origin/main
git rev-parse HEAD
```

O `git fetch` já foi feito na seção 1.

### Passo 5: migrar

```
cd /srv/apps/prod/criptofarol/source/backend
set -a; source .env; set +a
.venv/bin/alembic upgrade head
.venv/bin/alembic current
```

O `current` precisa ser igual ao head registrado no passo 1. O `upgrade head` roda todas as revisões numa **transação única** (`backend/alembic/env.py`); uma falha comum desfaz tudo e o banco fica na revisão inicial. Só uma operação fora de transação (por exemplo `autocommit_block`) deixaria o banco numa revisão intermediária. Se o `upgrade` falhar, vá para a seção 3.

### Passo 6: build

```
cd /srv/apps/prod/criptofarol/source
VITE_API_URL=/api VITE_APP_ENV=production npm --prefix frontend run build
```

### Passo 7: subir a janela e religar os timers

Antes de reiniciar, confira o limite de partidas (seção 4).

Release que já tem a unit do worker de lote:

```
systemctl restart criptofarol-prod-backend.service criptofarol-prod-frontend.service criptofarol-prod-leads.service
systemctl restart criptofarol-prod-runtime-worker.service
systemctl restart criptofarol-prod-discovery-worker.service
systemctl restart criptofarol-prod-batch-worker.service
systemctl start criptofarol-prod-candle-writer.timer criptofarol-prod-telegram-alert-scan.timer
```

Primeira release com o worker de lote (#1120): a unit do batch-worker ainda não existe em PROD, então não há `restart` dela; instale-a com `./install-discovery-workers-systemd.sh --root /srv/apps/prod/criptofarol/source --batch-only` (seção 5), que já a liga:

```
systemctl restart criptofarol-prod-backend.service criptofarol-prod-frontend.service criptofarol-prod-leads.service
systemctl restart criptofarol-prod-runtime-worker.service
systemctl restart criptofarol-prod-discovery-worker.service
./install-discovery-workers-systemd.sh --root /srv/apps/prod/criptofarol/source --batch-only
systemctl start criptofarol-prod-candle-writer.timer criptofarol-prod-telegram-alert-scan.timer
```

### Passo 8: verificar

- `alembic current` igual ao head registrado no passo 1.
- As seis units da janela `active`, com `ActiveEnterTimestamp` dentro da janela, e `NRestarts` registrado.
- Os dois timers `active` (`systemctl list-timers 'criptofarol-prod-*'`).
- `curl -s -o /dev/null -w '%{http_code}\n' https://criptofarol.com.br/api/health` devolve `200`.
- Journal sem erro desde o passo 2: `journalctl -u criptofarol-prod-backend -u criptofarol-prod-runtime-worker -u criptofarol-prod-discovery-worker -u criptofarol-prod-batch-worker --since "<horário do passo 2>" -p err --no-pager`.
- Estado da Descoberta PROD: `systemctl show criptofarol-prod-discovery-worker.service -p MemoryHigh -p MemoryMax -p MemorySwapMax -p OOMPolicy -p KillMode -p Restart -p RestartUSec -p StartLimitBurst -p StartLimitIntervalUSec -p TimeoutStopUSec -p ActiveState -p NRestarts`. Esperado depois do card #1110 aplicado: `4294967296` / `5368709120` / `536870912` / `kill` / `control-group` / `on-failure` / `1min` / `3` / `15min` / `30s` / `active`.

### Passo 9: evidência

Registre em `docs/release-AAAA-MM-DD.md`: horário de cada passo, o backup (tamanho, número de entradas, SHA-256), as revisões aplicadas e os workers que ficaram parados, mais o resultado do passo 8. Um passo sem fonte verificável entra como "sem registro", nunca inventado.

## 3. Falhas

- **Backup ilegível** (`pg_restore --list` falha, lista zero entradas ou não lista `alembic_version`): nada foi publicado nem migrado. Religue os três serviços (runtime, Descoberta e batch-worker) e os dois timers (`start` dos cinco), verifique e registre. Encerre o runbook **sem migrar**.
- **`alembic upgrade head` falha e `alembic current` ainda é a revisão do passo 1** (caso comum: a transação única desfez tudo): volte o source ao SHA do passo 1 (`git reset --hard <SHA>`), religue os três serviços e os dois timers (runtime, Descoberta e worker de lote) com o código anterior, verifique e registre. A correção da migração fica com Alan, numa nova janela.
- **`alembic upgrade head` falha e `alembic current` não é a revisão inicial nem o head, ou não responde** (revisão intermediária): volte o source ao SHA do passo 1, **mantenha os workers e os timers parados**, não execute downgrade (o do ledger da Descoberta recusa) e avise Alan. A decisão entre restaurar o backup e corrigir para frente é dele.

Religar significa: `systemctl start` do runtime-worker, da Descoberta, do batch-worker e dos dois timers, depois a verificação do passo 8. Cada partida da Descoberta gasta uma das três do limite (seção 4).

## 4. Limite de partidas (StartLimit) da Descoberta PROD

A unit da Descoberta PROD aceita no máximo **3 partidas em 900 s** (`StartLimitBurst=3`, `RestartSec=60`, `Restart=on-failure`). A quarta em 15 min é recusada (`start-limit-hit`) e a unit fica parada até Alan agir.

- O `stop` do passo 2 não conta. O `restart` do passo 7 conta 1. Religar após uma falha (seção 3) conta 1.
- Deploy normal: 1 partida. Release que também aplica o teto (seção 5): janela (1) + aplicação do teto (1) = 2.
- Antes de repetir um restart, confira `systemctl show criptofarol-prod-discovery-worker.service -p NRestarts -p ActiveState -p Result` e espere a janela de 15 min passar. **Nunca rode `reset-failed` na Descoberta sem Alan.**
- O restart normal de PROD continua interrompendo a busca em curso, como hoje.

## 5. Teto da Descoberta PROD (depois da janela)

Se o pacote também muda a unit da Descoberta PROD (card #1110), aplique o teto **depois do passo 8**, nunca no meio da migração:

```
cd /srv/apps/prod/criptofarol/source
./install-discovery-workers-systemd.sh --root /srv/apps/prod/criptofarol/source --discovery-only
```

O instalador consulta a sonda e espera até 30 min por ausência de busca ativa (`--wait-idle <min>` muda o prazo; `0` não espera). Esgotado o prazo, sai com código 75 e "adiado: busca ativa", sem parar nem gravar nada; repita depois. Sem busca ativa, ele para só a Descoberta PROD, recusa se a unit seguir ativa ou o cgroup tiver processo, grava só essa unit, recarrega e liga uma vez, e imprime o `systemctl show` de verificação do passo 8. Pendentes (`pending`) e pausados (`paused`) são listados e não bloqueiam. Detalhes e valores em `docs/discovery-memory-operations.md` (seção "Discovery PROD").

### Worker dos lotes em PROD (#1120)

O worker dos lotes (`criptofarol-prod-batch-worker.service`, fila `batch_backtest`) é independente da Descoberta: roda ao mesmo tempo, tem cgroup, spool (`/var/tmp/criptofarol-prod-batch`) e teto próprios (4 GiB aviso, 5 GiB corte, `OOMPolicy=kill`) e não depende da sonda de busca ativa. Para instalá-lo (primeira release do #1120: no lugar do `restart` dele no passo 7) ou atualizar a unit (release que a muda: **depois do passo 8**):

```
cd /srv/apps/prod/criptofarol/source
./install-discovery-workers-systemd.sh --root /srv/apps/prod/criptofarol/source --batch-only
```

Se a unit estiver ativa, o instalador a para antes (um lote em curso tem até 300 s para terminar; depois é interrompido e retoma pela reentrega), grava só essa unit, recarrega e liga uma vez, e imprime o `systemctl show` (`MemoryHigh`, `MemoryMax`, `MemorySwapMax`, `OOMPolicy`, `KillMode`, `Restart`, `TimeoutStopUSec`, `ActiveState`). Não toca na Descoberta, no runtime-worker nem no backend. Sem `--batch-only`, o instalador completo recusa reescrever uma Descoberta PROD ativa (seção 5). Evidência do fechamento (T16): inclua `criptofarol-prod-batch-worker` em `services=` do `PROD_DEPLOY_EVIDENCE`; o overlay o lista e o `release-guard post` o exige.

## 6. Reserva de memória contra `user.slice`

A Descoberta DEV (até 4 GiB) e a PROD (até 5 GiB) dividem a VM com os demais serviços e com as sessões de agentes (`user.slice`, volátil). A admissão exige `MemTotal` de pelo menos 9 GiB (soma dos dois tetos) mais 14 GiB (13 GiB para os demais serviços e 1 GiB de margem), `MemAvailable` de pelo menos 8 GiB, swap livre de pelo menos 1 GiB e disco livre de pelo menos 4 GiB. A VM tem 23,41 GiB: sobra 0,41 GiB. Se o `MemTotal` cair abaixo de 23 GiB, **as duas Descobertas recusam** (`resource_budget_unavailable` no journal) e as buscas de clientes ficam em "Varredura em execução", sem progresso, até alguém ajustar a reserva.

A reserva estática não garante nada sozinha. A proteção real é a de execução: admissão com `MemAvailable` de pelo menos 8 GiB e parada da tentativa se `MemAvailable` ficar abaixo de 2 GiB por 30 s. Antes da janela, confira:

```
grep -E 'MemTotal|MemAvailable|SwapFree' /proc/meminfo
systemctl status user.slice --no-pager
```

Os workers dos lotes (#1120, tetos de 4 GiB em DEV e 5 GiB em PROD) **não entram** nessa conta de admissão: o lote não passa pela admissão da Descoberta, e o teto do cgroup é só o corte. O pico medido de uma árvore de otimização com 1 worker é 1,70 GiB; o lote usa o mesmo perfil de 1 worker. Duas Descobertas e dois lotes ao mesmo tempo podem, no pior caso de teto, passar do que a VM reserva; vigie `MemAvailable` na primeira semana com o lote em PROD.

Com `MemAvailable` abaixo de 8 GiB a busca de PROD não começa; o pedido volta pelo outbox (a cada cerca de 10 min) quando a memória voltar. Não gasta tentativa nem abre o circuito.

## 7. Referências

- Overlay, regra de deploy PROD: `docs/crypto-overlay.md`.
- Descoberta (limites, circuito, sonda, teto): `docs/discovery-memory-operations.md`.
- Release de exemplo, com a ordem reconstruída: `docs/release-2026-10-16.md`.
