# Design — Descoberta: cancelamento auto-finaliza, sem travar em `cancelling` (card #853)

## Problema

`DiscoveryService.command(cancel)` só aplica a transição para `cancelling` e
marca `cancellation_requested`, sem reconciliar nem agendar finalização. Os
três caminhos que poderiam chamar `reconcile_sweep` — único que promove
`cancelling -> cancelled` (marcando pendentes como `skipped`) — estão
fechados para esse estado:

- `ensure_sweep_wakeup` recusa criar intent com estado `!= running`;
- `_repair_incomplete_sweeps` só varre `pending`/`running`;
- `dispatch_outbox` só publica intents `pending` (o caso PROD já estava `acked`).

Resultado: com outbox `acked` e 0 combinações `running`, ninguém mais toca no
sweep. Caso real PROD: sweep `#564f92f1`, 694 combinações, travado em
`cancelling` com 690 `pending` / 4 `succeeded` / 0 `running` — e o rascunho
segue congelado até o estado terminal (Q2).

Decisões de operador já tomadas e fora de discussão: Q1 = cancelar com
avaliações em voo aguarda as em curso terminarem e conclui sozinho; Q2 =
rascunho libera só após a conclusão, via estado terminal. Pause/resume não
mudam.

## Decisão de design

O comando `cancel` finaliza sozinho, em dois tempos — reconciliação imediata
+ wake-up finalizador para o caso com voo:

1. **Reconcilia na hora, sob o lock do comando.** `command(cancel)` já adquire
   o lock da linha (`_lock_sweep`). Após `_apply_transition` para
   `cancelling`, o comando reutiliza `reconcile_sweep` no mesmo commit:
   combinações `pending` viram `skipped` imediatamente (comportamento atual do
   reconciliador, preservado); se `pending == 0` **e** `running == 0`, promove
   `cancelling -> cancelled` com `completed_at` ali mesmo. Isso fecha na hora
   o caso PROD (690 `pending` / 0 `running` → `cancelled` na resposta do
   comando) e todo cancel sem voo.
2. **Com `running` em voo, agenda/finaliza via wake-up finalizador (Q1).**
   Se `running > 0`, o sweep permanece `cancelling` — as avaliações em curso
   NÃO são forçadas a `skipped`, terminam sozinhas como `succeeded`/`failed`.
   No mesmo commit, o comando insere um intent `pending` (nova `generation`)
   no `DiscoveryOutbox` através de um método dedicado `ensure_cancel_wakeup`:
   exceção estreita e explícita ao guarda de `ensure_sweep_wakeup`, que
   continua recusando `cancelling` para wake-ups normais de claiming (nada
   novo é reclamado sob cancelamento). Dedup igual ao existente: se já houver
   intent `pending`/`delivered` em aberto, não duplica. `dispatch_outbox`
   publica intents `pending` sem filtro por estado do sweep, então o
   finalizador é entregue sem filtro novo. No caminho do intent (P1): com o
   sweep em `cancelling`, `claim_combinations` devolve `[]` (só `running`
   reclama), o orquestrador executa o release **escopado ao sweep**
   (`_release_expired_leases_for_sweep`, flush-only, sem commit próprio) +
   `reconcile_sweep` sob lock e dá `ack` — tudo num único commit do sweep (opção (a): ack integrado ao commit do sweep via variante flush-only - ex. `_ack_locked`, só flip `delivered` para `acked`, sem commit próprio; o `ack_outbox` atual, com commit próprio, NÃO é chamado neste caminho);
   o `release_expired_leases` global com commit próprio é REMOVIDO desse
   caminho (nunca roda entremeado: um release global com commit próprio
   ressuscitaria `running` expirado em `pending` de `cancelled` de OUTRO
   sweep sem reconcile acoplado, quebrando o invariante
   "nenhum `pending` sobrevive ao commit"). O `reconcile` em que
   `pending == 0` e `running == 0` (relidos pós-refresh sob lock) promove
   `cancelling -> cancelled`. Concorrência coberta pelos dois lados: se um
   orquestrador ativo ainda estiver no laço, os seus `reconcile` por
   combinação + final fecham; se o cancel chegou depois do último `reconcile`
   (ou o worker caiu), o finalizador fecha. Ambos os caminhos são
   idempotentes.

### Guarda anti-corrida cancel × claim (P0)

A leitura de `running == 0` no comando só vale sob o lock da linha
(`_lock_sweep`, `SELECT … FOR UPDATE`), com releitura real após o lock:
`_lock_sweep` devolve a linha bloqueada e o apply executa
`db.refresh(locked)` (ou `expire` + reload) explícito antes de qualquer
decisão — o objeto do identity map sem refresh ainda carrega valores
pré-lock. `claim_combinations` passa a obedecer à mesma ordem:
**lock do sweep → `db.refresh(locked)` explícito → verifica
`state == running` pós-refresh → reclama `pending`
(`FOR UPDATE SKIP LOCKED`) → commit único**, e TODA decisão de
guarda/transição do claim usa valores pós-refresh. O lock serializa os
dois lados: um claim concorrente bloqueia no lock do cancel e, ao adquiri-lo,
vê `cancelling`/`cancelled` pós-refresh e devolve `[]` sem tocar em linha
alguma — nenhum claim commita depois do fechamento inline.

Defesa em profundidade no lado terminal (para claim commitado na janela
antes do lock): `reconcile_sweep` ganha re-finalizador terminal — sob
`cancelled` (como já faz sob `cancelling`), qualquer `pending` residual vira
`skipped` e contadores/`processed` são recalculados; `run_combination`
distingue o pré-check: sob `cancelling` devolve a combinação a `pending`
(para o `reconcile` marcar `skipped`); sob `cancelled`/terminal marca
`skipped` direto, nunca `pending` (o pré-check não cria `pending`). O release
escopado ao sweep (único permitido nestes caminhos — o global com commit
próprio foi removido deles, § P1) PODE mover `running` expirado → `pending` de
forma transitória inclusive sob terminal (inclusive sob `cancelled`), mas a
conversão é garantida pelo `reconcile` no mesmo commit por sweep do repair
(ou, para settle que commitar após o fechamento, pelo recount do próximo
repair): nenhum `pending` sobrevive ao commit e `processed = total`
permanece invariante.

### Lock do reconcile + terminal de cancelamento nunca sobrescrito (P0)

`reconcile_sweep` (todos os chamadores: comando inline, orquestrador,
repair) SHALL adquirir `_lock_sweep` (`SELECT … FOR UPDATE`) na entrada e
executar `db.refresh(locked)` (ou `expire` + reload) explícito após o lock,
relendo estado + contadores (`pending`/`running`/`processed`/`total`) —
nenhuma decisão de transição terminal ou guarda claim×cancel usa leitura
pré-lock; toda decisão usa valores pós-refresh. Regra
transacional: **terminal de cancelamento nunca é sobrescrito por reconcile
tardio** — se o estado relido sob lock for `cancelled` (ou qualquer outro
terminal), o reconcile faz SOMENTE re-finalização residual (`pending → skipped`
+ recount de `processed`/contadores, flush) e NUNCA promove para outro
terminal nem reescreve `state`/`completed_at`. Em particular, o caminho
`running → completed` exige `state == running` relido sob lock; um reconcile
que leu `running` antes do commit do cancel observa `cancelling`/`cancelled`
após o lock e cai no caminho de cancelamento/re-finalização — nunca promove
`running → completed` por cima de `cancelled`. A reconciliação inline do
comando já roda sob o lock do comando, logo satisfaz a mesma regra sem lock
duplo.

Ordem no comando (um commit só, ver § Atomicidade): lock →
`db.refresh(locked)` explícito → `_apply_transition` →
reconciliação inline (flush, sem commit) → decisão terminal sobre valores
pós-refresh → insert do finalizador SOMENTE se, após o reconcile inline,
ainda `cancelling` com `running > 0` (se o inline já promoveu a `cancelled`,
nenhum insert) → commit único → resposta.
3. **Reparo cura os travados e fecha resíduo terminal (P1).**
   `_repair_incomplete_sweeps` (dentro de `dispatch_outbox`) inclui sweeps
   `cancelling`: reconcilia, e se ainda houver `running`, garante o
   finalizador via `ensure_cancel_wakeup`. Assim o sweep PROD já travado
   (`acked`, 0 `running`) vira `cancelled` no primeiro dispatch após o
   deploy — sem backfill, sem migração, sem reprocessar as 690 ignoradas.
   O repair cobre ADICIONALMENTE `cancelled` com resíduo — condição
   `pending > 0 OR running > 0 OR processed != total` (claim de janela
   pré-lock cujo settle commitou após o fechamento inline, quando o
   finalizador já deu `ack` e nenhum reconcile futuro estava agendado):
   sob o lock do sweep, o repair executa o release escopado flush-only do sweep e, na sequência, converte o `pending` residual para `skipped` e recalcula
   `processed`/contadores (flush) no commit por sweep, sem mudar
   `state`/`completed_at` e sem agendar wake-up novo. Sem o release, `cancelled` com `running` de lease expirado e worker morto nunca convergiria: o release devolve-o a `pending` transitoriamente e o `reconcile` do mesmo commit marca `skipped`. O settle tardio
   commita o resultado normalmente; é o recount do próximo repair que
   restaura `processed = total`. Invariante mantida, sem agendador extra.

### Atomicidade do comando (P1)

`reconcile_sweep` hoje tem `db.commit()` próprio; o comando **não** pode
chamá-lo como está e alegar "mesmo commit". O apply extrai a reconciliação
para um helper sem commit (ex.: `_reconcile_locked`, flush-only) usado tanto
pelo comando quanto pelo `reconcile_sweep` público (que mantém o commit para
os chamadores atuais). Ordem de commits do comando: **um único `db.commit()`**
cobrindo transição + `pending → skipped` + contadores + promoção a
`cancelled` + insert do finalizador. Estado observável em falha parcial:
qualquer exceção antes do commit faz rollback total — o sweep permanece no
estado anterior (sem `skipped` parcial, sem intent órfão); retry do comando
ou o reparo do próximo dispatch curam. Após o commit, só dois estados
existem: `cancelled` com `processed = total`, ou `cancelling` + finalizador
`pending` em aberto. Meio-estado (`skipped` sem `cancelled`, `cancelled` sem
contadores) é impossível por construção.

### Ordem de commits no `dispatch_outbox` (P1)

O repair roda **dentro** do dispatch; a ordem transacional é declarada para
não deixar meio-estado:

1. **Fase repair, um commit por sweep, com isolamento (P1/P2):** para cada
   sweep `cancelling` — e para cada `cancelled` com resíduo (`pending > 0`
   OR `running > 0` OR `processed != total`) — cada sweep roda em transação
   própria, sob lock, nesta ordem: `release_expired_leases` **escopado ao
   sweep** (ver § `release_expired_leases` escopado; vale também sob
   `cancelled`) → reconciliação (flush) →
   `ensure_cancel_wakeup` se `cancelling` com `running > 0` (NUNCA sob
   `cancelled`) → commit. **Isolamento de falha por sweep:** commit/rollback
   + `expire`/limpeza da sessão por sweep, sem transação única abrangendo o
   laço; exceção num sweep faz rollback só da transação do sweep e segue
   para o próximo ("falha num sweep não contamina" a
   sessão nem os demais); o próximo dispatch retenta o sweep falho.
   `begin_nested()`/savepoint só se o apply adotar txn única com locks
   retidos — NÃO é o padrão aqui.
2. **Fase outbox, um commit único:** flips `stale delivered → pending`
   (redelivery TTL) + marcações `pending → delivered` do laço de publicação
   (respeitando `OUTBOX_BATCH_SIZE` / `OUTBOX_MAX_GLOBAL` /
   `OUTBOX_MAX_PER_SWEEP`) → commit único. Falha de broker mantém o intent
   `pending` (caminho `except` já existente); falha antes do commit deixa os
   intents `pending`, republicáveis no próximo dispatch — nunca `delivered`
   sem enqueue, nunca intent perdido.

### `release_expired_leases` escopado no repair/dispatch (P1)

O `release_expired_leases` global (varredura de todos os sweeps, com commit
próprio) NÃO pode rodar dentro do laço por sweep do repair: quebraria o
"commit por sweep" e tocaria sweeps fora do escopo. O apply extrai um helper
escopado flush-only (ex.: `_release_expired_leases_for_sweep(sweep_id)`,
`WHERE sweep_id = :id AND lease_expires_at < now()`, sem commit) e o repair
usa SOMENTE ele, dentro da transação do sweep, nesta ordem: lock do sweep →
`db.refresh(locked)` explícito → release escopado (flush) → reconciliação
(flush) → `ensure_cancel_wakeup` se aplicável → commit por sweep. O release
global com commit próprio é REMOVIDO também do caminho do intent do
orquestrador: esse caminho usa SOMENTE o helper escopado ao sweep do intent
(`WHERE sweep_id = :id`), flush-only, no mesmo commit que o
`reconcile_sweep` sob lock + `ack` flush-only via `_ack_locked` (sem commit próprio - opção (a); `ack_outbox` NÃO é chamado aqui) (ordem: claim vazio → lock →
`db.refresh(locked)` → release escopado do sweep (flush) → reconcile sob
lock (flush) → ack flush-only → commit único). Se o release global for mantido para
qualquer outro caminho legado, ele NUNCA cobre sweeps `cancelling`/`cancelled`
nem roda com commit próprio entremeado num commit por sweep — todo
`running → pending` acontece somente dentro de um commit que contém o
reconcile do mesmo sweep, preservando o invariante "nenhum `pending`
sobrevive ao commit".

### `ensure_cancel_wakeup` sob lock e limites (P2)

Ordem estrita sob o lock do sweep já adquirido pelo chamador (`command` ou
repair): **lock → dedup (`pending`/`delivered` em aberto para o sweep,
`ORDER BY generation DESC LIMIT 1`) → insert da próxima `generation`
(`max+1`) `pending` sob o mesmo lock**, sem commit próprio (integra o commit
do chamador). Limites `OUTBOX_MAX_PER_SWEEP`/`OUTBOX_MAX_GLOBAL` são de
**publicação**, não de inserção: o finalizador é sempre inserido; sob
limite, permanece `pending` (adiado) e é republicado nos dispatches
seguintes dentro do bound `OUTBOX_POLL_LIMIT`/`OUTBOX_BATCH_SIZE` — o sweep
fecha com atraso, sem operador. Idempotência de finalizador duplo: cancel
repetido, repair + comando, ou redelivery `stale → pending` nunca duplicam
porque o dedup enxerga `pending`/`delivered` em aberto antes de inserir, e a
chave de idempotência de publicação (`sweep_id` + `generation`) faz o
orquestrador reexecutar sem reexecutar combinações com resultado.
Corrida de dedup (dois inserts concorrentes da mesma `generation`):
SEM savepoint — `IntegrityError` no Postgres aborta a transação, logo NÃO
há "retorna `created: False`" após violação de constraint única. Dois
desfechos, sem meio-termo: (a) dedup enxergou o intent em aberto → sem
insert, retorna `created: False` de forma limpa e o commit do chamador
prossegue; (b) a corrida furou o dedup e a constraint única
(`sweep_id`, `generation`) acusou → rollback TOTAL da transação do
chamador (comando ou sweep do repair), sem `created: False`, com cura por
retry do comando ou pelo repair do próximo dispatch (que re-lê o dedup e
converge para exatamente um finalizador em aberto) — já previsto em
§ Atomicidade. Nenhum `begin_nested()`/savepoint só ao redor do insert.

### Repeat-cancel passa pelo ensure (P2)

O early-return do `command` para sweep já `cancelling` (cf. `command`
linhas 1054–1056) NÃO retorna antes do ensure: sob o lock, o comando repete
reconciliação (flush) + `ensure_cancel_wakeup` com o mesmo dedup
(`pending`/`delivered` em aberto → sem insert) no commit do comando — cancel
repetido nunca duplica o finalizador e nunca deixa `cancelling` com
`running` sem finalizador em aberto. Repeat-cancel sob `cancelled` é no-op
idempotente (sem wake-up, sem tocar `state`/`completed_at`); resíduo
eventual fica para o repair do próximo dispatch (§ Reparo). Tasks 4.2 cobre:
repetido não duplica + garante exatamente um finalizador em aberto.

Por que não alternativas: estender `ensure_sweep_wakeup` para `cancelling`
reabriria claiming sob cancelamento (viola Q1); um worker/cron novo fora do
outbox duplicaria o canal at-least-once já existente; forçar `running` a
`skipped` violaria Q1.

## Escopo

- `command(cancel)`: reconciliação inline + `ensure_cancel_wakeup` quando
  restar `running`; resposta continua `{sweep_id, state}`.
- `_repair_incomplete_sweeps`: cobrir `cancelling` (reconcilia + finalizador
  se preciso) e `cancelled` com resíduo (`pending > 0 OR running > 0 OR
  `processed != total`: só residual pós-refresh `pending → skipped` + recount, sem
  wake-up). `dispatch_outbox`: sem mudança além de publicar o finalizador
  pelo caminho `pending` já existente.
- Orquestrador (`discovery_tasks.py`, `discovery_celery_tasks.py`): o caminho
  do intent com sweep `cancelling` passa a usar release escopado ao sweep
  (`_release_expired_leases_for_sweep`, flush-only) no mesmo commit que
  `reconcile_sweep` sob lock + `ack` flush-only (`_ack_locked`, sem commit próprio - opção (a), idem § P1) (claim vazio → lock → refresh →
  release escopado → reconcile → ack flush-only → commit único); o
  `release_expired_leases` global com commit próprio é removido desse
  caminho. `reconcile_sweep` passa a adquirir `_lock_sweep` com
  `db.refresh(locked)` explícito e nunca sobrescrever terminal de
  cancelamento; sem outra mudança de lógica.
- Spec canónica `discovery-sweep` recebe o delta antes do apply.
- Fora de escopo: reprocessar as 690 combinações ignoradas; mudar a regra de
  rascunho congelado (Q2); pause/resume; qualquer tela ou texto da UI.

## Riscos

- **Lease órfão de worker morto** (claim sem conclusão): o finalizador e o
  `_repair` executam `release_expired_leases` antes do `reconcile`, que
  recupera o desfecho conhecido ou devolve a `pending` (depois `skipped` sob
  `cancelling`); o sweep fecha no TTL do lease, sem operador.
- **Otimizador longo em voo retarda o `cancelled`** (esperado por Q1): o
  polling da tela já tolera `cancelling` prolongado; nenhum timeout novo.
- **Corrida cancel × último reconcile do orquestrador ativo**: serializada pelo
  lock da linha — `reconcile_sweep` adquire `_lock_sweep` com refresh explícito e relê estado sob
  lock; reconcile tardio que leu `running` antes do commit do cancel observa
  `cancelling`/`cancelled` pós-refresh após o lock e NUNCA promove `running → completed`
  por cima de terminal de cancelamento (regra "terminal nunca sobrescrito").
  Resíduo de janela é re-finalizado pelo re-finalizador terminal — quem
  commitar com `pending == 0` e `running == 0` relidos pós-refresh sob lock fecha, e
  `processed = total` é invariante.
- **Resíduo `running` sob `cancelled` sem agendador (P1)**: claim de janela
  pré-lock cujo settle commita após o fechamento inline deixa
  `processed != total` sem reconcile futuro (repair cobria só `cancelling`,
  finalizador já deu `ack`). Fechamento: o repair cobre também `cancelled`
  com resíduo (`pending > 0 OR running > 0 OR processed != total`) e faz
  release escopado do sweep → residual pós-refresh `pending → skipped` + recount sob
  lock no commit por sweep — sem novo wake-up, sem mudar
  `state`/`completed_at`. `running` de lease expirado com worker morto
  converge no TTL (release escopado + `skipped` no mesmo commit); settle
  tardio converge via recount do próximo repair.
- **Claim tardio sobre `cancelled`**: impossível pelo guarda (`claim` exige
  lock + refresh + `state == running` pós-refresh); se uma linha `running`/`pending` residual for
  observada sobre terminal, o re-finalizador a converte (`pending → skipped`,
  `running` via lease/settle) e recalcula contadores — nunca quebra
  `processed = total`.
- **Duplo finalizador** (cancel repetido / repair + comando): dedup por
  intent `pending`/`delivered` em aberto, mesmo padrão dos wake-ups normais.
- **`run_combination` em corrida** (sweep virou `cancelling` entre claim e
  execução): o pré-check existente devolve a combinação a `pending`, e o
  `reconcile` sob `cancelling` a marca `skipped` — converge, sem perda de
  resultado já commitado.

## O que explicitamente NÃO muda na UI

Nada visual muda: sem alteração em `DiscoveryPage`, polling, botão de
cancelar, mensagens, textos ou layout. A tela já trata `cancelling` e estados
terminais; com este change, o `cancelling` apenas deixa de ser eterno e o
rascunho libera via estado terminal como hoje (Q2). UI impact: none por
decisão do pai; correção 100% server-side.

## Gate (linhas legíveis por máquina)

UI impact: none
live_route: N/A correção 100% server-side; nenhuma superfície visual muda, não há protótipo a clonar

## Apply contract

1. `cancel` sem `running` em voo responde `cancelled` com
   `processed = total` (pendentes → `skipped`) num único commit do comando
   (helper de reconciliação flush-only, sem commit próprio).
2. `cancel` com `running` em voo mantém `cancelling`, não força as em curso a
   `skipped`, agenda um único finalizador no mesmo commit (dedup sob lock;
   limites de outbox só adiam a entrega) e chega a `cancelled` sozinho após
   o settle, com `processed = total`; claim tardio é barrado pelo guarda
   (lock + `db.refresh(locked)` + `state == running` pós-refresh) e resíduo
   terminal é re-finalizado.
3. Sweep `cancelling` travado com outbox `acked` vira `cancelled` no próximo
   `dispatch_outbox`, sem backfill e sem reprocessar ignoradas; `cancelled`
   com resíduo (`processed != total`) é re-finalizado (recount pós-refresh sob lock, sem
   wake-up) no próximo dispatch.
4. `pause`/`resume` continuam rejeitados em `cancelling`; claiming continua
   exclusivo de `running`; matriz terminal inalterada; `reconcile` sob lock
   nunca sobrescreve terminal de cancelamento.
5. Nenhum arquivo de frontend é tocado; spec canónica `discovery-sweep`
   recebe o delta antes do apply.

### Aceito com justificativa (P3 — detalhe de apply, sem tarefa própria)

- `skipped` direto sob terminal sem limpar lease/attempts: detalhe de apply —
  limpeza de lease/attempts é best-effort no apply. Corrida de dedup em
  `ensure_cancel_wakeup` NÃO tem fallback `IntegrityError → created: False`
  (inexequível sem savepoint no Postgres): violação da constraint única
  (`sweep_id`, `generation`) implica rollback total com cura por
  retry/repair (§ `ensure_cancel_wakeup` sob lock e limites, § Atomicidade);
  `created: False` só no caminho limpo (dedup enxergou intent em aberto, sem
  insert).
- Comando sem `release_expired_leases` antes da decisão inline: conservador
  correto por Q1 — nunca força `running` a `skipped` nem fecha cedo; o custo
  é só adiar o close até o TTL do lease (repair/finalizador fecha em seguida).
- Mantidos como aceitos na terceira crítica (já estavam certos, sem reabrir):
  finalizador duplicado idempotente (dedup + chave `sweep_id`+`generation`);
  resíduo `running` sob `cancelled` converge via settle/TTL (release escopado
  + recount, sem wake-up); `run_combination` sem re-check terminal adicional
  + `skipped` sem limpar lease (best-effort no apply); caminho do intent do
  orquestrador com release escopado ao sweep no mesmo commit (P1 desta
  crítica); escopo/regressão sem frontend.
- Registrados como aceitos na quarta crítica (sem reabrir, sem tarefa
  própria): varredura do repair sobre `cancelled` com resíduo sem bound
  (detalhe de apply — condição `pending > 0 OR running > 0 OR
  processed != total` já delimita; bound extra fica para o apply se preciso);
  `FOR UPDATE` no-op em SQLite nos testes (padrão do repo — cobertura lógica
  basta); pré-check de `run_combination` sem lock próprio (coberto por
  re-finalizador terminal + recount do próximo repair).

## Prototype

N/A — correção server-side sem mudança visual: não há estado, layout, copy
ou fluxo de tela a prototipar em HTML; o comportamento observável (fechar em
`cancelled` e liberar o rascunho) já existe na tela e é coberto por testes de
integração do backend.

- **Impeccable:** N/A — sem impacto visual ou de UX; não há o que criticar em
  interface porque nenhuma superfície muda.
- **DESIGN.md:** N/A — nenhum token, componente ou padrão visual é tocado.
- **Playwright:** N/A — sem fluxo de tela novo ou alterado; a verificação é
  por testes de integração do backend (comando, reconciliação, outbox e
  reparo), que cobrem os cenários do contrato.

## Design Critique

Crítica independente em 6 passadas (mesmo modelo, sessões isoladas sem transcript). Rodadas BLOCKED convergiram para PASS final com zero P0/P1 aberto.

- P0 guarda claim×cancel (lock + refresh explícito, claim só com `running` pós-refresh, commit único) — corrigido no design; teste 4.8.
- P0 sobrescrita de terminal por reconcile tardio (lock + refresh, `running→completed` só com estado relido, terminal nunca reescrito) — corrigido; teste 4.9.
- P0 commit parcial comando/repair (helpers flush-only, commit único, rollback total) — corrigido; tasks 2.1/3.1.
- P0 finalizador perdido/duplicado (dedup sob lock, repeat-cancel passa pelo ensure, idempotência por chave) — corrigido; testes 4.2/4.5/4.6.
- P0 terminal com `processed != total` sem reconciliador (repair cobre `cancelled` com resíduo, recount sob lock) — corrigido; teste 4.9.
- P1 ack do finalizador (variante flush-only `_ack_locked` como última mutação, `ack_outbox` proibido no caminho) — corrigido, opção (a).
- P2/P3 restantes — aceitos com justificativa (release global nunca cobre cancelling/cancelled; repair sem bound extra; pré-check sem lock; FOR UPDATE no-op em SQLite; lease/attempts best-effort; sem savepoint).
- Riscos não bloqueantes: otimizador longo em voo retarda o close (Q1, polling tolera); finalizador em cadeia gera dispatches extras até o settle; limites OUTBOX_* adiam sem perder; lock de linha serializa orquestradores do mesmo sweep (lotes de 20, aceitável).

Referências: Prototype N/A justificado (server-side, sem superfície visual); snapshot Impeccable N/A justificado (UI impact none, sem HTML para criticar).

`Design Agent verdict: PASS`
