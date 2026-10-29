# Crítica de Design — card #1110 (`card-1110-runbook-migracao-teto-prod`)

- Papel: design-critic (filho isolado, rodada 1 de 1 crítico; teto sem-tela 1+1+1).
- Modelo: Claude Opus 5.5 (`claude-opus-5-5`), effort high, conforme `cap-design-critic-1110-a.json` (attempt `cfdd58f7-7885-436b-ac9b-e4b0aeb0cef9`).
- Data: 2026-10-16. Somente leitura: nenhum arquivo do pacote OpenSpec ou de código foi editado; `systemctl show` só para leitura.
- Fontes: issue #1110 (body + 2 comentários, REST), `proposal.md`, `design.md`, `tasks.md`, 4 deltas em `specs/`, specs principais (`discovery-resource-budget`, `dev-restart-discovery`, `prod-discovery-workers`), archive #1093 (`design.md`, `dev_inventory.json`, `apply-evidence.md`), `backend/app/services/discovery_resources.py`, `backend/app/tasks/discovery_celery_tasks.py`, `backend/app/services/combo_optimizer.py`, `backend/app/services/discovery_supervisor.py`, `backend/app/models_discovery.py`, `backend/alembic/env.py`, `backend/scripts/discovery/acknowledge_circuit.py`, `install-discovery-workers-systemd.sh`, `ops/systemd/*discovery*`, `.covenant-flow/overlay.yaml`, `docs/crypto-overlay.md`, `docs/discovery-memory-operations.md`, `docs/release-2026-10-16.md`.

## 1. Tokens do gate

`design.md:63-65`: `UI impact: none` / `live_route: N/A` / `surface: none`, cada um em linha própria, com justificativa curta em `:67` (units, perfil, instalador, runbook; sem tela). Não há rota de catálogo emprestada. **OK.**

## 2. Fidelidade ao issue

- `proposal.md:7-29` copia Problema / História / Entra / Não entra literalmente do body do issue (conferido texto a texto). Nada inventado.
- Valores de Alan respeitados: PROD 4/5 GiB, DEV 3/4 GiB, swap 512 MiB, política de falha igual ao DEV (on-failure, 60 s, 3/900 s, parada até Alan), teto só sem busca ativa, runbook para toda migração. Comentário de Alan ("janela de restart que respeite o StartLimitBurst", "verificação com `systemctl show`") coberto em D8.
- Cobertura de cada item de Entra:

| Entra | Spec | Task |
| --- | --- | --- |
| Runbook para toda migração | `prod-migration-runbook` R1–R3 | 5.1 |
| Overlay + doc da Descoberta com seção PROD | `prod-migration-runbook` R4 | 5.2, 5.3 |
| Evidência da release 2026-10-16 | `prod-migration-runbook` R5 | 5.4 |
| Teto contido sem derrubar DEV/backend | `discovery-resource-budget` R1 (última frase) | 4.1 |
| DEV com teto menor admite e conclui busca normal | `discovery-resource-budget` cenário "Normal DEV search" | 2.x, 6.2 |
| Falha repetida em PROD = DEV | `discovery-resource-budget` cenário "Repeated PROD failure" | 4.1 |
| Teto não interrompe busca ativa | `prod-discovery-workers` R1 | 3.1, 4.3 |
| Limites efetivos visíveis no serviço | `prod-discovery-workers` R2 | 7.2 |

- Não entra: circuito e fluxo do `./restart` DEV não mudam (só o valor esperado em `dev-restart-discovery`, exigido pelo Entra); nenhum teto para backend/runtime/frontend; #1109/#1111 fora. `acknowledge_circuit.py` por ambiente (3.3) não muda regra do circuito; é o mínimo para "parada até Alan agir" valer em PROD. **Sem escopo furado por Não entra.**
- Acréscimo de escopo: a espera por busca ativa dentro do **runbook de migração** (D7 passo 2) não está no issue (o issue pede "workers afetados parados durante a migração"; a regra "não interrompe busca ativa" é do teto). Ver P2-2.

## 3. Fatos técnicos conferidos

| Citação | Resultado |
| --- | --- |
| MemTotal 25.137.336.320 B / 23,41 GiB, swap 4 GiB, 4 CPUs | Confere (`/proc/meminfo` 24.548.180 kB; `nproc`=4) |
| Unit PROD instalada: infinity, OOMPolicy=stop, Restart=always, 5 s, Burst 5/10 s | Confere (`systemctl show`) |
| `discovery_resources.py:35-37`, `:52`, `:53-56`, `:60-64`, `:66-73`, `:106-113`, `:145` | Confere (`MemTotal < memory_max + 17 GiB` em `:111`) |
| `discovery_celery_tasks.py:70-77` admissão só com perfil | Confere |
| `combo_optimizer.py:2119` | Confere |
| `discovery_supervisor.py:317` MemAvailable < 2 GiB / 30 s | Confere |
| `install-discovery-workers-systemd.sh:68`, `:130-147`, `:167` | Confere (trava em `:129-148`) |
| `acknowledge_circuit.py:15,31` | `:15` confere; unit fixa está em `:32` (trivial) |
| Inventário 10,38 GiB | Confere (`other_cgroups_total_bytes` 11.146.293.248). Inclui `user.slice` 5,48 GiB (sessões de agentes) e a própria Descoberta PROD |
| Pico 1.825.865.728 B | Confere (`apply-evidence.md:119`, `original_run_3.json`) |
| Formatos D8 (`1min`, `15min`, `30s`) | Confere contra a unit DEV viva |
| "DDL do PostgreSQL é transacional por revisão" (`design.md:233`) | **Impreciso**: `backend/alembic/env.py:64-65` roda todas as revisões numa só transação (sem `transaction_per_migration`). Falha do `upgrade head` deixa o banco na revisão inicial (salvo operação não transacional). Ver P2-3 |
| Contrato #1093: reserva ≥16 GiB + 1 GiB, base 2 GiB/worker | Confere (`archive/.../design.md:37,39`; spec principal `discovery-resource-budget:7,18`) |

## 4. Pontos de atenção pedidos

### (a) Reserva 16 → 13 GiB e fórmula `(MemoryMax − 1 GiB)/3 GiB`

É **mudança de contrato** de uma spec aprovada no #1093, não só recalibração. A conta é forçada pelos valores de Alan (9 + 16 + 1 = 26 > 23,41), então não há alternativa real que preserve 16 GiB sem mudar os valores dele; Alan escreveu "9 GiB cabe em 23", o que implica a troca, mas não a nomeia. O design é honesto ("Aprovar este Design aprova essa troca", `design.md:144`), mas a troca vive só no corpo de D3; a proposal (`:37`) diz "reserva do host calculada sobre os dois envelopes" sem os números. Também fica escondida a consequência para o cliente: folga de 0,41 GiB; se o MemTotal cair (kernel novo), as duas Descobertas recusam e as buscas de PROD ficam na fila (`design.md:230`, só em Riscos). A base 2 → 1 GiB tem evidência (pico 1,70 GiB da árvore inteira) e não muda o resultado (1 worker nos dois); é visível só como regra. **P2 de contrato (visibilidade)**, ver P2-4.

### (b) Ordem do runbook e falha de migração

Ordem coerente com a prática da release 2026-10-16 (`docs/release-2026-10-16.md:41-42`): parar, backup verificado, publicar, migrar, build, subir, verificar. Dois furos:

1. **Gatilho**: o runbook vale quando há revisão nova "entre `alembic current` e `alembic heads` no source PROD", mas o `heads` do código novo só existe no source depois do passo 5 (`git reset --hard`), quando parar e fazer backup já deveria ter acontecido. O cenário "Pacote sem migração" diz literalmente "no source PROD publicado" (`spec prod-migration-runbook:11`). O operador não consegue aplicar o gatilho na ordem escrita. P2-1.
2. **Falha**: workers e timers ficam parados até Alan, sem distinção. Para os clientes isso significa candles sem atualização, alerta Telegram, Descoberta e refresh de favoritos parados, sem que o runbook diga isso. Como o `env.py` é de transação única, na falha comum o banco fica na revisão do passo 1 e é seguro voltar o SHA e religar o que foi parado. O mesmo vale para "backup ilegível" (nada publicado nem migrado, mas o texto não manda religar). P2-3.

### (c) StartLimit 3/15 min no deploy normal

D8 está correto: o `restart` da janela gasta 1 partida, o `stop` do passo 3 não conta, a release deste card gasta 2 (janela + D6), a 4ª em 15 min dá `start-limit-hit`, e não há `reset-failed` sem Alan. Consequência residual (dita): logo após a release deste card sobra 1 reinício automático em 15 min. A interação do contador de partidas com o `daemon-reload` que troca Burst/Interval é detalhe de Apply (P3). **OK.**

### (d) Sonda de busca ativa falhando fechado

Falhar fechado em erro de banco é correto: sem banco não há teto nem migração seguros. O problema está no critério: `pending` conta como ativo (`design.md:157`). Parar o worker não interrompe uma busca que ainda não começou (a mensagem fica na fila e é consumida na volta), então isso é mais estrito do que Alan pediu ("não interrompe busca ativa"). Somado a buscas de ~6,6 h com 1 worker, fila de clientes e sweep travado (`design.md:231`, "sem forçar"), a espera pode não ter fim. No teto isso só adia este card. No runbook de migração, adia a release inteira com o código já em `main` e o `release-guard post` pendente. Ver P2-2.

## 5. Decisão de operador pendente (`design.md:218-226`)

Bem posta no essencial: pergunta única e clara, três alternativas reais (A medida, B condicionada a medição, C sem admissão), recomendação explícita, consequência em linguagem de operador (buscas até ~3× mais lentas, ~6,6 h contra ~2–3 h, sem SLA) e efeito em specs/tasks de cada escolha (task 1.1 e 2.6). Faltam duas consequências que mudam o peso entre A/B e C:

1. Com A ou B, a admissão passa a valer em PROD pela primeira vez. Uma busca de cliente pode ficar na fila (`resource_budget_unavailable`) quando o host compartilhado tiver MemAvailable < 8 GiB por causa do DEV ou das sessões de agentes (`user.slice` 5,48 GiB no inventário). O texto não diz o que o cliente vê nem como a busca retoma. C não tem esse efeito.
2. Com A, buscas de ~6,6 h alongam a espera do D6 e, se mantida, a do runbook de migração.

## 6. Heurística rápida (operador como usuário do runbook)

- Visibilidade de estado: boa (D8, `systemctl show`, JSON da sonda, mensagem "adiado: busca ativa").
- Prevenção de erro: boa na trava e no backup verificado; fraca no gatilho (P2-1).
- Recuperação: fraca no caminho de falha (P2-3).
- Consistência: o deploy normal interrompe busca (D8 `:212`), o de migração espera sem limite (P2-2).

## Design Critique

- **P2-1 — Gatilho do runbook só se resolve depois de publicar o código** (contrato). `specs/prod-migration-runbook/spec.md:4,11`; `design.md:182,186`. O `alembic heads` do pacote novo só existe no source após o passo 5. Correção: decidir antes do passo 2, depois de `git fetch`, comparando a revisão do banco PROD com os heads de `origin/main` (diff de `backend/alembic/versions` entre `HEAD` e `origin/main`, ou `alembic heads` num checkout descartável) e registrar no passo 1. Trocar "no source PROD publicado" no cenário sem migração. Disposition: rework (autor).
- **P2-2 — Espera por busca ativa no runbook de migração foi acrescentada, sem saída, e `pending` conta como ativa** (escopo). `design.md:157,187,212`; `specs/prod-migration-runbook/spec.md:21-23`; `specs/prod-discovery-workers/spec.md:4`. O issue pede parar os workers na migração. A espera, sem prazo nem desfecho definidos, pode adiar a release sem limite com `main` já publicada, e isso é inconsistente com o deploy normal, que interrompe a busca. Correção: (i) tirar `pending` do critério de ativa (listar, não bloquear), no D5 e nas duas specs; (ii) no runbook, prazo explícito e desfecho ao esgotar (adiar ou parar mesmo assim, com retomada pela recuperação gastando 1 tentativa), apresentado a Alan como escolha na seção de decisão, ou removido para seguir o issue. Disposition: rework (autor).
- **P2-3 — Caminho de falha deixa PROD degradado sem dizer, e o fato do Alembic está impreciso** (contrato). `design.md:197,233`; `specs/prod-migration-runbook/spec.md:25-31`; `backend/alembic/env.py:64-65`. Workers e timers parados até Alan param candles, alerta Telegram, Descoberta e refresh de favoritos para os clientes. Correção: se após a falha `alembic current` for a revisão do passo 1, voltar o SHA e religar o que foi parado (registrando); só manter parado com revisão intermediária. Backup ilegível: religar e encerrar. Declarar a consequência ao cliente e corrigir "transacional por revisão" para "uma transação para todas as revisões". Disposition: rework (autor).
- **P2-4 — Troca de contrato do #1093 (reserva 16 → 13 GiB, base 2 → 1 GiB) e folga de 0,41 GiB só no corpo de D2/D3** (contrato). `design.md:130,142-144,230`; `proposal.md:37`; `specs/discovery-resource-budget/spec.md:4,23`. Correção: números explícitos em What Changes da proposal e uma linha "confirmação junto da aprovação" na seção de decisão (sem alternativa real, pois 9 + 16 + 1 > 23,41), com a consequência da folga: queda de MemTotal recusa as duas Descobertas, PROD inclusive. Corrigir também o exagero de `:142` ("a segunda admissão recusa" depende de MemAvailable ≥ 8 GiB). Disposition: rework (autor).
- **P2-5 — A Decisão de operador pendente omite o efeito da admissão nova em PROD** (produto). `design.md:222-224`. Com A/B, uma busca de cliente pode ficar na fila por memória do host compartilhado (DEV, agentes), e o texto não diz como o cliente vê nem como retoma; com A, a espera do D6 se alonga. Correção: uma linha de consequência em A e B (e o contraste com C). Disposition: rework (autor); a decisão continua de Alan.
- **P3 — Unit PROD sem `DISCOVERY_MARKET_CACHE_DIR`** (apply). `design.md:148`, contra `ops/systemd/criptofarol-dev-discovery-worker.service`. Detalhe de Apply. Disposition: aceito.
- **P3 — Reserva estática contra `user.slice` volátil** (apply). Inventário de 10,38 GiB inclui 5,48 GiB de sessões de agentes. A proteção real é a de runtime (MemAvailable ≥ 8 GiB e < 2 GiB por 30 s). Citar no runbook. Disposition: aceito.
- **P3 — Retenção e limpeza dos backups `pg_dump` (~165 MB cada)** (apply). `design.md:189`. Disposition: aceito.
- **P3 — Contador de StartLimit ao trocar Burst/Interval no `daemon-reload`, e corrida sonda → stop no D6** (apply). `design.md:170,207-210,232`. Disposition: aceito.
- **P3 — `acknowledge_circuit.py:31` → `:32`** (apply). `design.md:82`. Disposition: aceito.
- Tokens `UI impact` / `live_route` / `surface` em linhas próprias (`design.md:63-65`), sem-tela justificado: OK.

Design Agent verdict: rework
