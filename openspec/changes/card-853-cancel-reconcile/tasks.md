# Tasks: Descoberta — cancelamento auto-finaliza (card #853)

> Fonte: proposal + design § Apply contract. Só após `Status=Pronto para Dev`
> (T7). Sem frontend, sem protótipo.

## 1. Spec canónica

- [x] 1.1 Aplicar o delta
  `openspec/changes/card-853-cancel-reconcile/specs/discovery-sweep/spec.md`
  em `openspec/specs/discovery-sweep/spec.md`: auto-finalização do `cancel`
  (fecha na hora sem voo; aguarda voo e conclui via finalizador; reparo cura
  `cancelling` órfão; `processed = total` em todo terminal de cancelamento).

## 2. Backend — comando `cancel` (contrato 1, 2, 4)

- [x] 2.1 `command(cancel)` reconcilia inline sob o lock via helper flush-only
  (extraído de `reconcile_sweep`, sem commit próprio): após a transição para
  `cancelling`, pendentes → `skipped`; com `pending == 0` e `running == 0`,
  promove a `cancelled` + `completed_at` — tudo num único commit do comando
  (rollback total em falha parcial; sem `skipped` sem `cancelled`).
- [x] 2.2 Novo `ensure_cancel_wakeup` (sem commit próprio): ordem sob o lock do
  chamador — dedup por intent `pending`/`delivered` em aberto → insert da
  próxima `generation` `pending` no mesmo commit; `ensure_sweep_wakeup` segue
  recusando `cancelling` para claiming. Limites OUTBOX_* só adiam a entrega
  (republicação nos dispatches seguintes), nunca bloqueiam o insert.
  `created: False` SOMENTE no caminho limpo (dedup enxergou intent em aberto,
  sem insert); corrida de dedup que furar o check e violar a constraint única
  (`sweep_id`, `generation`) implica rollback total da transação do chamador
  (sem savepoint, sem `created: False`), com cura por retry do comando ou
  repair do próximo dispatch.
- [x] 2.3 Guarda anti-corrida: `claim_combinations` passa a adquirir
  `_lock_sweep` e só reclama com `state == running` pós-refresh (lock →
  `db.refresh(locked)` explícito → check → claim → commit único; toda decisão
  de guarda usa valores pós-refresh — sem refresh, o objeto do identity map
  carrega valores pré-lock). `reconcile_sweep` passa a adquirir `_lock_sweep`
  na entrada com `db.refresh(locked)` explícito (ou expire + reload) e reler
  estado + contadores após o lock; regra "terminal de cancelamento
  nunca é sobrescrito por reconcile tardio": sob `cancelled`/terminal, só
  re-finalização residual (`pending → skipped` + recount, sem reescrever
  `state`/`completed_at`); o caminho `running → completed` exige
  `state == running` relido pós-refresh sob lock (toda decisão de transição
  usa valores pós-refresh). Re-finalizador terminal em
  `reconcile_sweep`: sob `cancelled`, residual `pending → skipped` +
  recálculo (`processed = total`); pré-check de `run_combination` distingue
  `cancelling` (→ `pending`) de terminal (→ `skipped` direto).
- [x] 2.4 Preservar: claiming exclusivo de `running`, rejeição de
  `pause`/`resume` em `cancelling`, matriz terminal (`cancelling -> cancelled`/`failed`).
- [x] 2.5 Repeat-cancel passa pelo ensure (early-return `command` 1054–1056):
  sob `cancelling`, o comando NÃO retorna antes do ensure — sob lock,
  reconcilia (flush) + `ensure_cancel_wakeup` com dedup no mesmo commit
  — o finalizador só é inserido se, após o reconcile inline, o sweep ainda
  estiver `cancelling` com `running > 0` (se o inline já promoveu a
  `cancelled`, nenhum insert); repetido nunca duplica, nunca deixa
  `cancelling` com `running` sem
  finalizador em aberto); sob `cancelled`, no-op idempotente sem wake-up,
  sem tocar `state`/`completed_at` (resíduo via repair do próximo dispatch).

## 3. Backend — reparo e orquestrador (contrato 2, 3)

- [x] 3.1 `_repair_incomplete_sweeps` cobre `cancelling` e `cancelled` com
  resíduo: cada sweep em transação própria, sob lock com `db.refresh(locked)`
  explícito — release escopado
  flush-only do sweep (`_release_expired_leases_for_sweep(sweep_id)`, sem
  commit próprio; o release global nunca roda dentro do laço por sweep;
  vale também sob `cancelled`, onde `running` de lease expirado e worker
  morto só converge via release → `pending` transitório → `skipped` no
  mesmo commit) → reconcilia (flush)
  → `ensure_cancel_wakeup` se `cancelling` com `running > 0` (nunca sob
  `cancelled`) → um commit por sweep; isolamento por sweep: commit/rollback
  + expire/limpeza da sessão por sweep, sem transação única abrangendo o
  laço e sem `begin_nested()` por padrão (`begin_nested()` só se o apply
  adotar txn única com locks retidos); exceção faz rollback só da transação
  do sweep e segue ("falha num sweep não contamina"); `cancelled` com
  resíduo (`pending > 0 OR running > 0 OR processed != total`) recebe
  release escopado + residual `pending → skipped` + recount, sem wake-up e
  sem tocar `state`/`completed_at`. `dispatch_outbox`
  publica o finalizador pelo caminho `pending` existente, sem filtro novo.
  Ordem de commits: um por sweep no repair, depois um único para flips
  stale→pending + marcações pending→delivered; falha parcial republica no
  próximo dispatch, sem meio-estado.
- [x] 3.2 Orquestrador — escopar o release ao sweep (P1): o caminho do intent com
  sweep `cancelling` (claim vazio → lock + refresh → release escopado do sweep
  flush-only → `reconcile_sweep` sob lock (flush) → `ack` flush-only via `_ack_locked` (sem commit próprio; o `ack_outbox` NÃO é chamado neste caminho - opção (a)) como última mutação, tudo no mesmo commit único do
  sweep) usa SOMENTE `_release_expired_leases_for_sweep(sweep_id)`; remover o
  `release_expired_leases` global com commit próprio desse caminho — com commit
  próprio ele ressuscitaria `running` expirado em `pending` de `cancelled` de
  OUTRO sweep sem reconcile acoplado. Se o release global for mantido em outro
  caminho, ele nunca cobre `cancelling`/`cancelled`.

## 4. Testes (contrato 1–4; sem Playwright — ver design § Prototype)

- [x] 4.1 Regressão do caso PROD: sweep `cancelling` com outbox `acked`,
  `pending > 0`, `running == 0` fecha a `cancelled` com `processed = total`
  no comando e/ou no próximo dispatch, sem reprocessar ignoradas.
- [x] 4.2 Cancel com `running` em voo: permanece `cancelling`, agenda um
  único finalizador (cancel repetido sob `cancelling` passa pelo ensure com
  dedup — não duplica e mantém exatamente um finalizador em aberto;
  repetido sob `cancelled` é no-op sem wake-up) e chega a `cancelled` após
  o settle, sem forçar as em curso a `skipped`.
- [x] 4.3 Cancel sem voo fecha na hora no próprio comando.
- [x] 4.4 `pause`/`resume` em `cancelling` continuam rejeitados; rascunho
  segue liberando só via estado terminal.
- [x] 4.5 Repair com `running`: sweep `cancelling` com `running > 0` e sem
  intent em aberto gera exatamente um finalizador (repair repetido / repair +
  comando não duplicam); após o settle vira `cancelled` com `processed = total`.
- [x] 4.6 Redelivery / duplo finalizador idempotente: intent `delivered` stale
  que volta a `pending` não gera segundo finalizador; orquestrador executado
  duas vezes para o mesmo (`sweep_id`, `generation`) não reexecuta
  combinações com resultado e dá `ack` uma vez.
- [x] 4.7 Corrida claim → `cancelling` → `skipped` via pré-check: combinação
  reclamada antes do cancel, cujo `run_combination` roda já sob
  `cancelling`, volta a `pending` e é marcada `skipped` pelo `reconcile`
  (sem perda de resultado já commitado); combinação que chega ao pré-check
  já sob `cancelled` vai direto a `skipped` (o pré-check não cria `pending`;
  eventual `pending` transitório do release escopado é convertido a
  `skipped` no mesmo commit).
- [x] 4.8 Claim concorrente pós-close inline devolve vazio sob lock:
  com o cancel já commitado a `cancelled`, `claim_combinations` concorrente
  adquire `_lock_sweep`, observa o terminal e devolve `[]` sem tocar em
  linha alguma; o sweep permanece `cancelled` com `processed = total`.
- [x] 4.9 Reconcile sob `cancelled` re-finaliza sem sobrescrever o terminal:
  com resíduo `pending` (e/ou `processed != total` após settle tardio de
  claim pré-lock), `reconcile_sweep`/repair sob lock executa release
  escopado do sweep e converte residual
  `pending → skipped` + recount, mantém `state = cancelled` e
  `completed_at` intactos e restaura `processed = total` sem agendar
  wake-up novo.

## 5. Ajustes pós-review (sem produção)

- [x] 5.1 P2 perf do repair: filtrar `cancelled` com resíduo no banco
  (`EXISTS pending/running` ou `processed != total`) com limite por dispatch,
  sem carregar o histórico em memória e sem lock espúrio por candidato.
- [x] 5.2 P3 rollback em sessão alheia: `claim_combinations` e
  `_command_cancel` só fazem rollback em sessão própria; sessão do chamador
  nunca é descartada, mantendo o comportamento para sessão fresca.
- [x] 5.3 P3 log enganoso do finalizador: incluir o estado (`cancelling` com
  `running > 0` ainda não é close) no log do caminho do intent.
- [x] 5.4 P3 redação de spec: restaurar os nomes concretos `_ack_locked` /
  `ack_outbox` na frase do ack do Requirement "Cancel with in-flight work…".
- [x] 5.5 P3 tiebreak de ordenação: nas duas varreduras do repair,
  `.order_by(created_at.asc(), id.asc())` (mesmo padrão de
  `list_active_sweeps`/`list_history`).
- [x] 5.6 P3 env clamp: parse de `DISCOVERY_REPAIR_CANCELLED_BATCH` com
  clamp >= 1 (inválido/<= 0 vira 1); default 100 inalterado.
- [x] 5.7 P3 spec normativa: removido o "e.g." da frase do ack para tornar
  `_ack_locked` normativo (espelhado no delta do change).
