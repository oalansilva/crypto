## Context

Card [#652](https://github.com/oalansilva/crypto/issues/652) (kaizen P1). O yaml T16 já é `Homologado --fechar_release, Alan, M_lote--> Pronto` com ações `release_guard`, `deploy_prod`, `set_status` e I9. O live recusa o Agent: `process_event` hardcode `actor=Agent`, `m_lote=False`, reject `unbound` em `develop`. O lote 2026-08-21 (`33df201a`, post PASS) ficou Homologado. Alan pediu que o Agent mova os cards após a publicação, como antes do EFSM.

**UI impact: none.** Harness/CLI. Prototype N/A. Impeccable N/A.

## Goals / Non-Goals

**Goals:**

- Live `process_event fechar_release` mede `M_lote` (`release-guard post` PASS).
- Com guarda verdadeira, comenta Pronto e move todos os `RELEASE_CARDS` Homologado → Pronto.
- Falha de medição / card fora de Homologado / comentário ⇒ I9, Status do pacote não avança como sucesso.
- T1 / T7 / T15 continuam reject Agent. pytest cobre verde e falha.

**Non-Goals:**

- Encapsular archive OpenSpec, PR `main`, merge, deploy PROD ou sync `main→develop` dentro de `process_event` (continuam o overlay no pedido de release).
- Bypass de T15 (Done→Homologado).
- `--actor Alan`, `--m-lote` na CLI, `PROCESS_FSM_MOVE`.
- Código de produto (`backend/`, `frontend/src/`).
- Arraste residual do Alan no UI do Project (hook não vê; igual T14).

## Decisions

1. **T16.actor = Agent; T15 permanece Alan.**  
   Homologar é teste humano em DEV. Pronto é consequência de `M_lote`. Alternativa: `actor: [Alan, Agent]` só para não quebrar o validator — recusada: I2 listaria T16 como humano e o Agent continuaria “não arraste”. **BREAKING** de processo: `ALAN_GATES` perde T16; `harness.mdc` passa a “Alan único em T1/T7/T15”; skill `alan-workflow` atualiza a lista de gates. Validator que hoje falha se T16 não tiver Alan **inverte**: T16 MUST ter Agent e MUST NOT exigir Alan.

2. **Medir `M_lote` no live; testes injetam o predicado.**  
   Alternativa: flag `--m-lote` (Agent forja, mesma classe do `--checks-green` recusado no #632). `main()` **não** aceita essa flag. Se o caller não passou `m_lote`, `process_event` chama `measure_m_lote()` **antes** de `evaluate()`. True **somente** quando `scripts/release-guard post` exit 0 no cwd do repo (env `RELEASE_DATE`, `RELEASE_CARDS`, `RELEASE_BRANCHES`, `PROD_DEPLOY_EVIDENCE`, `PRESERVED_BRANCHES` já exigidos pelo guard). Exit ≠ 0, timeout, binário ausente ou erro de spawn ⇒ False (fail-closed). Pytest injeta `m_lote=` ou measurer fake; **não** chama `release-guard` real nem GitHub.

3. **`process_event` NÃO faz deploy PROD.**  
   A ação yaml `deploy_prod` é satisfeita pela prova já embutida no post (`PROD_DEPLOY_EVIDENCE` ancestor de `origin/main` + services + URL). Reexecutar `git reset --hard` no path PROD ou `systemctl restart` a partir do evento duplicaria o overlay e aumentaria o blast radius. Ação yaml `release_guard` = a medição live (D2), não um segundo closeout.

4. **Membership Homologado-ou-Pronto; skip idempotente; I9 só no resto.**  
   `RELEASE_CARDS` (env, canônico do guard) é a lista. `--card N` sozinho, se `RELEASE_CARDS` vazio, equivale a pacote `{N}`. Cada id MUST estar Homologado **ou já Pronto**. Done/QA/Design/ausente ⇒ `reject` `I9`, closer e mover vazios (nenhum `set_status` nesta invocação). Homologado: `comment_pronto` e então `set_status(Pronto)`. Já Pronto: skip (sem segundo move; comentário pode no-op via dedupe). Falha de comentário **antes** de qualquer move desta invocação ⇒ I9, Homologados intactos. Falha no meio do loop: não reverte os já Pronto; retry do **mesmo** `RELEASE_CARDS` trata os Pronto como skip e continua os Homologado. Não reabre Pronto.

5. **Lote não exige `bound_card` de worktree.**  
   Closeout roda no source DEV (`q_git=develop`) ou na `release-*`. O reject `unbound` atual bloqueia T16. Exceção **só** para `event=fechar_release` com lista de cards não vazia. Demais eventos (T8, T14, …) continuam unbound-deny. `--card` que não casa `q_git` de worktree **não** aplica `card_mismatch` em T16. Depois do check de membership, `evaluate()` MUST receber `state=Homologado` (injetado), `actor=Agent`, `m_lote` medido — **não** o `q` de `github_status_provider(None)`. O mover chama `set_status` **por id do pacote**, não pelo `bound_card` da sessão.

6. **`comment_pronto` = helper canônico.**  
   Uma invocação do helper **por membro Homologado**: `scripts/post-card-evidence-comment.sh --transition pronto --card <id>` com `--cards` (lista do pacote), `--deploy` copiado de `PROD_DEPLOY_EVIDENCE`, `--commit` = SHA de `origin/main`. Falha ⇒ I9 se ainda não moveu nesta invocação; após primeiro move, reject sem reverter Status (Project não tem transação); retry D4.

7. **`--dry-run` e runner ausente.**  
   Dry-run MAY medir (read-only post) e MUST NOT comentar nem mover. Live `main()` injeta measurer+closer reais. Measurer `None` ou closer `None` ⇒ reject, nunca `_safe_move`. Mesmo padrão T14.

8. **Paging / tools Homologado.**  
   `enabled_tools[Homologado]` inclui `process_event`. Stub `context_file[Homologado]`: T16 = `process_event fechar_release` com `M_lote` live; chat ≠ δ. `HUMAN_EVENTS` perde `fechar_release`.

9. **I9 compilada no runtime (depois da guarda); ¬M_lote é `guard:`.**  
   Padrão T14: measurer False/None ⇒ `evaluate()` com `m_lote=False` ⇒ `reason` começa com `guard:` (`guard:M_lote`); closer não roda. Yaml I9 (“T16 exige M_lote”) continua verdadeira via essa guarda. Depois da guarda True, falha de membership/closer/comentário ⇒ `reason=I9` (não `actor`). Reject de T15 permanece `actor`. Toda reject de `fechar_release` por ¬M_lote continua a citar `alan-workflow-ambientes` e `release-guard`. Token yaml `deploy_prod` permanece no T16; **não** é passo Mealy de `process_event` (D3).

## Risks / Trade-offs

- [Agent forja env do post] → o measurer reexecuta o guard fail-closed; forjar `PROD_DEPLOY_EVIDENCE` já era possível no closeout manual. Aceito.
- [Partial Pronto no loop de move] → sem transação no Project. Mitigação: checar Homologado em lote antes; retry idempotente.
- [Alan ainda arrasta Pronto no UI] → residual; este card não fecha o furo do hook (igual #632).
- [post PASS com cards já mistos] → Pronto no pacote = skip; Done/QA = I9 até o Agent tirar esses ids de `RELEASE_CARDS`.
- [T16 em worktree de card] → permitido se `RELEASE_CARDS` está set; não é o caminho canônico (source `develop`).

## Migration Plan

Aditivo em yaml + `process_event` + validator. Cards Homologado passam a poder `fechar_release` de verdade após post. Rollback = reverter o módulo; T16 volta ao reject Agent. Sem migration de banco. O lote 2026-08-21 já publicado não é reprocessado por este card (Alan arrasta, ou um `fechar_release` live depois do apply se os cards ainda estiverem Homologado e o post ainda PASS).

## Open Questions

Nenhuma bloqueante. Deploy continua no overlay; T16 só fecha o board.

## UI impact

**none** — CLI de processo. Nenhuma tela de produto nova ou alterada.

## Prototype

N/A — `UI impact: none`. T16 não tem superfície visual.

## Prototype Validation

N/A.

## Impeccable Brief

N/A — `UI impact: none`.

## Impeccable Critique

N/A — `UI impact: none`.

## Impeccable Audit

N/A — `UI impact: none`.

## Impeccable Trace

N/A — `UI impact: none`.

## Design Critique

Crítica isolada inherit (read-only, duas rodadas). Fontes: `proposal.md`, `design.md` (D1–D9), `tasks.md`, `specs/process-fsm/spec.md`, `specs/process-fsm-event/spec.md`, `specs/cursor-harness/spec.md`, yaml T16/I2/I9, `process_event.py` baseline, padrão T14 #632. Card #652, change `card-652-t16-live-fechar-release`, `Status=Design`. Prototype: N/A. Impeccable: N/A (`UI impact: none`).

Primeira crítica: **BLOCKED** — P0 (D4 Pronto⇒I9 vs retry), P1 (`reason` I9 vs `guard:M_lote`; `evaluate` unbound sem `state=Homologado`).

Correções no escopo: membership Homologado-ou-Pronto (Pronto=skip); ¬M_lote = `guard:M_lote` (I9 só após guarda True); `evaluate(state=Homologado)` e mover por id do pacote.

Recrítica 2 (inherit, não editar): P0/P1 da rodada 1 fechados. P2 aceitos: overlap ¬M_lote+Done; closer “each member” vs Homologado restante; pacote 100% Pronto sem cenário próprio; título “lote stub”; fixture unbound não nomeada em 2.6.

- **Escopo:** T16 live fecha Pronto; deploy PROD fora do evento; T15 Alan.
- **Processo:** Agent ⇏ T1/T7/T15; Pronto = `process_event fechar_release` após post PASS.
- **Operação:** `guard:M_lote` fail-closed; retry idempotente; yaml `deploy_prod` não-Mealy.

**Design Agent verdict: PASS** — crítica isolada inherit (recrítica 2). Prototype N/A. Impeccable N/A.

